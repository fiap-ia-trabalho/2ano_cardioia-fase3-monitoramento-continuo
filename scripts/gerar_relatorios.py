"""Gera os dois relatorios PDF; renderiza cada pagina para revisao visual."""
from pathlib import Path
import json
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Flowable
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from pypdf import PdfReader
import pypdfium2 as pdfium

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/pdf'; OUT.mkdir(parents=True,exist_ok=True)
PREVIEW=ROOT/'tmp/pdfs'; PREVIEW.mkdir(parents=True,exist_ok=True)
for name,file in [('Arial','arial.ttf'),('Arial-Bold','arialbd.ttf'),('Arial-Italic','ariali.ttf')]:
 pdfmetrics.registerFont(TTFont(name,str(Path('C:/Windows/Fonts')/file)))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial-Italic')
INK=colors.HexColor('#173343'); TEAL=colors.HexColor('#007c83'); LIGHT=colors.HexColor('#eaf4f5'); GRAY=colors.HexColor('#5b7280')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleCardio',fontName='Arial-Bold',fontSize=22,leading=26,textColor=INK,spaceAfter=12))
styles.add(ParagraphStyle(name='SubCardio',fontName='Arial',fontSize=10.5,leading=15,textColor=GRAY,spaceAfter=16))
styles.add(ParagraphStyle(name='BodyCardio',fontName='Arial',fontSize=9.8,leading=13.7,textColor=INK,spaceAfter=7))
styles.add(ParagraphStyle(name='HeadCardio',fontName='Arial-Bold',fontSize=12,leading=16,textColor=TEAL,spaceBefore=8,spaceAfter=5))
styles.add(ParagraphStyle(name='SmallCardio',fontName='Arial',fontSize=8.3,leading=11.5,textColor=GRAY,spaceAfter=6))
styles.add(ParagraphStyle(name='TableCardio',fontName='Arial',fontSize=9,leading=12.5,textColor=INK))
def p(s):return Paragraph(s,styles['BodyCardio'])
def h(s):return Paragraph(s,styles['HeadCardio'])
def small(s):return Paragraph(s,styles['SmallCardio'])
def table(rows,widths):
 data=[[Paragraph(str(v),styles['TableCardio']) for v in row] for row in rows]
 t=Table(data,colWidths=widths,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),LIGHT),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),('LINEBELOW',(0,0),(-1,0),.8,TEAL),('LINEBELOW',(0,1),(-1,-1),.35,colors.HexColor('#dae5ea'))]))
 return t
def header(title,sub):return [small('FIAP  |  INTELIGÊNCIA ARTIFICIAL  |  2º ANO  |  CAP 1'),Paragraph(title,styles['TitleCardio']),Paragraph(sub,styles['SubCardio'])]
def footer(canvas,doc):
 canvas.setStrokeColor(colors.HexColor('#d3e2e8'));canvas.line(48,43,A4[0]-48,43)
 canvas.setFont('Arial',8);canvas.setFillColor(GRAY);canvas.drawString(48,29,'CardioIA Conectada  |  Atividade principal  |  04/11/2026')
 canvas.drawRightString(A4[0]-48,29,str(doc.page))
def build(name,story):
 path=OUT/name
 doc=SimpleDocTemplate(str(path),pagesize=A4,leftMargin=48,rightMargin=48,topMargin=43,bottomMargin=59,title=name.replace('_',' '),author='Equipe CardioIA - FIAP')
 doc.build(story,onFirstPage=footer,onLaterPages=footer)
 reader=PdfReader(path);assert len(reader.pages)==2,(name,len(reader.pages))
 assert all(len(pg.extract_text())>900 for pg in reader.pages)
 pdf=pdfium.PdfDocument(str(path))
 for i,page in enumerate(pdf):page.render(scale=1.35).to_pil().save(PREVIEW/(path.stem+f'_{i+1}.png'))
 print(name,'2 paginas')

link='https://wokwi.com/projects/479728974687586305'
checked=ROOT/'docs/verificacao_wokwi.json'
executed=json.loads(checked.read_text(encoding='utf-8-sig')) if checked.exists() else {}
runtime_text=executed.get('report_summary','A execução do circuito no Wokwi está em validação. A compilação local passou; isso não comprova, isoladamente, leitura dos sensores ou recuperação durante a simulação.')

s=header('Parte 1<br/>Coleta e resiliência no Edge','Relatório de funcionamento, armazenamento limitado e recuperação após desconexão.')
s += [h('1. Proposta e componentes'),p('O protótipo representa um dispositivo de monitoramento com ESP32 no Wokwi. São usados dois sensores distintos: DHT22, para temperatura e umidade, e MPU6050, para aceleração. Um botão acrescenta pulsos manuais e uma chave define o booleano de conectividade. Todos os dados são simulados. O DHT22 mede o ambiente, não a temperatura corporal.'),
table([['Componente','Ligação e função'],['DHT22','Dados no GPIO15; alimentação 3V3 e GND. Leitura nominal a cada 5 s.'],['MPU6050','SDA GPIO21 e SCL GPIO22; alimentação 3V3 e GND. Consulta a cada 200 ms.'],['Botão de pulso','GPIO27 e GND, com INPUT_PULLUP. Cada pressão gera um pulso, com intervalo mínimo de 180 ms.'],['Chave / LED','GPIO25: esquerda offline, direita online. GPIO19 aciona LED com resistor de 220 Ω.']],[105,394]),
h('2. Fluxo de coleta e processamento'),p('O laço consulta botão e movimento, captura temperatura/umidade, acrescenta a amostra à fila e tenta sincronizar. Não existe espera infinita para conectar. A leitura contém sequência, sessão aleatória de inicialização, tempo de coleta em millis(), valores e indicadores de disponibilidade. Falhas do DHT são transmitidas como null, em vez de inventar valores.'),
p('O movimento é a diferença entre vetores consecutivos de aceleração: norma superior a 0,8 m/s² reinicia o contador de inatividade. A gravidade constante não conta como movimento. Após 60 s sem mudança, há alerta didático. Pulsos são contados numa janela móvel de 60 s; a primeira janela é apresentada como incompleta. Nenhum pulso manual não constitui conclusão clínica.'),
h('3. Armazenamento limitado'),p('A fila FIFO contém 2.000 amostras de 36 bytes (aproximadamente 72 KB). A cada 5 s, a cobertura nominal de uma fila inicialmente vazia é 10.000 s, ou 2h46min40s. Esse limite preserva memória para Wi-Fi, MQTT e bibliotecas. Na compilação validada, a RAM estática total foi 118.612 bytes de 327.680 (36,2%).'),
p('Ao encher, a estratégia drop-new recusa a nova amostra, mantém as já aceitas e incrementa um contador de perdas. Preservar o histórico e o item em voo simplifica a sincronização FIFO; em contrapartida, perde-se cobertura recente após o limite. O LED ainda avalia a leitura atual. Não se promete resiliência ilimitada.'),PageBreak()]
s+=header('Parte 1<br/>Sincronização e limites','Continuação - comportamento offline e evidências verificáveis.')
s += [h('4. Retorno da conectividade'),p('A chave offline bloqueia o envio, mas mantém coleta, fila e alerta local. No modo padrão MQTT, somente a amostra mais antiga fica em voo. Se não houver confirmação em 3 s, ela é reenviada. O ESP32 só a retira ao receber ACK com o mesmo dispositivo, sessão e sequência. O Node-RED confirma duplicatas novamente e evita acrescentá-las outra vez aos gráficos.'),
p('Para a demonstração específica da Parte 1, o comando s no Monitor Serial habilita saída simulada de nuvem por Serial.println. Com a chave online, cada leitura é impressa antes de sair da fila. O comando m retorna ao MQTT. A saída Serial demonstra o fluxo local; ela não é uma transmissão real para o broker.'),
h('5. Roteiro e evidências'),p(runtime_text),
table([['Cenário','Verificação esperada'],['Offline por 15 s ou mais','Serial continua registrando coleta; ao menos três amostras entram na fila.'],['Retorno online','Sequências antigas são sincronizadas; ACKs reduzem a fila até alcançar o fluxo recente.'],['Sem ACK ou sem Node-RED','O item é reenviado e permanece localmente, em vez de ser apagado por publish().'],['Fila esgotada / reinício','Drop-new registra perdas. Reiniciar a simulação apaga a fila RAM.']],[135,364]),
h('6. Limitações e responsabilidade'),p('O enunciado torna SPIFFS opcional pela limitação dos simuladores. Foi adotada fila RAM com rastreio Serial; ela não persiste após parar ou reiniciar a simulação. O ACK confirma recepção/validação em RAM no Node-RED, não gravação em banco nem revisão humana. Reconexões e chamadas de rede podem atrasar o laço; o período é nominal, sem garantia de tempo real. Não há testes em hardware físico nem validação assistencial.'),
h('Equipe'),small('CAUAN OTTO RODRIGUES SOUSA - RM567940<br/>FERNANDO A GURGEL - RM567606<br/>IRACI MONTEIRO SOUZA - RM567544<br/>MARIA LUISA RODRIGUES NASCIMENTO - RM567659<br/>RAFAELA TORRES MARTINS - RM567735'),
h('Projeto e referências'),small(f'<link href="{link}" color="#007c83">Wokwi: {link}</link><br/>Código: esp32/sketch.ino; circuito: esp32/diagram.json.<br/>Wokwi DHT22: docs.wokwi.com/parts/wokwi-dht22<br/>Wokwi MPU6050: docs.wokwi.com/parts/wokwi-mpu6050')]
build('Relatorio_Parte_1_Edge.pdf',s)

s=header('Parte 2<br/>MQTT e dashboard','Relatório de comunicação Fog/Cloud, visualização e alertas automáticos.')
s += [h('1. Arquitetura de comunicação'),p('O ESP32 é a camada Edge: lê sensores, avalia regras locais e guarda amostras offline. O broker público HiveMQ, acessível pela internet, intermedeia MQTT. O Node-RED no computador atua como consumidor e processamento Fog: valida o JSON, deduplica, prepara os indicadores e devolve ACK. A interface é servida localmente pelo FlowFuse Dashboard, sem necessidade de Grafana.'),
table([['Configuração','Valor usado'],['Broker','broker.hivemq.com, TCP 1883, sem autenticação e sem TLS; somente dados sintéticos.'],['Telemetria','fiap/cardioia/2026/m567659-iot-6a19/telemetria'],['Confirmação','fiap/cardioia/2026/m567659-iot-6a19/ack'],['Entrega','Telemetria QoS 0; ACK publicado pelo Node-RED em QoS 1; retain desativado.'],['Dashboard','http://127.0.0.1:1880/dashboard/monitoramento']],[105,394]),
h('2. Contrato e confirmação'),p('O JSON inclui schema=1, simulated=true, device_id, boot_id, seq, uptime_ms, age_ms, temperatura, umidade, acelerações, inatividade, BPM, disponibilidade da janela, fila e perdas. O consumidor exige tipos e faixas válidas. Pacotes inválidos não recebem ACK. Um ACK contém device_id, boot_id e seq, exatamente como a amostra aceita.'),
p('PubSubClient 2.8 publica em QoS 0: retorno positivo de publish() não comprova entrega ao consumidor. Por isso foi acrescentada confirmação na aplicação. Sem ACK, o registro continua em RAM e é reenviado. A assinatura QoS 1 não aumenta o QoS original da telemetria. O desenho não oferece persistência durável, autenticação ou garantia de entrega exatamente uma vez.'),
h('3. Configuração reproduzível'),p('Node.js 24.18.0 foi usado com Node-RED 5.0.9 e @flowfuse/node-red-dashboard 1.34.1, fixados no package-lock.json. Em node-red/, executar npm ci e npm start; no Windows, há o atalho iniciar_dashboard.bat. O servidor escuta apenas em 127.0.0.1:1880. Em outra instalação, instalar o pacote Dashboard, importar node-red/flows.json pelo menu Import e acionar Deploy.'),
p('O fluxo conecta MQTT in ao Function de validação e deduplicação, e dele aos gráficos, medidores, resumo e MQTT out de ACK. O código fonte do Function está em node-red/processar_telemetria.js; scripts/preparar_projeto.py o insere no export. Deve existir um único consumidor desse fluxo para a demonstração.'),PageBreak()]
s+=header('Parte 2<br/>Visualização e avaliação','Continuação - comportamento do dashboard, testes e segurança.')
s += [h('4. Indicadores e alertas'),p('A página apresenta gráficos de temperatura e pulsos manuais, medidores de temperatura e umidade e um painel de estado. Ele mostra dispositivo, sequência, fila após confirmação, perdas e inatividade. As regras são: temperatura &gt; 38 °C, pulsos &gt; 120 bpm, ausência de mudança de aceleração por pelo menos 60 s, falha de sensor ou perda por fila cheia. São limites didáticos, sem diagnóstico clínico.'),
p('O horário do gráfico é estimado pelo recebimento menos age_ms. A coleta não dispõe de relógio civil sincronizado. Amostras com mais de 10 s de idade são identificadas como histórico recuperado. Após 20 s sem recebimento, o painel informa ausência de leitura recente; as últimas leituras exibidas não passam a representar o estado atual do paciente.'),
h('5. Evidências e resultados'),p('A compilação do firmware para ESP32 foi concluída com sucesso. Dez testes automatizados passaram, cobrindo contrato, limites, sensores indisponíveis, janela incompleta, retransmissão sem duplicação, sessão nova, histórico e limitação de memória da deduplicação. O contexto mantém até 64 sessões, pressupõe fluxo FIFO e é volátil.'),
p('O ensaio MQTT real pelo computador recebeu sete ACKs do Node-RED: leitura regular, alerta, repetição, três amostras históricas e retorno a valores abaixo dos limites. O cliente foi identificado como cardioia-teste-01, sem se passar pelo ESP32. Um teste Socket.IO confirmou cinco widgets, os dados recebidos e os pontos reais dos gráficos; o template Vue também compilou. Arquivos de evidência: docs/verificacao_mqtt.json e docs/verificacao_dashboard.json.'),
p(runtime_text),
h('6. Segurança, eficiência e limites'),p('O broker é compartilhado e sem TLS nesta configuração. Não há validação da origem; terceiros com os tópicos podem publicar mensagens ou ACKs forjados. O namespace reduz colisões, mas não é controle de acesso. Nenhum nome de paciente, identificador pessoal ou dado real de saúde é transmitido. Em produção seriam necessários TLS com certificado validado, broker privado, autenticação, ACLs por dispositivo, banco durável e proteção de dados.'),
p('Amostragem de 5 s, envio de um item em voo, retry de 3 s e fila limitada controlam memória e tráfego. Essa cadência é uma escolha didática, não adequada a sinais de ECG. Reiniciar ESP32 ou Node-RED apaga estados. Testes de protocolo não substituem avaliação visual da interface, disponibilidade contínua nem validação clínica.'),
h('Referências e acesso'),small(f'<link href="{link}" color="#007c83">Simulação Wokwi: {link}</link><br/>Wokwi Wi-Fi: docs.wokwi.com/guides/esp32-wifi<br/>HiveMQ: www.hivemq.com/mqtt/public-mqtt-broker/<br/>Dashboard: dashboard.flowfuse.com/getting-started<br/>Gráficos: dashboard.flowfuse.com/nodes/widgets/ui-chart.html<br/>PubSubClient: github.com/knolleary/pubsubclient')]
build('Relatorio_Parte_2_MQTT_Dashboard.pdf',s)
