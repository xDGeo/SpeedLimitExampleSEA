from core.decider import Proposal, decide


def test_no_proposals_is_80():
    final = decide([])
    assert final.limit_kmh == 80
    assert final.reduction_kmh == 0
    assert not final.review


def test_single_weather_proposal():
    final = decide([Proposal(60, "weather", "dark")])
    assert final.limit_kmh == 60
    assert final.reduction_kmh == 20


def test_single_air_proposal():
    assert decide([Proposal(70, "air", "pm10")]).limit_kmh == 70


def test_strictest_wins():
    final = decide([Proposal(60, "weather", "dark"), Proposal(50, "air", "pm10")])
    assert final.limit_kmh == 50
    assert final.sources == ["air"]


def test_equal_limits_keep_both_sources():
    final = decide([Proposal(60, "weather", "dark"), Proposal(60, "air", "pm10")])
    assert set(final.sources) == {"weather", "air"}


def test_review_flag_from_any_proposal_is_passed_on():
    final = decide([Proposal(60, "weather", "dark"), Proposal(80, "air", "fallback", review=True)])
    assert final.limit_kmh == 60
    assert final.review


def test_proposal_of_80_is_no_reduction():
    final = decide([Proposal(80, "air", "good air")])
    assert final.limit_kmh == 80
    assert final.reduction_kmh == 0


def test_reasons_are_collected():
    final = decide([Proposal(60, "weather", "dark"), Proposal(70, "air", "pm10")])
    assert final.reasons == ["dark", "pm10"]


def test_default_reason_explains_req3():
    assert "80 km/h" in decide([]).reasons[0]
