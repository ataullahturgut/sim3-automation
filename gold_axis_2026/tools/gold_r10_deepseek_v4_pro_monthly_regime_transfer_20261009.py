"""One real DeepSeek V4 Pro science review of monthly-to-session asof mechanism, NOT automated trading."""
from pathlib import Path
import json,os,urllib.request,urllib.error,hashlib,datetime as dt
ROOT=Path(__file__).resolve().parents[1]
BRIEF=ROOT/"GOLD_R10_DEEPSEEK_PRO_MONTHLY_REGIME_TRANSFER_SAFE_BRIEF_20261009.md"
OUT=ROOT/"GOLD_R10_DEEPSEEK_V4_PRO_MONTHLY_REGIME_TRANSFER_20261009"
MODEL="deepseek-v4-pro";CAP=3000;DOLLAR_MAX=0.026
def main():
 key=os.environ.get("DEEPSEEK_API_KEY","").strip()
 if not key or any(c.isspace() for c in key):raise RuntimeError("API_SECRET_MISSING")
 raw=BRIEF.read_bytes()
 if not 4000<=len(raw)<=11000:raise RuntimeError("SAFE_BRIEF_INVALID")
 system=("Independent critical macro-statistical researcher, tasked with finding only causally "
 "available and independently testable mechanisms for signed gold bank-window direction. "
 "Your previous model results and claims must be skeptical; avoid invented successes. "
 "Understand scale mismatch monthly-average level regression versus intraday bank signed returns. "
 "Return ONLY concise final empirical/scientific verdict.")
 question=(
  "Review the supplied sanitized actual monthly ChHHO and HMM evidence and weak short-horizon models. "
  "Give FIVE sections: (1) empirical and mechanistic explanation for monthly price-model success, "
  "strictly distinguishing smoothed monthly level, autocorrelated slow trend, 8 Au/Ag/Pt/Pd MR+GPR-VW "
  "complementarity, and 13D HMM context; avoid claiming monthly HMM state-label agreement proves "
  "return prediction; examine DEV N33/long-history fail and 2025/26 regime issues. "
  "(2) ONE strongest genuinely testable HIERARCHICAL MONTH-PRIOR/SESSION-RESIDUAL mechanism; "
  "exact two clock cuts, as-of features and mathematical model, limited degrees-of-freedom. "
  "(3) one ablation and negative control by 2023/24 vs already-inspected2025/26 and full same-date "
  "signed two windows BA, DOWN recall, rescue/break; month-shuffle null and fallibility. "
  "(4) precise source gate for each metal/GPR/HMM original monthly first-print vintage and "
  "no postissue month-end values; source feasibility TODAY. "
  "(5) strongest objection, hard stop rule, independent prospective qualification; "
  "must issue NO_PROMOTION if only hypothesized improvement. "
  "Avoid merely selecting bigger ML ensemble, adding rates VIX that already harmed monthly DEV, "
  "fitting 2026, manufacturing intraday silver data or saying monthly regime labels are known mid-month. "
  "No market quote rows were provided, so no invented test metrics. Limit 1400 words.\n\nSAFE RESEARCH BRIEF:\n"
  +raw.decode())
 nbytes=len((system+question).encode());est=(nbytes*1.32+CAP*3.96)/1e6
 if nbytes>12500 or est>DOLLAR_MAX:raise RuntimeError("PRICE_GATE_BLOCK")
 payload={"model":MODEL,"messages":[{"role":"system","content":system},{"role":"user","content":question}],
          "thinking":{"type":"disabled"},"max_tokens":CAP,"stream":False}
 req=urllib.request.Request("https://api.deepseek.com/chat/completions",
 data=json.dumps(payload,ensure_ascii=False).encode(),
 headers={"Content-Type":"application/json","Accept":"application/json","Authorization":"Bearer "+key},method="POST")
 try:
  with urllib.request.urlopen(req,timeout=145) as resp: x=json.loads(resp.read(700000).decode())
 except urllib.error.HTTPError as err: raise RuntimeError("PRO_HTTP_"+str(err.code)) from None
 except (urllib.error.URLError,TimeoutError):raise RuntimeError("NETWORK_TIMEOUT") from None
 cs=x.get("choices") or []
 if not cs:raise RuntimeError("PRO_NO_CHOICES")
 choice=cs[0]; answer=(choice.get("message") or {}).get("content") or "";finish=choice.get("finish_reason")
 good=finish=="stop" and len(answer)>=1100 and x.get("model")==MODEL
 u=x.get("usage") or {};use={k:v for k,v in u.items() if k in ("prompt_tokens","completion_tokens","total_tokens","prompt_cache_miss_tokens","prompt_cache_hit_tokens") and isinstance(v,int)}
 receipt={"status":"PASS" if good else "INCOMPLETE","requested":MODEL,"returned":x.get("model"),"finish":finish,
 "output_chars":len(answer),"usage":use,"prompt_bytes":nbytes,"token_cap":CAP,"peak_cost_estimated_upper_usd":round(est,6),
 "safe_input_sha256":hashlib.sha256(raw).hexdigest(),"utc":dt.datetime.now(dt.timezone.utc).isoformat(),
 "provider_did_not_run_market_experiment":True,"no_private_market_rows_or_secrets_sent":True}
 Path(str(OUT)+"_RESULT.json").write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
 Path(str(OUT)+"_REVIEW.md").write_text("# DeepSeek V4 Pro R10 monthly-to-session expert referee\n\nUNTRUSTED hypotheses, no actual market experiment by DeepSeek.\n\n"+answer+"\n")
 print("PRO_R10",receipt["status"],"MODEL",x.get("model"),"CHARS",len(answer),"USAGE",use,flush=True)
 if not good:raise RuntimeError("TRUNCATED_REVIEW_NO_RETRY")
if __name__=="__main__":
 try: main()
 except Exception as e:
  msg=str(e)
  if len(msg)>110:msg=type(e).__name__
  Path(str(OUT)+"_FAILURE_QC.json").write_text(json.dumps({"status":"FAIL_CLOSED","reason":msg,"secrets_logged":False})+"\n")
  print("PRO_R10_FAIL",msg,flush=True);raise SystemExit(1)
