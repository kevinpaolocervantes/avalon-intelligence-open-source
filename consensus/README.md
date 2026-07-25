# Consensus Engine

The Consensus Engine combines recommendations from multiple specialized AI
agents into one transparent, weighted decision.

## Features

- Weighted agent voting
- Confidence-adjusted support
- Transparent agreement scoring
- Configurable tie breaking
- Supporting and dissenting agent lists
- Human-readable explanations
- Input validation
- JSON-serializable output

## Example

```python
from consensus import ConsensusEngine

recommendations = [
    {"agent": "Researcher", "decision": "BUY", "confidence": 82},
    {"agent": "Quant Agent", "decision": "BUY", "confidence": 91},
    {"agent": "Market Observer", "decision": "HOLD", "confidence": 78},
    {"agent": "Challenger", "decision": "SELL", "confidence": 35},
]

result = ConsensusEngine().evaluate(recommendations)

print(result.decision)
print(result.agreement_score)
print(result.explanation)
```

## Recommendation Format

```python
{
    "agent": "Quant Agent",
    "decision": "BUY",
    "confidence": 85,
    "weight": 1.0,
}
```

Supported decisions are `BUY`, `HOLD`, and `SELL`.

The `confidence` field defaults to `100`. The `weight` field defaults to `1.0`.

## Output

The engine returns:

- Final decision
- Agreement score
- Weighted support by decision
- Raw vote counts
- Supporting agents
- Dissenting agents
- Human-readable explanations

Use `result.to_dict()` for a JSON-serializable response.

## Intended Uses

- Investment research
- Risk reviews
- Product decisions
- Forecasting
- Scientific analysis
- Enterprise recommendations
- Multi-agent AI experiments

This is an open-source building block from the Avalon ecosystem.
