import json
from pathlib import Path

from streamlit.testing.v1 import AppTest

from core import cycle, llm_manager
from tests.test_cycle import FakeAir, FakeLLM, FakePredictor

APP = Path(__file__).resolve().parent.parent / "app.py"
RECOMMENDED = "Recommended limit"
NETWORK = "Neural network (dark or black ice)"
LLM = "LLM (air quality)"
RESEARCH = "Research (expert evidence)"


def write_log(tmp_path, *records):
    lines = [json.dumps({"time": "2026-11-10T19:16:23", "review": False, **record}) for record in records]
    (tmp_path / "decisions.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")


def launch(tmp_path, llm=None):
    at = AppTest.from_file(str(APP), default_timeout=30)
    at.session_state["cycle"] = cycle.SpeedLimitCycle(
        predictor=FakePredictor(), llm=llm or FakeLLM(), air_client=FakeAir(),
        log_path=tmp_path / "decisions.jsonl",
    )
    at.run()
    assert not at.exception
    return at


def all_text(at):
    parts = [m.value for m in at.markdown] + [c.value for c in at.caption]
    parts += [w.value for w in at.warning] + [e.value for e in at.error] + [s.value for s in at.success]
    parts += [i.value for i in at.info]
    parts += [f"{m.label} {m.value}" for m in at.metric]
    return "\n".join(parts)


def metrics(at) -> dict:
    return {m.label: m.value for m in at.metric}


def calculate(at):
    at.button(key="calculate").click().run()
    assert not at.exception
    return at


def set_conditions(at, lux, water, temperature):
    at.number_input(key="illuminance_lux").set_value(lux)
    at.number_input(key="water_um").set_value(water)
    at.number_input(key="temperature_c").set_value(temperature)


def set_day(at):
    set_conditions(at, 50000.0, 0.0, 10.0)


def set_icy_day(at):
    set_conditions(at, 5000.0, 1500.0, -3.0)


def test_inputs_show_units(tmp_path):
    at = launch(tmp_path)
    labels = {w.key: w.label for w in at.number_input}
    assert "lux" in labels["illuminance_lux"]
    assert "µm" in labels["water_um"]
    assert "°C" in labels["temperature_c"]
    assert "km/h" in labels["wind_strength_kmh"]
    assert "%" in labels["humidity_pct"]
    assert "cars/s" in labels["traffic_cars_s"]


def test_one_calculate_button(tmp_path):
    at = launch(tmp_path)
    assert at.button(key="calculate").label == "Calculate"


def test_waits_for_calculate(tmp_path):
    at = launch(tmp_path)
    assert "Press Calculate" in all_text(at)
    assert RECOMMENDED not in metrics(at)


def test_clear_day_shows_all_three_speeds(tmp_path):
    at = launch(tmp_path)
    set_day(at)
    calculate(at)
    shown = metrics(at)
    assert shown[RECOMMENDED] == "80 km/h"
    assert shown[NETWORK] == "Not used"
    assert shown[LLM] == "80 km/h"
    assert shown[RESEARCH] == "80 km/h"
    assert "not dark and there is no black ice" in all_text(at)


def test_speeds_not_reductions(tmp_path):
    at = launch(tmp_path)
    set_icy_day(at)
    calculate(at)
    assert not any("Reduction" in label for label in metrics(at))
    columns = " ".join(" ".join(map(str, frame.value.columns)) for frame in at.dataframe)
    assert "Reduction" not in columns
    assert "Sampled speeds: 80 km/h, 80 km/h, 80 km/h" in all_text(at)


def test_icy_day_shows_each_speed_with_justification(tmp_path):
    at = launch(tmp_path)
    set_icy_day(at)
    calculate(at)
    shown, text = metrics(at), all_text(at)
    assert shown[RECOMMENDED] == "60 km/h"
    assert shown[NETWORK] == "60 km/h"
    assert shown[LLM] == "80 km/h"
    assert shown[RESEARCH] == "50 km/h"
    assert "fixed 60 km/h applies" in text
    assert "PM10 10.0 µg/m³" in text
    assert "50 km/h is the fastest limit that can stop within 128 m" in text


def test_explains_how_the_recommendation_is_formed(tmp_path):
    at = launch(tmp_path)
    set_icy_day(at)
    calculate(at)
    text = all_text(at)
    assert "lower of the neural network and the LLM" in text
    assert "Research is shown for comparison and does not change it" in text


def test_dark_night_flags_review_and_low_confidence(tmp_path):
    at = launch(tmp_path)
    set_conditions(at, 0.1, 0.0, 3.0)
    calculate(at)
    text = all_text(at)
    assert metrics(at)[RECOMMENDED] == "60 km/h"
    assert "REQ1 not met" in text
    assert "Confidence: 🔴 Low" in text
    assert "guessing the average" in text


def test_poor_air_lowers_the_recommendation(tmp_path):
    at = launch(tmp_path, llm=FakeLLM(30))
    set_day(at)
    at.toggle(key="air_manual").set_value(True).run()
    at.number_input(key="pm10").set_value(120.0)
    at.number_input(key="no2").set_value(250.0)
    calculate(at)
    shown = metrics(at)
    assert shown[LLM] == "50 km/h"
    assert shown[RECOMMENDED] == "50 km/h"
    assert at.session_state["last_result"].air_reading.source == "Manual override"
    assert "PM10 120.0 µg/m³, NO₂ 250.0 µg/m³" in all_text(at)


def test_changed_conditions_ask_for_recalculation(tmp_path):
    at = launch(tmp_path)
    set_day(at)
    calculate(at)
    assert "Conditions have changed" not in all_text(at)
    at.number_input(key="illuminance_lux").set_value(0.1).run()
    assert "Conditions have changed" in all_text(at)
    calculate(at)
    assert "Conditions have changed" not in all_text(at)


def test_normal_abnormal_badges(tmp_path):
    at = launch(tmp_path)
    at.number_input(key="illuminance_lux").set_value(0.1)
    at.run()
    assert "Abnormal" in all_text(at)


def test_published_limit_says_who_set_it(tmp_path):
    at = launch(tmp_path)
    set_day(at)
    calculate(at)
    assert "Published limit: 80 km/h, set by the system" in all_text(at)


def test_override_publishes_and_keeps_the_recommendation_visible(tmp_path):
    at = launch(tmp_path)
    set_day(at)
    calculate(at)
    at.selectbox(key="override_limit").set_value(60)
    at.button(key="apply_override").click().run()
    assert not at.exception
    text = all_text(at)
    assert at.session_state["cycle"].last_limit == 60
    assert "Published limit: 60 km/h, set by an operator override" in text
    assert "The system recommends 80 km/h" in text
    assert metrics(at)[RECOMMENDED] == "80 km/h"


def test_override_is_explained(tmp_path):
    at = launch(tmp_path)
    assert at.button(key="apply_override").label == "Publish this limit"
    assert "until the next Calculate or timer cycle" in all_text(at)


def test_calculate_after_override_returns_to_the_system(tmp_path):
    at = launch(tmp_path)
    set_day(at)
    calculate(at)
    at.selectbox(key="override_limit").set_value(60)
    at.button(key="apply_override").click().run()
    calculate(at)
    assert "Published limit: 80 km/h, set by the system" in all_text(at)


def test_rejected_input_keeps_the_published_limit(tmp_path):
    at = launch(tmp_path)
    set_day(at)
    calculate(at)
    at.number_input(key="temperature_c").set_value(500.0)
    calculate(at)
    text = all_text(at)
    assert "Input rejected" in text
    assert "80 km/h stays published" in text


def test_history_shows_published_speeds(tmp_path):
    at = launch(tmp_path)
    set_day(at)
    calculate(at)
    columns = " ".join(" ".join(map(str, frame.value.columns)) for frame in at.dataframe)
    assert "Published limit (km/h)" in columns
    assert "Set by" in columns


def test_ollama_unreachable_shows_labelled_fallback(tmp_path):
    backend = llm_manager.OllamaBackend(url="http://localhost:1", timeout=1)
    manager = llm_manager.LLMManager(backend, log_path=tmp_path / "llm.jsonl")
    at = launch(tmp_path, llm=manager)
    set_day(at)
    calculate(at)
    text = all_text(at)
    assert at.session_state["last_result"].air.source == "rule-based fallback"
    assert "Confidence: ⚫ No confidence" in text
    assert "a fixed rule decided" in text
    assert "Operator review needed" in text


def test_research_details_and_sources(tmp_path):
    at = launch(tmp_path)
    set_icy_day(at)
    calculate(at)
    text = all_text(at)
    assert "Stopping-distance evidence" in text
    assert "Crash-effect evidence" in text
    assert "https://" in text
    columns = " ".join(" ".join(map(str, t.value.columns)) for t in at.table)
    assert "Stopping distance (m)" in columns
    assert "Injury crashes (%)" in columns
    assert "Limit (km/h)" in columns


def test_new_page_shows_the_last_published_limit_from_the_log(tmp_path):
    write_log(tmp_path, {"status": "published", "source": "manual", "limit_kmh": 60},
              {"status": "override", "source": "operator", "limit_kmh": 40},
              {"status": "rejected", "source": "manual", "limit_kmh": 40})
    at = launch(tmp_path)
    assert "Published limit: 40 km/h, set by an operator override" in all_text(at)
    assert at.session_state["cycle"].last_limit == 40


def test_new_page_with_system_limit_in_the_log(tmp_path):
    write_log(tmp_path, {"status": "published", "source": "scheduler", "limit_kmh": 70})
    at = launch(tmp_path)
    assert "Published limit: 70 km/h, set by the system" in all_text(at)


def test_override_list_starts_at_the_published_limit(tmp_path):
    write_log(tmp_path, {"status": "published", "source": "manual", "limit_kmh": 60})
    assert launch(tmp_path).selectbox(key="override_limit").value == 60


def test_override_list_starts_at_80_without_history(tmp_path):
    assert launch(tmp_path).selectbox(key="override_limit").value == 80
