"""One costly but hard-capped independent DeepSeek V4-Pro scientific hypothesis audit.
Consumes ONLY explicitly vetted aggregate text; NEVER external raw market data.
One chat request maximum, high reasoning mode, no retries, no background loop.
No actual investment advice, data acquisition, or code execution by LLM.
"""
from __future__ import annotations
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
BRIEF = ROOT / "GOLD_DEEPSEEK_STAGE2_EXTERNAL_SAFE_RESEARCH_BRIEF_20261009.md"
STEM = ROOT / "GOLD_DEEPSEEK_V4_PRO_HIGH_EFFORT_RESEARCH_20261009"
MODEL = "deepseek-v4-pro"
MAX_OUTPUT = 8500
MAX_PROMPT_BYTES = 10000
# Official maximum weekday peak per-million-token prices as of 2026-10-09:
# cache-miss input $1.32, output $3.96. Require upper bound <= $0.05.
MAX_PEAK_ESTIMATE_USD = (MAX_PROMPT_BYTES * 1.32 + MAX_OUTPUT * 3.96) / 1000000
assert MAX_PEAK_ESTIMATE_USD <= 0.05

def main():
    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key or any(ch.isspace() for ch in api_key):
        raise RuntimeError("DEEPSEEK_SECRET_MISSING_OR_INVALID")
    if not BRIEF.exists() or not BRIEF.resolve().is_relative_to(ROOT.resolve()):
        raise RuntimeError("ALLOWLIST_BRIEF_MISSING")
    raw = BRIEF.read_bytes()
    if not (2000 <= len(raw) <= 6000):
        raise RuntimeError("ALLOWLIST_BRIEF_BYTES_OUT_OF_POLICY")
    brief_hash = hashlib.sha256(raw).hexdigest()
    system = (
        "You are an independent scientific referee and financial econometrician, "
        "not a trading agent. We need falsifiable novel pre-origin signed predictive "
        "information beyond existing gold price models, not renamed price regressions. "
        "Never invent market measurements, authority citations, source availability "
        "or a numerical accuracy increase. Separate hypothesis from empirical result. "
        "If evidence is inadequate say BLOCK. Return only final scientific conclusions."
    )
    question = (
        "Use serious mathematical reasoning (high effort) and critique our negative "
        "experimental record below. Propose AT MOST TWO nonredundant approaches: "
        "(A) a small-capacity study truly executable on our EXISTING audited XAU "
        "2020-25 M15 BID/ASK and sparse CME 2023-26 H1 records, with exact clock, "
        "eligibility, and no hidden post-origin information; "
        "(B) a genuinely new independent directional input obtainable from an "
        "auditable PIT source if A logically cannot supply an edge. Avoid "
        "previous BSC-8, preopening quote repair, residual GC-minus-XAU trend, "
        "CME3 K25, PRAMV/CIG, confidence gates, old first-passage/volatility "
        "indicators, and generic HGB/ANN ensembles. Distinguish endpoint 17TR to "
        "next09TR from asymmetric barrier and 09TR to 17TR, and separate same-day "
        "macro surprise known-before-issue from future event knowledge. "
        "Prior reviewer invented 2020-22 GC for OLS even though GC archive starts "
        "2023, and conflated OLS residual with price-discovery leadership: DO "
        "NOT repeat either. Give exact equations, timestamped observable data "
        "fields, mechanistic reason for DOWN sign, absence-or-presence of genuine "
        "independent information, and rigorous prior-only model specification. "
        "Give head-to-head exact-date comparisons with price-only benchmark, "
        "negative controls, strong matched BA, DOWN precision/recall, action "
        "coverage, Brier, false DOWN alarms, rescue/break balance, calendar-month "
        "blocked uncertainty and a lockbox on dates not yet inspected. "
        "2025/2026 have ALREADY been seen, so NO new OOS claims. "
        "Critique your own preferred idea: strongest way it could FAIL, "
        "a concrete STOP test, and least-expensive decisive next trial. "
        "No claim of measured success. Be rigorous and concise, about 1200 words.\n\n"
        "SAFE AGGREGATE RESEARCH RECORD:\n" + raw.decode("utf-8")
    )
    prompt_bytes = len((system + question).encode("utf-8"))
    if prompt_bytes > MAX_PROMPT_BYTES:
        raise RuntimeError("PROMPT_EXCEEDS_PRICE_BOUND")
    headers = {"Authorization": "Bearer " + api_key,
               "Content-Type": "application/json", "Accept": "application/json"}
    req = urllib.request.Request(
        "https://api.deepseek.com/chat/completions",
        data=json.dumps({
            "model": MODEL,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": question}],
            "thinking": {"type": "enabled"},
            "reasoning_effort": "high",
            "max_tokens": MAX_OUTPUT,
            "stream": False
        }, ensure_ascii=False).encode("utf-8"),
        headers=headers, method="POST")
    # Intentional exactly ONE charged chat request. No transient automatic retries.
    try:
        with urllib.request.urlopen(req, timeout=210) as response:
            if response.status != 200:
                raise RuntimeError("PRO_PROVIDER_NON200")
            obj = json.loads(response.read(1000000).decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError("PRO_HTTP_" + str(exc.code)) from None
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError("PRO_PROVIDER_TRANSPORT_" + type(exc).__name__) from None
    choices = obj.get("choices") or []
    if not choices:
        raise RuntimeError("PRO_EMPTY_CHOICES")
    choice = choices[0]
    finish = choice.get("finish_reason")
    msg = choice.get("message") or {}
    answer = msg.get("content") or ""
    usage = obj.get("usage") or {}
    u = {k:int(v) for k,v in usage.items()
         if k in ("prompt_tokens","completion_tokens","total_tokens",
                  "prompt_cache_hit_tokens","prompt_cache_miss_tokens")
         and isinstance(v,int)}
    receipt = {
        "status": "PASS" if finish == "stop" and len(answer) >= 1000 else "INCOMPLETE",
        "provider_model_requested": MODEL,
        "provider_model_returned": obj.get("model"),
        "reasoning_effort_requested": "high",
        "thinking_enabled": True,
        "chat_calls_attempted": 1,
        "prompt_utf8_bytes": prompt_bytes,
        "output_token_cap": MAX_OUTPUT,
        "conservative_peak_cost_upper_bound_usd": round(MAX_PEAK_ESTIMATE_USD,6),
        "finish_reason": finish,
        "final_output_characters": len(answer),
        "usage": u,
        "original_safe_brief_sha256": brief_hash,
        "date_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "external_text_only_not_market_backtest": True,
        "no_raw_market_rows_or_secrets_sent": True,
        "no_production_model_promotion": True
    }
    (Path(str(STEM) + "_RESULT.json")).write_text(
        json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (Path(str(STEM) + "_REVIEW.md")).write_text(
        "# DeepSeek V4 Pro high-reasoning independent review (unverified hypotheses)\n\n"
        "Single call; model-generated text, **not** an executed forecasting model. "
        "Never treat any claimed success as evidence.\n\n" +
        answer + "\n", encoding="utf-8")
    print("PRO_SINGLE_CHAT_REVIEW_STATUS",receipt["status"],flush=True)
    print("PRO_RETURNED_MODEL",receipt["provider_model_returned"],flush=True)
    print("PRO_USAGE",u,flush=True)
    print("PRO_FINAL_CHARACTERS",len(answer),flush=True)
    if receipt["status"]!="PASS":
        raise RuntimeError("PRO_OUTPUT_INCOMPLETE_NO_RETRY")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        reason = str(exc)
        if not reason.startswith(("DEEPSEEK_","ALLOWLIST_","PROMPT_","PRO_")):
            reason = type(exc).__name__ + "_UNEXPECTED_ERROR"
        (Path(str(STEM) + "_FAILURE_QC.json")).write_text(
            json.dumps({"status":"FAIL_CLOSED","reason":reason[:160],
                        "no_secret_logging":True},indent=2)+"\n",
            encoding="utf-8")
        print("PRO_FAIL_CLOSED",reason,flush=True)
        raise SystemExit(1)
