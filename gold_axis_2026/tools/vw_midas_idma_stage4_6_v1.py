from __future__ import annotations
import json, math, os
from itertools import combinations
from pathlib import Path
import numpy as np
import psycopg
import vw_midas_msvr_successor_v1 as base
import vw_midas_dma_batch1_v1 as dma

DEV_START, DEV_END = "2022-04", "2024-12"
TR_START, TR_END = "2025-01", "2025-12"
ST_START, ST_END = "2026-01", "2026-07"
WARMUP = 30
FEATURES = dma.FEATURES
FORGETTING = dma.FORGETTING

# Paper-structured robustness: local validation window and loss metric.
SELECTOR_VARIANTS = (
    ("AE_PRICE", 12),
    ("AE_PRICE", 24),
    ("AE_PRICE", None),
    ("MSFE_LOGRET", 12),
    ("MSFE_LOGRET", 24),
    ("MSFE_LOGRET", None),
)

def masks_mandatory_gold_mr():
    optional = list(range(1, 8))
    return [(0,) + tuple(c) for r in range(8) for c in combinations(optional, r)]

MASKS = masks_mandatory_gold_mr()  # 2^7 = 128 candidate DMA models
MASK_TO_I = {m:i for i,m in enumerate(MASKS)}

# Each predictor-set pool contains every DMA model nested inside that selected predictor set.
# With only seven optional predictors we can exhaustively search all 128 predictor sets,
# avoiding a heuristic cyclic search error while preserving the IDMA optimization target.
POOL_SETS = MASKS
MEMBERSHIP = np.zeros((len(POOL_SETS), len(MASKS)), float)
for pi, pool in enumerate(POOL_SETS):
    S = set(pool)
    for mi, m in enumerate(MASKS):
        if set(m).issubset(S):
            MEMBERSHIP[pi, mi] = 1.0
if np.any(MEMBERSHIP.sum(1) < 1):
    raise RuntimeError("EMPTY_IDMA_PREDICTOR_POOL")

def scale_outer(samples, outer_target):
    keys = sorted(k for k in samples if k < outer_target)
    if len(keys) < WARMUP + 24:
        raise RuntimeError(f"IDMA_TRAIN_TOO_SMALL {outer_target} n={len(keys)}")
    X0 = np.stack([samples[k][0] for k in keys])
    Y0 = np.stack([samples[k][1] for k in keys])
    tx0 = np.asarray(samples[outer_target][0], float)
    xm, xs = X0[:WARMUP].mean(0), X0[:WARMUP].std(0)
    ym, ys = Y0[:WARMUP].mean(0), Y0[:WARMUP].std(0)
    xs = np.where(xs < 1e-9, 1.0, xs)
    ys = np.where(ys < 1e-9, 1.0, ys)
    return keys, (X0-xm)/xs, (Y0-ym)/ys, (tx0-xm)/xs, ym, ys

def pool_forecasts(weights, means):
    # weights K, means Kxq -> P x q
    den = MEMBERSHIP @ weights
    if np.any(den <= 1e-300):
        den = np.maximum(den, 1e-300)
    num = MEMBERSHIP @ (weights[:,None] * means)
    return num / den[:,None]

def prequential_forgetting_path(samples, outer_target, alpha, lam, lane):
    keys, X, Y, tx, ym, ys = scale_outer(samples, outer_target)
    q = 1 if lane == "AUTHORITY_GOLD" else 4
    Yuse = Y[:, :q]
    states = [dma.ModelState(m, q) for m in MASKS]
    K = len(states)
    log_post = np.full(K, -math.log(K), float)
    hist = []

    for t, key in enumerate(keys):
        log_prior = alpha * log_post
        log_prior -= dma.logsumexp(log_prior)
        prior_w = np.exp(log_prior)
        means = np.empty((K,q), float)
        ll = np.empty(K,float)
        cached = []
        for k, st in enumerate(states):
            z, mu, var, Rs = st.forecast(X[t], lam)
            means[k] = mu
            e = Yuse[t] - mu
            ll[k] = float(np.sum(-0.5*(np.log(2*np.pi*var)+(e*e)/var)))
            cached.append((z,mu,var,Rs))

        # Pre-update predictive forecasts: valid for nested selector scoring.
        pf = pool_forecasts(prior_w, means)
        pred_gold = pf[:,0] * ys[0] + ym[0]
        if t >= WARMUP:
            hist.append({
                "target": key,
                "pred_log_returns": pred_gold.copy(),
            })

        log_post = log_prior + ll
        log_post -= dma.logsumexp(log_post)
        for st,c in zip(states,cached):
            st.update(c[0], Yuse[t], c[1], c[2], c[3])

    # Outer target forecast uses all training rows but never target Y.
    log_prior = alpha * log_post
    log_prior -= dma.logsumexp(log_prior)
    prior_w = np.exp(log_prior)
    means = np.empty((K,q), float)
    for k, st in enumerate(states):
        means[k] = st.forecast(tx, lam)[1]
    pf = pool_forecasts(prior_w, means)
    final_gold = pf[:,0] * ys[0] + ym[0]
    return hist, final_gold

def price_from_ret(bundle, target, pred_ret):
    origin = base.month_shift(target, -1)
    return float(bundle.core_gold[origin] * math.exp(float(pred_ret)))

def selector_scores(bundle, hist, objective, window):
    usable = hist[-window:] if window is not None else hist
    if len(usable) < 12:
        raise RuntimeError(f"IDMA_SELECTOR_WINDOW_TOO_SMALL n={len(usable)}")
    P = len(POOL_SETS)
    if objective == "AE_PRICE":
        scores = np.zeros(P, float)
        for h in usable:
            target = h["target"]
            actual = float(bundle.core_gold[target])
            origin = base.month_shift(target, -1)
            anchor = float(bundle.core_gold[origin])
            forecasts = anchor * np.exp(h["pred_log_returns"])
            scores += np.abs(forecasts - actual)
        return scores, len(usable)
    if objective == "MSFE_LOGRET":
        scores = np.zeros(P, float)
        for h in usable:
            target = h["target"]
            p = base.month_shift(target, -1)
            actual_ret = math.log(float(bundle.monthly_metal["Gold"][target]) / float(bundle.monthly_metal["Gold"][p]))
            e = h["pred_log_returns"] - actual_ret
            scores += e*e
        return scores / len(usable), len(usable)
    raise ValueError(objective)

def compute_outer_candidates(bundle, samples, target, lane):
    out = {}
    for alpha, lam, tag in FORGETTING:
        hist, final = prequential_forgetting_path(samples, target, alpha, lam, lane)
        out[tag] = {"alpha":alpha, "lambda":lam, "hist":hist, "final":final}
    return out

def select_outer(bundle, candidates, objective, window):
    ranked = []
    for tag, z in candidates.items():
        scores, n = selector_scores(bundle, z["hist"], objective, window)
        for pi, s in enumerate(scores):
            ranked.append((float(s), tag, pi, n))
    ranked.sort(key=lambda x:(x[0], x[1], x[2]))
    best = ranked[0]
    s, tag, pi, n = best
    z = candidates[tag]
    return {
        "score": s,
        "forgetting_tag": tag,
        "alpha": z["alpha"],
        "lambda": z["lambda"],
        "pool_index": int(pi),
        "predictors": [FEATURES[j] for j in POOL_SETS[pi]],
        "selector_n": int(n),
        "pred_log_return_gold": float(z["final"][pi]),
        "top5": [
            {"score":float(a),"forgetting_tag":b,"pool_index":int(c),
             "predictors":[FEATURES[j] for j in POOL_SETS[c]]}
            for a,b,c,_ in ranked[:5]
        ],
    }

def outer_row(bundle, target, lane, objective, window, selection, model_id):
    origin = base.month_shift(target,-1)
    pred = selection["pred_log_return_gold"]
    return {
        "target":target, "origin":origin, "model":model_id, "lane":lane,
        "pred_log_return_gold":pred,
        "forecast":price_from_ret(bundle,target,pred),
        "actual":float(bundle.core_gold[target]),
        "rw":float(bundle.core_gold[origin]),
        "idma_selection":{
            "objective":objective,
            "window":"EXPANDING" if window is None else f"W{window}",
            "score":selection["score"],
            "forgetting_tag":selection["forgetting_tag"],
            "alpha":selection["alpha"], "lambda":selection["lambda"],
            "predictors":selection["predictors"],
            "selector_n":selection["selector_n"],
            "top5":selection["top5"],
            "target_or_future_actual_used":False,
        },
    }

def config_key(sel):
    return (sel["forgetting_tag"], sel["pool_index"])

def frozen_outer_prediction(candidates, frozen):
    return float(candidates[frozen["forgetting_tag"]]["final"][frozen["pool_index"]])

def build_variant(bundle, cache, lane, objective, window, precomputed):
    tag = "EXPANDING" if window is None else f"W{window}"
    model_id = f"IDMA_EXHAUSTIVE__{lane}__{objective}__{tag}"
    dev=[]; trace=[]
    for target in base.month_range(DEV_START,DEV_END):
        sel=select_outer(bundle,precomputed[target][lane],objective,window)
        dev.append(outer_row(bundle,target,lane,objective,window,sel,model_id))
        trace.append({"target":target,**sel})

    # Holdout guard: freeze predictor set and forgetting factors at 2025-01 origin,
    # using training history only through 2024-12.
    freeze_sel=select_outer(bundle,precomputed["2025-01"][lane],objective,window)
    freeze = {
        "frozen_at":DEV_END,
        "forgetting_tag":freeze_sel["forgetting_tag"],
        "alpha":freeze_sel["alpha"], "lambda":freeze_sel["lambda"],
        "pool_index":freeze_sel["pool_index"],
        "predictors":freeze_sel["predictors"],
        "selector_score_at_freeze":freeze_sel["score"],
        "selector_n":freeze_sel["selector_n"],
        "2025_2026_actuals_used_for_selection":False,
    }

    tr=[]; st=[]
    for start,end,dst in ((TR_START,TR_END,tr),(ST_START,ST_END,st)):
        for target in base.month_range(start,end):
            cand=precomputed[target][lane]
            pred=frozen_outer_prediction(cand,freeze)
            sel=dict(freeze); sel["pred_log_return_gold"]=pred; sel["top5"]=[]
            dst.append(outer_row(bundle,target,lane,objective,window,sel,model_id))
    return {
        "model_id":model_id,"lane":lane,"objective":objective,"window":tag,
        "dev":{"metrics":dma.active_metrics(dev),"yearly":dma.yearly(dev),"rows":dev},
        "transport_2025":{"metrics":dma.active_metrics(tr),"rows":tr},
        "stress_2026":{"metrics":dma.active_metrics(st),"rows":st},
        "selection_trace":trace,"external_freeze":freeze,
    }

def pareto(models):
    rows=[]
    for m in models:
        z=m["dev"]["metrics"]
        rows.append({"model":m["model_id"],"sum_abs_error":z["sum_abs_error"],
                     "direction_correct":z["direction_correct"],"direction_accuracy_pct":z["direction_accuracy_pct"],
                     "mae":z["mae"],"mape_pct":z["mape_pct"],"rmse":z["rmse"]})
    front=[]
    for a in rows:
        if not any((b["sum_abs_error"]<=a["sum_abs_error"] and b["direction_correct"]>=a["direction_correct"] and
                    (b["sum_abs_error"]<a["sum_abs_error"] or b["direction_correct"]>a["direction_correct"]))
                   for b in rows if b is not a):
            front.append(a)
    rows.sort(key=lambda x:(x["sum_abs_error"],-x["direction_correct"],x["model"]))
    front.sort(key=lambda x:(x["sum_abs_error"],-x["direction_correct"],x["model"]))
    return rows,front

def read_invariants(dsn):
    with psycopg.connect(dsn,autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("SET default_transaction_read_only=on")
            return base.authority_invariants(cur)

def main():
    dsn=os.environ.get("NEON_DATABASE_URL")
    if not dsn: raise SystemExit("NEON_DATABASE_URL required")
    bundle=base.load_data(dsn)
    targets=list(base.month_range(DEV_START,ST_END))
    cache={t:base.all_samples_at_origin(bundle,t,governed=True) for t in targets}

    # Shared expensive layer. Each outer origin is computed once per lane and forgetting pair;
    # all 128 predictor sets are then evaluated by exact pool re-normalization.
    precomputed={}
    for target in targets:
        precomputed[target]={}
        for lane in ("AUTHORITY_GOLD","GOVERNED_MULTI4"):
            precomputed[target][lane]=compute_outer_candidates(bundle,cache[target],target,lane)

    models=[]
    for lane in ("AUTHORITY_GOLD","GOVERNED_MULTI4"):
        for objective,window in SELECTOR_VARIANTS:
            models.append(build_variant(bundle,cache,lane,objective,window,precomputed))

    ranking,frontier=pareto(models)
    after=read_invariants(dsn)
    if after!=bundle.invariants_before: raise RuntimeError("AUTHORITY_INVARIANTS_CHANGED")

    for m in models:
        if len(m["dev"]["rows"])!=33 or len(m["transport_2025"]["rows"])!=12 or len(m["stress_2026"]["rows"])!=7:
            raise RuntimeError("PERIOD_COUNT_GATE_FAIL")
        if m["external_freeze"]["frozen_at"]!=DEV_END: raise RuntimeError("FREEZE_GATE_FAIL")
        for r in m["dev"]["rows"]+m["transport_2025"]["rows"]+m["stress_2026"]["rows"]:
            if not math.isfinite(r["forecast"]) or abs(r["pred_log_return_gold"])>=1:
                raise RuntimeError(f"SCIENTIFIC_GATE_FAIL {m['model_id']} {r['target']}")

    out={
        "family":"IDMA_STAGE4_6_V2","scope":"STAGE_4_TO_6",
        "method_identity":{
            "published_idma":"Chen et al. 2025: DMA inputs are optimized on neighbouring training/test windows by reselecting predictors and calibrating alpha/lambda.",
            "gold_authority":"Chen, Yang & Lan 2026: monthly gold IDMA; predictor selection plus forgetting-factor updates; horizon-specific gold drivers.",
            "implementation_status":"PAPER_STRUCTURED_EXHAUSTIVE_SMALL_SPACE_ADAPTATION",
            "why_exhaustive_not_cyclic":"Only 7 optional frozen predictors exist, so all 2^7=128 predictor sets can be evaluated exactly inside the training history. This removes heuristic path dependence while optimizing the same declared inputs.",
            "exact_author_software_replication_claim":False,
            "candidate_predictor_sets":128,
            "forgetting_configs":len(FORGETTING),
            "candidates_per_outer_lane":128*len(FORGETTING),
            "selector_objectives":["AE_PRICE","MSFE_LOGRET"],
            "selector_windows":["W12","W24","EXPANDING"],
            "horizon":"H=1_ONLY_BY_PROJECT_CONTRACT",
        },
        "governance":{
            "feature_contract":"UNCHANGED_VW_MIDAS_8_FEATURE",
            "gold_mr_mandatory":"mirrors lagged-dependent-variable role in gold IDMA literature",
            "selection_authority":f"{DEV_START}..{DEV_END}",
            "nested_selector":"inside each outer origin training history",
            "2025_role":"LOCKED_TRANSPORT_NOT_SELECTION",
            "2026_role":"RETROSPECTIVE_STRESS_NOT_SELECTION",
            "external_config_frozen_at":DEV_END,
            "database":"READ_ONLY","random_split":"NONE","target_month_leakage":False,
        },
        "source_checks":bundle.source_checks,
        "authority_invariants_before":bundle.invariants_before,
        "authority_invariants_after":after,
        "models":models,"dev_ranking":ranking,"dev_pareto_frontier":frontier,
    }
    Path("vw_midas_idma_stage4_6_v1_result.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("OUTPUT_GATE=PASS")
    print(json.dumps({
        "model_count":len(models),"best_dev_12":ranking[:12],"pareto":frontier,
        "external_freezes":{m["model_id"]:m["external_freeze"] for m in models},
        "authority_invariants_unchanged":after==bundle.invariants_before,
        "source_checks":bundle.source_checks,
    },sort_keys=True))

if __name__=="__main__": main()
