from playwright.sync_api import sync_playwright
import json, re, time

URL="https://www.borsaistanbul.com/veriler/kiymetli-madenler-ve-kiymetli-taslar-piyasasi/metal-fiyatlari"

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    page=browser.new_page()
    reqs=[]
    resps=[]
    page.on("request", lambda r: reqs.append({"method":r.method,"url":r.url,"post_data":r.post_data}))
    page.on("response", lambda r: resps.append({"status":r.status,"url":r.url}))
    page.goto(URL, wait_until="networkidle", timeout=120000)
    print("TITLE",page.title())
    form=page.locator("form.metal-fiyatlari-form")
    print("FORM_COUNT",form.count())
    if form.count():
        print("FORM_HTML",form.first.inner_html()[:12000])
    inputs=page.locator("form.metal-fiyatlari-form input.inputCalendar")
    print("DATE_INPUTS",inputs.count())
    buttons=page.locator("form.metal-fiyatlari-form button")
    print("BUTTONS",buttons.count())
    for i in range(buttons.count()):
        try: print("BUTTON",i,buttons.nth(i).inner_text(),buttons.nth(i).get_attribute("type"))
        except: pass
    # set dates robustly
    if inputs.count()>=2:
        for loc,val in [(inputs.nth(0),"01.01.2025"),(inputs.nth(1),"31.01.2025")]:
            try:
                loc.fill(val)
            except Exception:
                page.evaluate("(el,v)=>{el.value=v;el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}));}",loc.element_handle(),val)
    au=page.locator("form.metal-fiyatlari-form input[name=priceType][value=AU]")
    if au.count(): au.check(force=True)
    before=len(reqs)
    if buttons.count():
        buttons.last.click(force=True)
    else:
        # button may be input[type=button/submit]
        cand=page.locator("form.metal-fiyatlari-form input[type=button], form.metal-fiyatlari-form input[type=submit]")
        print("INPUT_BUTTONS",cand.count())
        if cand.count(): cand.last.click(force=True)
    page.wait_for_timeout(6000)
    print("REQUESTS_AFTER_QUERY")
    for x in reqs[before:]:
        print(json.dumps(x,ensure_ascii=False))
    print("RESPONSES_AFTER_QUERY")
    for x in resps:
        if re.search(r"metal|kmtp|price|query|xml|api|ajax",x["url"],re.I):
            print(json.dumps(x,ensure_ascii=False))
    print("PAGE_TEXT_AFTER",page.locator("body").inner_text()[-8000:])
    # click XML link separately
    xml=page.locator("#xmlVeriler_KMTP_Metal")
    print("XML_COUNT",xml.count())
    if xml.count():
        before=len(reqs)
        try: xml.click(force=True)
        except Exception as e: print("XML_CLICK_ERR",repr(e))
        page.wait_for_timeout(5000)
        print("REQUESTS_AFTER_XML")
        for x in reqs[before:]:
            print(json.dumps(x,ensure_ascii=False))
    browser.close()
