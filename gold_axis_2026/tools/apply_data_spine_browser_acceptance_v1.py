from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "apps" / "mobile_viewport_qa.py"


def replace_once(text: str, old: str, new: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"EXPECTED_EXACTLY_ONE_MATCH:{n}:{old[:120]!r}")
    return text.replace(old, new, 1)


def main() -> int:
    text = QA.read_text(encoding="utf-8")
    text = replace_once(
        text,
        '            "NOT_PROVEN_EXPERT_SELECTION_RULE","AUTO SELECTOR","AUTO ENSEMBLE"\n',
        '            "NOT_PROVEN_EXPERT_SELECTION_RULE","AUTO SELECTOR","AUTO ENSEMBLE",\n            "DB Evidence Spine: runtime 12/12","context link 7/7","integrity PASS"\n',
    )
    text = replace_once(
        text,
        '    print("MOBILE_V123_ALL_ENGINE_FINAL_MOCKUP_VIEWPORT_QA_PASS"); print("ENGINE_INVENTORY_VISIBLE=12/12"); print("DIRECTION_CONTEXT_VISIBLE=3/3"); print("DIRECTION_SUMMARY_ABOVE_FOLD=3/3"); print(f"VIEWPORT={PHONE_WIDTH}x{PHONE_HEIGHT}"); print(f"SCREENSHOTS={out}"); return 0\n',
        '    print("MOBILE_V123_ALL_ENGINE_FINAL_MOCKUP_VIEWPORT_QA_PASS"); print("ENGINE_INVENTORY_VISIBLE=12/12"); print("DIRECTION_CONTEXT_VISIBLE=3/3"); print("DIRECTION_SUMMARY_ABOVE_FOLD=3/3"); print("DATA_EVIDENCE_SPINE_UI_VISIBLE=12/12:7/7:PASS"); print(f"VIEWPORT={PHONE_WIDTH}x{PHONE_HEIGHT}"); print(f"SCREENSHOTS={out}"); return 0\n',
    )
    QA.write_text(text, encoding="utf-8")
    print("DATA_SPINE_BROWSER_ACCEPTANCE_V1_PATCH_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
