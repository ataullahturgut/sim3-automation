"""Recompute artifact metrics and emit one authoritative cumulative Stage-1 report."""
import argparse,hashlib,json,math
from pathlib import Path
import numpy as np
import vw_midas_elmfis_baseline_v1 as metric

def audit(d):
    assert d['status']=='COMPLETE'
    assert d['authority']['invariants_before']==d['authority']['invariants_after']
    digest=hashlib.sha256(json.dumps(d['dev'],sort_keys=True).encode()).hexdigest()
    assert digest==d['dev_freeze_sha256']
    for period,n in [('dev',33),('transport_2025',12),('stress_2026',7)]:
        part=d[period]
        assert len(part['rows'])+len(part['failures'])==n
        assert len({r['target'] for r in part['rows']})==len(part['rows'])
        for r in part['rows']:
            dg=r['diag']; assert dg['train_last']<r['target']
            if period!='dev' and 'external_lineage' in d:
                assert dg['tuning_last']=='2024-12'
                assert dg['frozen_geometry_sha256']==d['external_lineage']['frozen_geometry_sha256']
            else:
                assert dg['inner_train_last']<dg['validation_first']<=dg['validation_last']<r['target']
            assert all(math.isfinite(x) and abs(x)<1 for x in r['pred_returns'])
            assert dg['design_condition']<=d['spec']['condition_limit']
            if 'initial_cluster_counts' in dg:assert min(dg['initial_cluster_counts'])>0
        if part['scientific_gate']=='PASS':
            m=metric.active_metrics(part['rows'])
            for k,v in m.items():assert np.isclose(v,part['metrics'][k],rtol=1e-10,atol=1e-10),(period,k)
            ae=np.array([abs(r['forecast']-r['actual']) for r in part['rows']])
            m.update(worst_ae=float(ae.max()),worst_target=part['rows'][int(ae.argmax())]['target'],
                     leave_one_origin_sum_min=float(ae.sum()-ae.max()),leave_one_origin_sum_max=float(ae.sum()-ae.min()))
            part['audited_metrics']=m
    return d

def report(root,out):
    records=[audit(json.loads(p.read_text())) for p in sorted(root.glob('rbfnn_stage1_*_result.json'))]
    lines=['# RBFNN Stage 1 — artifact audit and cumulative results','',
      'Selection authority: DEV 2022-04..2024-12 only. 2025/2026 reporting only. No parent frozen.',
      'Exact optimizer equations/constants: source file, function and SHA256 in each artifact. Population 24, generations 45, repeats 3.',
      'Script `gold_axis_2026/tools/vw_midas_rbfnn_stage1_v1.py`; workflow `.github/workflows/gold-monthly-rbfnn-stage1-v1.yml`.',
      'Numerical audit checks all available rows, chronology, full-period coverage, invariant equality, DEV freeze hash and recomputed metrics.','',
      '| Model | DEV ΣAE | Direction | MAE | RMSE | RW relative MAE | RW wins | Worst AE | Gate |',
      '|---|---:|---:|---:|---:|---:|---:|---:|---|']
    valid=sorted([d for d in records if d['dev']['scientific_gate']=='PASS'],key=lambda d:d['dev']['metrics']['sum_abs_error'])
    for d in valid:
        m=d['dev']['audited_metrics']; lines.append(f"| {d['method']} | {m['sum_abs_error']:.4f} | {m['direction_correct']}/33 | {m['mae']:.4f} | {m['rmse']:.4f} | {m['relative_mae_vs_rw']:.5f} | {round(m['monthly_win_rate_vs_rw']*33)}/33 | {m['worst_ae']:.4f} | PASS |")
    for d in records:
        if d not in valid:lines.append(f"| {d['method']} | NOT_RANKED | — | — | — | — | — | — | SCIENTIFIC_FAIL |")
    lines+=['','## External reporting — excluded from selection','',
      'Only STRICT_FROZEN rows are authoritative. Original expanding-tuning external rows are SUPERSEDED pending strict pre-2025 tuning freeze. DEV remains unchanged.',
      '| Model | 2025 ΣAE | 2025 direction | 2026 Jan–Jul ΣAE | 2026 direction |','|---|---:|---:|---:|---:|']
    for d in records:
        vals=[]
        for p,n in [('transport_2025',12),('stress_2026',7)]:
            m=d[p]['metrics'];vals.extend([f"{m['sum_abs_error']:.4f}",f"{m['direction_correct']}/{n}"] if m else ['SCIENTIFIC_FAIL','—'])
        if 'external_lineage' not in d:vals=['SUPERSEDED']*4
        lines.append('| '+d['method']+' | '+' | '.join(vals)+' |')
    lines+=['','## Provenance and decisions','']
    for d in records:
        lines += [f"- {d['method']}: run {d['run_id']}; commit `{d['commit']}`; decision {d['dev_decision_frozen_before_external']}. Source `{d['spec']['optimizer_source']}` / `{d['spec']['optimizer_function']}`."]
    lines+=['','Job/artifact IDs are recorded in the main ledger batch entries and evidence provenance JSON.',
      '',f'Completed artifacts audited: {len(records)}/32. Scientific failures retained; no missing rows silently dropped.',
      'Next: finish remaining Stage-1 batches; only then Stage-2 filtering/parent freeze.']
    out.write_text('\n'.join(lines)+'\n')
    (out.with_suffix('.json')).write_text(json.dumps({d['method']:{p:d[p].get('audited_metrics') for p in ['dev','transport_2025','stress_2026']} for d in records},indent=2)+'\n')
    print(json.dumps({'audited':len(records),'leader':valid[0]['method'] if valid else None,
      'leader_dev':valid[0]['dev']['metrics'] if valid else None}))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('out',type=Path)
    a=ap.parse_args();report(a.root,a.out)
