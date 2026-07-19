class AdversarialAgent:
    """
    Challenges a recommendation by identifying weaknesses,
    hidden assumptions, and alternative explanations before action.
    """

    def review(self, recommendation: dict) -> dict:
        thesis = recommendation.get("thesis", "")
        confidence = recommendation.get("confidence", 0)
        evidence = recommendation.get("supporting_evidence", [])
        assumptions = recommendation.get("assumptions", [])

        risks = []
        questions = []
        alternative_views = []

        # Confidence Review
        if confidence >= 90:
            risks.append(
                "Very high confidence may indicate overconfidence or untested assumptions."
            )
            questions.append(
                "What evidence would cause us to change our recommendation?"
            )

        elif confidence <= 40:
            risks.append(
                "Low confidence suggests insufficient information for a strong recommendation."
            )

        # Evidence Review
        if len(evidence) < 3:
            risks.append(
                "Recommendation is supported by limited evidence."
            )
            questions.append(
                "What additional evidence should be gathered before acting?"
            )

        # Assumption Review
        if not assumptions:
            risks.append(
                "No explicit assumptions were documented."
            )
        else:
            for assumption in assumptions:
                questions.append(
                    f"What if this assumption is false? → '{assumption}'"
                )

        # Thesis Review
        if len(thesis.strip()) < 50:
            risks.append(
                "Recommendation thesis may be too brief to fully justify the decision."
            )

        # Alternative Explanations
        alternative_views.extend([
            "Could the opposite recommendation also be supported?",
            "Has contradictory evidence been considered?",
            "Could external factors explain the observed outcome?",
            "What important information might still be missing?"
        ])

        # Overall Recommendation
        if risks:
            verdict = "Challenge recommendation before proceeding."
        else:
            verdict = "No major concerns identified. Proceed with appropriate monitoring."

        return {
            "agent": "Adversarial Agent",
            "status": "review_complete",
            "verdict": verdict,
            "risks_identified": risks,
            "critical_questions": questions,
            "alternative_views": alternative_views,
            "challenge": (
                "Stress-test every recommendation against uncertainty, "
                "missing information, opposing evidence, and cognitive bias."
            ),
        }
