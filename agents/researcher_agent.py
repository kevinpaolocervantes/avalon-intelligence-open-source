"""
Avalon Researcher Agent

Collects and organizes evidence before analysis begins.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ResearchFinding:
    topic: str
    summary: str
    sources: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    confidence: int = 0

    def __post_init__(self) -> None:
        if not 0 <= self.confidence <= 100:
            raise ValueError("Confidence must be between 0 and 100.")

    def as_dict(self) -> dict:
        return {
            "agent": "Researcher",
            "topic": self.topic,
            "summary": self.summary,
            "sources": self.sources,
            "assumptions": self.assumptions,
            "confidence": self.confidence,
        }


class ResearcherAgent:
    """Creates a structured research finding from supplied evidence."""

    def review(
        self,
        topic: str,
        evidence: List[str],
        assumptions: Optional[List[str]] = None,
    ) -> ResearchFinding:
        if not evidence:
            return ResearchFinding(
                topic=topic,
                summary="Insufficient evidence to produce a reliable finding.",
                assumptions=assumptions or [],
                confidence=20,
            )

        summary = (
            f"Reviewed {len(evidence)} evidence item"
            f"{'s' if len(evidence) != 1 else ''} related to {topic}."
        )

        confidence = min(60 + (len(evidence) * 8), 95)

        return ResearchFinding(
            topic=topic,
            summary=summary,
            sources=evidence,
            assumptions=assumptions or [],
            confidence=confidence,
        )
