"""
Avalon Decision Calculator

Aggregates specialist recommendations into a single consensus score.
"""

from typing import Dict, List


class DecisionCalculator:
    """
    Combines multiple specialist reviews into a simple
    consensus confidence score.

    This class is intentionally lightweight and serves as a
    foundational building block for Avalon's future Consensus Engine.
    """

    def calculate(self, reviews: List[Dict]) -> Dict:
        if not reviews:
            return {
                "consensus_confidence": 0,
                "agreement": "No Reviews",
                "specialists": 0,
                "highest_confidence": None,
                "lowest_confidence": None,
            }

        confidences = [review.get("confidence", 0) for review in reviews]

        consensus = round(sum(confidences) / len(confidences), 2)
        spread = max(confidences) - min(confidences)

        if consensus >= 90:
            recommendation = "Strong Consensus"
        elif consensus >= 75:
            recommendation = "Moderate Consensus"
        elif consensus >= 60:
            recommendation = "Weak Consensus"
        else:
            recommendation = "No Consensus"

        return {
            "consensus_confidence": consensus,
            "recommendation": recommendation,
            "specialists": len(reviews),
            "highest_confidence": max(confidences),
            "lowest_confidence": min(confidences),
            "confidence_spread": spread,
            "agreement_score": round(100 - spread, 2),
        }
