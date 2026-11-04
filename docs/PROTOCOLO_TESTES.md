# Protocolo sistêmico de testes - CardioIA Fase 3

Escopo: **atividade principal, Partes 1 e 2**. Ir Além 1 e 2 ficam fora.
Fonte: enunciado integral recebido, conferido na atividade FIAP 661499 em 04/11/2026.
Fase 3, Capítulo 1.

## Critérios e rastreabilidade

| ID | Requisito | Tarefas de teste / resultado esperado |
|---|---|---|
| T01 | Entregáveis das Partes 1 e 2 | Conferir C++ comentado, Wokwi público, circuito, export, relatórios de pelo menos 1 e 2 páginas, instruções e integrantes. |
| T02 | Código executável | Compilar firmware para ESP32, instalar dependências fixadas do dashboard em pasta limpa e iniciar o export sem erro de nó/configuração. |
| T03 | Dois sensores distintos | Verificar circuito DHT22 + MPU6050 e alterar leituras no Wokwi, observando os dados no consumidor. DHT22 conta como um sensor. |
| T04 | Leitura periódica | Confirmar sequência crescente e intervalo nominal de 5 s no Serial/telemetria; admitir atrasos de rede documentados. |
| T05 | Botão de batimentos | Conferir janela inicial indisponível, pressões, debounce, expiração em 60 s e limiar de 120 bpm. |
| T06 | Movimento | Alterar aceleração, verificar reset da inatividade e alerta ao alcançar 60 s sem mudança. |
| T07 | Booleano offline | Desligar a chave, continuar a coleta, não transmitir e manter a fila. |
| T08 | Retorno online | Reconectar e confirmar as mesmas sequências guardadas, em FIFO; fila deve chegar a zero sem inventar amostras. |
| T09 | Armazenamento limitado | Executar o núcleo C++ com as 2.000 posições: aceitar até o limite, recusar a próxima, manter a amostra em voo e recuperar espaço após confirmação. |
| T10 | Falta de confirmação | Interromper o Node-RED com ESP32 online; observar reenvio da mesma sequência e crescimento da fila. Reiniciar consumidor e recuperar. |
| T11 | Confirmação correspondente | Rejeitar ACK de sessão/dispositivo/sequência diferentes e não remover item sem confirmação; confirmar duplicatas no consumidor sem duplicar gráfico. |
| T12 | Parte 1 por Serial | Modo `s`, offline acumula; online imprime cada amostra antes de removê-la. Voltar ao MQTT com `m`. |
| T13 | Broker real | Publicar/assinar no HiveMQ por MQTT e receber ACK; distinguir cliente de teste do ESP32 simulado. |
| T14 | Dashboard | Confirmar gráficos, gauges e resumo com valores reais da simulação, incluindo recarga da página e histórico recuperado. |
| T15 | Limites e retorno | Verificar 38 °C / 120 bpm sem alerta desses motivos; valores superiores com alerta; retorno abaixo do limite remove o motivo. |
| T16 | Dados inválidos | JSON malformado, tipos incorretos, faixas inválidas e medições inconsistentes não recebem ACK nem alteram os widgets. |
| T17 | Falha de sensor | Valores indisponíveis não viram zero; falha aparece no resumo; kernel de firmware trata leitura inválida. |
| T18 | Dados desatualizados | Sem mensagens por mais de 20 s, mostrar falta de leitura recente; não apresentar último estado como atual. |
| T19 | Reinício | Reiniciar consumidor e ESP32; observar nova sessão e declarar perda do estado RAM. Não alegar persistência após encerramento. |
| T20 | Tempo e memória | Exercitar wraparound uint32, janela de pulsos, limite de deduplicação em 64 sessões e tamanho/uso da RAM compilada. |
| T21 | Segurança e eficiência | Confirmar somente dados sintéticos, ausência de credenciais versionadas, bind local 127.0.0.1, broker público sem TLS declarado, limites e retry documentados. |
| T22 | Relatórios e pacote | Renderizar/revisar todas as páginas, verificar links e conteúdo ZIP, excluir caches/dependências/credenciais; extrair o pacote e executar verificações. |
| T23 | Publicação | Criar repositório público no padrão `2ano_cardioia-fase3-monitoramento-continuo`; conferir branch main, arquivos, PDF, link Wokwi e igualdade com commit entregue. |

## Camadas e evidências

1. Núcleo C++ utilizado pelo firmware: fila, confirmação, pulsos, movimento, alertas e tempo.
2. Function Node-RED: contrato, regras, histórico e deduplicação.
3. Integração MQTT + Socket.IO: broker e dados efetivamente armazenados pelos widgets.
4. Ponta a ponta no navegador: ESP32 no Wokwi -> HiveMQ -> Node-RED -> dashboard -> ACK -> fila.
5. Entrega: instalação limpa, PDFs, ZIP e GitHub.

Registrar comandos/contagens nas evidências estruturadas e capturas em `docs/`.
Revisão estática, teste automatizado, teste na simulação e teste em hardware físico
são categorias diferentes. Não marcar execução física, SPIFFS ou Grafana: são opcionais
e não foram adotados. O teste acelerado da fila exercita 2.000 posições no mesmo núcleo
C++, sem precisar aguardar 2h46; ele não é um ensaio de autonomia física.

## Critério de encerramento

Todos os requisitos obrigatórios devem ter evidência de aprovação. Falhas descobertas
precisam de correção e reteste. Limites de projeto devem permanecer declarados. A execução em hardware físico não integra a validação deste protótipo simulado.
