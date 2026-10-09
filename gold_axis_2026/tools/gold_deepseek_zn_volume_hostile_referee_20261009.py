"""One-call DeepSeek technical referee of GPT-6's *specific preregistered* ZN hypothesis.
No open-ended model brainstorming. Aggregate-only public-safe signed-source data.
"""
from __future__ import annotations
import os, json, hashlib, datetime as dt, urllib.request, urllib.error
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"GOLD_ZN_VOLUME_CONDITIONED_NIGHT_SIGN_HYPOTHESIS_PREREG_20261009.md"
STEM=ROOT/"GOLD_DEEPSEEK_ZN_VOLUME_FOCUSED_REFEREE_20261009"
MODEL="deepseek-flash"; MAX_TOKENS=2600
def main():
    key=os.getenv("DEEPSEEK_API_KEY","").strip()
    if not key or any(c.isspace() for c in key):raise RuntimeError("KEY_MISSING_OR_INVALID")
    if not SOURCE.exists() or not SOURCE.resolve().is_relative_to(ROOT.resolve()):
        raise RuntimeError("SAFE_SOURCE_MISSING")
    b=SOURCE.read_bytes()
    if not 2500<=len(b)<=11500:raise RuntimeError("SAFE_SOURCE_SIZE")
    system=(
      "You are a technical and skeptical financial-econometrics journal reviewer. "
      "Your job is NOT to come up with a new strategy and NOT to flatter. "
      "You are reviewing the author's fully formulated new study. "
      "Do not claim any market results beyond the included coverage counts. "
      "Be stringent on origin clocks, source semantics, novelty versus CAVS/CME3-K25, "
      "real independence of total futures volume, and false-DOWN alerts. "
      "Only final concise review, no fabricated citations.")
    question=(
      "DO NOT SUGGEST GENERIC MODELS. Critically REVIEW THE ATTACHED ZN-VPT "
      "preregistered mathematical hypothesis. Specifically answer: "
      "(1) Does ZN 15→16 return × historical volume surprise carry possible "
      "incremental overnight XAU signed information beyond same-date rZN, "
      "rXAU, |rZN| and volatility? Name the precise falsifiable null. "
      "(2) Point to every time/source leak, rollover, trade-volume seasonality, "
      "asset-correlation or rarity failure; distinguish real from theoretical. "
      "(3) Compare with the existing PREVIOUSLY EXECUTED CME3-K25, PRAMV, "
      "BSC8, and untrained CAVS; is this materially new or redundant? "
      "(4) Give the MINIMUM decisive study on actual 2023/2024 development "
      "and already-inspected 2025 retrospective, including matched SAME "
      "DATES and coverage-aware DOWN precision/recall, MONTH-shuffle negative "
      "control, and correction for selecting volume threshold/cohort. "
      "(5) Explicit KEEP as high-risk testable experiment or REJECT/REVISE "
      "with a mathematical reason. Do not propose alternative model families "
      "or numerical success without actual source data. Max 950 words.\n\n"
      "AUTHOR PRE-RESULT PREREGISTRATION:\n"+b.decode("utf-8"))
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
      "# DeepSeek independent technical critique of author-pre-registered ZN volume hypothesis\n\n"
      "**External LLM text, not market evidence.**\n\n"+answer+"\n",encoding="utf-8")
    print("FOCUSED_ZN_REFEREE",result["status"],"chars",len(answer),
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
      print("FOCUSED_ZN_REVIEW_FAILED",why,flush=True)
      raise SystemExit(1)
