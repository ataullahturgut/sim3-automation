import re, sys, urllib.request, urllib.parse
from html.parser import HTMLParser

URL="https://www.borsaistanbul.com/veriler/kiymetli-madenler-ve-kiymetli-taslar-piyasasi/metal-fiyatlari"

class P(HTMLParser):
    def __init__(self):
        super().__init__(); self.forms=[]; self.scripts=[]; self.links=[]; self.current_form=None
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if tag=="form":
            self.current_form={"attrs":d,"inputs":[]}; self.forms.append(self.current_form)
        elif tag in ("input","select","button") and self.current_form is not None:
            self.current_form["inputs"].append((tag,d))
        elif tag=="script" and d.get("src"):
            self.scripts.append(d["src"])
        elif tag=="a" and d.get("href"):
            self.links.append(d["href"])
    def handle_endtag(self, tag):
        if tag=="form": self.current_form=None

def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"})
    with urllib.request.urlopen(req,timeout=30) as r:
        return r.status, r.geturl(), dict(r.headers), r.read().decode("utf-8","replace")

st,final,headers,html=get(URL)
print("PAGE_STATUS",st)
print("FINAL_URL",final)
print("CONTENT_TYPE",headers.get("Content-Type"))
print("HTML_LEN",len(html))

p=P(); p.feed(html)
print("FORM_COUNT",len(p.forms))
for i,f in enumerate(p.forms):
    print("FORM",i,f["attrs"])
    for item in f["inputs"][:80]:
        print("  ",item)
print("SCRIPT_COUNT",len(p.scripts))
for s in p.scripts: print("SCRIPT",urllib.parse.urljoin(final,s))

keywords=["metal","kmtp","precious","ajax","api","xml","referans","fiyat"]
for k in keywords:
    print("\nKEYWORD",k)
    for m in list(re.finditer(k,html,re.I))[:20]:
        a=max(0,m.start()-180); b=min(len(html),m.end()+320)
        print(re.sub(r"\s+"," ",html[a:b]))

for src in p.scripts:
    u=urllib.parse.urljoin(final,src)
    try:
        sst,sfinal,sh,js=get(u)
        hits=[]
        for m in re.finditer(r".{0,180}(?:metal|kmtp|precious|api/|ajax|xml|referans|fiyat).{0,260}",js,re.I|re.S):
            frag=re.sub(r"\s+"," ",m.group(0))
            hits.append(frag)
            if len(hits)>=20: break
        if hits:
            print("\nSCRIPT_HITS",u,"LEN",len(js))
            for h in hits: print(h)
    except Exception as e:
        print("SCRIPT_ERR",u,repr(e))

print("\nLINKS_RELEVANT")
for h in p.links:
    if re.search(r"metal|kmtp|precious|xml|fiyat",h,re.I):
        print(urllib.parse.urljoin(final,h))
