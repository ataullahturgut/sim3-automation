"""One strictly capped DeepSeek V4 Pro scientific research critique on aggregate-only R6-R8 facts.
No raw prices/private records, credentials, personal identifiers, or provider code execution.
"""
from pathlib import Path
import os, json, datetime as dt, hashlib, urllib.request, urllib.error
ROOT=Path(__file__).resolve().parents[1]
IN=ROOT/"GOLD_R9_DEEPSEEK_V4_PRO_CPI_NFP_CAUSAL_RESEARCH_BRIEF_20261009.md"
OUT=ROOT/"GOLD_R9_DEEPSEEK_V4_PRO_CPI_NFP_CAUSAL_20261009"
MODEL="deepseek-v4-pro"
LIMIT=2600
# Conservative 2026-10-09 rate cap based on available Pro API prices, not guaranteed final invoice.
MAX_USD=0.025
def main():
    secret=os.environ.get("DEEPSEEK_API_KEY","").strip()
    if not secret or any(s.isspace() for s in secret): raise RuntimeError("PRO_API_SECRET_MISSING")
    raw=IN.read_bytes()
    if not 2500<=len(raw)<=8000: raise RuntimeError("SAFE_BRIEF_SIZE_INVALID")
    system=("You are an independent quant macroeconometric researcher and hostile referee. "
            "Give a SPECIFIC falsifiable new US CPI/NFP XAU signed price mechanism, "
            "or explicitly reject it if prepublication independent information is absent. "
            "Do not invent experimental results or promise success. Never propose a postrelease "
            "first-minute jump as a pre09 forecast. All 2025/26 already inspected. "
            "Return compact FINAL ANSWER only, no reasoning trace.")
    question=(
        "In <=1100 words, read the AGGREGATE prior failed tests. You previously suggested "
        "missing daily LBMA allocated flow for unrelated overnight, do NOT repeat that. "
        "Think as monetary economist and market microstructure/causal transport researcher. "
        "(1) propose ONE cheapest implementable new PRE08:45 signed 09-17 XAU information "
        "channel, maybe forecast DIFFERENCE between true PIT pre-release CPI/NFP nowcast and "
        "pre-release consensus. Must distinguish the genuine advance information from future "
        "actual/consensus, source-vintage unavailability and from known high-volatility calendar. "
        "(2) equation and exact original signal issuance timestamp, and source authority; "
        "(3) specify whether can ACTUALLY be backtested TODAY with listed historical sources. "
        "If not, name precise low-cost data and 1 gating feasibility test, no fake scores. "
        "(4) specify minimalist model and SAME DATE price-only and constant direction controls "
        "on 2023-24 development, inspected2025, inspected2026; false DOWN, BA, Brier and effect. "
        "(5) explain 2026 event apparent B4 success, class imbalance, after1min 50% failure. "
        "(6) list strongest 2 mechanisms for this idea to fail and a definite reject gate. "
        "No generic classifiers, selectors, NQ/ZN/CL failed indicators, threshold fitting, "
        "physical LBMA unlicensed data, arbitrary claimed model improvement. "
        "Provide actual thought-out alternative IF original macro vintages irretrievable. "
        "Distinguish direction from risk and do not alter user's 09-17/17-next09 horizons.\n\n"
        +raw.decode("utf-8"))
    nbytes=len((system+question).encode("utf-8"))
    estimate=(nbytes*1.32+LIMIT*3.96)/1e6
    if nbytes>10500 or estimate>MAX_USD: raise RuntimeError("MODEL_PRICE_GUARD")
    payload={"model":MODEL,"messages":[{"role":"system","content":system},{"role":"user","content":question}],
             "thinking":{"type":"disabled"},"max_tokens":LIMIT,"stream":False}
    req=urllib.request.Request("https://api.deepseek.com/chat/completions",
      data=json.dumps(payload,ensure_ascii=False).encode("utf-8"),
      headers={"Authorization":"Bearer "+secret,"Content-Type":"application/json","Accept":"application/json"},
      method="POST")
    try:
      with urllib.request.urlopen(req,timeout=125) as rsp: obj=json.loads(rsp.read(500000).decode())
    except urllib.error.HTTPError as e: raise RuntimeError("PRO_HTTP_"+str(e.code)) from None
    except (urllib.error.URLError,TimeoutError): raise RuntimeError("PRO_TIMEOUT_NETWORK") from None
    items=obj.get("choices") or []
    if not items: raise RuntimeError("PRO_NO_CHOICES")
    first=items[0];msg=first.get("message") or {};answer=msg.get("content") or ""
    usage=obj.get("usage") or {}; u={x:int(usage[x]) for x in
      ("prompt_tokens","completion_tokens","total_tokens","prompt_cache_miss_tokens","prompt_cache_hit_tokens")
      if isinstance(usage.get(x),int)}
    verdict="PASS" if first.get("finish_reason")=="stop" and len(answer)>900 and obj.get("model")==MODEL else "FAIL_INCOMPLETE_OR_MODEL_MISMATCH"
    receipt={"status":verdict,"requested":MODEL,"returned":obj.get("model"),"finish_reason":first.get("finish_reason"),
             "usage":u,"query_bytes":nbytes,"max_completion_tokens":LIMIT,"input_brief_sha256":hashlib.sha256(raw).hexdigest(),
             "peak_usd_upper_estimate":round(estimate,6),"provider_date_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
             "raw_prices_or_secrets_transmitted":False,"model_market_experiments_performed_by_deepseek":False}
    Path(str(OUT)+"_RESULT.json").write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    Path(str(OUT)+"_REVIEW.md").write_text("# Independent DeepSeek V4-Pro R9 original-response referee — hypothesis only\n\n"+
      "Model text is NOT verified empirical model improvement. 2025/26 already inspected.\n\n"+answer+"\n")
    print("R9_PRO_STATUS",verdict,"FINISH",first.get("finish_reason"),
        "RETURNED_MODEL",obj.get("model"),"TOKENS",u,"CHARS",len(answer),flush=True)
    if verdict!="PASS":raise RuntimeError("PRO_FINISH_INCOMPLETE")
if __name__=="__main__":
  try:main()
  except Exception as e:
    reason=str(e)
    if len(reason)>120:reason=type(e).__name__
    Path(str(OUT)+"_FAILURE_QC.json").write_text(json.dumps({"status":"FAIL_CLOSED","reason":reason,"no_secret_logged":True},indent=2)+"\n")
    print("R9_PRO_FAIL",reason,flush=True)
    raise SystemExit(1)
