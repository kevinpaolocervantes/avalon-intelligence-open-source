"""
Avalon Researcher Agent

Collects, validates, and organizes evidence before analysis begins.

The Researcher Agent does not make a final decision. Its role is to establish
what is known, identify conflicting information, document assumptions, surface
gaps, and produce a structured finding for downstream agents or human review.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Iterable, Optional


@dataclass(frozen=True)
class ResearchFinding:
    """Structured output produced by the Researcher Agent."""

    agent: str
    status: str
    topic: str
    summary: str
    supporting_evidence: list[str] = field(default_factory=list)
    contradictions: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    confidence: int = 0

    def __post_init__(self) -> None:
        if not self.topic.strip():
            raise ValueError("Topic cannot be empty.")

        if not 0 <= self.confidence <= 100:
            raise ValueError("Confidence must be between 0 and 100.")

    def as_dict(self) -> dict:
        """Return the finding as a JSON-serializable dictionary."""
        return asdict(self)


class ResearcherAgent:
    """
    Organizes supplied evidence into a transparent research finding.

    The agent is domain-agnostic and can be used for:

    - Business analysis
    - Finance
    - Healthcare
    - Scientific research
    - Product strategy
    - Risk assessment
    - Policy evaluation
    - Engineering decisions
    - Sports analytics
    - General research workflows

    It evaluates the quantity and completeness of evidence, records conflicting
    information, documents assumptions, and identifies unresolved gaps.

    It does not make a final recommendation. That responsibility belongs to
    downstream analytical, adversarial, consensus, or human decision-makers.
    """

    name = "Researcher"
    minimum_reliable_evidence = 3

    def review(
        self,
        topic: str,
        evidence: Iterable[str],
        assumptions: Optional[Iterable[str]] = None,
        contradictions: Optional[Iterable[str]] = None,
        gaps: Optional[Iterable[str]] = None,
    ) -> ResearchFinding:
        """
        Review evidence related to a topic, question, claim, or decision.

        Args:
            topic:
                The subject, claim, question, or decision being researched.

            evidence:
                Facts, observations, source summaries, measurements, or other
                information that supports the finding.

            assumptions:
                Claims currently treated as true but not fully verified.

            contradictions:
                Information that challenges or conflicts with the main evidence.

            gaps:
                Missing information that may materially affect the analysis.

        Returns:
            A structured ResearchFinding.
        """

        clean_topic = topic.strip()

        if not clean_topic:
            raise ValueError("A research topic is required.")

        evidence_items = self._clean_items(evidence)
        assumption_items = self._clean_items(assumptions or [])
        contradiction_items = self._clean_items(contradictions or [])
        gap_items = self._clean_items(gaps or [])

        if not evidence_items:
            return ResearchFinding(
                agent=self.name,
                status="insufficient_evidence",
                topic=clean_topic,
                summary=(
                    "Insufficient evidence to produce a reliable research "
                    "finding."
                ),
                supporting_evidence=[],
                contradictions=contradiction_items,
                assumptions=assumption_items,
                gaps=gap_items or ["No supporting evidence was supplied."],
                confidence=10,
            )

        confidence = self._calculate_confidence(
            evidence_count=len(evidence_items),
            contradiction_count=len(contradiction_items),
            assumption_count=len(assumption_items),
            gap_count=len(gap_items),
        )

        status = self._determine_status(
            evidence_count=len(evidence_items),
            contradiction_count=len(contradiction_items),
            gap_count=len(gap_items),
        )

        summary = self._build_summary(
            topic=clean_topic,
            evidence_count=len(evidence_items),
            contradiction_count=len(contradiction_items),
            assumption_count=len(assumption_items),
            gap_count=len(gap_items),
        )

        return ResearchFinding(
            agent=self.name,
            status=status,
            topic=clean_topic,
            summary=summary,
            supporting_evidence=evidence_items,
            contradictions=contradiction_items,
            assumptions=assumption_items,
            gaps=gap_items,
            confidence=confidence,
        )

    @staticmethod
    def _clean_items(items: Iterable[str]) -> list[str]:
        """
        Normalize whitespace, remove empty values, and eliminate duplicates
        while preserving the original order.
        """

        cleaned: list[str] = []
        seen: set[str] = set()

        for item in items:
            normalized = " ".join(str(item).split())

            if not normalized:
                continue

            comparison_key = normalized.casefold()

            if comparison_key in seen:
                continue

            seen.add(comparison_key)
            cleaned.append(normalized)

        return cleaned

    def _determine_status(
        self,
        evidence_count: int,
        contradiction_count: int,
        gap_count: int,
    ) -> str:
        """Determine the completeness and reliability of the research finding."""

        if evidence_count < self.minimum_reliable_evidence:
            return "limited_evidence"

        if contradiction_count > evidence_count:
            return "conflicting_evidence"

        if gap_count > 0:
            return "research_incomplete"

        return "review_complete"

    @staticmethod
    def _calculate_confidence(
        evidence_count: int,
        contradiction_count: int,
        assumption_count: int,
        gap_count: int,
    ) -> int:
        """
        Calculate a transparent heuristic confidence score.

        The score is not a statistical probability. It is an indicator of
        evidence coverage, consistency, and completeness.
        """

        score = 35

        score += min(evidence_count * 10, 50)
        score -= contradiction_count * 10
        score -= assumption_count * 5
        score -= gap_count * 7

        return max(0, min(95, score))

    @staticmethod
    def _build_summary(
        topic: str,
        evidence_count: int,
        contradiction_count: int,
        assumption_count: int,
        gap_count: int,
    ) -> str:
        """Build a concise, domain-neutral summary of the research review."""

        parts = [
            (
                f"Reviewed {evidence_count} evidence item"
                f"{'s' if evidence_count != 1 else ''} related to "
                f"'{topic}'."
            )
        ]

        if contradiction_count:
            parts.append(
                f"Identified {contradiction_count} contradictory item"
                f"{'s' if contradiction_count != 1 else ''}."
            )
        else:
            parts.append("No direct contradictions were supplied.")

        if assumption_count:
            parts.append(
                f"The finding depends on {assumption_count} unverified "
                f"assumption{'s' if assumption_count != 1 else ''}."
            )

        if gap_count:
            parts.append(
                f"{gap_count} material information gap"
                f"{'s remain' if gap_count != 1 else ' remains'}."
            )

        return " ".join(parts)
