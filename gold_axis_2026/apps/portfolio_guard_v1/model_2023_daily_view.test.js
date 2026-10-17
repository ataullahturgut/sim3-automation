"use strict";
const test=require("node:test");
const assert=require("node:assert/strict");
const fs=require("node:fs"),path=require("node:path");
const {MONTHS,VERSION,readMonth}=require("./model_2023_daily_view");

test("January and February are chronological, source-backed and explicitly research-only",()=>{
 for(const [id,count] of [["2023-01",31],["2023-02",28]]){
  const r=readMonth(id);
  assert.equal(r.version,VERSION);
  assert.equal(r.days.length,count);
  assert.equal(r.days[0].date,id+"-01");
  assert.equal(r.days.at(-1).date,id+"-"+count);
  assert.equal(r.bankTradeAuthorized,false);
  assert.equal(r.actualEconomicRuleLearningVerified,false);
  assert.equal(r.actualMacroPITVerified,false);
  assert.equal(r.confirmedTradeSignals,0);
  assert.equal(r.economicSnapshots,2);
  assert.equal(r.sourceRun,MONTHS[id].sourceRun);
  assert.ok(r.days.every(d=>d.s3.realAction===null&&d.s3.tradeAllowed===false));
  assert.ok(r.days.every(d=>d.ruleClassification==="RESEARCHER_RETROSPECTIVE_HYPOTHESIS_NOT_TRAINED_CAUSAL_RULE"));
  assert.ok(r.days.filter(d=>d.hasSession).every(d=>d.s1.pUpPct>=0&&d.s1.pUpPct<=100));
  assert.ok(r.days.filter(d=>!d.hasSession).every(d=>d.s1.pUpPct===null&&d.observedSessionReturnPct===null));
  assert.ok(r.days.filter(d=>d.hasSession).every(d=>d.s3.researchSuggestion==="KEEP"));
 }
});
test("January pretraining and February continuity are verified, not reset",()=>{
 const a=readMonth("2023-01"),b=readMonth("2023-02");
 assert.equal(a.trainingM15Bars,5865);
 assert.equal(a.monthM15Bars,1920);
 assert.equal(a.startingLearnedMarketRules,3);
 assert.equal(a.endingLearnedMarketRules,5);
 assert.equal(b.trainingM15Bars,7785);
 assert.equal(b.monthM15Bars,1830);
 assert.equal(b.startingLearnedMarketRules,a.endingLearnedMarketRules);
 assert.equal(b.startingMaturedFourHourLabels,a.endingMaturedFourHourLabels);
 assert.equal(b.endingLearnedMarketRules,6);
 assert.equal(b.endingMaturedFourHourLabels,553);
});
test("known 2023 macro dates reflect recorded day-end metrics and distinct release observations",()=>{
 const a=readMonth("2023-01"),b=readMonth("2023-02");
 const get=(m,d)=>m.days.find(x=>x.date===d);
 assert.equal(get(a,"2023-01-06").s1.pUpPct,51.77);
 assert.equal(get(a,"2023-01-06").s2.fastPhase,"PULLBACK");
 assert.equal(get(a,"2023-01-06").economicRelease.s2Phase,"NEUTRAL");
 assert.equal(get(a,"2023-01-12").economicRelease.s2Phase,"REENTRY");
 assert.equal(get(a,"2023-01-12").economicRelease.s1EconomicFourHourReady,false);
 assert.equal(get(b,"2023-02-02").observedSessionReturnPct,-2.222);
 assert.equal(get(b,"2023-02-03").observedSessionReturnPct,-2.469);
 assert.equal(get(b,"2023-02-03").economicRelease.at,"2023-02-03T14:30:00.000Z");
 assert.equal(get(b,"2023-02-03").economicRelease.s2TrendZ,-1.10);
 assert.equal(get(b,"2023-02-14").economicRelease.s1EconomicFourHourReady,false);
 assert.equal(get(b,"2023-02-22").s2.fastDirection,"DOWN");
 assert.equal(get(b,"2023-02-24").s1.pUpPct,50.32);
});
test("unsupported months cannot silently populate future or fictional model outputs",()=>{
 for(const id of ["2023-03","2026-01","2023-1",undefined,"__proto__"])
  assert.throws(()=>readMonth(id),/MONTH_NOT_AVAILABLE|DAILY_/);
});
test("the existing app has a wired navigation, controls, endpoint and non-live warnings",()=>{
 const html=fs.readFileSync(path.join(__dirname,"public","index.html"),"utf8");
 const client=fs.readFileSync(path.join(__dirname,"public","app.js"),"utf8");
 const server=fs.readFileSync(path.join(__dirname,"server.js"),"utf8");
 for(const id of ["model2023","model23Month","model23Filter","model23Rows","model23Detail",
   "model23Status","model23Rules","model23Labels","model23Events","model23Trades",
   "model23DetailDate","model23RowsLabel","model23Source"]){
  assert.match(html,new RegExp('id="'+id+'"'));
 }
 assert.match(html,/href="#model2023"/);
 assert.match(html,/Ekonomik kural adayı|Ekonomik kural ve S1/);
 assert.match(html,/yatırım tavsiyesi değil/);
 assert.match(client,/function loadModel23|async function loadModel23/);
 assert.match(client,/function model23Detail/);
 assert.match(client,/\/api\/model\/2023\/daily\?month=/);
 assert.match(server,/model2023\.readMonth\(month\)/);
 assert.match(server,/UNSUPPORTED_MODEL_2023_MONTH/);
});
