import numpy as np
import pandas as pd
import pytest

from core import model

COLUMNS = ["a", "b"]


def dataset(n_days=40, per_day=20, signal=True, seed=0):
    rng = np.random.default_rng(seed)
    rows = n_days * per_day
    days = np.repeat(np.arange(1, n_days + 1), per_day)
    X = pd.DataFrame(rng.normal(size=(rows, 2)), columns=COLUMNS)
    rate = np.exp(0.2 + (1.0 * X["a"].values if signal else 0.0))
    y = rng.poisson(rate)
    return X, pd.Series(y, dtype=float), pd.Series(days)


def small_ensemble(n_members=3, seed=1, signal=True):
    X, y, days = dataset(signal=signal)
    train, val = days <= 30, days > 30
    return model.train_ensemble(X[train], y[train], days[train], X[val], y[val],
                                n_members=n_members, seed=seed, max_epochs=120), X


def test_predictions_are_positive():
    ensemble, X = small_ensemble()
    assert (ensemble.predict(X) > 0).all()


def test_member_shape():
    ensemble, X = small_ensemble(n_members=3)
    assert ensemble.predict_members(X).shape == (3, len(X))


def test_summary_columns_and_order():
    ensemble, X = small_ensemble()
    summary = ensemble.summary(X.iloc[:4])
    assert list(summary.columns) == ["mean", "low", "high", "p_le_target"]
    assert (summary["low"] <= summary["mean"]).all() and (summary["mean"] <= summary["high"]).all()
    assert summary["p_le_target"].between(0, 1).all()


def test_same_seed_is_reproducible():
    (a, X), (b, _) = small_ensemble(seed=7), small_ensemble(seed=7)
    assert a.predict(X) == pytest.approx(b.predict(X))


def test_different_members_disagree():
    ensemble, X = small_ensemble(n_members=3)
    assert ensemble.predict_members(X).std(axis=0).mean() > 0


def test_save_and_load_same_predictions(tmp_path):
    ensemble, X = small_ensemble()
    ensemble.meta["skill_pct"] = -1.5
    path = tmp_path / "model.pt"
    ensemble.save(path)
    loaded = model.Ensemble.load(path)
    assert loaded.predict(X) == pytest.approx(ensemble.predict(X))
    assert loaded.meta["skill_pct"] == -1.5


def test_validation_loss_recorded_and_training_loss_falls():
    ensemble, _ = small_ensemble(n_members=1)
    history = ensemble.history[0]
    assert history["train_loss"][-1] < history["train_loss"][0]
    assert 0 < history["best_epoch"] <= len(history["val_loss"])


def test_inside_training_range():
    ensemble, X = small_ensemble()
    assert ensemble.in_training_range(X.iloc[:1]).all()
    far = pd.DataFrame([[100.0, 0.0]], columns=COLUMNS)
    assert not ensemble.in_training_range(far).any()


def test_poisson_deviance_zero_for_perfect_fit():
    y = np.array([1.0, 2.0, 3.0])
    assert model.poisson_deviance(y, y) == pytest.approx(0.0)


def test_poisson_deviance_handles_zero_counts():
    assert model.poisson_deviance(np.array([0.0]), np.array([1.0])) == pytest.approx(2.0)


def test_control_experiment_learns_planted_signal():
    X, y, days = dataset(signal=True)
    result = model.cross_validated_skill(X, y, days, n_members=2, folds=4, repeats=1, max_epochs=120)
    assert result["skill_pct"] > 5


def test_control_experiment_finds_no_skill_on_noise():
    X, y, days = dataset(signal=False)
    result = model.cross_validated_skill(X, y, days, n_members=2, folds=4, repeats=1, max_epochs=120)
    assert result["skill_pct"] < 5
