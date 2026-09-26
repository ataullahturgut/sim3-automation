"""Import downloaded stage3 artifact ZIPs, audit, archive and update provenance.
Usage: python tools/gpr_archive_stage3_v1.py RUN STAGE --attachments PATH
"""
from pathlib import Path
import sys,json,gzip,zipfile,urllib.request,re,contextlib,io,argparse
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from gpr_audit_v1 import audit,report
ap=argparse.ArgumentParser();ap.add_argument('run');ap.add_argument('stage');ap.add_argument('--attachments',type=Path,required=True);a=ap.parse_args()
out=root/'evidence/gpr_stage3';out.mkdir(parents=True,exist_ok=True)
for p in a.attachments.rglob('*.zip'):
 with zipfile.ZipFile(p) as z:
  for n in z.namelist():
   if not (n.startswith('gpr_') and n.endswith('_result.json')):continue
   raw=z.read(n);d=json.loads(raw)
   if d.get('run_id')!=a.run:continue
   audit(d);(out/Path(n).name).write_bytes(raw)
base='https://api.github.com/repos/ataullahturgut/sim3-automation/actions/runs/'+a.run
jobs=json.load(urllib.request.urlopen(base+'/jobs?per_page=100'))['jobs'];arts=json.load(urllib.request.urlopen(base+'/artifacts?per_page=100'))['artifacts']
p=out/'provenance.json';prov=json.loads(p.read_text()) if p.exists() else {}
models={d['method']:d for p in out.glob('gpr_*_result.json') for d in [json.loads(p.read_text())]}
ledger=root/'GOLD_MONTHLY_ELM_METAHEURISTIC_LEDGER_ANN_PLAN_2026-09-25.md';text=ledger.read_text()
for n,d in models.items():
 if d['run_id']!=a.run:continue
 job=next((j for j in jobs if n in j['name']),jobs[0] if len(jobs)==1 else None);artifact=next(x for x in arts if n in x['name'] or len(arts)==1)
 assert job and job['conclusion']=='success'
 prov[n]={'run_id':int(a.run),'job_id':job['id'],'artifact_id':artifact['id'],'commit':d['commit'],'stage':a.stage}
 title=f'### GPR Stage {a.stage} — {n} / AUDITED'
 if title in text:continue
 lines=['','',title,'',f"Run {a.run}; job {job['id']}; artifact {artifact['id']}; execution commit `{d['commit']}`. Full per-origin parameters, optimizer bounds/source hashes, termination, exact posterior diagnostics and repeat selection remain in raw archive.",'','| Period | ΣAE | Direction | Gate |','|---|---:|---:|---|']
 for period,nn in [('dev',33),('transport_2025',12),('stress_2026',7)]:
  part=d[period];m=part['metrics'];lines.append(f"| {period} | {m['sum_abs_error']:.4f} | {m['direction_correct']}/{nn} | {part['scientific_gate']} |" if m else f'| {period} | — | — | SCIENTIFIC_REJECTED |')
 lines+=['','Decision: DEV-only candidate; final role awaits all Stage3 methods. External results reporting only.','','Kontrol ve Uyum Özeti: chronology, DEV hash, strict external theta freeze, positive uncertainty and numerical gates PASS for accepted rows; DB READ_ONLY/invariants equal; no random split; incomplete scientific periods not ranked.','']
 text+='\n'.join(lines)
ledger.write_text(text);p.write_text(json.dumps(prov,indent=2,sort_keys=True)+'\n');(out/'results.json.gz').write_bytes(gzip.compress(json.dumps(models,sort_keys=True,separators=(',',':')).encode(),mtime=0))
with contextlib.redirect_stdout(io.StringIO()):report(out,root/'GOLD_MONTHLY_GPR_STAGE3_REPORT_2026-09-26.md')
print(json.dumps({n:{'dev':d['dev']['metrics'],'stage':d['stage']} for n,d in models.items()}))
