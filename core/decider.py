"""SpeedLimitDecider: strictest proposal wins, otherwise 80 km/h (REQ3)."""
from dataclasses import dataclass

from core import config


@dataclass(frozen=True)
class Proposal:
    limit_kmh: int
    source: str
    reason: str
    review: bool = False


@dataclass(frozen=True)
class FinalDecision:
    limit_kmh: int
    reduction_kmh: int
    reasons: list
    sources: list
    review: bool


def decide(proposals) -> FinalDecision:
    if not proposals:
        reason = f"No reason to reduce: {config.DEFAULT_LIMIT} km/h applies (REQ3)"
        return FinalDecision(config.DEFAULT_LIMIT, 0, [reason], ["rule"], False)
    limit = min(proposal.limit_kmh for proposal in proposals)
    return FinalDecision(
        limit, config.DEFAULT_LIMIT - limit,
        [proposal.reason for proposal in proposals],
        [proposal.source for proposal in proposals if proposal.limit_kmh == limit],
        any(proposal.review for proposal in proposals),
    )
