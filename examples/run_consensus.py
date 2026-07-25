from pprint import pprint

from consensus import ConsensusEngine


recommendations = [
    {"agent": "Researcher", "decision": "BUY", "confidence": 82},
    {"agent": "Quant Agent", "decision": "BUY", "confidence": 91},
    {"agent": "Market Observer", "decision": "HOLD", "confidence": 78},
    {"agent": "Challenger", "decision": "SELL", "confidence": 35},
]

result = ConsensusEngine().evaluate(recommendations)

pprint(result.to_dict())
