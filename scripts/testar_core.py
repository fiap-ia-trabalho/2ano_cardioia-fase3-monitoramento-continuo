"""Compila/executa o nucleo real. Usa CXX, c++/g++/clang++ ou Zig local de teste."""
from pathlib import Path
import os,shutil,subprocess,json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.local/test-bin';OUT.mkdir(parents=True,exist_ok=True)
zig=ROOT/'.local/compiler/ziglang/zig.exe'
command=os.environ.get('CXX') or next((shutil.which(c) for c in ['c++','g++','clang++'] if shutil.which(c)),None)
if command: compiler=[command]
elif zig.exists(): compiler=[str(zig),'c++']
else: raise SystemExit('Instale um compilador C++ ou defina CXX. Opcional Windows: python -m pip install --target .local/compiler ziglang==0.13.0')
exe=OUT/('core_test.exe' if os.name=='nt' else 'core_test')
subprocess.run(compiler+['-std=c++17','-O0','-g',str(ROOT/'tests/core_test.cpp'),'-o',str(exe)],cwd=ROOT,check=True)
result=subprocess.run([str(exe)],cwd=ROOT,check=True,capture_output=True,text=True)
assert result.stdout.count('PASS ')==7
(ROOT/'docs/verificacao_core.json').write_text(json.dumps({'compiler':Path(compiler[0]).name,'groups_passed':7,'capacity_exercised':2000,'source':'esp32/core.hpp compartilhado com firmware','output':result.stdout},ensure_ascii=False,indent=2),encoding='utf-8')
print(result.stdout)
