"use strict";
const assert=require("node:assert/strict");
const {audit,buildNews,horizonLabel}=require("./downside_alert_news_join_v1");
const STEP=900000,T=Date.parse("2023-01-02T00:00:00Z");
let n=0,names=[];
function test(name,fn){fn();n++;names.push(name);}
function bars(count=40,fallAt=20){
 const v=[];
 for(let i=0;i<count;i++){const p=i<fallAt?2000:1984;
  v.push({bar_start_utc:new Date(T+i*STEP).toISOString(),
   bid_close:p-.1,ask_close:p+.1});}
 return v;
}
function macro(i,id="NFP_MOCK"){
 return {release_id:id,kind:"NFP",release_utc:new Date(T+(i+1)*STEP).toISOString()};
}
function runAll(){
 test("No news must not turn price alerts into news or trade orders",()=>{
  const r=audit({bars:bars(),macro:[]});
  assert.ok(r.alertCounts.marketOnlyAlertTotal>=1);
  assert.equal(r.alertCounts.alertsWithAnyMacroWithin24h,0);
  assert.equal(r.tradingActions,0);
 });
 test("Past macro within four hours counted as historical candidate, not established cause",()=>{
  const r=audit({bars:bars(),macro:[macro(18)]});
  const a=r.alertRecords[0];
  assert.equal(a.macro_chronology_group,"PRE_0_4H");
  assert.equal(a.closest_macro_before.id,"NFP_MOCK");
  assert.equal(a.causal_attribution,"UNVERIFIED");
  assert.equal(r.dataQuality.actualOriginalFirstprintVerified,0);
 });
 test("Future macro must be classified only as future calendar, not past cause",()=>{
  const r=audit({bars:bars(),macro:[macro(22)]});
  const a=r.alertRecords[0];
  assert.equal(a.macro_chronology_group,"POST_0_4H");
  assert.equal(a.closest_macro_before,null);
  assert.equal(a.closest_macro_after.id,"NFP_MOCK");
 });
 test("Date-only headline same day never acquires fabricated clock time",()=>{
  const r=audit({bars:bars(),macro:[],stories:[{
   id:"TARIH",newsDate:"2023-01-02",precision:"ARTICLE_DATE_ONLY",headline:"Narrative"}]});
  assert.ok(r.alertRecords.some(x=>x.other_news_date_only.some(n=>
   n.relation==="SAME_CALENDAR_DAY_ORDER_UNKNOWN")));
  assert.equal(r.dateOnlyStories[0].reliableHour,null);
  assert.equal(r.alertCounts.alertsWithMacroBefore24h,0);
 });
 test("Alarms are exactly partitioned into five nonoverlapping chronology classes",()=>{
  const r=audit({bars:bars(70),macro:[macro(18),macro(32,"CPI_MOCK")]});
  assert.equal(Object.values(r.chronologyGroups).reduce((a,b)=>a+b.alarms,0),
   r.alertCounts.marketOnlyAlertTotal);
 });
 test("Label after horizon is null when future data not yet exists",()=>{
  const p=bars(24).map((x,i)=>({time:T+(i+1)*STEP,price:(x.bid_close+x.ask_close)/2}));
  assert.equal(horizonLabel(p,20,10),null);
 });
 test("Historical firstprint never auto-certified from research macro timestamp",()=>{
  const r=buildNews([macro(18)],[]);
  assert.equal(r.releases[0].firstprintCertified,false);
  assert.equal(r.releases[0].provenance,
   "RESEARCH_MACRO_SCHEDULE_RELEASE_CLOCK_NOT_ORIGINAL_PIT_FIRSTPRINT");
 });
 test("Invalid macro type is rejected",()=>{
  assert.throws(()=>buildNews([{...macro(18),kind:"UNKNOWN"}],[]));
 });
 test("Within-price-month news outside +/-24h is not a chronological match",()=>{
  const r=audit({bars:bars(140,120),macro:[macro(1)]});
  assert.equal(r.alertRecords[0].closest_macro_before,null);
 });
 test("Exact official release at completed bar close is unresolved, not news-first",()=>{
  const r=audit({bars:bars(),macro:[macro(20)]});
  const a=r.alertRecords[0];
  assert.equal(a.macro_chronology_group,"COINCIDENT_RELEASE_BAR_CLOSE_UNRESOLVED");
  assert.equal(a.closest_macro_before,null);
  assert.equal(a.coincident_macro_at_price_bar_close[0].id,"NFP_MOCK");
  assert.equal(r.alertCounts.alertsAtMacroExactBarCloseUnresolved,1);
 });
 return {passed:n,tests:names};
}
module.exports={runAll};
if(require.main===module)process.stdout.write(JSON.stringify(runAll(),null,2)+"\n");
