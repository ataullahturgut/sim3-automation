"""One-call DeepSeek technical referee of GPT-6's *specific preregistered* ZN hypothesis.
No open-ended model brainstorming. Aggregate-only public-safe signed-source data.
"""
from __future__ import annotations
import os, json, hashlib, datetime as dt, urllib.request, urllib.error
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"GOLD_R4_EURJPY_USD_COMMON_FACTOR_SIGN_AUDIT_PREREG_20261009.md"
STEM=ROOT/"GOLD_DEEPSEEK_FX2_HOSTILE_PRERESULT_REVIEW_20261009"
MODEL="deepseek-flash"; MAX_TOKENS=3200
def main():
    key=os.getenv("DEEPSEEK_API_KEY","").strip()
    if not key or any(c.isspace() for c in key):raise RuntimeError("KEY_MISSING_OR_INVALID")
    if not SOURCE.exists() or not SOURCE.resolve().is_relative_to(ROOT.resolve()):
        raise RuntimeError("SAFE_SOURCE_MISSING")
    b=SOURCE.read_bytes()
    if not 2500<=len(b)<=11500:raise RuntimeError("SAFE_SOURCE_SIZE")
    system=(
      "You are an independent macro-FX and gold-market microstructure peer "
      "reviewer. GPT-6 ALREADY researched, author-preregistered and sourced "
      "an exact-clock FX-signed hypothesis. Do not brainstorm generic models "
      "or invent data/accuracy. Be a hostile technical referee.")
    question=(
      "Critically audit this fully specified original EURUSD + USDJPY hourly "
      "USD-pressure consensus and gold DAY09TR->17TR/OVN17TR->next09TR "
      "overlay hypothesis BEFORE its 2023-25 history is scored. "
      "Ask whether USDJPY gold relation is intrinsically confounded "
      "by risk-off yen demand and US rates, and whether double agreement "
      "is genuinely independent information or correlated USD. "
      "Check exact local->UTC H1 start-label times (06/07 and14/15 TRT), "
      "bar-close knowledge, potential FX OTC feed publication and "
      "source/target-vintage mismatches: existing older LIT gold target "
      "has known 5 of 589 sign mismatches vs new same-vendor governed gold. "
      "Distinguish a high paired selective BA from artificially selected "
      "coverage; require paired full-coverage Brier only if honest calibrated "
      "probabilities exist, and exact DOWN recall false alarms. "
      "Compare explicitly with prior PRICE-only CME3-K25, ZN-VPT2, "
      "PRAMV and proposed CAVS: does FX add truly new market input "
      "or repeat a broad cross-asset idea? "
      "Give 1 exact negative control, 1 falsifiable sign stability test "
      "across 2023/24 and inspected 2025, and clear GO_FOR_EXPLORATION "
      "or BLOCK. DO NOT GIVE ANY FORECAST SCORE. "
      "No more than 700 words. AUTHOR'S SAFE PREREGISTRATION:\\n"+b.decode("utf-8"))
    req=urllib.request.Request("https://api.deepseek.com/chat/completions",
        headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},
        data=json.dumps({"model":MODEL,
          "messages":[{"role":"system","content":system},{"role":"user","content":question}],
          "thinking":{"type":"disabled"},"max_tokens":MAX_TOKENS,"stream":False
        },ensure_ascii=False).encode("utf-8"),method="POST")
    try:
      with urllib.request.urlopen(req,timeout=105) as resp:
        obj=json.loads(resp.read(500000).decode("utf-8"))
    except urllib.error.HTTPError as exc:raise RuntimeError("HTTP_"+str(exc.code)) from None
    except (urllib.error.URLError,TimeoutError) as exc:
        raise RuntimeError("TRANSPORT_"+type(exc).__name__) from None
    choice=(obj.get("choices") or [{}])[0]
    answer=(choice.get("message") or {}).get("content") or ""
    reason=choice.get("finish_reason")
    usage=obj.get("usage") or {}
    result={"status":"PASS" if reason=="stop" and len(answer)>1300 else "INCOMPLETE",
      "model_requested":MODEL,"model_returned":obj.get("model"),
      "calls":1,"finish_reason":reason,"answer_chars":len(answer),
      "prompt_digest_sha256":hashlib.sha256(b).hexdigest(),
      "token_usage":{k:int(v) for k,v in usage.items() if k in
        ("prompt_tokens","completion_tokens","total_tokens") and isinstance(v,int)},
      "date_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
      "hypothesis_review_only":True,"no_market_backtest_by_provider":True,
      "never_sent_private_quote_rows_or_secrets":True}
    Path(str(STEM)+"_RESULT.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    Path(str(STEM)+"_REVIEW.md").write_text(
      "# DeepSeek independent pre-result critique of original EURUSD/USDJPY dual confirmation\n\n"
      "**External LLM text, not market evidence.**\n\n"+answer+"\n",encoding="utf-8")
    print("FX2_HOSTILE_CRITIQUE",result["status"],"chars",len(answer),
          "usage",result["token_usage"],flush=True)
    if result["status"]!="PASS":raise RuntimeError("NO_FINISHED_REVIEW")
if __name__=="__main__":
    try:main()
    except Exception as exc:
      why=str(exc)
      if len(why)>100:why=type(exc).__name__
      Path(str(STEM)+"_FAILURE_QC.json").write_text(
        json.dumps({"status":"FAIL","safe_error":why},indent=2)+"\n",
        encoding="utf-8")
      print("FX2_HOSTILE_REVIEW_FAILED",why,flush=True)
      raise SystemExit(1)
