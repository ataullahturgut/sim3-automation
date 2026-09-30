from __future__ import annotations
import io, json, requests, pandas as pd
from pathlib import Path

URLS={
 "GLD":"https://api.spdrgoldshares.com/api/v1/historical-archive?exchange=NYSE&lang=en&product=gld",
 "IAU":"https://www.blackrock.com/varnish-api/blk-one01-product-data/product-data/api/v1/get-fund-document?appSubType=ISHARES&appType=PRODUCT_PAGE&component=fundDownload&locale=en_US&portfolioId=239561&targetSite=us-ishares&userType=individual",
}
H={"User-Agent":"Mozilla/5.0 GOLD_MONTHLY_RESEARCH/1.0","Accept":"*/*"}

def describe(name, raw, content_type=""):
    out={"name":name,"bytes":len(raw),"content_type":content_type,"magic_hex":raw[:16].hex()}
    # XLSX/ZIP
    if raw[:2]==b"PK":
        xl=pd.ExcelFile(io.BytesIO(raw),engine="openpyxl")
        out["format"]="xlsx"
        out["sheets"]=xl.sheet_names
        details={}
        for s in xl.sheet_names:
            try:
                df=pd.read_excel(io.BytesIO(raw),sheet_name=s,header=None,engine="openpyxl")
                details[s]={
                    "shape":list(df.shape),
                    "head":df.head(15).fillna("").astype(str).values.tolist(),
                    "tail":df.tail(8).fillna("").astype(str).values.tolist(),
                }
            except Exception as e:
                details[s]={"error":repr(e)}
        out["details"]=details
        return out
    # Legacy XLS
    if raw[:8]==bytes.fromhex("d0cf11e0a1b11ae1"):
        xl=pd.ExcelFile(io.BytesIO(raw),engine="xlrd")
        out["format"]="xls"
        out["sheets"]=xl.sheet_names
        out["details"]={}
        for s in xl.sheet_names:
            df=pd.read_excel(io.BytesIO(raw),sheet_name=s,header=None,engine="xlrd")
            out["details"][s]={
                "shape":list(df.shape),
                "head":df.head(15).fillna("").astype(str).values.tolist(),
                "tail":df.tail(8).fillna("").astype(str).values.tolist(),
            }
        return out
    # Some BlackRock download endpoints return CSV/text while advertising Excel.
    txt=raw.decode("utf-8",errors="replace")
    out["format"]="text_or_csv"
    out["text_head"]=txt[:4000]
    try:
        df=pd.read_csv(io.StringIO(txt),header=None)
        out["csv_shape"]=list(df.shape)
        out["csv_head"]=df.head(20).fillna("").astype(str).values.tolist()
        out["csv_tail"]=df.tail(10).fillna("").astype(str).values.tolist()
    except Exception as e:
        out["csv_error"]=repr(e)
    return out

def main():
    result={}
    for n,u in URLS.items():
        r=requests.get(u,headers=H,timeout=120)
        r.raise_for_status()
        result[n]=describe(n,r.content,r.headers.get("Content-Type",""))
    Path("GOLD_MONTHLY_ETF_DAILY_SOURCE_INSPECT_2026-09-30.json").write_text(
        json.dumps(result,indent=2,ensure_ascii=False)+"\n"
    )
    print("OUTPUT_GATE=PASS")
    print(json.dumps(result,ensure_ascii=False))

if __name__=="__main__": main()
