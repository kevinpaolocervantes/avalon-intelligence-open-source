import pytest

from consensus import ConsensusEngine


def test_weighted_consensus_returns_buy():
    recommendations = [
        {"agent": "Researcher", "decision": "BUY", "confidence": 82},
        {"agent": "Quant Agent", "decision": "BUY", "confidence": 91},
        {"agent": "Market Observer", "decision": "HOLD", "confidence": 78},
        {"agent": "Challenger", "decision": "SELL", "confidence": 35},
    ]

    result = ConsensusEngine().evaluate(recommendations)

    assert result.decision == "BUY"
    assert result.total_agents == 4
    assert result.vote_counts == {
        "BUY": 2,
        "HOLD": 1,
        "SELL": 1,
    }
    assert result.agreement_score == pytest.approx(60.49, abs=0.01)


def test_agent_weight_can_change_final_decision():
    recommendations = [
        {"agent": "Researcher", "decision": "BUY", "confidence": 80},
        {"agent": "Quant Agent", "decision": "BUY", "confidence": 80},
        {
            "agent": "Risk Agent",
            "decision": "SELL",
            "confidence": 100,
            "weight": 2,
        },
    ]

    result = ConsensusEngine().evaluate(recommendations)

    assert result.decision == "SELL"


def test_tie_breaker_defaults_to_hold():
    recommendations = [
        {"agent": "Researcher", "decision": "BUY", "confidence": 100},
        {"agent": "Observer", "decision": "HOLD", "confidence": 100},
    ]

    result = ConsensusEngine().evaluate(recommendations)

    assert result.decision == "HOLD"


def test_vote_alias_is_supported():
    recommendations = [
        {"agent": "Researcher", "vote": "BUY", "confidence": 80},
        {"agent": "Quant Agent", "vote": "BUY", "confidence": 90},
    ]

    result = ConsensusEngine().evaluate(recommendations)

    assert result.decision == "BUY"


@pytest.mark.parametrize(
    "recommendations",
    [
        [],
        [{"agent": "", "decision": "BUY"}],
        [{"agent": "Quant Agent", "decision": "WAIT"}],
        [{"agent": "Quant Agent", "decision": "BUY", "confidence": 101}],
        [{"agent": "Quant Agent", "decision": "BUY", "weight": 0}],
    ],
)
def test_invalid_recommendations_raise_value_error(recommendations):
    with pytest.raises(ValueError):
        ConsensusEngine().evaluate(recommendations)
