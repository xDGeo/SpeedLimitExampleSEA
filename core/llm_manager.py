"""LLMManager: guardrails, repeated sampling and a gateway log around the local LLM."""
import http.client
import json
import math
import urllib.request
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from core import config, confidence

SOURCE_LLM = "llm"
SOURCE_FALLBACK = "rule-based fallback"


class LLMUnavailable(Exception):
    pass


class InvalidReply(ValueError):
    pass


class InvalidAirInput(ValueError):
    pass


@dataclass(frozen=True)
class AirDecision:
    reduction_kmh: int
    limit_kmh: int
    confidence: confidence.Confidence
    answers: list
    reason: str
    source: str
    review: bool


def build_prompt(pm10: float, no2: float) -> str:
    """The only variable parts are two numbers, so nothing can be injected."""
    return (
        "You decide whether a highway speed limit of 80 km/h must be reduced because of air pollution. "
        f"The EU limits are PM10 {config.PM10_LIMIT:g} µg/m³ and NO2 {config.NO2_LIMIT:g} µg/m³.\n"
        f"Worst forecast values for the coming hours: PM10 {pm10:.1f} µg/m³, NO2 {no2:.1f} µg/m³.\n"
        "Rules: if both values are within their limits, the reduction must be 0. "
        "A slight exceedance needs a small reduction, a severe exceedance a large one. "
        "Lower speed reduces emissions but costs drivers time.\n"
        'Reply as JSON: {"reduction_kmh": one of 0, 10, 20, 30, 40, "reason": one short sentence}.'
    )


def parse_reply(text: str) -> tuple:
    """Output guardrail: only a legal reduction passes."""
    try:
        data = json.loads(text)
    except (TypeError, ValueError) as error:
        raise InvalidReply("Reply is not JSON") from error
    reduction = data.get("reduction_kmh") if isinstance(data, dict) else None
    if isinstance(reduction, bool) or not isinstance(reduction, int) or reduction not in config.ALLOWED_REDUCTIONS:
        raise InvalidReply(f"Illegal reduction: {reduction!r}")
    return reduction, str(data.get("reason", "")).strip()


def rule_based_reduction(pm10: float, no2: float) -> int:
    """Used only when the LLM cannot answer. Always labelled as a fallback."""
    worst_ratio = max(pm10 / config.PM10_LIMIT, no2 / config.NO2_LIMIT)
    for ratio, reduction in ((1.0, 0), (1.5, 10), (2.5, 20), (4.0, 30)):
        if worst_ratio <= ratio:
            return reduction
    return 40


def _majority(answers) -> int:
    counts = Counter(answers)
    top = max(counts.values())
    return max(value for value, count in counts.items() if count == top)


def _http_post_json(url: str, body: dict, timeout: float) -> dict:
    request = urllib.request.Request(url, data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


class OllamaBackend:
    def __init__(self, url=config.OLLAMA_URL, model=config.OLLAMA_MODEL, timeout=config.OLLAMA_TIMEOUT_S, post=None):
        self.url, self.model, self.timeout = url, model, timeout
        self.post = post or _http_post_json

    def generate(self, prompt: str, seed: int) -> str:
        body = {
            "model": self.model, "stream": False, "think": False,
            "messages": [{"role": "user", "content": prompt}],
            "options": {"seed": seed, "temperature": 0.7},
            "format": {
                "type": "object",
                "properties": {
                    "reduction_kmh": {"type": "integer", "enum": list(config.ALLOWED_REDUCTIONS)},
                    "reason": {"type": "string"},
                },
                "required": ["reduction_kmh", "reason"],
            },
        }
        try:
            return self.post(f"{self.url}/api/chat", body, self.timeout)["message"]["content"]
        except (OSError, ValueError, KeyError, TypeError, http.client.HTTPException) as error:
            raise LLMUnavailable(str(error)) from error

    def available(self) -> bool:
        try:
            with urllib.request.urlopen(f"{self.url}/api/tags", timeout=2):
                return True
        except OSError:
            return False


class LLMManager:
    def __init__(self, backend, log_path=config.LLM_LOG, samples=config.LLM_SAMPLES):
        self.backend, self.log_path, self.samples = backend, Path(log_path), samples
        self._cache = {}

    @staticmethod
    def _check_input(value):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) \
                or not 0 <= value <= config.AIR_INPUT_MAX:
            raise InvalidAirInput(f"Impossible air quality value: {value!r}")

    def _log(self, prompt, seed, reply, valid, error=None):
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        record = {"time": datetime.now(timezone.utc).isoformat(), "model": getattr(self.backend, "model", "?"),
                  "seed": seed, "prompt": prompt, "reply": reply, "valid": valid, "error": error}
        with open(self.log_path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _sample(self, prompt):
        answers, reasons, invalid = [], {}, 0
        for seed in range(1, self.samples + 1):
            try:
                reply = self.backend.generate(prompt, seed)
            except LLMUnavailable as error:
                self._log(prompt, seed, None, False, str(error))
                invalid += self.samples - seed + 1
                break
            try:
                reduction, reason = parse_reply(reply)
            except InvalidReply as error:
                self._log(prompt, seed, reply, False, str(error))
                invalid += 1
                continue
            self._log(prompt, seed, reply, True)
            answers.append(reduction)
            reasons.setdefault(reduction, reason)
        return answers, reasons, invalid

    def decide(self, pm10, no2) -> AirDecision:
        self._check_input(pm10)
        self._check_input(no2)
        key = (round(float(pm10), 1), round(float(no2), 1))
        if key in self._cache:
            return self._cache[key]

        answers, reasons, invalid = self._sample(build_prompt(float(pm10), float(no2)))
        if not answers:
            reduction = rule_based_reduction(float(pm10), float(no2))
            return AirDecision(reduction, config.DEFAULT_LIMIT - reduction,
                               confidence.llm_confidence([], fallback=True), [],
                               "The local LLM gave no usable answer, so a fixed rule decided",
                               SOURCE_FALLBACK, True)

        reduction = _majority(answers)
        decision = AirDecision(reduction, config.DEFAULT_LIMIT - reduction,
                               confidence.llm_confidence(answers, invalid=invalid), answers,
                               reasons[reduction], SOURCE_LLM, False)
        self._cache[key] = decision
        return decision
