from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "apps" / "gold_control_mobile_v1.py"
MANIFEST = ROOT / "GOLD_CONTROL_PROJECT_MANIFEST.md"
MARKER = ROOT / "apps" / "replay_fallback_fix_marker.tmp"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"EXPECTED_ONE_MATCH:{path}:{n}:{old}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> int:
    replace_once(
        APP,
        '    historical_replay_experts=safe_call(lambda:get_latest_experts_cached(url,TRACK_HISTORICAL_REPLAY),[]) if url else []',
        '    historical_replay_experts=safe_call(lambda:get_latest_experts_cached(url,TRACK_HISTORICAL_REPLAY),[])',
    )
    replace_once(
        APP,
        '    historical_replay_history=safe_call(lambda:get_expert_history_cached(url,TRACK_HISTORICAL_REPLAY),[]) if url else []',
        '    historical_replay_history=safe_call(lambda:get_expert_history_cached(url,TRACK_HISTORICAL_REPLAY),[])',
    )

    text = MANIFEST.read_text(encoding="utf-8")
    if "FROZEN_PRODUCTION_DISPLAY_SNAPSHOT_V2" not in text:
        if text.count("**Manifest version:** 1.27") != 1:
            raise RuntimeError("MANIFEST_127_HEADER_NOT_UNIQUE")
        text = text.replace("**Manifest version:** 1.27", "**Manifest version:** 1.29", 1)
        text += '''\n\n## v1.29 — Deployment Replay Snapshot Closure\n\n- Frozen marker: `FROZEN_PRODUCTION_DISPLAY_SNAPSHOT_V2`.\n- Root cause closed: a hosting instance without `NEON_DATABASE_URL` previously received stored direction/risk context from the display snapshot but historical replay readers returned an empty list.\n- V2 extends the display-only snapshot with governed `HISTORICAL_REPLAY` expert rows.\n- Replay rows must remain `canonical_authority=false`, `prospective_claim=false`, `direction_vote_permitted=false`, selector `NOT_PROVEN_EXPERT_SELECTION_RULE`, auto selector OFF and auto ensemble OFF.\n- Mobile Tahmin/Geçmiş replay reads are no longer skipped when the DB URL is absent; only the validated V2 snapshot may satisfy that fallback.\n- MONTH_END_EXPERT and EARLY_INDICATIVE remain empty when not genuinely issued; snapshot replay never populates those tracks.\n- Canonical forecast, Decision Store and position/action mapping remain unchanged and locked.\n- Required deployment acceptance: with `NEON_DATABASE_URL` deliberately absent, the 390×844 Tahmin screen must visibly render the production replay values for the available replay experts and the `REPLAY · PROSPECTIVE DEĞİL` marker.\n'''
        MANIFEST.write_text(text, encoding="utf-8")

    if MARKER.exists():
        MARKER.unlink()
    print("REPLAY_SNAPSHOT_FALLBACK_V129_PATCH_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
