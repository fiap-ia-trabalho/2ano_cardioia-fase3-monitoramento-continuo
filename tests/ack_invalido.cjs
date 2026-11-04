// Ensaio negativo no ESP32: executar com Node-RED parado e item aguardando ACK.
const mqtt=require('../node-red/node_modules/mqtt');const fs=require('node:fs');const path=require('node:path');
const boot=process.argv[2],seq=Number(process.argv[3]);
if(!/^[a-f0-9]{16}$/.test(boot)||!Number.isInteger(seq)||seq<1)throw Error('Uso: node tests/ack_invalido.cjs BOOT_ID SEQUENCIA');
const c=mqtt.connect('mqtt://broker.hivemq.com:1883',{clientId:'cardioia-ack-test-'+Date.now(),reconnectPeriod:0});
const packets=[{device_id:'cardioia-demo-01',boot_id:'ffffffffffffffff',seq},{device_id:'cardioia-outro',boot_id:boot,seq},{device_id:'cardioia-demo-01',boot_id:boot,seq:seq+100}];
const timer=setTimeout(()=>{c.end(true);process.exitCode=1},10000);
c.once('connect',async()=>{
 try{for(const p of packets)await new Promise((r,j)=>c.publish('fiap/cardioia/2026/m567659-iot-6a19/ack',JSON.stringify(p),{qos:1,retain:false},e=>e?j(e):r()));
 fs.writeFileSync(path.join(__dirname,'../docs/ack_negativo_enviado.json'),JSON.stringify({checked_at:new Date().toISOString(),expected_boot:boot,expected_head:seq,packets,interpretation:'Pacotes negativos enviados; rejeicao deve ser conferida no Serial do ESP32.'},null,2));console.log('Tres ACKs negativos publicados.');
 }catch(e){console.error(e);process.exitCode=1}
 finally{clearTimeout(timer);c.end()}
});
