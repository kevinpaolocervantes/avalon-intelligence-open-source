from statistics import mean, pstdev
from typing import Any


class QuantitativeAgent:
    """
    Evaluates a recommendation using numerical evidence, probability,
    expected value, uncertainty, and sensitivity analysis.
    """

    def review(self, recommendation: dict[str, Any]) -> dict[str, Any]:
        thesis = recommendation.get("thesis", "")
        confidence = self._normalize_percentage(
            recommendation.get("confidence", 0)
        )
        estimated_probability = self._normalize_probability(
            recommendation.get("estimated_probability")
        )
        market_probability = self._normalize_probability(
            recommendation.get("market_probability")
        )
        potential_gain = recommendation.get("potential_gain")
        potential_loss = recommendation.get("potential_loss")
        sample_size = recommendation.get("sample_size", 0)
        historical_results = recommendation.get("historical_results", [])
        assumptions = recommendation.get("assumptions", [])

        risks: list[str] = []
        observations: list[str] = []
        questions: list[str] = []
        metrics: dict[str, Any] = {
            "confidence": round(confidence, 2),
            "estimated_probability": estimated_probability,
            "market_probability": market_probability,
            "sample_size": sample_size,
        }

        if not thesis.strip():
            risks.append("No quantitative thesis was provided.")

        if estimated_probability is None:
            risks.append(
                "No estimated probability was supplied, so the recommendation "
                "cannot be evaluated probabilistically."
            )

        if market_probability is not None and estimated_probability is not None:
            edge = estimated_probability - market_probability
            metrics["estimated_edge"] = round(edge, 4)

            if edge <= 0:
                risks.append(
                    "The estimated probability does not exceed the market or "
                    "baseline probability."
                )
            elif edge < 0.03:
                risks.append(
                    "The estimated edge is small and may disappear after model "
                    "error, fees, slippage, or changing conditions."
                )
            else:
                observations.append(
                    f"The model estimates an edge of {edge:.1%} over the baseline."
                )

        expected_value = self._calculate_expected_value(
            estimated_probability=estimated_probability,
            potential_gain=potential_gain,
            potential_loss=potential_loss,
        )

        if expected_value is not None:
            metrics["expected_value"] = round(expected_value, 4)

            if expected_value <= 0:
                risks.append(
                    "The recommendation has non-positive expected value under "
                    "the supplied assumptions."
                )
            else:
                observations.append(
                    f"Expected value is positive at {expected_value:.4f} per unit."
                )
        elif potential_gain is not None or potential_loss is not None:
            risks.append(
                "Expected value could not be calculated because probability, "
                "gain, or loss inputs are incomplete or invalid."
            )

        if sample_size < 30:
            risks.append(
                "The sample size is small and may not support a stable conclusion."
            )
        elif sample_size < 100:
            observations.append(
                "The sample size is usable but still vulnerable to variance."
            )

        if confidence >= 90:
            risks.append(
                "Model confidence may be too high relative to real-world uncertainty."
            )
            questions.append(
                "How well calibrated has this confidence level been historically?"
            )

        if estimated_probability is not None:
            confidence_probability = confidence / 100

            if abs(confidence_probability - estimated_probability) > 0.20:
                risks.append(
                    "The stated confidence differs materially from the estimated "
                    "probability. These measures may be conflated or inconsistently defined."
                )

        if historical_results:
            clean_results = [
                float(result)
                for result in historical_results
                if isinstance(result, (int, float))
            ]

            if clean_results:
                historical_mean = mean(clean_results)
                historical_volatility = (
                    pstdev(clean_results) if len(clean_results) > 1 else 0.0
                )

                metrics["historical_mean"] = round(historical_mean, 4)
                metrics["historical_volatility"] = round(
                    historical_volatility, 4
                )

                if historical_volatility > abs(historical_mean):
                    risks.append(
                        "Historical volatility is larger than the average result, "
                        "which suggests unstable performance."
                    )

                if len(clean_results) < len(historical_results):
                    risks.append(
                        "Some historical results were ignored because they were "
                        "not numeric."
                    )
            else:
                risks.append(
                    "Historical results were provided but contained no usable "
                    "numeric observations."
                )

        if not assumptions:
            risks.append(
                "No model assumptions were documented."
            )
        else:
            questions.extend(
                f"How sensitive is the result if this assumption changes: {assumption}"
                for assumption in assumptions
            )

        if estimated_probability is not None:
            sensitivity = self._probability_sensitivity(
                estimated_probability=estimated_probability,
                potential_gain=potential_gain,
                potential_loss=potential_loss,
            )
            if sensitivity:
                metrics["probability_sensitivity"] = sensitivity

                if sensitivity["downside_ev"] is not None:
                    if sensitivity["downside_ev"] <= 0:
                        risks.append(
                            "A modest reduction in the estimated probability "
                            "eliminates the expected-value advantage."
                        )

        if expected_value is not None and expected_value > 0 and not risks:
            verdict = "Quantitative evidence supports proceeding."
        elif expected_value is not None and expected_value > 0:
            verdict = (
                "Positive expected value identified, but the recommendation "
                "requires additional validation."
            )
        else:
            verdict = (
                "Quantitative support is insufficient to recommend action."
            )

        return {
            "agent": "Quantitative Agent",
            "status": "review_complete",
            "verdict": verdict,
            "metrics": metrics,
            "observations": observations,
            "risks_identified": risks,
            "critical_questions": questions,
            "challenge": (
                "Proceed only when the estimated edge remains positive after "
                "accounting for uncertainty, model error, volatility, and "
                "reasonable changes to the underlying assumptions."
            ),
        }

    @staticmethod
    def _normalize_percentage(value: Any) -> float:
        try:
            percentage = float(value)
        except (TypeError, ValueError):
            return 0.0

        return max(0.0, min(percentage, 100.0))

    @staticmethod
    def _normalize_probability(value: Any) -> float | None:
        if value is None:
            return None

        try:
            probability = float(value)
        except (TypeError, ValueError):
            return None

        if 1 < probability <= 100:
            probability /= 100

        if not 0 <= probability <= 1:
            return None

        return probability

    @staticmethod
    def _calculate_expected_value(
        estimated_probability: float | None,
        potential_gain: Any,
        potential_loss: Any,
    ) -> float | None:
        if estimated_probability is None:
            return None

        try:
            gain = float(potential_gain)
            loss = abs(float(potential_loss))
        except (TypeError, ValueError):
            return None

        return (
            estimated_probability * gain
            - (1 - estimated_probability) * loss
        )

    def _probability_sensitivity(
        self,
        estimated_probability: float,
        potential_gain: Any,
        potential_loss: Any,
        adjustment: float = 0.05,
    ) -> dict[str, float | None]:
        downside_probability = max(0.0, estimated_probability - adjustment)
        upside_probability = min(1.0, estimated_probability + adjustment)

        return {
            "downside_probability": round(downside_probability, 4),
            "base_probability": round(estimated_probability, 4),
            "upside_probability": round(upside_probability, 4),
            "downside_ev": self._calculate_expected_value(
                downside_probability,
                potential_gain,
                potential_loss,
            ),
            "base_ev": self._calculate_expected_value(
                estimated_probability,
                potential_gain,
                potential_loss,
            ),
            "upside_ev": self._calculate_expected_value(
                upside_probability,
                potential_gain,
                potential_loss,
            ),
        }
