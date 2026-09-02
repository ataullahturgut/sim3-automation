from __future__ import annotations

import argparse
import re
from pathlib import Path

from playwright.sync_api import Page, sync_playwright


PHONE_WIDTH = 390
PHONE_HEIGHT = 844
MAIN_NAV = ".st-key-gc_main_nav"


def assert_no_streamlit_exception(page: Page, screen: str) -> None:
    """Fail on rendered Streamlit exceptions, not merely server-health failures."""
    exception_nodes = page.locator('[data-testid="stException"]')
    if exception_nodes.count() and exception_nodes.first.is_visible():
        text = exception_nodes.first.inner_text()
        raise AssertionError(f"STREAMLIT_EXCEPTION_VISIBLE:{screen}:{text[:500]}")

    body = page.locator("body").inner_text().upper()
    fatal_markers = (
        "THIS APP HAS ENCOUNTERED AN ERROR",
        "IMPORTERROR",
        "MODULENOTFOUNDERROR",
        "TRACEBACK (MOST RECENT CALL LAST)",
    )
    for marker in fatal_markers:
        if marker in body:
            raise AssertionError(f"STREAMLIT_FATAL_MARKER_VISIBLE:{screen}:{marker}")


def assert_no_horizontal_overflow(page: Page, screen: str) -> None:
    dims = page.evaluate(
        """() => ({
          innerWidth: window.innerWidth,
          scrollWidth: document.documentElement.scrollWidth,
          bodyScrollWidth: document.body.scrollWidth
        })"""
    )
    widest = max(int(dims["scrollWidth"]), int(dims["bodyScrollWidth"]))
    if widest > int(dims["innerWidth"]) + 4:
        raise AssertionError(f"MOBILE_HORIZONTAL_OVERFLOW:{screen}:{dims}")


def visible_text(page: Page) -> str:
    return page.locator("body").inner_text().upper()


def main_nav_label(page: Page, name: str):
    pattern = re.compile(re.escape(name), re.I)
    root = page.locator(MAIN_NAV)
    # A fixed-position descendant can be visible while Streamlit's wrapper has
    # a zero-sized/hidden bounding box. Require DOM attachment, not wrapper
    # visibility, then assert the actual interactive label is visible.
    root.first.wait_for(state="attached", timeout=30_000)
    labels = root.locator("label").filter(has_text=pattern)
    for index in range(min(labels.count(), 8)):
        item = labels.nth(index)
        if item.is_visible():
            return item
    text_nodes = root.get_by_text(pattern, exact=False)
    for index in range(min(text_nodes.count(), 8)):
        item = text_nodes.nth(index)
        if item.is_visible():
            return item
    return None


def require_nav_labels(page: Page) -> None:
    missing: list[str] = []
    for label in ["Bugün", "Görünüm", "Tahmin", "Geçmiş"]:
        if main_nav_label(page, label) is None:
            missing.append(label)
    if missing:
        root_text = page.locator(MAIN_NAV).inner_text() if page.locator(MAIN_NAV).count() else "NO_MAIN_NAV_ROOT"
        raise AssertionError(f"MOBILE_BOTTOM_NAV_MISSING:{missing}:ROOT={root_text}")


def click_tab(page: Page, name: str) -> None:
    target = main_nav_label(page, name)
    if target is None:
        raise AssertionError(f"MOBILE_TAB_CONTROL_NOT_FOUND:{name}")
    target.click()
    page.wait_for_timeout(1100)


def screenshot(page: Page, out: Path, name: str) -> None:
    path = out / f"gold_control_v2_{name}_390x844.png"
    page.screenshot(path=str(path), full_page=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8501")
    parser.add_argument("--out", default="/tmp/gold_mobile_v2_qa")
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": PHONE_WIDTH, "height": PHONE_HEIGHT}, device_scale_factor=1)
        page.goto(args.url, wait_until="domcontentloaded", timeout=60_000)
        page.wait_for_timeout(2200)
        assert_no_streamlit_exception(page, "initial")
        page.get_by_text("GOLD CONTROL", exact=False).first.wait_for(state="visible", timeout=45_000)

        assert_no_streamlit_exception(page, "bugun")
        screenshot(page, out, "bugun")
        require_nav_labels(page)
        assert_no_horizontal_overflow(page, "bugun")

        click_tab(page, "Görünüm")
        assert_no_streamlit_exception(page, "gorunum")
        page.get_by_text("GÖRÜNÜM", exact=True).first.wait_for(state="visible", timeout=15_000)
        body = visible_text(page)
        for marker in [
            "SİNYAL ÖZETİ",
            "MODEL YÖNÜ (AYLIK)",
            "FAST / SLOW TEYİDİ",
            "RİSK SEVİYESİ",
            "SİNYAL ZAMAN ÇİZELGESİ",
            "EMERGENCY DURUMU",
            "SİSTEM YORUMU",
        ]:
            if marker not in body:
                raise AssertionError(f"GORUNUM_V2_MARKER_MISSING:{marker}")
        if "POZİSYONU KORU" in body or "GÜÇ: %68" in body:
            raise AssertionError("UNPROVEN_MOCKUP_PLACEHOLDER_VISIBLE_GORUNUM")
        assert_no_horizontal_overflow(page, "gorunum")
        screenshot(page, out, "gorunum")

        click_tab(page, "Tahmin")
        assert_no_streamlit_exception(page, "tahmin")
        page.get_by_text("TAHMİN", exact=True).first.wait_for(state="visible", timeout=15_000)
        body = visible_text(page)
        for marker in [
            "GELECEK AY TAHMİNİ",
            "GEÇMİŞ VE TAHMİN KARŞILAŞTIRMASI",
            "SENARYOLAR",
            "MEVCUT FİYATA GÖRE FARK",
            "MODEL PERFORMANSI",
        ]:
            if marker not in body:
                raise AssertionError(f"TAHMIN_V2_MARKER_MISSING:{marker}")
        if "2.420,00" in body or "GÜVEN: %68" in body:
            raise AssertionError("MOCKUP_SAMPLE_NUMBER_VISIBLE_TAHMIN")
        assert_no_horizontal_overflow(page, "tahmin")
        screenshot(page, out, "tahmin")

        click_tab(page, "Geçmiş")
        assert_no_streamlit_exception(page, "gecmis")
        page.get_by_text("PERFORMANS", exact=True).first.wait_for(state="visible", timeout=15_000)
        body = visible_text(page)
        for marker in [
            "YAYIMLANAN İLERİ TAHMİN",
            "TAHMİN PERFORMANSI",
            "HATA / KARAR ZAMAN ÇİZELGESİ",
            "SEÇİLMİŞ GEÇMİŞ KAYITLAR",
        ]:
            if marker not in body:
                raise AssertionError(f"GECMIS_V2_MARKER_MISSING:{marker}")
        if "+12,8%" in body or "+22,6%" in body:
            raise AssertionError("MOCKUP_SAMPLE_PERFORMANCE_VISIBLE")
        assert_no_horizontal_overflow(page, "gecmis")
        screenshot(page, out, "gecmis")

        browser.close()

    print("MOBILE_V2_VIEWPORT_QA_PASS")
    print(f"VIEWPORT={PHONE_WIDTH}x{PHONE_HEIGHT}")
    print(f"SCREENSHOTS={out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
