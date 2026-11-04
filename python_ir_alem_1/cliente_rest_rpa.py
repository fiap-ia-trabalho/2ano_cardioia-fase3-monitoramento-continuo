# python/cliente_rest_rpa.py

import requests
import smtplib
import json
import time
from datetime import datetime
from email.message import EmailMessage

# ==============================================================================
# CONFIGURAÇÕES DO SISTEMA E CREDENCIAIS
# ==============================================================================

# Para testes, utilizamos endpoints públicos de simulação REST (JSONPlaceholder)
API_URL_GET = "https://jsonplaceholder.typicode.com/posts/1"
API_URL_POST = "https://jsonplaceholder.typicode.com/posts"

# Credenciais de e-mail 
EMAIL_REMETENTE = "seu_email_rpa@gmail.com"
EMAIL_SENHA = "sua_senha_de_aplicativo"
EMAIL_DESTINO = "equipe_medica@hospital.com"

# Limites Clínicos (Regras de Negócio)
LIMITE_BPM = 120
LIMITE_TEMP = 38.0
STATUS_INATIVIDADE = 0

# ==============================================================================
# FUNÇÕES DO CLIENTE REST E AUTOMAÇÃO
# ==============================================================================

def consumir_sinais_vitais() -> dict:
    """
    Consome a API REST via GET para obter os dados vitais atuais.
    Como a API real do ESP32/Node-RED não está exposta para a internet neste 
    simulador, injetamos um payload mockado validando a estrutura.
    """
    try:
        resposta = requests.get(API_URL_GET, timeout=5)
        resposta.raise_for_status()
        
        # Payload simulado representando a leitura recebida do IoT
        payload = {
            "paciente_id": "PT-9942",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "temperatura": 38.6,  # Gatilho de febre ativado
            "bpm": 135,           # Gatilho de taquicardia ativado
            "movimento": 0        # Gatilho de inatividade ativado
        }
        return payload
    except requests.RequestException as e:
        print(f"[ERRO] Falha ao consumir API REST: {e}")
        return {}

def registrar_historico_nuvem(dados: dict):
    """
    Envia um POST para a API REST para registrar que a leitura foi processada.
    """
    try:
        resposta = requests.post(API_URL_POST, json=dados, timeout=5)
        resposta.raise_for_status()
        print(f"[INFO] Dados do paciente {dados.get('paciente_id')} registrados via POST com status {resposta.status_code}.")
    except requests.RequestException as e:
        print(f"[ERRO] Falha ao enviar dados (POST): {e}")

def avaliar_riscos_clinicos(dados: dict) -> list:
    """
    Avalia os dados vitais contra os limiares pré-estabelecidos.
    Retorna uma lista contendo os alertas detectados.
    """
    alertas = []
    if dados.get("bpm", 0) > LIMITE_BPM:
        alertas.append(f"Taquicardia: {dados['bpm']} BPM")
    
    if dados.get("temperatura", 0) > LIMITE_TEMP:
        alertas.append(f"Febre: {dados['temperatura']} °C")
    
    if dados.get("movimento") == STATUS_INATIVIDADE:
        alertas.append("Ausência de movimento contínua")
        
    return alertas

def enviar_alerta_email(dados: dict, alertas: list):
    """
    Automação (RPA): Constrói e dispara o e-mail de emergência via SMTP.
    """
    motivos = "\n- ".join(alertas)
    corpo = (
        f"ALERTA CRÍTICO DE SAÚDE - SISTEMA CARDIOIA\n"
        f"=========================================\n\n"
        f"Paciente ID: {dados.get('paciente_id')}\n"
        f"Horário da Ocorrência: {dados.get('timestamp')}\n\n"
        f"RISCOS DETECTADOS:\n- {motivos}\n\n"
        f"MÉTRICAS ATUAIS:\n"
        f"Temperatura: {dados.get('temperatura')} °C\n"
        f"Batimentos: {dados.get('bpm')} BPM\n"
        f"Aceleração/Movimento: {dados.get('movimento')}\n\n"
        f"Por favor, verifique o paciente imediatamente."
    )

    msg = EmailMessage()
    msg.set_content(corpo)
    msg['Subject'] = f"URGENTE: Alerta de Risco - Paciente {dados.get('paciente_id')}"
    msg['From'] = EMAIL_REMETENTE
    msg['To'] = EMAIL_DESTINO

    try:
        # Envio utilizando o servidor SMTP do Gmail via SSL
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as servidor:
            servidor.login(EMAIL_REMETENTE, EMAIL_SENHA)
            servidor.send_message(msg)
        print(f"[INFO] E-mail de alerta enviado com sucesso para {EMAIL_DESTINO}.")
    except Exception as e:
        print(f"[ERRO] Falha na automação de e-mail: {e}")

# ==============================================================================
# EXECUÇÃO PRINCIPAL
# ==============================================================================

def main():
    print("Iniciando rotina de monitoramento REST/RPA CardioIA...\n")
    
    # Simulação de um ciclo de leitura 
    dados = consumir_sinais_vitais()
    
    if dados:
        print(f"[GET] Dados recebidos: {json.dumps(dados, indent=2)}")
        
        riscos = avaliar_riscos_clinicos(dados)
        
        if riscos:
            print(f"\n[ALERTA] Anomalias detectadas: {riscos}")
            enviar_alerta_email(dados, riscos)
        else:
            print("\n[INFO] Sinais vitais estáveis. Nenhuma ação requerida.")
            
        registrar_historico_nuvem(dados)

if __name__ == "__main__":
    main()