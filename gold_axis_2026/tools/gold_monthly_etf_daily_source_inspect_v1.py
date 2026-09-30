from __future__ import annotations
import io, json, requests, pandas as pd
from pathlib import Path

URLS={
 "GLD":"https://api.spdrgoldshares.com/api/v1/historical-archive?exchange=NYSE&lang=en&product=gld",
 "IAU":"https://www.blackrock.com/varnish-api/blk-one01-product-data/product-data/api/v1/get-fund-document?appSubType=ISHARES&appType=PRODUCT_PAGE&component=fundDownload&locale=en_US&portfolioId=239561&targetSite=us-ishares&userType=individual",
}
H={"User-Agent":"Mozilla/5.0 GOLD_MONTHLY_RESEARCH/1.0","Accept":"*/*"}

def describe(name, raw):
    out={"name":name,"bytes":len(raw)}
    xl=pd.ExcelFile(io.BytesIO(raw))
    out["sheets"]=xl.sheet_names
    details={}
    for s in xl.sheet_names:
        try:
            df=pd.read_excel(io.BytesIO(raw),sheet_name=s,header=None)
            details[s]={
                "shape":list(df.shape),
                "head":df.head(12).fillna("").astype(str).values.tolist(),
                "tail":df.tail(5).fillna("").astype(str).values.tolist(),
            }
        except Exception as e:
            details[s]={"error":repr(e)}
    out["details"]=details
    return out

def main():
    result={}
    for n,u in URLS.items():
        r=requests.get(u,headers=H,timeout=120)
        r.raise_for_status()
        result[n]=describe(n,r.content)
    Path("GOLD_MONTHLY_ETF_DAILY_SOURCE_INSPECT_2026-09-30.json").write_text(
        json.dumps(result,indent=2,ensure_ascii=False)+"\n"
    )
    print("OUTPUT_GATE=PASS")
    print(json.dumps(result,ensure_ascii=False))

if __name__=="__main__": main()
