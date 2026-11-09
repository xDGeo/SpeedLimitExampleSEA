"""ConfidenceRater: turns measurable checks into a level with plain-language reasons."""
from collections import Counter
from dataclasses import asdict, dataclass

from core import config

HIGH, MEDIUM, LOW = "High", "Medium", "Low"
ORDER = {LOW: 0, MEDIUM: 1, HIGH: 2}
NO_CONFIDENCE = "No confidence"
RULE = "Rule, not a prediction"


@dataclass(frozen=True)
class Confidence:
    level: str
    reasons: list

    def to_dict(self) -> dict:
        return asdict(self)


def _skill_check(skill_pct):
    if skill_pct < config.SKILL_MEANINGFUL_PCT:
        return LOW, f"Low: does not meaningfully beat guessing the average in testing (skill {skill_pct:+.1f}%)"
    if skill_pct < config.SKILL_HIGH_PCT:
        return MEDIUM, f"Medium: only slightly better than guessing the average (skill {skill_pct:+.1f}%)"
    return HIGH, f"High: clearly better than guessing the average in testing (skill {skill_pct:+.1f}%)"


def _agreement_check(mean, low, high):
    width = (high - low) / mean if mean > 0 else float("inf")
    text = f"90% range is {width:.0%} of the predicted rate"
    if width <= config.AGREEMENT_HIGH_WIDTH:
        return HIGH, f"High: the 10 networks agree closely ({text})"
    if width <= config.AGREEMENT_MEDIUM_WIDTH:
        return MEDIUM, f"Medium: the 10 networks partly disagree ({text})"
    return LOW, f"Low: the 10 networks disagree strongly ({text})"


def _support_check(hours):
    text = f"{hours} training hours at this limit"
    if hours >= config.SUPPORT_HIGH_HOURS:
        return HIGH, f"High: {text}"
    if hours >= config.SUPPORT_MEDIUM_HOURS:
        return MEDIUM, f"Medium: only {text}"
    return LOW, f"Low: only {text}"


def _range_check(inside):
    if inside:
        return HIGH, "High: all inputs lie inside the range seen in training"
    return LOW, "Low: some inputs lie outside the range seen in training"


def nn_confidence(skill_pct, mean, low, high, support_hours, inside_training_range) -> Confidence:
    """The overall level is the worst check, because every check has to be earned."""
    checks = [_skill_check(skill_pct), _agreement_check(mean, low, high),
              _support_check(support_hours), _range_check(inside_training_range)]
    return Confidence(min((level for level, _ in checks), key=ORDER.get), [text for _, text in checks])


def llm_confidence(answers, invalid=0, fallback=False) -> Confidence:
    if fallback or not answers:
        return Confidence(NO_CONFIDENCE, ["The LLM gave no usable answer, so a rule-based fallback decided"])
    total = len(answers) + invalid
    agreeing = Counter(answers).most_common(1)[0][1]
    level = HIGH if agreeing == total else MEDIUM if agreeing * 2 > total else LOW
    reasons = [f"{agreeing} of {total} answers from the local LLM agreed"]
    if invalid:
        reasons.append(f"{invalid} of {total} answers failed the output guardrail")
    reasons.append("Agreement shows consistency, not correctness")
    return Confidence(level, reasons)


def rule_confidence() -> Confidence:
    return Confidence(RULE, ["A fixed rule decided this, so there is no uncertainty to estimate"])
