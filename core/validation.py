"""DataValidator: the gate between cleaning and training."""
from dataclasses import asdict, dataclass

import pandas as pd

from core import config


class DataValidationError(Exception):
    pass


@dataclass
class Check:
    name: str
    passed: bool
    severity: str  # "hard" stops training, "warning" is only reported
    detail: str


@dataclass
class ValidationResult:
    checks: list

    @property
    def passed(self) -> bool:
        return all(check.passed for check in self.checks if check.severity == "hard")

    def raise_if_failed(self):
        if not self.passed:
            failed = [c.name for c in self.checks if c.severity == "hard" and not c.passed]
            raise DataValidationError(f"Data failed validation: {', '.join(failed)}")

    def to_dict(self) -> dict:
        return {"passed": self.passed, "checks": [asdict(check) for check in self.checks]}


def _range_violations(table: pd.DataFrame) -> dict:
    violations = {}
    for column, kind in config.TABLE_COLUMN_KIND.items():
        if column in table:
            low, high = config.RANGES[kind]
            count = int(((table[column] < low) | (table[column] > high)).sum())
            if count:
                violations[column] = count
    return violations


def _worst_sensor_correlation(wide: pd.DataFrame):
    """Lowest pairwise correlation inside the redundant groups. Constant sensors are skipped."""
    worst = None
    for group in config.REDUNDANT_GROUPS:
        sensors = [s for s in config.SENSOR_GROUPS[group] if s in wide.columns]
        if len(sensors) > 1:
            value = wide[sensors].corr().min().min()
            if pd.notna(value):
                worst = value if worst is None else min(worst, value)
    return worst


def validate(table: pd.DataFrame, sensor_wide: pd.DataFrame = None, source_near_total: int = None,
             expected_hours: int = 744, identical_to_other_year: bool = None) -> ValidationResult:
    checks = []

    def add(name, passed, detail, severity="hard"):
        checks.append(Check(name, bool(passed), severity, detail))

    add("complete_hours", len(table) == expected_hours, f"{len(table)} of {expected_hours} hours")
    duplicates = int(table.duplicated(["day", "hour"]).sum())
    add("unique_hours", duplicates == 0, f"{duplicates} duplicated hours")
    missing = int(table.isna().sum().sum())
    add("no_missing_values", missing == 0, f"{missing} missing values")
    violations = _range_violations(table)
    add("values_in_range", not violations, f"Out of range: {violations or 'none'}")
    illegal = int((~table["speed_limit"].isin(config.ALLOWED_LIMITS)).sum())
    add("legal_speed_limits", illegal == 0, f"{illegal} hours with an illegal limit (km/h)")
    personal = [c for c in table.columns if "licence" in c.lower() or "plate" in c.lower()]
    add("no_personal_data", not personal, f"Personal columns: {personal or 'none'}")
    negative = int((table["near_accidents"] < 0).sum())
    add("labels_valid", negative == 0, f"{negative} negative near-accident counts")
    if source_near_total is not None:
        total = int(table["near_accidents"].sum())
        add("labels_reconcile", total == source_near_total,
            f"{total} near-accidents in the table, {source_near_total} in the source file")
    if sensor_wide is not None:
        worst = _worst_sensor_correlation(sensor_wide)
        add("redundant_sensors_agree", worst is None or worst >= 0.9,
            f"Lowest correlation between redundant sensors: {worst if worst is None else round(worst, 3)}")

    add("only_january", False, "All readings are from January, so other seasons are unknown", "warning")
    support = table["speed_limit"].value_counts().sort_index()
    low = {int(k): int(v) for k, v in support.items() if v < config.LOW_SUPPORT_HOURS}
    add("support_per_limit", not low, f"Limits with under {config.LOW_SUPPORT_HOURS} hours: {low or 'none'}", "warning")
    if identical_to_other_year is not None:
        add("years_differ", not identical_to_other_year,
            "Year N+1 sensor readings are identical to Year N" if identical_to_other_year
            else "The two years differ", "warning")
    return ValidationResult(checks)
