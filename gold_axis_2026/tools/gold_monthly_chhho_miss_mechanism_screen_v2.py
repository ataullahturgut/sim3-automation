from __future__ import annotations
import argparse, json, math
from pathlib import Path
import numpy as np, pandas as pd

import gold_monthly_chhho_alarm_audit_v3 as v3
import gold_monthly_chhho_efg_alarm_audit_v1 as efg

CAL_START,CAL_END='2010-01','2020-12'
HIGH_AE=63.06

def load(p): return json.loads(Path(p).read_text())

def combined_chhho(pre,ch,transport):
    rows=[]
    rows.extend(dict(r) for r in pre['rows'])
    for sec in ['dev','transport_2025','stress_2026']:
        rows.extend(dict(r) for r in ch[sec]['rows'])
    aug=[r for r in transport['rows_2026_jan_aug'] if r['target']=='2026-08']
    if len(aug)!=1: raise RuntimeError('AUG_ROW_MISSING')
    a=aug[0]
    rows.append({
        'target':'2026-08','origin':'2026-07','forecast':float(a['forecast']),
        'actual':float(a['actual']),'rw':float(a['rw']),
        'pred_log_return_gold':math.log(float(a['forecast'])/float(a['rw']))
    })
    out={}
    for r in rows:
        z=dict(r)
        if 'rw' not in z: z['rw']=None
        if 'pred_log_return_gold' not in z and z.get('rw'):
            z['pred_log_return_gold']=math.log(float(z['forecast'])/float(z['rw']))
        z['ae']=abs(float(z['forecast'])-float(z['actual']))
        z['high_ae']=bool(z['ae']>HIGH_AE)
        out[z['target']]=z
    return out

def thresholds_2010_2020(monthly,gvz,cotm):
    cal=monthly.loc[CAL_START:CAL_END]
    gc=gvz.loc[CAL_START:CAL_END]
    cc=cotm.loc[CAL_START:CAL_END]
    q=efg.q
    return {
      'rv_q95':q(cal.Gold_rv_ratio,.95),
      'gvz_max_q80':q(gc.gvz_max,.80),
      'gvz_max_q90':q(gc.gvz_max,.90),
      'gvz_ratio_q90':q(gc.gvz_ratio12,.90),
      'cftc_abs_mmnet_chg_q90':q(cc.mm_net_oi_chg1.abs(),.90),
      'cftc_abs_oi_pct_q90':q(cc.oi_pct1.abs(),.90),
      'cftc_oi_ratio_q10':q(cc.oi_ratio12,.10),
      'cftc_mmnet_low_q10':q(cc.mm_net_oi,.10),
      'cftc_mmnet_high_q90':q(cc.mm_net_oi,.90),
    }

def feature_table(monthly,gvz,cotm,th):
    idx=monthly.index.union(gvz.index).union(cotm.index).sort_values()
    f=monthly.reindex(idx).join(gvz,how='left').join(cotm.add_prefix('cftc_'),how='left')
    f['VOL_EXTREME']=f.Gold_rv_ratio>=th['rv_q95']
    f['GVZ_Q80']=f.gvz_max>=th['gvz_max_q80']
    f['GVZ_Q90']=f.gvz_max>=th['gvz_max_q90']
    f['GVZ_DYNAMIC']=f.gvz_ratio12>=th['gvz_ratio_q90']
    f['CFTC_SHIFT']=(f.cftc_mm_net_oi_chg1.abs()>=th['cftc_abs_mmnet_chg_q90']) | (f.cftc_oi_pct1.abs()>=th['cftc_abs_oi_pct_q90'])
    f['OI_COMPRESSION']=f.cftc_oi_ratio12<=th['cftc_oi_ratio_q10']
    f['POSITION_EXTREME']=(f.cftc_mm_net_oi<=th['cftc_mmnet_low_q10']) | (f.cftc_mm_net_oi>=th['cftc_mmnet_high_q90'])
    f['FLOW_2OF4']=(
        f.GVZ_Q80.astype(int)+f.CFTC_SHIFT.astype(int)+
        f.OI_COMPRESSION.astype(int)+f.POSITION_EXTREME.astype(int)
    )>=2
    return f

def score(rows,flag):
    ev=[r for r in rows if r[flag]]
    hits=[r for r in ev if r['high_ae']]
    fps=[r for r in ev if not r['high_ae']]
    allhi=[r for r in rows if r['high_ae']]
    unexp=[r for r in rows if r['unexplained_high_ae']]
    uh=[r for r in ev if r['unexplained_high_ae']]
    return {
        'events':len(ev),'high_error_hits':len(hits),'false_alarms':len(fps),
        'precision':None if not ev else len(hits)/len(ev),
        'all_high_error_recall':None if not allhi else len(hits)/len(allhi),
        'unexplained_hits':len(uh),
        'unexplained_recall':None if not unexp else len(uh)/len(unexp),
        'alarm_targets':[r['target'] for r in ev],
        'hit_targets':[r['target'] for r in hits],
        'unexplained_hit_targets':[r['target'] for r in uh],
    }

def period(rows,a,b): return [r for r in rows if a<=r['target']<=b]

def main():
    ap=argparse.ArgumentParser()
    for x in ['snapshot','public_bundle','chhho','transport','predev','external','output']:
        ap.add_argument('--'+x.replace('_','-'),required=True)
    a=ap.parse_args()
    snap=load(a.snapshot); pub=load(a.public_bundle); ch=load(a.chhho)
    transport=load(a.transport); pre=load(a.predev); external=load(a.external)

    # Canonical alarm state and macro authority.
    corrected,_,gold=v3.build_markets(snap,pub)
    macro=v3.build_macro(external)

    # Gold/GVZ/CFTC feature state.
    monthly=efg.build_market(snap['payload'],pub)
    gvz,gvzmeta=efg.download_gvz()
    cot,cotmeta=efg.download_cftc()
    cotm=efg.cftc_monthly_pit(cot,start='2010-01',end='2026-08')
    th=thresholds_2010_2020(monthly,gvz,cotm)
    f=feature_table(monthly,gvz,cotm,th)

    chmap=combined_chhho(pre,ch,transport)
    rows=[]
    for t in sorted(chmap):
        if not ('2021-11'<=t<='2026-08'): continue
        r=chmap[t]; o=r['origin']; pred=float(r['pred_log_return_gold'])
        st=v3.state_row(corrected,o); mac=macro(o); ab=v3.alarm_flags(st,pred,mac)
        x=f.loc[o]
        candidate={k:bool(x[k]) if pd.notna(x[k]) else False for k in
                   ['VOL_EXTREME','GVZ_Q80','GVZ_Q90','GVZ_DYNAMIC','CFTC_SHIFT','OI_COMPRESSION','POSITION_EXTREME','FLOW_2OF4']}
        E_FROZEN=bool(st['Gold_vs_ma12']>.20 and abs(pred-st['Gold_r1'])>.05)
        G_FROZEN=bool(st['Gold_r3']<=-.10)
        existing=bool(ab['A'] or ab['B'] or ab['C'] or ab['D'])
        high=bool(r['high_ae'])
        z={
            'target':t,'origin':o,'ae':float(r['ae']),'high_ae':high,
            'pred_log_return_gold':pred,
            'A':ab['A'],'B':ab['B'],'C':ab['C'],'D':ab['D'],
            'existing_ABCD':existing,
            'unexplained_high_ae':bool(high and not existing),
            'E_FROZEN':E_FROZEN,'G_FROZEN':G_FROZEN,
            'Gold_r1':st['Gold_r1'],'Gold_r3':st['Gold_r3'],'Gold_vs_ma12':st['Gold_vs_ma12'],
            'Gold_rv_ratio':None if pd.isna(x.Gold_rv_ratio) else float(x.Gold_rv_ratio),
            'gvz_max':None if pd.isna(x.gvz_max) else float(x.gvz_max),
            'gvz_ratio12':None if pd.isna(x.gvz_ratio12) else float(x.gvz_ratio12),
            'cftc_mm_net_oi':None if pd.isna(x.cftc_mm_net_oi) else float(x.cftc_mm_net_oi),
            'cftc_mm_net_oi_chg1':None if pd.isna(x.cftc_mm_net_oi_chg1) else float(x.cftc_mm_net_oi_chg1),
            'cftc_oi_pct1':None if pd.isna(x.cftc_oi_pct1) else float(x.cftc_oi_pct1),
            'cftc_oi_ratio12':None if pd.isna(x.cftc_oi_ratio12) else float(x.cftc_oi_ratio12),
            **candidate,
        }
        rows.append(z)

    flags=['CFTC_SHIFT','POSITION_EXTREME','OI_COMPRESSION','GVZ_Q80','GVZ_Q90','GVZ_DYNAMIC','VOL_EXTREME','FLOW_2OF4','E_FROZEN','G_FROZEN']
    periods={
        'PRE_DISCOVERY_MODEL':('2021-11','2024-12'),
        '2025':('2025-01','2025-12'),
        '2026_JAN_AUG':('2026-01','2026-08'),
        'ALL_USABLE':('2021-11','2026-08'),
    }
    scores={p:{fl:score(period(rows,*rng),fl) for fl in flags} for p,rng in periods.items()}

    unexpl=[r for r in rows if r['unexplained_high_ae']]
    unresolved=[]
    for r in unexpl:
        candidate_any=any(r[x] for x in flags)
        if not candidate_any: unresolved.append(r['target'])

    repeated={}
    pre=period(rows,'2021-11','2024-12'); later=period(rows,'2025-01','2026-08')
    for fl in flags:
        ph=[r['target'] for r in pre if r[fl] and r['unexplained_high_ae']]
        lh=[r['target'] for r in later if r[fl] and r['unexplained_high_ae']]
        repeated[fl]={'pre_discovery_unexplained_hits':ph,'later_unexplained_hits':lh,'repeated':bool(ph and lh)}

    out={
        'schema':'GOLD_MONTHLY_CHHHO_MISS_MECHANISM_SCREEN_V2_2026-09-30',
        'status':'COMPLETE',
        'calibration_period':f'{CAL_START}..{CAL_END}',
        'thresholds':th,
        'sources':{'gvz':gvzmeta,'cftc':cotmeta},
        'existing_alarm_definition':'A_OR_B_OR_C_OR_D_FOR_EXPLANATION_ONLY',
        'rows':rows,
        'unexplained_high_error_targets':[r['target'] for r in unexpl],
        'unexplained_rows':unexpl,
        'fixed_candidate_scores':scores,
        'repeated_mechanism_gate':repeated,
        'candidate_unresolved_targets':unresolved,
        'governance':{
            'H1_counterfactual_model_errors_excluded':True,
            'thresholds_calibrated_pre_2021':True,
            'threshold_retuning_on_2021_2026':False,
            'routing_tested':False,
            'candidate_flags_not_promoted_to_hard_alarm':True,
        }
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print('OUTPUT_GATE=PASS')
    print(json.dumps({
        'unexplained':out['unexplained_high_error_targets'],
        'unresolved':unresolved,
        'repeated':repeated,
        'pre_scores':scores['PRE_DISCOVERY_MODEL'],
        'later_scores':{
            '2025':scores['2025'],
            '2026':scores['2026_JAN_AUG'],
        },
        'unexplained_rows':[{k:r[k] for k in ['target','ae','A','B','C','D']+flags} for r in unexpl],
    },sort_keys=True))

if __name__=='__main__': main()
