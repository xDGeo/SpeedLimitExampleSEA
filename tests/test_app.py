from pathlib import Path

from streamlit.testing.v1 import AppTest

from core import cycle, llm_manager
from tests.test_cycle import FakeAir, FakeLLM, FakePredictor


APP = Path(__file__).resolve().parent.parent / "app.py"


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
    parts += [str(m.value) for m in at.metric]
    return "\n".join(parts)


def press(at):
    at.button(key="set_limit").click().run()
    assert not at.exception
    return at


def set_day(at):
    at.number_input(key="illuminance_lux").set_value(50000.0)
    at.number_input(key="water_um").set_value(0.0)
    at.number_input(key="temperature_c").set_value(10.0)


def test_inputs_show_units(tmp_path):
    at = launch(tmp_path)
    labels = {w.key: w.label for w in at.number_input}
    assert "lux" in labels["illuminance_lux"]
    assert "µm" in labels["water_um"]
    assert "°C" in labels["temperature_c"]
    assert "km/h" in labels["wind_strength_kmh"]
    assert "%" in labels["humidity_pct"]
    assert "cars/s" in labels["traffic_cars_s"]


def test_clear_day_shows_80(tmp_path):
    at = launch(tmp_path)
    set_day(at)
    press(at)
    assert at.session_state["last_result"].limit_kmh == 80
    assert "80 km/h" in all_text(at)


def test_dark_shows_confidence_and_flag(tmp_path):
    at = launch(tmp_path)
    at.number_input(key="illuminance_lux").set_value(0.1)
    at.number_input(key="water_um").set_value(0.0)
    press(at)
    text = all_text(at)
    assert at.session_state["last_result"].limit_kmh == 60
    assert "REQ1 not met" in text
    assert "Low" in text
    assert "guessing the average" in text


def test_normal_abnormal_badges(tmp_path):
    at = launch(tmp_path)
    at.number_input(key="illuminance_lux").set_value(0.1)
    at.run()
    assert "Abnormal" in all_text(at)


def test_manual_air_override(tmp_path):
    at = launch(tmp_path, llm=FakeLLM(30))
    set_day(at)
    at.toggle(key="air_manual").set_value(True).run()
    at.number_input(key="pm10").set_value(120.0)
    at.number_input(key="no2").set_value(250.0)
    press(at)
    result = at.session_state["last_result"]
    assert result.limit_kmh == 50
    assert result.air_reading.source == "Manual override"
    assert "µg/m³" in all_text(at)


def test_operator_override(tmp_path):
    at = launch(tmp_path)
    set_day(at)
    press(at)
    at.selectbox(key="override_limit").set_value(60)
    at.button(key="apply_override").click().run()
    assert not at.exception
    assert at.session_state["cycle"].last_limit == 60


def test_history_has_units(tmp_path):
    at = launch(tmp_path)
    set_day(at)
    press(at)
    assert any("km/h" in " ".join(map(str, df.value.columns)) for df in at.dataframe)


def test_ollama_unreachable_shows_labelled_fallback(tmp_path):
    backend = llm_manager.OllamaBackend(url="http://localhost:1", timeout=1)
    manager = llm_manager.LLMManager(backend, log_path=tmp_path / "llm.jsonl")
    at = launch(tmp_path, llm=manager)
    set_day(at)
    press(at)
    text = all_text(at)
    result = at.session_state["last_result"]
    assert result.air.source == "rule-based fallback"
    assert result.review
    assert "No confidence" in text
    assert "rule-based" in text
    assert "Operator review needed" in text


def test_research_panel_sits_beside_the_decision(tmp_path):
    at = launch(tmp_path)
    at.number_input(key="illuminance_lux").set_value(5000.0)
    at.number_input(key="water_um").set_value(1500.0)
    at.number_input(key="temperature_c").set_value(-3.0)
    press(at)
    text = all_text(at)
    assert at.session_state["last_result"].limit_kmh == 60
    assert any(item.value == "Research suggests" for item in at.subheader)
    assert "50 km/h" in text
    assert "not used to set" in text
    assert "Stopping-distance evidence" in text
    assert "Crash-effect evidence" in text
    assert "https://" in text


def test_research_table_has_units(tmp_path):
    at = launch(tmp_path)
    set_day(at)
    press(at)
    columns = " ".join(" ".join(map(str, frame.value.columns)) for frame in at.dataframe)
    assert "Stopping distance (m)" in columns
    assert "Injury crashes (%)" in columns


def test_research_panel_waits_for_a_decision(tmp_path):
    at = launch(tmp_path)
    assert "Press Set limit now to see what research suggests" in all_text(at)
