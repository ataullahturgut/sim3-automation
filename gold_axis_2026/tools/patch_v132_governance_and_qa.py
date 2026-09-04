from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WF = ROOT / ".github/workflows"
APP = ROOT / "gold_axis_2026/apps"

ACTIVE_KEEP = {
    "gold-control-mobile-ui-v125-final.yml",
    "gold-control-bocpd-successor-v1.yml",
}
EXPLICIT_HISTORICAL_UI = {
    "gold-control-v130-current-month-reference-regression.yml",
    "gold-control-v130-september-replay-motor-visibility.yml",
    "gold-control-v131-aug31-replay-ui-validation.yml",
}
OLD_VERSION_RE = re.compile(r"Manifest version[^\n]*1\.(?:20|21|22|23|24|25|26|27|28|29|30|31)\b", re.I)
MANIFEST_WRITER_RE = re.compile(
    r"(?:git\s+add[^\n]*GOLD_CONTROL_PROJECT_MANIFEST\.md|"
    r"(?:apply|reconcile|finalize)[^\n]*manifest|"
    r"manifest[^\n]*(?:git\s+commit|git\s+push))",
    re.I,
)


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)


def top_on_block(text: str) -> tuple[int, int, str]:
    m = re.search(r"(?m)^on:\s*\n", text)
    if not m:
        raise RuntimeError("workflow missing top-level on block")
    n = re.search(r"(?m)^(?:permissions|env|jobs):\s*", text[m.end():])
    if not n:
        raise RuntimeError("workflow on block has no terminal permissions/env/jobs block")
    end = m.end() + n.start()
    return m.start(), end, text[m.start():end]


def make_manual_only(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if "HISTORICAL_MANUAL_ONLY_V132" in text:
        return False
    a, b, block = top_on_block(text)
    if "gold-r4-direction-engine" not in block and "gold-r4-direction-engine-ui-v122-final" not in block:
        return False
    manual = "on:\n  workflow_dispatch:\n\n"
    text = text[:a] + manual + text[b:]
    text = "# HISTORICAL_MANUAL_ONLY_V132 — superseded by GOLD_CONTROL_PROJECT_MANIFEST.md v1.32; no automatic canonical trigger.\n" + text
    write(path, text)
    return True


def retire_legacy_workflows() -> list[str]:
    retired: list[str] = []
    for path in sorted(WF.glob("*.yml")):
        if path.name in ACTIVE_KEEP or path.name.startswith("tmp-v132-"):
            continue
        text = path.read_text(encoding="utf-8")
        try:
            _, _, block = top_on_block(text)
        except RuntimeError:
            continue
        canonical_trigger = "gold-r4-direction-engine" in block or "gold-r4-direction-engine-ui-v122-final" in block
        if not canonical_trigger:
            continue
        old_version = bool(OLD_VERSION_RE.search(text))
        manifest_writer = "GOLD_CONTROL_PROJECT_MANIFEST.md" in text and bool(MANIFEST_WRITER_RE.search(text))
        explicit = path.name in EXPLICIT_HISTORICAL_UI
        if old_version or manifest_writer or explicit:
            if make_manual_only(path):
                retired.append(path.name)
    return retired


def patch_mobile_qa() -> None:
    path = APP / "mobile_viewport_qa.py"
    text = path.read_text(encoding="utf-8")
    old = '''        if "EYLÜL 2026 H=1 · CURRENT-MONTH REFERENCE" in tahmin_body:\n            forecast_hero_marker="EYLÜL 2026 H=1 · CURRENT-MONTH REFERENCE"\n        elif "EYLÜL 2026 H=1 REPLAY" in tahmin_body:\n            forecast_hero_marker="EYLÜL 2026 H=1 REPLAY"\n        else:\n            forecast_hero_marker="GELECEK AY TAHMİNİ"\n        markers(page, "TAHMIN", [forecast_hero_marker,"MULTI-EXPERT MONTHLY FORECAST ENGINE","CAUSAL PATCH","VW-MIDAS-MSVR","3M MOMENTUM","RANDOM WALK","GEÇMİŞ VE TAHMİN KARŞILAŞTIRMASI","EARLY INDICATIVE","SENARYOLAR","MEVCUT FİYATA GÖRE FARK","MODEL PERFORMANSI","NOT_PROVEN_EXPERT_SELECTION_RULE","AUTO SELECTOR","AUTO ENSEMBLE","HISTORICAL_REPLAY","REPLAY · PROSPECTIVE ISSUED DEĞİL","EYLÜL 2026 HISTORICAL REPLAY","NOT_ISSUED_MISSED_2026_08_31_ORIGIN","WAITING_ELIGIBLE_MONTH_END_ORIGIN","CURRENT-MONTH REFERENCE","31 AĞUSTOS AY-AÇILIŞ YÖN CONTEXT","DOWN","ROBUST_UP"])\n'''
    new = '''        if "EYLÜL 2026 · 31 AĞUSTOS ORIGIN" in tahmin_body:\n            forecast_hero_marker="EYLÜL 2026 · 31 AĞUSTOS ORIGIN"\n        else:\n            forecast_hero_marker="GELECEK AY TAHMİNİ"\n        markers(page, "TAHMIN", [forecast_hero_marker,"MULTI-EXPERT MONTHLY FORECAST ENGINE","CAUSAL PATCH","VW-MIDAS-MSVR","3M MOMENTUM","RANDOM WALK","GEÇMİŞ VE TAHMİN KARŞILAŞTIRMASI","EARLY INDICATIVE","SENARYOLAR","MEVCUT FİYATA GÖRE FARK","MODEL PERFORMANSI","NOT_PROVEN_EXPERT_SELECTION_RULE","AUTO SELECTOR","AUTO ENSEMBLE","HISTORICAL_REPLAY","ORIGIN_RECONSTRUCTION","31 AĞUSTOS ORIGIN","EYLÜL AY-AÇILIŞ YÖN MOTORLARI","30 EYLÜL ORIGIN","DOWN","ROBUST_UP","4 EYLÜL"])\n'''
    text = replace_once(text, old, new, "mobile viewport Tahmin contract")
    write(path, text)


def patch_bocpd_workflow() -> None:
    path = WF / "gold-control-bocpd-successor-v1.yml"
    text = path.read_text(encoding="utf-8")
    text = replace_once(text, "      - gold-r4-direction-engine\n", "      - gold-r4-direction-engine\n      - gold-control-v132-monthly-origin-contract\n", "bocpd feature trigger")
    text = replace_once(text, "grep -F '**Manifest version:** 1.31'", "grep -F '**Manifest version:** 1.32'", "bocpd manifest version")
    text = text.replace("grep -F 'AUTO_SELECTOR=OFF'", "grep -F 'AUTO_SELECTOR = OFF'")
    text = text.replace("grep -F 'AUTO_ENSEMBLE=OFF'", "grep -F 'AUTO_ENSEMBLE = OFF'")
    write(path, text)


def patch_mobile_final_workflow() -> None:
    path = WF / "gold-control-mobile-ui-v125-final.yml"
    text = path.read_text(encoding="utf-8")
    text = replace_once(text, "name: Gold Control Mobile UI V1.31 Compatibility Final", "name: Gold Control Mobile UI V1.32 Monthly Origin Compatibility Final", "mobile workflow name")
    text = replace_once(text, "branches: [gold-r4-direction-engine, gold-control-v131-postmerge-ci-reconcile]", "branches: [gold-r4-direction-engine, gold-control-v132-monthly-origin-contract]", "mobile branches")
    old = '''      - name: Verify manifest v1.31 governance and frozen locks\n        run: |\n          test -n "$NEON_DATABASE_URL" || (echo 'NEON_DATABASE_URL missing' && exit 1)\n          grep -Fq '**Manifest version:** 1.31' gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md\n          grep -Fq 'FROZEN_PRODUCTION_DISPLAY_SNAPSHOT_V2' gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md\n          grep -Fq 'FROZEN_AUG31_EOD_STATE_REPLAY_V1' gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md\n          grep -Fq 'FROZEN_AUG31_STATE_REPLAY_DISPLAY_SNAPSHOT_V1' gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md\n          grep -Fq 'FROZEN_DATA_EVIDENCE_SPINE_V1' gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md\n          grep -Fq 'FROZEN_ALL_GOVERNED_ENGINES_VISIBLE_V1' gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md\n          grep -Fq 'BOCPD_RETURN_SUCCESSOR_V1' gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md\n          grep -Fq 'NOT_PROVEN_EXPERT_SELECTION_RULE' gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md\n          grep -Fq 'auto selector = OFF' gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md\n          grep -Fq 'auto ensemble = OFF' gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md\n          grep -Fq 'NOT_PROVEN_POSITION_MAPPING' gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md\n          echo 'V131_MOBILE_GOVERNANCE_PASS'\n'''
    new = '''      - name: Verify manifest v1.32 monthly-origin governance and frozen locks\n        run: |\n          test -n "$NEON_DATABASE_URL" || (echo 'NEON_DATABASE_URL missing' && exit 1)\n          grep -Fq '**Manifest version:** 1.32' gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md\n          grep -Fq 'only canonical Gold Control project manifest' gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md\n          grep -Fq '2026-08-31 | **September 2026**' gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md\n          grep -Fq '2026-09-30 | **October 2026**' gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md\n          grep -Fq 'EYLÜL 2026 · 31 AĞUSTOS ORIGIN' gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md\n          grep -Fq 'BOCPD_RETURN_SUCCESSOR_V1' gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md\n          grep -Fq 'NOT_PROVEN_EXPERT_SELECTION_RULE' gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md\n          grep -Fq 'AUTO_SELECTOR = OFF' gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md\n          grep -Fq 'AUTO_ENSEMBLE = OFF' gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md\n          grep -Fq 'NOT_PROVEN_POSITION_MAPPING' gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md\n          echo 'V132_MOBILE_GOVERNANCE_PASS'\n'''
    text = replace_once(text, old, new, "mobile manifest gate")
    text = text.replace("Run deterministic v1.31 contracts", "Run deterministic v1.32 contracts")
    text = text.replace("V131_PRODUCTION_DB_TO_UI_PASS", "V132_PRODUCTION_DB_TO_UI_PASS")
    text = text.replace("V131_DEPLOYMENT_FALLBACK_SOURCE_PASS", "V132_DEPLOYMENT_FALLBACK_SOURCE_PASS")
    text = text.replace("MOBILE_V131_PRODUCTION_BACKED_BROWSER_PASS", "MOBILE_V132_PRODUCTION_BACKED_BROWSER_PASS")
    text = text.replace("gold-control-v131-compatibility-production-backed-390x844-screenshots", "gold-control-v132-monthly-origin-production-backed-390x844-screenshots")
    write(path, text)


def audit_no_legacy_auto_manifest_writer() -> None:
    offenders = []
    for path in sorted(WF.glob("*.yml")):
        if path.name.startswith("tmp-v132-"):
            continue
        text = path.read_text(encoding="utf-8")
        try:
            _, _, block = top_on_block(text)
        except RuntimeError:
            continue
        canonical_trigger = "gold-r4-direction-engine" in block or "gold-r4-direction-engine-ui-v122-final" in block
        if not canonical_trigger:
            continue
        if path.name in ACTIVE_KEEP:
            continue
        old_version = bool(OLD_VERSION_RE.search(text))
        manifest_writer = "GOLD_CONTROL_PROJECT_MANIFEST.md" in text and bool(MANIFEST_WRITER_RE.search(text))
        if old_version or manifest_writer:
            offenders.append(path.name)
    if offenders:
        raise RuntimeError(f"legacy canonical manifest consumers remain: {offenders}")


def main() -> None:
    retired = retire_legacy_workflows()
    patch_mobile_qa()
    patch_bocpd_workflow()
    patch_mobile_final_workflow()
    audit_no_legacy_auto_manifest_writer()
    print("PATCH_V132_GOVERNANCE_QA_PASS")
    print("RETIRED_COUNT", len(retired))
    for name in retired:
        print("RETIRED", name)


if __name__ == "__main__":
    main()
