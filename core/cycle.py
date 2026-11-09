"""CycleOrchestrator: one decision in a fixed order, with an audit record."""
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from core import air_quality as air_module
from core import config, confidence, features, llm_manager, model, parameter_ranges, router, weather_policy
from core.decider import Proposal, decide


@dataclass
class CycleResult:
    status: str
    limit_kmh: int = None
    reduction_kmh: int = None
    reasons: list = field(default_factory=list)
    route: router.RouteDecision = None
    weather: weather_policy.WeatherDecision = None
    air: llm_manager.AirDecision = None
    air_reading: air_module.AirQuality = None
    review: bool = False
    req1_met: bool = None
    router_confidence: confidence.Confidence = field(default_factory=confidence.rule_confidence)


class SpeedLimitCycle:
    def __init__(self, predictor, llm, air_client, log_path=config.DECISION_LOG):
        self.predictor, self.llm, self.air_client = predictor, llm, air_client
        self.log_path = Path(log_path)
        self.last_limit = None

    def _weather_proposal(self, readings):
        """Any failure of the network ends in a fixed limit and a review flag."""
        try:
            matrix = features.live_matrix(readings, config.CANDIDATE_LIMITS)
            summary = self.predictor.summary(matrix)
            predictions = [
                weather_policy.CandidatePrediction(limit, float(row["mean"]), float(row["low"]),
                                                   float(row["high"]), float(row["p_le_target"]))
                for limit, (_, row) in zip(config.CANDIDATE_LIMITS, summary.iterrows())
            ]
            inside = bool(self.predictor.in_training_range(matrix).all())
            meta = self.predictor.meta
            weather = weather_policy.choose_limit(predictions, meta["skill_pct"], meta["support_hours"], inside)
        except Exception as error:  # a broken model must not stop the cycle
            reason = (f"Neural network unavailable ({error}). Using the fixed limit of "
                      f"{config.NN_FAILURE_LIMIT} km/h")
            return None, Proposal(config.NN_FAILURE_LIMIT, "weather", reason, review=True)
        return weather, Proposal(weather.limit_kmh, "weather", weather.reason, review=not weather.req1_met)

    def _air_proposal(self, override):
        try:
            reading = override or self.air_client.get_forecast()
            decision = self.llm.decide(reading.pm10, reading.no2)
        except air_module.AirQualityUnavailable as error:
            reason = f"Air quality unavailable ({error}). No air-based reduction applied"
            return None, None, Proposal(config.DEFAULT_LIMIT, "air", reason, review=True)
        except llm_manager.InvalidAirInput as error:
            reason = f"Air quality values rejected ({error}). No air-based reduction applied"
            return None, reading, Proposal(config.DEFAULT_LIMIT, "air", reason, review=True)
        reason = f"Air quality ({decision.source}): {decision.reason}"
        return decision, reading, Proposal(decision.limit_kmh, "air", reason, review=decision.review)

    def run(self, readings: dict, air_override=None, source: str = "manual") -> CycleResult:
        try:
            parameter_ranges.validate_readings(readings)
        except parameter_ranges.InvalidReading as error:
            result = CycleResult("rejected", limit_kmh=self.last_limit, reasons=[str(error)], review=True)
            self._log(result, source, readings)
            return result

        route = router.route(router.lux_to_millilux(readings["illuminance_lux"]),
                             readings["water_um"], readings["temperature_c"])
        proposals, weather = [], None
        if route.use_nn:
            weather, proposal = self._weather_proposal(readings)
            proposals.append(proposal)
        air, air_reading, proposal = self._air_proposal(air_override)
        proposals.append(proposal)

        final = decide(proposals)
        self.last_limit = final.limit_kmh
        result = CycleResult(
            "published", final.limit_kmh, final.reduction_kmh, final.reasons, route, weather, air, air_reading,
            final.review, weather.req1_met if weather else None,
        )
        self._log(result, source, readings)
        return result

    def apply_override(self, limit_kmh: int, note: str = "") -> CycleResult:
        if limit_kmh not in config.ALLOWED_LIMITS:
            raise ValueError(f"{limit_kmh} km/h is not an allowed limit")
        self.last_limit = limit_kmh
        reason = f"Operator override to {limit_kmh} km/h" + (f": {note}" if note else "")
        result = CycleResult("override", limit_kmh, config.DEFAULT_LIMIT - limit_kmh, [reason])
        self._log(result, "operator", {})
        return result

    def _log(self, result: CycleResult, source: str, readings: dict) -> None:
        record = {
            "time": datetime.now(timezone.utc).isoformat(), "status": result.status, "source": source,
            "limit_kmh": result.limit_kmh, "reduction_kmh": result.reduction_kmh, "unit": "km/h",
            "readings": readings, "reasons": result.reasons, "review": result.review, "req1_met": result.req1_met,
            "route": asdict(result.route) if result.route else None,
            "predictions": [asdict(p) for p in result.weather.predictions] if result.weather else None,
            "nn_confidence": result.weather.confidence.to_dict() if result.weather else None,
            "air_ug_m3": asdict(result.air_reading) if result.air_reading else None,
            "llm_answers_kmh": result.air.answers if result.air else None,
            "llm_source": result.air.source if result.air else None,
            "llm_confidence": result.air.confidence.to_dict() if result.air else None,
        }
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


def cycle_due(now: float, last_run: float, interval_s: float) -> bool:
    return now - last_run >= max(interval_s, config.MIN_INTERVAL_S)


def build_default_cycle() -> SpeedLimitCycle:
    try:
        predictor = model.Ensemble.load(config.MODEL_FILE)
    except OSError:
        predictor = None
    llm = llm_manager.LLMManager(llm_manager.OllamaBackend())
    return SpeedLimitCycle(predictor, llm, air_module.OpenMeteoClient())
