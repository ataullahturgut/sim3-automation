"""R14B second authentic adversarial followup to R14 independent Pro: correct unavailable intraday metals."""
from pathlib import Path
import os,json,datetime as dt,urllib.request,urllib.error
R=Path(__file__).resolve().parents[1];O=R/"GOLD_R14B_DEEPSEEK_PRO_SOURCE_CORRECTION_20261010"
def main():
 k=os.environ.get("DEEPSEEK_API_KEY","").strip()
 if not k:raise RuntimeError("NO_AUTH")
 system="Adversarial academic peer referee. Turkish reply max 520 words, no invented market tests."
 user=("YOUR R14 proposal has a major impossible feature: Ag,Pt,Pd have NO verified 04:45-08:45 15-min observations. "
       "Only Au intraday Dukascopy M15; Au/Ag/Pt/Pd StakTrakr daily prices 2010-Jul2026 in original Neon, historical "
       "2023-25 rows archived only as of Sep2026 (thus historical availability cannot be certified); GPR monthly PIT 2022-Mar onward."
       "2026 Aug/Sep daily metal data NOT in source. Your 'available_as_of' based fourmetal screen would eliminate all 2023-26!"
       "Also your require 2023-24 minimum300 train samples is impossible for first2023 origin if only2022-03 GPR live "
       "vintage exists. Rework one precise test that uses only fourmetal prices through at least TWO prior completed daily dates, "
       "GPR asof monthly vintage, 16 prior completed M15 gold bars and H3 09Turkey target. "
       "Use chronological 2022-03..Dec pre2023 warmup and expanding2024 and freeze training at2024-12 for2025/2026. "
       "Source preissue availability caveat explicit. Strong null: same exact dates original PATH CBR forecast "
       "and Au-only daily; avoid selected hindsight thresholds in2025/26. Recommend at most four continuous features "
       "like Au5, industrial(Ag/Pt/Pd)5, divergence, GPRz×divergence with ridge fixed penalty. "
       "Decide if GPR should multiply direction or risk weight; show a one-line falsification and negative controls. "
       "NO PROMOTION without source-certified 2027. Do not recite unusable 15-min Ag/Pt/Pd PCA.")
 pay={"model":"deepseek-v4-pro","messages":[{"role":"system","content":system},{"role":"user","content":user}],"thinking":{"type":"disabled"},"max_tokens":1650,"stream":False}
 req=urllib.request.Request("https://api.deepseek.com/chat/completions",data=json.dumps(pay).encode(),headers={"Authorization":"Bearer "+k,"Content-Type":"application/json"},method="POST")
 try:
  with urllib.request.urlopen(req,timeout=130) as z:res=json.loads(z.read(500000).decode())
 except urllib.error.HTTPError as e:raise RuntimeError("HTTP_"+str(e.code)) from None
 ch=(res.get("choices") or [{}])[0];v=(ch.get("message") or {}).get("content") or ""
 good=res.get("model")=="deepseek-v4-pro" and ch.get("finish_reason")=="stop" and len(v)>300
 receipt={"status":"PASS" if good else "INCOMPLETE","returned":res.get("model"),"finish":ch.get("finish_reason"),"chars":len(v),
  "usage":res.get("usage"),"utc":dt.datetime.now(dt.timezone.utc).isoformat(),"no_market_backtest_by_provider":True}
 Path(str(O)+"_RESULT.json").write_text(json.dumps(receipt,indent=2)+"\n")
 Path(str(O)+"_REVIEW.md").write_text("# Actual DeepSeek Pro source feasibility rebuttal (R14B)\n\n"+v+"\n")
 print("R14B",receipt["status"],receipt["finish"])
 if not good:raise RuntimeError("INCOMPLETE")
if __name__=="__main__":
 try:main()
 except Exception as e:
  Path(str(O)+"_FAILURE_QC.json").write_text(json.dumps({"reason":str(e)[:90],"status":"FAIL"})+"\n")
  raise SystemExit(1)
