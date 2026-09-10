from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/"data_pipeline/audits/hs_sdl_dma_replay_v1/hs_sdl_dma_replay_v1.json"


def test_unpromoted_horizons_cannot_publish_dashboard_probability():
    x=json.loads(EVIDENCE.read_text())
    for row in x["horizons"].values():
        assert row["promotion"]["status"]=="NOT_PROVEN"
    assert x["production_authority"] is False
    assert x["auto_selector"]=="OFF"
    assert x["auto_ensemble"]=="OFF"


def test_evidence_label_is_not_prospective():
    x=json.loads(EVIDENCE.read_text())
    assert x["prospective_claim"] is False
    assert x["evidence_class"]=="RETROSPECTIVE_PSEUDO_REAL_TIME_RESEARCH"
