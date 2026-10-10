"""R14 one authenticated genuine DeepSeek V4 Pro external expert debate; no market/private rows sent."""
from pathlib import Path
import os,json,urllib.request,urllib.error,datetime as dt,hashlib
ROOT=Path(__file__).resolve().parents[1]
BRIEF=ROOT/"GOLD_R14_PRO_CROSSMETAL_GPR_REGIME_BRIEF_20261010.md"
OUT=ROOT/"GOLD_R14_PRO_CROSSMETAL_GPR_REGIME_REVIEW_20261010"
MODEL="deepseek-v4-pro"
def run():
    key=os.environ.get("DEEPSEEK_API_KEY","").strip()
    if not key or any(c.isspace() for c in key):raise RuntimeError("MISSING_OR_INVALID_SECRET")
    raw=BRIEF.read_bytes()
    if not 3000<len(raw)<12000:raise RuntimeError("SANITIZED_BRIEF_GATE")
    system=("You are a critical independent scientific econometrician. "
       "Challenge gold cross-metal GPR causal mechanisms and propose ONE mathematically falsifiable "
       "origin-safe low-capacity signed H3 bank-time test. Never fabricate empirical results. "
       "Explicitly reject unsound source-publication, target maturity, and future GPR/HMM leakage. "
       "Be concise and use Turkish; final answer only, max ~900 words.")
    user=("Evaluate the aggregate evidence and propose a novel sign-predictive Gold-minus-industrial-metals "
       "innovation conditional on legally published GPR regime (possible coefficient inversion under high risk), "
       "but attack this idea if economically implausible. Compare H3 vs DAY as separate target and no pseudo replication. "
       "Give formulas, exact data source/clock and interaction, minimum sample gates, frozen 2023/24 train and "
       "2025/26 already-opened transport, and true negative controls. Two strongest reason it could fail. "
       "Never confuse low-frequency monthly-average ChHHO with the H3 direction target. "
       "BRIEF:\n"+raw.decode())
    pay={"model":MODEL,"messages":[{"role":"system","content":system},{"role":"user","content":user}],
      "thinking":{"type":"disabled"},"max_tokens":2800,"stream":False}
    req=urllib.request.Request("https://api.deepseek.com/chat/completions",
      data=json.dumps(pay,ensure_ascii=False).encode(),
      headers={"Content-Type":"application/json","Accept":"application/json","Authorization":"Bearer "+key},
      method="POST")
    try:
      with urllib.request.urlopen(req,timeout=160) as rsp:j=json.loads(rsp.read(700000).decode())
    except urllib.error.HTTPError as e:raise RuntimeError("HTTP_"+str(e.code)) from None
    except (urllib.error.URLError,TimeoutError):raise RuntimeError("TIMEOUT_OR_NETWORK_FAIL") from None
    z=(j.get("choices") or [{}])[0]
    answer=(z.get("message") or {}).get("content") or ""
    good=j.get("model")==MODEL and z.get("finish_reason")=="stop" and len(answer)>500
    receipt={"status":"PASS" if good else "INCOMPLETE","requested":MODEL,"returned":j.get("model"),
      "finish":z.get("finish_reason"),"chars":len(answer),
      "usage":{k:v for k,v in (j.get("usage") or {}).items() if k in("prompt_tokens","completion_tokens","total_tokens")},
      "brief_sha256":hashlib.sha256(raw).hexdigest(),"utc":dt.datetime.now(dt.timezone.utc).isoformat(),
      "no_private_market_rows_or_secrets_shared":True,"deepseek_has_not_executed_market_test":True}
    Path(str(OUT)+"_RESULT.json").write_text(json.dumps(receipt,indent=2)+"\n")
    Path(str(OUT)+"_REVIEW.md").write_text("# Real DeepSeek V4 Pro R14 external independent research opinion\n"
      "**Hypotheses only; no executed backtest by DeepSeek.**\n\n"+answer+"\n")
    print("R14_DEEPSEEK_STATUS",receipt)
    if not good:raise RuntimeError("INCOMPLETE_PRO_OUTPUT")
if __name__=="__main__":
    try:run()
    except Exception as e:
      Path(str(OUT)+"_FAILURE_QC.json").write_text(json.dumps({"status":"FAIL_CLOSED","reason":str(e)[:90],"secrets_logged":False})+"\n")
      print("R14_DEEPSEEK_FAILED",str(e)[:90]);raise SystemExit(1)
