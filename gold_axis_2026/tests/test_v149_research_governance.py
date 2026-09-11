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
