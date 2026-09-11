from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd

from gold_axis_2026.v149_research.monthly import BASE_MODELS,build_same_origin_panel
from gold_axis_2026.v149_research.short_horizon import feature_columns,inventory,load_features,raw_paths,target_arrays

ROOT=Path(__file__).resolve().parents[1]


def test_single_manifest_v149_and_locks():
    manifests=list(ROOT.glob("**/*PROJECT_MANIFEST*.md"))
    assert manifests==[ROOT/"GOLD_CONTROL_PROJECT_MANIFEST.md"]
    text=manifests[0].read_text()
    assert "**Manifest version:** 1.49" in text
    assert "`AUTO_SELECTOR = OFF`" in text
    assert "`AUTO_ENSEMBLE = OFF`" in text


def test_monthly_common_origin_alignment_and_fail_closed_pit():
    panel,meta=build_same_origin_panel()
    assert len(panel)==301 and meta["targets"]==43
    assert sorted(panel.model.unique())==sorted(BASE_MODELS)
    assert not panel.duplicated(["forecast_origin","target_month","model"]).any()
    for row in panel.itertuples():
        assert pd.Period(row.forecast_origin,freq="M")+1==pd.Period(row.target_month,freq="M")
    assert meta["all_seven_common_pit_origins"]==0
    assert set(panel.loc[panel.model.isin(["DMA","DMS","IDMA"]),"pit_status"])=={"BLOCKED_PIT"}


def test_short_inventory_and_no_silent_blocks():
    inv=inventory()
    assert inv["origins"]==400
    assert inv["targets"]["NEXT_NY17_1D"]==399
    assert inv["targets"]["NEXT_NY17_3D"]==397
    assert inv["targets"]["TODAY_TO_NY17"]=="BLOCKED_CONTRACT"
    assert inv["blocks"]["1"]["status"].startswith("BLOCKED_")
    assert inv["blocks"]["2"]["status"].startswith("BLOCKED_")
    assert inv["blocks"]["3"]["status"].startswith("BLOCKED_")
    assert inv["blocks"]["5"]["status"].startswith("BLOCKED_")


def test_target_clock_and_3d_maturity():
    d=load_features(); y1,r1=target_arrays(d,1); y3,r3=target_arrays(d,3)
    assert y1.notna().sum()==399 and y3.notna().sum()==397
    for t in [100,240,399]:
        assert all(j+3<=t for j in range(t) if j+3<=t)
    assert np.isclose(r3.iloc[20],np.log(d.close.iloc[23]/d.close.iloc[20]))


def test_prefix_invariance_and_determinism_on_parsimonious_path():
    d=load_features(); config=[("LOGISTIC_C1","LOGISTIC",{"C":1.0})]
    a,_,_,_=raw_paths(d,1,[0],end_index=132,configs=config)
    b,_,_,_=raw_paths(d.iloc[:150].copy(),1,[0],end_index=132,configs=config)
    c,_,_,_=raw_paths(d,1,[0],end_index=132,configs=config)
    assert a==b==c


def test_candidate_freeze_precedes_outer_and_authority_closed():
    freeze=json.loads((ROOT/"v149_research/contracts/limited_candidate_freeze_v149.json").read_text())
    assert freeze["frozen_before_outer_scoring"] is True
    assert freeze["auto_selector"]=="OFF" and freeze["auto_ensemble"]=="OFF"
    assert freeze["production_authority"] is False
    assert freeze["short_horizon"]["NEXT_NY17_1D"]["outer_start_index"]==240
    assert freeze["short_horizon"]["NEXT_NY17_3D"]["outer_start_index"]==240
    assert set(freeze["short_model_configs"])=={"LOGISTIC_C0.1","LOGISTIC_C1","LOGISTIC_C10","GBRT_D1","GBRT_D2","HISTGB_D2","HISTGB_D3"}


def test_outer_evidence_is_research_only_and_fail_closed():
    result=json.loads((ROOT/"data_pipeline/audits/v149_research/v149_outer_results.json").read_text())
    assert result["evidence_class"]=="RETROSPECTIVE_RESEARCH_DIAGNOSTIC_NOT_PROSPECTIVE"
    assert result["production_authority"] is False
    assert result["production_writes"]=="NONE"
    assert result["auto_selector"]=="OFF" and result["auto_ensemble"]=="OFF"
    assert result["monthly"]["promotion"]=="NOT_PROVEN"
    assert result["monthly"]["all_seven_architecture"]=="BLOCKED_PIT"
    assert result["monthly"]["superior_set"]["formal_hansen_mcs"]=="NOT_PROVEN"
    for horizon in ["NEXT_NY17_1D","NEXT_NY17_3D"]:
        assert result["short_horizon"][horizon]["promotion"]=="NOT_PROVEN"


def test_outer_origin_maturity_and_expected_deterministic_hashes():
    result=json.loads((ROOT/"data_pipeline/audits/v149_research/v149_outer_results.json").read_text())
    assert result["output_hashes"]=={
        "monthly":"91ab3fd7a56411572d626e09f74d01467b3fb61becd1d9bffdb30ec2a4eebdf5",
        "NEXT_NY17_1D":"00a0e8130ebf2db72a364a715fad8572774d913cf532433b9516ed65961b50b5",
        "NEXT_NY17_3D":"ec0729a57c10e4738083e929b1f2297c5218613dfe26e8c2bab1877051c4ebc9",
    }
    one=pd.read_csv(ROOT/"data_pipeline/audits/v149_research/next_ny17_1d_outer_v149.csv",parse_dates=["origin_date","target_date"])
    three=pd.read_csv(ROOT/"data_pipeline/audits/v149_research/next_ny17_3d_outer_v149.csv",parse_dates=["origin_date","target_date"])
    assert len(one)==159 and len(three)==157
    assert (one.target_date>one.origin_date).all()
    assert (three.target_date>three.origin_date).all()
    governed_dates=load_features().date.dt.strftime("%Y-%m-%d").tolist()
    assert all(
        row.target_date.strftime("%Y-%m-%d")==governed_dates[row.origin_index+3]
        for row in three.itertuples()
    )


def test_calibration_is_prior_only_and_no_candidate_was_added_post_freeze():
    freeze=json.loads((ROOT/"v149_research/contracts/limited_candidate_freeze_v149.json").read_text())
    configured=set(freeze["short_model_configs"])
    for horizon in ["next_ny17_1d","next_ny17_3d"]:
        frame=pd.read_csv(ROOT/f"data_pipeline/audits/v149_research/{horizon}_outer_v149.csv")
        assert frame.calibration_n.min()>=40
        assert set(frame.probability_config).issubset(configured)
        assert set(frame.return_config).issubset(configured)
        assert (frame.origin_index>frame.calibration_n).all()
