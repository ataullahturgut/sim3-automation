from __future__ import annotations
import argparse, io, json, math, requests
from pathlib import Path

import numpy as np
import pandas as pd
from lxml import etree

GLD_URL="https://api.spdrgoldshares.com/api/v1/historical-archive?exchange=NYSE&lang=en&product=gld"
IAU_URL="https://www.blackrock.com/varnish-api/blk-one01-product-data/product-data/api/v1/get-fund-document?appSubType=ISHARES&appType=PRODUCT_PAGE&component=fundDownload&locale=en_US&portfolioId=239561&targetSite=us-ishares&userType=individual"
H={"User-Agent":"Mozilla/5.0 GOLD_MONTHLY_RESEARCH/1.0","Accept":"*/*"}
CAL_START,CAL_END="2010-01","2020-12"
CORE_TARGETS=["2022-05","2022-07","2022-09","2024-03"]

def fetch(url):
    r=requests.get(url,headers=H,timeout=120)
    r.raise_for_status()
    return r.content

def parse_gld(raw):
    df=pd.read_excel(io.BytesIO(raw),sheet_name="US GLD Historical Archive",engine="openpyxl")
    df=df.rename(columns={
        "Date":"date",
        "Tonnes of Gold":"tonnes",
        "Daily Share Volume":"volume",
    })
    df["date"]=pd.to_datetime(df["date"],format="%d-%b-%Y",errors="coerce")
    df["tonnes"]=pd.to_numeric(df["tonnes"],errors="coerce")
    df["volume"]=pd.to_numeric(df["volume"],errors="coerce")
    df=df.dropna(subset=["date","tonnes"]).sort_values("date").drop_duplicates("date",keep="last")
    return df[["date","tonnes","volume"]]

def parse_iau(raw):
    parser=etree.XMLParser(recover=True,huge_tree=True)
    root=etree.fromstring(raw,parser=parser)
    ns={"ss":"urn:schemas-microsoft-com:office:spreadsheet"}
    target=None
    for ws in root.xpath("//ss:Worksheet",namespaces=ns):
        name=ws.attrib.get("{urn:schemas-microsoft-com:office:spreadsheet}Name","")
        if name=="Historical":
            target=ws; break
    if target is None: raise RuntimeError("IAU_HISTORICAL_SHEET_MISSING")
    rows=[]
    for rr in target.xpath(".//ss:Row",namespaces=ns):
        vals=[]
        for cell in rr.xpath("./ss:Cell",namespaces=ns):
            ds=cell.xpath("./ss:Data",namespaces=ns)
            dat=ds[0] if ds else None
            vals.append("" if dat is None or dat.text is None else dat.text)
        rows.append(vals)
    if not rows: raise RuntimeError("IAU_ROWS_EMPTY")
    hdr=rows[0]
    if "As Of" not in hdr or "Shares Outstanding" not in hdr:
        raise RuntimeError(("IAU_HEADER_UNEXPECTED",hdr))
    di=hdr.index("As Of"); si=hdr.index("Shares Outstanding")
    out=[]
    for r in rows[1:]:
        if len(r)<=max(di,si): continue
        out.append((r[di],r[si]))
    df=pd.DataFrame(out,columns=["date","shares"])
    df["date"]=pd.to_datetime(df["date"],errors="coerce")
    df["shares"]=pd.to_numeric(df["shares"],errors="coerce")
    df=df.dropna().sort_values("date").drop_duplicates("date",keep="last")
    return df

def monthly_features(gld,iau):
    g=gld.copy(); i=iau.copy()
    g["month"]=g.date.dt.strftime("%Y-%m"); i["month"]=i.date.dt.strftime("%Y-%m")
    # End levels.
    ge=g.groupby("month").tail(1).set_index("month")
    ie=i.groupby("month").tail(1).set_index("month")
    idx=ge.index.union(ie.index).sort_values()
    m=pd.DataFrame(index=idx)
    m["gld_tonnes_end"]=ge.tonnes.reindex(idx)
    m["iau_shares_end"]=ie.shares.reindex(idx)
    m["gld_tonnes_pct1"]=m.gld_tonnes_end.pct_change()
    m["iau_shares_pct1"]=m.iau_shares_end.pct_change()
    m["combined_flow"]=(m.gld_tonnes_pct1+m.iau_shares_pct1)/2.0
    m["etf_divergence"]=(m.gld_tonnes_pct1-m.iau_shares_pct1).abs()
    m["outflow_breadth"]=(m.gld_tonnes_pct1<0).astype(int)+(m.iau_shares_pct1<0).astype(int)

    # Churn uses daily absolute changes, normalized by prior month-end.
    g["abs_dt"]=g.tonnes.diff().abs()
    i["abs_ds"]=i.shares.diff().abs()
    gch=g.groupby("month").abs_dt.sum(min_count=1).reindex(idx)
    ich=i.groupby("month").abs_ds.sum(min_count=1).reindex(idx)
    m["gld_churn"]=gch/m.gld_tonnes_end.shift(1)
    m["iau_churn"]=ich/m.iau_shares_end.shift(1)

    gv=g.groupby("month").volume.mean().reindex(idx)
    m["gld_volume_mean"]=gv
    m["gld_volume_med12_prior"]=gv.shift(1).rolling(12,min_periods=6).median()
    m["gld_volume_ratio12"]=gv/m.gld_volume_med12_prior
    return m

def q(s,p):
    return float(pd.to_numeric(s,errors="coerce").dropna().quantile(p))

def pct_rank(cal,val):
    z=pd.to_numeric(cal,errors="coerce").dropna().values.astype(float)
    if len(z)==0 or val is None or not np.isfinite(val): return None
    return float(np.mean(z<=float(val)))

def calibrate(m):
    c=m.loc[CAL_START:CAL_END]
    return {
        "combined_flow_q10":q(c.combined_flow,.10),
        "gld_tonnes_pct1_q10":q(c.gld_tonnes_pct1,.10),
        "iau_shares_pct1_q10":q(c.iau_shares_pct1,.10),
        "gld_churn_q90":q(c.gld_churn,.90),
        "iau_churn_q90":q(c.iau_churn,.90),
        "gld_volume_ratio12_q90":q(c.gld_volume_ratio12,.90),
        "etf_divergence_q90":q(c.etf_divergence,.90),
    }

def row_flags(r,th):
    d={
        "ETF_OUTFLOW_Q10": bool(r.combined_flow<=th["combined_flow_q10"]),
        "ETF_GLD_OUTFLOW_Q10": bool(r.gld_tonnes_pct1<=th["gld_tonnes_pct1_q10"]),
        "ETF_IAU_OUTFLOW_Q10": bool(r.iau_shares_pct1<=th["iau_shares_pct1_q10"]),
        "ETF_GLD_CHURN_Q90": bool(r.gld_churn>=th["gld_churn_q90"]),
        "ETF_IAU_CHURN_Q90": bool(r.iau_churn>=th["iau_churn_q90"]),
        "ETF_VOLUME_Q90": bool(r.gld_volume_ratio12>=th["gld_volume_ratio12_q90"]),
        "ETF_DIVERGENCE_Q90": bool(r.etf_divergence>=th["etf_divergence_q90"]),
    }
    d["ETF_STRESS_2PLUS"]=sum(d.values())>=2
    d["ETF_ANOMALY_COUNT"]=int(sum(v for k,v in d.items() if k!="ETF_STRESS_2PLUS"))
    return d

def score(rows,flag):
    ev=[r for r in rows if r[flag]]
    hi=[r for r in rows if r["ape_severity"]=="HIGH"]
    hits=[r for r in ev if r["ape_severity"]=="HIGH"]
    fps=[r for r in ev if r["ape_severity"]!="HIGH"]
    return {
        "n":len(rows),"events":len(ev),"high_n":len(hi),"hits":len(hits),"false_alarms":len(fps),
        "precision":None if not ev else len(hits)/len(ev),
        "recall":None if not hi else len(hits)/len(hi),
        "alarm_targets":[r["target"] for r in ev],
        "hit_targets":[r["target"] for r in hits],
        "false_alarm_targets":[r["target"] for r in fps],
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--severity",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()

    sev=json.loads(Path(a.severity).read_text())
    if sev.get("schema")!="GOLD_MONTHLY_CHHHO_ERROR_SEVERITY_V3_2026-09-30":
        raise RuntimeError(("BAD_SEVERITY_SCHEMA",sev.get("schema")))

    gld_raw,iau_raw=fetch(GLD_URL),fetch(IAU_URL)
    gld,iau=parse_gld(gld_raw),parse_iau(iau_raw)
    m=monthly_features(gld,iau)
    th=calibrate(m)
    cal=m.loc[CAL_START:CAL_END]

    rows=[]
    for sr in sev["rows"]:
        o=sr["origin"]
        if o not in m.index: continue
        r=m.loc[o]
        vals={
            "gld_tonnes_pct1":float(r.gld_tonnes_pct1),
            "iau_shares_pct1":float(r.iau_shares_pct1),
            "combined_flow":float(r.combined_flow),
            "gld_churn":float(r.gld_churn),
            "iau_churn":float(r.iau_churn),
            "gld_volume_ratio12":float(r.gld_volume_ratio12),
            "etf_divergence":float(r.etf_divergence),
            "outflow_breadth":int(r.outflow_breadth),
            "gld_tonnes_end":float(r.gld_tonnes_end),
            "iau_shares_end":float(r.iau_shares_end),
        }
        ranks={
            "pct_rank_combined_flow":pct_rank(cal.combined_flow,vals["combined_flow"]),
            "pct_rank_gld_tonnes_pct1":pct_rank(cal.gld_tonnes_pct1,vals["gld_tonnes_pct1"]),
            "pct_rank_iau_shares_pct1":pct_rank(cal.iau_shares_pct1,vals["iau_shares_pct1"]),
            "pct_rank_gld_churn":pct_rank(cal.gld_churn,vals["gld_churn"]),
            "pct_rank_iau_churn":pct_rank(cal.iau_churn,vals["iau_churn"]),
            "pct_rank_gld_volume_ratio12":pct_rank(cal.gld_volume_ratio12,vals["gld_volume_ratio12"]),
            "pct_rank_etf_divergence":pct_rank(cal.etf_divergence,vals["etf_divergence"]),
        }
        fl=row_flags(r,th)
        z={
            "target":sr["target"],"origin":o,"ape_pct":float(sr["ape_pct"]),
            "ape_severity":sr["ape_severity"],
            "A":bool(sr["A"]),"B":bool(sr["B"]),"C":bool(sr["C"]),"D":bool(sr["D"]),"H":bool(sr["H"]),
            **vals,**ranks,**fl
        }
        rows.append(z)

    core=[r for r in rows if r["target"] in CORE_TARGETS]
    high=[r for r in rows if r["ape_severity"]=="HIGH"]
    normalmed=[r for r in rows if r["ape_severity"]!="HIGH"]

    flags=["ETF_OUTFLOW_Q10","ETF_GLD_OUTFLOW_Q10","ETF_IAU_OUTFLOW_Q10",
           "ETF_GLD_CHURN_Q90","ETF_IAU_CHURN_Q90","ETF_VOLUME_Q90","ETF_DIVERGENCE_Q90","ETF_STRESS_2PLUS"]
    scores={f:score(rows,f) for f in flags}
    core_scores={f:{
        "hits":sum(r[f] for r in core),
        "n":len(core),
        "hit_targets":[r["target"] for r in core if r[f]]
    } for f in flags}

    # Descriptive anomaly-count separation.
    by_sev={}
    for s in ["NORMAL","MEDIUM","HIGH"]:
        z=[r["ETF_ANOMALY_COUNT"] for r in rows if r["ape_severity"]==s]
        by_sev[s]={
            "n":len(z),
            "mean_anomaly_count":None if not z else float(np.mean(z)),
            "median_anomaly_count":None if not z else float(np.median(z)),
            "stress2plus_rate":None if not z else float(np.mean([x>=2 for x in z])),
        }

    out={
        "schema":"GOLD_MONTHLY_CHHHO_ETF_ANOMALY_SCREEN_V1_2026-09-30",
        "status":"COMPLETE",
        "sources":{
            "GLD":{"url":GLD_URL,"rows":len(gld),"first":str(gld.date.min().date()),"last":str(gld.date.max().date()),"bytes":len(gld_raw)},
            "IAU":{"url":IAU_URL,"rows":len(iau),"first":str(iau.date.min().date()),"last":str(iau.date.max().date()),"bytes":len(iau_raw)},
        },
        "calibration_period":f"{CAL_START}..{CAL_END}",
        "thresholds":th,
        "core_targets":CORE_TARGETS,
        "core_rows":core,
        "all_rows":rows,
        "high_rows":high,
        "scores":scores,
        "core_scores":core_scores,
        "severity_anomaly_summary":by_sev,
        "governance":{
            "origin_month_only":True,
            "target_month_etf_data_used":False,
            "wgc_monthly_report_used_as_predictor":False,
            "thresholds_calibrated_pre_2021":True,
            "threshold_retuning":False,
            "routing_tested":False,
        }
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("OUTPUT_GATE=PASS")
    print(json.dumps({
        "thresholds":th,
        "core_rows":core,
        "scores":scores,
        "core_scores":core_scores,
        "severity_anomaly_summary":by_sev,
        "stress_targets":[r["target"] for r in rows if r["ETF_STRESS_2PLUS"]],
    },sort_keys=True))

if __name__=="__main__": main()
