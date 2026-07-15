"""Example usage of the Avalon Researcher Agent."""

from agents.researcher_agent import ResearcherAgent


def main() -> None:
    researcher = ResearcherAgent()

    result = researcher.review(
        topic="Quarterly revenue growth",
        evidence=[
            "Q1 earnings report",
            "Q2 earnings report",
            "Q3 earnings report",
        ],
        assumptions=[
            "Published financial statements are accurate.",
        ],
    )

    print(result.as_dict())


if __name__ == "__main__":
    main()
