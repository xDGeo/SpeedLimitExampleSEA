"""Does synthetic data help? Trains on it, scores on real held-out days, writes a report.

This is an experiment only. It never replaces artifacts/model.pt.
"""
import collections
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import PoissonRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from analyze_data import AQUA, BLUE, INK, MUTED, ORANGE, SURFACE, markdown_table, plt
from core import config, data, features, labels, model
from core import weather_policy as wp

LIMITS = np.array(config.CANDIDATE_LIMITS, dtype=float)
ASSUMPTIONS = {
    "Faster = riskier (speed squared)": lambda v: (v / 60) ** 2,
    "Slower = riskier (reversed)": lambda v: (60 / v) ** 2,
    "Speed has no effect": lambda v: np.ones_like(v),
}
COLORS = dict(zip(ASSUMPTIONS, (ORANGE, BLUE, AQUA)))


def load_real() -> pd.DataFrame:
    """Dark or black-ice hours, with the labels of both years."""
    result = data.build_hourly(config.READINGS_YEAR_N)
    year_n = labels.attach_labels(result.table, data.load_accidents(config.ACCIDENTS_YEAR_N))
    year_next = labels.attach_labels(result.table, data.load_accidents(config.ACCIDENTS_YEAR_N1))
    mask = features.dark_or_ice_mask(year_n).to_numpy()
    real = year_n[mask].reset_index(drop=True)
    real["y"] = real["near_accidents"].astype(float)
    real["y_next"] = year_next.loc[mask, "near_accidents"].astype(float).to_numpy()
    return real


def jittered(base: pd.DataFrame, n: int, rng) -> pd.DataFrame:
    """New plausible hours: real rows with small noise, kept only if still dark or icy."""
    s = base.iloc[rng.integers(0, len(base), n)].reset_index(drop=True).copy()
    s["lux"] = s["lux"] * np.exp(rng.normal(0, 0.1, n))
    for column, scale, low, high in (("water_um", 40, 0, 10000), ("temperature_c", 0.5, -30, 70),
                                     ("wind_strength", 3, 0, 300), ("humidity_pct", 2, 0, 100),
                                     ("traffic_cars_s", 1, 0, 50)):
        s[column] = np.clip(s[column] + rng.normal(0, scale, n), low, high)
    return s[features.dark_or_ice_mask(s).to_numpy()].reset_index(drop=True)


def assumed(base, n, rng, shape, mean_rate, reference_limits=None) -> pd.DataFrame:
    """Hours whose near-accidents follow an assumed effect of speed, not anything observed."""
    s = jittered(base, n, rng)
    s["speed_limit"] = rng.choice(LIMITS, len(s))
    reference = base["speed_limit"] if reference_limits is None else reference_limits
    scale = mean_rate / shape(np.asarray(reference, dtype=float)).mean()
    s["y"] = rng.poisson(scale * shape(s["speed_limit"].to_numpy(dtype=float))).astype(float)
    return s


def folds(real, repeats):
    days = np.sort(real["day"].unique())
    for repeat in range(repeats):
        order = np.random.default_rng(repeat).permutation(days)
        for index, test_days in enumerate(np.array_split(order, 5)):
            rest = np.setdiff1d(order, test_days)
            yield repeat * 10 + index, rest[len(rest) // 5:], rest[: len(rest) // 5], test_days


def _fit(train, val, members, seed):
    return model.train_ensemble(features.training_matrix(train), train["y"], train["day"].to_numpy(),
                                features.training_matrix(val), val["y"], n_members=members, seed=seed)


def _real_scores(ensemble, test, constant):
    """Scored on real held-out days, against both years of real labels."""
    y = np.r_[test["y"], test["y_next"]]
    mu = ensemble.predict(features.training_matrix(test))
    return model.poisson_deviance(y, np.r_[mu, mu]), model.poisson_deviance(y, np.full(len(y), constant))


def _split(real, *day_groups):
    return [real[real["day"].isin(days)].reset_index(drop=True) for days in day_groups]


def _synthetic_rows(kind, factor, train, rng):
    extra = jittered(train, len(train) * factor, rng)
    if kind == "glm":
        generator = make_pipeline(StandardScaler(), PoissonRegressor(alpha=0.1, max_iter=500)).fit(
            features.training_matrix(train), train["y"])
        extra["y"] = rng.poisson(generator.predict(features.training_matrix(extra))).astype(float)
    return extra


def imitation_study(real, repeats, factors, members) -> list:
    configs = [("Real data only", None, 0)]
    configs += [(f"Resampled with noise, x{m}", "resample", m) for m in factors]
    configs += [(f"Generated from a fitted model, x{m}", "glm", m) for m in factors]
    rows = []
    for name, kind, factor in configs:
        model_d, base_d, added = [], [], []
        for seed, train_days, val_days, test_days in folds(real, repeats):
            rng = np.random.default_rng(1000 + seed)
            train, val, test = _split(real, train_days, val_days, test_days)
            extra = _synthetic_rows(kind, factor, train, rng) if kind else train.iloc[0:0]
            ensemble = _fit(pd.concat([train, extra], ignore_index=True), val, members, seed + 1)
            m, b = _real_scores(ensemble, test, train["y"].mean())
            model_d.append(m), base_d.append(b), added.append(len(extra))
        rows.append({"method": name, "synthetic_rows": int(np.mean(added)),
                     "skill_real_pct": model.skill_pct(float(np.mean(model_d)), float(np.mean(base_d)))})
    return rows


def _skills(real, shape, mean_rate, reference, repeats, members, factor):
    model_syn, base_syn, model_real, base_real = [], [], [], []
    for seed, train_days, val_days, test_days in folds(real, repeats):
        rng = np.random.default_rng(2000 + seed)
        parts = _split(real, train_days, val_days, test_days)
        train, val, test = (assumed(p, len(p) * factor, rng, shape, mean_rate, reference) for p in parts)
        ensemble = _fit(train, val, members, seed + 1)
        model_syn.append(model.poisson_deviance(test["y"], ensemble.predict(features.training_matrix(test))))
        base_syn.append(model.poisson_deviance(test["y"], np.full(len(test), train["y"].mean())))
        m, b = _real_scores(ensemble, parts[2], parts[0]["y"].mean())
        model_real.append(m), base_real.append(b)
    return (model.skill_pct(float(np.mean(model_syn)), float(np.mean(base_syn))),
            model.skill_pct(float(np.mean(model_real)), float(np.mean(base_real))))


def _replay(real, ensemble, skill, support) -> dict:
    """Runs the real policy over the real hours, with the skill a synthetic test would claim."""
    base = features.training_matrix(real)
    chosen, levels, met = collections.Counter(), collections.Counter(), 0
    curve = {int(v): [] for v in LIMITS}
    for index in range(len(base)):
        rows = pd.concat([base.iloc[[index]]] * len(LIMITS), ignore_index=True)
        rows["speed_limit"] = LIMITS
        predictions = [wp.CandidatePrediction(int(v), float(a.mean), float(a.low), float(a.high), float(a.p_le_target))
                       for v, a in zip(LIMITS, ensemble.summary(rows).itertuples())]
        for prediction in predictions:
            curve[prediction.limit_kmh].append(prediction.mean)
        decision = wp.choose_limit(predictions, skill, support, True)
        chosen[decision.limit_kmh] += 1
        levels[decision.confidence.level] += 1
        met += decision.req1_met
    return {
        "predicted_per_hour_by_limit_kmh": {str(k): float(np.mean(v)) for k, v in curve.items()},
        "limit_kmh_counts": {str(k): v for k, v in sorted(chosen.items())},
        "req1_met_hours": int(met), "hours": len(real), "confidence_counts": dict(levels),
    }


def assumption_study(real, repeats, members, replay_members, replay_rows, factor) -> dict:
    mean_rate = real["y"].mean()
    reference = real["speed_limit"]
    support = {int(k): int(v) for k, v in reference.value_counts().items()}
    days = np.sort(real["day"].unique())
    cut = round(len(days) * 0.8)
    results = {}
    for name, shape in ASSUMPTIONS.items():
        skill_syn, skill_real = _skills(real, shape, mean_rate, reference, repeats, members, factor)
        rng = np.random.default_rng(99)
        early, late = _split(real, days[:cut], days[cut:])
        train = assumed(early, replay_rows, rng, shape, mean_rate, reference)
        val = assumed(late, max(replay_rows // 4, 50), rng, shape, mean_rate, reference)
        ensemble = _fit(train, val, replay_members, 7)
        results[name] = {"skill_synthetic_pct": skill_syn, "skill_real_pct": skill_real,
                         **_replay(real, ensemble, skill_syn, support)}
    return results


def _plot_imitation(report, folder):
    rows = list(reversed(report["imitation"]))
    positions = range(len(rows))
    fig, ax = plt.subplots(figsize=(9.5, 4.2))
    ax.axvline(0, color=MUTED, linewidth=1.5)
    values = [row["skill_real_pct"] for row in rows]
    ax.plot(values, list(positions), "o", color=BLUE, markersize=9, markeredgecolor=SURFACE, markeredgewidth=2)
    for y, value in zip(positions, values):
        ax.text(1.0, y, f"{value:+.2f}%", va="center", color=INK, fontsize=10)
    ax.set_yticks(list(positions), [row["method"] for row in rows])
    ax.set_xlim(-5, 5)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Skill on real held-out days compared with guessing the average (%)")
    fig.suptitle("Imitating the real data adds no skill, however much is generated",
                 x=0.01, ha="left", fontweight="bold", fontsize=13)
    fig.tight_layout()
    fig.savefig(folder / "09_synthetic_imitation.png", dpi=150)
    plt.close(fig)


def _plot_assumptions(report, folder):
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    limits = [int(v) for v in LIMITS]
    for name, entry in report["assumptions"].items():
        values = [entry["predicted_per_hour_by_limit_kmh"][str(v)] for v in limits]
        ax.plot(limits, values, color=COLORS[name], linewidth=2, label=f"Trained on: {name}")
        ax.text(70.5, values[-1], name.split(" (")[0], va="center", color=INK, fontsize=10)
    observed = [report["real_observed_per_hour_by_limit_kmh"][str(v)] for v in limits]
    ax.plot(limits, observed, "o", color=INK, markersize=8, markeredgecolor=SURFACE, markeredgewidth=2,
            label="Real data, both years")
    ax.axhline(config.REQ1_TARGET_PER_HOUR, color=MUTED, linewidth=1.5, linestyle="--")
    ax.text(40, config.REQ1_TARGET_PER_HOUR + 0.05, "REQ1 target: 1 near-accident/h", color=INK, fontsize=10)
    ax.set_xticks(limits, [f"{v} km/h" for v in limits])
    ax.set_xlim(38, 78)
    ax.set_ylim(0, None)
    ax.grid(axis="x", visible=False)
    ax.set_xlabel("Speed limit (km/h)")
    ax.set_ylabel("Predicted near-accidents per hour")
    ax.legend(loc="upper center", fontsize=9, ncols=2)
    ax.set_title("Opposite assumptions give opposite answers, and the model simply returns them")
    fig.tight_layout()
    fig.savefig(folder / "10_synthetic_assumptions.png", dpi=150)
    plt.close(fig)


def _limit_text(counts) -> str:
    return ", ".join(f"{k} km/h: {v} h" for k, v in counts.items())


def write_markdown(report, path):
    imitation = pd.DataFrame([{
        "Training data": row["method"], "Synthetic rows": row["synthetic_rows"],
        "Skill on real held-out days": f"{row['skill_real_pct']:+.2f}%",
    } for row in report["imitation"]])
    assumption = pd.DataFrame([{
        "Assumption built into the data": name,
        "Skill on synthetic test": f"{e['skill_synthetic_pct']:+.2f}%",
        "Skill on real held-out days": f"{e['skill_real_pct']:+.2f}%",
        "Limits chosen": _limit_text(e["limit_kmh_counts"]),
        "REQ1 'met'": f"{e['req1_met_hours']} of {e['hours']} h",
    } for name, e in report["assumptions"].items()])
    predicted = pd.DataFrame([{
        "Assumption": name, **{f"{k} km/h": f"{v:.2f}" for k, v in e["predicted_per_hour_by_limit_kmh"].items()},
    } for name, e in report["assumptions"].items()] + [{
        "Assumption": "Real data, both years",
        **{f"{k} km/h": f"{v:.2f}" for k, v in report["real_observed_per_hour_by_limit_kmh"].items()},
    }])
    text = f"""# Synthetic data experiment

*Generated by `synthetic_experiment.py`. This is an experiment only: the production model is not changed.*

**Question:** can generating more data make the network better, or help satisfy REQ1?

**Answer: no.** Data that imitates the real data adds no information. Data with an assumed effect of speed teaches the model that assumption, so its results say nothing about this road.

Every skill figure compares the model with guessing the average. Real results use real held-out days and both years of near-accident labels. Whole days are held out, and synthetic rows come only from training days.

## Experiment 1: imitate the real data

Synthetic hours are real hours with small noise added. Their near-accident counts are either copied, or drawn from a model fitted to the training days.

{markdown_table(imitation)}

![Imitation results](plots/09_synthetic_imitation.png)

## Experiment 2: assume an effect of speed

Synthetic hours get a random speed limit, and their near-accidents are drawn from an assumed relation between speed and risk. The model trains only on these hours. The policy then runs over all real dark or black-ice hours.

{markdown_table(assumption)}

Predicted near-accidents/h, averaged over the real hours:

{markdown_table(predicted)}

![Assumption results](plots/10_synthetic_assumptions.png)

Two opposite assumptions both claim to satisfy REQ1, and they recommend opposite speeds. Each scores well on a test made from its own assumption, yet loses to guessing the average on real days. A score on synthetic data only measures how well the model learned the assumption.

## Where synthetic data is useful

- Testing that the code can learn at all. The control experiment in `tests/test_model.py` does this.
- Demos and stress tests of rare conditions or sensor faults.
- Planning a real trial, by simulating how many hours are needed to detect an effect of a given size.

If published road-safety research is used to set a limit, it should appear as an explicit expert rule with its source, not as training data.
"""
    path.write_text(text, encoding="utf-8")


def run(real=None, repeats=2, factors=(1, 5, 20), members=3, replay_members=10, replay_rows=5000, factor=20,
        artifacts_dir=config.ARTIFACTS_DIR, docs_dir=config.DOCS_DIR) -> dict:
    real = load_real() if real is None else real
    artifacts_dir, docs_dir = Path(artifacts_dir), Path(docs_dir)
    plots = docs_dir / "plots"
    plots.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    pooled = (real["y"] + real["y_next"]) / 2
    report = {
        "imitation": imitation_study(real, repeats, factors, members),
        "assumptions": assumption_study(real, repeats, members, replay_members, replay_rows, factor),
        "real_observed_per_hour_by_limit_kmh": {
            str(int(k)): float(v) for k, v in pooled.groupby(real["speed_limit"]).mean().items()
        },
    }
    (artifacts_dir / "synthetic_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    _plot_imitation(report, plots)
    _plot_assumptions(report, plots)
    write_markdown(report, docs_dir / "SYNTHETIC_DATA.md")
    return report


def main():
    report = run()
    for row in report["imitation"]:
        print(f"{row['method']:40s}{row['synthetic_rows']:7d}{row['skill_real_pct']:+9.2f}%")
    for name, entry in report["assumptions"].items():
        print(f"{name}: synthetic {entry['skill_synthetic_pct']:+.2f}%, real {entry['skill_real_pct']:+.2f}%, "
              f"limits {entry['limit_kmh_counts']}, REQ1 met {entry['req1_met_hours']}/{entry['hours']}")


if __name__ == "__main__":
    main()
