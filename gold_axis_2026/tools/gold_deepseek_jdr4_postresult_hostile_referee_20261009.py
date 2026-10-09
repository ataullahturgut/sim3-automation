"""One-call DeepSeek technical referee of GPT-6's *specific preregistered* ZN hypothesis.
No open-ended model brainstorming. Aggregate-only public-safe signed-source data.
"""
from __future__ import annotations
import os, json, hashlib, datetime as dt, urllib.request, urllib.error
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"GOLD_R3_POST_RESULT_DEEPSEEK_AGGREGATE_ONLY_BRIEF_20261009.md"
STEM=ROOT/"GOLD_DEEPSEEK_JDR4_POST_RESULT_REFEREE_20261009"
MODEL="deepseek-flash"; MAX_TOKENS=3200
def main():
    key=os.getenv("DEEPSEEK_API_KEY","").strip()
    if not key or any(c.isspace() for c in key):raise RuntimeError("KEY_MISSING_OR_INVALID")
    if not SOURCE.exists() or not SOURCE.resolve().is_relative_to(ROOT.resolve()):
        raise RuntimeError("SAFE_SOURCE_MISSING")
    b=SOURCE.read_bytes()
    if not 2500<=len(b)<=11500:raise RuntimeError("SAFE_SOURCE_SIZE")
    system=(
      "You are a hostile scientific referee in financial econometrics and "
      "market microstructure. You must DISPROVE weak claims when possible. "
      "Do not invent financial gains, cite fake papers, or suggest broad model lists. "
      "This is only an external critique, not an actual market experiment.")
    question=(
      "GPT-6 independently designed, preregistered and EXECUTED "
      "three signed XAU candidate mechanisms across two EXACT bank-decision "
      "execution horizons. Only JDR4, a purported 15-minute "
      "dominant-squared-return reversal in the preorigin 4h, has a "
      "SMALL positive DAY effect across historical years, yet nominal "
      "paired p-values are weak and the sample has been selected from "
      "many tried alternatives. Act as a hostile post-result "
      "journal referee, NOT a brainstorm partner. "
      "(1) Explain why JDR4 is not established gold jump "
      "detection at 15m sampling and offer a concrete 5m native "
      "event-time falsification. (2) Why naive month block CIs "
      "and pooled McNemar over inspected years do NOT confirm novelty. "
      "(3) How a 43-percent single-day share of zero-cost gross delta "
      "can undermine economic trust. (4) Propose 2 strict negative "
      "controls and a locked prospective 09 Istanbul forecast "
      "registration, down recall/false alarms, paired BA/Brier "
      "and bank spread gate. (5) Return a precise verdict "
      "KEEP_AS_PROSPECTIVE_CANDIDATE or REJECT_NOW. "
      "No invented numeric forecast results, no unrelated model proposals. "
      "At most 750 words. AGGREGATE SCIENCE BRIEF:\\n"
      +b.decode("utf-8"))
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
    print("JDR4_POSTRESULT_CRITIQUE",result["status"],"chars",len(answer),
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
      print("JDR4_POSTRESULT_REVIEW_FAILED",why,flush=True)
      raise SystemExit(1)
