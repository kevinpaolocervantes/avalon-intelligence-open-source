"""Example usage of the Avalon Quantitative Agent."""

from agents.quantitative_agent import QuantitativeAgent


def main() -> None:
    recommendation = {
        "thesis": (
            "The opportunity appears attractive because the modeled probability "
            "exceeds the market-implied probability."
        ),
        "confidence": 78,
        "estimated_probability": 0.62,
        "market_probability": 0.54,
        "potential_gain": 1.0,
        "potential_loss": 1.0,
        "sample_size": 240,
        "historical_results": [
            0.12,
            -0.04,
            0.09,
            0.15,
            -0.02,
        ],
        "assumptions": [
            "Historical relationships remain relevant.",
            "Transaction costs are negligible.",
            "The underlying data is complete and accurate.",
        ],
    }

    quant = QuantitativeAgent()
    result = quant.review(recommendation)

    print(result)


if __name__ == "__main__":
    main()
