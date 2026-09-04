from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "GOLD_CONTROL_PROJECT_MANIFEST.md"
APP = ROOT / "apps" / "gold_control_mobile_v1.py"


def test_v132_is_the_single_current_project_manifest():
    text = MANIFEST.read_text(encoding="utf-8")
    assert "**Manifest version:** 1.32" in text
    assert "only canonical Gold Control project manifest" in text
    candidates = sorted(ROOT.glob("*PROJECT_MANIFEST*.md"))
    assert candidates == [MANIFEST]
    assert "FILE_MANIFEST_SHA256.txt" in text
    assert "not** the Gold Control project decision manifest" in text


def test_month_end_origin_maps_to_immediately_following_month():
    text = MANIFEST.read_text(encoding="utf-8")
    assert "2026-08-31 | **September 2026**" in text
    assert "2026-09-30 | **October 2026**" in text
    assert "31 Aug 2026 → September 2026 forecast/direction reference" in text
    assert "30 Sep 2026 → October 2026 forecast/direction reference" in text
    assert "There is no rule that September forecast motors should remain blank until 30 September" in text


def test_september_origin_values_are_frozen_without_selector():
    text = MANIFEST.read_text(encoding="utf-8")
    for token in (
        "4345.814584037808 USD/oz",
        "4397.305673870967 USD/oz",
        "4452.046728838838 USD/oz",
        "`DOWN`",
        "`ROBUST_UP`",
        "`NEUTRAL`",
        "`OFF`",
        "`NO_ADVERSE_BREAK_CANDIDATE`",
        "AUTO_SELECTOR = OFF",
        "AUTO_ENSEMBLE = OFF",
        "NOT_PROVEN_EXPERT_SELECTION_RULE",
        "NOT_PROVEN_POSITION_MAPPING",
    ):
        assert token in text


def test_ui_primary_semantics_are_origin_first_and_audit_is_secondary():
    text = APP.read_text(encoding="utf-8")
    assert 'hero_kicker="EYLÜL 2026 · 31 AĞUSTOS ORIGIN"' in text
    assert 'direction_label="EYLÜL AY-AÇILIŞ YÖN MOTORLARI"' in text
    assert 'origin_label="ORIGIN BOUNDARY"' in text
    assert 'badge="31 AĞUSTOS ORIGIN · RECONSTRUCTION"' in text
    assert 'hero_title=f"{mom_value} / {rw_value} / {patch_value} USD"' in text
    assert "3M Momentum / Random Walk / Causal Patch" in text
    assert "4 Eylül'de 31 Ağustos bilgi sınırıyla yeniden hesaplandı" in text
    assert "ORIGIN_RECONSTRUCTION / HISTORICAL_REPLAY" in text
    assert "30 Eylül origin → Ekim 2026" in text
    assert "EYLÜL 2026 HISTORICAL REPLAY" not in text


def test_reconstruction_does_not_claim_backdated_issuance():
    text = MANIFEST.read_text(encoding="utf-8")
    assert "must **not** say or imply `issued on 31-Aug`" in text
    assert "No historical timestamp may be rewritten" in text
    assert "monthly_forecast_contracts = 0" in text
    assert "decision_signal_snapshots = 0" in text
    assert "decision_runs = 0" in text
    assert "decision_events = 0" in text
