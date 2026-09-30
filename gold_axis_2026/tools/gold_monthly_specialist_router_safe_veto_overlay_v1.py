from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

TAU = 0.50
MIN_PRIOR = 6
AGREE_THR = 0.80

TRANSPORT_MODELS = [
    "AOA_ELM",
    "ChHHO_ANFIS",
    "FULL7_ANN",
    "REDUCED4_ANN",
    "DE_ABC_RBFNN",
    "LMC2_RBF_M32",
    "PLS1_V1",
]

PERIODS = {
    "DEV_2022_04_2024_12": ("2022-04","2024-12"),
    "OPENED_2025": ("2025-01","2025-12"),
    "OPENED_2026": ("2026-01","2026-08"),
    "OPENED_2025_2026": ("2025-01","2026-08"),
}


def load_json(path: str):
    return json.loads(Path(path).read_text())


def row_map(rows):
    return {str(r["target"]): r for r in rows}


def combine_rows(*parts):
    out = {}
    for rows in parts:
        for r in rows:
            t = str(r["target"])
            if t in out:
                raise RuntimeError(("DUP_TARGET", t))
            out[t] = r
    return out


def load_transport_models(reference_rows_path: str, deabc_path: str, gpr_path: str, pls_path: str):
    ref = load_json(reference_rows_path)
    models = {}

    for name in ["AOA_ELM","ChHHO_ANFIS","FULL7_ANN","REDUCED4_ANN"]:
        p = ref["models"][name]
        models[name] = combine_rows(p["dev"], p["transport_2025"], p["stress_2026"])

    d = load_json(deabc_path)
    models["DE_ABC_RBFNN"] = combine_rows(
        d["dev"]["rows"], d["transport_2025"]["rows"], d["stress_2026"]["rows"]
    )

    d = load_json(gpr_path)
    models["LMC2_RBF_M32"] = combine_rows(
        d["dev"]["rows"], d["transport_2025"]["rows"], d["stress_2026"]["rows"]
    )

    d = load_json(pls_path)
    models["PLS1_V1"] = combine_rows(
        d["dev"]["rows"], d["holdout_2025"]["rows"], d["stress_2026"]["rows"]
    )

    missing = [m for m in TRANSPORT_MODELS if m not in models]
    if missing:
        raise RuntimeError(("MISSING_MODELS", missing))
    return models


def q(x, p):
    return float(np.quantile(np.asarray(x, float), p))


def build_transport_features(models):
    common = set(models[TRANSPORT_MODELS[0]])
    for m in TRANSPORT_MODELS[1:]:
        common &= set(models[m])

    targets = sorted(t for t in common if "2022-04" <= t <= "2026-07")
    expected = 33 + 12 + 7
    if len(targets) != expected:
        raise RuntimeError(("COMMON_TARGETS", len(targets), targets[:3], targets[-3:]))

    feat = []
    for t in targets:
        vals = np.asarray([float(models[m][t]["forecast"]) for m in TRANSPORT_MODELS], float)
        base = models["ChHHO_ANFIS"][t]
        rw = float(base["rw"])
        ch = float(base["forecast"])
        med = float(np.median(vals))
        q25, q75 = np.quantile(vals, [.25,.75])
        disp = float((q75-q25)/abs(med)*100.0) if med != 0 else np.nan
        dirs = np.sign(vals-rw)
        chdir = np.sign(ch-rw)
        agree = float(np.mean(dirs==chdir)) if chdir != 0 else float(np.mean(dirs==0))
        feat.append({
            "target": t,
            "origin": str(base["origin"]),
            "rw": rw,
            "median_fcst": med,
            "dispersion_pct": disp,
            "chhho_direction_agreement": agree,
            "model_count": len(TRANSPORT_MODELS),
        })

    for i, r in enumerate(feat):
        hist = feat[:i]
        r["veto_eligible"] = bool(len(hist) >= MIN_PRIOR)
        if not r["veto_eligible"]:
            r["prior_disp_median"] = None
            r["V2_STRONG_DIRECTION_CONSENSUS"] = False
        else:
            prior = [x["dispersion_pct"] for x in hist]
            r["prior_disp_median"] = q(prior, .50)
            r["V2_STRONG_DIRECTION_CONSENSUS"] = bool(
                r["chhho_direction_agreement"] >= AGREE_THR
                and r["dispersion_pct"] <= r["prior_disp_median"]
            )
    return feat


def subset(rows, a, b):
    return [r for r in rows if a <= r["target"] <= b]


def metrics(rows, decision_field: str):
    fired = [r for r in rows if bool(r[decision_field])]
    high_all = sum(r["severity"]=="HIGH" for r in rows)
    med_all = sum(r["severity"]=="MEDIUM" for r in rows)
    elev_all = high_all + med_all
    hh = sum(r["severity"]=="HIGH" for r in fired)
    mh = sum(r["severity"]=="MEDIUM" for r in fired)
    fc = sum(r["severity"]=="NORMAL" for r in fired)
    return {
        "events": len(fired),
        "high_hits": int(hh),
        "medium_hits": int(mh),
        "false_calls": int(fc),
        "high_recall": None if high_all==0 else float(hh/high_all),
        "elevated_recall": None if elev_all==0 else float((hh+mh)/elev_all),
        "false_call_rate": None if not fired else float(fc/len(fired)),
        "useful_call_rate": None if not fired else float((hh+mh)/len(fired)),
        "event_targets": [r["target"] for r in fired],
    }


def annotate_router_rows(router, supp, feat7):
    supp_map = {r["target"]: r for r in supp["rows"]}
    feat7_map = {r["target"]: r for r in feat7}

    rows = []
    for period in ["DEV_2022_04_2024_12","OPENED_2025","OPENED_2026"]:
        for rr in router["periods"][period]["rows"]:
            r = dict(rr)
            r["router_warn"] = bool(float(r["p_high"]) >= TAU)

            s = supp_map.get(r["target"])
            if s is not None:
                r["dev_veto16_eligible"] = bool(s["veto_eligible"])
                r["dev_veto16"] = bool(s["V2_STRONG_DIRECTION_CONSENSUS"])
                r["dev_veto16_dispersion_pct"] = s["dispersion_pct"]
                r["dev_veto16_prior_disp_median"] = s["prior_disp_median"]
                r["dev_veto16_direction_agreement"] = s["chhho_direction_agreement"]
            else:
                r["dev_veto16_eligible"] = False
                r["dev_veto16"] = False
                r["dev_veto16_dispersion_pct"] = None
                r["dev_veto16_prior_disp_median"] = None
                r["dev_veto16_direction_agreement"] = None

            f = feat7_map.get(r["target"])
            if f is not None:
                r["transport_veto7_feature_available"] = True
                r["transport_veto7_eligible"] = bool(f["veto_eligible"])
                r["transport_veto7"] = bool(f["V2_STRONG_DIRECTION_CONSENSUS"])
                r["transport_veto7_dispersion_pct"] = f["dispersion_pct"]
                r["transport_veto7_prior_disp_median"] = f["prior_disp_median"]
                r["transport_veto7_direction_agreement"] = f["chhho_direction_agreement"]
            else:
                r["transport_veto7_feature_available"] = False
                r["transport_veto7_eligible"] = False
                r["transport_veto7"] = False
                r["transport_veto7_dispersion_pct"] = None
                r["transport_veto7_prior_disp_median"] = None
                r["transport_veto7_direction_agreement"] = None

            # Primary DEV overlay uses exact original 16-model veto.
            r["dev_overlay_warn"] = bool(
                r["router_warn"] and not (
                    r["dev_veto16_eligible"] and r["dev_veto16"]
                )
            )

            # Transport-compatible overlay: no feature -> pass through.
            r["transport_overlay_warn"] = bool(
                r["router_warn"] and not (
                    r["transport_veto7_feature_available"]
                    and r["transport_veto7_eligible"]
                    and r["transport_veto7"]
                )
            )
            rows.append(r)

    # De-duplicate combined periods source: DEV + 2025 + 2026 are disjoint.
    seen=set()
    uniq=[]
    for r in rows:
        if r["target"] in seen:
            raise RuntimeError(("DUP_ROUTER_TARGET",r["target"]))
        seen.add(r["target"])
        uniq.append(r)
    return sorted(uniq,key=lambda x:x["target"])


def suppressed_detail(rows, base_field, final_field, veto_kind):
    out=[]
    for r in rows:
        if bool(r[base_field]) and not bool(r[final_field]):
            out.append({
                "origin":r["origin"],
                "target":r["target"],
                "severity":r["severity"],
                "active_signals":r["active_signals"],
                "awake_experts":r["awake_experts"],
                "p_high":float(r["p_high"]),
                "veto_kind":veto_kind,
                "direction_agreement": (
                    r["dev_veto16_direction_agreement"]
                    if veto_kind=="DEV_16_MODEL" else r["transport_veto7_direction_agreement"]
                ),
                "dispersion_pct": (
                    r["dev_veto16_dispersion_pct"]
                    if veto_kind=="DEV_16_MODEL" else r["transport_veto7_dispersion_pct"]
                ),
                "prior_disp_median": (
                    r["dev_veto16_prior_disp_median"]
                    if veto_kind=="DEV_16_MODEL" else r["transport_veto7_prior_disp_median"]
                ),
            })
    return out


def dev_veto_overlap(rows):
    eligible = [
        r for r in rows
        if r["dev_veto16_eligible"] and r["transport_veto7_eligible"]
    ]
    set16={r["target"] for r in eligible if r["dev_veto16"]}
    set7={r["target"] for r in eligible if r["transport_veto7"]}
    union=set16|set7
    inter=set16&set7
    return {
        "jointly_eligible_n":len(eligible),
        "veto16_targets":sorted(set16),
        "veto7_targets":sorted(set7),
        "intersection":sorted(inter),
        "only16":sorted(set16-set7),
        "only7":sorted(set7-set16),
        "jaccard":None if not union else float(len(inter)/len(union)),
    }


def period_report(rows, use_dev16=False):
    base = metrics(rows,"router_warn")
    final_field = "dev_overlay_warn" if use_dev16 else "transport_overlay_warn"
    final = metrics(rows,final_field)
    suppressed = suppressed_detail(
        rows,"router_warn",final_field,
        "DEV_16_MODEL" if use_dev16 else "TRANSPORT_7_MODEL"
    )
    return {
        "n":len(rows),
        "router":base,
        "overlay":final,
        "suppressed":suppressed,
        "additional_false_removed":sum(x["severity"]=="NORMAL" for x in suppressed),
        "high_removed":sum(x["severity"]=="HIGH" for x in suppressed),
        "medium_removed":sum(x["severity"]=="MEDIUM" for x in suppressed),
        "feature_available_n": (
            len(rows) if use_dev16
            else sum(r["transport_veto7_feature_available"] for r in rows)
        ),
        "no_feature_targets": (
            [] if use_dev16
            else [r["target"] for r in rows if not r["transport_veto7_feature_available"]]
        ),
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--router-json",required=True)
    ap.add_argument("--suppressor-json",required=True)
    ap.add_argument("--reference-rows",required=True)
    ap.add_argument("--deabc-json",required=True)
    ap.add_argument("--gpr-json",required=True)
    ap.add_argument("--pls-json",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()

    router=load_json(args.router_json)
    supp=load_json(args.suppressor_json)
    if router.get("status")!="COMPLETE" or router.get("scientific_gate")!="PASS":
        raise RuntimeError("BAD_ROUTER")
    if router["selected_candidate"]["params"]["id"]!="HEDGE_eta0.25_tau0.50":
        raise RuntimeError(("ROUTER_NOT_FROZEN",router["selected_candidate"]["params"]))
    if supp.get("schema")!="GOLD_MONTHLY_ALARM_FALSE_CALL_SUPPRESSOR_SCREEN_V1_2026-09-30":
        raise RuntimeError("BAD_SUPPRESSOR")

    models=load_transport_models(
        args.reference_rows,args.deabc_json,args.gpr_json,args.pls_json
    )
    feat7=build_transport_features(models)
    rows=annotate_router_rows(router,supp,feat7)

    dev=subset(rows,*PERIODS["DEV_2022_04_2024_12"])
    y25=subset(rows,*PERIODS["OPENED_2025"])
    y26=subset(rows,*PERIODS["OPENED_2026"])
    opened=subset(rows,*PERIODS["OPENED_2025_2026"])
    if (len(dev),len(y25),len(y26),len(opened)) != (33,12,8,20):
        raise RuntimeError(("PERIOD_COUNTS",len(dev),len(y25),len(y26),len(opened)))

    dev_primary=period_report(dev,use_dev16=True)
    dev_shadow=period_report(dev,use_dev16=False)
    p25=period_report(y25,use_dev16=False)
    p26=period_report(y26,use_dev16=False)
    popen=period_report(opened,use_dev16=False)

    gate={
        "router_high_hits":dev_primary["router"]["high_hits"],
        "overlay_high_hits":dev_primary["overlay"]["high_hits"],
        "retain_all_router_high":bool(
            dev_primary["overlay"]["high_hits"]==dev_primary["router"]["high_hits"]
        ),
        "router_medium_hits":dev_primary["router"]["medium_hits"],
        "overlay_medium_hits":dev_primary["overlay"]["medium_hits"],
        "retain_all_router_medium":bool(
            dev_primary["overlay"]["medium_hits"]==dev_primary["router"]["medium_hits"]
        ),
        "additional_false_removed":dev_primary["additional_false_removed"],
        "additional_false_removed_pass":bool(dev_primary["additional_false_removed"]>=1),
        "router_useful_call_rate":dev_primary["router"]["useful_call_rate"],
        "overlay_useful_call_rate":dev_primary["overlay"]["useful_call_rate"],
        "useful_rate_improves":bool(
            dev_primary["overlay"]["useful_call_rate"] is not None
            and dev_primary["router"]["useful_call_rate"] is not None
            and dev_primary["overlay"]["useful_call_rate"] > dev_primary["router"]["useful_call_rate"]
        ),
    }
    gate["candidate_pass"]=all([
        gate["retain_all_router_high"],
        gate["retain_all_router_medium"],
        gate["additional_false_removed_pass"],
        gate["useful_rate_improves"],
    ])

    compatibility={
        "dev_shadow_high_removed":dev_shadow["high_removed"],
        "dev_shadow_medium_removed":dev_shadow["medium_removed"],
        "dev_shadow_false_removed":dev_shadow["additional_false_removed"],
        "safety_compatible":bool(dev_shadow["high_removed"]==0 and dev_shadow["medium_removed"]==0),
        "veto_flag_overlap":dev_veto_overlap(dev),
    }

    critical={}
    for target in ["2026-06","2026-08"]:
        r=next(x for x in opened if x["target"]==target)
        critical[target]={
            "origin":r["origin"],
            "severity":r["severity"],
            "router_warn":r["router_warn"],
            "transport_feature_available":r["transport_veto7_feature_available"],
            "transport_veto7":r["transport_veto7"],
            "overlay_warn":r["transport_overlay_warn"],
            "p_high":float(r["p_high"]),
            "awake_experts":r["awake_experts"],
        }

    result={
        "schema":"GOLD_MONTHLY_SPECIALIST_ROUTER_SAFE_VETO_OVERLAY_V1_2026-09-30",
        "status":"COMPLETE",
        "scientific_gate":"PASS",
        "frozen_router":{
            "id":"HEDGE_eta0.25_tau0.50",
            "eta":0.25,"alpha":0.0,"tau":TAU,
            "source_artifact":11124892942,
        },
        "frozen_dev_veto":{
            "id":"V2_STRONG_DIRECTION_CONSENSUS",
            "direction_agreement_threshold":AGREE_THR,
            "dispersion_rule":"<= expanding prior median",
            "min_prior":MIN_PRIOR,
            "original_competitive_pool_n":16,
            "source_artifact":11095060918,
        },
        "transport_pool":{
            "models":TRANSPORT_MODELS,
            "n":len(TRANSPORT_MODELS),
            "feature_targets_first":feat7[0]["target"],
            "feature_targets_last":feat7[-1]["target"],
            "feature_target_count":len(feat7),
        },
        "dev_primary_16_model_overlay":dev_primary,
        "dev_transport_pool_shadow":dev_shadow,
        "transport_pool_compatibility":compatibility,
        "periods":{
            "OPENED_2025":p25,
            "OPENED_2026":p26,
            "OPENED_2025_2026":popen,
        },
        "dev_overlay_candidate_gate":gate,
        "dev_overlay_status":"DEV_OVERLAY_CANDIDATE_PASS" if gate["candidate_pass"] else "DEV_OVERLAY_REJECT",
        "transport_pool_status":(
            "TRANSPORT_POOL_SAFETY_COMPATIBLE"
            if compatibility["safety_compatible"]
            else "TRANSPORT_POOL_NOT_SAFETY_COMPATIBLE"
        ),
        "critical_opened_checks":critical,
        "transport_features":feat7,
        "rows":rows,
        "governance":{
            "router_retuned":False,
            "safe_veto_threshold_retuned":False,
            "dispersion_rule_changed":False,
            "min_history_changed":False,
            "transport_model_pool_selected_after_outcomes":False,
            "target_actual_used_in_veto_features":False,
            "2025_2026_used_for_selection":False,
            "production_authorized":False,
            "forecast_modified":False,
            "model_switching_tested":False,
        },
    }

    Path(args.output).write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")

    print("SCIENTIFIC_GATE=PASS")
    print(json.dumps({
        "dev_overlay_status":result["dev_overlay_status"],
        "dev_gate":gate,
        "dev_primary":dev_primary,
        "transport_pool_status":result["transport_pool_status"],
        "compatibility":compatibility,
        "opened_2025":p25,
        "opened_2026":p26,
        "opened_2025_2026":popen,
        "critical_opened_checks":critical,
    },sort_keys=True))


if __name__=="__main__":
    main()
