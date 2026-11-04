// Corpo do Function node; o gerador insere este mesmo codigo em flows.json.
// ACK significa recebido/validado em RAM pelo Node-RED, nao gravado em banco.
let p = msg.payload;
try { if (typeof p === 'string' || Buffer.isBuffer(p)) p = JSON.parse(p.toString()); }
catch { node.warn('JSON invalido: sem ACK'); return null; }
const integer = (v, min, max) => Number.isInteger(v) && v >= min && v <= max;
const nullable = (v, min, max) => v === null || (typeof v === 'number' && Number.isFinite(v) && v >= min && v <= max);
if (!p || p.schema !== 1 || p.simulated !== true || typeof p.device_id !== 'string' ||
    !/^cardioia-[a-z0-9-]{1,40}$/.test(p.device_id) || typeof p.boot_id !== 'string' ||
    !/^[a-f0-9]{16}$/.test(p.boot_id) || !integer(p.seq, 1, 4294967295) ||
    !integer(p.uptime_ms, 0, 4294967295) || !integer(p.age_ms, 0, 4294967295) ||
    !integer(p.queue_pending, 1, 2000) || !integer(p.dropped_total, 0, 4294967295) ||
    !nullable(p.temperature_c, -40, 80) || !nullable(p.humidity_pct, 0, 100) ||
    !nullable(p.accel_x, -80, 80) || !nullable(p.accel_y, -80, 80) || !nullable(p.accel_z, -80, 80) ||
    !(p.idle_ms === null || integer(p.idle_ms, 0, 4294967295)) ||
    ((p.temperature_c === null) !== (p.humidity_pct === null)) ||
    !([p.accel_x,p.accel_y,p.accel_z,p.idle_ms].every(v=>v===null) ||
      [p.accel_x,p.accel_y,p.accel_z,p.idle_ms].every(v=>v!==null)) ||
    typeof p.pulse_window_ready !== 'boolean' ||
    !(p.pulse_window_ready ? integer(p.bpm, 0, 300) : p.bpm === null)) {
    node.warn('Telemetria fora do contrato: sem ACK'); return null;
}
const ack = { payload: JSON.stringify({device_id:p.device_id, boot_id:p.boot_id, seq:p.seq}) };
const key = p.device_id + '/' + p.boot_id;
const state = context.get('state') || {sessions:{}, order:[], accepted:0, duplicates:0};
if (state.sessions[key] !== undefined && p.seq <= state.sessions[key]) {
    state.duplicates++;
    context.set('state', state);
    return [null, null, null, null, null, ack];
}
if (state.sessions[key] === undefined) {
    state.order.push(key);
    // Limite de memoria: as 64 sessoes mais recentes. Um dispositivo por execucao.
    if (state.order.length > 64) delete state.sessions[state.order.shift()];
}
state.sessions[key] = p.seq;
state.accepted++;
context.set('state', state);
const receivedAt = Date.now();
const estimatedAt = receivedAt - p.age_ms;
const warnings = [];
if (p.temperature_c !== null && p.temperature_c > 38) warnings.push('Temperatura acima de 38 °C');
if (p.bpm !== null && p.bpm > 120) warnings.push('Pulsos simulados acima de 120 bpm');
if (p.idle_ms !== null && p.idle_ms >= 60000) warnings.push('Sem mudança de aceleração há 60 s');
if (p.temperature_c === null || p.humidity_pct === null || p.idle_ms === null) warnings.push('Falha de leitura de sensor');
if (p.dropped_total > 0) warnings.push(p.dropped_total + ' amostra(s) perdida(s) por fila cheia');
const summary = { ...p, received_at:receivedAt, sample_at:estimatedAt,
    historical:p.age_ms > 10000, warnings, accepted:state.accepted,
    duplicates:state.duplicates, pending_after_ack:Math.max(0,p.queue_pending-1) };
const point = (topic,value) => value === null ? null : {topic, payload:{time:estimatedAt,value}};
return [point('Temperatura',p.temperature_c), point('Pulsos manuais',p.bpm),
    p.temperature_c === null ? null : {payload:p.temperature_c},
    p.humidity_pct === null ? null : {payload:p.humidity_pct},
    {payload:summary}, ack];
