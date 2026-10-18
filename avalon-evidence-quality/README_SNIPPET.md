## Evidence Quality Evaluator

`evaluation/evidence_quality.py` provides a dependency-free, domain-agnostic utility that summarizes **user-supplied** evidence-quality ratings across reliability, relevance, recency, independence, and completeness. It returns a weighted heuristic score, a rating, the weakest dimension, and improvement prompts. **It does not verify sources or estimate the probability a claim is true.**

```bash
python -m examples.run_evidence_evaluation
python -m unittest discover -s tests -p 'test_evidence_quality.py'
```

See [evaluation/README.md](evaluation/README.md) for API usage, scoring methodology, and limitations.
