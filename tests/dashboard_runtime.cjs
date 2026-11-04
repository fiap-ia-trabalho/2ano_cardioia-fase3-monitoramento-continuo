// Inspecao do protocolo publico Socket.IO do dashboard local, sem automacao de navegador.
const {io}=require('../node-red/node_modules/socket.io-client');
const {parse,compileTemplate,compileScript}=require('../node-red/node_modules/@vue/compiler-sfc');
const fs=require('node:fs');
const path=require('node:path');
const assert=require('node:assert/strict');
const flow=JSON.parse(fs.readFileSync(path.join(__dirname,'../node-red/flows.json'),'utf8'));
const template=flow.find(n=>n.type==='ui-template');
const parsed=parse(template.format);
assert.equal(parsed.errors.length,0);
assert.equal(compileTemplate({source:parsed.descriptor.template.content,filename:'CardioIA.vue',id:'cardioia'}).errors.length,0);
compileScript(parsed.descriptor,{id:'cardioia'});
const socket=io('http://127.0.0.1:1880',{path:'/dashboard/socket.io',transports:['polling'],reconnection:false});
const received={};
const timeout=setTimeout(()=>{console.error('Timeout no protocolo do dashboard');process.exitCode=1;socket.close()},12000);
socket.on('connect_error',e=>{console.error(e.message);process.exitCode=1;clearTimeout(timeout);socket.close()});
socket.on('ui-config',(base,config)=>{
 try{
  assert.equal(Object.keys(config.widgets).length,5);
  for(const n of flow.filter(n=>['ui-template','ui-chart','ui-gauge'].includes(n.type))){
   assert.ok(config.widgets[n.id],n.name);
   socket.once('widget-load:'+n.id,(data)=>{
    received[n.name]={type:n.type,data};
    if(Object.keys(received).length===5){
     try{
      const summary=received['Estado e alertas'].data;
      assert.equal(summary.payload.device_id,'cardioia-teste-01');
      assert.equal(summary.payload.seq,6);
      const chart=received['Temperatura ambiente (°C)'].data;
      assert.ok(Array.isArray(chart));
      assert.ok(chart.some(p=>p._datapoint?.y===39.2),'alerta chegou ao grafico real');
      assert.ok(chart.every(p=>Number.isFinite(p._datapoint.x)&&Number.isFinite(p._datapoint.y)));
      const out={checked_at:new Date().toISOString(),vue_template_compiled:true,widget_count:5,origin:'protocolo Socket.IO local, sem revisao visual no navegador',widgets:received};
      fs.writeFileSync(path.join(__dirname,'../docs/verificacao_dashboard.json'),JSON.stringify(out,null,2));
      console.log('OK: template Vue valido; 5 widgets registrados, dados e pontos dos graficos conferidos.');
     }catch(e){console.error(e);process.exitCode=1;}
     finally{clearTimeout(timeout);socket.close()}
    }
   });
   socket.emit('widget-load',n.id,{});
  }
 }catch(e){console.error(e);process.exitCode=1;clearTimeout(timeout);socket.close()}
});
