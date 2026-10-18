"""Run from the repository root: python -m examples.run_evidence_evaluation"""
from pprint import pprint
from evaluation.evidence_quality import EvidenceQualityEvaluator


def main() -> None:
    evaluator = EvidenceQualityEvaluator()
    result = evaluator.evaluate(
        source="Annual financial report",
        reliability=95,
        relevance=90,
        recency=85,
        independence=75,
        completeness=90,
    )
    pprint(result.as_dict())


if __name__ == "__main__":
    main()
