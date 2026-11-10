"""Expected values come from the tables in reports/Speed limit advisor evidence.md."""
import pytest

from core import air_quality, research_advisor as ra
from tests.helpers import DAY_READINGS, NIGHT_READINGS

DAY_ICE = {**DAY_READINGS, "water_um": 1500.0, "temperature_c": -3.0}
NIGHT_ICE = {**NIGHT_READINGS, "water_um": 1500.0, "temperature_c": -3.0}
NIGHT_WET = {**NIGHT_READINGS, "water_um": 1500.0, "temperature_c": 5.0}
DAY_WET = {**DAY_READINGS, "water_um": 500.0}
POOR_AIR = air_quality.AirQuality(120.0, 250.0, "test")
GOOD_AIR = air_quality.AirQuality(20.0, 40.0, "test")


def candidate(advice, limit):
    return next(c for c in advice.candidates if c.limit_kmh == limit)


@pytest.mark.parametrize("speed, friction, expected", [
    (80, 0.80, 87.0), (80, 0.70, 91.5), (60, 0.70, 61.9), (40, 0.15, 69.7),
    (50, 0.15, 100.3), (60, 0.15, 136.1), (80, 0.15, 223.4), (40, 0.08, 106.4),
])
def test_stopping_distance_matches_published_formula(speed, friction, expected):
    assert ra.stopping_distance_m(speed, friction) == pytest.approx(expected, abs=0.1)


def test_shorter_reaction_time_shortens_distance():
    assert ra.stopping_distance_m(80, 0.8, reaction_s=1.5) < ra.stopping_distance_m(80, 0.8)


@pytest.mark.parametrize("limit, change", [(80, 0.0), (70, -2.5), (60, -5.0), (50, -7.5), (40, -10.0)])
def test_posted_cut_reaches_mean_speed_at_one_quarter(limit, change):
    assert ra.mean_speed_change_kmh(limit) == pytest.approx(change)


@pytest.mark.parametrize("limit, beta, compliance, ratio", [
    (70, 0.065, 0.25, 0.850), (60, 0.034, 0.25, 0.844), (50, 0.034, 0.25, 0.775),
    (40, 0.034, 0.25, 0.712), (60, 0.034, 0.17, 0.891), (60, 0.06, 0.55, 0.517),
])
def test_crash_change_matches_report_table(limit, beta, compliance, ratio):
    assert ra.crash_change_pct(limit, beta, compliance) == pytest.approx((ratio - 1) * 100, abs=0.1)


def test_no_limit_change_means_no_crash_change():
    assert ra.crash_change_pct(80, 0.065, 0.25) == 0


@pytest.mark.parametrize("readings, surface, limit", [
    (DAY_READINGS, "dry", 80),
    (DAY_WET, "wet", 80),
    (NIGHT_READINGS, "dry", 80),
    (NIGHT_WET, "wet", 70),
    (DAY_ICE, "black ice", 50),
    (NIGHT_ICE, "black ice", 40),
])
def test_limit_is_highest_that_stops_within_sight(readings, surface, limit):
    advice = ra.advise(readings)
    assert advice.surface == surface
    assert advice.limit_kmh == limit
    assert advice.reduction_kmh == 80 - limit


def test_water_below_ice_threshold_counts_as_wet_not_ice():
    assert ra.advise({**DAY_READINGS, "water_um": 1000.0, "temperature_c": -1.0}).surface == "wet"


def test_darkness_shortens_available_distance():
    assert ra.advise(NIGHT_READINGS).available_distance_m == 91
    assert ra.advise(DAY_READINGS).available_distance_m == 128


def test_stress_case_on_very_low_friction():
    assert ra.advise(DAY_ICE).stress_limit_kmh == 40
    assert ra.advise(NIGHT_ICE).stress_limit_kmh is None


def test_every_allowed_limit_is_tabulated_with_range():
    advice = ra.advise(DAY_ICE)
    assert [c.limit_kmh for c in advice.candidates] == [40, 50, 60, 70, 80]
    row = candidate(advice, 60)
    assert row.stopping_m == pytest.approx(136.1, abs=0.1)
    assert not row.fits
    assert candidate(advice, 50).fits
    assert row.injury_pct == pytest.approx(-15.6, abs=0.1)
    assert row.injury_low_pct == pytest.approx(-10.9, abs=0.1)
    assert row.injury_high_pct == pytest.approx(-48.3, abs=0.1)
    assert row.killed_pct == pytest.approx(-27.7, abs=0.1)


def test_clear_day_evidence():
    advice = ra.advise(DAY_READINGS)
    assert advice.stopping_evidence.level == "High"
    assert advice.crash_evidence.level == "Not applicable"


def test_darkness_alone_is_weak_evidence():
    evidence = ra.advise(NIGHT_READINGS).stopping_evidence
    assert evidence.level == "Low"
    assert any("Darkness alone" in reason for reason in evidence.reasons)


def test_black_ice_is_medium_evidence_with_friction_warning():
    evidence = ra.advise(DAY_ICE).stopping_evidence
    assert evidence.level == "Medium"
    assert any("0.05" in reason for reason in evidence.reasons)


def test_darkness_on_wet_road_is_medium():
    assert ra.advise(NIGHT_WET).stopping_evidence.level == "Medium"


@pytest.mark.parametrize("readings, level", [(NIGHT_WET, "Medium"), (DAY_ICE, "Low"), (NIGHT_ICE, "Low")])
def test_crash_estimate_weakens_at_low_limits(readings, level):
    assert ra.advise(readings).crash_evidence.level == level


def test_poor_air_is_flagged_but_never_lowers_the_limit():
    advice = ra.advise(DAY_READINGS, air=POOR_AIR)
    assert advice.limit_kmh == 80
    assert advice.air_evidence.level == "Low"
    assert any("below 80 km/h" in reason for reason in advice.air_evidence.reasons)


def test_good_or_missing_air_has_no_air_finding():
    assert ra.advise(DAY_READINGS, air=GOOD_AIR).air_evidence is None
    assert ra.advise(DAY_READINGS).air_evidence is None


def test_advice_never_claims_to_predict_near_accidents():
    caveats = " ".join(ra.advise(NIGHT_ICE).caveats)
    assert "near-accidents" in caveats
    assert "not used to set" in caveats


def test_sources_are_cited_with_links():
    sources = ra.advise(DAY_ICE).sources
    assert len(sources) >= 5
    assert all(source.citation and source.url.startswith("http") for source in sources)


def test_reasons_show_units():
    text = " ".join(ra.advise(DAY_ICE).reasons)
    assert "km/h" in text and " m" in text


@pytest.mark.parametrize("readings, words", [
    (DAY_READINGS, ["Dry road in daylight", "80 km/h", "128 m"]),
    (NIGHT_READINGS, ["Dry road in darkness", "80 km/h", "91 m"]),
    (NIGHT_WET, ["Wet road in darkness", "70 km/h", "91 m"]),
    (DAY_ICE, ["Black ice in daylight", "50 km/h is the fastest limit that can stop within 128 m"]),
    (NIGHT_ICE, ["Black ice in darkness", "40 km/h", "91 m"]),
])
def test_headline_is_one_short_justification(readings, words):
    headline = ra.advise(readings).headline
    assert all(word in headline for word in words)
    assert len(headline) < 160


def test_headline_mentions_air_quality_when_poor():
    assert "Air quality alone does not justify going below 80 km/h" in ra.advise(DAY_READINGS, air=POOR_AIR).headline
    assert "Air quality" not in ra.advise(DAY_READINGS, air=GOOD_AIR).headline
