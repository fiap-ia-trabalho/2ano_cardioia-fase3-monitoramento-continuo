import os
from dataclasses import dataclass


@dataclass
class Settings:
    api_url: str = os.getenv("API_URL", "http://127.0.0.1:5000")
    api_timeout: int = int(os.getenv("API_TIMEOUT", "10"))
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    from_email: str = os.getenv("FROM_EMAIL", "alertas@demo.local")
    to_email: str = os.getenv("TO_EMAIL", "destinatario@demo.local")
    simulate_email: bool = os.getenv("SIMULATE_EMAIL", "true").lower() == "true"


settings = Settings()
