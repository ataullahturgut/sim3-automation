"""DEV-only filtering; refuses incomplete Stage 1. No external metric access."""
import argparse,hashlib,json,itertools
from pathlib import Path
import numpy as np
import vw_midas_elmfis_baseline_v1 as metrics
from vw_midas_rbfnn_stage1_v1 import BATCHES

def run(root,baseline,out):
    models={};decisions={};source_hashes={}
    for name in sum(BATCHES,[]):
        path=root/f'rbfnn_stage1_{name.lower()}_result.json'
        if not path.exists():raise RuntimeError('STAGE1_INCOMPLETE: '+name)
        d=json.loads(path.read_text()); assert d['status']=='COMPLETE'
        source_hashes[name]=hashlib.sha256(json.dumps(d['dev'],sort_keys=True).encode()).hexdigest()
        if d['dev']['scientific_gate']!='PASS':decisions[name]='REJECTED_SCIENTIFIC_FAILURE';continue
        models[name]=d['dev']['rows']
    for name,file in [('VANILLA','vw_midas_rbfnn_vanilla_v1_result.json'),('REGULARIZED','vw_midas_rbfnn_regularized_v1_result.json')]:
        d=json.loads((baseline/file).read_text());models[name]=d['dev']['rows']
        source_hashes[name]=hashlib.sha256(json.dumps(d['dev'],sort_keys=True).encode()).hexdigest()
    summaries={}; errors={};correct={};sign={}
    targets=None; actual=None; rw=None
    for name,rows in models.items():
        rows=sorted(rows,key=lambda r:r['target']);assert len(rows)==33
        ts=[r['target'] for r in rows];a=np.array([r['actual'] for r in rows]);w=np.array([r['rw'] for r in rows]);p=np.array([r['forecast'] for r in rows])
        if targets is None:targets,actual,rw=ts,a,w
        assert ts==targets and np.array_equal(a,actual) and np.array_equal(w,rw)
        errors[name]=p-a;sign[name]=np.sign(p-w);correct[name]=sign[name]==np.sign(a-w)
        yearly=metrics.yearly(rows);m=metrics.active_metrics(rows);ae=abs(errors[name])
        ds=[r.get('diag',r.get('rbfnn_diag',{})) for r in rows]
        repeat_spreads=[np.ptp([z['validation_loss'] for z in d['repeat_records'] if z['validation_loss'] is not None]) for d in ds if 'repeat_records' in d]
        summaries[name]={'metrics':m,'yearly':yearly,'worst_ae':float(ae.max()),'worst_month':rows[int(ae.argmax())]['target'],
          'max_year_relative_mae':max(z['relative_mae_vs_rw'] for z in yearly.values()),
          'loo_sum_ae':(ae.sum()-ae).tolist(),'median_repeat_validation_spread':float(np.median(repeat_spreads)) if repeat_spreads else None,
          'repeat_stability_note':'validation fitness spread; independent end-to-end repeat predictions NOT_PROVEN',
          'max_design_condition':max(d.get('design_condition',d.get('condition',d.get('design_condition_number',0))) for d in ds)}
    def dominates(a,b):
        x,y=summaries[a]['metrics'],summaries[b]['metrics']
        return x['sum_abs_error']<=y['sum_abs_error'] and x['direction_correct']>=y['direction_correct'] and (x['sum_abs_error']<y['sum_abs_error'] or x['direction_correct']>y['direction_correct'])
    pareto=[n for n in models if not any(dominates(o,n) for o in models if o!=n)]
    pairs={}
    for a,b in itertools.combinations(sorted(models),2):
        pairs[a+'|'+b]={'signed_error_correlation':float(np.corrcoef(errors[a],errors[b])[0,1]),
          'absolute_error_correlation':float(np.corrcoef(abs(errors[a]),abs(errors[b]))[0,1]),
          'direction_agreement':int(np.sum(sign[a]==sign[b])),
          'direction_disagreement':int(np.sum(sign[a]!=sign[b])),
          'b_rescues_a':int(np.sum(correct[b]&~correct[a])),
          'b_loses_a':int(np.sum(correct[a]&~correct[b])),
          'b_price_wins':int(np.sum(abs(errors[b])<abs(errors[a])))}
    retained=[]
    for n in sorted(models,key=lambda n:summaries[n]['metrics']['sum_abs_error']):
        if n=='VANILLA':decisions[n]='ARCHITECTURE_ANCHOR';retained.append(n);continue
        if summaries[n]['metrics']['relative_mae_vs_rw']>=1 and n not in pareto:
            decisions[n]='REJECTED_DEV_RW_GATE';continue
        redundant=next((o for o in retained if dominates(o,n) and np.corrcoef(errors[o],errors[n])[0,1]>.995),None)
        if redundant:decisions[n]='REDUNDANT_WITH_'+redundant
        else:decisions[n]='RETAINED_DEV_BENCHMARK';retained.append(n)
    candidates=[n for n in retained if n!='VANILLA']
    roles={'price_leader':min(candidates,key=lambda n:summaries[n]['metrics']['sum_abs_error']),
      'direction_leader':min(candidates,key=lambda n:(-summaries[n]['metrics']['direction_correct'],summaries[n]['metrics']['sum_abs_error'])),
      'stability_parent':min(candidates,key=lambda n:(summaries[n]['max_year_relative_mae'],summaries[n]['worst_ae'])),
      'architecture_anchor':'VANILLA'}
    # A named hybrid family can only open when its MPA parent is retained.
    hybrid_eligible=[]
    if 'MPA' in retained:
        roles['optimizer_hybrid_parent']='MPA'
        for n in ['SCA','GA','CPA']:
            if n not in retained:continue
            corr=float(np.corrcoef(errors['MPA'],errors[n])[0,1])
            rescue=int(np.sum(correct[n]&~correct['MPA']));loss=int(np.sum(correct['MPA']&~correct[n]))
            wins=int(np.sum(abs(errors[n])<abs(errors['MPA'])))
            if corr<.90 and rescue>=2 and loss>=2 and 8<=wins<=25:
                hybrid_eligible.append((corr,summaries[n]['metrics']['sum_abs_error'],n))
        if hybrid_eligible:roles['hybrid_complement']=min(hybrid_eligible)[2]
    parents=list(dict.fromkeys(roles.values()))
    data={'status':'FROZEN_BEFORE_STAGE3','authority':'DEV_ONLY_2022-04..2024-12',
      'source_dev_hashes':source_hashes,'summary':summaries,'pairwise':pairs,'decisions':decisions,
      'pareto':pareto,'retained':retained,'roles':roles,'parents':parents,
      'parent_policy':'price; max-direction then price; minimum worst-year RW-relative MAE; optional retained MPA; Vanilla anchor',
      'redundancy_policy':'signed error correlation >.995 and Pareto dominated',
      'hybrid_opening_policy':'at most one of MPA+SCA/GA/CPA; both retained, correlation<.90, bidirectional direction rescues>=2, each price wins>=8; minimum correlation then price tie-break',
      'hybrid_eligible':hybrid_eligible,
      'external_metrics_used':False}
    out.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'roles':roles,'pareto':pareto,'retained_count':len(retained)}))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('baseline',type=Path);ap.add_argument('out',type=Path)
    a=ap.parse_args();run(a.root,a.baseline,a.out)
