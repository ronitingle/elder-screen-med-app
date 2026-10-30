"""
Unit and smoke tests for LLM & Risk Fusion Service
"""

import unittest
from fastapi.testclient import TestClient
from main import app
from fusion import RiskFusionEngine


class TestLLMService(unittest.TestCase):
    def setUp(self):
        self.engine = RiskFusionEngine()
        self.client = TestClient(app)

    def test_health(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "ok")

    def test_low_risk_fusion(self):
        vision_result = {
            "pallor": {"score": 0.15, "confidence": 0.90},
            "facial_asymmetry": {"score": 0.10, "confidence": 0.92},
            "scleral_yellowing": {"score": 0.12, "confidence": 0.88}
        }
        res = self.engine.calculate_risk(vision_result, "No issues, regular checkup", age=66)
        self.assertEqual(res["risk_level"], "low")
        self.assertIsNone(res["emergency_warning"])

    def test_high_risk_emergency_stroke_signs(self):
        vision_result = {
            "pallor": {"score": 0.20, "confidence": 0.80},
            "facial_asymmetry": {"score": 0.72, "confidence": 0.95},
            "scleral_yellowing": {"score": 0.10, "confidence": 0.85}
        }
        res = self.engine.generate_summary(vision_result, "Sudden speech slurring and face droop", age=72, lang="en")
        self.assertEqual(res["risk_level"], "high")
        self.assertEqual(res["urgency"], "immediate_emergency")
        self.assertIsNotNone(res["emergency_warning"])
        self.assertIn("EMERGENCY", res["patient_summary"].upper())
        self.assertIn("108", res["patient_summary"])

    def test_hindi_language_generation(self):
        vision_result = {
            "pallor": {"score": 0.60, "confidence": 0.85},
            "facial_asymmetry": {"score": 0.10, "confidence": 0.90},
            "scleral_yellowing": {"score": 0.65, "confidence": 0.88}
        }
        res = self.engine.generate_summary(vision_result, "पीला पेशाब और बहुत कमजोरी", age=68, lang="hi")
        self.assertEqual(res["risk_level"], "medium")
        self.assertIn("जांच", res["patient_summary"])
        self.assertTrue(len(res["next_steps"]) >= 2)

    def test_api_endpoint_contract(self):
        payload = {
            "vision_result": {
                "pallor": {"score": 0.35, "confidence": 0.88},
                "facial_asymmetry": {"score": 0.12, "confidence": 0.91},
                "scleral_yellowing": {"score": 0.68, "confidence": 0.85},
                "quality_flags": ["adequate_lighting"]
            },
            "symptoms_text": "Feeling very weak for 3 days and dark urine.",
            "age": 68,
            "lang": "en"
        }
        res = self.client.post("/summarize", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("risk_level", data)
        self.assertIn("patient_summary", data)
        self.assertIn("clinical_summary", data)
        self.assertIn("next_steps", data)
        self.assertIn("reasons", data)


if __name__ == "__main__":
    unittest.main()
