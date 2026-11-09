"""Cleans and validates the data, then writes plots, the data report and the parameter ranges."""
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from scipy import stats

from core import config, data, features, labels, validation
from core import parameter_ranges as ranges

SURFACE, INK, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e7e6e1"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
UNIT_BY_KIND = {
    "water": "µm", "light": "lux", "noise": "dB", "humidity": "%", "wind_direction": "°",
    "wind_strength": "km/h", "temperature": "°C", "traffic": "cars/s", "speed_limit": "km/h",
}
plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "text.color": INK, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.edgecolor": GRID, "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "font.size": 11, "axes.titlesize": 13, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "legend.frameon": False,
})


def save(fig, name):
    config.PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(config.PLOTS_DIR / name, dpi=150)
    plt.close(fig)


def corrupted_copy(raw: pd.DataFrame) -> pd.DataFrame:
    """Injects the fault types listed on slide 17 into a copy. Used only for the demo plot."""
    rng = np.random.default_rng(7)
    frame = raw.copy()
    sensor_15 = frame.index[frame["Sensor"] == "15"]
    frame.loc[rng.choice(sensor_15, 12, replace=False), "Value"] = "500,00"
    frame.loc[frame["Sensor"].eq("2") & frame["Day"].eq("18"), "Month"] = "NULL"
    frame.loc[frame["Sensor"].eq("9") & frame["Day"].eq("3"), "Month"] = "January"
    frame.loc[rng.choice(frame.index, 60, replace=False), "Value"] = ""
    frame.loc[rng.choice(frame.index, 10, replace=False), "Sensor"] = ""
    frame = frame[~(frame["Sensor"].eq("15") & frame["Day"].eq("10"))]
    repeated = frame[frame["Sensor"].eq("4") & frame["Day"].eq("12")]
    return pd.concat([frame, repeated], ignore_index=True)


def plot_issues(report, label_counts):
    issues = [
        ("Licence plates removed", label_counts["rows"]),
        ("Accident hours shifted from 1-24 to 0-23", label_counts["rows"]),
        ("Sensors documented but without readings (7, 10, 17)", len(report["sensors_without_readings"])),
        ("Sensors with readings but undocumented (19)", len(report["undocumented_sensors"])),
        ("Accident rows without any measurement", label_counts["empty_rows"]),
        ("Duplicate readings", report["duplicates_removed"]),
        ("Out-of-range readings", report["out_of_range"]),
        ("Empty values", report["empty_values"]),
        ("Invalid month text", report["months_repaired"]),
        ("Rows with no sensor id", report["rows_without_sensor"]),
        ("Whole hours missing", report["hours_filled"]),
    ]
    names, counts = zip(*reversed(issues))
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.barh(names, counts, color=BLUE, height=0.55)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Records or sensors affected (count)")
    ax.set_xlim(0, max(counts) * 1.1)
    for y, count in enumerate(counts):
        ax.text(count + max(counts) * 0.01, y, f"{count:,}", va="center", color=INK)
    fig.suptitle("Year N needed structural fixes; the listed value faults were absent",
                 x=0.01, ha="left", fontweight="bold", fontsize=13)
    save(fig, "01_issues_found.png")


def plot_before_after(raw_year):
    corrupted = corrupted_copy(raw_year)
    long, report = data.clean_readings(corrupted)
    table, _, grid_report = data.hourly_table(long)
    report.update(grid_report)
    original, _ = data.clean_readings(raw_year)
    reference, _, _ = data.hourly_table(original)
    error = float((table["temperature_c"] - reference["temperature_c"]).abs().mean())

    sensor = corrupted[corrupted["Sensor"].eq("15") & corrupted["Value"].ne("")].copy()
    sensor["hour_index"] = (sensor["Day"].astype(int) - 1) * 24 + sensor["Hour"].astype(int)
    sensor["value"] = sensor["Value"].str.replace(",", ".").astype(float)
    sensor = sensor.sort_values("hour_index")

    fig, axes = plt.subplots(2, 1, figsize=(10, 5.6), sharex=True)
    axes[0].plot(sensor["hour_index"], sensor["value"], color=ORANGE, linewidth=1.3)
    axes[0].set_ylabel("Sensor 15 (°C)")
    axes[0].set_title("Demo on a deliberately corrupted copy: before cleaning (spikes of 500 °C, missing day)")
    hours = (table["day"] - 1) * 24 + table["hour"]
    axes[1].plot(hours, table["temperature_c"], color=BLUE, linewidth=1.3)
    axes[1].set_ylabel("Temperature (°C)")
    axes[1].set_xlabel("Hour of January (h)")
    axes[1].set_title("After cleaning: faults removed and the gap filled from sensors 18 and 19")
    save(fig, "02_before_after_demo.png")
    return report, error


def plot_completeness(wide):
    documented = data.load_sensors()["sensor"].tolist()
    order = sorted(set(documented) | {19}) + [config.SPEED_LIMIT_SENSOR]
    per_day = wide.notna().groupby(level="Day").sum().reindex(columns=order, fill_value=0) / 24 * 100
    cmap = LinearSegmentedColormap.from_list("blue", ["#eef4fc", BLUE])
    fig, ax = plt.subplots(figsize=(10, 5.2))
    image = ax.imshow(per_day.T.values, aspect="auto", cmap=cmap, vmin=0, vmax=100)
    ax.grid(False)
    ax.set_xticks(range(0, 31, 2), range(1, 32, 2))
    ax.set_yticks(range(len(order)), [f"Sensor {s}" if s != -1 else "Speed limit (-1)" for s in order])
    ax.set_xlabel("Day of January (day)")
    ax.set_title("Every sensor with readings is complete; sensors 7, 10 and 17 report nothing")
    fig.colorbar(image, ax=ax, label="Hours with a reading (%)", fraction=0.025)
    save(fig, "03_completeness.png")


def plot_ranges(wide):
    sensors = [s for s in config.SENSOR_KIND if s in wide.columns]
    fig, ax = plt.subplots(figsize=(10, 5.8))
    labels_left = []
    for y, sensor in enumerate(sensors):
        kind = config.SENSOR_KIND[sensor]
        low, high = config.RANGES[kind]
        values = wide[sensor].dropna()
        start, end = (values.min() - low) / (high - low) * 100, (values.max() - low) / (high - low) * 100
        ax.barh(y, 100, color=GRID, height=0.5)
        ax.barh(y, max(end - start, 0.4), left=start, color=BLUE, height=0.5)
        unit = UNIT_BY_KIND[kind]
        labels_left.append("Speed limit" if sensor == -1 else f"Sensor {sensor} ({kind.replace('_', ' ')})")
        ax.text(102, y, f"{values.min():,.1f} to {values.max():,.1f} {unit}  (allowed {low:,.0f} to {high:,.0f})",
                va="center", fontsize=9, color=MUTED)
    ax.set_yticks(range(len(sensors)), labels_left)
    ax.set_xlim(0, 100)
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Position inside the allowed sensor range (% of range)")
    ax.set_title("All observed values (blue) stay inside the allowed range (grey)")
    save(fig, "04_values_vs_allowed_range.png")


def plot_agreement(wide):
    groups = [("lux", "Illuminance (lux)", True), ("water_um", "Water (µm)", False),
              ("temperature_c", "Temperature (°C)", False)]
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 4.1))
    for ax, (group, label, use_log) in zip(axes, groups):
        sensors = config.SENSOR_GROUPS[group]
        median = wide[list(sensors)].median(axis=1)
        for sensor, color in zip(sensors, (BLUE, ORANGE, AQUA)):
            ax.scatter(median, wide[sensor], s=9, color=color, alpha=0.55, linewidths=0, label=f"Sensor {sensor}")
        limits = [min(median.min(), wide[list(sensors)].min().min()), max(median.max(), wide[list(sensors)].max().max())]
        ax.plot(limits, limits, color=MUTED, linewidth=1)
        if use_log:
            ax.set_xscale("symlog", linthresh=1)
            ax.set_yscale("symlog", linthresh=1)
        ax.set_xlabel(f"Median of group: {label}")
        ax.set_ylabel(f"Single sensor: {label}")
        ax.set_title(label.split(" (")[0])
        ax.legend(markerscale=2, fontsize=9, loc="upper left")
    fig.suptitle("Redundant sensors agree, so their median is a safe combined value", x=0.01, ha="left",
                 fontweight="bold", fontsize=13)
    save(fig, "05_redundant_sensors.png")


def plot_poisson(counts):
    mean = counts.mean()
    k = np.arange(0, int(counts.max()) + 1)
    observed = np.array([(counts == value).sum() for value in k])
    expected = stats.poisson.pmf(k, mean) * len(counts)
    fig, ax = plt.subplots(figsize=(8.5, 4.3))
    ax.bar(k, observed, color=BLUE, width=0.5, label="Observed hours")
    ax.plot(k, expected, "o", color=ORANGE, markersize=8, markeredgecolor=SURFACE, markeredgewidth=2,
            label="Pure Poisson randomness")
    ax.set_xticks(k)
    ax.grid(axis="x", visible=False)
    ax.set_xlabel("Near-accidents in one hour (count)")
    ax.set_ylabel("Hours (count)")
    ax.legend()
    ax.set_title(f"Counts match pure randomness (mean {mean:.2f}/h, variance/mean {counts.var() / mean:.2f})")
    save(fig, "06_near_accidents_vs_poisson.png")


def rate_by_limit(table) -> pd.DataFrame:
    risky = table[features.dark_or_ice_mask(table)]
    rows = []
    for limit, group in risky.groupby("speed_limit"):
        total, hours = int(group["near_accidents"].sum()), len(group)
        low = stats.chi2.ppf(0.025, 2 * total) / 2 / hours
        high = stats.chi2.ppf(0.975, 2 * (total + 1)) / 2 / hours
        rows.append({"limit": int(limit), "hours": hours, "rate": total / hours, "low": low, "high": high})
    return pd.DataFrame(rows)


def plot_rate_by_limit(table):
    rates = rate_by_limit(table)
    positions = range(len(rates))
    fig, ax = plt.subplots(figsize=(8.5, 4.4))
    ax.errorbar(positions, rates["rate"], yerr=[rates["rate"] - rates["low"], rates["high"] - rates["rate"]],
                fmt="o", color=BLUE, ecolor=BLUE, elinewidth=2, capsize=0, markersize=9,
                markeredgecolor=SURFACE, markeredgewidth=2)
    ax.axhline(config.REQ1_TARGET_PER_HOUR, color=ORANGE, linewidth=2)
    ax.text(0.5, config.REQ1_TARGET_PER_HOUR - 0.14, "REQ1 target: 1 near-accident/h", color=INK, ha="center")
    ax.set_xticks(list(positions), [f"{r.limit} km/h\n{r.hours} hours" for r in rates.itertuples()])
    ax.set_xlim(-0.6, len(rates) - 0.4)
    ax.set_ylim(0, None)
    ax.grid(axis="x", visible=False)
    ax.set_xlabel("Speed limit in force during dark or black-ice hours (km/h)")
    ax.set_ylabel("Near-accidents per hour (95% interval)")
    ax.set_title("Every limit averages above the target, and slower does not look safer")
    save(fig, "07_rate_by_limit.png")
    return rates


def plot_years(table, table_next):
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.3), gridspec_kw={"width_ratios": [1.5, 1]})
    daily_n = table.groupby("day")["near_accidents"].sum()
    daily_next = table_next.groupby("day")["near_accidents"].sum()
    axes[0].plot(daily_n.index, daily_n.values, color=BLUE, linewidth=2, label="Year N")
    axes[0].plot(daily_next.index, daily_next.values, color=ORANGE, linewidth=2, label="Year N+1")
    axes[0].set_xlabel("Day of January (day)")
    axes[0].set_ylabel("Near-accidents per day (count)")
    axes[0].legend()
    axes[0].set_title(f"Fewer near-accidents in Year N+1 ({int(table['near_accidents'].sum())} to "
                      f"{int(table_next['near_accidents'].sum())})")

    mask = features.dark_or_ice_mask(table)
    x, y = table.loc[mask, "near_accidents"].to_numpy(), table_next.loc[mask, "near_accidents"].to_numpy()
    rng = np.random.default_rng(3)
    axes[1].scatter(x + rng.uniform(-0.2, 0.2, len(x)), y + rng.uniform(-0.2, 0.2, len(y)), s=12, color=BLUE,
                    alpha=0.5, linewidths=0)
    axes[1].set_xlabel("Near-accidents in that hour, Year N (count)")
    axes[1].set_ylabel("Same hour, Year N+1 (count)")
    axes[1].set_title(f"Same hours, unrelated (r = {stats.pearsonr(x, y)[0]:.3f})")
    save(fig, "08_year_comparison.png")


def compute_bands(table) -> dict:
    columns = {"wind_strength_kmh": "wind_strength", "humidity_pct": "humidity_pct", "traffic_cars_s": "traffic_cars_s"}
    bands = {key: [round(float(table[col].quantile(0.05)), 1), round(float(table[col].quantile(0.95)), 1)]
             for key, col in columns.items()}
    config.PARAMETER_BANDS.write_text(json.dumps(bands, indent=2), encoding="utf-8")
    return bands


def markdown_table(frame: pd.DataFrame) -> str:
    lines = ["| " + " | ".join(frame.columns) + " |", "|" + "---|" * len(frame.columns)]
    lines += ["| " + " | ".join(str(v) for v in row) + " |" for row in frame.values.tolist()]
    return "\n".join(lines)


def write_parameter_files(bands):
    table = ranges.ranges_table({key: tuple(value) for key, value in bands.items()})
    table.to_csv(config.DOCS_DIR / "parameter_ranges.csv", index=False, encoding="utf-8-sig")
    text = f"""# Normal and abnormal parameters

*Generated by `analyze_data.py`.*

**How to read this.** "Rule" rows come from the specification and the EU air-quality limits, and they change the speed limit. "Data band" rows only describe what was typical in the January data (5th to 95th percentile). They do not change the speed limit, and they do not say what is safe.

Optimal conditions, where the limit stays at {config.DEFAULT_LIMIT} km/h: at least 0.5 lux of light, no black-ice danger, PM10 at most {config.PM10_LIMIT:g} µg/m³ and NO₂ at most {config.NO2_LIMIT:g} µg/m³.

{markdown_table(table)}

## Notes on units

- SPEC1 states darkness in millilux. The sensors and the GUI use lux: 500 millilux = 0.5 lux.
- The water and temperature rules only apply together. Water alone or frost alone is not black ice.
- `SensorTypes.csv` gives wind strength in `hm/h`. This is read as a typo for km/h.
- `SensorTypes.csv` gives air pressure in `mmHG` with a range of 900 to 1000, which looks like hPa. Air pressure is not used, because its only sensor (17) has no readings.
"""
    (config.DOCS_DIR / "PARAMETER_RANGES.md").write_text(text, encoding="utf-8")


def write_quality_report(checked, report, label_counts, demo_report, demo_error, rates, counts):
    checks = pd.DataFrame([{
        "Check": c.name, "Type": "Hard" if c.severity == "hard" else "Warning",
        "Result": "Pass" if c.passed else ("Fail" if c.severity == "hard" else "Attention"), "Detail": c.detail,
    } for c in checked.checks])
    repairs = pd.DataFrame([{"Repair": k.replace("_", " "), "Count": v} for k, v in demo_report.items()
                            if isinstance(v, int) and k != "rows_read"])
    rate_table = pd.DataFrame([{
        "Limit (km/h)": r.limit, "Hours": r.hours, "Near-accidents/h": f"{r.rate:.2f}",
        "95% interval (near-accidents/h)": f"{r.low:.2f} to {r.high:.2f}",
    } for r in rates.itertuples()])
    text = f"""# Data quality report

*Generated by `analyze_data.py`. Training only starts when every hard check below passes.*

**Verdict: {"fit for training" if checked.passed else "NOT fit for training"}.** The table has one row for each of the 744 hours of January, with no gaps and no impossible values. The data is clean, but it has limited information: see the warnings and plots 6 to 8.

## Validation checks

{markdown_table(checks)}

## What was found and fixed

![Issues found](plots/01_issues_found.png)

The files needed structural repairs. Most value faults listed on slide 17 are not present in the V100 files. Near-accidents: {label_counts['near_accidents']}, real accidents: {label_counts['accidents']}, empty rows: {label_counts['empty_rows']}.

## Does the cleaner work?

The real files have few value faults to repair, so this demo injects slide-17 faults into a copy: spikes, invalid months, empty values, missing sensor ids, a missing day and duplicates.

![Before and after](plots/02_before_after_demo.png)

After cleaning, the temperature differs from the clean table by {demo_error:.3f} °C on average.

{markdown_table(repairs)}

## Is the data complete and plausible?

![Completeness](plots/03_completeness.png)

![Values against allowed range](plots/04_values_vs_allowed_range.png)

![Redundant sensors](plots/05_redundant_sensors.png)

## What the clean data can and cannot tell us

**Near-accidents look random.** Variance/mean is {counts.var() / counts.mean():.2f}. A value of 1 is what pure Poisson randomness gives, so there may be little for a model to learn.

![Near-accidents against Poisson](plots/06_near_accidents_vs_poisson.png)

**Slower limits do not look safer.** The intervals overlap heavily, and 40 km/h has very few hours. This is noise or confounding, not evidence that slowing down is dangerous.

![Rate by limit](plots/07_rate_by_limit.png)

{markdown_table(rate_table)}

**Year N+1 raises a question.** Its sensor file is identical to Year N, but near-accident counts differ and do not correlate hour by hour.

![Year comparison](plots/08_year_comparison.png)
"""
    (config.DOCS_DIR / "DATA_QUALITY.md").write_text(text, encoding="utf-8")


def main():
    raw = data.load_readings(config.READINGS_YEAR_N)
    year_n, year_next = data.build_hourly(config.READINGS_YEAR_N), data.build_hourly(config.READINGS_YEAR_N1)
    accidents = data.load_accidents(config.ACCIDENTS_YEAR_N)
    label_counts = labels.label_report(accidents)
    table = labels.attach_labels(year_n.table, accidents)
    table_next = labels.attach_labels(year_next.table, data.load_accidents(config.ACCIDENTS_YEAR_N1))

    checked = validation.validate(table, year_n.wide, label_counts["near_accidents"],
                                  identical_to_other_year=year_n.wide.equals(year_next.wide))
    config.ARTIFACTS_DIR.mkdir(exist_ok=True)
    (config.ARTIFACTS_DIR / "data_validation.json").write_text(json.dumps(checked.to_dict(), indent=2), encoding="utf-8")

    plot_issues(year_n.report, label_counts)
    demo_report, demo_error = plot_before_after(raw)
    plot_completeness(year_n.wide)
    plot_ranges(year_n.wide)
    plot_agreement(year_n.wide)
    plot_poisson(table["near_accidents"])
    rates = plot_rate_by_limit(table)
    plot_years(table, table_next)

    write_parameter_files(compute_bands(table))
    write_quality_report(checked, year_n.report, label_counts, demo_report, demo_error, rates, table["near_accidents"])
    print(f"Validation passed: {checked.passed}")
    print(f"Demo cleaning error: {demo_error:.3f} °C")
    print(f"Wrote {len(list(config.PLOTS_DIR.glob('*.png')))} plots, DATA_QUALITY.md and PARAMETER_RANGES.md")
    checked.raise_if_failed()


if __name__ == "__main__":
    main()
