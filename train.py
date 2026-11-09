"""Training stage: clean, validate, then train and evaluate the ensemble."""
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import PoissonRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from core import config, data, features, labels, model, validation


def _load_inputs():
    result = data.build_hourly(config.READINGS_YEAR_N)
    accidents = data.load_accidents(config.ACCIDENTS_YEAR_N)
    table = labels.attach_labels(result.table, accidents)
    other = data.build_hourly(config.READINGS_YEAR_N1)
    identical = result.wide.equals(other.wide)
    return table, result.wide, labels.label_report(accidents)["near_accidents"], identical


def _calibration(limits, y, mu) -> list:
    return [
        {"limit_kmh": int(limit), "hours": int((limits == limit).sum()),
         "observed_per_hour": float(y[limits == limit].mean()), "predicted_per_hour": float(mu[limits == limit].mean())}
        for limit in sorted(set(limits))
    ]


def run(table=None, sensor_wide=None, source_near_total=None, identical=None,
        artifacts_dir=config.ARTIFACTS_DIR, n_members=10, cv_repeats=4):
    artifacts_dir = Path(artifacts_dir)
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    if table is None:
        table, sensor_wide, source_near_total, identical = _load_inputs()

    checked = validation.validate(table, sensor_wide, source_near_total, identical_to_other_year=identical)
    (artifacts_dir / "data_validation.json").write_text(json.dumps(checked.to_dict(), indent=2), encoding="utf-8")
    checked.raise_if_failed()

    risky = table[features.dark_or_ice_mask(table)].reset_index(drop=True)
    X, y = features.training_matrix(risky), risky["near_accidents"].astype(float)
    days = risky["day"]
    train, val, test = days <= 21, days.between(22, 26), days >= 27

    ensemble = model.train_ensemble(X[train], y[train], days[train], X[val], y[val], n_members=n_members)
    test_members = ensemble.predict_members(X[test])
    test_mu = test_members.mean(axis=0)
    constant = np.full(int(test.sum()), y[train | val].mean())
    glm = make_pipeline(StandardScaler(), PoissonRegressor(alpha=0.1)).fit(X[train | val], y[train | val])

    network = model.evaluate(y[test], test_mu)
    baseline = model.evaluate(y[test], constant)
    cv = model.cross_validated_skill(X, y, days, n_members=3, folds=5, repeats=cv_repeats)
    support = {int(k): int(v) for k, v in risky["speed_limit"].value_counts().items()}

    ensemble.meta = {"skill_pct": cv["skill_pct"], "support_hours": support}
    ensemble.save(artifacts_dir / "model.pt")

    report = {
        "population": {"dark_or_ice_hours": len(risky), "train": int(train.sum()),
                       "validation": int(val.sum()), "test": int(test.sum())},
        "members": n_members,
        "best_epochs": [history["best_epoch"] for history in ensemble.history],
        "loss_history_member_0": ensemble.history[0],
        "test_network": network,
        "test_constant_baseline": baseline,
        "test_glm": model.evaluate(y[test], glm.predict(X[test])),
        "test_skill_pct": model.skill_pct(network["poisson_deviance"], baseline["poisson_deviance"]),
        "cross_validation": cv,
        "calibration_on_test": _calibration(risky["speed_limit"][test].to_numpy(), y[test].to_numpy(), test_mu),
        "predictive_coverage_90_on_test": model.predictive_coverage(y[test], test_members),
        "support_hours_by_limit_kmh": support,
        "prediction_range_on_test_per_hour": [float(test_mu.min()), float(test_mu.max())],
    }
    (artifacts_dir / "training_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main():
    report = run()
    cv, base = report["cross_validation"], report["test_constant_baseline"]
    print(f"Dark or black-ice hours: {report['population']['dark_or_ice_hours']}")
    print(f"Test deviance: network {report['test_network']['poisson_deviance']:.4f}, "
          f"constant {base['poisson_deviance']:.4f}, GLM {report['test_glm']['poisson_deviance']:.4f}")
    print(f"Test skill vs constant: {report['test_skill_pct']:+.1f}%")
    print(f"Cross-validated skill ({cv['folds']} folds): {cv['skill_pct']:+.1f}% "
          f"(best fold {cv['best_fold_skill_pct']:+.1f}%, worst {cv['worst_fold_skill_pct']:+.1f}%)")
    print(f"90% predictive coverage on test days: {report['predictive_coverage_90_on_test']:.0%}")


if __name__ == "__main__":
    main()
