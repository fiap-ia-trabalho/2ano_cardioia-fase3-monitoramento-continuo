// Captura finita somente dos topicos do projeto para evidenciar o ensaio Wokwi.
const fs=require('node:fs');const path=require('node:path');const mqtt=require('../node-red/node_modules/mqtt');
const root=path.join(__dirname,'../');const output=path.join(root,'docs/e2e_mqtt.ndjson');
const c=mqtt.connect('mqtt://broker.hivemq.com:1883',{clientId:'cardioia-observador-'+Date.now(),reconnectPeriod:2000});
c.on('connect',()=>c.subscribe('fiap/cardioia/2026/m567659-iot-6a19/+',{qos:1}));
c.on('message',(topic,b)=>{try{const p=JSON.parse(b);if(p.device_id==='cardioia-demo-01')fs.appendFileSync(output,JSON.stringify({received_at:new Date().toISOString(),topic,payload:p})+'\n')}catch{}});
c.on('error',e=>console.error(e.message));setTimeout(()=>c.end(true),600000);
