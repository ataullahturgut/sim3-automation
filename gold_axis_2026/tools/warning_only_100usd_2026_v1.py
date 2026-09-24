from __future__ import annotations
import argparse,csv,json,math,os
from datetime import date
from pathlib import Path
import numpy as np, psycopg

TABLE="public.xau_intraday_research_cache_5m"; TZ="America/New_York"; MIN_BARS=240

def db_url():
    v=os.environ.get("NEON_DATABASE_URL","").strip()
    if not v: raise RuntimeError("NEON_DATABASE_URL_MISSING")
    return v

def nearest_rank(a,q):
    a=np.asarray(a,float); k=max(1,min(len(a),int(math.ceil(q*len(a)))))
    return float(np.sort(a)[k-1])

def load_external(path):
    out=[]
    with open(path,newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            d=date.fromisoformat(r["date"])
            if d.year<=2021: out.append((d,float(r["close_mid"]),float(r["dr_5m"])))
    return out

def load_governed():
    sql=f"""
    with b as (
      select (observation_ts at time zone '{TZ}')::date d, observation_ts,
             close::double precision close,
             lag(close::double precision) over(partition by (observation_ts at time zone '{TZ}')::date order by observation_ts) prev_close
      from {TABLE}
      where observation_ts >= '2020-01-01'::timestamptz
        and extract(isodow from (observation_ts at time zone '{TZ}')) between 1 and 5
    ), intr as (
      select d,observation_ts,close,
             case when prev_close is not null and prev_close>0 then ln(close/prev_close) end r
      from b
    )
    select d,count(*)::int,
           (array_agg(close order by observation_ts desc))[1]::double precision close,
           coalesce(sum(case when r<=0 then r*r else 0 end),0)::double precision dr
    from intr group by d having count(*)>={MIN_BARS} order by d
    """
    with psycopg.connect(db_url(),autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("set default_transaction_read_only=on"); cur.execute(sql); raw=cur.fetchall()
    return [(d,float(c),float(dr)) for d,n,c,dr in raw if math.isfinite(float(c)) and float(c)>0]

def build(ext,gov):
    a=[x for x in ext if x[0].year<=2021]+[x for x in gov if x[0].year>=2022]
    a=sorted(a)
    ds=[x[0] for x in a]; close=np.array([x[1] for x in a],float); dr=np.array([x[2] for x in a],float)
    sd=np.sqrt(dr); rows=[]
    for i in range(21,len(ds)-1):
        t=i+1
        rows.append({"origin_date":ds[i],"target_date":ds[t],
          "sd_d":float(sd[i]),"sd_w":float(np.mean(sd[i-4:i+1])),"sd_m":float(np.mean(sd[i-21:i+1])),
          "target_sd":float(sd[t]),"target_dr":float(dr[t]),"ret":float(math.log(close[t]/close[i])),
          "close0":float(close[i]),"close1":float(close[t])})
    return rows,ds,close

def fit_predict(train,test,w=None):
    use=train if w is None else train[-w:]
    X=np.array([[1,r["sd_d"],r["sd_w"],r["sd_m"]] for r in use],float)
    y=np.array([r["target_sd"] for r in use],float)
    b=np.linalg.lstsq(X,y,rcond=None)[0]
    Xt=np.array([[1,r["sd_d"],r["sd_w"],r["sd_m"]] for r in test],float)
    pred=(Xt@b)**2; thr=nearest_rank([r["target_dr"] for r in use],.80)
    return pred,thr,len(use)

def simulate(test,pred,thr):
    wealth=100.0; invested_days=0; cash_days=0; alerts=0
    path=[]
    for r,p in zip(test,pred):
        alert=p>=thr
        if alert:
            cash_days+=1; alerts+=1
        else:
            wealth*=math.exp(r["ret"]); invested_days+=1
        path.append({"date":r["target_date"].isoformat(),"alert":bool(alert),"ret":r["ret"],"wealth":wealth})
    return {"final_value":wealth,"return_pct":(wealth/100-1)*100,"alerts":alerts,"invested_days":invested_days,"cash_days":cash_days,"path":path}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--external-spine",required=True); ap.add_argument("--out",required=True)
    args=ap.parse_args(); out=Path(args.out); out.mkdir(exist_ok=True)
    ext=load_external(args.external_spine); gov=load_governed(); rows,ds,close=build(ext,gov)
    train=[r for r in rows if r["target_date"]<=date(2025,12,31)]
    test=[r for r in rows if date(2026,1,1)<=r["target_date"]]
    if not test: raise RuntimeError("NO_2026")
    ep,eth,en=fit_predict(train,test,None); wp,wth,wn=fit_predict(train,test,500)
    e=simulate(test,ep,eth); w=simulate(test,wp,wth)
    bh=100.0
    for r in test: bh*=math.exp(r["ret"])
    result={"identity":"GOLD_CONTROL_2026_100USD_WARNING_ONLY_SIM_V1",
      "last_target_date":test[-1]["target_date"].isoformat(),"n_days":len(test),
      "rule":"Start 100 USD. If policy forecasts HIGH-RISK for target day, hold cash for that day; otherwise hold gold. No short/leverage/costs.",
      "buy_and_hold":{"final_value":bh,"return_pct":(bh/100-1)*100},
      "EXPANDING":{"formation_n":en,"threshold":eth,**{k:v for k,v in e.items() if k!="path"}},
      "W500":{"formation_n":wn,"threshold":wth,**{k:v for k,v in w.items() if k!="path"}},
      "governance":{"stress_only":True,"selection":False,"retuning":False,"production_writes":False}}
    (out/"GOLD_CONTROL_2026_100USD_WARNING_ONLY_SIM_V1_RESULT_2026-09-24.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))

if __name__=="__main__": main()
