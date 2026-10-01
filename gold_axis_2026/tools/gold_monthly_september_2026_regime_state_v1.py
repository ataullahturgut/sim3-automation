from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

import gold_monthly_market_regime_discovery_v1 as discovery
import gold_monthly_market_regime_prototype_alignment_v1 as palign
import gold_monthly_market_regime_transition_detector_v2 as transv2
import gold_monthly_market_regime_extreme_v1 as extreme


MONTH = "2026-09"
FROZEN_V2_RULE = {
    "alt_growth_thr": 0.1,
    "drop_thr": 0.1,
    "fast_votes": 2,
    "margin_drop_thr": 0.15,
    "margin_thr": 0.45,
    "persistent_margin_thr": 0.3,
    "persistent_votes": 1,
    "proto_drop_thr": 0.25,
}


def load(p):
    return json.loads(Path(p).read_text())


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--snapshot",required=True)
    ap.add_argument("--public-bundle",required=True)
    ap.add_argument("--external",required=True)
    ap.add_argument("--prior-discovery",required=True)
    ap.add_argument("--prior-transition-v2",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()

    snapshot=load(a.snapshot)
    public=load(a.public_bundle)
    external=load(a.external)
    prior=load(a.prior_discovery)
    prior_v2=load(a.prior_transition_v2)

    if prior.get("status")!="COMPLETE":
        raise RuntimeError("PRIOR_DISCOVERY_INVALID")
    if prior_v2.get("status")!="COMPLETE":
        raise RuntimeError("PRIOR_V2_INVALID")
    if prior_v2.get("selected_rule")!=FROZEN_V2_RULE:
        raise RuntimeError(("V2_RULE_MISMATCH",prior_v2.get("selected_rule"),FROZEN_V2_RULE))

    # Extend only the reporting/feature horizon. Frozen architecture/model-choice rules remain unchanged.
    discovery.END=MONTH

    panel,sources=discovery.build_panel(snapshot,public,external)
    if MONTH not in panel.index:
        raise RuntimeError(("SEPTEMBER_REGIME_FEATURE_ROW_MISSING",sources.get("missing")))

    required=list(pd.period_range("2025-01",MONTH,freq="M").astype(str))
    got=[m for m in panel.index if "2025-01"<=m<=MONTH]
    if got!=required:
        raise RuntimeError(("TRANSPORT_PANEL_NOT_CONTIGUOUS",got,sources.get("missing")))

    # Frozen semantic prototypes come only from the original 2010..2024 discovery authority.
    raw_prior=pd.DataFrame(prior["monthly_regimes"]).sort_values("month").reset_index(drop=True)
    proto=palign.build_frozen_prototypes(raw_prior)

    train=panel.loc[panel.index<MONTH].copy()
    cur=panel.loc[[MONTH]].copy()

    # Expanding-refit current state, strictly trained through Aug-2026.
    fit=palign.fit_frozen(train,proto)
    state=palign.score_sequence(fit,train,cur)[0]

    # Frozen V2 transition rule on the same current-month row.
    tr_base=transv2.score_sequence_features(fit,train,cur,proto)[0]
    tr={**tr_base,**transv2.apply_rule_row(tr_base,FROZEN_V2_RULE)}

    # Frozen extreme definition.
    ex=extreme.score_sequence(fit,train,cur)[0]

    # Cross-check semantic state/probability consistency across the three frozen views.
    if state["prototype_state"]!=tr["semantic_state"] or state["prototype_state"]!=ex["semantic_state"]:
        raise RuntimeError(("SEMANTIC_STATE_MISMATCH",state["prototype_state"],tr["semantic_state"],ex["semantic_state"]))
    if abs(float(state["probability"])-float(tr["semantic_probability"]))>1e-10:
        raise RuntimeError("TRANSITION_PROBABILITY_MISMATCH")
    if abs(float(state["probability"])-float(ex["semantic_probability"]))>1e-10:
        raise RuntimeError("EXTREME_PROBABILITY_MISMATCH")

    if tr["transition_flag"] and ex["extreme_flag"]:
        combined="BOTH"
    elif tr["transition_flag"]:
        combined="TRANSITION"
    elif ex["extreme_flag"]:
        combined="EXTREME"
    elif ex["extreme_status"]=="NORMAL":
        combined="NORMAL"
    else:
        combined="DEFER"

    row={k:float(panel.loc[MONTH,k]) for k in discovery.FEATURES}

    out={
        "schema":"GOLD_MONTHLY_SEPTEMBER_2026_REGIME_STATE_V1_2026-10-01",
        "status":"COMPLETE",
        "month":MONTH,
        "role":"ORIGIN_STATE_FOR_2026_10_FORECAST",
        "primary_schedule":"EXPANDING_REFIT",
        "training_end":str(train.index[-1]),
        "training_rows":int(len(train)),
        "semantic_state":state["prototype_state"],
        "semantic_label":state["prototype_label"],
        "semantic_probability":float(state["probability"]),
        "ood":bool(state["ood"]),
        "display_label":(
            ("BELIRSIZ" if state["prototype_label"]=="BELIRSIZ" else state["prototype_state"])
            + (" / AŞIRI-OOD" if state["ood"] else "")
        ),
        "transition":{
            "status":tr["transition_status"],
            "flag":bool(tr["transition_flag"]),
            "fast_branch":bool(tr["fast_branch"]),
            "persistent_branch":bool(tr["persistent_branch"]),
            "current_votes":int(tr["current_directional_votes"]),
            "previous_votes":int(tr["previous_directional_votes"]),
            "current_flags":list(tr["current_directional_flags"]),
            "previous_flags":list(tr["previous_directional_flags"]),
            "incumbent_drop":float(tr["current_incumbent_drop"]),
            "alternative_growth":float(tr["current_alternative_growth"]),
            "margin_cur":float(tr["current_margin_cur"]),
            "margin_drop":float(tr["current_margin_drop"]),
            "prototype_advantage_drop":float(tr["current_prototype_advantage_drop"]),
            "frozen_rule":FROZEN_V2_RULE,
        },
        "extreme":{
            "status":ex["extreme_status"],
            "flag":bool(ex["extreme_flag"]),
            "eligible_within_regime":bool(ex["eligible_within_regime"]),
            "anomaly_count":int(ex["anomaly_count"]),
            "active_signals":list(ex["active_signals"]),
            "E1_state_emission_tail":bool(ex["E1_state_emission_tail"]),
            "E2_predictive_surprise":bool(ex["E2_predictive_surprise"]),
            "E3_within_state_13D_distance":bool(ex["E3_within_state_13D_distance"]),
            "E4_market_state_jump":bool(ex["E4_market_state_jump"]),
            "emission_percentile":ex["emission_empirical_percentile"],
            "predictive_score_percentile":float(ex["predictive_score_empirical_percentile"]),
            "within_state_distance_percentile":ex["within_state_distance_empirical_percentile"],
            "market_state_jump_percentile":float(ex["market_state_jump_empirical_percentile"]),
        },
        "combined_state_category":combined,
        "market_state_features":row,
        "source_meta":sources,
        "data_notes":{
            "public_daily_last":public["daily_extension_last"],
            "world_bank_last":public["world_bank"]["last"],
            "world_bank_sep_available":"2026-09" in public["world_bank"]["gold_monthly"],
            "september_gold_level_source":"WORLD_BANK" if "2026-09" in public["world_bank"]["gold_monthly"] else "STAKTRAKR_FULL_MONTH_PROXY",
            "current_month_parameter_fit":False,
            "future_october_market_data_used":False,
        },
        "governance":{
            "regime_architecture_changed":False,
            "prototype_definition_changed":False,
            "transition_rule_changed":False,
            "extreme_rule_changed":False,
            "forecast_error_used":False,
            "alarm_outcome_used":False,
            "october_data_used":False,
        },
    }

    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("SEPTEMBER_2026_REGIME_GATE=PASS")
    print(json.dumps({
        "semantic_state":out["semantic_state"],
        "semantic_label":out["semantic_label"],
        "p":out["semantic_probability"],
        "ood":out["ood"],
        "transition":out["transition"],
        "extreme":out["extreme"],
        "combined_state_category":out["combined_state_category"],
        "training_end":out["training_end"],
        "public_daily_last":out["data_notes"]["public_daily_last"],
        "wb_sep_available":out["data_notes"]["world_bank_sep_available"],
        "gold_level_source":out["data_notes"]["september_gold_level_source"],
    },sort_keys=True))


if __name__=="__main__":
    main()
