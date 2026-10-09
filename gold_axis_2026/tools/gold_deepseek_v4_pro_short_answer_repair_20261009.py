"""Single strictly budgeted Pro final-answer repair after high-reasoning token exhaustion.
External data limited to user-approved aggregate brief, no secret or raw rows.
"""
from pathlib import Path
import os, json, hashlib, datetime as dt, urllib.request, urllib.error
ROOT=Path(__file__).resolve().parents[1]
BRIEF=ROOT/"GOLD_DEEPSEEK_PRO_REPAIR_SAFE_BRIEF_20261009.md"
FIRST=ROOT/"GOLD_DEEPSEEK_V4_PRO_HIGH_EFFORT_RESEARCH_20261009_RESULT.json"
STEM=ROOT/"GOLD_DEEPSEEK_V4_PRO_REPAIRED_RESEARCH_20261009"
MODEL="deepseek-v4-pro"
MAX_OUTPUT=2400
MAX_PROMPT_BYTES=3000
PEAK_IN=1.32
PEAK_OUT=3.96
def main():
    key=os.environ.get("DEEPSEEK_API_KEY","").strip()
    if not key or any(x.isspace() for x in key):
        raise RuntimeError("SECRET_MISSING")
    if not BRIEF.exists() or not FIRST.exists():
        raise RuntimeError("SOURCE_RECEIPT_MISSING")
    raw=BRIEF.read_bytes()
    if not (1000<=len(raw)<=1700):
        raise RuntimeError("SAFE_BRIEF_INVALID")
    initial=json.loads(FIRST.read_text(encoding="utf-8"))
    u0=initial.get("usage") or {}
    if initial.get("status")!="INCOMPLETE" or initial.get("provider_model_returned")!=MODEL:
        raise RuntimeError("PRIOR_PRO_STATUS_UNEXPECTED")
    system=("Act as a rigorous econometrics referee, not a trading adviser. "
            "Return ONLY concise final answer. No citations invented, no made-up data, "
            "no profit guarantee; admit impossible signals or unavailable feeds.")
    question=(
        "DeepSeek V4-Pro HIGH reasoning previously exhausted 8500 output tokens "
        "without a final answer. This ONE repair call uses thinking DISABLED. "
        "Do not reason aloud. IN AT MOST 600 WORDS, give 1 BEST genuinely distinct "
        "signed gold direction causal mechanism or a rigorous NO-NEW-ALPHA verdict. "
        "Use the exact data availability in brief. State (1) novel independent "
        "pre-decision signal and its source, (2) equation, (3) 17->next09 "
        "timing and label maturity, (4) minimal matched-date test and negative "
        "control, (5) STOP condition, (6) whether experiment can be executed "
        "today. No regression fit on missing 2020-22 GC; no post-17 surprises. "
        "Reject rebranded quote spread, GC-minus-spot own-price difference, "
        "CIG/PRAMV, and threshold tuning on 2025/26. "
        "Never report unobserved accuracy. Use plain final response only.\n\n"
        +raw.decode("utf-8")
    )
    prompt_bytes=len((system+question).encode("utf-8"))
    if prompt_bytes>MAX_PROMPT_BYTES:
        raise RuntimeError("PROMPT_PRICE_BOUND_EXCEEDED")
    prev_in=int(u0["prompt_tokens"])
    prev_out=int(u0["completion_tokens"])
    peak_total_max=((prev_in+MAX_PROMPT_BYTES)*PEAK_IN+
                    (prev_out+MAX_OUTPUT)*PEAK_OUT)/1000000
    if peak_total_max>0.05:
        raise RuntimeError("COMBINED_TWO_CALL_PEAK_PRICE_LIMIT")
    payload={
        "model":MODEL,
        "messages":[{"role":"system","content":system},{"role":"user","content":question}],
        "thinking":{"type":"disabled"},
        "max_tokens":MAX_OUTPUT,
        "stream":False
    }
    req=urllib.request.Request("https://api.deepseek.com/chat/completions",
        headers={"Authorization":"Bearer "+key,
                 "Content-Type":"application/json","Accept":"application/json"},
        data=json.dumps(payload,ensure_ascii=False).encode("utf-8"),
        method="POST")
    try:
        with urllib.request.urlopen(req,timeout=120) as rsp:
            data=json.loads(rsp.read(500000).decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError("HTTP_"+str(exc.code)) from None
    except (urllib.error.URLError,TimeoutError) as exc:
        raise RuntimeError("NETWORK_"+type(exc).__name__) from None
    choices=data.get("choices") or []
    if not choices: raise RuntimeError("NO_COMPLETION")
    choice=choices[0]
    msg=choice.get("message") or {}
    answer=msg.get("content") or ""
    reason=choice.get("finish_reason")
    usage=data.get("usage") or {}
    u={k:int(v) for k,v in usage.items()
       if k in ("prompt_tokens","completion_tokens","total_tokens",
                "prompt_cache_hit_tokens","prompt_cache_miss_tokens") and isinstance(v,int)}
    actual_peak_upper=((prev_in+int(u.get("prompt_tokens",MAX_PROMPT_BYTES)))*PEAK_IN+
        (prev_out+int(u.get("completion_tokens",MAX_OUTPUT)))*PEAK_OUT)/1000000
    receipt={"status":"PASS" if reason=="stop" and len(answer)>=900 else "INCOMPLETE",
      "requested_model":MODEL,"returned_model":data.get("model"),
      "thinking":"disabled_after_prior_reasoning_exhaustion",
      "chat_calls_this_run":1,"all_experiment_chat_calls":2,
      "finish_reason":reason,"final_response_chars":len(answer),
      "usage_this_call":u,"earlier_call_usage":u0,
      "two_call_peak_cost_upper_bound_usd":round(peak_total_max,6),
      "two_call_peak_cost_from_actual_tokens_usd":round(actual_peak_upper,6),
      "date_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
      "no_private_market_rows_or_secrets_transmitted":True,
      "no_executed_market_model":True}
    Path(str(STEM)+"_RESULT.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    Path(str(STEM)+"_REVIEW.md").write_text(
        "# DeepSeek V4-Pro nonthinking final-answer repair (hypotheses only)\n\n"
        "This is external textual advice, not a run of any gold model.\n\n"
        +answer+"\n",encoding="utf-8")
    print("PRO_SHORT_VERDICT",receipt["status"],"chars",len(answer),"usage",u,
          "peak_two_call_usd",round(actual_peak_upper,6),flush=True)
    if receipt["status"]!="PASS":raise RuntimeError("OUTPUT_INCOMPLETE_NO_MORE_RETRIES")
if __name__=="__main__":
    try:main()
    except Exception as exc:
        why=str(exc)
        if len(why)>100:why=type(exc).__name__
        Path(str(STEM)+"_FAILURE_QC.json").write_text(json.dumps({
            "status":"FAIL_CLOSED","reason":why,"no_secrets_logged":True},indent=2)+"\n",encoding="utf-8")
        print("PRO_SHORT_FAIL",why,flush=True)
        raise SystemExit(1)
