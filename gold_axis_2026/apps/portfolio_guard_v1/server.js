"use strict";
/** Offline-first local historical research dashboard; localhost only. */
const http=require("node:http");
const fs=require("node:fs");
const path=require("node:path");
const engine=require("./engine");
const HOST="127.0.0.1";
const portValue=process.env.PORT||"8787";
const PORT=Number(portValue);
if(!Number.isSafeInteger(PORT)||PORT<1024||PORT>65535)throw new Error("PORT must be 1024..65535");
const snapshots=engine.runAll(); // load + verify Git blob SHA + regression tests; fail closed
const scientificV2=require("./event_audit_v2").runAudit(); // read-only, independent shadow diagnostics
const learnedStateV2=require("./monthly_learning_v2").createJanuaryLearningRecord(); // forward-only feedback gate
const febRunner=require("./monthly_runner"); // real February 2026 replay computed on demand
const model2023=require("./model_2023_daily_view"); // existing 2023 mathematical CORE reports, never recalculated in UI
const jan2023Selective=require("./model_2023_selective_view"); // immutable real gated M15 replay aggregate
const janFebAI=require("./model_2023_ai_shadow_view"); // immutable Jan-Feb 2023 AI handoff real CORE research
function small(v) {
 const x=snapshots.scenarios[v];
 return {
  model:x.model,version:x.version,period:x.period,startUSD:x.startUSD,
  finalUSD:x.finalUSD,returnPct:x.returnPct,maxDrawdownPct:x.maxDrawdownPct,
  benchmarkBuyHoldUSD:x.benchmarkBuyHoldUSD,terminalAsset:x.terminalAsset,
  goldOunces:x.goldOunces,checks:x.checks,fullCalendarSlots:x.fullCalendarSlots,
  completePriceBars:x.completePriceBars,archiveCases:x.archiveCases,
  actions:x.actions,days:x.days
 };
}
function respond(res,code,data,type) {
 res.writeHead(code,{"Content-Type":type||"application/json; charset=utf-8",
  "Cache-Control":"no-store","X-Content-Type-Options":"nosniff",
  "X-Frame-Options":"DENY",
  "Content-Security-Policy":"default-src 'self'; connect-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; object-src 'none'; frame-ancestors 'none'; base-uri 'none'",
  "Access-Control-Allow-Origin":"null"});
 res.end(data);
}
function summary(){
 const {scenarios}=snapshots;
 return {
  version:snapshots.version,
  status:"RESEARCH_ONLY_NOT_LIVE",
  guarantee:"same frozen input blob + code + parameters = same replay output",
  dataHashes:snapshots.inputs,
  bankSpreadIncluded:false,commissionPerSide:0.008,
  independentOutOfSample:false,economicCausalityProven:false,
  comparison:["legacy3h","price15m","event15m"].map(function(m){return small(m);}),
  incrementalDNABenefitUSD:scenarios.event15m.finalUSD-scenarios.price15m.finalUSD
 };
}
function requestHandler(req,res) {
 if(req.method!=="GET"&&req.method!=="HEAD")return respond(res,405,JSON.stringify({error:"READ_ONLY_GET_ONLY"}));
 const url=new URL(req.url,"http://localhost");
 const route=url.pathname;
 if(route==="/api/model/2023/jan-feb-ai-shadow"){
  try{
   return respond(res,200,JSON.stringify(janFebAI.read()));
  }catch(err){
   console.error("Jan-Feb AI handoff aggregate validation:",err.message);
   return respond(res,503,JSON.stringify({error:"JAN_FEB_AI_HANDOFF_SOURCE_INVALID"}));
  }
 }
 if(route==="/api/model/2023/january/selective-walk"){
  try {
   return respond(res,200,JSON.stringify(jan2023Selective.read()));
  }catch(err){
   console.error("Jan 2023 selective replay aggregate invalid:",err.message);
   return respond(res,503,JSON.stringify({error:"JAN2023_SELECTIVE_REPLAY_SOURCE_INVALID"}));
  }
 }
 if(route==="/api/model/2023/daily"){
  const month=url.searchParams.get("month");
  if(!Object.prototype.hasOwnProperty.call(model2023.MONTHS,month))
   return respond(res,400,JSON.stringify({error:"UNSUPPORTED_MODEL_2023_MONTH",
      allowed:Object.keys(model2023.MONTHS)}));
  try {
   return respond(res,200,JSON.stringify(model2023.readMonth(month)));
  }catch(err){
   console.error("2023 model report unavailable:",err.message);
   return respond(res,503,JSON.stringify({error:"MODEL_2023_SOURCE_VALIDATION_FAILED"}));
  }
 }
 if(route==="/api/algorithm/v13/sentez"){
  const study=require("./v13_sentez_run").audit();
  return respond(res,200,JSON.stringify(study));
 }
 if(route==="/api/algorithm/v12/earliest"){
  const data=require("./v12_earliest_origin_audit").diag();
  return respond(res,200,JSON.stringify(data));
 }
 if(route==="/api/algorithm/v12/rehber"){
  const data=require("./v12_rehber_agent").audit();
  return respond(res,200,JSON.stringify(data));
 }
 if(route==="/api/algorithm/v11/ann"){
  const report=require("./v11_ann_research").research();
  return respond(res,200,JSON.stringify(report));
 }
 if(route==="/api/algorithm/v10/evidence"){
  const result=require("./v10_execution_audit").audit();
  return respond(res,200,JSON.stringify(result));
 }
 if(route==="/api/algorithm/v9/scientific"){
  const study=require("./v9_research_audit").report();
  return respond(res,200,JSON.stringify(study));
 }
 if(route==="/api/algorithm/v8/regret"){
  const audit=require("./v8_regret_audit").assess();
  return respond(res,200,JSON.stringify(audit));
 }
 if(route==="/api/algorithm/v7/intramonth-oracle"){
  const analysis=require("./intramonth_oracle_v7").runIntramonthOracle();
  return respond(res,200,JSON.stringify(analysis));
 }
 if(route==="/api/algorithm/v7/monthly-regimes"){
  const benchmark=require("./monthly_regime_benchmark_v7");
  const model=require("./adaptive_v7_app");
  const result=benchmark.replayMonthlyDecision(model.loadRows());
  return respond(res,200,JSON.stringify(result));
 }
 if(route==="/api/algorithm/v7/adaptive"){
  const model=require("./adaptive_v7_app").runResearch();
  return respond(res,200,JSON.stringify(model));
 }
 if(route==="/api/algorithm/v6/portfolio"){
  const r=require("./macro_v6_portfolio").fullResearch();
  return respond(res,200,JSON.stringify({
   version:r.version,status:r.status,years:r.years,monthResults:r.monthResults,
   initialUSD:r.fromFebThroughSeptember.openingUSD,
   finalUSD:r.fromFebThroughSeptember.finalUSD,
   position:r.fromFebThroughSeptember.position,
   trades:r.fromFebThroughSeptember.trades,
   comparison:r.comparison,scientificGate:r.scientificGate,
   promotionAuthorized:r.promotionAuthorized,
   economicEventEvidence:r.eventEvidence,macroCoverage:r.cmeByYear,
   dataSourcePins:r.sourcePins,
   bankSpreadIncluded:false
  }));
 }
 if(route==="/api/algorithm/v6"){
  const audit=require("./macro_v6").runAudit();
  return respond(res,200,JSON.stringify(audit));
 }
 if(route==="/api/algorithm/v4/forward"){
  const r=require("./v4_forward_review").runForwardReview();
  return respond(res,200,JSON.stringify({
   version:r.version,status:r.status,source:r.source,unchangedPolicy:r.unchangedPolicy,
   actual:r.actual,benchmarks:r.benchmarks,monthly:r.monthly,
   monthlyBenchmarks:r.monthlyBenchmarks,actions:r.actions,
   monthEndCarryVerified:r.monthEndCarryVerified,
   hasProspectiveBlindValidation:r.hasProspectiveBlindValidation,
   economicMechanismVerified:r.economicMechanismVerified,
   bankBidAskIncluded:r.bankBidAskIncluded,decision:r.decision
  }));
 }
 if(route==="/api/algorithm/v5"){
  const r=require("./recovery_v5").fullResearch();
  return respond(res,200,JSON.stringify({
   version:r.version,status:r.status,years:r.years,monthResults:r.monthResults,
   fromFebThroughSeptember:r.fromFebThroughSeptember,comparison:r.comparison,
   warnings:r.warnings,promotionAuthorized:r.promotionAuthorized,
   scientificGate:r.scientificGate,
   training:r.training
  }));
 }
 if(route==="/api/algorithm/v4"){
  const model=require("./recovery_v4").runResearch();
  return respond(res,200,JSON.stringify({
   version:model.version,status:model.status,
   training:model.training,candidatePolicy:model.candidatePolicy,
   annual:model.annual,january:model.january,february:model.february,
   baseline:model.baseline,chronology:model.chronology,
   economicCauseVerified:model.economicCauseVerified,
   bankBidAskSpreadIncluded:model.bankBidAskSpreadIncluded,
   warning:model.warning
  }));
 }
 if(route==="/api/algorithm/v3"){
  const v3=require("./recovery_v3").runJanuaryFebruary();
  return respond(res,200,JSON.stringify({
   version:v3.version,status:v3.status,history:v3.history,annual:v3.annual,
   policy:v3.policy,sourcePriceHistory2023Incomplete:v3.sourcePriceHistory2023Incomplete,
   january:{finalUSD:v3.january.finalUSD,actions:v3.january.actions,period:v3.january.period},
   february:{finalUSD:v3.february.finalUSD,actions:v3.february.actions,
    period:v3.february.period,terminalAsset:v3.february.terminalAsset,
    startUSD:v3.february.startUSD,maxDrawdownPct:v3.february.maxDrawdownPct,
    days:v3.february.days},
   frozenOriginalJanuaryCashUSD:v3.frozenOriginalJanuaryCashUSD,
   hardStop:v3.hardStop,scientificLearning:v3.scientificLearning,
   bankSpreadIncluded:false
  }));
 }
 if(route==="/api/months")return respond(res,200,JSON.stringify({months:[
  {id:"2026-01",label:"Ocak 2026",status:"FROZEN_REFERENCE"},
  {id:"2026-02",label:"Şubat 2026",status:"RUNNABLE_FROM_JAN_CASH"}
 ],requiredOrder:["2026-01","2026-02"],unavailableBeyondFebruary:true}));
 if(route==="/api/months/2026-02/run"){
  const result=febRunner.runFebruary();
  return respond(res,200,JSON.stringify({
   month:result.month,version:result.version,status:result.status,
   guarantee:"frozen January CASH + frozen 15m February as-of panel and unchanged V1 rules",
   dataHashes:result.dataHashes,bankSpreadIncluded:false,commissionPerSide:0.008,
   independentOutOfSample:false,economicCausalityProven:false,
   comparison:result.comparison,incrementalDNABenefitUSD:result.incrementalDNABenefitUSD,
   portfolioCarryForward:{from:"2026-01",initialCashUSD:result.scenarios.event15m.startUSD,
    autoRetrain:false,labelMaturityGuard:"96 hours"}
  }));
 }
 if(route==="/api/research/news-effect-2023"){
  try{
   const data=JSON.parse(fs.readFileSync(path.resolve(__dirname,"../../adaptive_trading_core/GLOBAL_NEWS_ROUTER_JANFEB2023_DEMO_20261018.json"),"utf8"));
   if(data.schema!=="GLOBAL_NEWS_RULES_2023_JAN_FEB_READONLY_DEMO_20261018"||!Array.isArray(data.inputs)||data.inputs.length!==8||!Array.isArray(data.results.events))throw Error("NEWS_EFFECT_SCHEMA");
   return respond(res,200,JSON.stringify({status:"RETROSPECTIVE_UNVERIFIED",events:data.inputs.map(n=>{const e=data.results.events.find(x=>x.id===n.id);return {date:n.announcementReferenceUtc.slice(0,10),eventKind:n.eventKind,source:n.source,referenceUtc:n.announcementReferenceUtc,archiveK:n.retrospectiveArchiveLabelsNotRouted,verifiedK:e?.conditions||[],orgs:(e?.candidateOrgs||[]).map(o=>o.org),patterns:e?.matchedPatterns||[],status:e?.status||"UNKNOWN",firstprintAttested:!!e?.firstprintAttested};})}));
  }catch(e){console.error("News effects:",e.message);return respond(res,503,JSON.stringify({error:"NEWS_EFFECT_UNAVAILABLE"}));}
 }
 if(route==="/api/research/down-news"){
  try {
   const source=path.resolve(__dirname,"../../ETKI_05_17_DUSUS_HABER_VE_M15_GERI_CEKILME_SAAT_KARSILASTIRMA_V2_20261018.json");
   const data=JSON.parse(fs.readFileSync(source,"utf8"));
   if(data.schema!=="GOLD_DOWN_NEWS_VS_M15_THRESHOLD_TIMELINE_V2"||!Array.isArray(data.records)||data.records.length!==17)
    throw new Error("Unexpected research data");
   return respond(res,200,JSON.stringify({status:"RETROSPECTIVE_RESEARCH_ONLY",firstNewsCausesDownCertified:data.firstNewsCausesDownCertified,records:data.records.map(r=>({id:r.id,startPivotDay:r.startPivotDay,endPivotDay:r.endPivotDay,fullLegPct:r.fullLegPct,newsHeadline:r.newsHeadline,newsDate:r.newsDate,documentedNewsReleaseUtc:r.documentedNewsReleaseUtc,newsUtcQuality:r.newsUtcQuality,firstHalfPctDrawdownUtc:r.firstHalfPctDrawdownUtc,firstOnePctDrawdownUtc:r.firstOnePctDrawdownUtc,firstTwoPctDrawdownUtc:r.firstTwoPctDrawdownUtc,observation:r.observation,sourceUrl:r.sourceUrl,newsOriginalFirstAvailableUtcCertified:r.newsOriginalFirstAvailableUtcCertified,newsCausedInitialFall:r.newsCausedInitialFall}))}));
  }catch(e){console.error("Down-news research read:",e.message);return respond(res,503,JSON.stringify({error:"DOWN_NEWS_RESEARCH_UNAVAILABLE"}));}
 }
 if(route==="/api/summary")return respond(res,200,JSON.stringify(summary()));
 if(route==="/api/replay"){
  const mode=url.searchParams.get("mode");
  if(!["event15m","price15m","legacy3h"].includes(mode))
   return respond(res,400,JSON.stringify({error:"UNKNOWN_FROZEN_MODEL",allowed:["event15m","price15m","legacy3h"]}));
  return respond(res,200,JSON.stringify(snapshots.scenarios[mode]));
 }
 if(route==="/api/algorithm/v2")return respond(res,200,JSON.stringify(scientificV2));
 if(route==="/api/learning/v2")return respond(res,200,JSON.stringify(learnedStateV2));
 if(route==="/api/health"){
  return respond(res,200,JSON.stringify({ok:true,version:snapshots.version,verifiedAtStartup:true,readOnly:true}));
 }
 const files={"/":"index.html","/index.html":"index.html","/app.js":"app.js","/style.css":"style.css"};
 const name=files[route];
 if(!name)return respond(res,404,JSON.stringify({error:"NOT_FOUND"}));
 const mime=name.endsWith(".js")?"text/javascript; charset=utf-8":name.endsWith(".css")?"text/css; charset=utf-8":"text/html; charset=utf-8";
 return respond(res,200,fs.readFileSync(path.join(__dirname,"public",name),"utf8"),mime);
}
if(require.main===module){
 if(process.argv.includes("--verify")){
  const s=summary();
  console.log(JSON.stringify({status:"PASS",version:s.version,
    price15m:s.comparison[1].finalUSD,
    event15m:s.comparison[2].finalUSD,
    legacy3h:s.comparison[0].finalUSD,
    hashChecks:"PASS",bankExecution:false},null,2));
 }else{
  http.createServer(requestHandler).listen(PORT,HOST,function(){
   console.log("Gold Portfolio Guard V1 — http://"+HOST+":"+PORT);
   console.log("Historical replay only; no bank login and no order execution.");
  });
 }
}
module.exports={requestHandler,summary,small};
