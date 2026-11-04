import argparse
import json

from config import settings
from risk_engine import evaluate_risk
from rest_client import RestClient
from mailer import build_alert_email, send_email


def build_sample(patient="Maria", temperature=36.8, bpm=76, idle_ms=5000, sensor_ok=True):
    return {
        "patient": patient,
        "temperature_c": temperature,
        "bpm": bpm,
        "idle_ms": idle_ms,
        "sensor_ok": sensor_ok,
        "timestamp": "2026-11-04T12:00:00Z",
    }


def process_monitoring_sample(sample):
    client = RestClient(settings.api_url, timeout=settings.api_timeout)
    payload = client.post_sample(sample)
    result = evaluate_risk(sample)

    print(f"Resposta da API: {json.dumps(payload, indent=2)}")
    print(f"Status de risco: {result['status']}")
    if result["reasons"]:
        print(f"Motivos: {result['reasons']}")

    if result["status"] == "alert":
        email = build_alert_email({**sample, "reasons": result["reasons"]})
        send_email(email["subject"], email["body"], settings.to_email)
        return {"api": payload, "risk": result, "email": email}

    return {"api": payload, "risk": result}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cliente REST para monitoramento de sinais vitais")
    parser.add_argument("--patient", default="Maria")
    parser.add_argument("--temperature", type=float, default=36.8)
    parser.add_argument("--bpm", type=int, default=76)
    parser.add_argument("--idle-ms", type=int, default=5000)
    parser.add_argument("--sensor-ok", action="store_true", default=True)
    parser.add_argument("--api-url", default=settings.api_url)
    args = parser.parse_args()

    settings.api_url = args.api_url
    sample = build_sample(
        patient=args.patient,
        temperature=args.temperature,
        bpm=args.bpm,
        idle_ms=args.idle_ms,
        sensor_ok=args.sensor_ok,
    )

    process_monitoring_sample(sample)
