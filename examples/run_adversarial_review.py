from agents.adversarial_agent import AdversarialAgent

recommendation = {
    "thesis": "Team A has a favorable setup based on recent performance.",
    "confidence": 87,
    "supporting_evidence": [
        "Team A has won 4 of its last 5 games.",
        "Team B has two key injuries."
    ]
}

agent = AdversarialAgent()
review = agent.review(recommendation)

print(review)
