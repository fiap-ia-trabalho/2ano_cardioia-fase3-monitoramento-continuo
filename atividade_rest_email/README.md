# Monitoramento com REST e e-mail

Projeto didático de monitoramento de sinais vitais em Python.

## Objetivo

Simular um fluxo em que um cliente REST envia e recebe dados de sinais vitais, calcula risco e dispara alerta automatizado por e-mail.

## Estrutura

- `app.py`: ponto de entrada para execução do cliente.
- `config.py`: configuração de API e SMTP.
- `risk_engine.py`: regras de detecção de risco.
- `rest_client.py`: cliente HTTP para consumir a API REST.
- `mailer.py`: criação e envio do e-mail de alerta.
- `mock_api.py`: API REST local de demonstração.
- `tests/test_monitoramento.py`: testes básicos da lógica.

## Como executar

1. Instale as dependências:

```bash
cd atividade_rest_email
python3 -m pip install -r requirements.txt
```

2. Inicie a API local:

```bash
python3 mock_api.py
```

3. Envie um exemplo de monitoramento:

```bash
python3 app.py --patient Maria --temperature 39.2 --bpm 128 --idle-ms 65000
```

## Lógica de risco

- temperatura > 38 °C: febre
- bpm > 120: taquicardia
- idle_ms >= 60.000 ms: inatividade
- sensor_ok = False: falha de sensor

Qualquer motivo crítico coloca o resultado em estado `alert`.

## Observação

Por padrão, o envio de e-mail roda em modo simulado para evitar dependência de credenciais externas. Para usar SMTP real, configure as variáveis de ambiente:

- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `FROM_EMAIL`
- `TO_EMAIL`
