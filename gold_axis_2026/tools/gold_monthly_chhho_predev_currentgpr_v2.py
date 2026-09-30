from __future__ import annotations
import calendar, hashlib, io, json, math, os
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np, pandas as pd, requests

import vw_midas_msvr_successor_v1 as base
import vw_midas_anfis_stage3c_literature_v1 as chhho

REPO="iacoviel/iacoviel.github.io"
PATH="gpr_files/data_gpr_export.xls"
ORIGINS=["2021-10","2021-11","2021-12","2022-01","2022-02"]
HIGH_AE=63.06
NY=ZoneInfo("America/New_York")
MACRO_PATH=Path(__file__).resolve().parents[1]/"data"/"GOLD_MONTHLY_PREDEV_MACRO_RECON_V1_2026-09-30.json"

def mshift(m,d): return base.month_shift(m,d)

def cutoff(m):
    y,mo=map(int,m.split("-")); d=calendar.monthrange(y,mo)[1]
    return datetime(y,mo,d,17,0,0,tzinfo=NY).astimezone(timezone.utc)

def headers():
    h={"Accept":"application/vnd.github+json","User-Agent":"gold-currentgpr-backcast/2.0"}
    if os.environ.get("GH_TOKEN"): h["Authorization"]="Bearer "+os.environ["GH_TOKEN"]
    return h

def history():
    out=[]
    for page in range(1,5):
        r=requests.get(f"https://api.github.com/repos/{REPO}/commits",
            params={"path":PATH,"per_page":100,"page":page},headers=headers(),timeout=60)
        r.raise_for_status(); a=r.json()
        if not a: break
        for c in a:
            dt=datetime.fromisoformat(c["commit"]["committer"]["date"].replace("Z","+00:00")).astimezone(timezone.utc)
            out.append({"sha":c["sha"],"at":dt,"at_iso":dt.isoformat().replace("+00:00","Z"),
                        "msg":c["commit"].get("message","")})
    out.sort(key=lambda x:x["at"])
    return out

def fetch_snapshot(sha):
    u=f"https://raw.githubusercontent.com/{REPO}/{sha}/{PATH}"
    r=requests.get(u,headers={"User-Agent":"gold-currentgpr-backcast/2.0"},timeout=120)
    r.raise_for_status()
    if len(r.content)<10000: raise RuntimeError(f"SNAPSHOT_TOO_SMALL {len(r.content)}")
    return r.content

def parse_xls(raw):
    sheets=pd.read_excel(io.BytesIO(raw),sheet_name=None,header=None,engine="xlrd")
    candidates=[]
    for sn,df0 in sheets.items():
        for hr in range(min(25,len(df0))):
            vals=[str(v).strip().upper() if pd.notna(v) else "" for v in df0.iloc[hr].tolist()]
            exact=[i for i,v in enumerate(vals) if v=="GPR"]
            if not exact: continue
            dcands=[i for i,v in enumerate(vals) if v=="MONTH" or v=="DATE" or "MONTH" in v or "DATE" in v]
            dc=dcands[0] if dcands else 0; gc=exact[0]
            q=df0.iloc[hr+1:,[dc,gc]].copy(); q.columns=["date","gpr"]
            q["date"]=pd.to_datetime(q.date,errors="coerce")
            q["gpr"]=pd.to_numeric(q.gpr,errors="coerce")
            q=q.dropna().sort_values("date"); q=q[q.gpr>0].drop_duplicates("date",keep="last")
            if len(q)>=24: candidates.append((len(q),sn,hr,q))
    if not candidates: raise RuntimeError("EXACT_GPR_COLUMN_NOT_FOUND")
    candidates.sort(key=lambda x:x[0],reverse=True)
    _,sn,hr,q=candidates[0]
    out={pd.Timestamp(r.date).strftime("%Y-%m"):float(r.gpr) for r in q.itertuples(index=False)}
    return out,{"sheet":sn,"header_row_zero_based":hr,"n":len(q),"first":min(out),"last":max(out)}

def audit():
    hist=history(); cache={}; rows=[]
    for o in ORIGINS:
        cs=[c for c in hist if c["at"]<=cutoff(o)]
        if not cs:
            rows.append({"origin":o,"buildable":False,"status":"NO_CURRENT_METHOD_COMMIT"}); continue
        c=cs[-1]
        try:
            if c["sha"] not in cache:
                raw=fetch_snapshot(c["sha"]); h,meta=parse_xls(raw)
                cache[c["sha"]]={"hist":h,"meta":meta,"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw)}
            z=cache[c["sha"]]; req=mshift(o,-1); hh={k:v for k,v in z["hist"].items() if k<=req}
            ok=req in hh and len(hh)>=24
            rows.append({"origin":o,"buildable":ok,"status":"PASS" if ok else "P_MINUS_1_MISSING",
                         "commit_sha":c["sha"],"commit_at":c["at_iso"],"commit_msg":c["msg"],
                         "required_month":req,"required_value":hh.get(req),"history_n":len(hh),
                         "history_first":min(hh) if hh else None,"history_last":max(hh) if hh else None,
                         "snapshot_sha256":z["sha256"],"snapshot_bytes":z["bytes"],"parse_meta":z["meta"],
                         "_history":hh if ok else None})
        except Exception as e:
            rows.append({"origin":o,"buildable":False,"status":"PARSE_FAIL","commit_sha":c["sha"],
                         "commit_at":c["at_iso"],"error":repr(e)})
    return rows

def load_macro():
    p=json.loads(MACRO_PATH.read_text())
    out={}
    for k,rows in p["rows"].items():
        df=pd.DataFrame(rows,columns=["date","value"]); df["date"]=pd.to_datetime(df.date); df["value"]=pd.to_numeric(df.value)
        out[k]=df.dropna().sort_values("date")
    return out

def mm(df,m,lag):
    p=pd.Period(m,freq="M"); cut=p.end_time.normalize()-pd.Timedelta(days=lag)
    z=df[(df.date.dt.to_period("M")==p)&(df.date<=cut)]
    return np.nan if z.empty else float(z.value.mean())

def macro_states():
    z=load_macro(); out={}
    for m in ORIGINS:
        pm=mshift(m,-1)
        nc,npv=mm(z["DGS10"],m,2),mm(z["DGS10"],pm,2)
        rc,rpv=mm(z["DFII10"],m,2),mm(z["DFII10"],pm,2)
        uc,upv=mm(z["DTWEXBGS"],m,7),mm(z["DTWEXBGS"],pm,7)
        out[m]={"nom10_change":nc-npv,"real10_change":rc-rpv,"broad_usd_logchg":math.log(uc/upv)}
    return out

def samples_with_hist(b,target,h):
    out={}
    for t in base.month_range("2010-03",target):
        try: out[t]=base.sample_for_target(b,t,h,lag_gpr=True)
        except RuntimeError: pass
    if target not in out: raise RuntimeError(f"TARGET_NOT_BUILDABLE {target}")
    return out

def state(b,o):
    pm=mshift(o,-1); p3=mshift(o,-3); d={}
    for metal in base.METALS:
        M=b.monthly_metal[metal]; d[metal+"_r1"]=math.log(M[o]/M[pm])
    d["Gold_r3"]=math.log(b.monthly_metal["Gold"][o]/b.monthly_metal["Gold"][p3])
    ma12=np.mean([b.monthly_metal["Gold"][mshift(o,-k)] for k in range(1,13)])
    d["Gold_vs_ma12"]=b.monthly_metal["Gold"][o]/ma12-1
    return d

def alarms(s,pred,m):
    g=s["Gold_r1"]; oth=[s[x+"_r1"] for x in ("Silver","Platinum","Palladium")]
    opp=sum(x*g<0 for x in oth)
    A=np.sign(pred)==np.sign(g) and abs(g)<.02 and opp>=2
    C=g<0 and m["nom10_change"]<0 and m["real10_change"]<0 and abs(pred)<.01
    D=g>.03 and m["broad_usd_logchg"]>0 and m["nom10_change"]>0 and m["real10_change"]>0 and pred>0
    E=s["Gold_vs_ma12"]>.20 and abs(pred-g)>.05
    G=s["Gold_r3"]<=-.10
    return {"A":bool(A),"C":bool(C),"D":bool(D),"E":bool(E),"G":bool(G),"hard_alarm":bool(A or C or D or E or G),"opposite_metals":int(opp)}

def main():
    au=audit(); passing=[x for x in au if x["buildable"]]
    print("SOURCE_AUDIT",json.dumps([{k:v for k,v in x.items() if k!="_history"} for x in au],sort_keys=True))
    if not passing: raise RuntimeError("NO_BUILDABLE_CURRENT_METHOD_ORIGINS")
    b=base.load_data(os.environ["NEON_DATABASE_URL"]); ms=macro_states(); rows=[]
    for x in passing:
        o=x["origin"]; t=mshift(o,1); h=x["_history"]
        ss=samples_with_hist(b,t,h); pred,n,diag=chhho.select(ss,t,"CHHHO"); pg=float(pred[0])
        fc=float(b.core_gold[o]*math.exp(pg)); act=float(b.core_gold[t]); ae=abs(fc-act); ape=ae/act*100
        st=state(b,o); al=alarms(st,pg,ms[o])
        rows.append({"origin":o,"target":t,"source_commit_sha":x["commit_sha"],"source_commit_at":x["commit_at"],
                     "required_gpr_month":x["required_month"],"required_gpr_value":x["required_value"],
                     "pred_log_return_gold":pg,"forecast":fc,"actual":act,"ae":ae,"ape_pct":ape,
                     "high_error":bool(ae>HIGH_AE),"train_rows":int(n),"diag":diag,**st,**ms[o],**al})
    for x in au: x.pop("_history",None)
    tp=sum(r["hard_alarm"] and r["high_error"] for r in rows); fp=sum(r["hard_alarm"] and not r["high_error"] for r in rows)
    fn=sum((not r["hard_alarm"]) and r["high_error"] for r in rows)
    out={"schema":"GOLD_MONTHLY_CHHHO_PREDEV_CURRENTGPR_V2_2026-09-30","status":"COMPLETE",
         "authority_commit":"ae009acc67cbf22c3cd6edaa7e934067823db260",
         "source":{"repo":REPO,"path":PATH},"source_audit":au,"rows":rows,
         "summary":{"n":len(rows),"high_error_n":sum(r["high_error"] for r in rows),
                    "alarms":sum(r["hard_alarm"] for r in rows),"hits":tp,"false_alarms":fp,"misses":fn,
                    "precision":None if tp+fp==0 else tp/(tp+fp),"recall":None if tp+fn==0 else tp/(tp+fn)},
         "per_alarm":{a:{"events":sum(r[a] for r in rows),"hits":sum(r[a] and r["high_error"] for r in rows),
                          "false_alarms":sum(r[a] and not r["high_error"] for r in rows),
                          "targets":[r["target"] for r in rows if r[a]]} for a in "ACDEG"},
         "governance":{"same_methodology_current_gpr":True,"threshold_retuning":False,"routing_tested":False}}
    Path("GOLD_MONTHLY_CHHHO_PREDEV_CURRENTGPR_V2_2026-09-30.json").write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("OUTPUT_GATE=PASS")
    print(json.dumps({"summary":out["summary"],"per_alarm":out["per_alarm"],
                      "rows":[{k:r[k] for k in ("target","origin","ae","ape_pct","A","C","D","E","G")} for r in rows]},sort_keys=True))
if __name__=="__main__": main()
