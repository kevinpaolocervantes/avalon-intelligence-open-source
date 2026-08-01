"""Example usage of the Avalon Researcher Agent."""

from pprint import pprint

from agents.researcher_agent import ResearcherAgent


def main() -> None:
    researcher = ResearcherAgent()

    result = researcher.review(
        topic="Should the company expand into the Southeast market?",
        evidence=[
            "Customer demand increased 18% year-over-year.",
            "Three enterprise customers requested local support.",
            "Projected operating margins exceed the company minimum.",
            "Existing distribution partners can support expansion.",
        ],
        contradictions=[
            "Customer acquisition costs are projected to increase by 12%."
        ],
        assumptions=[
            "Regional demand will remain stable over the next twelve months."
        ],
        gaps=[
            "Regulatory compliance costs have not been fully estimated."
        ],
    )

    pprint(result.as_dict())


if __name__ == "__main__":
    main()
