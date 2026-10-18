"use strict";
const assert=require("node:assert/strict");
const engine=require("./economic_mechanism_integrator_v1");
const registry=require("../OLAY_02_KURESEL_HABER_KAYNAK_KURALLARI_V1_20261018.json");
const library=require("../ETKI_05_GENEL_BUYUK_HAREKET_MEKANIZMA_KURAL_MATRISI_20261018.json");
const issuer={
 ECB:"https://www.ecb.europa.eu/press/pr/date/2023/html/ecb.mp230202~08a972ac76.en.html",
 BOE:"https://www.bankofengland.co.uk/monetary-policy-summary-and-minutes/2023/february-2023",
 FED:"https://www.federalreserve.gov/newsevents/pressreleases/monetary20230201a.htm",
 BLS:"https://www.bls.gov/news.release/archives/empsit_02032023.htm"
};
const jurisdictions={ECB:"EU",BOE:"UK",FED:"US",BLS:"US"};
const T="2023-02-02T13:15:00Z";
function report(id="ECB1",opt={}){
 return {id,publisher:"ECB",jurisdiction:"EU",eventKind:"CB_DECISION",
  sourceUrl:issuer.ECB,eventTime:T,publishedAt:T,availableAt:T,detectedAt:T,
  firstprintVerified:false,...opt};
}
function fakePrices(start="2023-02-02T09:00:00Z",count=26){
 const out=[],t=Date.parse(start);
 for(let i=0;i<count;i++){
  // price trend is an observational proxy, NOT an explanatory economic series.
  const p=1950-i*.7;
  out.push({bar_start_utc:new Date(t+i*900000).toISOString(),
   bid_close:p-.11,ask_close:p+.11});
 }
 return out;
}
function med(id,code,time=T,sourceId="USD"){return {id,code,observedAt:time,
 availableAt:time,originalEvidenceVerified:true,independentFromGoldPrice:true,
 sourceEvidenceId:"verified_external_data_"+id,sourceId};}
function run(news,extras={}){
 return engine.integrate({news:Array.isArray(news)?news:[news],registry,
  mechanismLibrary:library,asof:"2023-02-02T15:00:00Z",
  completedBars:fakePrices(),marketEvidence:[],...extras});
}
let n=0,results=[];
function test(name,fn){fn();n++;results.push(name);}
function testAll(){
 test("registry and original mechanism archive remain available",()=>{
  assert.equal(registry.sources.length,32);assert.equal(library.mechanisms.length,12);});
 test("normal market without news maintains price metrics and no orders",()=>{
  const s=run([]);assert.equal(s.events.length,0);assert.equal(s.tradeAllowed,false);
  assert.equal(s.globalMarket.ready,true);assert.equal(s.audit.bankOrders,0);});
 test("ECB unknown consensus routes to K39 and ORG01 ORG02 ambiguity",()=>{
  const s=run(report());assert.deepEqual(s.events[0].conditions,["K39"]);
  assert.deepEqual(s.events[0].mechanisms.map(x=>x.org),["ORG01","ORG02"]);
  assert.equal(s.events[0].market.directionOfObservedResponse,"OBSERVED_DOWN");
  assert.equal(s.events[0].mechanisms[0].status,"H0_UNVERIFIED_OR_UNATTRIBUTED");});
 test("observed price decline cannot certify causal DOWN",()=>{
  const s=run(report());for(const x of s.events[0].mechanisms){
   assert.equal(x.causalConfirmation,"NOT_ESTABLISHED");assert.equal(x.readyForLiveTrading,false);
   assert.equal(x.remainingMovePrediction,null);
  }});
 test("only first closed bars within asof are visible",()=>{
  const s=run(report(),{asof:"2023-02-02T13:30:00Z"});
  assert.equal(s.globalMarket.asof,"2023-02-02T13:30:00.000Z");
  assert.equal(s.events[0].market.eventElapsedMinutes,15);});
 test("future event not visible",()=>{
  const s=run(report("FUTURE",{eventTime:"2023-02-03T13:15:00Z",
   publishedAt:"2023-02-03T13:15:00Z",availableAt:"2023-02-03T13:15:00Z",
   detectedAt:"2023-02-03T13:15:00Z"}));
  assert.equal(s.events[0].status,"PENDING_FIRST_ACCESS");
  assert.equal(s.events[0].market,null);});
 test("firstprint attestation alone cannot generate H2",()=>{
  const s=run(report("PRINT",{firstprintVerified:true,firstprintEvidenceId:"certified_original_001"}));
  assert.equal(s.events[0].mechanisms[0].status,"H1_SOURCE_ATTESTED_MECHANISM_UNCONFIRMED");
  assert.equal(s.audit.independentMechanismConfirmations,0);});
 test("independent USD/yield channels can support ORG02 without proving causality",()=>{
  const j=report("RATE",{firstprintVerified:true,firstprintEvidenceId:"certified_original_002",
   data:{rate:{actual:3.5,consensus:3.25,consensusVerified:true,
    actualAvailableAt:T,consensusAvailableAt:"2023-02-02T11:00:00Z"}}});
  const s=run(j,{marketEvidence:[
   med("USD_A","USD_UP","2023-02-02T13:30:00Z","fx_agency"),
   med("YIELD_A","REAL_YIELD_UP","2023-02-02T13:45:00Z","bond_agency")
  ]});
  assert.deepEqual(s.events[0].conditions,["K20"]);
  const o=s.events[0].mechanisms.find(x=>x.org==="ORG02");
  assert.equal(o.status,"H2_MEDIATOR_EVIDENCE_PRESENT_NOT_CAUSAL");
  assert.equal(o.causalConfirmation,"NOT_ESTABLISHED");assert.equal(s.tradeAllowed,false);});
 test("two indicators from same vendor not sufficiently independent",()=>{
  const s=run(report("SA",{firstprintVerified:true,firstprintEvidenceId:"certified_original_003"}),{
   marketEvidence:[med("USD_B","USD_DOWN",T,"same"),med("REAL_B","REAL_YIELD_DOWN",T,"same")]});
  const o=s.events[0].mechanisms.find(x=>x.org==="ORG01");
  assert.equal(o.status,"H1_SOURCE_ATTESTED_MECHANISM_UNCONFIRMED");});
 test("countervailing source blocks unambiguous H2",()=>{
  const s=run(report("CONTRA",{firstprintVerified:true,firstprintEvidenceId:"certified_original_004"}),{
   marketEvidence:[med("USD_C","USD_UP",T,"fx_a"),med("Y_C","REAL_YIELD_UP",T,"bond_b"),
    med("USD_O","USD_DOWN",T,"fx_c")]});
  const o=s.events[0].mechanisms.find(x=>x.org==="ORG02");
  assert.equal(o.counterEvidence,true);assert.equal(o.status,"H1_SOURCE_ATTESTED_MECHANISM_UNCONFIRMED");});
 test("future USD data is ignored",()=>{
  const s=run(report("LATER",{firstprintVerified:true,firstprintEvidenceId:"certified_original_005"}),{
   marketEvidence:[med("X","USD_DOWN","2023-02-02T17:00:00Z","fx_a")]});
  assert.equal(s.events[0].mechanisms[0].supportingIndependentSignals.length,0);});
 test("old market observation cannot be tagged as post-news mediator",()=>{
  const s=run(report(),{marketEvidence:[med("OLD","USD_DOWN","2023-02-01T13:00:00Z","fx_a")]});
  assert.equal(s.events[0].mechanisms[0].supportingIndependentSignals.length,0);});
 test("price-only evidence is rejected",()=>{
  const z=med("GOLD","USD_DOWN",T,"fake");z.independentFromGoldPrice=false;
  const s=run(report(),{marketEvidence:[z]});assert.equal(s.events[0].mechanisms[0].supportingIndependentSignals.length,0);});
 test("late detection measures price since detected separately from news",()=>{
  const s=run(report("LATE",{detectedAt:"2023-02-02T13:45:00Z"}));
  const x=s.events[0].market;assert.notEqual(x.priceSinceAnnouncementPct,x.priceSinceDetectionPct);
  assert.equal(x.firstDetectedAt,"2023-02-02T13:45:00Z");});
 test("missing event pre-price does not become fabricated return",()=>{
  const s=run(report(),{completedBars:[]});
  assert.equal(s.events[0].market.priceSinceAnnouncementPct,null);
  assert.equal(s.events[0].market.directionOfObservedResponse,"UNKNOWN");});
 test("bid greater than ask gets rejected",()=>{
  const p=fakePrices();p[5].ask_close=p[5].bid_close-1;
  assert.throws(()=>run(report(),{completedBars:p}));});
 test("duplicated market bars get rejected",()=>{
  const p=fakePrices();p.push({...p[0]});assert.throws(()=>run(report(),{completedBars:p}));});
 test("Fed BoE ECB press conference events overlap but count once as economic episode",()=>{
  const boe={...report("BOE"),publisher:"BOE",jurisdiction:"UK",sourceUrl:issuer.BOE,
   eventTime:"2023-02-02T12:00:00Z",publishedAt:"2023-02-02T12:00:00Z",
   availableAt:"2023-02-02T12:00:00Z",detectedAt:"2023-02-02T12:00:00Z"};
  const press={...report("PRESS"),eventKind:"CB_PRESSER",
   eventTime:"2023-02-02T13:45:00Z",publishedAt:"2023-02-02T13:45:00Z",
   availableAt:"2023-02-02T13:45:00Z",detectedAt:"2023-02-02T13:45:00Z"};
  const s=run([boe,report(),press]);assert.equal(s.overlappingEpisodes.length,1);
  assert.equal(s.overlappingEpisodes[0].priceReturnsMayNotBeSummed,true);
  assert.ok(s.overlappingEpisodes[0].matchedPatterns.some(x=>x.id==="CR14"));
  assert.equal(s.audit.bankOrders,0);});
 test("module never emits trained signals or orderable S1-S3 conclusions",()=>{
  const s=run(report());assert.equal(s.S1Shadow.status,"NOT_TRAINED");
  assert.equal(s.S2Shadow.status,"GLOBAL_BASELINE_PLUS_EVENT_MEASUREMENT_ONLY");
  assert.equal(s.S3Shadow.netExpectedBenefit,null);
  assert.equal(s.audit.trainedDirectionalRules,0);});
 test("feature frame contains dated K/ORG but no forward unknown labels",()=>{
  const s=run(report());
  assert.equal(s.eventFeatureFrames.length,1);
  const f=s.eventFeatureFrames[0];
  assert.deepEqual(f.economicKTags,["K39"]);
  assert.equal(f.containsFutureReturnLabels,false);
  assert.equal(f.forwardDirectionPrediction,null);
  assert.equal(f.economicDecisionFeatureCertified,false);
  assert.equal(f.tradeAllowed,false);});
 test("stale event observation scope cannot become a long swing attributed to a single news",()=>{
  const news=report("OLD",{eventTime:"2023-01-12T13:15:00Z",
    publishedAt:"2023-01-12T13:15:00Z",availableAt:"2023-01-12T13:15:00Z",
    detectedAt:"2023-01-12T13:15:00Z"});
  const s=run(news,{asof:"2023-02-02T15:00:00Z"});
  assert.equal(s.events[0].market.priceSinceAnnouncementPct,null);
  assert.equal(s.events[0].market.observationWindowExpired,true);});
 return {count:n,checks:results};
}
module.exports={testAll};
if(require.main===module){const r=testAll();process.stdout.write(JSON.stringify(r,null,2)+"\n");}
