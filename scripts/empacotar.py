"""Empacota somente os entregaveis; exclui dependencias, caches e dados locais."""
from pathlib import Path
import zipfile,re,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
DEST=Path.home()/'Downloads/CardioIA_Conectada_Atividade_Principal.zip'
SKIP={'.git','.pio','.local','node_modules','tmp','__pycache__'}
files=[p for p in ROOT.rglob('*') if p.is_file() and not any(s in SKIP for s in p.relative_to(ROOT).parts) and not p.name.startswith('.config') and not p.name.endswith(('_cred.json','.log'))]
names={p.relative_to(ROOT).as_posix() for p in files}
required=['esp32/sketch.ino','esp32/diagram.json','esp32/libraries.txt','node-red/flows.json','node-red/package-lock.json','README.md','docs/link_wokwi.txt','output/pdf/Relatorio_Parte_1_Edge.pdf','output/pdf/Relatorio_Parte_2_MQTT_Dashboard.pdf','ENTREGA_CARDIOIA_CONECTADA.txt','docs/verificacao_wokwi.json']
assert all(p in names for p in required)
for p in files:
 if p.suffix=='.md':
  for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
   if '://' not in target and not target.startswith('#'):assert (p.parent/target.split('#')[0]).exists(),target
with zipfile.ZipFile(DEST,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted(files):z.write(p,'CardioIA_Conectada/'+p.relative_to(ROOT).as_posix())
with zipfile.ZipFile(DEST) as z:assert z.testzip() is None
print(json.dumps({'arquivo':str(DEST),'bytes':DEST.stat().st_size,'arquivos':len(files),'sha256':hashlib.sha256(DEST.read_bytes()).hexdigest()},ensure_ascii=False,indent=2))
