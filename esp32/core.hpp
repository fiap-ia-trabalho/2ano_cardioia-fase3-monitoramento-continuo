#pragma once
// Nucleo independente de Arduino, compartilhado pelo ESP32 e pelos testes C++.
#include <stdint.h>
#include <stddef.h>
#include <math.h>
#include <string.h>

struct Sample {
  uint32_t seq, uptimeMs, idleMs;
  float temperature, humidity, ax, ay, az;
  uint16_t bpm;
  uint8_t valid; // bit 0: DHT; bit 1: MPU; bit 2: janela completa
};
static_assert(sizeof(Sample) == 36, "Revisar dimensionamento da fila");

template<class T, size_t Capacity> class FixedQueue {
  T storage[Capacity];
  size_t head = 0, count = 0;
 public:
  bool push(const T &value) {
    if (count == Capacity) return false; // drop-new preserva item em voo
    storage[(head + count) % Capacity] = value; ++count; return true;
  }
  const T &front() const { return storage[head]; } // chamar apenas se size()>0
  bool pop() {
    if (!count) return false;
    head = (head + 1) % Capacity; --count; return true;
  }
  size_t size() const { return count; }
};

inline uint32_t elapsedMs(uint32_t now, uint32_t before) { return now - before; }
inline bool validDht(float t, float h) {
  return isfinite(t) && isfinite(h) && t >= -40 && t <= 80 && h >= 0 && h <= 100;
}
inline bool validMotion(float x, float y, float z) {
  return isfinite(x) && isfinite(y) && isfinite(z) && fabsf(x)<=80 && fabsf(y)<=80 && fabsf(z)<=80;
}
inline bool changedMotion(float x,float y,float z,float oldX,float oldY,float oldZ) {
  float dx=x-oldX, dy=y-oldY, dz=z-oldZ;
  return sqrtf(dx*dx+dy*dy+dz*dz) > .8f;
}
inline bool localAlert(const Sample &s) {
  return !(s.valid & 1) || !(s.valid & 2) || s.temperature > 38.0f
      || ((s.valid & 4) && s.bpm > 120) || s.idleMs >= 60000;
}
inline bool matchesAck(bool waiting, uint32_t headSeq, uint32_t seq,
                       const char *expectedDevice, const char *expectedBoot,
                       const char *device, const char *boot) {
  return waiting && seq==headSeq && !strcmp(expectedDevice,device) && !strcmp(expectedBoot,boot);
}

class PulseCounter {
  uint32_t times[300];
  uint16_t head=0, count=0;
  uint32_t last=0;
  bool oldPressed=false, hasPulse=false, warmed=false;
 public:
  void poll(uint32_t now, bool pressed) {
    if (now >= 60000) warmed=true;
    while(count && elapsedMs(now,times[head])>=60000) {head=(head+1)%300;--count;}
    if(pressed && !oldPressed && (!hasPulse || elapsedMs(now,last)>=180)) {
      if(count<300) { times[(head+count)%300]=now; ++count; }
      last=now; hasPulse=true;
    }
    oldPressed=pressed;
  }
  uint16_t bpm() const { return count; }
  bool ready() const { return warmed; }
};
