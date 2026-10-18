"""Run from repository root: python -m unittest discover -s tests -p 'test_evidence_quality.py'"""
import math
import unittest
from evaluation.evidence_quality import EvidenceQualityEvaluator


class EvidenceQualityTests(unittest.TestCase):
    def setUp(self):
        self.evaluator = EvidenceQualityEvaluator()
        self.sample = dict(source="Report", reliability=95, relevance=90,
                           recency=85, independence=75, completeness=90)

    def test_example_score(self):
        result = self.evaluator.evaluate(**self.sample)
        self.assertEqual(result.evidence_quality_score, 88.5)
        self.assertEqual(result.rating, "High")
        self.assertEqual(result.weakest_dimension, "independence")
        self.assertEqual(result.recommendations, ("Seek independent corroboration.",))

    def test_boundaries(self):
        for value, expected in [(0, "Low"), (60, "Moderate"), (80, "High"), (100, "High")]:
            args = {key: value for key in ("reliability", "relevance", "recency", "independence", "completeness")}
            result = self.evaluator.evaluate(source="X", **args)
            self.assertEqual(result.rating, expected)
            self.assertEqual(result.evidence_quality_score, value)

    def test_rejects_invalid_values(self):
        for value in (-1, 101, float("nan"), float("inf"), True, "90"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.evaluator.evaluate(**dict(self.sample, reliability=value))

    def test_custom_weights_normalized(self):
        evaluator = EvidenceQualityEvaluator(dict(reliability=2, relevance=0,
                                                  recency=0, independence=0, completeness=0))
        self.assertEqual(evaluator.evaluate(**self.sample).evidence_quality_score, 95)

    def test_invalid_weights(self):
        for weights in ({}, {"reliability": 1}, dict.fromkeys(self.evaluator.weights, 0),
                        dict(self.evaluator.weights, reliability=-1),
                        dict(self.evaluator.weights, reliability=float("nan"))):
            with self.subTest(weights=weights), self.assertRaises(ValueError):
                EvidenceQualityEvaluator(weights)

    def test_empty_source(self):
        with self.assertRaises(ValueError):
            self.evaluator.evaluate(**dict(self.sample, source=" "))

    def test_as_dict_is_serializable(self):
        import json
        result = self.evaluator.evaluate(**self.sample).as_dict()
        self.assertIsInstance(json.dumps(result), str)
        self.assertIsInstance(result["recommendations"], list)


if __name__ == "__main__":
    unittest.main()
