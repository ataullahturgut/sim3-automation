"""Evaluation-only SESSION inventory. Never fits a model or combines forecasts."""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, log_loss, roc_auc_score

AX = Path(__file__).resolve().parents[1]
PRE = "GOLD_SESSION_WINDOW_EVIDENCE"
KEY = ["partition", "window", "start_utc"]
DATE = "2026-10-07"
LEDGER = AX / f"{PRE}_EVALUATION_LEDGER_{DATE}.csv.gz"
ARTIFACTS = {
    "01B": 11470124785, "02": 11470612138, "03B": 11472199349,
    "04B": 11473356018, "05B": 11473407627, "06B": 11473827316,
    "07B": 11473569980, "08B": 11473894951, "09B": 11474937494,
    "OPAL": 11477723785, "TURN": 11482156300,
    "PRISM": 11481753368, "TWIN": 11481709820,
    "RIFT": 11474619596, "VEGA": 11476795551,
}

def targets():
    q = pd.concat([pd.read_csv(AX / name) for name in [
        "GOLD_SESSION_TARGETS_WGC2026_NY3_FINAL_V5_2023_2025.csv",
        "GOLD_SESSION_TARGETS_SOBTI5_ET_FINAL_V5_2023_2025.csv"]])
    q = q[q.final_trainable.astype(str).str.lower().eq("true")].copy()
    q.start_utc = pd.to_datetime(q.start_utc, utc=True)
    q.end_utc = pd.to_datetime(q.end_utc, utc=True)
    q["year"] = q.start_utc.dt.year
    q["y_up"] = q.direction.eq("UP").astype(int)
    assert not q.duplicated(KEY).any()
    return q

def ingest(evidence):
    parts = []
    sources = []
    def add(q, name, pcol="p_up", kind="primary", family=None, source="", basecol=None, activecol=None):
        if q.empty:
            return
        q = q.copy()
        q.start_utc = pd.to_datetime(q.start_utc, utc=True)
        q["year"] = q.start_utc.dt.year
        assert q.year.isin([2023, 2024, 2025]).all()
        fields = KEY + ["year", "y_up"]
        z = q[fields].copy()
        z["p_up"] = q[pcol].astype(float)
        z["model"] = name
        z["family"] = family or name
        z["kind"] = kind
        z["source"] = source
        z["p_original_base"] = q[basecol].astype(float) if basecol else np.nan
        if activecol:
            z["active"] = q[activecol].astype(str).str.lower().isin(["true", "1"])
        elif basecol:
            z["active"] = (q[pcol].ge(.5) != q[basecol].ge(.5))
        else:
            z["active"] = False
        parts.append(z)
    def repo(name):
        return pd.read_csv(AX / name)
    def artifact(family, file):
        p = evidence / str(ARTIFACTS[family]) / file
        sources.append(dict(family=family, artifact_id=ARTIFACTS[family], filename=file,
            sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
        try:
            return pd.read_csv(p)
        except pd.errors.EmptyDataError:
            return pd.DataFrame()
    for model, file, pcol, family in [
        ("CORE3_A0", "GOLD_SESSION_NOVA_A0_CORE3_RAW_REPLAY_V1_PREDICTIONS_2023_2024.csv", "p_up", "CORE3"),
        ("NOVA_A1_ARCR", "GOLD_SESSION_NOVA_A1_ARCR_RAW_REPLAY_V1_PREDICTIONS_2023_2024.csv", "p_A1_arcr", "A1"),
        ("PATH_GLOBAL_1H", "GOLD_SESSION_IRIS_HOURLY_RAW_REPLAY_V1_PREDICTIONS_2023_2024.csv", "p_up", "PATH")]:
        add(repo(file), model, pcol, family=family, source=file)
    sfile = "GOLD_SESSION_STRUCTURAL_IRIS_S14_V2_WARMUP22_PREDICTIONS_2026-10-07.csv"
    s = repo(sfile)
    for model, name in [("S14_A1_PLUS_1H_FULL", "STRUCTURAL_IRIS_1H"), ("S14_A1_PLUS_15M_FULL", "STRUCTURAL_IRIS_15M")]:
        add(s[s.model.eq(model)], name, family="STRUCTURAL", source=sfile)
    sagefile = "GOLD_SESSION_SAGE_V2_STAGE1_CORRECTED_PREDICTIONS_2026-10-07.csv"
    sage = repo(sagefile)
    # 07/08 canonical variants below use their later identity-corrected producer.
    for model in ["S15_SESSION_ONLY", "S18_A1_PATH_SESSION"]:
        add(sage[sage.model.eq(model)], model, family=model.split("_")[0], source=sagefile)
    for fam, model, name in [
        ("01B", "SELECTED_CLASSICAL", "SELECTED_CLASSICAL"),
        ("03B", "SELECTED_A1_ARCR", "SELECTED_A1_ARCR"),
        ("04B", "SELECTED_PATH_GLOBAL", "SELECTED_PATH_GLOBAL"),
        ("05B", "S14_A1_PLUS_1H_SELECTED_BLOCK", "SELECTED_STRUCTURAL_IRIS_1H"),
        ("06B", "S15_SESSION_ONLY_SELECTED_BLOCK", "SELECTED_SESSION_ONLY"),
        ("07B", "CANONICAL_PATH_SESSION", "S16_PATH_SESSION"),
        ("08B", "CANONICAL_A1_SESSION", "S17_A1_SESSION")]:
        q = artifact(fam, "dev_predictions.csv")
        family = {"01B":"CORE3", "03B":"A1", "04B":"PATH", "05B":"STRUCTURAL",
                  "06B":"S15", "07B":"S16", "08B":"S17"}[fam]
        add(q[q.model.eq(model)], name, family=family, source=f"artifact:{ARTIFACTS[fam]}:dev_predictions.csv")
    repair = f"GOLD_SESSION_NESTED_ROLE_REPAIR_PREDICTIONS_{DATE}.csv"
    q = repo(repair)
    for name, family in [("NESTED_PATH_SESSION", "S16"), ("NESTED_A1_SESSION", "S17"), ("NESTED_A1_PATH_SESSION", "S18")]:
        add(q[q.model.eq(name)], name, family=family, source=repair)
    # CART keeps all preregistered development representations as negative controls.
    q = artifact("02", "dev_predictions.csv")
    for rep, g in q.groupby("representation"):
        add(g, "CART_" + rep, kind="negative_control", family="CART", source=f"artifact:{ARTIFACTS['02']}:dev_predictions.csv")
    transportfile = "GOLD_SESSION_STAGE1_GLOBAL_CONTROLS_2025_V2_CONTINUOUS_PREDICTIONS_2026-10-07.csv"
    q = repo(transportfile)
    for old, name, family in [("A0_CORE3", "CORE3_A0", "CORE3"), ("A1_ARCR", "NOVA_A1_ARCR", "A1"), ("PATH_GLOBAL_1H", "PATH_GLOBAL_1H", "PATH")]:
        add(q[q.model.eq(old)], name, family=family, source=transportfile)
    tfile = "GOLD_SESSION_S14_FROZEN_2025_TRANSPORT_PREDICTIONS_2026-10-07.csv"
    q = repo(tfile)
    for old, name in [("S14_A1_PLUS_1H_FULL", "STRUCTURAL_IRIS_1H"), ("S14_A1_PLUS_15M_FULL", "STRUCTURAL_IRIS_15M")]:
        add(q[q.model.eq(old)], name, family="STRUCTURAL", source=tfile)
    tfile = "GOLD_SESSION_SAGE_FROZEN_2025_TRANSPORT_V2_CONTINUOUS_PREDICTIONS_2026-10-07.csv"
    q = repo(tfile)
    for model in ["S15_SESSION_ONLY", "S16_PATH_SESSION"]:
        add(q[q.model.eq(model)], model, family=model.split("_")[0], source=tfile)
    for fam, old, name, family in [
        ("01B", "MODEL01B_FROZEN_FEATURES", "SELECTED_CLASSICAL", "CORE3"),
        ("03B", "SELECTED_A1_ARCR", "SELECTED_A1_ARCR", "A1"),
        ("04B", "SELECTED_PATH_GLOBAL", "SELECTED_PATH_GLOBAL", "PATH"),
        ("05B", "S14_A1_PLUS_1H_SELECTED", "SELECTED_STRUCTURAL_IRIS_1H", "STRUCTURAL"),
        ("06B", "S15_SESSION_ONLY_SELECTED_BLOCK", "SELECTED_SESSION_ONLY", "S15"),
        ("07B", "SELECTED_PATH_SESSION", "FROZEN_PATH_SESSION", "S16"),
        ("08B", "CANONICAL_A1_SESSION", "S17_A1_SESSION", "S17"),
        ("08B", "SELECTED_A1_SESSION", "FROZEN_A1_SESSION", "S17"),
        ("09B", "SELECTED_A1_PATH_SESSION", "FROZEN_A1_PATH_SESSION", "S18")]:
        q = artifact(fam, "transport_2025_predictions.csv")
        if not q.empty:
            add(q[q.model.eq(old)], name, family=family, source=f"artifact:{ARTIFACTS[fam]}:transport_2025_predictions.csv")
    q = artifact("02", "transport_2025_predictions.csv")
    add(q, "CART_FROZEN", kind="negative_control", family="CART", source=f"artifact:{ARTIFACTS['02']}:transport_2025_predictions.csv")
    # Specialists keep their original intervention conditions and baselines.
    for fam in ["OPAL", "TURN", "PRISM", "TWIN"]:
        for file in ["dev_predictions.csv", "transport_2025_predictions.csv"]:
            q = artifact(fam, file)
            if q.empty:
                continue
            if fam == "PRISM":
                # Keep each latent regularization identity visible; transport
                # contains only originally eligible lambda/window pairs.
                for lam, g in q.groupby("lambda"):
                    add(g, f"PRISM_L{int(lam)}", "p_prism", "specialist", fam,
                        f"artifact:{ARTIFACTS[fam]}:{file}", "p_aurora")
            elif fam == "TWIN":
                for rep, g in q.groupby("rep"):
                    add(g, "TWIN_" + rep, "p_twin", "specialist", fam,
                        f"artifact:{ARTIFACTS[fam]}:{file}", "p_aurora", "override")
            else:
                add(q, fam, "p_" + fam.lower(), "specialist", fam,
                    f"artifact:{ARTIFACTS[fam]}:{file}", "p_aurora", "override")
    # Reconstruct only the historical evaluation rule against archived base
    # evidence; these records are never inputs to a new predictive model.
    primary_long = pd.concat(parts, ignore_index=True)
    for fam in ["RIFT", "VEGA"]:
        source = f"GOLD_SESSION_{fam}_V1_PREDICTIONS_2026-10-07.csv"
        rev = repo(source); rev.start_utc = pd.to_datetime(rev.start_utc, utc=True)
        for base_name in ["CORE3_A0", "NOVA_A1_ARCR", "PATH_GLOBAL_1H", "STRUCTURAL_IRIS_1H"]:
            bg=primary_long[primary_long.model.eq(base_name)&primary_long.year.isin([2023,2024])]
            z=bg.merge(rev[KEY+["momentum_up","p_reversal"]],on=KEY,validate="one_to_one")
            z["override"]=z.p_up.ge(.5).eq(z.momentum_up.astype(bool))&z.p_reversal.ge(.70)
            z["p_corrected"]=z.p_up
            z.loc[z.override,"p_corrected"]=np.where(z.loc[z.override,"momentum_up"].eq(1),
                1-z.loc[z.override,"p_reversal"],z.loc[z.override,"p_reversal"])
            add(z,f"{fam}_ON_{base_name}","p_corrected","specialist",fam,source,"p_up","override")
        z=artifact(fam,"matched_predictions.csv")
        if fam=="RIFT":
            z=z[z.rift_variant.eq("FULL_RIFT_V1")]
            for base_name,g in z.groupby("baseline"):
                mapped={"A0_CORE3":"CORE3_A0","A1_ARCR":"NOVA_A1_ARCR",
                    "STRUCTURAL_IRIS_A1_PLUS_1H":"STRUCTURAL_IRIS_1H"}.get(base_name,base_name)
                add(g,f"RIFT_ON_{mapped}","p_corrected","specialist",fam,
                    f"artifact:{ARTIFACTS[fam]}:matched_predictions.csv","p_up","override")
        else:
            z["override"]=z.p_up.ge(.5).eq(z.momentum_up.astype(bool))&z.p_reversal.ge(.70)
            add(z,"VEGA_ON_PATH_GLOBAL_1H","p_corrected","specialist",fam,
                f"artifact:{ARTIFACTS[fam]}:matched_predictions.csv","p_up","override")
    long = pd.concat(parts, ignore_index=True)
    assert not long.duplicated(KEY + ["model"]).any(), "DUPLICATE_MODEL_TARGET"
    long.to_csv(LEDGER, index=False, compression={"method":"gzip", "mtime":0})
    files=set(long.source[~long.source.str.startswith("artifact:")])
    files.update(["GOLD_SESSION_TARGETS_WGC2026_NY3_FINAL_V5_2023_2025.csv","GOLD_SESSION_TARGETS_SOBTI5_ET_FINAL_V5_2023_2025.csv","GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"])
    for name in sorted(files):
        sources.append(dict(source="repository",filename=name,sha256=hashlib.sha256((AX/name).read_bytes()).hexdigest(),initial_branch_head="d24a6a7576e2c62a9fb17e5a59009e1287a67943" if "NESTED_ROLE_REPAIR" not in name else "new_successor_output"))
    (AX / f"{PRE}_ARTIFACT_PROVENANCE_{DATE}.json").write_text(json.dumps(sources, indent=2) + "\n")

def score(g, target_n=None, probability="p_up"):
    y = g.y_up.to_numpy(int)
    p = g[probability].to_numpy(float)
    d = p >= .5
    tn, fp, fn, tp = confusion_matrix(y, d, labels=[0, 1]).ravel()
    up = tp / (tp + fn) if tp + fn else np.nan
    down = tn / (tn + fp) if tn + fp else np.nan
    ba = (up + down) / 2
    # Descriptive normal interval; does not correct search multiplicity or dependence.
    se = .5 * np.sqrt(up * (1 - up) / max(1, tp+fn) + down * (1-down) / max(1, tn+fp))
    bins = np.minimum((p * 10).astype(int), 9)
    ece = sum(np.mean(bins == b) * abs(np.mean(p[bins == b]) - np.mean(y[bins == b])) for b in np.unique(bins))
    up_precision = tp / (tp + fp) if tp + fp else np.nan
    down_precision = tn / (tn + fn) if tn + fn else np.nan
    return dict(n=len(g), eligible_n=target_n, coverage=len(g)/target_n if target_n else np.nan,
        accuracy=float(np.mean(d == y)), balanced_accuracy=ba,
        ba_lower95=max(0,ba-1.96*se), ba_upper95=min(1,ba+1.96*se),
        up_recall=up, down_recall=down, up_precision=up_precision, down_precision=down_precision,
        up_prevalence=float(np.mean(y)), predicted_up_rate=float(np.mean(d)),
        brier=float(np.mean((p-y)**2)), prevalence_brier=float(np.mean((y-y.mean())**2)),
        logloss=float(log_loss(y,np.clip(p,1e-12,1-1e-12),labels=[0,1])),
        auc=float(roc_auc_score(y,p)) if len(np.unique(y)) == 2 else np.nan,
        ece10=ece, probability_bias=float(np.mean(p-y)), tn=int(tn),fp=int(fp),fn=int(fn),tp=int(tp))

def compare(z):
    z=z.rename(columns={"p_up_a":"p_a","p_up_b":"p_b"});y=z.y_up.to_numpy(int);a=z.p_a.ge(.5).to_numpy();b=z.p_b.ge(.5).to_numpy()
    ea=a!=y;eb=b!=y;dis=a!=b;res=ea&~eb;broken=~ea&eb
    corr = np.corrcoef(ea.astype(float),eb.astype(float))[0,1] if np.std(ea) and np.std(eb) else np.nan
    pcorr = np.corrcoef(z.p_a,z.p_b)[0,1] if len(z)>1 and z.p_a.std()>0 and z.p_b.std()>0 else np.nan
    ma=score(z,probability="p_a");mb=score(z,probability="p_b")
    return dict(a_ba=ma["balanced_accuracy"],b_ba=mb["balanced_accuracy"],delta_ba=mb["balanced_accuracy"]-ma["balanced_accuracy"],a_brier=ma["brier"],b_brier=mb["brier"],common_n=len(z),disagreement_n=int(dis.sum()),rescues=int(res.sum()),breaks=int(broken.sum()),
        net_rescue=int(res.sum()-broken.sum()),win_on_disagreement=float(res.sum()/dis.sum()) if dis.sum() else np.nan,
        agreement_rate=float(np.mean(~dis)),error_corr=corr,probability_corr=pcorr,
        double_fault_rate=float(np.mean(ea&eb)),a_wrong_b_right_rate=float(np.mean(res)),
        up_rescues=int((res&(y==1)).sum()),down_rescues=int((res&(y==0)).sum()),
        up_breaks=int((broken&(y==1)).sum()),down_breaks=int((broken&(y==0)).sum()))

def evaluate():
    long=pd.read_csv(LEDGER);long.start_utc=pd.to_datetime(long.start_utc,utc=True)
    t=targets()
    # Joining without outcome in key makes a wrong target label a hard failure.
    joined=long.merge(t[KEY+["y_up","end_utc"]],on=KEY,validate="many_to_one",suffixes=("","_v5"),how="left")
    assert joined.end_utc.notna().all() and joined.y_up.eq(joined.y_up_v5).all(), "V5_LABEL_IDENTITY_FAIL"
    assert np.isfinite(long.p_up).all() and long.p_up.between(0,1).all()
    metrics=[];cal=[]
    for (model,kind,fam,part,win),g in long.groupby(["model","kind","family","partition","window"]):
        for period,gg in [("DEV",g[g.year.isin([2023,2024])])]+[(str(y),g[g.year.eq(y)]) for y in [2023,2024,2025]]:
            if gg.empty:continue
            tt=t[t.partition.eq(part)&t.window.eq(win)&t.year.isin([2023,2024] if period=="DEV" else [int(period)])]
            met=score(gg,len(tt))
            metrics.append(dict(model=model,kind=kind,family=fam,partition=part,window=win,period=period,**met))
            bins=np.minimum((gg.p_up.to_numpy()*10).astype(int),9)
            for b in np.unique(bins):
                q=gg.iloc[np.flatnonzero(bins==b)]
                cal.append(dict(model=model,partition=part,window=win,period=period,bin=int(b),n=len(q),
                    mean_probability=q.p_up.mean(),observed_up_rate=q.y_up.mean()))
    met=pd.DataFrame(metrics);met.to_csv(AX/f"{PRE}_METRICS_{DATE}.csv",index=False)
    pd.DataFrame(cal).to_csv(AX/f"{PRE}_CALIBRATION_{DATE}.csv",index=False)
    dev=met[met.period.eq("DEV")&met.kind.eq("primary")]
    roles=[]
    for (part,win),g in dev.groupby(["partition","window"]):
        eligible=g[g.n.ge(80)&g.up_recall.ge(.30)&g.down_recall.ge(.30)]
        best=eligible.sort_values(["balanced_accuracy","brier","n"],ascending=[False,True,False]).iloc[0]
        up=g[g.n.ge(80)].sort_values(["up_recall","up_precision"],ascending=False).iloc[0]
        down=g[g.n.ge(80)].sort_values(["down_recall","down_precision"],ascending=False).iloc[0]
        ymet=met[met.model.eq(best.model)&met.partition.eq(part)&met.window.eq(win)&met.period.isin(["2023","2024"])]
        stable=(len(ymet)==2 and ymet.n.ge(80).all() and ymet.balanced_accuracy.gt(.5).all()
                and ymet.up_recall.ge(.30).all() and ymet.down_recall.ge(.30).all())
        # N=80/class floor inherited safety rules; year replication is a
        # descriptive flag, not a new transport eligibility or membership gate.
        roles.append(dict(partition=part,window=win,balanced_primary=best.model,dev_n=int(best.n),
            dev_ba=best.balanced_accuracy,dev_coverage=best.coverage,
            up_profile=up.model,up_recall=up.up_recall,up_precision=up.up_precision,
            down_profile=down.model,down_recall=down.down_recall,down_precision=down.down_precision,
            replicated_two_year_edge=bool(stable),
            verdict="PRIMARY_CANDIDATE_UNVALIDATED" if stable else "NO_ROBUST_EDGE_ESTABLISHED"))
    roles=pd.DataFrame(roles);roles.to_csv(AX/f"{PRE}_ROLE_MATRIX_{DATE}.csv",index=False)
    replicated=[]
    for (part,win,model),gg in met[met.kind.eq("primary")&met.period.isin(["2023","2024"])].groupby(["partition","window","model"]):
        if len(gg)==2 and gg.n.ge(80).all() and gg.balanced_accuracy.gt(.5).all() and gg.up_recall.ge(.30).all() and gg.down_recall.ge(.30).all():
            allg=met[(met.partition==part)&(met.window==win)&(met.model==model)].set_index("period")
            values={}
            for year in ["2023","2024","2025"]:
                values["year_"+year]=(f"{100*allg.loc[year,'balanced_accuracy']:.2f} / {allg.loc[year,'n']}" if year in allg.index else "NO SAME-POLICY TEST")
            replicated.append(dict(partition=part,window=win,model=model,**values))
    pd.DataFrame(replicated).to_csv(AX/f"{PRE}_YEAR_REPLICATION_CANDIDATES_{DATE}.csv",index=False)
    repair=pd.read_csv(AX/f"GOLD_SESSION_NESTED_ROLE_REPAIR_PREDICTIONS_{DATE}.csv")
    timing=pd.read_csv(AX/f"GOLD_SESSION_NESTED_ROLE_REPAIR_TIMING_{DATE}.csv")
    assert pd.to_datetime(timing.max_train_end,utc=True).le(pd.to_datetime(timing.cutoff,utc=True)).all()
    assert pd.to_datetime(timing.max_train_start,utc=True).lt(pd.to_datetime(timing.cutoff,utc=True)).all()
    assert set(repair.year)=={2023,2024}
    assert pd.to_datetime(repair.selection_cutoff,utc=True).le(pd.to_datetime(repair.start_utc,utc=True)).all()
    paired=[]
    for (part,win),gg in repair.groupby(["partition","window"]):
        for model,base in [("NESTED_PATH_SESSION","NESTED_PATH_MATCHED"),("NESTED_A1_SESSION","DIRECT_A1"),("NESTED_A1_PATH_SESSION","NESTED_A1_PATH_MATCHED")]:
            aa=gg[gg.model.eq(base)];bb=gg[gg.model.eq(model)]
            zz=aa[KEY+["year","y_up","p_up"]].merge(bb[KEY+["p_up"]],on=KEY,validate="one_to_one",suffixes=("_a","_b"))
            for period,z in [("DEV",zz)]+[(str(y),zz[zz.year.eq(y)]) for y in [2023,2024]]:
                if len(z):paired.append(dict(partition=part,window=win,model=model,base=base,period=period,**compare(z)))
    pd.DataFrame(paired).to_csv(AX/f"GOLD_SESSION_NESTED_ROLE_REPAIR_PAIRED_METRICS_{DATE}.csv",index=False)

    pairs=[];special=[]
    for (part,win),g in long[long.year.isin([2023,2024])&long.kind.eq("primary")].groupby(["partition","window"]):
        for a,b in itertools.combinations(sorted(g.model.unique()),2):
            aa=g[g.model.eq(a)];bb=g[g.model.eq(b)]
            z=aa[KEY+["year","y_up","p_up"]].merge(bb[KEY+["p_up"]],on=KEY,validate="one_to_one",suffixes=("_a","_b"))
            for period,zz in [("DEV",z)]+[(str(y),z[z.year.eq(y)]) for y in [2023,2024]]:
                if zz.empty:continue
                pairs.append(dict(partition=part,window=win,model_a=a,model_b=b,period=period,
                    same_family=aa.family.iloc[0]==bb.family.iloc[0],**compare(zz)))
    for (part,win,model),g in long[long.kind.eq("specialist")].groupby(["partition","window","model"]):
        for period,gg in [("DEV",g[g.year.isin([2023,2024])])]+[(str(y),g[g.year.eq(y)]) for y in [2023,2024,2025]]:
            if gg.empty:continue
            z=gg.rename(columns={"p_original_base":"p_a","p_up":"p_b"})
            special.append(dict(partition=part,window=win,specialist=model,period=period,
                comparator=(model.split("_ON_",1)[1] if "_ON_" in model else "ORIGINAL_AURORA"),
                eligible_n=len(z),active_n=int(z.active.sum()),**compare(z)))
            # Evaluation of frozen interventions against development-chosen
            # reference only. No new corrected/combined prediction is emitted.
            base=roles[(roles.partition==part)&(roles.window==win)].iloc[0].balanced_primary
            bg=long[(long.partition==part)&(long.window==win)&(long.model==base)]
            active=gg[gg.active.astype(str).str.lower().isin(["true","1"])]
            zz=active[KEY+["year","y_up","p_up"]].merge(bg[KEY+["p_up"]],on=KEY,validate="one_to_one",suffixes=("_b","_a"))
            if not zz.empty:
                special.append(dict(partition=part,window=win,specialist=model,period=period,
                    comparator=base,eligible_n=len(gg),active_n=len(zz),**compare(zz)))
    pd.DataFrame(pairs).to_csv(AX/f"{PRE}_PAIRWISE_ERRORS_{DATE}.csv",index=False)
    pd.DataFrame(special).to_csv(AX/f"{PRE}_SPECIALIST_INTERVENTIONS_{DATE}.csv",index=False)
    # Failure mechanisms, descriptive only. Exact 12h pre-target path; never
    # condition on a realised target-window feature as if it were origin-known.
    raw=pd.read_csv(AX/"GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv")
    raw["available_at"]=pd.to_datetime(raw.dt_utc,utc=True)+pd.Timedelta(minutes=15)
    raw=raw.sort_values("available_at")
    rt=raw.available_at.astype("int64").to_numpy();lp=np.log(raw.close.to_numpy(float))
    diagnostics=[]
    for r in roles.itertuples(index=False):
        g=long[(long.partition==r.partition)&(long.window==r.window)&(long.model==r.balanced_primary)&long.year.isin([2023,2024])].copy()
        state=[]
        for q in g.itertuples(index=False):
            origin=q.start_utc.value;hi=np.searchsorted(rt,origin,side="left")-1
            lo=np.searchsorted(rt,origin-int(pd.Timedelta(hours=12).value),side="left")-1
            if lo<0 or hi<=lo or origin-rt[hi]>int(pd.Timedelta(minutes=60).value) or origin-int(pd.Timedelta(hours=12).value)-rt[lo]>int(pd.Timedelta(minutes=60).value):
                state.append((np.nan,np.nan));continue
            dr=np.diff(lp[lo:hi+1]);state.append((lp[hi]-lp[lo],float(np.sqrt(np.sum(dr*dr)))))
        g[["prior_return12","prior_rv12"]]=state
        g=g.dropna(subset=["prior_return12","prior_rv12"])
        # Freeze diagnostic high/low RV boundary on 2023 origins only.
        cutoff=g[g.year.eq(2023)].prior_rv12.median()
        subsets={"PRIOR_UP":g[g.prior_return12.gt(0)],"PRIOR_DOWN":g[g.prior_return12.lt(0)],
            "CONTINUATION_OUTCOME_ONLY":g[g.y_up.eq(g.prior_return12.gt(0).astype(int))],
            "REVERSAL_OUTCOME_ONLY":g[g.y_up.ne(g.prior_return12.gt(0).astype(int))]}
        if np.isfinite(cutoff):
            subsets.update({"RV_HIGH_2023_MEDIAN":g[g.prior_rv12.gt(cutoff)],"RV_LOW_2023_MEDIAN":g[g.prior_rv12.le(cutoff)]})
        for name,q in subsets.items():
            for period,zz in [("DEV",q)]+[(str(y),q[q.year.eq(y)]) for y in [2023,2024]]:
                if not zz.empty:
                    diagnostics.append(dict(partition=r.partition,window=r.window,model=r.balanced_primary,
                        subset=name,period=period,rv_threshold=cutoff,diagnostic_only=True,**score(zz)))
    pd.DataFrame(diagnostics).to_csv(AX/f"{PRE}_FAILURE_MECHANISMS_{DATE}.csv",index=False)
    summary=dict(status="WINDOW_EVIDENCE_AUDIT_COMPLETE",selection_years=[2023,2024],transport_only=[2025],
        no_2026=True,no_consensus=True,no_router=True,ledger_rows=len(long),metric_rows=len(met),
        target_identity="V5_SESSION",label_matches=len(joined),
        caution="Role ranks on native coverage are descriptive; pairwise comparisons use exact common rows. Highest recall is skew, not proved specialist edge.",
        roles=roles.to_dict("records"),
        ledger_sha256=hashlib.sha256(LEDGER.read_bytes()).hexdigest())
    (AX/f"{PRE}_SUMMARY_{DATE}.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(roles.to_string(index=False))

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--evidence",type=Path);args=p.parse_args()
    if args.evidence:ingest(args.evidence)
    evaluate()
