from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GOLD = ROOT / "gold_axis_2026"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"EXPECTED_EXACTLY_ONE_MATCH:{path}:{count}:{old[:120]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def patch_app() -> None:
    path = GOLD / "apps" / "gold_control_mobile_v1.py"
    old = '''    direction_summary=(
        "<div class='gc-card gc-direction-summary'><div class='gc-section-title'>YÖN MOTORLARI ÖZETİ · STORED CONTEXT</div>"
        +"<div class='gc-grid4'>"
        +mini_card("MONTHLY 3M",f"{ma} {display_state(monthly,'YAYIMLANMADI')}","Stratejik monthly prior",tone_class(mt))
        +mini_card("FAST",f"{fa} {display_state(fast_value,'YAYIMLANMADI')}","Taktik yön teyidi",tone_class(ft))
        +mini_card("SLOW",f"{sa} {display_state(slow_value,'YAYIMLANMADI')}","Orta hız yön teyidi",tone_class(stn))
        +mini_card("GVZ RİSK",stored_risk,"Risk-only · yön oyu değildir")
        +"</div><div class='gc-footnote' style='margin-top:.55rem'>Bu özet seçim/ensemble değildir; yalnız persisted motor context'ini görünür kılar.</div></div>"
    )
'''
    new = '''    direction_summary=(
        "<div class='gc-card gc-direction-summary' style='padding:.62rem .68rem;margin:.42rem 0'>"
        +"<div class='gc-section-title' style='margin-bottom:.42rem'>YÖN MOTORLARI ÖZETİ · STORED CONTEXT</div>"
        +"<div class='gc-direction-strip' style='display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:.36rem'>"
        +f"<div class='gc-direction-cell' style='min-width:0;border:1px solid var(--gc-line);border-radius:12px;padding:.52rem .42rem;text-align:center'><div style='font-size:.59rem;font-weight:900;color:var(--gc-muted)'>MONTHLY 3M</div><div class='{tone_class(mt)}' style='font-size:.95rem;font-weight:900;margin:.22rem 0'>{esc(ma)} {esc(display_state(monthly,'YAYIMLANMADI'))}</div><div style='font-size:.56rem;color:var(--gc-muted)'>Stratejik prior</div></div>"
        +f"<div class='gc-direction-cell' style='min-width:0;border:1px solid var(--gc-line);border-radius:12px;padding:.52rem .42rem;text-align:center'><div style='font-size:.59rem;font-weight:900;color:var(--gc-muted)'>FAST</div><div class='{tone_class(ft)}' style='font-size:.95rem;font-weight:900;margin:.22rem 0'>{esc(fa)} {esc(display_state(fast_value,'YAYIMLANMADI'))}</div><div style='font-size:.56rem;color:var(--gc-muted)'>Taktik teyit</div></div>"
        +f"<div class='gc-direction-cell' style='min-width:0;border:1px solid var(--gc-line);border-radius:12px;padding:.52rem .42rem;text-align:center'><div style='font-size:.59rem;font-weight:900;color:var(--gc-muted)'>SLOW</div><div class='{tone_class(stn)}' style='font-size:.95rem;font-weight:900;margin:.22rem 0'>{esc(sa)} {esc(display_state(slow_value,'YAYIMLANMADI'))}</div><div style='font-size:.56rem;color:var(--gc-muted)'>Orta hız teyidi</div></div>"
        +"</div><div class='gc-footnote' style='margin-top:.38rem'>Persisted context · selector/ensemble değildir. GVZ risk-only olarak aşağıdaki risk bölümünde kalır.</div></div>"
    )
'''
    replace_once(path, old, new)


def patch_qa() -> None:
    path = GOLD / "apps" / "mobile_viewport_qa.py"
    old = '''    cards = summary.locator(".gc-mini")
    if cards.count() != 4:
        raise AssertionError(f"DIRECTION_SUMMARY_CARD_COUNT:{cards.count()}:4")
    for label in ("MONTHLY 3M", "FAST", "SLOW"):
        card = cards.filter(has_text=re.compile(re.escape(label), re.I))
        if card.count() != 1:
            raise AssertionError(f"DIRECTION_SUMMARY_ENGINE_COUNT:{label}:{card.count()}:1")
        value = norm(card.first.locator(".value").inner_text().strip())
        if value in {"", "—", "YAYIMLANMADI", "NOT_ISSUED"}:
            raise AssertionError(f"DIRECTION_SUMMARY_VALUE_MISSING:{label}:{value}")
        card_box = card.first.bounding_box()
        if not card_box or card_box["y"] + card_box["height"] > nav_box["y"] - 4:
            raise AssertionError(f"DIRECTION_SUMMARY_ENGINE_NOT_VISIBLE:{label}:{card_box}:{nav_box}")
'''
    new = '''    cards = summary.locator(".gc-direction-cell")
    if cards.count() != 3:
        raise AssertionError(f"DIRECTION_SUMMARY_CARD_COUNT:{cards.count()}:3")
    for label in ("MONTHLY 3M", "FAST", "SLOW"):
        card = cards.filter(has_text=re.compile(re.escape(label), re.I))
        if card.count() != 1:
            raise AssertionError(f"DIRECTION_SUMMARY_ENGINE_COUNT:{label}:{card.count()}:1")
        value_text = norm(card.first.inner_text().strip())
        if not any(token in value_text for token in ("UP", "DOWN", "NEUTRAL", "ROBUST")):
            raise AssertionError(f"DIRECTION_SUMMARY_VALUE_MISSING:{label}:{value_text}")
        card_box = card.first.bounding_box()
        if not card_box or card_box["y"] + card_box["height"] > nav_box["y"] - 4:
            raise AssertionError(f"DIRECTION_SUMMARY_ENGINE_NOT_VISIBLE:{label}:{card_box}:{nav_box}")
'''
    replace_once(path, old, new)


def main() -> None:
    patch_app()
    patch_qa()
    print("DIRECTION_SUMMARY_COMPACT_V123_PATCH_PASS")


if __name__ == "__main__":
    main()
