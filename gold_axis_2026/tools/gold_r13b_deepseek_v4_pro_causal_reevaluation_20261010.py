"""Causal repair: concise second independent DeepSeek V4 Pro challenge after incomplete R13."""
from pathlib import Path
import os,json,urllib.request,urllib.error,datetime as dt
ROOT=Path(__file__).resolve().parents[1]
O=ROOT/"GOLD_R13B_DEEPSEEK_V4_PRO_CAUSAL_REPAIR_20261010"
def main():
    key=os.environ.get("DEEPSEEK_API_KEY","").strip()
    if not key:raise RuntimeError("MISSING_SECRET")
    system=("You are an adversarial gold quant reviewer. Only recommend causally sound low-capacity H3/D1 forecast "
            "tests; never invent backtest scores, never leak any return observed after origin, "
            "and NEVER confuse retrospective regime labels with causal asof states. "
            "Maximum 750 Turkish words. No expanded derivation or long intro.")
    user=("Review your own earlier R13 suggestions that contain SEVERE FUTURE LEAKAGE: "
          "(1) current t DAY 09:00->17:00 actual return CANNOT enter a forecast issued t 09:00; use yesterday's DAY only. "
          "(2) H3 agreement A_{t-1}=same-sign(DAY at t-1,H3 end at t+2) CANNOT be available at t; only matured origins i with "
          "their 3-business-day target-end strictly before current issue time are legal; do NOT call t-1 valid! "
          "(3) do not use US macro CPI/NFP actual-surprise before 08:30 New York release, nor post hoc smoothed HMM regimes. "
          "Historical quote source 2020-25, source-qualified 2026, GVZ previous NY close, scheduled CPI/NFP/FOMC dates available. "
          "True outputs DAY 09→17 and H3 09→3-business-days 09, or 17→3business days 17, unknown labels overlap. "
          "Latest H3 09 source-tested path CBR BA2023/24/25/26 48.41/47.98/54.33/48.31; "
          "CBR+RV/GVZ 51.59/47.84/53.97/50.62; 17 H3 path55.21/50.69/54.02/53.14; "
          "09 H3 previous-month direction prior48.02/49.59/48.88/64.34. No champion. "
          "Give ONE highest-value EXACT falsifiable next experiment and one fallback, with formulas, ex-ante event/no-event "
          "and RV regimes, two-way direction and error metrics, preorigin maturation, folds2023-24 vs opened25/26, "
          "event-day calendar-vintage and permuted event negative controls, and abstain/selectivity gate."
          "Max 750 words; stop before answer truncation; no invented market outcomes.")
    payload={"model":"deepseek-v4-pro","messages":[{"role":"system","content":system},{"role":"user","content":user}],
             "thinking":{"type":"disabled"},"max_tokens":2800,"stream":False}
    req=urllib.request.Request("https://api.deepseek.com/chat/completions",data=json.dumps(payload,ensure_ascii=False).encode(),
      headers={"Content-Type":"application/json","Authorization":"Bearer "+key},method="POST")
    try:
      with urllib.request.urlopen(req,timeout=150) as resp: x=json.loads(resp.read(600000).decode())
    except urllib.error.HTTPError as e:raise RuntimeError("HTTP_"+str(e.code)) from None
    except (urllib.error.URLError,TimeoutError):raise RuntimeError("NETWORK_FAIL") from None
    ch=(x.get("choices") or [{}])[0]
    answer=(ch.get("message") or {}).get("content") or ""
    good=x.get("model")=="deepseek-v4-pro" and ch.get("finish_reason")=="stop" and len(answer)>500
    receipt={"status":"PASS" if good else "INCOMPLETE","requested":"deepseek-v4-pro","returned":x.get("model"),
      "finish":ch.get("finish_reason"),"chars":len(answer),"tokens":x.get("usage"),
      "utc":dt.datetime.now(dt.timezone.utc).isoformat(),"external_only_review_no_market_backtest":True}
    Path(str(O)+"_RESULT.json").write_text(json.dumps(receipt,indent=2)+"\n")
    Path(str(O)+"_REVIEW.md").write_text("# R13B genuine DeepSeek V4 Pro causal repair\n\n"+answer+"\n")
    print("R13B_DEEPSEEK",receipt["status"],receipt["finish"],receipt["chars"])
    if not good:raise RuntimeError("INCOMPLETE_REVIEW")
if __name__=="__main__":
    try:main()
    except Exception as e:
      Path(str(O)+"_FAILURE_QC.json").write_text(json.dumps({"status":"FAIL","reason":str(e)[:100]})+"\n")
      raise SystemExit(1)
