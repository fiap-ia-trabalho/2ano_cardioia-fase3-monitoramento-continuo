// Ensaio ampliado com broker real e dados dos widgets. Nao simula hardware.
const mqtt=require('../node-red/node_modules/mqtt');
const {io}=require('../node-red/node_modules/socket.io-client');
const assert=require('node:assert/strict');const fs=require('node:fs');const path=require('node:path');
const boot=require('node:crypto').randomBytes(8).toString('hex');
const base='fiap/cardioia/2026/m567659-iot-6a19';
const flow=JSON.parse(fs.readFileSync(path.join(__dirname,'../node-red/flows.json'),'utf8'));
const summaryId=flow.find(n=>n.type==='ui-template').id;
const socket=io('http://127.0.0.1:1880',{path:'/dashboard/socket.io',transports:['polling'],reconnection:false});
const client=mqtt.connect('mqtt://broker.hivemq.com:1883',{clientId:'cardioia-protocolo-'+boot,connectTimeout:10000,reconnectPeriod:0});
const acks=[],summaries=[],results=[];let seq=0;
const wait=ms=>new Promise(r=>setTimeout(r,ms));
const end=setTimeout(()=>{console.error('Tempo excedido');process.exitCode=1;client.end(true);socket.close()},60000);
client.on('message',(_,b)=>{try{const a=JSON.parse(b);if(a.boot_id===boot)acks.push(a)}catch{}});
socket.on('msg-input:'+summaryId,m=>{if(m.payload?.boot_id===boot)summaries.push(m.payload)});
function packet(extra={}){return {schema:1,simulated:true,device_id:'cardioia-teste-02',boot_id:boot,seq:++seq,uptime_ms:70000+seq*5000,age_ms:0,temperature_c:37,humidity_pct:55,accel_x:0,accel_y:0,accel_z:9.806,idle_ms:0,bpm:72,pulse_window_ready:true,queue_pending:1,dropped_total:0,...extra};}
async function until(fn){for(let i=0;i<60;i++){if(fn())return;await wait(100)}throw Error('Resposta esperada nao recebida')}
async function send(p){const n=acks.length;client.publish(base+'/telemetria',JSON.stringify(p),{retain:false,qos:0});await until(()=>acks.length>n);await until(()=>summaries.some(s=>s.seq===p.seq));return summaries.find(s=>s.seq===p.seq)}
async function task(id,fn){await fn();results.push({id,status:'APROVADO'});console.log(id+' OK')}
(async()=>{
 try{
  await Promise.all([new Promise((r,j)=>client.once('connect',()=>client.subscribe(base+'/ack',{qos:1},e=>e?j(e):r()))),new Promise(r=>socket.once('ui-config',r))]);
  const live=await (await fetch('http://127.0.0.1:1880/flows')).json();
  assert.equal(live.find(n=>n.type==='function').func,fs.readFileSync(path.join(__dirname,'../node-red/processar_telemetria.js'),'utf8'),'Runtime deve usar o mesmo codigo testado');
  await task('T13-broker',async()=>{const p=packet();const s=await send(p);assert.equal(s.device_id,p.device_id);assert.equal(s.warnings.length,0)});
  await task('T15-limites',async()=>{const s=await send(packet({temperature_c:38,bpm:120}));assert.equal(s.warnings.length,0);const high=await send(packet({temperature_c:38.1,bpm:121}));assert.equal(high.warnings.length,2);assert.equal((await send(packet())).warnings.length,0)});
  await task('T17-falha',async()=>{const s=await send(packet({temperature_c:null,humidity_pct:null,accel_x:null,accel_y:null,accel_z:null,idle_ms:null,bpm:null,pulse_window_ready:false}));assert.ok(s.warnings.includes('Falha de leitura de sensor'));assert.equal(s.bpm,null)});
  await task('T06-inatividade',async()=>{assert.equal((await send(packet({idle_ms:60000}))).warnings.length,1)});
  await task('T09-perdas',async()=>{assert.ok((await send(packet({dropped_total:3,queue_pending:2000}))).warnings.some(w=>w.includes('3 amostra')))});
  await task('T14-historico',async()=>{const s=await send(packet({age_ms:45000,queue_pending:3}));assert.equal(s.historical,true);assert.equal(s.pending_after_ack,2);assert.ok(s.received_at-s.sample_at===45000)});
  await task('T11-duplicata',async()=>{const p=packet();await send(p);const before=summaries.length;const n=acks.length;client.publish(base+'/telemetria',JSON.stringify(p));await until(()=>acks.length>n);await wait(300);assert.equal(summaries.length,before)});
  await task('T16-invalido',async()=>{for(const p of ['{',packet({boot_id:1234567890123456}),packet({temperature_c:'39'}),packet({accel_x:null})]){const n=acks.length,m=summaries.length;client.publish(base+'/telemetria',typeof p==='string'?p:JSON.stringify(p));await wait(1800);assert.equal(acks.length,n);assert.equal(summaries.length,m)}});
  await task('T19-sessao',async()=>{assert.ok((await send(packet())).seq>0)});
  fs.writeFileSync(path.join(__dirname,'../docs/verificacao_protocolo_mqtt.json'),JSON.stringify({checked_at:new Date().toISOString(),origin:'cliente MQTT sintetico + Socket.IO do servidor',results,acks:acks.length,summaries:summaries.length},null,2));
 }catch(e){console.error(e);process.exitCode=1}
 finally{clearTimeout(end);client.end(true);socket.close()}
})();
