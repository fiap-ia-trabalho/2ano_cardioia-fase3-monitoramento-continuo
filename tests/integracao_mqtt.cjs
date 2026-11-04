// Teste finito via broker real. Origem explicitamente identificada como teste,
// sem fingir que e o ESP32. Exige o Node-RED iniciado com o export do projeto.
const mqtt=require('../node-red/node_modules/mqtt');
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const base='fiap/cardioia/2026/m567659-iot-6a19';
const boot=crypto.randomBytes(8).toString('hex');
const results=[];
const client=mqtt.connect('mqtt://broker.hivemq.com:1883',{clientId:'cardioia-check-'+boot,connectTimeout:10000,reconnectPeriod:0});
const pending=new Map();
client.on('message',(_,buffer)=>{try{const a=JSON.parse(buffer);if(a.boot_id===boot&&pending.has(a.seq)){pending.get(a.seq)(a);pending.delete(a.seq);}}catch{}});
const timeout=setTimeout(()=>{console.error('Timeout: confirme broker e Node-RED iniciado.');client.end(true);process.exitCode=1;},45000);
const pause=ms=>new Promise(r=>setTimeout(r,ms));
async function send(seq,extra={}){
 const p={schema:1,simulated:true,device_id:'cardioia-teste-01',boot_id:boot,seq,uptime_ms:65000+seq*5000,age_ms:0,temperature_c:36.5,humidity_pct:55,accel_x:0,accel_y:0,accel_z:9.806,idle_ms:1000,bpm:72,pulse_window_ready:true,queue_pending:1,dropped_total:0,...extra};
 const ack=new Promise((resolve,reject)=>{const t=setTimeout(()=>{pending.delete(seq);reject(new Error('ACK ausente seq '+seq));},10000);pending.set(seq,a=>{clearTimeout(t);resolve(a)});});
 client.publish(base+'/telemetria',JSON.stringify(p),{qos:0,retain:false});
 const value=await ack;results.push({seq,ack:value,temperature:p.temperature_c,age_ms:p.age_ms});return p;
}
client.once('connect',()=>client.subscribe(base+'/ack',{qos:1},async error=>{
 try{
  if(error)throw error;
  await send(1); await pause(150);
  await send(2,{temperature_c:39.2,bpm:130}); await pause(150);
  await send(2,{temperature_c:39.2,bpm:130}); // reenvio precisa receber ACK
  await send(3,{age_ms:30000,queue_pending:3});
  await send(4,{age_ms:25000,queue_pending:2});
  await send(5,{age_ms:20000});
  await send(6,{temperature_c:37.1,humidity_pct:58,idle_ms:0});
  const out={checked_at:new Date().toISOString(),origin:'cliente MQTT de teste no computador; nao simulacao de ESP32',broker:'broker.hivemq.com:1883',ack_count:results.length,boot_id:boot,results};
  fs.writeFileSync(path.join(__dirname,'../docs/verificacao_mqtt.json'),JSON.stringify(out,null,2));
  console.log('OK: '+results.length+' ACKs reais; duplicata, alerta e historico exercitados.');
 }catch(e){console.error(e);process.exitCode=1;}
 finally{clearTimeout(timeout);client.end();}
}));
client.on('error',e=>{console.error(e.message);clearTimeout(timeout);process.exitCode=1;client.end(true);});
