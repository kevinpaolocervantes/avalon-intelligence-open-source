from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from typing import Iterable, Mapping


VALID_DECISIONS = {"BUY", "HOLD", "SELL"}


@dataclass(frozen=True)
class ConsensusResult:
    """Structured result returned by the Consensus Engine."""

    decision: str
    agreement_score: float
    weighted_support: dict[str, float]
    vote_counts: dict[str, int]
    total_agents: int
    supporting_agents: list[str]
    dissenting_agents: list[str]
    explanation: list[str]

    def to_dict(self) -> dict:
        """Return the result as a JSON-serializable dictionary."""
        return asdict(self)


class ConsensusEngine:
    """Combine multiple agent recommendations into one transparent decision."""

    def __init__(self, tie_breaker: str = "HOLD") -> None:
        tie_breaker = tie_breaker.strip().upper()

        if tie_breaker not in VALID_DECISIONS:
            raise ValueError(
                f"tie_breaker must be one of {sorted(VALID_DECISIONS)}"
            )

        self.tie_breaker = tie_breaker

    def evaluate(
        self,
        recommendations: Iterable[Mapping[str, object]],
    ) -> ConsensusResult:
        """Evaluate agent recommendations and return a consensus result."""

        normalized = [
            self._normalize_recommendation(item)
            for item in recommendations
        ]

        if not normalized:
            raise ValueError("At least one recommendation is required.")

        vote_counts = Counter(
            recommendation["decision"]
            for recommendation in normalized
        )

        weighted_support = {
            decision: 0.0
            for decision in VALID_DECISIONS
        }

        for recommendation in normalized:
            contribution = (
                recommendation["weight"]
                * recommendation["confidence"]
                / 100
            )
            weighted_support[recommendation["decision"]] += contribution

        final_decision = self._select_decision(weighted_support)
        total_support = sum(weighted_support.values())

        agreement_score = (
            weighted_support[final_decision] / total_support * 100
            if total_support
            else 0.0
        )

        supporting_agents = [
            recommendation["agent"]
            for recommendation in normalized
            if recommendation["decision"] == final_decision
        ]

        dissenting_agents = [
            f'{recommendation["agent"]} ({recommendation["decision"]})'
            for recommendation in normalized
            if recommendation["decision"] != final_decision
        ]

        explanation = self._build_explanation(
            final_decision=final_decision,
            agreement_score=agreement_score,
            total_agents=len(normalized),
            supporting_agents=supporting_agents,
            dissenting_agents=dissenting_agents,
            vote_counts=vote_counts,
        )

        return ConsensusResult(
            decision=final_decision,
            agreement_score=round(agreement_score, 2),
            weighted_support={
                decision: round(weighted_support[decision], 4)
                for decision in sorted(VALID_DECISIONS)
            },
            vote_counts={
                decision: vote_counts.get(decision, 0)
                for decision in sorted(VALID_DECISIONS)
            },
            total_agents=len(normalized),
            supporting_agents=supporting_agents,
            dissenting_agents=dissenting_agents,
            explanation=explanation,
        )

    def _select_decision(
        self,
        weighted_support: dict[str, float],
    ) -> str:
        highest_support = max(weighted_support.values())

        leaders = [
            decision
            for decision, support in weighted_support.items()
            if support == highest_support
        ]

        if len(leaders) == 1:
            return leaders[0]

        if self.tie_breaker in leaders:
            return self.tie_breaker

        return sorted(leaders)[0]

    @staticmethod
    def _normalize_recommendation(
        recommendation: Mapping[str, object],
    ) -> dict[str, object]:
        agent = str(recommendation.get("agent", "")).strip()
        decision = str(
            recommendation.get(
                "decision",
                recommendation.get("vote", ""),
            )
        ).strip().upper()

        if not agent:
            raise ValueError(
                "Every recommendation must include an agent name."
            )

        if decision not in VALID_DECISIONS:
            raise ValueError(
                f"Invalid decision '{decision}' from {agent}. "
                f"Expected one of {sorted(VALID_DECISIONS)}."
            )

        try:
            confidence = float(recommendation.get("confidence", 100))
            weight = float(recommendation.get("weight", 1))
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Confidence and weight for {agent} must be numeric."
            ) from exc

        if not 0 <= confidence <= 100:
            raise ValueError(
                f"Confidence for {agent} must be between 0 and 100."
            )

        if weight <= 0:
            raise ValueError(
                f"Weight for {agent} must be greater than zero."
            )

        return {
            "agent": agent,
            "decision": decision,
            "confidence": confidence,
            "weight": weight,
        }

    @staticmethod
    def _build_explanation(
        final_decision: str,
        agreement_score: float,
        total_agents: int,
        supporting_agents: list[str],
        dissenting_agents: list[str],
        vote_counts: Counter,
    ) -> list[str]:
        explanation = [
            (
                f"{len(supporting_agents)} of {total_agents} agents "
                f"support {final_decision}."
            ),
            f"Weighted agreement is {agreement_score:.1f}%.",
            "Supporting agents: " + ", ".join(supporting_agents) + ".",
        ]

        if dissenting_agents:
            explanation.append(
                "Dissenting views: "
                + ", ".join(dissenting_agents)
                + "."
            )
        else:
            explanation.append(
                "No dissenting recommendations were recorded."
            )

        if vote_counts.get("BUY", 0) and vote_counts.get("SELL", 0):
            explanation.append(
                "The group contains directly opposing BUY and SELL views."
            )

        if agreement_score < 50:
            explanation.append(
                "Consensus is weak and should be reviewed before action."
            )
        elif agreement_score < 70:
            explanation.append(
                "Consensus is moderate and includes meaningful uncertainty."
            )
        else:
            explanation.append(
                "Consensus is strong based on weighted agent support."
            )

        return explanation
