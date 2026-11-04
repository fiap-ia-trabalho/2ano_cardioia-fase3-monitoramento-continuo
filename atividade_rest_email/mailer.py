import smtplib
from email.mime.text import MIMEText

from config import settings


def build_alert_email(alert_data):
    """Cria o corpo do e-mail para alerta crítico."""
    patient = alert_data.get("patient", "Paciente")
    temperature = alert_data.get("temperature_c")
    bpm = alert_data.get("bpm")
    idle_ms = alert_data.get("idle_ms", 0)
    reasons = alert_data.get("reasons", [])

    if not reasons:
        reasons = []
        if temperature is not None and temperature > 38.0:
            reasons.append("febre")
        if bpm is not None and bpm > 120:
            reasons.append("taquicardia")
        if idle_ms is not None and idle_ms >= 60000:
            reasons.append("inatividade")
        if not reasons:
            reasons = ["alerta geral"]

    reasons_text = ", ".join(reasons)
    body = (
        f"Paciente: {patient}\n"
        f"Temperatura: {temperature} °C\n"
        f"BPM: {bpm}\n"
        f"Inatividade: {idle_ms} ms\n"
        f"Motivos: {reasons_text}\n\n"
        "Este alerta foi gerado automaticamente pelo sistema de monitoramento."
    )

    subject = f"[ALERTA] {patient} - monitoramento de sinais vitais"
    return {"subject": subject, "body": body}


def send_email(subject, body, to_email=None):
    """Envia e-mail por SMTP, ou apenas simula o envio quando configurado."""
    if settings.simulate_email:
        print("[SIMULAÇÃO DE E-MAIL]")
        print(f"Assunto: {subject}")
        print(body)
        return {"status": "simulated", "to": to_email or settings.to_email}

    if not settings.smtp_username or not settings.smtp_password:
        raise ValueError("Credenciais SMTP ausentes. Ajuste SMTP_USERNAME e SMTP_PASSWORD.")

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.from_email
    msg["To"] = to_email or settings.to_email

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(msg)

    return {"status": "sent", "to": to_email or settings.to_email}
