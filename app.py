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
LEVEL_ICON = {"High": "🟢", "Medium": "🟡", "Low": "🔴", "No confidence": "⚫", "Rule, not a prediction": "⚙️",
              "Not applicable": "➖"}
BADGE = {"Normal": "🟢 Normal", "Abnormal": "🟠 Abnormal", "Unknown": "⚪ Unknown"}
SET_BY = {"manual": "Calculate", "scheduler": "Timer", "operator": "Operator override"}
SCHEDULER_POLL_S = 2

RECOMMENDED = "Recommended limit"
NETWORK = "Neural network (dark or black ice)"
LLM = "LLM (air quality)"
RESEARCH = "Research (expert evidence)"

state = st.session_state
if "cycle" not in state:
    state["cycle"] = cycle.build_default_cycle()
system = state["cycle"]


def last_published_from_log():
    """The limit currently in force, so a newly opened page shows it even if another session set it."""
    try:
        lines = system.log_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    for record in map(json.loads, reversed(lines)):
        if record.get("status") in ("published", "override") and record.get("limit_kmh") is not None:
            return {"limit": record["limit_kmh"], "by": "operator" if record["source"] == "operator" else "system"}
    return None


for key, value in {"last_result": None, "last_auto_run": 0.0, "calc_inputs": None,
                   "interval_s": 3600, **DEFAULTS}.items():
    state.setdefault(key, value)
if "published" not in state:
    state["published"] = last_published_from_log()
    if state["published"] and system.last_limit is None:
        system.last_limit = state["published"]["limit"]
if "override_limit" not in state:
    state["override_limit"] = state["published"]["limit"] if state["published"] else config.DEFAULT_LIMIT


# ---------- state helpers ----------

def apply_scenario(name):
    state.update(SCENARIOS[name])


def current_readings() -> dict:
    return {key: state[key] for key in DEFAULTS}


def input_snapshot() -> tuple:
    air = (state.get("pm10"), state.get("no2")) if state.get("air_manual") else None
    return tuple(sorted(current_readings().items())), air


def air_override():
    if state.get("air_manual"):
        return air_quality.manual_reading(state["pm10"], state["no2"])
    return None


def run_cycle(source: str):
    result = system.run(current_readings(), air_override=air_override(), source=source)
    state["last_result"] = result
    state["calc_inputs"] = input_snapshot()
    if result.status == "published":
        state["published"] = {"limit": result.limit_kmh, "by": "system"}


def publish_override(limit: int):
    system.apply_override(limit)
    state["published"] = {"limit": limit, "by": "operator"}


def read_history(limit=15) -> pd.DataFrame:
    columns = ["Time (UTC)", "Published limit (km/h)", "Set by", "Status", "Operator review"]
    try:
        lines = system.log_path.read_text(encoding="utf-8").splitlines()[-limit:]
    except OSError:
        lines = []
    rows = [{
        "Time (UTC)": record["time"][:19].replace("T", " "),
        "Published limit (km/h)": record["limit_kmh"],
        "Set by": SET_BY.get(record["source"], record["source"]),
        "Status": "input rejected" if record["status"] == "rejected" else record["status"],
        "Operator review": "yes" if record["review"] else "no",
    } for record in map(json.loads, reversed(lines))]
    return pd.DataFrame(rows, columns=columns)


# ---------- small display helpers ----------

def level_text(rating) -> str:
    return f"Confidence: {LEVEL_ICON.get(rating.level, '')} {rating.level}"


def show_reasons(title: str, rating):
    st.markdown(f"**{title}: {LEVEL_ICON.get(rating.level, '')} {rating.level}**")
    for reason in rating.reasons:
        st.markdown(f"- {reason}")


def number(key: str, step: float, fmt: str, context: dict, bands: dict):
    param = ranges.PARAMETERS[key]
    st.number_input(f"{param.label} ({param.unit})", key=key, step=step, format=fmt)
    result = ranges.classify(key, state[key], context=context, bands=bands)
    st.caption(f"{BADGE[result.status]}: {result.reason}")


def card(label: str, value: str, confidence: str, justification: str):
    with st.container(border=True):
        st.metric(label, value)
        st.caption(confidence)
        st.markdown(justification)


# ---------- the three results ----------

def network_card(result):
    weather = result.weather
    if not result.route.use_nn:
        card(NETWORK, "Not used", "Not needed under these conditions",
             "Not used: it is not dark and there is no black ice.")
    elif weather is None:
        card(NETWORK, f"{config.FALLBACK_LIMIT} km/h", "Confidence: none, the network did not run",
             f"The network is unavailable, so the fixed {config.FALLBACK_LIMIT} km/h applies.")
    elif weather.req1_met:
        chosen = next(p for p in weather.predictions if p.limit_kmh == weather.limit_kmh)
        card(NETWORK, f"{weather.limit_kmh} km/h", level_text(weather.confidence),
             f"{weather.limit_kmh} km/h is the fastest limit predicted to keep near-accidents at or below "
             f"1 per hour ({chosen.mean:.2f}/h).")
    else:
        card(NETWORK, f"{weather.limit_kmh} km/h", level_text(weather.confidence),
             f"No limit keeps near-accidents at or below 1 per hour, so the fixed {weather.limit_kmh} km/h applies.")


def llm_card(result):
    air, reading = result.air, result.air_reading
    if air is None:
        card(LLM, "Not available", "Confidence: none, the LLM was not asked",
             "Air-quality data was unavailable or invalid, so the LLM gave no recommendation.")
        return
    card(LLM, f"{air.limit_kmh} km/h", level_text(air.confidence),
         f"PM10 {reading.pm10:.1f} µg/m³, NO₂ {reading.no2:.1f} µg/m³: {air.reason}")


def research_card(result):
    advice = result.research
    card(RESEARCH, f"{advice.limit_kmh} km/h",
         f"Evidence: {LEVEL_ICON.get(advice.stopping_evidence.level, '')} {advice.stopping_evidence.level}",
         advice.headline)


# ---------- details ----------

def network_details(result):
    route = result.route
    conditions = [name for name, active in (("dark", route.dark), ("black ice", route.black_ice)) if active]
    st.markdown(f"Conditions found by the router: {', '.join(conditions) or 'not dark, no black ice'}.")
    if result.weather is None:
        return
    show_reasons("Neural network confidence", result.weather.confidence)
    st.dataframe(pd.DataFrame([{
        "Limit (km/h)": p.limit_kmh,
        "Predicted near-accidents/h": round(p.mean, 2),
        "90% range of the 10 networks (/h)": f"{p.low:.2f} to {p.high:.2f}",
        "Networks at or below 1/h (%)": round(p.p_le_target * 100),
    } for p in result.weather.predictions]), hide_index=True)


def llm_details(result):
    air, reading = result.air, result.air_reading
    if reading:
        st.markdown(f"Air quality ({reading.source}): PM10 {reading.pm10:.1f} µg/m³, NO₂ {reading.no2:.1f} µg/m³. "
                    f"EU limits: PM10 {config.PM10_LIMIT:g} µg/m³, NO₂ {config.NO2_LIMIT:g} µg/m³.")
    if air is None:
        return
    show_reasons("LLM confidence", air.confidence)
    speeds = ", ".join(f"{config.DEFAULT_LIMIT - value} km/h" for value in air.answers) or "none"
    st.caption(f"Sampled speeds: {speeds}. Source: {air.source}.")


def _pct(central, low, high) -> str:
    return f"{central:+.0f} ({low:+.0f} to {high:+.0f})" if central else "0"


def research_details(result):
    advice = result.research
    for reason in advice.reasons:
        st.markdown(f"- {reason}")
    show_reasons("Stopping-distance evidence", advice.stopping_evidence)
    show_reasons("Crash-effect evidence", advice.crash_evidence)
    if advice.air_evidence:
        show_reasons("Air-quality evidence", advice.air_evidence)
    st.markdown(f"**Stopping within {advice.available_distance_m:g} m**")
    st.table(pd.DataFrame([{
        "Limit (km/h)": c.limit_kmh,
        "Stopping distance (m)": f"{c.stopping_m:.1f}",
        "Stops in time": "yes" if c.fits else "no",
    } for c in advice.candidates]))
    st.markdown("**Expected change compared with 80 km/h**")
    st.table(pd.DataFrame([{
        "Limit (km/h)": c.limit_kmh,
        "Mean speed (km/h)": f"{c.mean_speed_change_kmh:+.1f}",
        "Injury crashes (%)": _pct(c.injury_pct, c.injury_low_pct, c.injury_high_pct),
        "Deaths (%)": _pct(c.killed_pct, c.killed_low_pct, c.killed_high_pct),
    } for c in advice.candidates]))
    st.caption("Typical value, with the published range in brackets. A calculation, not a measurement on this road.")
    for caveat in advice.caveats:
        st.caption(caveat)
    st.markdown("**Sources**")
    for source in advice.sources:
        st.markdown(f"- {source.citation} [Link]({source.url})")


# ---------- sections ----------

def published_banner(result):
    published = state["published"]
    if published is None:
        st.info("No limit has been published yet.")
    elif published["by"] == "operator":
        recommended = (f" The system recommends {result.limit_kmh} km/h."
                       if result is not None and result.status == "published" else "")
        st.info(f"Published limit: {published['limit']} km/h, set by an operator override.{recommended}")
    else:
        st.success(f"Published limit: {published['limit']} km/h, set by the system.")


def recommendation(result):
    if result is None:
        st.info("Press Calculate to see the recommendations for these conditions.")
        return
    if result.status == "rejected":
        kept = (f"{result.limit_kmh} km/h stays published" if result.limit_kmh is not None
                else "no limit has been published yet")
        st.error(f"Input rejected: {result.reasons[0]}. Nothing was changed: {kept}.")
        return
    if state["calc_inputs"] != input_snapshot():
        st.warning("Conditions have changed since the last calculation. Press Calculate to update.")

    st.metric(RECOMMENDED, f"{result.limit_kmh} km/h")
    st.caption("The recommended limit is the lower of the neural network and the LLM "
               "(80 km/h when neither gives a reason to reduce). "
               "Research is shown for comparison and does not change it.")
    if result.req1_met is False:
        st.warning("REQ1 not met: no limit is predicted to keep near-accidents at or below 1 per hour. "
                   "Operator review needed.")
    elif result.review:
        st.warning("Operator review needed: " + " ".join(result.reasons))

    left, middle, right = st.columns(3)
    with left:
        network_card(result)
    with middle:
        llm_card(result)
    with right:
        research_card(result)

    with st.expander("Neural network details"):
        network_details(result)
    with st.expander("LLM details"):
        llm_details(result)
    with st.expander("Research details and sources"):
        research_details(result)


def override_section(result):
    st.subheader("Publish a different limit")
    st.caption("Use this when you disagree with the recommendation, for example after an accident or during "
               "road works. The override stays published until the next Calculate or timer cycle.")
    columns = st.columns([2, 1])
    columns[0].selectbox("Limit to publish", config.ALLOWED_LIMITS, key="override_limit",
                         format_func=lambda limit: f"{limit} km/h")
    columns[1].write("")
    if columns[1].button("Publish this limit", key="apply_override"):
        publish_override(state["override_limit"])
        st.rerun()


@st.fragment(run_every=(SCHEDULER_POLL_S if state.get("auto_run") else None))
def scheduler():
    """Polls often and asks whether a cycle is due, so a slightly early tick cannot skip one."""
    if state.get("auto_run") and cycle.cycle_due(time.time(), state["last_auto_run"], state["interval_s"]):
        state["last_auto_run"] = time.time()
        run_cycle("scheduler")
        st.rerun(scope="app")


# ---------- page ----------

st.title("SpeedLimit control")
st.caption("Recommends a highway speed limit from light, weather and air quality. "
           "An MVP for a case study, not for real roads.")

if system.predictor is None:
    st.error("No trained model found. Run train.py. Until then, dark or icy conditions use a fixed 60 km/h.")
else:
    skill = system.predictor.meta.get("skill_pct")
    if skill is not None and skill < config.SKILL_MEANINGFUL_PCT:
        st.caption(f"⚠️ In testing, the neural network does not meaningfully beat guessing the average "
                   f"(skill {skill:+.1f}%), so its confidence is always Low.")

bands = ranges.load_bands()
inputs, results = st.columns([1, 2.2], gap="large")

with inputs:
    st.subheader("1. Conditions")
    scenario_columns = st.columns(2)
    for index, name in enumerate(SCENARIOS):
        scenario_columns[index % 2].button(name, on_click=apply_scenario, args=(name,),
                                           key=f"scenario_{name}", use_container_width=True)
    readings_now = current_readings()
    number("illuminance_lux", 100.0, "%.3f", {}, bands)
    number("water_um", 100.0, "%.1f", {"temperature_c": readings_now["temperature_c"]}, bands)
    number("temperature_c", 1.0, "%.1f", {"water_um": readings_now["water_um"]}, bands)
    number("wind_strength_kmh", 1.0, "%.1f", {}, bands)
    number("humidity_pct", 1.0, "%.1f", {}, bands)
    number("traffic_cars_s", 1.0, "%.1f", {}, bands)

    st.subheader("2. Air quality")
    st.toggle("Enter air quality manually (for demos)", key="air_manual")
    if state.get("air_manual"):
        state.setdefault("pm10", 20.0)
        state.setdefault("no2", 40.0)
        number("pm10", 5.0, "%.1f", {}, bands)
        number("no2", 5.0, "%.1f", {}, bands)
    else:
        st.caption("Uses the Open-Meteo forecast for Vienna: the worst PM10 and NO₂ (µg/m³) of the next "
                   f"{config.FORECAST_HOURS} hours.")

    with st.expander("Run automatically on a timer"):
        st.toggle("Auto-run on a timer", key="auto_run")
        st.number_input("Interval (seconds, 3600 = hourly)", key="interval_s", min_value=config.MIN_INTERVAL_S,
                        step=5)
        if state.get("auto_run"):
            st.caption(f"On: a new calculation about every {state['interval_s']} s while this page stays open.")
        else:
            st.caption("Off.")
    scheduler()

with results:
    header, button = st.columns([3, 1])
    header.subheader("3. Recommendation")
    if button.button("Calculate", key="calculate", type="primary", use_container_width=True):
        with st.spinner("Calculating. The local LLM can take about 10 seconds..."):
            run_cycle("manual")
    published_banner(state["last_result"])
    recommendation(state["last_result"])
    override_section(state["last_result"])
    st.subheader("History")
    st.dataframe(read_history(), hide_index=True)

with st.expander("Normal and abnormal values for each parameter"):
    st.markdown("Rules change the limit. Data bands only describe what was typical in January and do not.")
    st.dataframe(ranges.ranges_table(bands), hide_index=True)
