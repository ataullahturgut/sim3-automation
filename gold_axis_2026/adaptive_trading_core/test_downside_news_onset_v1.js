"use strict";
const assert=require("node:assert/strict");
const core=require("./adaptive_market_core_s1_s2");
const monitor=require("./downside_news_onset_v1");
const registry=require("../OLAY_02_KURESEL_HABER_KAYNAK_KURALLARI_V1_20261018.json");
const SOURCE="GOLD_M15_FAKE";
const T=Date.parse("2023-01-02T00:00:00Z"),STEP=900000;
function news(id,bar=29,opts={}){
 const when=new Date(T+(bar+1)*STEP).toISOString();
 return {id,publisher:"ECB",jurisdiction:"EU",eventKind:"CB_DECISION",
  sourceUrl:"https://www.ecb.europa.eu/press/pr/date/2023/html/ecb.mp230202~08a972ac76.en.html",
  eventTime:when,publishedAt:when,availableAt:when,detectedAt:when,
  firstprintVerified:true,firstprintEvidenceId:"SYNTHETIC_TEST_PRIMARY_"+id,...opts};
}
function bar(i,price,newsItems){
 const start=new Date(T+i*STEP).toISOString(),asof=new Date(T+(i+1)*STEP).toISOString();
 return {asof,barStartedAt:start,price,priceAvailableAt:asof,
  barMinutes:15,priceSource:SOURCE,
  ...(newsItems?{downsideNews:newsItems}:{})};
}
function model(enabled=true){return core.create({sourceId:SOURCE,sourceEvidence:"SYNTHETIC_ONLY",
 downsideEnabled:enabled,downsideNewsRegistry:registry,
 positionResearchMode:"CONDITIONAL_ECONOMIC_RESEARCH"});}
let n=0,checks=[];
function test(name,fn){fn();n++;checks.push(name);}
function testAll(){
 test("completed past prices produce risk features inside S1 and S3",()=>{
  const s=model(),b=[];
  let price=2000;
  for(let i=0;i<60;i++){price*=i<31?1.00025:.998;
   b.push(core.observe(s,bar(i,price)));}
  const d=b.find(x=>x.downsideResearch.newPriceWeakness);
  assert.ok(d);assert.ok(d.downsideResearch.observedPriceWeaknessSince);
  assert.equal(d.downsideResearch.linkedNewsBeforeObservedWeakness.length,0);
  assert.ok(s.s1.featureNames.includes("down_drawdown_norm"));
  assert.equal(d.positionResearch.downsideResearch.tradeAllowed,false);
  assert.equal(d.action,null);
  assert.equal(core.summary(s).downsideResearch.audit.priceOnlyStarts,1);
 });
 test("earlier firstprinted news can be linked by chronological order only",()=>{
  const s=model();let price=2000,first;
  for(let i=0;i<55;i++){
   price*=i<32?1.0001:.998;
   const o=core.observe(s,bar(i,price,i===29?[news("PIT",29)]:undefined));
   if(o.downsideResearch.newPriceWeakness)first=o;
  }
  assert.ok(first);assert.deepEqual(first.downsideResearch.linkedNewsBeforeObservedWeakness,["PIT"]);
  assert.equal(first.downsideResearch.causalAttribution,"UNPROVEN");
  assert.equal(core.summary(s).downsideResearch.audit.firstNewsBeforeOnsetCandidates,1);
 });
 test("news arriving after price onset classifies as accelerant, never first",()=>{
  const s=model();let price=2000,last;
  for(let i=0;i<55;i++){
   price*=i<28?1.0001:.998;
   last=core.observe(s,bar(i,price,i===38?[news("AFTER",38)]:undefined));
  }
  assert.equal(last.downsideResearch.latestNews.role,"AFTER_PRICE_WEAKNESS_ACCELERANT_CANDIDATE");
  assert.equal(core.summary(s).downsideResearch.audit.newsAfterOnset,1);
 });
 test("same M15 bar news cannot claim earlier start",()=>{
  const s=model();let price=2000,first;
  for(let i=0;i<45;i++){
   price*=i<30?1.0001:.994;
   const o=core.observe(s,bar(i,price,i===30?[news("SAME",30)]:undefined));
   if(o.downsideResearch.newPriceWeakness)first=o;
  }
  assert.ok(first);assert.deepEqual(first.downsideResearch.linkedNewsBeforeObservedWeakness,[]);
  assert.equal(first.downsideResearch.newsNewlyObserved[0].role,"SAME_BAR_UNRESOLVED");
 });
 test("unverified source cannot create first trigger",()=>{
  const s=model();let price=2000,first;
  for(let i=0;i<46;i++){
   price*=i<30?1.0001:.995;
   const o=core.observe(s,bar(i,price,i===28?[news("UNV",28,{firstprintVerified:false})]:undefined));
   if(o.downsideResearch.newPriceWeakness)first=o;
  }
  assert.ok(first);assert.deepEqual(first.downsideResearch.linkedNewsBeforeObservedWeakness,[]);
  assert.equal(core.summary(s).downsideResearch.audit.posthocOrUnverified,1);
 });
 test("future publication is rejected before market state mutation",()=>{
  const s=model();
  const bad=news("FUTURE",0,{detectedAt:"2023-01-03T00:00:00Z"});
  assert.throws(()=>core.observe(s,bar(0,2000,[bad])));
  assert.equal(s.audit.observed,0);
 });
 test("repeat news id cannot be inserted",()=>{
  const s=model();core.observe(s,bar(0,2000,[news("REP",0)]));
  assert.throws(()=>core.observe(s,bar(1,2000,[news("REP",1)])));
  assert.equal(s.audit.observed,1);
 });
 test("M15 time gap resets old price onset and avoids weekend bridging",()=>{
  const s=monitor.create({sourceId:SOURCE});
  let out;
  for(let i=0;i<29;i++)out=monitor.observe(s,bar(i,i<20?2000:1970));
  assert.ok(out.observedPriceWeaknessSince);
  const newBar={...bar(100,1970)};
  out=monitor.observe(s,newBar);
  assert.equal(out.phase,"WARMUP");
  assert.equal(out.observedPriceWeaknessSince,null);
  assert.equal(s.audit.gaps,1);
 });
 test("model ablation preserves old S1 feature schema",()=>{
  const s=model(false);
  const p=core.observe(s,bar(0,2000));
  assert.ok(!s.s1.featureNames.includes("down_pressure_z"));
  assert.equal(p.downsideResearch.phase,"WARMUP");
 });
 test("checkpoint restore preserves current onset, firstprint and time",()=>{
  const s=model();let price=2000;
  for(let i=0;i<45;i++){price*=i<30?1.0002:.998;core.observe(s,bar(i,price));}
  const recovered=core.restore(core.checkpoint(s));
  assert.equal(recovered.downside.onsetAt,s.downside.onsetAt);
  assert.equal(recovered.s1.audit.observations,s.s1.audit.observations);
  assert.deepEqual(recovered.downside.audit,s.downside.audit);
 });
 test("legacy checkpoint starts empty downside history rather than fabricate past",()=>{
  const s=model(false);core.observe(s,bar(0,2000));
  const legacy=core.checkpoint(s);delete legacy.downside;delete legacy.downsideEnabled;
  const recovered=core.restore(legacy);
  assert.equal(recovered.downside.audit.bars,0);
  assert.equal(recovered.downsideEnabled,false);
 });
 return {passed:n,names:checks};
}
module.exports={testAll};
if(require.main===module)process.stdout.write(JSON.stringify(testAll(),null,2)+"\n");
