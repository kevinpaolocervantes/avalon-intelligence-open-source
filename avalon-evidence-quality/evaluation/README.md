# Evidence Quality Evaluator

A small, dependency-free, domain-agnostic utility for **organizing subjective evidence-quality assessments** in multi-agent or human decision workflows.

## What it does

Takes five **user-provided** scores (0–100) and produces a weighted score, a rating, the lowest-scoring dimension, and targeted improvement prompts.

| Dimension | Default weight | Meaning |
|---|---:|---|
| Reliability | 30% | Credibility and provenance of the source |
| Relevance | 25% | Connection to the claim being evaluated |
| Recency | 15% | Timeliness for the question |
| Independence | 15% | Independence from other evidence and sources |
| Completeness | 15% | Coverage of important details and limitations |

**Formula:** `score = sum(dimension_score * normalized_weight)`.

Ratings: **High** >= 80, **Moderate** >= 60, **Low** < 60. These are configurable *interpretive thresholds in code*, not validated statistical categories. Recommendations are generated for any dimension below 80, ordered from lowest score.

## Quick start

From the repository root (Python 3.9+):

```bash
python -m examples.run_evidence_evaluation
python -m unittest discover -s tests -p 'test_evidence_quality.py'
```

```python
from evaluation.evidence_quality import EvidenceQualityEvaluator

result = EvidenceQualityEvaluator().evaluate(
    source="Annual financial report",
    reliability=95,
    relevance=90,
    recency=85,
    independence=75,
    completeness=90,
)
print(result.as_dict())
```

The example yields **88.5**, **High**, with **independence** as the weakest dimension and a recommendation to seek independent corroboration.

### Custom weights

```python
weights = dict(reliability=4, relevance=3, recency=1, independence=1, completeness=1)
evaluator = EvidenceQualityEvaluator(weights=weights)  # normalized automatically
```

## Important limitations

- **Does not** browse, verify sources, detect fabricated claims, or independently measure credibility.
- The score is a **weighted heuristic**, **not a probability**, calibrated confidence, or evidence that a claim is true.
- Higher scores can be assigned to inaccurate information; quality depends on how humans or upstream systems justify the five inputs.
- Recency is context-dependent: older evidence can remain the most relevant.
- Multiple sources repeating one claim do not necessarily count as independent corroboration.
- Not intended as a standalone basis for medical, financial, or other high-stakes decisions.

MIT-compatible utility; see repository-level license.
