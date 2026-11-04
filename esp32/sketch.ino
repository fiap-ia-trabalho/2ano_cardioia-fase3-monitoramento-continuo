/*
 * CardioIA Conectada - atividade principal: Edge -> MQTT -> Node-RED.
 * Somente sinais simulados. DHT22 mede ambiente, nao temperatura corporal.
 * Sensores distintos: DHT22 e acelerometro MPU6050. Botao = pulso manual.
 * Conectividade simulada: chave direita = online; esquerda = offline.
 * Serial: 's' demonstra sincronizacao apenas no Serial; 'm' retorna ao MQTT.
 * RAM e contexto Node-RED sao volateis: nao resistem a reinicio.
 */
#include <Arduino.h>
#include <WiFi.h>
#include <Wire.h>
#include <DHTesp.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <math.h>
#include "core.hpp"

const uint8_t DHT_PIN = 15, PULSE_PIN = 27, ONLINE_PIN = 25, ALERT_PIN = 19;
const uint32_t SAMPLE_MS = 5000, ACK_TIMEOUT_MS = 3000, RETRY_MS = 5000;
const uint16_t CAPACITY = 2000;
const char *BROKER = "broker.hivemq.com";
const char *DEVICE = "cardioia-demo-01";
// Namespace exclusivo deste trabalho. Usar o mesmo no fluxo Node-RED.
const char *DATA_TOPIC = "fiap/cardioia/2026/m567659-iot-6a19/telemetria";
const char *ACK_TOPIC = "fiap/cardioia/2026/m567659-iot-6a19/ack";

FixedQueue<Sample, CAPACITY> queue;
uint32_t nextSeq = 1, dropped = 0;
PulseCounter pulses;
uint32_t lastSample = 0, lastMotion = 0, lastMotionPoll = 0;
uint32_t lastRetry = 0, sentAt = 0, lastSend = 0, lastWifiTry = 0;
bool waitingAck = false, serialOnly = false, connectedSim = true;
bool mpuOk = false, motionBaseline = false, motionValid = false;
float ax = 0, ay = 0, az = 0, oldAx = 0, oldAy = 0, oldAz = 0;
char bootId[17];
DHTesp dht;
Adafruit_MPU6050 mpu;
class BoundedWiFiClient : public WiFiClient {
 public:
  using WiFiClient::connect;
  int connect(const char *host, uint16_t port) override { return WiFiClient::connect(host, port, 1000); }
  int connect(IPAddress ip, uint16_t port) override { return WiFiClient::connect(ip, port, 1000); }
};
BoundedWiFiClient network;
PubSubClient mqtt(network);

// Intervalos por subtracao de uint32_t continuam funcionando no rollover de millis().
void pollPulse(uint32_t now) {
  pulses.poll(now, digitalRead(PULSE_PIN) == LOW);
}

void pollMotion(uint32_t now) {
  if (!mpuOk || uint32_t(now - lastMotionPoll) < 200) return;
  lastMotionPoll = now;
  sensors_event_t a, g, t;
  motionValid = mpu.getEvent(&a, &g, &t) && validMotion(a.acceleration.x,a.acceleration.y,a.acceleration.z);
  if (!motionValid) { motionBaseline=false; return; }
  ax = a.acceleration.x; ay = a.acceleration.y; az = a.acceleration.z;
  // Mudanca do vetor evita confundir a gravidade constante com movimento.
  if (!motionBaseline || changedMotion(ax,ay,az,oldAx,oldAy,oldAz)) lastMotion = now;
  oldAx = ax; oldAy = ay; oldAz = az; motionBaseline = true;
}

void capture(uint32_t now) {
  if (uint32_t(now - lastSample) < SAMPLE_MS) return;
  lastSample = now;
  TempAndHumidity th = dht.getTempAndHumidity();
  Sample s = {};
  s.seq = nextSeq++; s.uptimeMs = now; s.idleMs = now - lastMotion;
  s.temperature = th.temperature; s.humidity = th.humidity;
  s.ax = ax; s.ay = ay; s.az = az; s.bpm = pulses.bpm();
  s.valid = (validDht(th.temperature,th.humidity) ? 1 : 0)
          | (motionValid ? 2 : 0) | (pulses.ready() ? 4 : 0);
  digitalWrite(ALERT_PIN, localAlert(s) ? HIGH : LOW);
  // Politica drop-new: preserva a leitura em voo e o historico ja aceito.
  if (!queue.push(s)) {
    ++dropped;
    Serial.printf("[FILA CHEIA] seq=%lu descartada; perdas=%lu\n", s.seq, dropped);
    return;
  }
  Serial.printf("[COLETA] seq=%lu t=%.1f umidade=%.1f fila=%u/%u online=%d\n",
                s.seq, s.temperature, s.humidity, unsigned(queue.size()), CAPACITY, connectedSim);
}

void toJson(const Sample &s, JsonDocument &doc, uint32_t now) {
  doc["schema"] = 1; doc["device_id"] = DEVICE; doc["boot_id"] = bootId;
  doc["seq"] = s.seq; doc["uptime_ms"] = s.uptimeMs;
  doc["age_ms"] = uint32_t(now - s.uptimeMs);
  if (s.valid & 1) { doc["temperature_c"] = s.temperature; doc["humidity_pct"] = s.humidity; }
  else { doc["temperature_c"] = nullptr; doc["humidity_pct"] = nullptr; }
  if (s.valid & 2) {
    doc["accel_x"] = s.ax; doc["accel_y"] = s.ay; doc["accel_z"] = s.az;
    doc["idle_ms"] = s.idleMs;
  } else { doc["accel_x"] = nullptr; doc["accel_y"] = nullptr; doc["accel_z"] = nullptr; doc["idle_ms"] = nullptr; }
  if (s.valid & 4) doc["bpm"] = s.bpm; else doc["bpm"] = nullptr;
  doc["pulse_window_ready"] = bool(s.valid & 4);
  doc["queue_pending"] = queue.size();
  doc["dropped_total"] = dropped;
  doc["simulated"] = true;
}

void acknowledge(char *topic, byte *payload, unsigned int length) {
  if (!waitingAck || !queue.size() || strcmp(topic, ACK_TOPIC)) return;
  JsonDocument doc;
  if (deserializeJson(doc, payload, length)) return;
  if (!doc["seq"].is<uint32_t>() || !matchesAck(waitingAck,queue.front().seq,doc["seq"].as<uint32_t>(),DEVICE,bootId,doc["device_id"] | "",doc["boot_id"] | "")) return;
  Serial.printf("[SINCRONIZADO MQTT] seq=%lu confirmada pelo Node-RED; fila=%u\n", queue.front().seq, unsigned(queue.size()-1));
  queue.pop(); waitingAck = false;
}

void serviceNetwork(uint32_t now) {
  if (!connectedSim || serialOnly) {
    if (mqtt.connected()) mqtt.disconnect();
    waitingAck = false;
    return;
  }
  if (WiFi.status() != WL_CONNECTED) {
    if (uint32_t(now - lastWifiTry) >= 15000) {
      lastWifiTry = now;
      WiFi.begin("Wokwi-GUEST", "", 6);
    }
    return;
  }
  if (!mqtt.connected()) {
    waitingAck = false;
    if (uint32_t(now - lastRetry) < RETRY_MS) return;
    lastRetry = now;
    String clientId = String(DEVICE) + "-" + bootId;
    if (mqtt.connect(clientId.c_str())) {
      mqtt.subscribe(ACK_TOPIC, 1);
      Serial.println("[MQTT] conectado. Aguardando confirmacoes do dashboard.");
    } else Serial.printf("[MQTT] falha %d; coleta continua.\n", mqtt.state());
  }
  mqtt.loop();
}

void synchronize(uint32_t now) {
  if (!connectedSim || !queue.size()) return;
  if (serialOnly) {
    if (uint32_t(now - lastSend) < 100) return;
    lastSend = now;
    JsonDocument doc; toJson(queue.front(), doc, now);
    Serial.print("[SINCRONIZADO SERIAL - simulacao de nuvem] "); serializeJson(doc, Serial); Serial.println();
    queue.pop();
    return;
  }
  if (!mqtt.connected()) return;
  if (waitingAck && uint32_t(now - sentAt) < ACK_TIMEOUT_MS) return;
  if (uint32_t(now - lastSend) < 100) return;
  lastSend = now;
  JsonDocument doc; toJson(queue.front(), doc, now);
  char buffer[768];
  size_t size = serializeJson(doc, buffer, sizeof(buffer));
  if (size >= sizeof(buffer) - 1) return;
  if (mqtt.publish(DATA_TOPIC, buffer, false)) {
    waitingAck = true; sentAt = now;
    // publish() e QoS 0: so removemos apos ACK da aplicacao.
    Serial.printf("[ENVIO MQTT] seq=%lu aguardando ACK; fila=%u\n", queue.front().seq, unsigned(queue.size()));
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(PULSE_PIN, INPUT_PULLUP); pinMode(ONLINE_PIN, INPUT_PULLUP); pinMode(ALERT_PIN, OUTPUT);
  snprintf(bootId, sizeof(bootId), "%08lx%08lx", (unsigned long)esp_random(), (unsigned long)esp_random());
  dht.setup(DHT_PIN, DHTesp::DHT22);
  Wire.begin(21, 22);
  mpuOk = mpu.begin();
  if (mpuOk) { mpu.setAccelerometerRange(MPU6050_RANGE_8_G); mpu.setFilterBandwidth(MPU6050_BAND_21_HZ); }
  else Serial.println("[SENSOR] MPU6050 indisponivel; temperaturas continuam.");
  network.setTimeout(1); // WiFiClient Arduino-ESP32 2.x: segundos.
  mqtt.setServer(BROKER, 1883); mqtt.setCallback(acknowledge);
  mqtt.setBufferSize(1024); mqtt.setSocketTimeout(1); mqtt.setKeepAlive(15);
  WiFi.mode(WIFI_STA); WiFi.begin("Wokwi-GUEST", "", 6);
  Serial.printf("CardioIA | sessao=%s | capacidade=%u | RAM amostras=%u bytes\n", bootId, CAPACITY, unsigned(sizeof(Sample)*CAPACITY));
  Serial.println("Chave esquerda=offline; direita=online. Serial: s=Parte1; m=MQTT Parte2.");
}

void loop() {
  uint32_t now = millis();
  connectedSim = digitalRead(ONLINE_PIN) == HIGH;
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 's') { serialOnly = true; waitingAck = false; Serial.println("[MODO] Serial - Parte 1"); }
    if (c == 'm') { serialOnly = false; Serial.println("[MODO] MQTT - Parte 2"); }
  }
  pollPulse(now); pollMotion(now); capture(now);
  serviceNetwork(now); synchronize(millis());
  delay(2);
}
