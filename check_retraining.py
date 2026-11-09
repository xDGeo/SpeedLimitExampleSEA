"""Analyses Year N+1 and writes artifacts/retraining_report.json."""
import json

from core import config, model, retraining


def main():
    report = retraining.analyse(model.Ensemble.load(config.MODEL_FILE))
    path = config.ARTIFACTS_DIR / "retraining_report.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Inputs identical to Year N: {report['inputs_identical']}")
    rate = report["near_accident_rate"]
    print(f"Near-accidents: {rate['count_first']} -> {rate['count_second']} (p = {rate['p_value']:.4f})")
    print(f"Frozen model skill on Year N+1: {report['frozen_skill_pct']:+.1f}%")
    print(f"Retrained model cross-validated skill: {report['retrained_cv']['skill_pct']:+.1f}%")
    print(f"Decision: {report['recommendation']['decision']}")
    for reason in report["recommendation"]["reasons"]:
        print(f"  - {reason}")


if __name__ == "__main__":
    main()
