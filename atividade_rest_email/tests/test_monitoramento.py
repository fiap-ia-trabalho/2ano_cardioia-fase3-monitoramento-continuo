import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from risk_engine import evaluate_risk
from mailer import build_alert_email


class RiskEngineTests(unittest.TestCase):
    def test_alerta_febre_e_taquicardia(self):
        result = evaluate_risk({
            "temperature_c": 39.2,
            "bpm": 128,
            "idle_ms": 2000,
            "sensor_ok": True,
        })
        self.assertEqual(result["status"], "alert")
        self.assertIn("febre", result["reasons"][0].lower())

    def test_alerta_inatividade(self):
        result = evaluate_risk({
            "temperature_c": 36.5,
            "bpm": 72,
            "idle_ms": 65000,
            "sensor_ok": True,
        })
        self.assertEqual(result["status"], "alert")
        self.assertTrue(any("inatividade" in reason.lower() for reason in result["reasons"]))

    def test_status_normal(self):
        result = evaluate_risk({
            "temperature_c": 36.8,
            "bpm": 76,
            "idle_ms": 5000,
            "sensor_ok": True,
        })
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["reasons"], [])

    def test_email_alerta_gerado(self):
        email = build_alert_email({
            "patient": "Maria",
            "temperature_c": 39.5,
            "bpm": 130,
            "idle_ms": 90_000,
        })
        self.assertIn("Maria", email["subject"])
        self.assertIn("febre", email["body"].lower())
        self.assertIn("taquicardia", email["body"].lower())


if __name__ == "__main__":
    unittest.main()
