"""WeatherPolicy: turns candidate predictions into a limit, with an output guardrail."""
import math
from dataclasses import dataclass

from core import config, confidence


class InvalidPrediction(ValueError):
    pass


@dataclass(frozen=True)
class CandidatePrediction:
    limit_kmh: int
    mean: float
    low: float
    high: float
    p_le_target: float


@dataclass(frozen=True)
class WeatherDecision:
    limit_kmh: int
    reduction_kmh: int
    req1_met: bool
    predictions: list
    confidence: confidence.Confidence
    reason: str


def _check(predictions) -> None:
    if not predictions:
        raise InvalidPrediction("No predictions")
    for prediction in predictions:
        if prediction.limit_kmh not in config.CANDIDATE_LIMITS:
            raise InvalidPrediction(f"{prediction.limit_kmh} km/h is not a candidate limit")
        if not math.isfinite(prediction.mean) or prediction.mean < 0:
            raise InvalidPrediction(f"Impossible prediction {prediction.mean} near-accidents/h")


def choose_limit(predictions, skill_pct, support_hours, inside_training_range) -> WeatherDecision:
    """Highest limit meeting REQ1, otherwise a fixed limit with an operator review."""
    _check(predictions)
    target = config.REQ1_TARGET_PER_HOUR
    meeting = [p for p in predictions if p.mean <= target]
    if meeting:
        chosen = max(meeting, key=lambda p: p.limit_kmh)
        reason = (f"Dark or black ice: {chosen.limit_kmh} km/h is the highest limit predicted "
                  f"at or below {target:g} near-accidents/h ({chosen.mean:.2f}/h)")
    else:
        chosen = next((p for p in predictions if p.limit_kmh == config.FALLBACK_LIMIT), None)
        if chosen is None:
            raise InvalidPrediction(f"No prediction for the fixed limit of {config.FALLBACK_LIMIT} km/h")
        reason = (f"REQ1 not met: no limit is predicted at or below {target:g} near-accidents/h. "
                  f"Using the fixed limit of {chosen.limit_kmh} km/h, the limit with the most evidence "
                  f"in dark or black-ice hours")
    rating = confidence.nn_confidence(skill_pct, chosen.mean, chosen.low, chosen.high,
                                      support_hours.get(chosen.limit_kmh, 0), inside_training_range)
    return WeatherDecision(chosen.limit_kmh, config.DEFAULT_LIMIT - chosen.limit_kmh, bool(meeting),
                           list(predictions), rating, reason)
