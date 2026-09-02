from __future__ import annotations

import argparse
import re
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

PHONE_WIDTH = 390
PHONE_HEIGHT = 844
MAIN_NAV = ".st-key-gc_main_nav"
MARKET_RANGE = ".st-key-gc_market_range"


def normalize_text(value: str) -> str:
    return value.upper().replace("İ", "I")


def assert_no_streamlit_exception(page: Page, screen: str) -> None:
    exception_nodes = page.locator('[data-testid="stException"]')
    if exception_nodes.count() and exception_nodes.first.is_visible():
        text = exception_nodes.first.inner_text()
        raise AssertionError(f"STREAMLIT_EXCEPTION_VISIBLE:{screen}:{text[:500]}")
    body = normalize_text(page.locator("body").inner_text())
    for marker in ("THIS APP HAS ENCOUNTERED AN ERROR", "IMPORTERROR", "MODULENOTFOUNDERROR", "TRACEBACK (MOST RECENT CALL LAST)"):
        if marker in body:
            raise AssertionError(f"STREAMLIT_FATAL_MARKER_VISIBLE:{screen}:{marker}")


def assert_no_horizontal_overflow(page: Page, screen: str) -> None:
    dims = page.evaluate("""() => ({innerWidth:window.innerWidth,scrollWidth:document.documentElement.scrollWidth,bodyScrollWidth:document.body.scrollWidth})""")
    widest = max(int(dims["scrollWidth"]), int(dims["bodyScrollWidth"]))
    if widest > int(dims["innerWidth"]) + 4:
        raise AssertionError(f"MOBILE_HORIZONTAL_OVERFLOW:{screen}:{dims}")


def visible_text(page: Page) -> str:
    return normalize_text(page.locator("body").inner_text())


def main_nav_label(page: Page, name: str):
    pattern = re.compile(re.escape(name), re.I)
    root = page.locator(MAIN_NAV)
    root.first.wait_for(state="attached", timeout=30_000)
    labels = root.locator('label[data-testid="stRadioOption"]').filter(has_text=pattern)
    for index in range(min(labels.count(), 8)):
        item = labels.nth(index)
        if item.is_visible():
            return item
    return None


def require_nav_labels(page: Page) -> None:
    missing = [label for label in ["Bugün", "Görünüm", "Tahmin", "Geçmiş"] if main_nav_label(page, label) is None]
    if missing:
        root_text = page.locator(MAIN_NAV).inner_text() if page.locator(MAIN_NAV).count() else "NO_MAIN_NAV_ROOT"
        raise AssertionError(f"MOBILE_BOTTOM_NAV_MISSING:{missing}:ROOT={root_text}")


def assert_segmented_control(page: Page, root_selector: str, expected_count: int, name: str) -> None:
    root = page.locator(root_selector)
    root.first.wait_for(state="attached", timeout=30_000)
    options = root.locator('label[data-testid="stRadioOption"]')
    if options.count() != expected_count:
        raise AssertionError(f"{name}_OPTION_COUNT:{options.count()}:{expected_count}")
    widths = []
    for i in range(expected_count):
        option = options.nth(i)
        if not option.is_visible():
            raise AssertionError(f"{name}_OPTION_NOT_VISIBLE:{i}")
        box = option.bounding_box()
        if not box:
            raise AssertionError(f"{name}_OPTION_NO_BOX:{i}")
        widths.append(float(box["width"]))
    if max(widths) - min(widths) > 3.0:
        raise AssertionError(f"{name}_UNEQUAL_WIDTHS:{widths}")
    selected = root.locator('label[data-testid="stRadioOption"][data-selected="true"]')
    if selected.count() != 1:
        raise AssertionError(f"{name}_SELECTED_COUNT:{selected.count()}")


def assert_bottom_nav_in_viewport(page: Page) -> None:
    radio = page.locator(f'{MAIN_NAV} [data-testid="stRadio"]').first
    box = radio.bounding_box(); viewport = page.viewport_size
    if not box or not viewport:
        raise AssertionError("MOBILE_BOTTOM_NAV_NO_BOX")
    if box["x"] < -1 or box["x"] + box["width"] > viewport["width"] + 1:
        raise AssertionError(f"MOBILE_BOTTOM_NAV_HORIZONTAL_BOUNDS:{box}:{viewport}")
    if box["y"] + box["height"] > viewport["height"] + 1:
        raise AssertionError(f"MOBILE_BOTTOM_NAV_VERTICAL_BOUNDS:{box}:{viewport}")


def assert_no_visible_tooltip(page: Page) -> None:
    tooltip = page.locator(".vg-tooltip, #vg-tooltip-element")
    for index in range(min(tooltip.count(), 8)):
        if tooltip.nth(index).is_visible():
            raise AssertionError("CHART_TOOLTIP_VISIBLE")


def click_tab(page: Page, name: str) -> None:
    target = main_nav_label(page, name)
    if target is None:
        raise AssertionError(f"MOBILE_TAB_CONTROL_NOT_FOUND:{name}")
    target.click(); page.wait_for_timeout(1200)


def screenshot(page: Page, out: Path, name: str) -> None:
    page.screenshot(path=str(out / f"gold_control_v122_{name}_390x844.png"), full_page=True)


def require_markers(body: str, screen: str, markers: list[str]) -> None:
    normalized_body = normalize_text(body)
    for marker in markers:
        if normalize_text(marker) not in normalized_body:
            raise AssertionError(f"{screen}_FINAL_MARKER_MISSING:{marker}")


def marker_y(page: Page, marker: str) -> float:
    # Prefer the actual section heading so a hero/meta label with similar text
    # cannot satisfy or disturb the frozen mockup section order.
    scoped = page.locator(".gc-section-title").filter(has_text=re.compile(re.escape(marker), re.I))
    for candidates in (scoped, page.get_by_text(marker, exact=False)):
        for i in range(min(candidates.count(), 12)):
            item = candidates.nth(i)
            if item.is_visible():
                box = item.bounding_box()
                if box:
                    return float(box["y"])
    raise AssertionError(f"VISIBLE_MARKER_NOT_FOUND:{marker}")


def assert_vertical_order(page: Page, screen: str, markers: list[str]) -> None:
    positions = [(marker, marker_y(page, marker)) for marker in markers]
    ys = [y for _, y in positions]
    if any(b <= a for a, b in zip(ys, ys[1:])):
        raise AssertionError(f"{screen}_VERTICAL_ORDER_MISMATCH:{positions}")


def grid_column_count(page: Page, selector: str) -> int:
    root = page.locator(selector).first
    if not root.count() or not root.is_visible():
        raise AssertionError(f"GRID_NOT_VISIBLE:{selector}")
    value = root.evaluate("el => getComputedStyle(el).gridTemplateColumns")
    return len([x for x in str(value).split() if x])


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--url", default="http://127.0.0.1:8501"); parser.add_argument("--out", default="/tmp/gold_mobile_v122_qa"); args = parser.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width":PHONE_WIDTH,"height":PHONE_HEIGHT}, device_scale_factor=1)
        page.goto(args.url, wait_until="domcontentloaded", timeout=60_000); page.wait_for_timeout(2400)
        assert_no_streamlit_exception(page,"initial"); page.get_by_text("GOLD CONTROL",exact=False).first.wait_for(state="visible",timeout=45_000)
        require_nav_labels(page); assert_segmented_control(page,MAIN_NAV,4,"MAIN_NAV"); assert_segmented_control(page,MARKET_RANGE,4,"MARKET_RANGE"); assert_bottom_nav_in_viewport(page); assert_no_visible_tooltip(page); assert_no_horizontal_overflow(page,"bugun"); screenshot(page,out,"bugun")

        click_tab(page,"Görünüm"); assert_no_streamlit_exception(page,"gorunum"); page.get_by_text("GÖRÜNÜM",exact=True).first.wait_for(state="visible",timeout=15_000); body=visible_text(page)
        require_markers(body,"GORUNUM",["MEVCUT KAYITLI DURUM","SİNYAL ÖZETİ","MODEL YÖNÜ (AYLIK)","FAST / SLOW TEYİDİ","RİSK SEVİYESİ","SİNYAL ZAMAN ÇİZELGESİ","EMERGENCY DURUMU","SİSTEM YORUMU","MACRO EVENT","BOCPD","NOT_PROVEN_EXPERT_SELECTION_RULE","AUTO SELECTOR","AUTO ENSEMBLE"])
        assert_vertical_order(page,"GORUNUM",["SİNYAL ÖZETİ","MODEL YÖNÜ (AYLIK)","FAST / SLOW TEYİDİ","RİSK SEVİYESİ","SİNYAL ZAMAN ÇİZELGESİ","EMERGENCY DURUMU","SİSTEM YORUMU"])
        if grid_column_count(page,".gc-grid2") != 1:
            raise AssertionError("GORUNUM_MOBILE_CARDS_MUST_STACK")
        if normalize_text("POZİSYONU KORU") in body or normalize_text("GÜÇ: %68") in body:
            raise AssertionError("UNPROVEN_MOCKUP_PLACEHOLDER_VISIBLE_GORUNUM")
        assert_segmented_control(page,MAIN_NAV,4,"MAIN_NAV_GORUNUM"); assert_bottom_nav_in_viewport(page); assert_no_horizontal_overflow(page,"gorunum"); screenshot(page,out,"gorunum")

        click_tab(page,"Tahmin"); assert_no_streamlit_exception(page,"tahmin"); page.get_by_text("TAHMİN",exact=True).first.wait_for(state="visible",timeout=15_000); body=visible_text(page)
        require_markers(body,"TAHMIN",["GELECEK AY TAHMİNİ","MULTI-EXPERT MONTHLY FORECAST ENGINE","CAUSAL PATCH","VW-MIDAS-MSVR","3M MOMENTUM","RANDOM WALK","GEÇMİŞ VE TAHMİN KARŞILAŞTIRMASI","EARLY INDICATIVE","MEVCUT FİYATA GÖRE FARK","MODEL PERFORMANSI","NOT_PROVEN_EXPERT_SELECTION_RULE","AUTO SELECTOR","AUTO ENSEMBLE","HISTORICAL_REPLAY"])
        assert_vertical_order(page,"TAHMIN",["GELECEK AY TAHMİNİ","GEÇMİŞ VE TAHMİN KARŞILAŞTIRMASI","MULTI-EXPERT MONTHLY FORECAST ENGINE","MEVCUT FİYATA GÖRE FARK","MODEL PERFORMANSI"])
        if grid_column_count(page,".gc-grid2") != 1:
            raise AssertionError("TAHMIN_MOBILE_MODULES_MUST_STACK")
        if grid_column_count(page,".gc-expert-grid") != 2:
            raise AssertionError("TAHMIN_EXPERT_GRID_EXPECTED_2X2_AT_390PX")
        if "2.420,00" in body or normalize_text("GÜVEN: %68") in body:
            raise AssertionError("MOCKUP_SAMPLE_NUMBER_VISIBLE_TAHMIN")
        assert_segmented_control(page,MAIN_NAV,4,"MAIN_NAV_TAHMIN"); assert_bottom_nav_in_viewport(page); assert_no_horizontal_overflow(page,"tahmin"); screenshot(page,out,"tahmin")

        click_tab(page,"Geçmiş"); assert_no_streamlit_exception(page,"gecmis"); page.get_by_text("GEÇMİŞ",exact=True).first.wait_for(state="visible",timeout=15_000); body=visible_text(page)
        require_markers(body,"GECMIS",["MAPE","MAE (USD)","YÖN DOĞRULUĞU","REALIZED TAHMİN","TAHMİN PERFORMANSI","HATA / KARAR ZAMAN ÇİZELGESİ","SEÇİLMİŞ GEÇMİŞ KAYITLAR","MULTI-EXPERT FORECAST LEDGER","MONTH_END_EXPERT","EARLY INDICATIVE","HISTORICAL_REPLAY","NOT_PROVEN_EXPERT_SELECTION_RULE"])
        assert_vertical_order(page,"GECMIS",["PROSPECTIVE / LIVE CANONICAL SCORECARD","TAHMİN PERFORMANSI","HATA / KARAR ZAMAN ÇİZGİSİ","SEÇİLMİŞ GEÇMİŞ KAYITLAR","MULTI-EXPERT FORECAST LEDGER"])
        if grid_column_count(page,".gc-grid4") != 2:
            raise AssertionError("GECMIS_SUMMARY_CARDS_EXPECTED_2X2_AT_390PX")
        if "+12,8%" in body or "+22,6%" in body:
            raise AssertionError("MOCKUP_SAMPLE_PERFORMANCE_VISIBLE")
        assert_segmented_control(page,MAIN_NAV,4,"MAIN_NAV_GECMIS"); assert_bottom_nav_in_viewport(page); assert_no_horizontal_overflow(page,"gecmis"); screenshot(page,out,"gecmis")
        browser.close()
    print("MOBILE_V122_MULTI_EXPERT_FINAL_MOCKUP_VIEWPORT_QA_PASS"); print(f"VIEWPORT={PHONE_WIDTH}x{PHONE_HEIGHT}"); print(f"SCREENSHOTS={out}"); return 0


if __name__ == "__main__":
    raise SystemExit(main())
