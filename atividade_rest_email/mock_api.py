from flask import Flask, jsonify, request

app = Flask(__name__)

latest_sample = {
    "patient": "Maria",
    "temperature_c": 36.8,
    "bpm": 72,
    "idle_ms": 5000,
    "sensor_ok": True,
    "timestamp": "2026-11-04T12:00:00Z",
}


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "mock-monitoramento"})


@app.post("/samples")
def receive_sample():
    global latest_sample
    payload = request.get_json(force=True, silent=True) or {}
    if not payload:
        return jsonify({"error": "payload vazio"}), 400
    latest_sample = payload
    return jsonify({"status": "received", "sample": latest_sample})


@app.get("/samples/latest")
def get_latest():
    return jsonify(latest_sample)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
