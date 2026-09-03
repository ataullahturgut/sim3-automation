from __future__ import annotations

import argparse
import re
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

PHONE_WIDTH, PHONE_HEIGHT = 390, 844
MAIN_NAV = ".st-key-gc_main_nav"
MARKET_RANGE = ".st-key-gc_market_range"


def norm(s: str) -> str:
    return s.upper().replace("İ", "I")


def body(page: Page) -> str:
    return norm(page.locator("body").inner_text())


def no_exception(page: Page, screen: str) -> None:
    nodes = page.locator('[data-testid="stException"]')
    if nodes.count() and nodes.first.is_visible():
        raise AssertionError(f"STREAMLIT_EXCEPTION_VISIBLE:{screen}:{nodes.first.inner_text()[:500]}")
    text = body(page)
    for marker in ("THIS APP HAS ENCOUNTERED AN ERROR", "IMPORTERROR", "MODULENOTFOUNDERROR", "TRACEBACK (MOST RECENT CALL LAST)"):
        if marker in text:
            raise AssertionError(f"STREAMLIT_FATAL_MARKER_VISIBLE:{screen}:{marker}")


def no_overflow(page: Page, screen: str) -> None:
    d = page.evaluate("() => ({w:innerWidth,d:document.documentElement.scrollWidth,b:document.body.scrollWidth})")
    if max(int(d["d"]), int(d["b"])) > int(d["w"]) + 4:
        raise AssertionError(f"MOBILE_HORIZONTAL_OVERFLOW:{screen}:{d}")


def nav_label(page: Page, name: str):
    root = page.locator(MAIN_NAV); root.first.wait_for(state="attached", timeout=30_000)
    labels = root.locator('label[data-testid="stRadioOption"]').filter(has_text=re.compile(re.escape(name), re.I))
    for i in range(min(labels.count(), 8)):
        if labels.nth(i).is_visible():
            return labels.nth(i)
    return None


def segmented(page: Page, selector: str, count: int, name: str) -> None:
    root = page.locator(selector); root.first.wait_for(state="attached", timeout=30_000)
    last_count = -1
    last_widths: list[float] = []
    last_selected = -1
    for _ in range(48):
        opts = root.locator('label[data-testid="stRadioOption"]')
        last_count = opts.count()
        widths: list[float] = []
        visible = last_count == count
        if visible:
            for i in range(count):
                opt = opts.nth(i)
                box = opt.bounding_box() if opt.is_visible() else None
                if not box:
                    visible = False
                    break
                widths.append(float(box["width"]))
        last_widths = widths
        last_selected = root.locator('label[data-testid="stRadioOption"][data-selected="true"]').count()
        if visible and len(widths) == count and max(widths) - min(widths) <= 3 and last_selected == 1:
            return
        page.wait_for_timeout(250)
    if last_count != count:
        raise AssertionError(f"{name}_OPTION_COUNT:{last_count}:{count}")
    if len(last_widths) != count:
        raise AssertionError(f"{name}_OPTION_NOT_VISIBLE:{last_widths}")
    if max(last_widths) - min(last_widths) > 3:
        raise AssertionError(f"{name}_UNEQUAL_WIDTHS:{last_widths}")
    raise AssertionError(f"{name}_SELECTED_COUNT:{last_selected}:1")


def bottom_nav_ok(page: Page) -> None:
    for label in ("Bugün", "Görünüm", "Tahmin", "Geçmiş"):
        if nav_label(page, label) is None:
            raise AssertionError(f"MOBILE_BOTTOM_NAV_MISSING:{label}")
    box = page.locator(f'{MAIN_NAV} [data-testid="stRadio"]').first.bounding_box(); vp = page.viewport_size
    if not box or not vp or box["x"] < -1 or box["x"] + box["width"] > vp["width"] + 1 or box["y"] + box["height"] > vp["height"] + 1:
        raise AssertionError(f"MOBILE_BOTTOM_NAV_BOUNDS:{box}:{vp}")


def no_tooltip(page: Page) -> None:
    nodes = page.locator(".vg-tooltip, #vg-tooltip-element")
    for i in range(min(nodes.count(), 8)):
        if nodes.nth(i).is_visible():
            raise AssertionError("CHART_TOOLTIP_VISIBLE")


def click(page: Page, name: str) -> None:
    target = nav_label(page, name)
    if target is None:
        raise AssertionError(f"MOBILE_TAB_CONTROL_NOT_FOUND:{name}")
    target.click(); page.wait_for_timeout(1200)


def markers(page: Page, screen: str, required: list[str]) -> None:
    text = body(page)
    for marker in required:
        if norm(marker) not in text:
            raise AssertionError(f"{screen}_FINAL_MARKER_MISSING:{marker}")


def marker_y(page: Page, marker: str) -> float:
    want = norm(marker)
    headings = page.locator(".gc-section-title")
    for i in range(min(headings.count(), 64)):
        node = headings.nth(i)
        if node.is_visible() and want in norm(node.inner_text()):
            box = node.bounding_box()
            if box:
                return float(box["y"])
    candidates = page.get_by_text(marker, exact=False)
    for i in range(min(candidates.count(), 16)):
        node = candidates.nth(i)
        if node.is_visible() and node.bounding_box():
            return float(node.bounding_box()["y"])
    raise AssertionError(f"VISIBLE_MARKER_NOT_FOUND:{marker}")


def ordered(page: Page, screen: str, required: list[str]) -> None:
    pos = [(m, marker_y(page, m)) for m in required]
    ys = [y for _, y in pos]
    if any(b <= a for a, b in zip(ys, ys[1:])):
        raise AssertionError(f"{screen}_VERTICAL_ORDER_MISMATCH:{pos}")


def columns(page: Page, selector: str) -> int:
    node = page.locator(selector).first
    if not node.count() or not node.is_visible():
        raise AssertionError(f"GRID_NOT_VISIBLE:{selector}")
    return len(str(node.evaluate("el => getComputedStyle(el).gridTemplateColumns")).split())


def shot(page: Page, out: Path, name: str) -> None:
    page.screenshot(path=str(out / f"gold_control_v123_{name}_390x844.png"), full_page=True)


def common(page: Page, screen: str) -> None:
    no_exception(page, screen); segmented(page, MAIN_NAV, 4, f"MAIN_NAV_{screen.upper()}"); bottom_nav_ok(page); no_tooltip(page); no_overflow(page, screen)


def assert_direction_engine_values(page: Page, engine_cards) -> None:
    for label in ("Monthly Direction · 3M", "FAST", "SLOW"):
        cards = engine_cards.filter(has_text=re.compile(re.escape(label), re.I))
        if cards.count() != 1:
            raise AssertionError(f"DIRECTION_ENGINE_CARD_COUNT:{label}:{cards.count()}:1")
        card = cards.first
        output = norm(card.locator(".forecast").inner_text().strip())
        status = norm(card.locator(".state").inner_text().strip())
        if output in {"", "—", "YAYIMLANMADI", "NOT_ISSUED"}:
            raise AssertionError(f"DIRECTION_ENGINE_VALUE_MISSING:{label}:{output}")
        if status != "STORED_CONTEXT_AVAILABLE":
            raise AssertionError(f"DIRECTION_ENGINE_STATUS_NOT_STORED:{label}:{status}")


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--url", default="http://127.0.0.1:8501"); ap.add_argument("--out", default="/tmp/gold_mobile_v123_qa"); args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": PHONE_WIDTH, "height": PHONE_HEIGHT}, device_scale_factor=1)
        page.goto(args.url, wait_until="domcontentloaded", timeout=60_000); page.wait_for_timeout(2400)
        page.get_by_text("GOLD CONTROL", exact=False).first.wait_for(state="visible", timeout=45_000)
        common(page, "bugun"); segmented(page, MARKET_RANGE, 4, "MARKET_RANGE"); shot(page, out, "bugun")

        click(page, "Görünüm"); page.get_by_text("GÖRÜNÜM", exact=True).first.wait_for(state="visible", timeout=15_000); common(page, "gorunum")
        markers(page, "GORUNUM", [
            "MEVCUT KAYITLI DURUM","TÜM TAHMİN VE YÖN MOTORLARI",
            "Causal Patch","VW-MIDAS-MSVR","3M Momentum · H=1 Expert","Random Walk",
            "Monthly Direction · 3M","FAST","SLOW","Macro Event","Emergency · Level",
            "Emergency · Reversal","BOCPD","GVZ Risk Cap",
            "SİNYAL ÖZETİ","MODEL YÖNÜ (AYLIK)","FAST / SLOW TEYİDİ","RİSK SEVİYESİ",
            "SİNYAL ZAMAN ÇİZELGESİ","EMERGENCY DURUMU","SİSTEM YORUMU",
            "NOT_PROVEN_EXPERT_SELECTION_RULE","AUTO SELECTOR","AUTO ENSEMBLE"
        ])
        engine_cards = page.locator(".gc-expert")
        if engine_cards.count() != 12:
            raise AssertionError(f"GORUNUM_ENGINE_INVENTORY_COUNT:{engine_cards.count()}:12")
        for i in range(12):
            if not engine_cards.nth(i).is_visible() or not engine_cards.nth(i).bounding_box():
                raise AssertionError(f"GORUNUM_ENGINE_CARD_NOT_VISIBLE:{i}")
        assert_direction_engine_values(page, engine_cards)
        ordered(page, "GORUNUM", ["TÜM TAHMİN VE YÖN MOTORLARI","SİNYAL ÖZETİ","MODEL YÖNÜ (AYLIK)","FAST / SLOW TEYİDİ","RİSK SEVİYESİ","SİNYAL ZAMAN ÇİZELGESİ","EMERGENCY DURUMU","SİSTEM YORUMU"])
        if columns(page, ".gc-grid2") != 1: raise AssertionError("GORUNUM_MOBILE_CARDS_MUST_STACK")
        if norm("POZİSYONU KORU") in body(page) or norm("GÜÇ: %68") in body(page): raise AssertionError("UNPROVEN_MOCKUP_PLACEHOLDER_VISIBLE_GORUNUM")
        shot(page, out, "gorunum")

        click(page, "Tahmin"); page.get_by_text("TAHMİN", exact=True).first.wait_for(state="visible", timeout=15_000); common(page, "tahmin")
        markers(page, "TAHMIN", ["GELECEK AY TAHMİNİ","MULTI-EXPERT MONTHLY FORECAST ENGINE","CAUSAL PATCH","VW-MIDAS-MSVR","3M MOMENTUM","RANDOM WALK","GEÇMİŞ VE TAHMİN KARŞILAŞTIRMASI","EARLY INDICATIVE","MEVCUT FİYATA GÖRE FARK","MODEL PERFORMANSI","NOT_PROVEN_EXPERT_SELECTION_RULE","AUTO SELECTOR","AUTO ENSEMBLE","HISTORICAL_REPLAY"])
        ordered(page, "TAHMIN", ["GELECEK AY TAHMİNİ","GEÇMİŞ VE TAHMİN KARŞILAŞTIRMASI","MULTI-EXPERT MONTHLY FORECAST ENGINE","MEVCUT FİYATA GÖRE FARK","MODEL PERFORMANSI"])
        if columns(page, ".gc-grid2") != 1: raise AssertionError("TAHMIN_MOBILE_MODULES_MUST_STACK")
        if columns(page, ".gc-expert-grid") != 2: raise AssertionError("TAHMIN_EXPERT_GRID_EXPECTED_2X2_AT_390PX")
        if "2.420,00" in body(page) or norm("GÜVEN: %68") in body(page): raise AssertionError("MOCKUP_SAMPLE_NUMBER_VISIBLE_TAHMIN")
        shot(page, out, "tahmin")

        click(page, "Geçmiş"); page.get_by_text("GEÇMİŞ", exact=True).first.wait_for(state="visible", timeout=15_000); common(page, "gecmis")
        markers(page, "GECMIS", ["MAPE","MAE (USD)","YÖN DOĞRULUĞU","REALIZED TAHMİN","TAHMİN PERFORMANSI","HATA / KARAR ZAMAN ÇİZELGESİ","SEÇİLMİŞ GEÇMİŞ KAYITLAR","MULTI-EXPERT FORECAST LEDGER","MONTH_END_EXPERT","EARLY INDICATIVE","HISTORICAL_REPLAY","NOT_PROVEN_EXPERT_SELECTION_RULE"])
        ordered(page, "GECMIS", ["PROSPECTIVE / LIVE CANONICAL SCORECARD","TAHMİN PERFORMANSI","HATA / KARAR ZAMAN ÇİZELGESİ","SEÇİLMİŞ GEÇMİŞ KAYITLAR","MULTI-EXPERT FORECAST LEDGER"])
        if columns(page, ".gc-grid4") != 2: raise AssertionError("GECMIS_SUMMARY_CARDS_EXPECTED_2X2_AT_390PX")
        if "+12,8%" in body(page) or "+22,6%" in body(page): raise AssertionError("MOCKUP_SAMPLE_PERFORMANCE_VISIBLE")
        shot(page, out, "gecmis"); browser.close()
    print("MOBILE_V123_ALL_ENGINE_FINAL_MOCKUP_VIEWPORT_QA_PASS"); print("ENGINE_INVENTORY_VISIBLE=12/12"); print("DIRECTION_CONTEXT_VISIBLE=3/3"); print(f"VIEWPORT={PHONE_WIDTH}x{PHONE_HEIGHT}"); print(f"SCREENSHOTS={out}"); return 0


if __name__ == "__main__":
    raise SystemExit(main())
