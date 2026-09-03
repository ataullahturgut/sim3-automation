from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GOLD = ROOT / "gold_axis_2026"


def insert_before_once(path: Path, marker: str, addition: str) -> None:
    text = path.read_text(encoding="utf-8")
    if addition.strip() in text:
        raise RuntimeError(f"PATCH_ALREADY_PRESENT:{path}")
    count = text.count(marker)
    if count != 1:
        raise RuntimeError(f"EXPECTED_EXACTLY_ONE_MARKER:{path}:{count}:{marker[:100]!r}")
    path.write_text(text.replace(marker, addition + marker, 1), encoding="utf-8")


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"EXPECTED_EXACTLY_ONE_MATCH:{path}:{count}:{old[:100]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def patch_app() -> None:
    path = GOLD / "apps" / "gold_control_mobile_v1.py"
    marker = "    inventory_summary=(\n"
    addition = '''    fast_value=None if not decision else decision.get("fast_state")
    slow_value=None if not decision else decision.get("slow_state")
    fa,ft=arrow_state(fast_value); sa,stn=arrow_state(slow_value)
    direction_summary=(
        "<div class='gc-card gc-direction-summary'><div class='gc-section-title'>YÖN MOTORLARI ÖZETİ · STORED CONTEXT</div>"
        +"<div class='gc-grid4'>"
        +mini_card("MONTHLY 3M",f"{ma} {display_state(monthly,'YAYIMLANMADI')}","Stratejik monthly prior",tone_class(mt))
        +mini_card("FAST",f"{fa} {display_state(fast_value,'YAYIMLANMADI')}","Taktik yön teyidi",tone_class(ft))
        +mini_card("SLOW",f"{sa} {display_state(slow_value,'YAYIMLANMADI')}","Orta hız yön teyidi",tone_class(stn))
        +mini_card("GVZ RİSK",stored_risk,"Risk-only · yön oyu değildir")
        +"</div><div class='gc-footnote' style='margin-top:.55rem'>Bu özet seçim/ensemble değildir; yalnız persisted motor context'ini görünür kılar.</div></div>"
    )
    st.markdown(direction_summary,unsafe_allow_html=True)
'''
    insert_before_once(path, marker, addition)


def patch_qa() -> None:
    path = GOLD / "apps" / "mobile_viewport_qa.py"
    marker = "\ndef main() -> int:\n"
    addition = '''\ndef assert_direction_summary_above_fold(page: Page) -> None:
    summary = page.locator(".gc-direction-summary")
    if summary.count() != 1 or not summary.first.is_visible():
        raise AssertionError(f"DIRECTION_SUMMARY_COUNT:{summary.count()}:1")
    box = summary.first.bounding_box()
    nav_box = page.locator(f'{MAIN_NAV} [data-testid="stRadio"]').first.bounding_box()
    if not box or not nav_box:
        raise AssertionError(f"DIRECTION_SUMMARY_BOUNDS:{box}:{nav_box}")
    if box["y"] < 0 or box["y"] + box["height"] > nav_box["y"] - 4:
        raise AssertionError(f"DIRECTION_SUMMARY_NOT_ABOVE_FOLD:{box}:{nav_box}")
    cards = summary.locator(".gc-mini")
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
    insert_before_once(path, marker, addition)

    replace_once(
        path,
        '            "MEVCUT KAYITLI DURUM","TÜM TAHMİN VE YÖN MOTORLARI",\n',
        '            "MEVCUT KAYITLI DURUM","YÖN MOTORLARI ÖZETİ · STORED CONTEXT","TÜM TAHMİN VE YÖN MOTORLARI",\n',
    )
    replace_once(
        path,
        '        engine_cards = page.locator(".gc-expert")\n',
        '        assert_direction_summary_above_fold(page)\n        engine_cards = page.locator(".gc-expert")\n',
    )
    replace_once(
        path,
        '        ordered(page, "GORUNUM", ["TÜM TAHMİN VE YÖN MOTORLARI","SİNYAL ÖZETİ","MODEL YÖNÜ (AYLIK)","FAST / SLOW TEYİDİ","RİSK SEVİYESİ","SİNYAL ZAMAN ÇİZELGESİ","EMERGENCY DURUMU","SİSTEM YORUMU"])\n',
        '        ordered(page, "GORUNUM", ["YÖN MOTORLARI ÖZETİ · STORED CONTEXT","TÜM TAHMİN VE YÖN MOTORLARI","SİNYAL ÖZETİ","MODEL YÖNÜ (AYLIK)","FAST / SLOW TEYİDİ","RİSK SEVİYESİ","SİNYAL ZAMAN ÇİZELGESİ","EMERGENCY DURUMU","SİSTEM YORUMU"])\n',
    )
    replace_once(
        path,
        '    print("MOBILE_V123_ALL_ENGINE_FINAL_MOCKUP_VIEWPORT_QA_PASS"); print("ENGINE_INVENTORY_VISIBLE=12/12"); print("DIRECTION_CONTEXT_VISIBLE=3/3"); print(f"VIEWPORT={PHONE_WIDTH}x{PHONE_HEIGHT}"); print(f"SCREENSHOTS={out}"); return 0\n',
        '    print("MOBILE_V123_ALL_ENGINE_FINAL_MOCKUP_VIEWPORT_QA_PASS"); print("ENGINE_INVENTORY_VISIBLE=12/12"); print("DIRECTION_CONTEXT_VISIBLE=3/3"); print("DIRECTION_SUMMARY_ABOVE_FOLD=3/3"); print(f"VIEWPORT={PHONE_WIDTH}x{PHONE_HEIGHT}"); print(f"SCREENSHOTS={out}"); return 0\n',
    )


def main() -> None:
    patch_app()
    patch_qa()
    print("DIRECTION_SUMMARY_V123_PATCH_PASS")


if __name__ == "__main__":
    main()
