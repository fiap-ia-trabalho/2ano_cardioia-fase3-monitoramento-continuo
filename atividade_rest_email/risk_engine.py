def evaluate_risk(sample):
    """Analisa um payload de sinais vitais e retorna status e motivos de risco."""
    temperature = sample.get("temperature_c")
    bpm = sample.get("bpm")
    idle_ms = sample.get("idle_ms", 0)
    sensor_ok = sample.get("sensor_ok", True)

    reasons = []

    if not sensor_ok:
        reasons.append("falha de sensor")

    if temperature is not None and temperature > 38.0:
        reasons.append("febre")

    if bpm is not None and bpm > 120:
        reasons.append("taquicardia")

    if idle_ms is not None and idle_ms >= 60000:
        reasons.append("inatividade")

    if reasons:
        return {"status": "alert", "reasons": reasons}

    return {"status": "ok", "reasons": []}
