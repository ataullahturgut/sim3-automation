"""Recompute all GP period metrics and enforce chronology/freeze provenance."""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
import vw_midas_elmfis_baseline_v1 as metric

def audit(d):
 assert d['status']=='COMPLETE'
 assert d['authority']['invariants_before']==d['authority']['invariants_after']
 assert hashlib.sha256(json.dumps(d['dev'],sort_keys=True).encode()).hexdigest()==d['dev_freeze_sha256']
 summary={}
 for period,n in [('dev',33),('transport_2025',12),('stress_2026',7)]:
  part=d[period];assert len(part['rows'])+len(part['failures'])==n
  assert len({r['target'] for r in part['rows']})==len(part['rows'])
  for r in part['rows']:
   a=r['diag'];assert a['inner_train_last']<a['validation_first']<=a['validation_last']<r['target'] and a['train_last']<r['target']
   if period!='dev':assert a['tuning_last']=='2024-12' and a['theta_sha256']==d['external_freeze']['theta_sha256']
   assert a['condition_upper_bound']<=1e12
   assert all(math.isfinite(p) and abs(p)<1 for p in r['pred_returns'])
   assert all(v>0 and math.isfinite(v) for v in a['observation_return_variance'])
   assert r['gold_interval95'][0]<=r['forecast']<=r['gold_interval95'][1]
  if part['scientific_gate']=='PASS':
   m=metric.active_metrics(part['rows'])
   for k,v in m.items():assert np.isclose(v,part['metrics'][k],rtol=1e-10,atol=1e-10),(period,k)
   ae=np.array([abs(r['forecast']-r['actual']) for r in part['rows']]);m.update(worst_ae=float(ae.max()),worst_month=part['rows'][int(ae.argmax())]['target'],max_condition_bound=max(r['diag']['condition_upper_bound'] for r in part['rows']))
   summary[period]=m
  else:summary[period]={'status':'SCIENTIFIC_REJECTED','failures':part['failures']}
 return summary

def report(root,out):
 ds=[json.loads(p.read_text()) for p in sorted(root.glob('gpr_*_result.json'))];summary={d['method']:audit(d) for d in ds}
 lines=['# GPR cumulative evidence — audited artifacts','','Selection authority DEV only. External metrics reporting only, theta/kernel/scaler frozen at 2024-12.','', '| Model | DEV ΣAE | Direction | MAE | RMSE | 95% coverage | Max condition upper bound | Decision |','|---|---:|---:|---:|---:|---:|---:|---|']
 for d in sorted(ds,key=lambda d:d['dev']['metrics']['sum_abs_error'] if d['dev']['metrics'] else math.inf):
  if d['dev']['scientific_gate']!='PASS':lines.append(f"| {d['method']} | SCIENTIFIC_REJECTED | — | — | — | — | — | Not ranked | ");continue
  m=summary[d['method']]['dev'];u=d['dev']['uncertainty'];lines.append(f"| {d['method']} | {m['sum_abs_error']:.4f} | {m['direction_correct']}/33 | {m['mae']:.4f} | {m['rmse']:.4f} | {u['coverage95']:.4f} | {m['max_condition_bound']:.4g} | {d['dev_decision_frozen_before_external']} |")
 lines+=['','## Reporting only','','| Model | 2025 ΣAE / direction | 2026 ΣAE / direction |','|---|---|---|']
 for d in ds:
  values=[]
  for period,n in [('transport_2025',12),('stress_2026',7)]:
   m=d[period]['metrics'];values.append(f"{m['sum_abs_error']:.4f} / {m['direction_correct']}/{n}" if m else 'SCIENTIFIC_FAILURE')
  lines.append('| '+d['method']+' | '+' | '.join(values)+' |')
 lines+=['','## Provenance and interpretation','']
 for d in ds:lines.append(f"- {d['method']}: run {d['run_id']}, commit `{d['commit']}`; exact source, bounds and per-origin hyperparameters/optimizer termination retained in artifact. Job/artifact IDs in adjacent provenance and ledger.")
 lines+=['','Intervals are uncalibrated predictive-observation intervals. Coverage/NLPD are diagnostics, not new acceptance authority. Finite budget-limited L-BFGS candidates are explicitly recorded and are not claims of converged/global optima.','','## Kontrol ve Uyum Özeti','','DEV-only PASS; 2025/2026 tuning/selection exclusion PASS; random split NONE; chronology and freeze hashes PASS; DB READ_ONLY/invariants equal; scientific failures retained without subset ranking; provenance recorded.']
 out.write_text('\n'.join(lines)+'\n');out.with_suffix('.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n');print(json.dumps(summary))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('out',type=Path);a=p.parse_args();report(a.root,a.out)
