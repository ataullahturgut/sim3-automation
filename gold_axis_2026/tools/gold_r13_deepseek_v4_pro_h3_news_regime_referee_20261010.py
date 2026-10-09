"""Authenticated, bounded DeepSeek Pro independent mechanism review; only aggregate results shared."""
from pathlib import Path
import os,json,hashlib,urllib.request,urllib.error,datetime as dt
ROOT=Path(__file__).resolve().parents[1]
BRIEF=ROOT/"GOLD_R13_DEEPSEEK_V4_PRO_H3_D1_REGIME_NEWS_SANITIZED_SCIENTIFIC_BRIEF_20261010.md"
OUT=ROOT/"GOLD_R13_DEEPSEEK_V4_PRO_H3_NEWS_REGIME_20261010"
MODEL="deepseek-v4-pro"
def main():
    key=os.environ.get("DEEPSEEK_API_KEY","").strip()
    if not key or any(c.isspace() for c in key):raise RuntimeError("DEEPSEEK_API_KEY_NOT_SET")
    raw=BRIEF.read_bytes()
    if not 2000<=len(raw)<=11000:raise RuntimeError("BRIEF_SIZE_GATE")
    system=("Act as an adversarial financial-statistics research collaborator. Gold returns require causal "
       "time alignment, vintage-safe macro calendars, nested validation, and class-balanced signed predictions. "
       "Do not claim access to source-private data or pretend you executed any backtest. "
       "Explicitly call out target mismatches and impossibilities. Return only final substantive analysis.")
    user=("Run independent scientific ideation and ruthless critique with maximum 3 falsifiable innovational candidate mechanisms. "
       "Focus on prospective news-calendar risk interaction with 09TR and17TR forecasts, 3-trading-day change-point/regime "
       "and joint daily/H3 horizon consistency. For each, supply formulas, strict-asof feature/label clock, negative "
       "control, ablations, sample-size limitations, responsible promotion criteria, and WHY it could beat chance "
       "in BOTH UP and DOWN. Rank one exact feasible first test on original-source data. Do not invent data or results. "
       "Do not suggest extensive black-box model grid. Clearly distinguish ex-ante scheduled release calendar from "
       "post-release surprises. Challenge 2026 previous-month 64.34 BA transport collapse. Report in Turkish. "
       "Safe aggregate brief follows:\n\n"+raw.decode())
    max_tokens=3400
    if len((system+user).encode())>12800:raise RuntimeError("REQUEST_SIZE_GATE")
    payload={"model":MODEL,"messages":[{"role":"system","content":system},{"role":"user","content":user}],
          "thinking":{"type":"disabled"},"max_tokens":max_tokens,"stream":False}
    req=urllib.request.Request("https://api.deepseek.com/chat/completions",
       data=json.dumps(payload,ensure_ascii=False).encode(),
       headers={"Content-Type":"application/json","Accept":"application/json","Authorization":"Bearer "+key},
       method="POST")
    try:
        with urllib.request.urlopen(req,timeout=160) as response:x=json.loads(response.read(600000).decode())
    except urllib.error.HTTPError as e:raise RuntimeError("PRO_HTTP_"+str(e.code)) from None
    except (urllib.error.URLError, TimeoutError):raise RuntimeError("NETWORK_FAIL_OR_TIMEOUT") from None
    ans=((x.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
    finish=((x.get("choices") or [{}])[0].get("finish_reason"))
    good=x.get("model")==MODEL and finish=="stop" and len(ans)>900
    usage=x.get("usage") or {}
    receipt={"status":"PASS" if good else "INCOMPLETE","requested":MODEL,"returned":x.get("model"),
      "finish_reason":finish,"chars":len(ans),"request_sha256":hashlib.sha256(raw).hexdigest(),
      "token_cap":max_tokens,"usage":{k:v for k,v in usage.items() if k in ("prompt_tokens","completion_tokens","total_tokens")},
      "utc":dt.datetime.now(dt.timezone.utc).isoformat(),
      "no_secret_or_raw_quote_rows_transmitted":True,"provider_did_not_execute_backtest":True}
    Path(str(OUT)+"_RESULT.json").write_text(json.dumps(receipt,indent=2)+"\n")
    Path(str(OUT)+"_REVIEW.md").write_text("# DeepSeek V4 Pro — R13 D1/H3 news/regime/hybrid independent referee\n\n"
       "**Independent ideas, no execution claim.**\n\n"+ans+"\n")
    print("R13_DEEPSEEK_RECEIPT",receipt,flush=True)
    if not good:raise RuntimeError("PRO_ANSWER_NOT_COMPLETE")
if __name__=="__main__":
    try:main()
    except Exception as e:
        msg=str(e)[:100]
        Path(str(OUT)+"_FAILURE_QC.json").write_text(json.dumps({"status":"FAIL_CLOSED","reason":msg,"secret_printed":False})+"\n")
        print("R13_DEEPSEEK_FAIL",msg,flush=True);raise SystemExit(1)
