"""Gera diagram.json e export Node-RED a partir dos arquivos-fonte versionados."""
from pathlib import Path
import json
import hashlib

ROOT = Path(__file__).resolve().parents[1]
topic = 'fiap/cardioia/2026/m567659-iot-6a19'
parts = [
    {'type':'wokwi-esp32-devkit-v1','id':'esp','top':30,'left':0,'attrs':{}},
    {'type':'wokwi-dht22','id':'dht','top':-80,'left':220,'attrs':{'temperature':'36.5','humidity':'55'}},
    {'type':'wokwi-mpu6050','id':'mpu','top':80,'left':260,'attrs':{}},
    {'type':'wokwi-pushbutton','id':'pulse','top':250,'left':210,'attrs':{'color':'blue','label':'Pulso manual (P)','key':'P','bounce':'0'}},
    {'type':'wokwi-slide-switch','id':'online','top':-90,'left':-140,'attrs':{'value':'1','bounce':'0'}},
    {'type':'wokwi-led','id':'alert','top':120,'left':-130,'attrs':{'color':'red','label':'Alerta didático'}},
    {'type':'wokwi-resistor','id':'r1','top':180,'left':-120,'attrs':{'value':'220'}},
    {'type':'wokwi-text','id':'label','top':-150,'left':-170,'attrs':{'text':'CARDIOIA CONECTADA\nChave: esquerda OFFLINE / direita ONLINE\nDHT22 + MPU6050 | dados simulados'}}
]
connections = []
def wire(a,b,color): connections.append([a,b,color,[]])
for a,b,c in [('dht:VCC','esp:3V3','red'),('dht:GND','esp:GND.1','black'),('dht:SDA','esp:D15','green'),
              ('mpu:VCC','esp:3V3','red'),('mpu:GND','esp:GND.1','black'),('mpu:SDA','esp:D21','green'),('mpu:SCL','esp:D22','blue'),
              ('pulse:1.r','esp:D27','blue'),('pulse:2.r','esp:GND.1','black'),
              ('online:2','esp:D25','orange'),('online:1','esp:GND.1','black'),('online:3','esp:3V3','red'),
              ('alert:A','esp:D19','red'),('alert:C','r1:1','black'),('r1:2','esp:GND.1','black')]: wire(a,b,c)
diagram = {'version':1,'author':'Equipe CardioIA - FIAP','editor':'wokwi','parts':parts,'connections':connections,'dependencies':{}}
(ROOT/'esp32/diagram.json').write_text(json.dumps(diagram,ensure_ascii=False,indent=2),encoding='utf-8')

status_template = '''<template>
  <section class="cardio-status">
    <div class="cardio-kicker">CARDIOIA CONECTADA · SIMULAÇÃO ACADÊMICA</div>
    <h2>Monitoramento de sinais</h2>
    <div v-if="!msg?.payload?.received_at" class="cardio-muted">Aguardando dados MQTT. Inicie o ESP32 no Wokwi.</div>
    <template v-else>
      <div :class="['cardio-banner', stale ? 'paused' : msg.payload.warnings.length ? 'alert' : 'ok']">
        {{ stale ? 'Sem leitura recente — verifique conexão ou simulação' : msg.payload.historical ? 'Recuperando histórico offline' : msg.payload.warnings.length ? 'Limite de demonstração ultrapassado' : 'Dados recebidos — limites didáticos não ultrapassados' }}
      </div>
      <div class="cardio-grid">
        <div><small>Dispositivo</small><strong>{{ msg.payload.device_id }}</strong></div>
        <div><small>Sequência</small><strong>#{{ msg.payload.seq }}</strong></div>
        <div><small>Fila após confirmação</small><strong>{{ msg.payload.pending_after_ack }} / 2.000</strong></div>
        <div><small>Amostras recebidas</small><strong>{{ msg.payload.accepted }}</strong></div>
        <div><small>Temperatura ambiente</small><strong>{{ formatReading(msg.payload.temperature_c, ' °C') }}</strong></div>
        <div><small>Pulsos manuais / 60 s</small><strong>{{ msg.payload.pulse_window_ready ? formatReading(msg.payload.bpm, ' bpm') : 'Aguardando 60 s' }}</strong></div>
        <div><small>Sem mudança de aceleração</small><strong>{{ msg.payload.idle_ms === null ? 'Sensor indisponível' : (msg.payload.idle_ms/1000).toFixed(0)+' s' }}</strong></div>
        <div><small>Perdas por fila cheia</small><strong>{{ msg.payload.dropped_total }}</strong></div>
      </div>
      <ul v-if="msg.payload.warnings.length"><li v-for="item in msg.payload.warnings" :key="item">{{ item }}</li></ul>
      <p class="cardio-muted">Recebimento: {{ new Date(msg.payload.received_at).toLocaleTimeString('pt-BR') }} · {{ msg.payload.historical ? 'Histórico recuperado' : 'Fluxo recente' }}</p>
    </template>
    <p class="cardio-note">DHT22 mede o ambiente. Pulsos são acionados manualmente. Alertas são regras de demonstração, sem interpretação clínica.</p>
  </section>
</template>
<script>
export default {
  data() { return { clock:Date.now(), timer:null } },
  mounted() { this.timer=setInterval(()=>{this.clock=Date.now()},1000) },
  unmounted() { clearInterval(this.timer) },
  computed:{ stale(){return this.msg?.payload?.received_at && this.clock-this.msg.payload.received_at>20000} },
  methods:{ formatReading(v,unit){return v===null ? 'Indisponível' : Number(v).toLocaleString('pt-BR',{maximumFractionDigits:1})+unit} }
}
</script>
<style>
.cardio-status{padding:12px 18px;color:#182d3b}.cardio-kicker{font-size:11px;letter-spacing:1.5px;color:#007c83;font-weight:700}.cardio-status h2{font-size:28px;margin:8px 0 16px;letter-spacing:-.7px}.cardio-banner{border-radius:10px;padding:12px 16px;margin-bottom:18px;font-weight:600}.cardio-banner.ok{background:#e0f4ee;color:#126047}.cardio-banner.alert{background:#ffe6df;color:#973c24}.cardio-banner.paused{background:#fff1d1;color:#7f5b12}.cardio-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:16px 24px}.cardio-grid small{display:block;color:#627785;font-size:12px;margin-bottom:4px}.cardio-grid strong{font-size:18px}.cardio-muted,.cardio-note{font-size:12px;color:#627785;margin-top:16px}.cardio-note{border-top:1px solid #dce7ed;padding-top:12px}.cardio-status li{font-size:13px;color:#973c24}
</style>'''
flow=[
 {'id':'cardio-flow','type':'tab','label':'CardioIA | Edge → MQTT → Dashboard','disabled':False,'info':'Somente atividade principal. Telemetria e ACK de aplicacao, sem banco persistente.'},
 {'id':'broker','type':'mqtt-broker','name':'HiveMQ público · dados sintéticos','broker':'broker.hivemq.com','port':'1883','clientid':'','autoConnect':True,'usetls':False,'protocolVersion':'4','keepalive':'30','cleansession':True,'autoUnsubscribe':True},
 {'id':'base','type':'ui-base','name':'CardioIA','path':'/dashboard','includeClientData':True,'acceptsClientConfig':['ui-notification','ui-control'],'showPathInSidebar':False,'headerContent':'page','navigationStyle':'default','titleBarStyle':'default','showReconnectNotification':True,'notificationDisplayTime':'1','showDisconnectNotification':True},
 {'id':'theme','type':'ui-theme','name':'CardioIA Claro','colors':{'surface':'#ffffff','primary':'#007c83','bgPage':'#eef4f6','groupBg':'#ffffff','groupOutline':'#dce7ed'},'sizes':{'density':'default','pagePadding':'16px','groupGap':'16px','groupBorderRadius':'12px','widgetGap':'12px'}},
 {'id':'page','type':'ui-page','name':'CardioIA · Monitoramento','ui':'base','path':'/monitoramento','icon':'monitor-heart','layout':'grid','theme':'theme','breakpoints':[{'name':'Default','px':'0','cols':'3'},{'name':'Tablet','px':'576','cols':'6'},{'name':'Desktop','px':'1024','cols':'12'}],'order':1,'className':'','visible':True,'disabled':False},
 {'id':'summary-group','type':'ui-group','name':'Visão geral','page':'page','width':'12','height':'1','order':1,'showTitle':False,'visible':'true','disabled':'false'},
 {'id':'chart-group','type':'ui-group','name':'Histórico dos sinais','page':'page','width':'8','height':'1','order':2,'showTitle':True,'visible':'true','disabled':'false'},
 {'id':'gauge-group','type':'ui-group','name':'Últimas leituras','page':'page','width':'4','height':'1','order':3,'showTitle':True,'visible':'true','disabled':'false'},
 {'id':'mqtt-in','type':'mqtt in','z':'cardio-flow','name':'Telemetria do ESP32','topic':topic+'/telemetria','qos':'1','datatype':'auto-detect','broker':'broker','nl':False,'rap':False,'rh':0,'x':170,'y':180,'wires':[['process']]},
 {'id':'process','type':'function','z':'cardio-flow','name':'Validar, deduplicar e confirmar','func':(ROOT/'node-red/processar_telemetria.js').read_text(encoding='utf-8'),'outputs':6,'timeout':0,'noerr':0,'initialize':'','finalize':'','libs':[],'x':460,'y':180,'wires':[['temp-chart'],['bpm-chart'],['temp-gauge'],['hum-gauge'],['summary','debug'],['mqtt-ack']]},
 {'id':'mqtt-ack','type':'mqtt out','z':'cardio-flow','name':'ACK para o ESP32','topic':topic+'/ack','qos':'1','retain':'false','respTopic':'','contentType':'','userProps':'','correl':'','expiry':'','broker':'broker','x':790,'y':380,'wires':[]},
 {'id':'summary','type':'ui-template','z':'cardio-flow','group':'summary-group','name':'Estado e alertas','order':1,'width':'12','height':'0','format':status_template,'storeOutMessages':False,'passthru':False,'resendOnRefresh':True,'templateScope':'local','x':800,'y':320,'wires':[[]]},
 {'id':'debug','type':'debug','z':'cardio-flow','name':'Dados validados','active':False,'tosidebar':True,'console':False,'tostatus':False,'complete':'payload','targetType':'msg','x':800,'y':440,'wires':[]},
 {'id':'notes','type':'comment','z':'cardio-flow','name':'Broker público: dados simulados. ACK = recepção em RAM, não gravação durável.','info':'Desconecte no Wokwi pela chave. O FIFO so esvazia apos ACK. Tempo do grafico estimado por recebimento menos idade da amostra.','x':410,'y':80,'wires':[]}
]
for id,label,order,color,y in [('temp-chart','Temperatura ambiente (°C)',1,'#007c83',80),('bpm-chart','Pulsos manuais por minuto',2,'#d06d43',140)]:
 flow.append({'id':id,'type':'ui-chart','z':'cardio-flow','group':'chart-group','name':label,'label':label,'order':order,'width':'8','height':'4','chartType':'line','category':'topic','categoryType':'msg','xAxisLabel':'Horário estimado da coleta','xAxisProperty':'payload.time','xAxisPropertyType':'msg','xAxisType':'time','xAxisFormat':'{HH}:{mm}:{ss}','yAxisLabel':'°C' if order==1 else 'bpm','yAxisProperty':'payload.value','yAxisPropertyType':'msg','action':'append','pointShape':'circle','pointRadius':1,'showLegend':False,'removeOlder':3,'removeOlderUnit':'3600','removeOlderPoints':'2200','colors':[color],'textColor':['#182d3b'],'textColorDefault':False,'gridColor':['#e2ebee'],'gridColorDefault':False,'interpolation':'linear','x':800,'y':y,'wires':[[]]})
for id,label,unit,minv,maxv,order,y in [('temp-gauge','Temperatura ambiente','°C',0,50,1,200),('hum-gauge','Umidade relativa','%',0,100,2,260)]:
 flow.append({'id':id,'type':'ui-gauge','z':'cardio-flow','group':'gauge-group','name':label,'order':order,'width':'4','height':'4','gtype':'gauge-half','gstyle':'needle','title':label,'alwaysShowTitle':True,'units':unit,'icon':'thermometer' if order==1 else 'water-percent','prefix':'','suffix':'','segments':[{'from':str(minv),'color':'#007c83'},{'from':'38' if order==1 else '70','color':'#d06d43'}],'min':minv,'max':maxv,'sizeThickness':16,'sizeGap':4,'sizeKeyThickness':8,'value':'payload','valueType':'msg','x':800,'y':y,'wires':[[]]})
# IDs opacos evitam que valores como headerContent='page' sejam interpretados
# pelo runtime como referencias a um config node tambem chamado 'page'.
ids = {n['id']:hashlib.sha256(('cardioia/'+n['id']).encode()).hexdigest()[:16] for n in flow}
for n in flow:
 n['id'] = ids[n['id']]
 for key in ['z','group','page','ui','theme','broker']:
  if key in n and n[key] in ids: n[key] = ids[n[key]]
 if 'wires' in n: n['wires'] = [[ids[target] for target in wire] for wire in n['wires']]
(ROOT/'node-red/flows.json').write_text(json.dumps(flow,ensure_ascii=False,indent=2),encoding='utf-8')
print('Circuito e fluxo Node-RED gerados.')
