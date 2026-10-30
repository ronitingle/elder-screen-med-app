"""
ElderScreen Comprehensive End-to-End Test Suite & Edge Case Audit
Tests:
1. Normal healthy senior screening
2. Acute stroke emergency escalation (FAST protocol)
3. Scleral icterus (jaundice) + mucosal pallor (anemia)
4. Edge Case: Empty symptoms string
5. Edge Case: Blurry / low light / invalid photos (Quality Flags)
6. Bilingual output verification (Hindi & English)
7. End-to-end latency benchmark (< 15 seconds requirement)
"""

import os
import sys
import time
import json
import unittest
from pathlib import Path
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "vision"))
sys.path.insert(0, str(REPO_ROOT / "llm"))
sys.path.insert(0, str(REPO_ROOT / "supabase"))

from analyzer import VisionAnalyzer
from fusion import RiskFusionEngine
from orchestrator import app as orchestrator_app

SAMPLE_DIR = REPO_ROOT / "vision" / "samples"


class TestElderScreenE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(orchestrator_app)
        cls.analyzer = VisionAnalyzer()
        cls.fusion = RiskFusionEngine()

    def test_e2e_normal_screening_latency(self):
        """Verifies full screening completes well under 15 seconds."""
        face_path = SAMPLE_DIR / "face_normal.jpg"
        eye_path = SAMPLE_DIR / "eye_normal.jpg"

        start_time = time.time()
        with open(face_path, "rb") as f_face, open(eye_path, "rb") as f_eye:
            files = {
                "face_image": ("face_normal.jpg", f_face, "image/jpeg"),
                "eye_image": ("eye_normal.jpg", f_eye, "image/jpeg")
            }
            data = {
                "symptoms": "No issues, regular monthly checkup",
                "age": 68,
                "lang": "en",
                "patient_name": "Ramesh Kumar"
            }
            res = self.client.post("/api/screenings", files=files, data=data)

        elapsed = time.time() - start_time
        print(f"\n[Benchmark] Full E2E screening elapsed time: {elapsed:.3f} seconds (Target: < 15.0s)")

        self.assertEqual(res.status_code, 200)
        self.assertLess(elapsed, 15.0, "Screening took longer than 15-second constraint!")

        body = res.json()
        self.assertEqual(body["summary_result"]["risk_level"], "low")
        self.assertIn("patient_summary", body["summary_result"])
        self.assertIn("clinical_summary", body["summary_result"])

    def test_stroke_red_flag_emergency_escalation(self):
        """Verifies acute facial asymmetry triggers emergency warning and 108/112 advice."""
        face_path = SAMPLE_DIR / "face_stroke.jpg"
        eye_path = SAMPLE_DIR / "eye_stroke.jpg"

        with open(face_path, "rb") as f_face, open(eye_path, "rb") as f_eye:
            files = {
                "face_image": ("face_stroke.jpg", f_face, "image/jpeg"),
                "eye_image": ("eye_stroke.jpg", f_eye, "image/jpeg")
            }
            data = {
                "symptoms": "Sudden facial drooping and difficulty speaking clearly",
                "age": 75,
                "lang": "en",
                "patient_name": "Senior Patient"
            }
            res = self.client.post("/api/screenings", files=files, data=data)

        self.assertEqual(res.status_code, 200)
        body = res.json()
        summary = body["summary_result"]
        self.assertEqual(summary["risk_level"], "high")
        self.assertEqual(summary["urgency"], "immediate_emergency")
        self.assertIsNotNone(summary["emergency_warning"])
        self.assertIn("108", summary["patient_summary"])

    def test_jaundice_and_pallor_detection(self):
        """Verifies yellow sclera and pale mucosa trigger medium risk clinic consult."""
        face_path = SAMPLE_DIR / "face_jaundice.jpg"
        eye_path = SAMPLE_DIR / "eye_jaundice.jpg"

        with open(face_path, "rb") as f_face, open(eye_path, "rb") as f_eye:
            files = {
                "face_image": ("face_jaundice.jpg", f_face, "image/jpeg"),
                "eye_image": ("eye_jaundice.jpg", f_eye, "image/jpeg")
            }
            data = {
                "symptoms": "Dark yellow urine and feeling exhausted for 4 days",
                "age": 70,
                "lang": "en",
                "patient_name": "Senior Patient"
            }
            res = self.client.post("/api/screenings", files=files, data=data)

        self.assertEqual(res.status_code, 200)
        body = res.json()
        summary = body["summary_result"]
        self.assertEqual(summary["risk_level"], "medium")
        self.assertEqual(summary["urgency"], "scheduled_clinic_visit")

    def test_edge_case_empty_symptoms(self):
        """Verifies app functions gracefully with empty or whitespace symptoms."""
        face_path = SAMPLE_DIR / "face_normal.jpg"
        eye_path = SAMPLE_DIR / "eye_normal.jpg"

        with open(face_path, "rb") as f_face, open(eye_path, "rb") as f_eye:
            files = {
                "face_image": ("face_normal.jpg", f_face, "image/jpeg"),
                "eye_image": ("eye_normal.jpg", f_eye, "image/jpeg")
            }
            data = {"symptoms": "   ", "age": 65, "lang": "en"}
            res = self.client.post("/api/screenings", files=files, data=data)

        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertIsNotNone(body["summary_result"]["patient_summary"])

    def test_edge_case_corrupt_or_blurred_photo(self):
        """Verifies analyzer flags blur without crashing."""
        import numpy as np
        import cv2

        # Create artificially blurred image
        blank = np.ones((200, 200, 3), dtype=np.uint8) * 128
        blurred = cv2.GaussianBlur(blank, (25, 25), 0)
        flags = self.analyzer.check_image_quality(blurred)
        self.assertIn("blur_detected", flags)

    def test_hindi_language_localization(self):
        """Verifies complete Hindi response for patient summary."""
        face_path = SAMPLE_DIR / "face_normal.jpg"
        eye_path = SAMPLE_DIR / "eye_normal.jpg"

        with open(face_path, "rb") as f_face, open(eye_path, "rb") as f_eye:
            files = {
                "face_image": ("face_normal.jpg", f_face, "image/jpeg"),
                "eye_image": ("eye_normal.jpg", f_eye, "image/jpeg")
            }
            data = {
                "symptoms": "हल्की कमजोरी है",
                "age": 69,
                "lang": "hi",
                "patient_name": "रामलाल"
            }
            res = self.client.post("/api/screenings", files=files, data=data)

        self.assertEqual(res.status_code, 200)
        body = res.json()
        self.assertIn("जांच", body["summary_result"]["patient_summary"])


if __name__ == "__main__":
    unittest.main()
