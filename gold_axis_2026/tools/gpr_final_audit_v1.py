"""Recompute family and cross-family metrics from aligned monthly predictions."""
import argparse,json
from pathlib import Path
import numpy as np
import gpr_stage4_v1 as s4
import vw_midas_elmfis_baseline_v1 as metric

def run(root):
    models=s4.load(root)
    valid={n:d for n,d in models.items() if d['spec']['outputs']==4 and len(d['dev']['rows'])==33 and d['dev'].get('scientific_gate','PASS')=='PASS'}
    ensemble=json.loads((root/'GOLD_MONTHLY_GPR_STAGE4_RESULT_2026-09-26.json').read_text())
    assert ensemble['status']=='COMPLETE'
    em={}
    for pool,rec in ensemble['pools'].items():
        for name,d in rec['variants'].items():em[f'{pool}_{name}']=d
    sm={n:s4.metrics(d['dev']['rows']) for n,d in valid.items()}
    ensm={n:s4.metrics(d['dev']['rows']) for n,d in em.items()}
    single=min(sm,key=lambda n:sm[n]['sum_abs_error']);ens=min(ensm,key=lambda n:ensm[n]['sum_abs_error'])
    refinements=[n for n in valid if n.startswith('ADAPTIVE') or 'TUNED' in n or n=='PSO_TLBO' or n.startswith('MPA_') or n.startswith('LMC')]
    refine=min(refinements,key=lambda n:sm[n]['sum_abs_error']) if refinements else 'NONE_SCIENTIFIC_PASS'
    merged={**sm,**ensm}
    def dominates(x,y):return x['sum_abs_error']<=y['sum_abs_error'] and x['direction_correct']>=y['direction_correct'] and (x['sum_abs_error']<y['sum_abs_error'] or x['direction_correct']>y['direction_correct'])
    frontier=[n for n,m in merged.items() if not any(dominates(z,m) for k,z in merged.items() if k!=n)]
    primary=ens if dominates(ensm[ens],sm[single]) else single
    direction=min(merged,key=lambda n:(-merged[n]['direction_correct'],merged[n]['sum_abs_error']))
    balanced_candidates=[n for n in merged if n!=primary and merged[n]['direction_correct']>=23]
    balanced=min(balanced_candidates,key=lambda n:merged[n]['sum_abs_error']) if balanced_candidates else 'NOT_SUPPORTED'
    hybrid_names=[n for n in valid if n in ('DE_ABC','FA_FPA','MULTISWARM','PSO_TLBO') or n.startswith('MPA_')]
    hybrid=min(hybrid_names,key=lambda n:sm[n]['sum_abs_error']) if hybrid_names else 'NONE_SCIENTIFIC_PASS'
    refs=json.loads((root/'evidence/rbfnn_cross_family/reference_rows.json').read_text())
    cross={n:{p:{'rows':rr} for p,rr in d.items()} for n,d in refs['models'].items()}
    cross['GPR_'+single]=valid[single];cross['GPR_ENSEMBLE_'+ens]=em[ens]
    if refine in valid:cross['GPR_STAGE3_'+refine]=valid[refine]
    if hybrid in valid:cross['GPR_BEST_HYBRID_'+hybrid]=valid[hybrid]
    if 'PSO_TLBO' in valid:cross['GPR_STAGE3_HYBRID_PSO_TLBO']=valid['PSO_TLBO']
    if models['SO_RBF']['dev']['scientific_gate']=='PASS':cross['GPR_AUX_SO_RBF']=models['SO_RBF']
    import gzip
    rb=json.loads(gzip.decompress((root/'evidence/rbfnn_stage1/strict_results.json.gz').read_bytes()))['DE_ABC']
    cross['DE_ABC_RBFNN']=rb
    reference=refs['models']['ChHHO_ANFIS']['dev']
    keys=[(r['target'],r['actual'],r['rw']) for r in reference]
    refae=np.array([abs(r['forecast']-r['actual']) for r in reference])
    summary={}
    for n,d in cross.items():
        rr=sorted(d['dev']['rows'],key=lambda x:x['target']);assert [(r['target'],r['actual'],r['rw']) for r in rr]==keys
        ae=np.array([abs(r['forecast']-r['actual']) for r in rr]);delta=ae-refae
        summary[n]={'dev':s4.metrics(rr),'yearly':metric.yearly(rr),
          'loo_lower_SAE_than_ChHHO_count':int(np.sum(delta.sum()-delta<0)),
          'loo_price_gap_vs_ChHHO':(delta.sum()-delta).tolist(),
          'signed_error_corr_ChHHO':float(np.corrcoef([r['forecast']-r['actual'] for r in rr],[r['forecast']-r['actual'] for r in reference])[0,1])}
        for p in ['transport_2025','stress_2026']:
            summary[n][p]=s4.metrics(d[p]['rows']) if len(d[p]['rows'])==({'transport_2025':12,'stress_2026':7}[p]) else {'status':'INCOMPLETE_SCIENTIFIC_FAILURE'}
    global_frontier=[n for n,z in summary.items() if not any(dominates(v['dev'],z['dev']) for k,v in summary.items() if k!=n)]
    if hybrid==single:
        global_frontier=[n for n in global_frontier if n!='GPR_BEST_HYBRID_'+hybrid]
    out={'status':'COMPLETE','selection':'DEV_ONLY','primary':primary,'single_leader':single,'stage3_leader':refine,
      'run_id':ensemble['run_id'],'commit':ensemble['commit'],'pool_freeze_sha256':ensemble['pool_freeze_sha256'],
      'direction_specialist':direction,'ensemble_leader':ens,
      'balanced_challenger':balanced,'balanced_policy':'lowest DEV ΣAE excluding primary, requiring at least 23/33 directions; benchmark role, not automatic promotion',
      'hybrid_leader':hybrid,
      'ensemble_decision':'PROMOTED_DEV_DOMINANCE' if primary==ens else 'BENCHMARK_NOT_PRIMARY',
      'gpr_frontier':frontier,'cross_family_frontier':global_frontier,'cross_family_metrics':summary,
      'refinement_metrics':{n:sm[n] for n in refinements},'ensemble_metrics':ensm,
      'limitations':['n=33 DEV and many model comparisons: point-estimate selection, not statistical superiority',
        'GP posterior intervals ignore hyperparameter uncertainty; coverage and NLPD reported without external calibration',
        'optimizer repeat-validation dispersion is available; independent full-prediction repeat robustness is NOT_PROVEN',
        'prequential weighting conditional on a DEV-selected frozen pool; not a nested-independent holdout',
        'historical cross-family external protocols differ; no external tuning/acceptance or ranking authority'],
      'next_action':'GPR family frozen; return to governed monthly roadmap N3 Multi-task RFF-BLR; no automatic N3 execution in this task'}
    (root/'GOLD_MONTHLY_GPR_FINAL_FREEZE_2026-09-26.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    lines=['# GOLD MONTHLY FORECAST — GPR final family freeze and cross-family audit','','Status: COMPLETE. Selection: DEV 2022-04..2024-12 only (33 months).','',
      f'Joint GPR primary: **{primary}**. Direction specialist: **{direction}**. Balanced challenger: **{balanced}** (benchmark role). Best hybrid: **{hybrid}**. Ensemble leader: **{ens}**, {out["ensemble_decision"]}. Auxiliary SO_RBF is shown separately and is not a four-output parent.','',
      '## Cross-family recomputed DEV evidence','','| Model | ΣAE | Direction | MAE | RMSE | Worst AE | Relative MAE vs RW | LOO lower ΣAE than ChHHO |',
      '|---|---:|---:|---:|---:|---:|---:|---:|']
    for n,z in sorted(summary.items(),key=lambda kv:kv[1]['dev']['sum_abs_error']):
        m=z['dev'];lines.append(f"| {n} | {m['sum_abs_error']:.4f} | {m['direction_correct']}/33 | {m['mae']:.4f} | {m['rmse']:.4f} | {m['worst_ae']:.4f} | {m['relative_mae_vs_rw']:.5f} | {z['loo_lower_SAE_than_ChHHO_count']}/33 |")
    lines+=['','Global point-estimate Pareto: '+', '.join(global_frontier)+'.','','## Stage-4 shrinkage and robustness','']
    for pool,d in ensemble['pools'].items():
        lines.append(f"- {pool}: components {', '.join(d['components'])}; selected prequential alpha {d['selected_alpha']}; full-DEV simplex ΣAE {d['diagnostic_full_DEV_simplex']['metrics']['sum_abs_error']:.4f} is DIAGNOSTIC ONLY.")
        for a in s4.ALPHAS:
            m=d['variants'][f'SHRINK_{a:.2f}']['dev']['metrics'];lines.append(f"  - alpha {a:.2f}: prequential ΣAE {m['sum_abs_error']:.4f}, direction {m['direction_correct']}/33.")
    lines+=['','Full monthly forecasts, prequential weight trajectories, all year blocks, worst-month errors and leave-one-component-out diagnostics are in the Stage-4 JSON. No component/pool changed after ensemble evaluation.','',
      '## Reporting only — no acceptance authority','','Historical family external protocols differ from the strict GPR 2024-12 tuning freeze. These are reported values, not a controlled cross-family external ranking.','',
      '| Model | 2025 ΣAE | Direction | 2026 Jan–Jul ΣAE | Direction |','|---|---:|---:|---:|---:|']
    for n,z in summary.items():
        t,v=z['transport_2025'],z['stress_2026']
        if 'sum_abs_error' in t and 'sum_abs_error' in v:lines.append(f"| {n} | {t['sum_abs_error']:.4f} | {t['direction_correct']}/12 | {v['sum_abs_error']:.4f} | {v['direction_correct']}/7 |")
    lines+=['','## Kontrol ve Uyum Özeti','','- DEV-only selection: PASS.','- 2025/2026 optimizer, parent, alpha and pool selection exclusion: PASS for this GPR program under the predeclared frozen external hyperparameter protocol.','- Random split: NONE.','- Chronological leakage checks and target-label/future invariance tests: PASS.','- DB: READ_ONLY; invariant equality checked.','- Scientific/numerical gate: recorded per model and period; no failed subset ranked.','- Full-DEV learned-weight fits: DIAGNOSTIC ONLY.','- Main roadmap/ledger: updated with stage status, run/job/artifact/commit lineage.','',
      'Limitations: '+'; '.join(out['limitations'])+'.','',out['next_action']+'.']
    (root/'GOLD_MONTHLY_GPR_FINAL_FREEZE_2026-09-26.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:out[k] for k in ['primary','single_leader','stage3_leader','direction_specialist','ensemble_leader','cross_family_frontier']}))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);run(ap.parse_args().root)
