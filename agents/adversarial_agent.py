"""
Avalon Adversarial Agent

Stress-tests a recommendation before action by identifying weaknesses,
unsupported assumptions, contradictory evidence, missing information,
alternative explanations, and possible reasoning biases.

The Adversarial Agent does not make the final decision. Its role is to improve
decision quality by challenging the recommendation and making unresolved risks
visible to downstream agents or human reviewers.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Iterable, Mapping, Optional


@dataclass(frozen=True)
class AdversarialReview:
    """Structured output produced by the Adversarial Agent."""

    agent: str
    status: str
    verdict: str
    risk_level: str
    risks_identified: list[str] = field(default_factory=list)
    critical_questions: list[str] = field(default_factory=list)
    alternative_explanations: list[str] = field(default_factory=list)
    potential_biases: list[str] = field(default_factory=list)
    missing_information: list[str] = field(default_factory=list)
    challenge_score: int = 0

    def __post_init__(self) -> None:
        if not 0 <= self.challenge_score <= 100:
            raise ValueError("Challenge score must be between 0 and 100.")

    def as_dict(self) -> dict:
        """Return the review as a JSON-serializable dictionary."""
        return asdict(self)


class AdversarialAgent:
    """
    Challenges a recommendation before action.

    The agent evaluates:

    - Strength and clarity of the thesis
    - Quantity of supporting evidence
    - Contradictory evidence
    - Explicit and hidden assumptions
    - Missing information
    - Confidence calibration
    - Alternative explanations
    - Possible cognitive or analytical biases

    The agent is domain-agnostic and can be used for business decisions,
    finance, healthcare, research, engineering, policy, product strategy,
    forecasting, risk reviews, and other decision workflows.
    """

    name = "Adversarial Agent"

    def review(
        self,
        recommendation: Mapping[str, object],
    ) -> AdversarialReview:
        """
        Stress-test a structured recommendation.

        Expected input fields may include:

            thesis:
                The main conclusion or recommendation.

            confidence:
                A number from 0 to 100.

            supporting_evidence:
                Evidence supporting the thesis.

            contradictions:
                Evidence that conflicts with the thesis.

            assumptions:
                Claims treated as true but not fully verified.

            gaps:
                Known missing information.

            recommendation:
                Optional action or decision label.

        Returns:
            A structured AdversarialReview.
        """

        if not isinstance(recommendation, Mapping):
            raise TypeError("Recommendation must be a mapping or dictionary.")

        thesis = str(
            recommendation.get(
                "thesis",
                recommendation.get("summary", ""),
            )
        ).strip()

        action = str(
            recommendation.get(
                "recommendation",
                recommendation.get("decision", ""),
            )
        ).strip()

        confidence = self._normalize_confidence(
            recommendation.get("confidence", 0)
        )

        evidence = self._clean_items(
            recommendation.get(
                "supporting_evidence",
                recommendation.get("evidence", []),
            )
        )

        contradictions = self._clean_items(
            recommendation.get("contradictions", [])
        )

        assumptions = self._clean_items(
            recommendation.get("assumptions", [])
        )

        gaps = self._clean_items(
            recommendation.get(
                "gaps",
                recommendation.get("missing_information", []),
            )
        )

        risks: list[str] = []
        questions: list[str] = []
        alternative_explanations: list[str] = []
        potential_biases: list[str] = []

        self._review_thesis(
            thesis=thesis,
            action=action,
            risks=risks,
            questions=questions,
        )

        self._review_confidence(
            confidence=confidence,
            evidence_count=len(evidence),
            contradiction_count=len(contradictions),
            gap_count=len(gaps),
            risks=risks,
            questions=questions,
            potential_biases=potential_biases,
        )

        self._review_evidence(
            evidence=evidence,
            contradictions=contradictions,
            risks=risks,
            questions=questions,
        )

        self._review_assumptions(
            assumptions=assumptions,
            risks=risks,
            questions=questions,
        )

        self._review_gaps(
            gaps=gaps,
            risks=risks,
            questions=questions,
        )

        self._generate_alternative_explanations(
            thesis=thesis,
            evidence=evidence,
            contradictions=contradictions,
            alternatives=alternative_explanations,
        )

        risks = self._deduplicate(risks)
        questions = self._deduplicate(questions)
        alternative_explanations = self._deduplicate(
            alternative_explanations
        )
        potential_biases = self._deduplicate(potential_biases)

        challenge_score = self._calculate_challenge_score(
            risks=risks,
            contradictions=contradictions,
            assumptions=assumptions,
            gaps=gaps,
            confidence=confidence,
        )

        risk_level = self._determine_risk_level(challenge_score)

        verdict = self._build_verdict(
            risk_level=risk_level,
            risks=risks,
            contradictions=contradictions,
            gaps=gaps,
        )

        return AdversarialReview(
            agent=self.name,
            status="review_complete",
            verdict=verdict,
            risk_level=risk_level,
            risks_identified=risks,
            critical_questions=questions,
            alternative_explanations=alternative_explanations,
            potential_biases=potential_biases,
            missing_information=gaps,
            challenge_score=challenge_score,
        )

    @staticmethod
    def _normalize_confidence(value: object) -> int:
        try:
            confidence = int(float(value))
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Confidence must be a number between 0 and 100."
            ) from exc

        if not 0 <= confidence <= 100:
            raise ValueError(
                "Confidence must be between 0 and 100."
            )

        return confidence

    @staticmethod
    def _clean_items(items: object) -> list[str]:
        """
        Normalize list-like input, remove empty values, and eliminate
        duplicates while preserving order.
        """

        if items is None:
            return []

        if isinstance(items, str):
            items = [items]

        if not isinstance(items, Iterable):
            raise TypeError(
                "Evidence, assumptions, contradictions, and gaps must be "
                "iterable."
            )

        cleaned: list[str] = []
        seen: set[str] = set()

        for item in items:
            normalized = " ".join(str(item).split())

            if not normalized:
                continue

            key = normalized.casefold()

            if key in seen:
                continue

            seen.add(key)
            cleaned.append(normalized)

        return cleaned

    @staticmethod
    def _review_thesis(
        thesis: str,
        action: str,
        risks: list[str],
        questions: list[str],
    ) -> None:
        if not thesis:
            risks.append(
                "No thesis or analytical summary was provided."
            )
            questions.append(
                "What conclusion is being defended or challenged?"
            )
        elif len(thesis) < 50:
            risks.append(
                "The thesis may be too brief to explain the reasoning "
                "behind the recommendation."
            )
            questions.append(
                "What reasoning connects the evidence to the conclusion?"
            )

        if not action:
            risks.append(
                "No explicit recommendation or decision was documented."
            )
            questions.append(
                "What action, decision, or conclusion is being proposed?"
            )

    @staticmethod
    def _review_confidence(
        confidence: int,
        evidence_count: int,
        contradiction_count: int,
        gap_count: int,
        risks: list[str],
        questions: list[str],
        potential_biases: list[str],
    ) -> None:
        if confidence >= 90:
            risks.append(
                "Very high confidence may understate uncertainty."
            )
            questions.append(
                "What evidence would materially reduce confidence or reverse "
                "the recommendation?"
            )
            potential_biases.append(
                "Overconfidence bias may be present."
            )

        if confidence <= 40:
            risks.append(
                "Low confidence suggests the recommendation may not be ready "
                "for action."
            )
            questions.append(
                "What information would be required to reach a more reliable "
                "conclusion?"
            )

        if confidence >= 80 and evidence_count < 3:
            risks.append(
                "Confidence appears high relative to the amount of supporting "
                "evidence."
            )
            potential_biases.append(
                "Confidence may not be calibrated to evidence coverage."
            )

        if confidence >= 75 and contradiction_count > 0:
            risks.append(
                "Confidence remains elevated despite contradictory evidence."
            )

        if confidence >= 75 and gap_count > 0:
            risks.append(
                "Confidence remains elevated despite unresolved information "
                "gaps."
            )

    @staticmethod
    def _review_evidence(
        evidence: list[str],
        contradictions: list[str],
        risks: list[str],
        questions: list[str],
    ) -> None:
        if not evidence:
            risks.append(
                "No supporting evidence was provided."
            )
            questions.append(
                "What evidence supports the recommendation?"
            )
        elif len(evidence) < 3:
            risks.append(
                "The recommendation is supported by limited evidence."
            )
            questions.append(
                "What additional independent evidence should be gathered?"
            )

        if contradictions:
            risks.append(
                f"{len(contradictions)} contradictory evidence item"
                f"{'s were' if len(contradictions) != 1 else ' was'} "
                "identified."
            )

            for contradiction in contradictions:
                questions.append(
                    f"How does the recommendation account for this "
                    f"contradiction: '{contradiction}'?"
                )
        else:
            questions.append(
                "Has evidence that could disconfirm the recommendation been "
                "actively searched for?"
            )

    @staticmethod
    def _review_assumptions(
        assumptions: list[str],
        risks: list[str],
        questions: list[str],
    ) -> None:
        if not assumptions:
            risks.append(
                "No explicit assumptions were documented."
            )
            questions.append(
                "What must be true for this recommendation to remain valid?"
            )
            return

        for assumption in assumptions:
            questions.append(
                f"What happens if this assumption is false: '{assumption}'?"
            )

        if len(assumptions) >= 3:
            risks.append(
                "The recommendation depends on several unverified "
                "assumptions."
            )

    @staticmethod
    def _review_gaps(
        gaps: list[str],
        risks: list[str],
        questions: list[str],
    ) -> None:
        if not gaps:
            questions.append(
                "What important information might still be missing?"
            )
            return

        risks.append(
            f"{len(gaps)} unresolved information gap"
            f"{'s were' if len(gaps) != 1 else ' was'} documented."
        )

        for gap in gaps:
            questions.append(
                f"Could this missing information change the recommendation: "
                f"'{gap}'?"
            )

    @staticmethod
    def _generate_alternative_explanations(
        thesis: str,
        evidence: list[str],
        contradictions: list[str],
        alternatives: list[str],
    ) -> None:
        alternatives.extend(
            [
                (
                    "The observed evidence may be explained by a temporary or "
                    "external factor rather than the proposed thesis."
                ),
                (
                    "The same evidence may support a more cautious or neutral "
                    "conclusion."
                ),
                (
                    "The recommendation may reflect correlation without "
                    "establishing causation."
                ),
                (
                    "Selection effects or incomplete data may be influencing "
                    "the apparent conclusion."
                ),
                (
                    "The opposite recommendation may become reasonable under "
                    "different assumptions or future conditions."
                ),
            ]
        )

        if contradictions:
            alternatives.append(
                "The contradictory evidence may represent a competing "
                "explanation that deserves greater weight."
            )

        if not thesis or not evidence:
            alternatives.append(
                "A reliable alternative explanation cannot be evaluated until "
                "the thesis and supporting evidence are more complete."
            )

    @staticmethod
    def _calculate_challenge_score(
        risks: list[str],
        contradictions: list[str],
        assumptions: list[str],
        gaps: list[str],
        confidence: int,
    ) -> int:
        """
        Calculate the intensity of the challenge.

        A higher score means the recommendation requires more scrutiny.
        This score is a transparent heuristic, not a statistical probability.
        """

        score = 10
        score += min(len(risks) * 8, 48)
        score += min(len(contradictions) * 8, 16)
        score += min(len(assumptions) * 3, 9)
        score += min(len(gaps) * 6, 18)

        if confidence >= 90:
            score += 8

        return max(0, min(100, score))

    @staticmethod
    def _determine_risk_level(challenge_score: int) -> str:
        if challenge_score >= 70:
            return "high"

        if challenge_score >= 40:
            return "moderate"

        return "low"

    @staticmethod
    def _build_verdict(
        risk_level: str,
        risks: list[str],
        contradictions: list[str],
        gaps: list[str],
    ) -> str:
        if risk_level == "high":
            return (
                "Do not proceed without further review. Material weaknesses "
                "or unresolved uncertainties remain."
            )

        if risk_level == "moderate":
            return (
                "Proceed cautiously only after addressing the most important "
                "risks, contradictions, and information gaps."
            )

        if risks or contradictions or gaps:
            return (
                "No critical weakness was identified, but the documented "
                "concerns should be monitored."
            )

        return (
            "No major concerns were identified. The recommendation may "
            "proceed with appropriate monitoring and human judgment."
        )

    @staticmethod
    def _deduplicate(items: list[str]) -> list[str]:
        """Remove duplicate messages while preserving their original order."""

        unique: list[str] = []
        seen: set[str] = set()

        for item in items:
            key = item.casefold()

            if key in seen:
                continue

            seen.add(key)
            unique.append(item)

        return unique
