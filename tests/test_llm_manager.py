import json
import math

import pytest

from core import llm_manager as lm


class FakeBackend:
    model = "fake"

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def generate(self, prompt, seed):
        self.calls.append((prompt, seed))
        reply = self.replies[(len(self.calls) - 1) % len(self.replies)]
        if isinstance(reply, Exception):
            raise reply
        return reply


def reply(reduction, reason="ok"):
    return json.dumps({"reduction_kmh": reduction, "reason": reason})


def manager(replies, tmp_path, **kwargs):
    backend = FakeBackend(replies)
    return lm.LLMManager(backend, log_path=tmp_path / "llm.jsonl", **kwargs), backend


def test_unanimous_answer(tmp_path):
    m, _ = manager([reply(20, "Clear exceedance")], tmp_path)
    decision = m.decide(120, 250)
    assert decision.reduction_kmh == 20
    assert decision.limit_kmh == 60
    assert decision.confidence.level == "High"
    assert decision.answers == [20, 20, 20]
    assert decision.reason == "Clear exceedance"
    assert decision.source == "llm"
    assert not decision.review


def test_majority_wins(tmp_path):
    m, _ = manager([reply(20), reply(10), reply(20)], tmp_path)
    decision = m.decide(120, 250)
    assert decision.reduction_kmh == 20
    assert decision.confidence.level == "Medium"


def test_tie_takes_larger_reduction(tmp_path):
    m, _ = manager([reply(0), reply(10), reply(30)], tmp_path)
    decision = m.decide(120, 250)
    assert decision.reduction_kmh == 30
    assert decision.confidence.level == "Low"


def test_three_different_seeds(tmp_path):
    m, backend = manager([reply(0)], tmp_path)
    m.decide(10, 10)
    assert len({seed for _, seed in backend.calls}) == 3


def test_same_reading_is_cached(tmp_path):
    m, backend = manager([reply(0)], tmp_path)
    m.decide(10, 10)
    m.decide(10, 10)
    assert len(backend.calls) == 3


@pytest.mark.parametrize("value", [0, 10, 20, 30, 40])
def test_output_guardrail_accepts_legal_reductions(value):
    assert lm.parse_reply(reply(value))[0] == value


@pytest.mark.parametrize("text", [
    reply(15), reply(-10), reply(80), reply(True), reply("ten"),
    json.dumps({"reason": "no number"}), "not json at all", "",
])
def test_output_guardrail_rejects_illegal_replies(text):
    with pytest.raises(lm.InvalidReply):
        lm.parse_reply(text)


@pytest.mark.parametrize("pm10, no2", [(-1, 10), (10, -1), (2001, 10), (math.nan, 10), ("high", 10)])
def test_input_guardrail(tmp_path, pm10, no2):
    m, backend = manager([reply(0)], tmp_path)
    with pytest.raises(lm.InvalidAirInput):
        m.decide(pm10, no2)
    assert backend.calls == []


def test_partly_invalid_replies_still_decide(tmp_path):
    m, _ = manager([reply(20), "garbage", reply(20)], tmp_path)
    decision = m.decide(120, 250)
    assert decision.reduction_kmh == 20
    assert decision.confidence.level == "Medium"


def test_all_invalid_uses_labelled_fallback(tmp_path):
    m, _ = manager(["garbage"], tmp_path)
    decision = m.decide(120, 250)
    assert decision.source == "rule-based fallback"
    assert decision.review
    assert decision.confidence.level == "No confidence"


def test_ollama_down_uses_fallback(tmp_path):
    m, _ = manager([lm.LLMUnavailable("connection refused")], tmp_path)
    decision = m.decide(20, 40)
    assert decision.source == "rule-based fallback"
    assert decision.reduction_kmh == 0
    assert decision.review


@pytest.mark.parametrize("pm10, no2, low, high", [
    (20, 40, 0, 0), (55, 90, 0, 10), (120, 250, 20, 30), (400, 500, 30, 40), (0, 0, 0, 0),
])
def test_fallback_rule_matches_golden_ranges(pm10, no2, low, high):
    assert low <= lm.rule_based_reduction(pm10, no2) <= high


def test_failed_decision_not_cached(tmp_path):
    backend = FakeBackend([lm.LLMUnavailable("down")])
    m = lm.LLMManager(backend, log_path=tmp_path / "llm.jsonl")
    m.decide(20, 40)
    backend.replies = [reply(0)]
    assert m.decide(20, 40).source == "llm"


def test_every_call_is_logged(tmp_path):
    m, _ = manager([reply(20), "garbage", reply(20)], tmp_path)
    m.decide(120, 250)
    lines = [json.loads(line) for line in (tmp_path / "llm.jsonl").read_text().splitlines()]
    assert len(lines) == 3
    assert lines[0].keys() >= {"time", "model", "seed", "prompt", "reply", "valid"}
    assert [line["valid"] for line in lines] == [True, False, True]


def test_prompt_contains_only_numbers_as_input():
    prompt = lm.build_prompt(123.4, 56.7)
    assert "123.4" in prompt and "56.7" in prompt


def test_ollama_backend_request_format():
    sent = {}
    def post(url, body, timeout):
        sent.update(url=url, body=body)
        return {"message": {"content": reply(10)}}
    backend = lm.OllamaBackend(post=post)
    assert json.loads(backend.generate("hello", seed=5))["reduction_kmh"] == 10
    assert sent["url"].endswith("/api/chat")
    assert sent["body"]["model"] == "qwen3:8b"
    assert sent["body"]["options"]["seed"] == 5
    assert sent["body"]["format"]["properties"]["reduction_kmh"]["enum"] == [0, 10, 20, 30, 40]


def test_ollama_backend_connection_error():
    def post(url, body, timeout):
        raise OSError("refused")
    with pytest.raises(lm.LLMUnavailable):
        lm.OllamaBackend(post=post).generate("hello", seed=1)


@pytest.mark.live
@pytest.mark.parametrize("pm10, no2, low, high", [
    (20, 40, 0, 10), (55, 90, 0, 20), (120, 250, 10, 40), (400, 500, 20, 40), (0, 0, 0, 10),
])
def test_live_ollama_golden_ranges(tmp_path, pm10, no2, low, high):
    backend = lm.OllamaBackend()
    if not backend.available():
        pytest.skip("Ollama is not running")
    decision = lm.LLMManager(backend, log_path=tmp_path / "llm.jsonl").decide(pm10, no2)
    assert decision.source == "llm"
    assert low <= decision.reduction_kmh <= high
