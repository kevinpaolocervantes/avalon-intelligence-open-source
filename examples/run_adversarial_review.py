from pprint import pprint

from agents.adversarial_agent import AdversarialAgent


recommendation = {
    "recommendation": "Expand into the Southeast market.",
    "thesis": (
        "The company should expand into the Southeast market because customer "
        "demand is growing, projected operating margins exceed internal "
        "targets, and existing distribution partners can support expansion."
    ),
    "confidence": 82,
    "supporting_evidence": [
        "Customer demand increased 18% year-over-year.",
        "Three enterprise customers requested local support.",
        "Projected operating margins exceed the company's minimum threshold.",
        "Existing distribution partners can support expansion.",
    ],
    "contradictions": [
        "Customer acquisition costs are projected to increase by 12%.",
    ],
    "assumptions": [
        "Regional demand will remain stable over the next twelve months.",
        "Current operating cost projections are accurate.",
    ],
    "gaps": [
        "Regulatory compliance costs have not been finalized.",
        "No sensitivity analysis has been completed for an economic slowdown.",
    ],
}

agent = AdversarialAgent()

review = agent.review(recommendation)

pprint(review.as_dict())
