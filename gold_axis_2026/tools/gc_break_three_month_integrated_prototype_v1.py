from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parents[1]
R4_SRC = ROOT / "r4_1" / "src"
if str(R4_SRC) not in sys.path:
    sys.path.insert(0, str(R4_SRC))

from gold_r4.emergency import EmergencyState
from gold_r4.gvz import gvz_risk
from gold_r4.monthly import three_month_direction
from gold_r4.tactical import completed_weekly_closes, fast_state, slow_state

CONTRACT_PATH = ROOT / "gc_break_v0" / "gc_break_three_month_integrated_prototype_contract_v1.json"
EVENT_CONTRACT_PATH = ROOT / "gc_break_v0" / "gc_break_event_contract_v1.json"
LOCKED_H1 = ROOT / "patch_repro_v1" / "locked_replay_v7_daily_feature_pit_43.csv"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if not spec or not spec.loader:
        raise RuntimeError(f"MODULE_IMPORT_FAIL:{path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def fetch_df(conn, sql: str, params=()) -> pd.DataFrame:
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return pd.DataFrame(cur.fetchall(), columns=[d.name for d in cur.description])


def sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(z, -35.0, 35.0)))


def fit_balanced_ridge_logit(X: np.ndarray, y: np.ndarray, lam: float = 1.0):
    n = len(y); n1 = int(y.sum()); n0 = n - n1
    if n1 < 5 or n0 < 20:
        raise RuntimeError(f"INSUFFICIENT_CLASS_SUPPORT:POS={n1}:NEG={n0}")
    w1 = n / (2.0 * n1); w0 = n / (2.0 * n0); sw = np.where(y == 1, w1, w0)
    def objective(theta):
        b = theta[0]; beta = theta[1:]; p = sigmoid(b + X @ beta); eps = 1e-12
        nll = -np.sum(sw * (y * np.log(p + eps) + (1-y) * np.log(1-p + eps)))
        return nll + 0.5 * lam * float(beta @ beta)
    res = minimize(objective, np.zeros(X.shape[1] + 1), method="L-BFGS-B")
    if not res.success:
        raise RuntimeError(f"LOGIT_OPTIMIZATION_FAIL:{res.message}")
    return float(res.x[0]), res.x[1:].astype(float), {"positive_weight": w1, "negative_weight": w0}


def auc_rank(y: np.ndarray, p: np.ndarray):
    y = np.asarray(y, int); p = np.asarray(p, float); n1 = int(y.sum()); n0 = len(y)-n1
    if n1 == 0 or n0 == 0: return None
    ranks = pd.Series(p).rank(method="average").to_numpy(); s = float(ranks[y == 1].sum())
    return float((s - n1*(n1+1)/2.0)/(n1*n0))


def same_robust(state: str, regime: str | None) -> bool:
    return (regime == "UP" and state == "ROBUST_UP") or (regime == "DOWN" and state == "ROBUST_DOWN")


def opposite_robust(state: str, regime: str | None) -> bool:
    return (regime == "UP" and state == "ROBUST_DOWN") or (regime == "DOWN" and state == "ROBUST_UP")


def load_inputs(conn, start: str, end_exclusive: str):
    xau = fetch_df(conn, """SELECT DISTINCT ON (observation_ts::date) observation_ts::date AS date, value AS close, quality_status, retrieved_at, metadata
      FROM observations WHERE series_id='XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1' AND observation_ts >= %s AND observation_ts < %s
      ORDER BY observation_ts::date, retrieved_at DESC NULLS LAST, id DESC""", (start, end_exclusive))
    gvz = fetch_df(conn, """SELECT DISTINCT ON (observation_ts::date) observation_ts::date AS date, value AS gvz, quality_status, retrieved_at
      FROM observations WHERE series_id='GVZ_CBOE' AND observation_ts >= %s AND observation_ts < %s
      ORDER BY observation_ts::date, retrieved_at DESC NULLS LAST, id DESC""", (start, end_exclusive))
    vix = fetch_df(conn, """SELECT DISTINCT ON (observation_ts::date) observation_ts::date AS date, value AS vix, quality_status, retrieved_at
      FROM observations WHERE series_id='VIX_CBOE' AND observation_ts >= %s AND observation_ts < %s
      ORDER BY observation_ts::date, retrieved_at DESC NULLS LAST, id DESC""", (start, end_exclusive))
    macro = fetch_df(conn, """SELECT series_id, observation_ts, value, metadata, available_as_of, first_seen_at, retrieved_at, quality_status
      FROM observations WHERE series_id = ANY(%s) AND observation_ts >= %s AND observation_ts < %s ORDER BY observation_ts, series_id""",
      (["MACRO_EVENT_V3_EMPLOYMENT_SCORE","MACRO_EVENT_V3_INFLATION_SCORE","MACRO_EVENT_V3_FOMC_SCORE"], start, end_exclusive))
    cache5 = fetch_df(conn, """SELECT date_trunc('month',observation_ts)::date AS month, COUNT(*) AS rows,
      COUNT(DISTINCT observation_ts::date) AS distinct_dates, MIN(observation_ts) AS min_ts, MAX(observation_ts) AS max_ts
      FROM xau_intraday_research_cache_5m WHERE observation_ts >= %s AND observation_ts < %s GROUP BY 1 ORDER BY 1""", (start, end_exclusive))
    return xau, gvz, vix, macro, cache5


def prepare_h1() -> pd.DataFrame:
    h1 = pd.read_csv(LOCKED_H1); h1["month"] = h1["month"].astype(str)
    cols = ["month","rw","mom","vw","patch_v7"]
    if not set(cols) <= set(h1.columns): raise RuntimeError("LOCKED_H1_SCHEMA_FAIL")
    for c in cols[1:]:
        h1[c] = pd.to_numeric(h1[c], errors="raise")
        if (~np.isfinite(h1[c])).any() or (h1[c] <= 0).any(): raise RuntimeError(f"INVALID_H1:{c}")
    return h1[cols].copy()


def build_bocpd_lookup() -> pd.DataFrame:
    mod = load_module(ROOT / "tools" / "bocpd_return_successor_v1.py", "gc_break_three_month_bocpd")
    r = mod.build_replay().rows.reset_index(); r["month"] = pd.to_datetime(r["month"]).dt.to_period("M").astype(str)
    return r[["month","state","reset_fraction","p_run0","run_length_entropy","evidence_class"]].copy()


def build_role_panel(daily: pd.DataFrame, h1: pd.DataFrame, bocpd: pd.DataFrame) -> pd.DataFrame:
    hl = h1.set_index("month"); bl = bocpd.set_index("month")
    month_levels = daily.set_index("date")["close"].resample("MS").last().dropna(); em = EmergencyState(); rows=[]
    for i,row in daily.iterrows():
        d=pd.Timestamp(row["date"]); c=float(row["close"]); hist=daily.loc[:i,["date","close"]]
        fs=fast_state(hist["close"].tolist()).value; ss=slow_state(completed_weekly_closes(hist,d)).value
        mk=d.strftime("%Y-%m"); prior=month_levels.loc[month_levels.index < pd.Timestamp(mk+"-01")]
        md=three_month_direction(prior.pct_change().dropna().tolist()).value
        if mk not in hl.index: raise RuntimeError(f"H1_MONTH_MISSING:{mk}")
        hr=hl.loc[mk]; hv=[float(hr["rw"]),float(hr["mom"]),float(hr["vw"]),float(hr["patch_v7"])]
        consensus=float(np.median(hv)); dispersion=float(np.std(hv,ddof=0)); el,er=em.update(d,c,float(hr["patch_v7"]))
        pm=(d.to_period("M")-1).strftime("%Y-%m")
        if pm in bl.index:
            br=bl.loc[pm]; bs=str(br["state"]); breset=float(br["reset_fraction"]); brun=float(br["p_run0"]); bent=float(br["run_length_entropy"]); be=str(br["evidence_class"])
        else: bs=None; breset=np.nan; brun=np.nan; bent=np.nan; be=None
        rows.append({"date":d,"close":c,"fast_state":fs,"slow_state":ss,"monthly_direction_3m":md,
          "h1_random_walk":hv[0],"h1_momentum_3m":hv[1],"h1_vw_midas":hv[2],"h1_causal_patch":hv[3],
          "h1_consensus_median":consensus,"h1_dispersion_std":dispersion,"h1_price_gap_to_consensus":c/consensus-1.0,
          "emergency_level":el.value,"emergency_reversal":er.value,"bocpd_source_month":pm,"bocpd_state":bs,
          "bocpd_reset_fraction":breset,"bocpd_p_run0":brun,"bocpd_run_length_entropy":bent,"bocpd_evidence_class":be})
    return pd.DataFrame(rows)


def map_macro(origins: pd.DataFrame, macro: pd.DataFrame) -> pd.DataFrame:
    out=origins[["date"]].copy().sort_values("date").reset_index(drop=True)
    for c in ["macro_event_count","macro_strong_adverse_count","macro_strong_supportive_count"]: out[c]=0
    out["macro_max_abs_score"]=0.0; dates=out["date"].to_numpy(dtype="datetime64[ns]")
    for _,r in macro.iterrows():
        ed=pd.Timestamp(r["observation_ts"]).tz_convert("America/New_York").tz_localize(None).normalize(); pos=int(np.searchsorted(dates,np.datetime64(ed),side="left"))
        if pos>=len(out): continue
        state=str((r["metadata"] or {}).get("state") or "")
        out.loc[pos,"macro_event_count"]+=1; out.loc[pos,"macro_strong_adverse_count"]+=int(state=="GOLD_ADVERSE_MACRO_SHOCK")
        out.loc[pos,"macro_strong_supportive_count"]+=int(state=="GOLD_SUPPORTIVE_MACRO_SHOCK")
        out.loc[pos,"macro_max_abs_score"]=max(float(out.loc[pos,"macro_max_abs_score"]),abs(float(r["value"])))
    return out


def episode_metrics(timeline: pd.DataFrame, signal_col: str):
    x=timeline[["date","is_break",signal_col]].copy().reset_index(drop=True); flags=x[signal_col].fillna(False).astype(bool).to_numpy(); episodes=[]; start=None
    for i,flag in enumerate(flags):
        if flag and start is None: start=i
        if start is not None and ((not flag) or i==len(flags)-1):
            end=i-1 if not flag else i; next_idx=end+1; converted=next_idx<len(x) and bool(x.loc[next_idx,"is_break"])
            bd=pd.Timestamp(x.loc[next_idx,"date"]) if converted else None
            episodes.append({"start_date":pd.Timestamp(x.loc[start,"date"]).date().isoformat(),"end_date":pd.Timestamp(x.loc[end,"date"]).date().isoformat(),
              "converted":converted,"break_date":bd.date().isoformat() if bd is not None else None,"lead_origins":int(next_idx-start) if converted else None})
            start=None
    conv=[e for e in episodes if e["converted"]]; detected={e["break_date"] for e in conv}; breaks=set(pd.to_datetime(x.loc[x["is_break"],"date"]).dt.strftime("%Y-%m-%d"))
    leads=[e["lead_origins"] for e in conv if e["lead_origins"] is not None]
    return {"episodes":len(episodes),"converted_episodes":len(conv),"false_episodes":len(episodes)-len(conv),
      "episode_conversion_rate":len(conv)/len(episodes) if episodes else None,"event_recall":len(detected)/len(breaks) if breaks else None,
      "false_episodes_per_100_scored_origins":(len(episodes)-len(conv))*100.0/max(int((~x["is_break"]).sum()),1),
      "median_lead_origins":float(np.median(leads)) if leads else None,"episodes_detail":episodes}


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--output-dir",type=Path,required=True); args=ap.parse_args(); args.output_dir.mkdir(parents=True,exist_ok=True)
    contract=json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if contract.get("status")!="RESEARCH_ONLY_FROZEN_BEFORE_SCORING" or contract["governance"]["no_database_writes"] is not True: raise RuntimeError("CONTRACT_GUARD_FAIL")
    db=os.environ.get("NEON_DATABASE_URL","").strip()
    if not db: raise RuntimeError("NEON_DATABASE_URL_NOT_SET")
    with psycopg.connect(db) as conn:
        with conn.cursor() as cur: cur.execute("SET TRANSACTION READ ONLY")
        xau,gvz,vix,macro_all,cache5=load_inputs(conn,"2025-01-01","2026-07-01")
    for d in (xau,gvz,vix): d["date"]=pd.to_datetime(d["date"]).dt.normalize()
    xau["close"]=pd.to_numeric(xau["close"],errors="raise"); gvz["gvz"]=pd.to_numeric(gvz["gvz"],errors="raise"); vix["vix"]=pd.to_numeric(vix["vix"],errors="raise")
    macro_all["observation_ts"]=pd.to_datetime(macro_all["observation_ts"],utc=True)
    daily=xau[xau["date"].dt.dayofweek<5][["date","close"]].drop_duplicates("date").sort_values("date").reset_index(drop=True)
    h1=prepare_h1(); bocpd=build_bocpd_lookup(); panel=build_role_panel(daily,h1,bocpd)
    diag=load_module(ROOT/"tools"/"gc_break_v0_governed_diagnostic_v1.py","gc_break_three_month_diag"); event_contract=json.loads(EVENT_CONTRACT_PATH.read_text(encoding="utf-8"))
    events,origins=diag.build_break_inventory(panel[["date","close"]],event_contract); p=panel.merge(origins,on="date",how="left",validate="one_to_one")
    valid=p["regime_pre"].isin(["UP","DOWN"]); p["adverse_fraction_clipped_0_1"]=p["adverse_fraction"].clip(0,1).fillna(0.0)
    p["fast_conflict"]=valid & ~pd.Series([same_robust(s,r) for s,r in zip(p["fast_state"],p["regime_pre"])])
    p["fast_opposite"]=pd.Series([opposite_robust(s,r) for s,r in zip(p["fast_state"],p["regime_pre"])])
    p["slow_opposite"]=pd.Series([opposite_robust(s,r) for s,r in zip(p["slow_state"],p["regime_pre"])])
    p["emergency_reversal_opposite"]=((p["regime_pre"]=="UP")&(p["emergency_reversal"]=="DOWN_ALERT"))|((p["regime_pre"]=="DOWN")&(p["emergency_reversal"]=="UP_ALERT"))
    p["is_break"]=p["event_id"].notna(); p["next_date"]=p["date"].shift(-1); all_break=set(pd.to_datetime(events["break_date"])) if len(events) else set(); p["y_next_break"]=p["next_date"].isin(all_break).astype(int)
    model=p[~p["is_break"]].copy(); train=model[(model["date"]>="2025-01-02")&(model["next_date"]<="2026-03-31")].copy(); train["fast_conflict"]=train["fast_conflict"].astype(int)
    feats=["adverse_fraction_clipped_0_1","fast_conflict"]; Xtr=train[feats].to_numpy(float); ytr=train["y_next_break"].to_numpy(int)
    intercept,beta,class_weights=fit_balanced_ridge_logit(Xtr,ytr,1.0); ptr=sigmoid(intercept+Xtr@beta); threshold=float(np.quantile(ptr,0.75))
    risk=gvz.merge(vix,on="date",how="inner",validate="one_to_one"); risk=risk[(risk["date"]>="2026-04-01")&(risk["date"]<="2026-06-30")]
    full=p[(p["date"]>="2026-04-01")&(p["date"]<="2026-06-30")].merge(risk[["date","gvz","vix"]],on="date",how="inner",validate="one_to_one").sort_values("date").reset_index(drop=True)
    if len(full)<int(contract["selection_rule"]["minimum_common_xau_gvz_vix_origins"]): raise RuntimeError(f"COMMON_ORIGIN_COVERAGE_FAIL:{len(full)}")
    macro=macro_all[(macro_all["observation_ts"]>=pd.Timestamp("2026-04-01",tz="UTC"))&(macro_all["observation_ts"]<pd.Timestamp("2026-07-01",tz="UTC"))]
    full=full.merge(map_macro(full,macro),on="date",how="left",validate="one_to_one")
    gvz_states=[gvz_risk(float(v)) for v in full["gvz"]]; full["gvz_cap"]=[float(s.cap) for s in gvz_states]; full["gvz_panic"]=[bool(s.panic) for s in gvz_states]
    full["macro_event_opposite"]=((full["regime_pre"]=="UP")&(full["macro_strong_adverse_count"]>0))|((full["regime_pre"]=="DOWN")&(full["macro_strong_supportive_count"]>0))
    full["strong_modifier"]=full["fast_opposite"]|full["emergency_reversal_opposite"]|full["macro_event_opposite"]
    full["strategic_prior_conflict"]=((full["regime_pre"]=="UP")&(full["monthly_direction_3m"]=="DOWN"))|((full["regime_pre"]=="DOWN")&(full["monthly_direction_3m"]=="UP"))
    full["h1_consensus_context"]=np.where(full["h1_price_gap_to_consensus"]>=0,"PRICE_ABOVE_H1_CONSENSUS","PRICE_BELOW_H1_CONSENSUS")
    full["risk_context"]=np.where(full["gvz_panic"],"PANIC",np.where(full["gvz_cap"]<1.0,"ELEVATED","NORMAL"))
    full["reliability_status"]=np.where(full[["bocpd_state","h1_consensus_median","gvz"]].notna().all(axis=1),"SUPPORTED_RESEARCH_REPLAY","NO_SIGNAL_MISSING_CONTEXT")
    score=full[~full["is_break"]].copy().reset_index(drop=True); Xte=score[feats].assign(fast_conflict=score["fast_conflict"].astype(int)).to_numpy(float); yte=score["y_next_break"].to_numpy(int)
    score["hazard_next_observation"]=sigmoid(intercept+Xte@beta); score["weakening"]=score["hazard_next_observation"]>=threshold
    states=[]; consecutive=0
    for _,r in score.iterrows():
        if bool(r["weakening"]): consecutive+=1; states.append("BREAK_ALERT" if consecutive>=2 or bool(r["strong_modifier"]) else "WEAKENING")
        else: consecutive=0; states.append("STABLE")
    score["sequential_state"]=states; score["break_alert"]=score["sequential_state"].eq("BREAK_ALERT")
    full=full.merge(score[["date","hazard_next_observation","weakening","sequential_state","break_alert"]],on="date",how="left",validate="one_to_one")
    full.loc[full["is_break"],["weakening","break_alert"]]=False; full.loc[full["is_break"],"sequential_state"]="GROUND_TRUTH_BREAK_NOT_SCORED"
    weakening_metrics=episode_metrics(full,"weakening"); alert_metrics=episode_metrics(full,"break_alert")

    event_meta=events[["break_date","new_regime"]].copy()
    event_meta["break_date"]=pd.to_datetime(event_meta["break_date"]).dt.normalize()
    if event_meta["break_date"].duplicated().any():
        raise RuntimeError("DUPLICATE_BREAK_DATE_IN_EVENT_META")
    break_rows=full[full["is_break"]].copy().merge(
        event_meta,
        left_on="date",
        right_on="break_date",
        how="left",
        validate="one_to_one",
    )
    if break_rows["new_regime"].isna().any():
        raise RuntimeError("BREAK_EVENT_REGIME_JOIN_FAIL")
    slow_conf=[]
    for _,ev in break_rows.iterrows():
        bd=pd.Timestamp(ev["date"]); new_regime=str(ev["new_regime"]); nxt=break_rows.loc[break_rows["date"]>bd,"date"].min(); after=full[full["date"]>=bd].copy()
        if pd.notna(nxt): after=after[after["date"]<nxt]
        target="ROBUST_UP" if new_regime=="UP" else "ROBUST_DOWN"; hit=after[after["slow_state"].eq(target)]; confirm=None if hit.empty else pd.Timestamp(hit.iloc[0]["date"])
        delay=None if confirm is None else int(after.reset_index(drop=True).index[after["date"].reset_index(drop=True).eq(confirm)][0])
        slow_conf.append({"break_date":bd.date().isoformat(),"new_regime":new_regime,"confirmation_date":confirm.date().isoformat() if confirm is not None else None,"delay_origins":delay})
    represented={
      "CAUSAL_PATCH":bool(full["h1_causal_patch"].notna().all()),"VW_MIDAS_MSVR_SUCCESSOR_V1":bool(full["h1_vw_midas"].notna().all()),
      "MOMENTUM_3M":bool(full["h1_momentum_3m"].notna().all()),"RANDOM_WALK":bool(full["h1_random_walk"].notna().all()),
      "MONTHLY_DIRECTION_3M":bool(full["monthly_direction_3m"].notna().all()),"FAST":bool(full["fast_state"].notna().all()),"SLOW":bool(full["slow_state"].notna().all()),
      "MACRO_EVENT_SUCCESSOR_V2":bool(len(macro)>0),"BOCPD_RETURN_SUCCESSOR_V1":bool(full["bocpd_state"].notna().all()),
      "EMERGENCY_LEVEL":bool(full["emergency_level"].notna().all()),"EMERGENCY_REVERSAL":bool(full["emergency_reversal"].notna().all()),"GVZ_RISK":bool(full["gvz"].notna().all())}
    if not all(represented.values()): raise RuntimeError(f"RUNTIME_IDENTITY_INTEGRATION_FAIL:{represented}")
    cache5["month"]=pd.to_datetime(cache5["month"]).dt.strftime("%Y-%m"); cache_sel=cache5[cache5["month"].isin(["2026-04","2026-05","2026-06"])]
    breaks=[pd.Timestamp(d).date().isoformat() for d in full.loc[full["is_break"],"date"]]
    summary={"audit_id":"GC_BREAK_THREE_MONTH_INTEGRATED_PROTOTYPE_V1","contract_status":contract["status"],"evidence_class":"HISTORICAL_RESEARCH_REPLAY_NOT_CANONICAL_NY17",
      "official_wp4_completion":False,"coverage_selection_consumed_outcomes":False,
      "coverage":{"selected_window":["2026-04-01","2026-06-30"],"common_xau_gvz_vix_origins":int(len(full)),"scored_non_break_origins":int(len(score)),
        "origins_by_month":{k:int(v) for k,v in full.groupby(full["date"].dt.strftime("%Y-%m")).size().to_dict().items()},"macro_events":int(len(macro)),
        "macro_events_by_family":{str(k):int(v) for k,v in macro["series_id"].value_counts().to_dict().items()},"cache5":cache_sel.to_dict(orient="records"),
        "missing_required_context_rows":int((full["reliability_status"]!="SUPPORTED_RESEARCH_REPLAY").sum())},
      "runtime_identity_representation":represented,
      "learned_core":{"training_start":"2025-01-02","training_end":"2026-03-31","train_origins":int(len(train)),"train_break_targets":int(ytr.sum()),"features":feats,
        "intercept":intercept,"coefficients":{k:float(v) for k,v in zip(feats,beta)},"class_weights":class_weights,"weakening_threshold_training_q75":threshold,"train_auc":auc_rank(ytr,ptr)},
      "test":{"coverage_origins":int(len(full)),"scored_origins":int(len(score)),"next_break_targets":int(yte.sum()),"break_dates":breaks,"test_auc":auc_rank(yte,score["hazard_next_observation"].to_numpy(float)),
        "weakening":weakening_metrics,"break_alert":alert_metrics,"slow_confirmation":slow_conf},
      "channel_activity":{"fast_conflict_origins":int(full["fast_conflict"].sum()),"fast_opposite_origins":int(full["fast_opposite"].sum()),
        "emergency_level_non_neutral":int((full["emergency_level"]!="NEUTRAL").sum()),"emergency_reversal_origins":int((full["emergency_reversal"]!="OFF").sum()),
        "strong_macro_event_origins":int(((full["macro_strong_adverse_count"]+full["macro_strong_supportive_count"])>0).sum()),"gvz_panic_origins":int(full["gvz_panic"].sum()),
        "gvz_elevated_or_panic_origins":int((full["gvz_cap"]<1.0).sum()),"strategic_prior_conflict_origins":int(full["strategic_prior_conflict"].sum()),
        "bocpd_state_counts":{str(k):int(v) for k,v in full["bocpd_state"].value_counts(dropna=False).to_dict().items()}},
      "governance":{"database_write":"NONE","prospective_claim":False,"canonical_exact_ny17":False,"post_test_threshold_tuning":False,"flat_equal_vote":False,"buy_sell_mapping":False,
        "interpretation":"Research-only three-month integration prototype. All 12 governed runtime identities are role-preserved. This does not complete manifest WP4 and requires canonical/full-formation validation."}}
    full.to_csv(args.output_dir/"gc_break_three_month_integrated_panel_v1.csv",index=False); pd.DataFrame(slow_conf).to_csv(args.output_dir/"gc_break_three_month_slow_confirmation_v1.csv",index=False)
    (args.output_dir/"gc_break_three_month_integrated_summary_v1.json").write_text(json.dumps(summary,indent=2,sort_keys=True,default=str,allow_nan=False)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2,sort_keys=True,default=str,allow_nan=False)); return 0

if __name__ == "__main__":
    raise SystemExit(main())
