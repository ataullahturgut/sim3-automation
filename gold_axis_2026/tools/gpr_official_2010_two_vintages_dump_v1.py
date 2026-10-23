"""Export exactly 2010+ two recent official GPR vintages for audited Neon append."""
from __future__ import annotations
import argparse,hashlib,io,json,math,urllib.request
import pandas as pd

META={
"2026-09":("21449bec606bc5a5b1bf58d08ce526dc35d66c94","253056ac5d54881c1f3e5767087ef682e258c7a5","2026-09-01T14:27:55Z"),
"2026-10":("8b903073ea4ce9caf9b2f238e792685ca17270f4","a46ff84a7e9fe83f5d1b73186d161aeba57b4da0","2026-10-01T14:19:21Z")
}
def month_shift(s):
    y,m=map(int,s.split("-"));x=y*12+m-2
    return f"{x//12:04d}-{x%12+1:02d}"
def read(vintage):
    sha,blob,published=META[vintage]
    url=f"https://raw.githubusercontent.com/iacoviel/iacoviel.github.io/{sha}/gpr_archive_files/data_gpr_export_{vintage.replace('-','')}.xls"
    with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"GPR-2010-vintage-confirmation"}),timeout=120) as z:raw=z.read()
    digest=hashlib.sha1(b"blob "+str(len(raw)).encode()+bytes([0])+raw).hexdigest()
    if digest!=blob:raise RuntimeError(f"GPR_ORIGINAL_BLOB_MISMATCH {vintage}")
    df=pd.read_excel(io.BytesIO(raw),engine="xlrd",sheet_name="Sheet1")
    if not {"month","GPR","GPRT","GPRA"}.issubset(df.columns):raise RuntimeError("WRONG_GPR_COLS")
    seen=set();out=[]
    for _,r in df.iterrows():
        d=pd.to_datetime(r["month"],errors="coerce")
        if pd.isna(d):continue
        ym=d.strftime("%Y-%m")
        if ym<"2010-01" or ym>=vintage:continue
        if ym in seen:raise RuntimeError("DUPLICATE_MONTH")
        seen.add(ym)
        for s in ("GPR","GPRT","GPRA"):
            v=float(r[s])
            if not(math.isfinite(v) and v>=0):raise RuntimeError("INVALID_GPR_INDEX")
            out.append([vintage,s,ym,v])
    n=200 if vintage=="2026-09" else 201
    if len(seen)!=n or max(seen)!=month_shift(vintage) or len(out)!=n*3:
        raise RuntimeError(f"INCOMPLETE_GPR_HISTORY {vintage} {len(out)}")
    return out
def main():
    a=read("2026-09")+read("2026-10")
    if len(a)!=1203:raise RuntimeError("REQUIRED_1203_RECORDS")
    print("GPR_2010_FORWARD_TWO_ORIGINAL_VINTAGES=PASS count=1203",flush=True)
    print("GPR_2010_FORWARD_JSON="+json.dumps(a,separators=(",",":")),flush=True)
if __name__=="__main__":
    main()
