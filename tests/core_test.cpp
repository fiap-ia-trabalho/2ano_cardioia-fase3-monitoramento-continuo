#include "../esp32/core.hpp"
#include <assert.h>
#include <stdio.h>
#include <limits.h>

int main() {
  FixedQueue<Sample,2000> queue;
  Sample s={};
  assert(!queue.pop());
  for(unsigned i=1;i<=2000;++i){s.seq=i;assert(queue.push(s));}
  assert(queue.size()==2000 && queue.front().seq==1);
  s.seq=2001;assert(!queue.push(s));assert(queue.front().seq==1 && queue.size()==2000);
  // Confirma mil registros, reutiliza o anel e preserva a ordem dos demais.
  for(unsigned i=1;i<=1000;++i){assert(queue.front().seq==i);assert(queue.pop());}
  for(unsigned i=2002;i<=3001;++i){s.seq=i;assert(queue.push(s));}
  for(unsigned i=1001;i<=2000;++i){assert(queue.front().seq==i);queue.pop();}
  for(unsigned i=2002;i<=3001;++i){assert(queue.front().seq==i);queue.pop();}
  assert(queue.size()==0 && !queue.pop());
  puts("PASS fila: capacidade 2000, drop-new, item em voo, wrap e FIFO");

  assert(matchesAck(true,8,8,"d","b","d","b"));
  assert(!matchesAck(false,8,8,"d","b","d","b"));
  assert(!matchesAck(true,8,9,"d","b","d","b"));
  assert(!matchesAck(true,8,8,"d","b","outro","b"));
  assert(!matchesAck(true,8,8,"d","b","d","outra"));
  puts("PASS ACK: sessao, dispositivo, sequencia e item em voo");

  PulseCounter pulse;
  pulse.poll(0,false);assert(!pulse.ready());
  pulse.poll(100,true);pulse.poll(150,false);pulse.poll(200,true);pulse.poll(250,false);
  assert(pulse.bpm()==1); // segunda pressao foi ruido dentro de 180 ms
  pulse.poll(400,true);pulse.poll(500,false);assert(pulse.bpm()==2);
  pulse.poll(60000,false);assert(pulse.ready() && pulse.bpm()==2);
  pulse.poll(60100,false);assert(pulse.bpm()==1);
  pulse.poll(60400,false);assert(pulse.bpm()==0);
  puts("PASS pulsos: aquecimento, debounce, contagem e expiracao");

  PulseCounter atRollover;
  atRollover.poll(UINT32_MAX-500,true);atRollover.poll(UINT32_MAX-300,false);
  atRollover.poll(100,true);assert(atRollover.ready() && atRollover.bpm()==2);
  atRollover.poll(60000,false);assert(atRollover.bpm()==1);
  atRollover.poll(60100,false);assert(atRollover.bpm()==0);
  assert(elapsedMs(10,UINT32_MAX-5)==16);
  puts("PASS tempo: rollover uint32 sem reiniciar aquecimento");

  PulseCounter cap;
  for(unsigned i=0;i<300;++i){cap.poll(i*180,true);cap.poll(i*180+10,false);}
  assert(cap.bpm()==300);
  cap.poll(54100,true);cap.poll(54110,false);assert(cap.bpm()==300);
  cap.poll(60000,true);assert(cap.bpm()<=300);
  puts("PASS limite de 300 timestamps na janela de pulsos");

  assert(validDht(-40,0) && validDht(80,100));
  assert(!validDht(NAN,55) && !validDht(39,101));
  assert(validMotion(0,0,9.806f) && !validMotion(NAN,0,1));
  assert(!changedMotion(0,0,9.806f,0,0,9.806f));
  assert(!changedMotion(.79f,0,9.806f,0,0,9.806f));
  assert(changedMotion(.81f,0,9.806f,0,0,9.806f));
  puts("PASS sensores: faixas, NaN, gravidade e mudanca vetorial");

  Sample reading={};reading.valid=7;reading.temperature=38;reading.bpm=120;reading.idleMs=59999;
  assert(!localAlert(reading));
  reading.temperature=38.1f;assert(localAlert(reading));reading.temperature=38;
  reading.bpm=121;assert(localAlert(reading));reading.bpm=120;
  reading.idleMs=60000;assert(localAlert(reading));reading.idleMs=0;
  reading.valid=6;assert(localAlert(reading));reading.valid=5;assert(localAlert(reading));
  puts("PASS alertas: limites, recuperacao, inatividade e falha local");
  puts("RESULTADO: 7 grupos C++ aprovados");
}
