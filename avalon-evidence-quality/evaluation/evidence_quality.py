"""Transparent, domain-agnostic evidence-quality scoring (not fact checking)."""

from dataclasses import asdict, dataclass
from math import isfinite
from typing import Dict, Mapping, Optional, Tuple

DIMENSIONS: Tuple[str, ...] = (
    "reliability", "relevance", "recency", "independence", "completeness"
)
DEFAULT_WEIGHTS: Dict[str, float] = {
    "reliability": 0.30,
    "relevance": 0.25,
    "recency": 0.15,
    "independence": 0.15,
    "completeness": 0.15,
}
IMPROVEMENTS = {
    "reliability": "Verify source credibility and provenance.",
    "relevance": "Find evidence more directly related to the claim.",
    "recency": "Look for more recent information or justify using older evidence.",
    "independence": "Seek independent corroboration.",
    "completeness": "Address missing context, methods, and limitations.",
}


def _number(value: object, label: str, *, positive: bool = False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("{} must be a finite number.".format(label))
    result = float(value)
    if not isfinite(result) or (positive and result <= 0):
        raise ValueError("{} must be {}.".format(label, "positive and finite" if positive else "finite"))
    return result


@dataclass(frozen=True)
class EvidenceQualityResult:
    source: str
    evidence_quality_score: float
    rating: str
    weakest_dimension: str
    dimension_scores: Dict[str, float]
    weights: Dict[str, float]
    recommendations: Tuple[str, ...]
    methodology: str = "User-supplied ratings; weighted heuristic, not independent verification or probability."

    def as_dict(self) -> dict:
        result = asdict(self)
        result["recommendations"] = list(self.recommendations)
        return result


class EvidenceQualityEvaluator:
    """Score user-provided dimension ratings from 0 to 100.

    Does not retrieve sources, validate claims, or establish truth. Ratings
    should be justified externally and may be subjective.
    """

    def __init__(self, weights: Optional[Mapping[str, float]] = None) -> None:
        selected = dict(DEFAULT_WEIGHTS if weights is None else weights)
        if set(selected) != set(DIMENSIONS):
            raise ValueError("Weights must specify exactly: {}".format(", ".join(DIMENSIONS)))
        normalized = {key: _number(value, "Weight for " + key) for key, value in selected.items()}
        if any(value < 0 for value in normalized.values()):
            raise ValueError("Weights cannot be negative.")
        total = sum(normalized.values())
        if total <= 0:
            raise ValueError("At least one weight must be positive.")
        self.weights = {key: value / total for key, value in normalized.items()}

    def evaluate(
        self,
        source: str,
        reliability: float,
        relevance: float,
        recency: float,
        independence: float,
        completeness: float,
    ) -> EvidenceQualityResult:
        if not isinstance(source, str) or not source.strip():
            raise ValueError("Source must be a non-empty string.")
        values = dict(reliability=reliability, relevance=relevance, recency=recency,
                      independence=independence, completeness=completeness)
        scores = {}
        for dimension in DIMENSIONS:
            score = _number(values[dimension], dimension)
            if not 0 <= score <= 100:
                raise ValueError("{} must be between 0 and 100.".format(dimension))
            scores[dimension] = score
        weighted = sum(scores[key] * self.weights[key] for key in DIMENSIONS)
        rating = "High" if weighted >= 80 else "Moderate" if weighted >= 60 else "Low"
        weakest = min(DIMENSIONS, key=lambda key: scores[key])
        # Focus on dimensions below 80, lowest first. Never imply evidence was verified.
        recommendations = tuple(
            IMPROVEMENTS[key]
            for key in sorted(DIMENSIONS, key=lambda name: scores[name])
            if scores[key] < 80
        )
        return EvidenceQualityResult(
            source=source.strip(), evidence_quality_score=round(weighted, 2),
            rating=rating, weakest_dimension=weakest, dimension_scores=scores,
            weights=dict(self.weights), recommendations=recommendations,
        )
