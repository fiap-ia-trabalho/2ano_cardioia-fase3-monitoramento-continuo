# CardioIA Conectada

**FIAP | 2º ano de Inteligência Artificial | Fase 3 | Cap 1 - IoT e Visualização de Dados para a Saúde Digital**

Atividade principal: simulação de coleta no ESP32, resiliência offline, transmissão
MQTT e visualização no Node-RED. Os desafios Ir Além 1 e 2 não fazem parte deste projeto.

> Somente dados simulados. O DHT22 mede temperatura e umidade do ambiente; não mede
> temperatura corporal. O botão representa pulsos manuais, sem sensor cardíaco real.
> Os limites são regras didáticas, sem validação clínica.

Repositório público: [2ano_cardioia-fase3-monitoramento-continuo](https://github.com/fiap-ia-trabalho/2ano_cardioia-fase3-monitoramento-continuo).

## Entregáveis

| Parte | Entregável | Local |
|---|---|---|
| 1 | Link da simulação Wokwi | [Abrir simulação](https://wokwi.com/projects/479728974687586305) |
| 1 e 2 | Código C++ comentado do ESP32 | [esp32/sketch.ino](esp32/sketch.ino) |
| 1 | Circuito com DHT22 e MPU6050 | [esp32/diagram.json](esp32/diagram.json) |
| 1 | Relatório do fluxo e da resiliência, mínimo 1 página | [Relatório Edge](output/pdf/Relatorio_Parte_1_Edge.pdf) |
| 2 | Export do dashboard Node-RED | [node-red/flows.json](node-red/flows.json) |
| 2 | Relatório MQTT e dashboard, mínimo 2 páginas | [Relatório MQTT](output/pdf/Relatorio_Parte_2_MQTT_Dashboard.pdf) |

O export do dashboard e as capturas de execução estão incluídos na entrega.
O texto original está em [docs/enunciado_recebido.txt](docs/enunciado_recebido.txt).

## Fluxo

```text
DHT22 + MPU6050 + botão de pulso
              ↓
         ESP32 / fila FIFO em RAM
              ↓ MQTT (telemetria)
        broker.hivemq.com:1883
              ↓
    Node-RED: validar e deduplicar
          ↙                 ↘
 dashboard e alertas       MQTT ACK → ESP32 remove a amostra
```

O ESP32 lê DHT22 a cada cinco segundos, consulta o acelerômetro a cada 200 ms e
conta bordas de pressão do botão. Cada leitura recebe sequência, sessão aleatória
de inicialização e tempo de coleta em `millis()`. O tempo no gráfico é estimado por
horário de recebimento menos idade da amostra; não é um relógio clínico sincronizado.

## Executar o dashboard

Requer **Node.js 22.9 ou superior**, validado no Node.js 24.18.0.
No Windows, abra `iniciar_dashboard.bat`. Na primeira execução ele instala as
dependências fixadas no `package-lock.json`. Alternativa pelo terminal:

```text
cd node-red
npm ci
npm start
```

- Dashboard: <http://127.0.0.1:1880/dashboard/monitoramento>
- Editor dos fluxos: <http://127.0.0.1:1880/>

Node-RED 5.0.9 e FlowFuse Dashboard 1.34.1. Ambos escutam somente em `127.0.0.1`.
O dashboard mostra dois gráficos (temperatura e pulsos), dois medidores
(temperatura e umidade), sequência, fila, perdas, inatividade e texto de alerta.
Após 20 segundos sem receber mensagens, informa ausência de leitura recente.

Para importar em outro Node-RED, instale `@flowfuse/node-red-dashboard@1.34.1`,
importe `node-red/flows.json` pelo menu Import e clique em Deploy. Não duplique o
fluxo no mesmo servidor: dois consumidores podem produzir ACKs independentes.

## Wokwi e circuito

O projeto usa ESP32 DevKit v1 e dois sensores distintos:

| Componente | Ligação | Função |
|---|---|---|
| DHT22 | SDA → GPIO15; VCC → 3V3; GND → GND | Temperatura e umidade (conta como um sensor) |
| MPU6050 | SDA → GPIO21; SCL → GPIO22; VCC → 3V3; GND → GND | Aceleração e detecção de mudança de movimento |
| Botão | GPIO27 e GND; INPUT_PULLUP | Cada pressão simula um batimento |
| Chave deslizante | Centro → GPIO25; esquerda → GND; direita → 3V3 | Booleano de conectividade: esquerda offline, direita online |
| LED vermelho | GPIO19 → LED → resistor 220 Ω → GND | Alerta local, inclusive offline |

No Wokwi, use os arquivos `sketch.ino`, `core.hpp`, `diagram.json` e `libraries.txt` da pasta
`esp32/`. `main.cpp` é apenas o adaptador para compilação com PlatformIO e não precisa
ser adicionado ao editor web. As bibliotecas e versões estão em `libraries.txt`.

### Demonstração das Partes 1 e 2

1. Inicie o dashboard e a simulação. Abra o Serial em 115200 baud.
2. Na Parte 2, o modo padrão é MQTT. `[SINCRONIZADO MQTT]` indica ACK do Node-RED.
3. Mova a chave para a esquerda. A coleta continua e a fila cresce no Serial.
4. Após pelo menos três amostras, volte para a direita. Observe a mesma sequência
   sendo confirmada, o histórico chegando ao gráfico e a fila esvaziando.
5. Clique no DHT22 e ajuste a temperatura para 39 °C. O LED e o dashboard alertam;
   ao voltar para 37 °C esse motivo é removido. Outro alerta pode continuar ativo.
6. Ajuste a aceleração no MPU6050. O contador de ausência de mudança é reiniciado;
   após 60 segundos sem mudança, aparece o alerta de inatividade didático.
7. O botão (atalho P, com foco no circuito) conta pulsos numa janela móvel de 60 s.
   Antes de completar a primeira janela, o BPM fica indisponível. Zero depois disso
   significa nenhum pulso manual registrado, não um diagnóstico de parada cardíaca.
8. Para demonstrar a Parte 1 sem broker, envie `s` no Serial. Com a chave offline
   a fila cresce; online cada amostra é impressa como sincronização simulada de nuvem
   e retirada. Envie `m` para voltar ao MQTT. O modo Serial não alimenta o dashboard.

## Resiliência e limites

- FIFO de **2.000 amostras**, aproximadamente **72.000 bytes** na fila.
- Período nominal de 5 s: **10.000 s = 2h46min40s** até esgotar uma fila inicialmente vazia.
- Fila cheia: descarta a amostra nova (*drop-new*), preservando o histórico aceito
  e o item aguardando confirmação. Contador de perdas aparece no Serial e no dashboard.
  A cobertura contínua termina no limite; não existe armazenamento ilimitado.
- No MQTT, mantém um item em voo, reenvia após 3 s sem ACK e só remove quando o ACK
  contém dispositivo, sessão e sequência correspondentes. O Node-RED confirma novamente
  duplicatas, mas não as acrescenta outra vez aos gráficos.
- A deduplicação mantém até 64 sessões em RAM e pressupõe envio FIFO de um dispositivo.
- O ACK comprova validação e recepção em RAM pelo Node-RED, não gravação durável,
  renderização no navegador ou atendimento humano.
- RAM do ESP32 e contexto/gráficos do Node-RED são voláteis. Encerrar a simulação
  ou reiniciar os processos apaga seus estados. SPIFFS é opcional no enunciado e
  não foi usado; não há promessa de persistência após reinício.
- Reconexões de rede podem bloquear brevemente. O período é nominal, sem garantia
  de tempo real. Não é firmware adequado para aquisição de ECG ou uso assistencial.

## MQTT e regras

Broker de demonstração: `broker.hivemq.com`, TCP 1883. Não exige conta ou senha.
É um broker público compartilhado, sem TLS neste protótipo; envie somente dados
sintéticos. Não há autenticação da origem nem proteção contra publicação/ACK forjado.
Para uso real seriam necessários broker privado, TLS com validação de certificado,
identidade por dispositivo, ACLs, armazenamento durável e controles de dados de saúde.

| Uso | Tópico |
|---|---|
| Telemetria | `fiap/cardioia/2026/m567659-iot-6a19/telemetria` |
| ACK | `fiap/cardioia/2026/m567659-iot-6a19/ack` |

Telemetria QoS 0 (limite do PubSubClient 2.8); ACK de aplicação, publicação pelo
Node-RED em QoS 1; mensagens sem retain. QoS da assinatura não eleva o QoS da publicação.
O dashboard precisa estar em execução para que o ESP32 esvazie a fila no modo MQTT.

Alertas: temperatura **> 38 °C**, pulsos **> 120 bpm**, ausência de mudança de
aceleração **≥ 60 s**, falha de sensor e perdas por fila cheia. Mudança de movimento:
norma da diferença entre vetores consecutivos **> 0,8 m/s²**, evitando contar a
gravidade constante como movimento. Esses critérios foram escolhidos para demonstração.

## Validação reproduzível

```text
# Na pasta node-red: testes das regras e do export
npm test

# Na raiz, com Node-RED rodando: integração real via broker
node tests/integracao_mqtt.cjs
node tests/dashboard_runtime.cjs

# Compilar o ESP32, com PlatformIO instalado
pio run
```

As evidências ficam em `docs/verificacao_mqtt.json` e
`docs/verificacao_dashboard.json`. O cliente de teste se identifica como
`cardioia-teste-01`; ele não é a simulação do ESP32. O ensaio verifica ACK, duplicata,
alertas e mensagens históricas no servidor e nos dados dos widgets. Teste de protocolo
e compilação não substituem executar o circuito e revisar visualmente o dashboard.

Para regenerar circuito e export após alterar as fontes:
`python scripts/preparar_projeto.py` (Python 3, sem dependências externas).

## Comunicação automatizada com REST e e-mail

Esta atividade complementar estende o monitoramento de sinais vitais com uma camada em Python que consome e publica dados por API REST e dispara alertas automatizados por e-mail quando são detectados riscos.

### Objetivo

Simular um sistema de monitoramento em que dados de temperatura, frequência cardíaca, inatividade e status do sensor sejam enviados para uma API REST, validados por regras de risco e encaminhados para uma automação de e-mail em caso de alerta.

### Estrutura sugerida

```text
Sinais vitais simulados
        ↓
Cliente REST em Python
        ↓
POST /samples
        ↓
API local ou endpoint REST
        ↓
Validação e detecção de risco
        ↙         ↘
     OK          ALERTA
                 ↓
      Geração de e-mail
                 ↓
   Envio automático de alerta
```

### Regras de risco implementadas

- Temperatura > 38 °C: risco de febre.
- BPM > 120: taquicardia.
- Inatividade ≥ 60 s: ausência de movimento ou baixo estímulo.
- Sensor inválido ou ausente: falha de leitura.
- Qualquer combinação desses critérios coloca o status em `alert`.

### Instruções de execução

```bash
cd atividade_rest_email
python3 -m pip install -r requirements.txt
python3 mock_api.py
python3 app.py --patient Maria --temperature 39.2 --bpm 128 --idle-ms 65000
```

### Descrição do fluxo

1. O cliente Python gera ou recebe um payload com `temperature_c`, `bpm`, `idle_ms` e `sensor_ok`.
2. O código envia esses dados para a API REST via `POST /samples`.
3. A API retorna uma confirmação de recebimento.
4. A lógica de risco classifica a amostra como `ok` ou `alert`.
5. Quando há risco, o sistema monta um e-mail de alerta e dispara a automação.
6. Em ambiente didático, a entrega usa simulação de e-mail por padrão para evitar credenciais reais.

### Observações

- O fluxo é didático e simulado, sem uso clínico ou diagnóstico real.
- O envio de e-mail pode ser habilitado em modo real com SMTP e credenciais configuradas em variáveis de ambiente.
- O código está organizado em módulos: cliente REST, regras de risco, envio de e-mail e documentação.

## Integrantes

| Nome | RM |
|---|---|
| CAUAN OTTO RODRIGUES SOUSA | 567940 |
| FERNANDO ARAUJO GURGEL | 567606 |
| IRACI MONTEIRO SOUZA | 567544 |
| MARIA LUISA RODRIGUES NASCIMENTO | 567659 |
| RAFAELA TORRES MARTINS | 567735 |

## Referências

- [Wokwi: rede Wi-Fi do ESP32](https://docs.wokwi.com/guides/esp32-wifi)
- [Wokwi: DHT22](https://docs.wokwi.com/parts/wokwi-dht22)
- [Wokwi: MPU6050](https://docs.wokwi.com/parts/wokwi-mpu6050)
- [HiveMQ: broker público](https://www.hivemq.com/mqtt/public-mqtt-broker/)
- [FlowFuse Dashboard: instalação](https://dashboard.flowfuse.com/getting-started)
- [FlowFuse Dashboard: gráficos](https://dashboard.flowfuse.com/nodes/widgets/ui-chart.html)
- [PubSubClient: limites de QoS e tamanho](https://github.com/knolleary/pubsubclient)

## Evidências de validação

Código compilado para ESP32 e executado no Wokwi. Testes de coleta offline,
recuperação com ACK e fila zerada, saída Serial, temperatura a 39 °C, movimento
e dois pulsos manuais foram exercitados. O dashboard foi revisado visualmente.
As evidências estão em [docs/verificacao_wokwi.json](docs/verificacao_wokwi.json),
[dashboard com alerta](docs/dashboard_alerta.png) e nos registros Serial da pasta `docs/`.
A capacidade de 2.000 posições, a recusa de excedentes, a ordem FIFO e a reutilização do anel foram executadas no núcleo C++ compartilhado com o firmware; o teste não exige aguardar 2h46 de simulação.

O [protocolo de testes](docs/PROTOCOLO_TESTES.md) relaciona os requisitos à validação.
O [resultado consolidado](docs/RESULTADOS_TESTES.md) registra escopo, evidências e limitações.
Para testar o núcleo do ESP32: `python scripts/testar_core.py`, com compilador C++
configurado em `CXX` ou disponível como c++, g++ ou clang++.
