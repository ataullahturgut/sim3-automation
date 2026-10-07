from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, balanced_accuracy_score, recall_score, confusion_matrix

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

RFR=AX/"GOLD_EXECUTION_RFR_NOMACRO_ROWS_2026-10-07.csv"
PATH_DEV=AX/"GOLD_SESSION_IRIS_HOURLY_RAW_REPLAY_V1_PREDICTIONS_2023_2024.csv"
PATH_25=AX/"GOLD_SESSION_STAGE1_GLOBAL_CONTROLS_2025_V2_CONTINUOUS_PREDICTIONS_2026-10-07.csv"
STRUCT_DEV=AX/"GOLD_SESSION_STRUCTURAL_IRIS_S14_V2_WARMUP2022_PREDICTIONS_2026-10-07.csv"
STRUCT_25=AX/"GOLD_SESSION_S14_FROZEN_2025_TRANSPORT_PREDICTIONS_2026-10-07.csv"

OUTR=AX/"GOLD_OVERNIGHT_RFR_RESCUE_GATE_RESULT_2026-10-07.md"
OUTJ=AX/"GOLD_OVERNIGHT_RFR_RESCUE_GATE_SUMMARY_2026-10-07.json"
OUTM=AX/"GOLD_OVERNIGHT_RFR_RESCUE_GATE_METRICS_2026-10-07.csv"
OUTC=AX/"GOLD_OVERNIGHT_RFR_RESCUE_GATE_COMMON_ROWS_2026-10-07.csv"

TARGET_WINDOWS=[
    ("WGC_2026_NY3","US"),
    ("SOBTI_5_ET","NY_LONDON_LIT"),
]
GATES=[
    "G0_PAIR_RFR_DISAGREE",
    "G1_ANY_FAMILY_CONFIRMS_RFR",
    "G2_BOTH_FAMILIES_CONFIRM_RFR",
    "G3_FAMILIES_SPLIT",
    "G4_SPLIT_ONE_CONFIRMS_RFR",
    "G5_BOTH_FAMILIES_OPPOSE_RFR",
]
MIN_YEAR_N=12

def read_pred(path, family, yearset, model=None):
    q=pd.read_csv(path,low_memory=False)
    q["label_date"]=pd.to_datetime(q["label_date"]).dt.normalize()
    q["start_utc"]=pd.to_datetime(q["start_utc"],utc=True,errors="coerce")
    if model is not None:
        q=q[q["model"].eq(model)].copy()
    q=q[q["year"].astype(int).isin(yearset)].copy()
    q=q[q.apply(lambda r:(r["partition"],r["window"]) in TARGET_WINDOWS,axis=1)].copy()
    # 17:00 Europe/Istanbul = 14:00 UTC fixed. Only origin-available predictions are legal.
    q=q[q["start_utc"].dt.hour*60+q["start_utc"].dt.minute <= 14*60].copy()
    q["p_up"]=pd.to_numeric(q["p_up"],errors="coerce")
    q=q.dropna(subset=["p_up"])
    q["head"]=q["partition"].astype(str)+"__"+q["window"].astype(str)
    # Enforce one row per family/date/head.
    if q.duplicated(["label_date","head"]).any():
        raise RuntimeError(f"DUPLICATE_{family}")
    return q[["label_date","year","head","p_up"]].copy()

def family_table(dev_path, p25_path, family, model25=None, model_dev=None):
    a=read_pred(dev_path,family,{2023,2024},model_dev)
    b=read_pred(p25_path,family,{2025},model25)
    q=pd.concat([a,b],ignore_index=True)
    piv=q.pivot(index=["label_date","year"],columns="head",values="p_up").reset_index()
    required=[f"{p}__{w}" for p,w in TARGET_WINDOWS]
    for c in required:
        if c not in piv.columns:
            raise RuntimeError(f"MISSING_HEAD_{family}_{c}")
    piv=piv.dropna(subset=required).copy()
    piv[f"{family.lower()}_p"]=piv[required].mean(axis=1)
    piv[f"{family.lower()}_dir"]=(piv[f"{family.lower()}_p"]>=0.5).astype(int)
    piv[f"{family.lower()}_wgc_p"]=piv[required[0]]
    piv[f"{family.lower()}_nyl_p"]=piv[required[1]]
    return piv[["label_date","year",f"{family.lower()}_p",f"{family.lower()}_dir",f"{family.lower()}_wgc_p",f"{family.lower()}_nyl_p"]]

def metric(g):
    if len(g)==0:
        return {"n":0,"accuracy":None,"ba":None,"up_recall":None,"down_recall":None,
                "pair_accuracy":None,"pair_ba":None,"rescue":0,"break":0,"net_rescue":0}
    y=g["y"].astype(int).to_numpy()
    r=g["rule_pred"].astype(int).to_numpy()
    p=g["pair_pred"].astype(int).to_numpy()
    acc=float(accuracy_score(y,r))
    ba=float(balanced_accuracy_score(y,r)) if len(np.unique(y))==2 else None
    pacc=float(accuracy_score(y,p))
    pba=float(balanced_accuracy_score(y,p)) if len(np.unique(y))==2 else None
    ur=float(recall_score(y,r,pos_label=1,zero_division=0))
    dr=float(recall_score(y,r,pos_label=0,zero_division=0))
    rc=r==y; pc=p==y
    rescue=int((~pc & rc).sum()); brk=int((pc & ~rc).sum())
    return {"n":int(len(g)),"accuracy":acc,"ba":ba,"up_recall":ur,"down_recall":dr,
            "pair_accuracy":pacc,"pair_ba":pba,"rescue":rescue,"break":brk,"net_rescue":rescue-brk}

def gate_mask(q,name):
    rfr=q["rule_pred"].astype(int)
    pair=q["pair_pred"].astype(int)
    pd=q["path_dir"].astype(int)
    sd=q["struct_dir"].astype(int)
    base=pair.ne(rfr)
    if name=="G0_PAIR_RFR_DISAGREE": return base
    if name=="G1_ANY_FAMILY_CONFIRMS_RFR": return base & (pd.eq(rfr)|sd.eq(rfr))
    if name=="G2_BOTH_FAMILIES_CONFIRM_RFR": return base & pd.eq(rfr)&sd.eq(rfr)
    if name=="G3_FAMILIES_SPLIT": return base & pd.ne(sd)
    if name=="G4_SPLIT_ONE_CONFIRMS_RFR": return base & pd.ne(sd) & (pd.eq(rfr)|sd.eq(rfr))
    if name=="G5_BOTH_FAMILIES_OPPOSE_RFR": return base & pd.ne(rfr)&sd.ne(rfr)
    raise KeyError(name)

def main():
    r=pd.read_csv(RFR,parse_dates=["date"])
    r=r[r["eligible_nomacro"].astype(str).str.lower().eq("true")].copy()
    r["year"]=r["year"].astype(int)
    r["label_date"]=r["date"].dt.normalize()

    path=family_table(PATH_DEV,PATH_25,"PATH",model25="PATH_GLOBAL_1H",model_dev=None)
    struct=family_table(STRUCT_DEV,STRUCT_25,"STRUCT",model25="S14_A1_PLUS_1H_FULL",model_dev="S14_A1_PLUS_1H_FULL")

    q=r.merge(path,on=["label_date","year"],how="inner",validate="one_to_one")
    q=q.merge(struct,on=["label_date","year"],how="inner",validate="one_to_one")
    if q.empty: raise RuntimeError("NO_COMMON_ROWS")
    q["path_confirms_rfr"]=q["path_dir"].astype(int).eq(q["rule_pred"].astype(int))
    q["struct_confirms_rfr"]=q["struct_dir"].astype(int).eq(q["rule_pred"].astype(int))
    q["families_split"]=q["path_dir"].astype(int).ne(q["struct_dir"].astype(int))

    metrics=[]
    gate_rows={}
    for gate in GATES:
        gm=gate_mask(q,gate)
        gate_rows[gate]=q[gm].copy()
        for year in [2023,2024,2025]:
            gy=q[gm & q["year"].eq(year)].copy()
            z=metric(gy)
            metrics.append({"gate":gate,"period":str(year),**z})
        gd=q[gm & q["year"].isin([2023,2024])].copy()
        z=metric(gd)
        metrics.append({"gate":gate,"period":"DEV",**z})

    m=pd.DataFrame(metrics)

    ranking=[]
    for gate in GATES:
        y3=m[(m.gate==gate)&(m.period=="2023")].iloc[0]
        y4=m[(m.gate==gate)&(m.period=="2024")].iloc[0]
        dev=m[(m.gate==gate)&(m.period=="DEV")].iloc[0]
        eligible=bool(
            int(y3.n)>=MIN_YEAR_N and int(y4.n)>=MIN_YEAR_N
            and y3.accuracy is not None and y4.accuracy is not None
            and float(y3.accuracy)>0.5 and float(y4.accuracy)>0.5
            and int(y3.net_rescue)>0 and int(y4.net_rescue)>0
            and pd.notna(y3.ba) and pd.notna(y4.ba)
        )
        minba=min(float(y3.ba),float(y4.ba)) if eligible else -1.0
        ranking.append({
            "gate":gate,"eligible":eligible,"min_year_ba":minba,
            "dev_ba":None if pd.isna(dev.ba) else float(dev.ba),
            "dev_n":int(dev.n),
            "n_2023":int(y3.n),"n_2024":int(y4.n),
            "net_2023":int(y3.net_rescue),"net_2024":int(y4.net_rescue),
        })
    ranking=sorted(ranking,key=lambda z:(z["min_year_ba"],-1 if z["dev_ba"] is None else z["dev_ba"],z["dev_n"]),reverse=True)
    selected=ranking[0] if ranking and ranking[0]["eligible"] else None

    summary={
        "status":"COMPLETE",
        "target":"17:00 -> next eligible 09:00 Europe/Istanbul",
        "common_row_n_by_year":{str(y):int((q.year==y).sum()) for y in [2023,2024,2025]},
        "causality":"All PATH/STRUCTURAL heads have start_utc <= 14:00 UTC (=17:00 Europe/Istanbul).",
        "path_family":"mean p_up of canonical PATH_GLOBAL WGC-US and Sobti NY/London heads",
        "struct_family":"mean p_up of canonical S14_A1_PLUS_1H_FULL WGC-US and Sobti NY/London heads",
        "selection_uses_2025":False,
        "selection_rule":"Both 2023 and 2024 require N>=12, RFR accuracy>50%, net rescue>0; rank by minimum yearly BA, then DEV BA, then DEV N.",
        "ranking":ranking,
        "selected_gate":None if selected is None else selected["gate"],
    }

    # Transport details for selected gate only after development selection.
    if selected is not None:
        gate=selected["gate"]
        for per in ["2023","2024","DEV","2025"]:
            z=m[(m.gate==gate)&(m.period==per)].iloc[0].to_dict()
            summary.setdefault("selected_metrics",{})[per]={k:(None if pd.isna(v) else (int(v) if k in ["n","rescue","break","net_rescue"] else float(v))) for k,v in z.items() if k not in ["gate","period"]}
        gate_rows[gate].to_csv(OUTC,index=False)
    else:
        q.head(0).to_csv(OUTC,index=False)

    m.to_csv(OUTM,index=False)
    OUTJ.write_text(json.dumps(summary,indent=2)+"\n")

    def pct(x):
        return "NA" if x is None or pd.isna(x) else f"{100*float(x):.2f}%"
    lines=[
        "# GOLD OVERNIGHT RFR RESCUE-GATE RESULT — 2026-10-07","",
        "**Status:** COMPLETE / DEVELOPMENT-ONLY RESCUE-GATE AUDIT","",
        "2025 did not participate in gate selection.","",
        f"Common origin-safe expert rows: 2023={summary['common_row_n_by_year']['2023']}, 2024={summary['common_row_n_by_year']['2024']}, 2025={summary['common_row_n_by_year']['2025']}.","",
        "| Gate | 2023 N | 2023 RFR BA | Net | 2024 N | 2024 RFR BA | Net | DEV BA | 2025 N | 2025 RFR BA | 2025 Net |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"
    ]
    for gate in GATES:
        y3=m[(m.gate==gate)&(m.period=="2023")].iloc[0]
        y4=m[(m.gate==gate)&(m.period=="2024")].iloc[0]
        dv=m[(m.gate==gate)&(m.period=="DEV")].iloc[0]
        y5=m[(m.gate==gate)&(m.period=="2025")].iloc[0]
        lines.append(f"| {gate} | {int(y3.n)} | {pct(y3.ba)} | {int(y3.net_rescue):+d} | {int(y4.n)} | {pct(y4.ba)} | {int(y4.net_rescue):+d} | {pct(dv.ba)} | {int(y5.n)} | {pct(y5.ba)} | {int(y5.net_rescue):+d} |")
    lines += [""]
    if selected is None:
        lines += ["**No candidate rescue gate passed the preregistered cross-year development rule.**",
                  "Therefore no PATH/STRUCTURAL-assisted RFR override is authorized from this experiment."]
    else:
        gate=selected["gate"]; z5=m[(m.gate==gate)&(m.period=="2025")].iloc[0]
        zd=m[(m.gate==gate)&(m.period=="DEV")].iloc[0]
        lines += [f"Development-selected gate: **{gate}**.",
                  f"DEV: N={int(zd.n)}, RFR accuracy={pct(zd.accuracy)}, BA={pct(zd.ba)}, rescue/break/net={int(zd.rescue)}/{int(zd['break'])}/{int(zd.net_rescue):+d}.",
                  f"2025 retrospective transport: N={int(z5.n)}, RFR accuracy={pct(z5.accuracy)}, BA={pct(z5.ba)}, rescue/break/net={int(z5.rescue)}/{int(z5['break'])}/{int(z5.net_rescue):+d}.",
                  "This remains a specialist override candidate, not a majority-vote consensus."]
    OUTR.write_text("\n".join(lines)+"\n")
    print(OUTR.read_text())
    print(json.dumps(summary,indent=2))

if __name__=="__main__":
    main()
