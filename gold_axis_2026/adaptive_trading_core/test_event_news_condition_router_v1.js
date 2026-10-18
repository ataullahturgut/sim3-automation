"use strict";
/** Deterministic rule-integrity tests. Mock historical news content is not a new economic dataset. */
const assert=require("node:assert/strict");
const router=require("./event_news_condition_router_v1");
const registry=require("../OLAY_02_KURESEL_HABER_KAYNAK_KURALLARI_V1_20261018.json");
const T="2023-02-02T13:15:00Z";
const profiles={
 FED:["US","https://www.federalreserve.gov/newsevents/pressreleases/monetary20230201a.htm"],
 BOE:["UK","https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2023/february-2023"],
 ECB:["EU","https://www.ecb.europa.eu/press/pr/date/2023/html/ecb.mp230202~08a972ac76.en.html"],
 BLS:["US","https://www.bls.gov/news.release/archives/empsit_02032023.htm"],
 BEA:["US","https://www.bea.gov/news"],
 PBOC:["CN","https://www.pbc.gov.cn/"],
 RBI:["IN","https://www.rbi.org.in/"],
 REUTERS:["GLOBAL","https://www.reuters.com/"],
 UN:["GLOBAL","https://www.un.org/"],
 US_WHITE_HOUSE:["US","https://www.whitehouse.gov/"],
 BOJ:["JP","https://www.boj.or.jp/en/"],
 INDIA_FINANCE:["IN","https://finmin.gov.in/"],
 WGC:["GLOBAL","https://www.gold.org/goldhub/data/gold-reserves-by-country"],
 EU_COUNCIL:["EU","https://www.consilium.europa.eu/en/press/press-releases/"]
};
function f(id,publisher,eventKind,time=T,extra={}){
 const [jurisdiction,sourceUrl]=profiles[publisher];
 return {id,publisher,jurisdiction,eventKind,eventTime:time,publishedAt:time,
  availableAt:time,detectedAt:time,firstprintVerified:false,sourceUrl,...extra};
}
function v(actual,consensus,eventTime=T,prior="2023-02-02T11:00:00Z"){
 return {actual,consensus,consensusVerified:true,actualAvailableAt:eventTime,consensusAvailableAt:prior};
}
let passed=0,report=[];
function test(name,fn){fn();report.push(name);passed++;}
function route(e,at="2023-02-03T15:00:00Z"){return router.route(e,{registry,asof:at});}
function tags(e,at){return route(e,at).conditions;}
function has(e,code,at){return tags(e,at).includes(code);}
function attempt(fn){assert.throws(fn);}
function testAll(){
 test("allowlist contains 32 publisher/venue sources",()=>assert.equal(registry.sources.length,32));
 test("zero BUY SELL policy in news router",()=>assert.equal(route(f("cb","ECB","CB_DECISION")).tradeAllowed,false));
 test("ECB rate hike without prior consensus is NOT K20 hawkish",()=>{
  const e=f("ecb","ECB","CB_DECISION",T,{data:{rate:{actual:3.0}}});
  assert.deepEqual(tags(e),["K39"]);assert.ok(route(e).candidateOrgs.some(x=>x.org==="ORG01"));});
 test("BoE rate decision recognized outside US",()=>assert.deepEqual(tags(f("boe","BOE","CB_DECISION","2023-02-02T12:00:00Z")),["K39"]));
 test("Fed rate decision recognized at 2023-02-01",()=>assert.deepEqual(tags(f("fed","FED","CB_DECISION","2023-02-01T19:00:00Z")),["K39"]));
 test("ECB press conference is NOT assumed dovish",()=>{const e=f("press","ECB","CB_PRESSER","2023-02-02T13:45:00Z");assert.deepEqual(tags(e),["K40"]);});
 test("a meeting statement without verified expectation cannot be hawkish",()=>{
  const e=f("test","ECB","CB_GUIDANCE",T,{guidance:{vsExpectation:"HAWKISH"}});
  assert.deepEqual(tags(e),[]);});
 test("rate higher relative to pre-release expected value gets K20",()=>{
  const e=f("rateHigh","ECB","CB_DECISION",T,{data:{rate:v(3.5,3.25,T)}});
  assert.deepEqual(tags(e),["K20"]);});
 test("rate lower than expected gets K21",()=>{
  const e=f("rateLow","ECB","CB_DECISION",T,{data:{rate:v(3.0,3.25,T)}});
  assert.deepEqual(tags(e),["K21"]);});
 test("rate at prior expected value gets K22 not K20",()=>{
  const e=f("rateEq","ECB","CB_DECISION",T,{data:{rate:v(3.25,3.25,T)}});
  assert.deepEqual(tags(e),["K22"]);});
 test("high CPI and low core CPI become mixed ORG01/ORG02 not forced gold DOWN",()=>{
  const e=f("mix","BLS","CPI",T,{data:{headline:v(0.7,0.5,T),core:v(0.1,0.3,T)}});
  const r=route(e);assert.deepEqual(r.conditions,["K01","K17"]);
  assert.equal(r.hasCompetingRateChannels,true);assert.equal(r.xauPrediction,"NOT_ESTIMATED");});
 test("NFP strong wage soft unemp lower: all 3 tags and both channels",()=>{
  const t="2023-02-03T13:30:00Z",e=f("nfp","BLS","NFP",t,{data:{
    employment:v(517,185,t),wages:v(.2,.3,t),unemployment:v(3.4,3.6,t)}});
  const r=route(e);assert.deepEqual(r.conditions,["K03","K18","K19"]);
  assert.equal(r.hasCompetingRateChannels,true);});
 test("non US CPI becomes K41, not US K01",()=>{
  const e=f("ukcpi","BOE","CB_DECISION",T);
  const r=route(e);assert.ok(r.conditions.includes("K39"));
  const n={...f("non","ECB","CB_DECISION"),publisher:"ONS",jurisdiction:"UK",
   eventKind:"CPI",sourceUrl:"https://www.ons.gov.uk/",data:{headline:v(.8,.4,T)}};
  assert.deepEqual(tags(n),["K41"]);});
 test("PCE separate from BLS CPI",()=>{
  const p=f("pce","BEA","PCE",T,{data:{headline:v(.4,.2,T)}});
  assert.deepEqual(tags(p),["K45"]);});
 test("GDP is a competing macro candidate, not guaranteed gold UP",()=>{
  const g=f("gdp","BEA","GDP",T,{data:{growth:v(4,3,T)}});
  assert.deepEqual(tags(g),["K47"]);assert.equal(route(g).xauPrediction,"NOT_ESTIMATED");});
 test("no publication until first detection",()=>{
  const e=f("later","ECB","CB_DECISION",T,{detectedAt:"2023-02-02T15:00:00Z"});
  assert.equal(route(e,"2023-02-02T13:30:00Z").status,"PENDING_FIRST_ACCESS");});
 test("actual arriving after decision is masked not leaked",()=>{
  const e=f("future","BLS","CPI",T,{data:{headline:v(.8,.4,"2023-02-02T14:00:00Z")}});
  assert.deepEqual(tags(e,"2023-02-02T13:30:00Z"),[]);});
 test("consensus first available after release cannot become historical surprise",()=>{
  const e=f("lookahead","ECB","CB_DECISION",T,{data:{rate:v(3.5,3.25,T,"2023-02-02T14:00:00Z")}});
  assert.deepEqual(tags(e),["K39"]);});
 test("future interest rate decision cannot be assigned before it happens",()=>{
  const e=f("later","ECB","CB_DECISION","2023-02-06T13:15:00Z");
  assert.equal(route(e,"2023-02-02T13:30:00Z").conditions.length,0);});
 test("publisher domain impersonation rejected",()=>{
  attempt(()=>tags(f("phish","ECB","CB_DECISION",T,{sourceUrl:"https://ecb.europa.eu.attacker.example/e"})));});
 test("secondary Reuters factual event remains secondary not validated firstprint",()=>{
  const e=f("risk","REUTERS","GEOPOLITICS",T,{firstprintVerified:true,firstprintEvidenceId:"long_immutable_hash",
   change:{direction:"ESCALATE",evidenceAvailableAt:T,factualEvidenceVerified:true,sourceEvidenceId:"text_immut_evidence"}});
  const r=route(e);assert.deepEqual(r.conditions,["K29"]);assert.equal(r.firstprintAttested,false);
  assert.equal(r.status,"SECONDARY_OR_LAGGED_CONTEXT_ONLY");});
 test("UN report no factual corroboration gives no geopolitics direction",()=>{
  const e=f("un","UN","GEOPOLITICS");assert.deepEqual(tags(e),[]);});
 test("unverified reserve report cannot backdate to observation month",()=>{
  const t="2023-02-02T13:15:00Z",e=f("reserve","PBOC","CB_RESERVE",t,{
    reportPeriod:"2023-01",change:{direction:"BUY",evidenceAvailableAt:t,factualEvidenceVerified:true,sourceEvidenceId:"pboc_evidence_report"}});
  assert.deepEqual(tags(e),["K25"]);assert.equal(route(e).status,"RETROSPECTIVE_OR_UNVERIFIED");});
 test("event overlap: Feb1 Fed separate from Feb2 BoE ECB conference",()=>{
  const seq=[
   f("fed","FED","CB_DECISION","2023-02-01T19:00:00Z"),
   f("boe","BOE","CB_DECISION","2023-02-02T12:00:00Z"),
   f("ecb","ECB","CB_DECISION","2023-02-02T13:15:00Z"),
   f("press","ECB","CB_PRESSER","2023-02-02T13:45:00Z"),
   f("nfp","BLS","NFP","2023-02-03T13:30:00Z",{data:{employment:v(517,185,"2023-02-03T13:30:00Z")}})
  ];
  const out=router.routeMany(seq,{asof:"2023-02-03T14:00:00Z",registry});
  assert.deepEqual(out.overlappingEpisodes.map(x=>x.ids),[["fed"],["boe","ecb","press"],["nfp"]]);
  assert.deepEqual(out.overlappingEpisodes[1].regions,["UK","EU"]);assert.equal(out.tradeAllowed,false);});
 test("duplicate events cannot triple-count identical headlines",()=>{
  const e=f("same","ECB","CB_DECISION",T);
  attempt(()=>router.routeMany([e,e],{asof:"2023-02-03T15:00:00Z",registry}));});
 test("issuer mismatch rejected",()=>attempt(()=>route(f("bad","ECB","CB_DECISION",T,{jurisdiction:"US"}))));
 test("bad timestamp zone rejected",()=>attempt(()=>route(f("bad2","ECB","CB_DECISION",T,{detectedAt:"2023-02-02T16:15:00"}))));
 test("retrospective market data and uncertain mechanisms do not generate a trade",()=>{
  const e=f("tariff","US_WHITE_HOUSE","TRADE_POLICY",T,{
   jurisdiction:"US",sourceUrl:"https://www.whitehouse.gov/",
   change:{direction:"TIGHTEN",evidenceAvailableAt:T,factualEvidenceVerified:true,sourceEvidenceId:"whitehouse_report_abc"}});
  const r=route(e);assert.deepEqual(r.conditions,["K27"]);assert.equal(r.action,null);
  assert.equal(r.countAsIndependentPriceCause,false);});
 test("firstprint proof flag with no independent evidence ID is not verified",()=>{
  const e=f("cert","ECB","CB_DECISION",T,{firstprintVerified:true});
  assert.equal(route(e).firstprintAttested,false);});
 test("strong rate label with attested firstprint still not XAU causality",()=>{
  const e=f("cert2","ECB","CB_DECISION",T,{firstprintVerified:true,firstprintEvidenceId:"reviewed_firstprint_document_001",
   data:{rate:v(3.5,3.25,T)}});
  const r=route(e);assert.equal(r.firstprintAttested,true);
  assert.equal(r.xauPrediction,"NOT_ESTIMATED");assert.equal(r.tradeAllowed,false);});

 test("Japan BOJ monetary decision is registered and requires rate expectation",()=>{
  assert.deepEqual(tags(f("boj","BOJ","CB_DECISION")),["K39"]);});
 test("India import tariff change is trade easing, not an US employment label",()=>{
  const e=f("india","INDIA_FINANCE","TRADE_POLICY",T,{change:{direction:"EASE",
   evidenceAvailableAt:T,factualEvidenceVerified:true,sourceEvidenceId:"official_india_policy_001"}});
  assert.deepEqual(tags(e),["K28"]);});
 test("EU council can carry a tariff tightening mechanism but never auto trade",()=>{
  const e=f("eu_trade","EU_COUNCIL","TRADE_POLICY",T,{change:{direction:"TIGHTEN",
   evidenceAvailableAt:T,factualEvidenceVerified:true,sourceEvidenceId:"eu_trade_report_001"}});
  const r=route(e);assert.deepEqual(r.conditions,["K27"]);assert.equal(r.tradeAllowed,false);});
 test("a WGC reserve data report cannot become firstprint official bank alert",()=>{
  const e=f("wgc","WGC","CB_RESERVE",T,{firstprintVerified:true,firstprintEvidenceId:"report_reference_id_001",
   change:{direction:"BUY",evidenceAvailableAt:T,factualEvidenceVerified:true,sourceEvidenceId:"published_report_001"}});
  const r=route(e);assert.deepEqual(r.conditions,["K25"]);
  assert.equal(r.firstprintAttested,false);assert.equal(r.status,"SECONDARY_OR_LAGGED_CONTEXT_ONLY");});
 test("UN verified security event produces geopolitical research candidate not UP prediction",()=>{
  const e=f("unEsc","UN","GEOPOLITICS",T,{change:{direction:"ESCALATE",
   evidenceAvailableAt:T,factualEvidenceVerified:true,sourceEvidenceId:"un_primary_statement_001"}});
  const r=route(e);assert.deepEqual(r.conditions,["K29"]);
  assert.ok(r.candidateOrgs.some(x=>x.org==="ORG04"));assert.equal(r.xauPrediction,"NOT_ESTIMATED");});
 return {passed,report};
}
module.exports={testAll};
if(require.main===module){const x=testAll();process.stdout.write(JSON.stringify({passed:x.passed},null,2)+"\n");}
