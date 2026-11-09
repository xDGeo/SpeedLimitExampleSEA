"""Streamlit GUI: the operational stage."""
import json
import time

import pandas as pd
import streamlit as st

from core import air_quality, config, cycle
from core import parameter_ranges as ranges

st.set_page_config(page_title="SpeedLimit", page_icon="🚦", layout="wide")

DEFAULTS = {
    "illuminance_lux": 20000.0, "water_um": 0.0, "temperature_c": 5.0,
    "wind_strength_kmh": 10.0, "humidity_pct": 80.0, "traffic_cars_s": 15.0,
}
SCENARIOS = {
    "Clear day": {"illuminance_lux": 50000.0, "water_um": 0.0, "temperature_c": 10.0},
    "Dark night": {"illuminance_lux": 0.1, "water_um": 0.0, "temperature_c": 3.0},
    "Black ice in daylight": {"illuminance_lux": 5000.0, "water_um": 1500.0, "temperature_c": -3.0},
    "Icy night": {"illuminance_lux": 0.1, "water_um": 2000.0, "temperature_c": -8.0},
}
LEVEL_ICON = {"High": "🟢", "Medium": "🟡", "Low": "🔴", "No confidence": "⚫", "Rule, not a prediction": "⚙️"}
BADGE = {"Normal": "🟢 Normal", "Abnormal": "🟠 Abnormal", "Unknown": "⚪ Unknown"}

state = st.session_state
if "cycle" not in state:
    state["cycle"] = cycle.build_default_cycle()
system = state["cycle"]
state.setdefault("last_result", None)
state.setdefault("last_auto_run", 0.0)
for key, value in DEFAULTS.items():
    state.setdefault(key, value)


def apply_scenario(name):
    state.update(SCENARIOS[name])


def current_readings() -> dict:
    return {key: state[key] for key in DEFAULTS}


def air_override():
    if state.get("air_manual"):
        return air_quality.manual_reading(state["pm10"], state["no2"])
    return None


def run_cycle(source: str):
    with st.spinner("Asking the local LLM about air quality..."):
        state["last_result"] = system.run(current_readings(), air_override=air_override(), source=source)


def read_history(limit=15) -> pd.DataFrame:
    try:
        lines = system.log_path.read_text(encoding="utf-8").splitlines()[-limit:]
    except OSError:
        lines = []
    rows = []
    for record in map(json.loads, reversed(lines)):
        rows.append({
            "Time (UTC)": record["time"][:19].replace("T", " "),
            "Limit (km/h)": record["limit_kmh"],
            "Reduction (km/h)": record["reduction_kmh"],
            "Status": record["status"],
            "Triggered by": record["source"],
            "Operator review": "yes" if record["review"] else "no",
        })
    return pd.DataFrame(rows, columns=["Time (UTC)", "Limit (km/h)", "Reduction (km/h)", "Status",
                                       "Triggered by", "Operator review"])


def show_badge(key: str, context: dict, bands: dict):
    result = ranges.classify(key, state[key], context=context, bands=bands)
    st.caption(f"{BADGE[result.status]}: {result.reason}")


def number(key: str, step: float, fmt: str, context: dict, bands: dict):
    param = ranges.PARAMETERS[key]
    st.number_input(f"{param.label} ({param.unit})", key=key, step=step, format=fmt)
    show_badge(key, context, bands)


def show_confidence(title: str, rating):
    st.markdown(f"**{title}: {LEVEL_ICON.get(rating.level, '')} {rating.level}**")
    for reason in rating.reasons:
        st.markdown(f"- {reason}")


def show_result(result):
    if result is None:
        st.info("Enter the conditions and press **Set limit now**.")
        return
    if result.status == "rejected":
        st.error(f"Input rejected: {result.reasons[0]}")
        kept = "no limit has been published yet" if result.limit_kmh is None else f"{result.limit_kmh} km/h stays in force"
        st.markdown(f"The limit was not changed: {kept}.")
        return

    left, right = st.columns(2)
    left.metric("Speed limit", f"{result.limit_kmh} km/h")
    right.metric("Reduction", f"{result.reduction_kmh} km/h")
    for reason in result.reasons:
        st.markdown(f"- {reason}")
    if result.status == "override":
        return
    if result.req1_met is False:
        st.warning("REQ1 not met: no limit is predicted to keep near-accidents at or below "
                   "1 per hour. An operator should review this limit.")
    elif result.review:
        st.warning("Operator review needed: see the reasons above.")

    st.subheader("Confidence and reasons")
    if result.route is not None:
        conditions = [name for name, active in (("dark", result.route.dark), ("black ice", result.route.black_ice)) if active]
        show_confidence("Router", result.router_confidence)
        st.caption("Conditions found: " + (", ".join(conditions) if conditions else "not dark, no black ice"))
    if result.weather:
        show_confidence("Neural network", result.weather.confidence)
        st.dataframe(pd.DataFrame([{
            "Limit (km/h)": p.limit_kmh,
            "Predicted near-accidents/h": round(p.mean, 2),
            "90% range of networks (near-accidents/h)": f"{p.low:.2f} to {p.high:.2f}",
            "Share of networks at or below 1/h (%)": round(p.p_le_target * 100),
        } for p in result.weather.predictions]), hide_index=True)
    if result.air_reading:
        st.markdown(f"**Air quality** ({result.air_reading.source}): "
                    f"PM10 {result.air_reading.pm10:.1f} µg/m³, NO₂ {result.air_reading.no2:.1f} µg/m³")
    if result.air:
        show_confidence("LLM (local Ollama)", result.air.confidence)
        answers = ", ".join(f"{value} km/h" for value in result.air.answers) or "none"
        st.caption(f"Reductions sampled: {answers}. Source: {result.air.source}.")


@st.fragment(run_every=(max(state.get("interval_s", 3600), 5) if state.get("auto_run") else None))
def scheduler():
    if not state.get("auto_run"):
        st.caption("Auto-run is off.")
        return
    interval = max(state.get("interval_s", 3600), 5)
    now = time.time()
    if now - state["last_auto_run"] >= interval:
        state["last_auto_run"] = now
        run_cycle("scheduler")
        st.rerun(scope="app")
    st.caption(f"Next automatic cycle in about {max(0, int(interval - (now - state['last_auto_run'])))} s.")


st.title("SpeedLimit control")
st.caption("Sets the limit from light, weather and air quality. An MVP for a case study, not for real roads.")

skill = getattr(getattr(system, "predictor", None), "meta", {}).get("skill_pct") if system.predictor else None
if system.predictor is None:
    st.error("No trained model found. Run train.py. Until then, dark or icy conditions use a fixed 60 km/h.")
elif skill is not None and skill <= 0:
    st.warning(f"Model warning: in testing the neural network does not beat guessing the average "
               f"(skill {skill:+.1f}%). Treat its limits as advisory.")

bands = ranges.load_bands()
inputs, decision = st.columns([1, 1.5], gap="large")

with inputs:
    st.subheader("Conditions")
    scenario_columns = st.columns(len(SCENARIOS))
    for column, name in zip(scenario_columns, SCENARIOS):
        column.button(name, on_click=apply_scenario, args=(name,), key=f"scenario_{name}")
    readings_now = current_readings()
    number("illuminance_lux", 100.0, "%.3f", {}, bands)
    number("water_um", 100.0, "%.1f", {"temperature_c": readings_now["temperature_c"]}, bands)
    number("temperature_c", 1.0, "%.1f", {"water_um": readings_now["water_um"]}, bands)
    number("wind_strength_kmh", 1.0, "%.1f", {}, bands)
    number("humidity_pct", 1.0, "%.1f", {}, bands)
    number("traffic_cars_s", 1.0, "%.1f", {}, bands)

    st.subheader("Air quality")
    st.toggle("Enter air quality manually (for demos)", key="air_manual")
    if state.get("air_manual"):
        state.setdefault("pm10", 20.0)
        state.setdefault("no2", 40.0)
        number("pm10", 5.0, "%.1f", {}, bands)
        number("no2", 5.0, "%.1f", {}, bands)
    else:
        st.caption("Uses the Open-Meteo forecast for Vienna: the worst PM10 and NO₂ (µg/m³) of the next "
                   f"{config.FORECAST_HOURS} hours.")

    pressed = st.button("Set limit now", key="set_limit", type="primary")

    st.subheader("Regular operation")
    st.toggle("Auto-run on a timer", key="auto_run")
    state.setdefault("interval_s", 3600)
    st.number_input("Interval (seconds, 3600 = hourly)", key="interval_s", min_value=5, step=5)
    scheduler()

if pressed:
    run_cycle("manual")

with decision:
    st.subheader("Decision")
    show_result(state["last_result"])

    st.subheader("Operator override")
    columns = st.columns([2, 1])
    columns[0].selectbox("Limit to publish", config.ALLOWED_LIMITS, key="override_limit",
                         format_func=lambda limit: f"{limit} km/h")
    columns[1].write("")
    if columns[1].button("Apply override", key="apply_override"):
        state["last_result"] = system.apply_override(state["override_limit"])
        st.rerun()

    st.subheader("History")
    st.dataframe(read_history(), hide_index=True)

with st.expander("Normal and abnormal values for each parameter"):
    st.markdown("Rules change the limit. Data bands only describe what was typical in January and do not.")
    st.dataframe(ranges.ranges_table(bands), hide_index=True)
