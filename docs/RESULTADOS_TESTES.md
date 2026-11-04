# Resultados de validação - CardioIA Fase 3

Data: 04/11/2026. Escopo: atividade principal, Partes 1 e 2.

## Testes automatizados

- **7 grupos C++ aprovados**: fila real de 2.000 amostras, drop-new, FIFO, reutilização
  circular, confirmação correspondente, pulsos/debounce/expiração, rollover uint32,
  sensores e limites dos alertas. O firmware importa o mesmo `esp32/core.hpp` testado.
- **11 testes Node-RED aprovados**: contrato, limites, sensores indisponíveis,
  janela incompleta, duplicatas, reinício de sessão, histórico e memória limitada.
- **9 cenários MQTT + Socket.IO aprovados**, com broker real: operação regular,
  limites e retorno, falha, inatividade, perdas, histórico, duplicata, rejeição de dados
  inválidos e continuidade de sequência. O ensaio verifica igualdade entre o Function
  em execução e o arquivo fonte local antes de aceitar os resultados.
- **7 ACKs no teste de integração** e **5 widgets no teste de runtime**.
- Instalação isolada com `npm ci`, sem reutilizar `node_modules`, seguida da inicialização
  do export e repetição dos testes de integração: aprovada.
- Compilação ESP32: aprovada; **118.620 bytes de RAM estática (36,2%)**, dos quais
  72.000 bytes correspondem às 2.000 amostras, e **790.773 bytes de flash (60,3%)**.

## Matriz de execução

| Teste | Resultado e evidência |
|---|---|
| T01 - entregáveis | Código, quatro arquivos Wokwi, export, documentação e dois relatórios de duas páginas. |
| T02 - instalação/compilação | Compilação ESP32 e instalação isolada aprovadas; `verificacao_instalacao.json`. |
| T03/T04 - sensores e período | DHT22 e MPU6050 no Wokwi; sequência e período nominal no Serial; registro `e2e_*.txt`. |
| T05 - pulsos | Pressões no Wokwi; debounce, janela, expiração e limite exercitados no C++; `verificacao_core.json`. |
| T06 - movimento | Mudança de aceleração e inatividade observadas na simulação; limites também exercitados no C++/MQTT. |
| T07/T08 - offline/recuperação | Coleta continua com chave offline; mesmas sequências confirmadas após reconectar; fila chega a zero. |
| T09 - capacidade | 2.000 posições preenchidas no núcleo C++; excedente recusado; FIFO e reutilização conferidos. |
| T10 - falta de ACK | Node-RED interrompido: mesmo item reenviado e fila cresce; retorno do consumidor recupera as leituras. |
| T11 - ACK/duplicatas | Três ACKs incorretos enviados ao ESP32, sem remover o item; duplicatas confirmadas sem repetir gráficos. |
| T12 - Serial | Modo `s`: acumulação offline e impressão/remoção ao reconectar; retorno ao MQTT por `m`. |
| T13/T14 - MQTT/dashboard | Broker real e cinco widgets conferidos; dashboard revisado no navegador e após recarga. |
| T15 - limites | 38 °C/120 bpm e valores superiores exercitados no C++/MQTT; temperatura alta e retorno observados no Wokwi. |
| T16/T17 - dados inválidos/falha | JSON/tipos/faixas/inconsistências rejeitados sem ACK; valores nulos e falhas de leitura não viram zero. |
| T18 - desatualização | Após interrupção, painel exibe “Sem leitura recente”; captura `dashboard_sem_dados.png`. |
| T19 - reinício | Reinício do consumidor e nova sessão do ESP32; reinicialização do estado RAM declarada. |
| T20 - tempo/memória | Rollover, janela e limite de 64 sessões exercitados; uso estático conferido na compilação. |
| T21 - segurança | Somente sinais sintéticos; bind em 127.0.0.1; limitações de autenticação/TLS e volatilidade documentadas. |
| T22 - documentos/pacote | Páginas renderizadas/revisadas; ZIP íntegro, links e arquivos obrigatórios conferidos. |
| T23 - publicação | Branch main publicada e conferida no repositório público indicado no README. |

## Correções aplicadas

1. Contrato MQTT passou a exigir identificadores textuais e consistência entre as
   leituras de cada sensor; mensagens inconsistentes não recebem confirmação.
2. O firmware verifica o retorno e os valores do acelerômetro, em vez de tratar
   sucesso na inicialização como garantia de todas as leituras seguintes.
3. Falha de sensor também aciona o indicador local.
4. A janela de pulsos preserva o aquecimento após rollover de `millis()` e expira
   timestamps antes de inserir um novo pulso na janela limitada.
5. Núcleo da fila e das regras compartilhado entre firmware e testes C++.
6. Relatórios, identificação da Fase 3, nome dos integrantes e lista de arquivos
   atualizados. Documentação de entrega revisada para linguagem técnica.

## Limites da validação

Não houve execução em hardware físico, persistência em SPIFFS, Grafana ou validação
clínica. Esses itens não são requisitos obrigatórios da implementação simulada adotada.
A fila cheia foi exercitada no núcleo C++ com a capacidade real, sem aguardar 2h46.
Falhas de sensor foram exercitadas no núcleo e no contrato de mensagens; não houve
ensaio de defeito eletrônico real. Broker público e estados voláteis permanecem
limitações explicitamente declaradas, não garantias de uso assistencial.
