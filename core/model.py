"""EnsembleTrainer and Predictor: small PyTorch networks predicting near-accidents per hour."""
import copy

import numpy as np
import pandas as pd
import torch
from scipy import stats
from torch import nn

from core import config

torch.set_num_threads(1)


class PoissonNet(nn.Module):
    """Feed-forward network whose output is the log of the expected count."""

    def __init__(self, n_features: int, hidden=(16, 8)):
        super().__init__()
        layers, size = [], n_features
        for width in hidden:
            layers += [nn.Linear(size, width), nn.ReLU()]
            size = width
        layers.append(nn.Linear(size, 1))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x).squeeze(-1)


def poisson_deviance(y, mu) -> float:
    y, mu = np.asarray(y, dtype=float), np.clip(np.asarray(mu, dtype=float), 1e-9, None)
    with np.errstate(divide="ignore", invalid="ignore"):
        term = np.where(y > 0, y * np.log(y / mu), 0.0)
    return float(2.0 * np.mean(term - (y - mu)))


def evaluate(y, mu) -> dict:
    y, mu = np.asarray(y, dtype=float), np.asarray(mu, dtype=float)
    return {
        "poisson_deviance": poisson_deviance(y, mu),
        "mae": float(np.mean(np.abs(y - mu))),
        "mse": float(np.mean((y - mu) ** 2)),
    }


def skill_pct(model_deviance: float, baseline_deviance: float) -> float:
    return float(100.0 * (1.0 - model_deviance / baseline_deviance))


class Ensemble:
    def __init__(self, members, n_features, columns, mean, std, minimum, maximum,
                 target=config.REQ1_TARGET_PER_HOUR, meta=None, history=None):
        self.members, self.n_features, self.columns = members, n_features, list(columns)
        self.mean, self.std = np.asarray(mean, dtype=float), np.asarray(std, dtype=float)
        self.minimum, self.maximum = np.asarray(minimum, dtype=float), np.asarray(maximum, dtype=float)
        self.target = target
        self.meta = meta or {}
        self.history = history or []

    def _scaled(self, X: pd.DataFrame) -> torch.Tensor:
        values = (X[self.columns].to_numpy(dtype=float) - self.mean) / self.std
        return torch.as_tensor(values, dtype=torch.float32)

    def predict_members(self, X: pd.DataFrame) -> np.ndarray:
        inputs = self._scaled(X)
        net = PoissonNet(self.n_features)
        net.eval()
        rows = []
        with torch.no_grad():
            for state in self.members:
                net.load_state_dict(state)
                rows.append(torch.exp(net(inputs)).numpy())
        return np.stack(rows)

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self.predict_members(X).mean(axis=0)

    def summary(self, X: pd.DataFrame) -> pd.DataFrame:
        members = self.predict_members(X)
        return pd.DataFrame({
            "mean": members.mean(axis=0),
            "low": np.percentile(members, 5, axis=0),
            "high": np.percentile(members, 95, axis=0),
            "p_le_target": (members <= self.target).mean(axis=0),
        }, index=X.index)

    def in_training_range(self, X: pd.DataFrame) -> np.ndarray:
        values = X[self.columns].to_numpy(dtype=float)
        return ((values >= self.minimum) & (values <= self.maximum)).all(axis=1)

    def save(self, path) -> None:
        torch.save({
            "members": self.members, "n_features": self.n_features, "columns": self.columns,
            "mean": self.mean.tolist(), "std": self.std.tolist(),
            "minimum": self.minimum.tolist(), "maximum": self.maximum.tolist(),
            "target": self.target, "meta": self.meta, "history": self.history,
        }, path)

    @classmethod
    def load(cls, path) -> "Ensemble":
        return cls(**torch.load(path, weights_only=True))


def _train_member(train_x, train_y, val_x, val_y, seed, max_epochs, patience, lr, weight_decay):
    torch.manual_seed(seed)
    net = PoissonNet(train_x.shape[1])
    with torch.no_grad():
        net.net[-1].bias.fill_(float(torch.log(train_y.mean().clamp(min=1e-3))))
    loss_fn = nn.PoissonNLLLoss(log_input=True, full=False)
    optimizer = torch.optim.Adam(net.parameters(), lr=lr, weight_decay=weight_decay)

    history = {"train_loss": [], "val_loss": [], "best_epoch": 1}
    best_loss, best_state, waited = float("inf"), None, 0
    for epoch in range(1, max_epochs + 1):
        net.train()
        optimizer.zero_grad()
        loss = loss_fn(net(train_x), train_y)
        loss.backward()
        optimizer.step()

        net.eval()
        with torch.no_grad():
            val_loss = loss_fn(net(val_x), val_y).item()
        history["train_loss"].append(loss.item())
        history["val_loss"].append(val_loss)
        if val_loss < best_loss - 1e-6:
            best_loss, best_state, waited = val_loss, copy.deepcopy(net.state_dict()), 0
            history["best_epoch"] = epoch
        else:
            waited += 1
            if waited >= patience:
                break
    return best_state, history


def train_ensemble(X_train, y_train, days_train, X_val, y_val, n_members=10, seed=42,
                   max_epochs=300, patience=30, lr=0.01, weight_decay=1e-3) -> Ensemble:
    """Each member sees a bootstrap of whole days, so hours of a day stay together."""
    columns = list(X_train.columns)
    raw = X_train.to_numpy(dtype=float)
    mean, std = raw.mean(axis=0), raw.std(axis=0)
    std[std == 0] = 1.0
    scaled = torch.as_tensor((raw - mean) / std, dtype=torch.float32)
    targets = torch.as_tensor(np.array(y_train, dtype=float), dtype=torch.float32)
    val_x = torch.as_tensor((X_val.to_numpy(dtype=float) - mean) / std, dtype=torch.float32)
    val_y = torch.as_tensor(np.array(y_val, dtype=float), dtype=torch.float32)

    day_values = np.asarray(days_train)
    unique_days = np.unique(day_values)
    day_rows = {day: np.flatnonzero(day_values == day) for day in unique_days}

    members, histories = [], []
    for index in range(n_members):
        member_seed = seed + index
        rng = np.random.default_rng(member_seed)
        sample = rng.choice(unique_days, size=len(unique_days), replace=True)
        rows = np.concatenate([day_rows[day] for day in sample])
        state, history = _train_member(scaled[rows], targets[rows], val_x, val_y, member_seed,
                                       max_epochs, patience, lr, weight_decay)
        members.append(state)
        histories.append(history)
    return Ensemble(members, raw.shape[1], columns, mean, std, raw.min(axis=0), raw.max(axis=0), history=histories)


def cross_validated_skill(X, y, days, n_members=3, folds=5, repeats=4, max_epochs=300, seed=0) -> dict:
    """Repeated cross-validation with whole days held out. One small split is too noisy."""
    X, y = X.reset_index(drop=True), pd.Series(np.asarray(y, dtype=float))
    day_values = np.asarray(days)
    unique_days = np.unique(day_values)
    model_scores, baseline_scores, fold_skills = [], [], []
    for repeat in range(repeats):
        order = np.random.default_rng(seed + repeat).permutation(unique_days)
        for fold in np.array_split(order, folds):
            remaining = np.setdiff1d(order, fold)
            n_val = max(1, len(remaining) // 5)
            val_days, train_days = remaining[:n_val], remaining[n_val:]
            train = np.isin(day_values, train_days)
            val = np.isin(day_values, val_days)
            test = np.isin(day_values, fold)
            ensemble = train_ensemble(X[train], y[train], day_values[train], X[val], y[val],
                                      n_members=n_members, seed=seed + 100 * repeat, max_epochs=max_epochs)
            model = poisson_deviance(y[test], ensemble.predict(X[test]))
            baseline = poisson_deviance(y[test], np.full(test.sum(), y[train | val].mean()))
            model_scores.append(model)
            baseline_scores.append(baseline)
            fold_skills.append(skill_pct(model, baseline))
    return {
        "skill_pct": skill_pct(float(np.mean(model_scores)), float(np.mean(baseline_scores))),
        "model_deviance": float(np.mean(model_scores)),
        "baseline_deviance": float(np.mean(baseline_scores)),
        "folds": len(fold_skills),
        "best_fold_skill_pct": float(np.max(fold_skills)),
        "worst_fold_skill_pct": float(np.min(fold_skills)),
    }


def predictive_coverage(y, members: np.ndarray, level: float = 0.90) -> float:
    """Share of observed counts inside the central interval of the Poisson mixture."""
    y = np.asarray(y, dtype=float)
    tail, covered = (1 - level) / 2, 0
    support = np.arange(0, 60)
    for row, count in enumerate(y):
        cdf = stats.poisson.cdf(support[:, None], members[:, row]).mean(axis=1)
        low = support[np.searchsorted(cdf, tail)]
        high = support[min(np.searchsorted(cdf, 1 - tail), len(support) - 1)]
        covered += int(low <= count <= high)
    return covered / len(y)
