# Relatório Técnico: Comunicação Automatizada com REST e RPA (Ir Além 1)
**Projeto CardioIA - A Nova Era da Cardiologia Inteligente**

## 1. Objetivo do Módulo
Este documento descreve a implementação da camada de automação corporativa do projeto CardioIA. O objetivo deste módulo é atuar como um consumidor dos dados gerados na borda (Edge) e na nuvem (MQTT/Node-RED), operando de forma autônoma para detectar riscos críticos nos sinais vitais dos pacientes e acionar equipes médicas imediatamente por e-mail, sem a necessidade de monitoramento humano contínuo nas dashboards.

## 2. Arquitetura e Comunicação REST
A aplicação foi desenvolvida em Python e estruturada para funcionar como um cliente REST. 
A comunicação bidirecional ocorre através da biblioteca padrão `requests`:
- **Consumo (GET):** A função `consumir_sinais_vitais()` realiza requisições para a API simulada, obtendo um payload em formato JSON que contém a identificação do paciente, o *timestamp* da medição, a temperatura, os batimentos cardíacos (BPM) e o índice de movimento.
- **Registro e Sincronização (POST):** Após o processamento da regra de negócio, a função `registrar_historico_nuvem()` efetua o envio de um *body* JSON via método POST. Este passo simula a inserção do histórico processado em um prontuário eletrônico ou banco de dados centralizado.

## 3. Lógica de Verificação de Risco
O script incorpora regras de negócios clínicas no método `avaliar_riscos_clinicos()`. A triagem de alertas baseia-se em parâmetros predefinidos para identificar anomalias sistêmicas:
1. **Taquicardia:** Disparada caso os batimentos cardíacos ultrapassem o limite de **120 BPM**.
2. **Febre Alta:** Disparada se a leitura do sensor de temperatura indicar um valor superior a **38,0 °C**.
3. **Inatividade:** Disparada se a leitura do sensor de movimento (acelerômetro simulado) registrar ausência de variação (valor 0), sugerindo possível queda ou desmaio.

A lógica é cumulativa. O sistema constrói um array de riscos, permitindo que o e-mail detalhe se o paciente está sofrendo de apenas um sintoma isolado ou de múltiplas falhas simultâneas (ex: taquicardia associada a desmaio).

## 4. Automação de Processos (RPA) e Envio de E-mail
O processo de alerta foi automatizado utilizando o protocolo SMTP. Assim que o vetor de riscos é preenchido com uma ou mais anomalias, a função `enviar_alerta_email()` é invocada.
- **Construção do Alerta:** Utilizamos a biblioteca `email.message.EmailMessage` para formatar adequadamente o escopo do e-mail, incluindo cabeçalhos, assunto emergencial com ID do paciente e corpo contendo a listagem clara dos riscos e as métricas exatas no momento da ocorrência.
- **Segurança da Comunicação:** O despacho é feito de forma segura conectando-se à porta 465 (SMTP over SSL) por meio do `smtplib.SMTP_SSL`, autenticando a aplicação emissora (conta de serviço) para evitar que mensagens de alerta de saúde sejam interceptadas ou caiam em filtros de spam hospitalares.

## 5. Conclusão
A implementação cumpre integralmente os requisitos de comunicação via protocolo HTTP, lógica de verificação de anomalias paramétricas e automação de alertas (RPA). O código foi estruturado com forte tratamento de exceções (blocos *try/except* e *raise_for_status*) e tipagem clara, provando a viabilidade de uma camada inteligente paralela à visualização de dashboards que age proativamente perante o risco, elevando a segurança do modelo de monitoramento contínuo em saúde digital.