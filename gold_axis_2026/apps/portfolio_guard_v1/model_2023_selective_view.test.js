"use strict";
const t=require("node:test"),a=require("node:assert/strict");
const fs=require("node:fs"),path=require("node:path");
const {read}=require("./model_2023_selective_view");
const view=read();
t("all January days, original M15 count, previous learned model and automatic cadence checks",()=>{
 a.equal(view.days.length,31);
 a.equal(view.days[0].date,"2023-01-01");
 a.equal(view.days.at(-1).date,"2023-01-31");
 a.equal(view.prior.bars,5865);
 a.equal(view.prior.rules,3);
 a.equal(view.observed.janM15,1920);
 a.equal(view.observed.modelCalls,1920);
 a.equal(view.observed.gateCalls,1920);
 a.equal(view.observed.daySessions,21);
 a.equal(view.observed.priceWatch15mEvents,3);
 a.equal(view.observed.retrospectiveMacroWaves,2);
 a.equal(view.observed.retrospectiveMacroQuarantined,2);
});
t("does not misstate archived economic ORG candidates as learned or firstprint-vintage verified",()=>{
 a.equal(view.firstPrintMacroVerified,false);
 a.equal(view.tradeAllowed,false);
 a.equal(view.goldBankExecution,false);
 a.equal(view.observed.macroPITFeaturesAccepted,0);
 a.equal(view.observed.actualBankTrades,0);
 for(const d of view.days){
  a.equal(d.economicFeaturesPITAccepted,0);
  a.equal(d.ruleEvidence,"RETROSPECTIVE_RESEARCH_HYPOTHESIS_NOT_MODEL_SIGNAL");
  if(d.hasSession){
   a.equal(d.snapshot.s3.tradeAllowed,false);
   a.equal(d.snapshot.s3.actualAction,null);
   a.equal(d.snapshot.s3.researchAction,"KEEP");
  }
 }
});
t("January 6 and 12 are the only independently counted retrospective macro release waves",()=>{
 const dates=view.days.filter(x=>x.eventCandidateCount).map(x=>x.date);
 a.deepEqual(dates,["2023-01-06","2023-01-12"]);
 const j6=view.days.find(x=>x.date==="2023-01-06");
 const j12=view.days.find(x=>x.date==="2023-01-12");
 a.equal(j6.priceChangeWatchCount,2);
 a.equal(j12.priceChangeWatchCount,1);
 for(const x of [j6,j12]){
  a.equal(x.eventNotes[0].evidenceStatus,"RECONSTRUCTED_POST_RELEASE_UNVERIFIED");
  a.match(x.eventNotes[0].note,/ilk baskı|ilk yayın/);
 }
});
t("daily metrics are from actual CORE and distinct from old provisional ECONOMIC_ON report",()=>{
 const day=d=>view.days.find(z=>z.date===d);
 a.ok(day("2023-01-03").snapshot.s1.pUpPct>50);
 a.equal(day("2023-01-06").snapshot.s2.phase,"PULLBACK");
 a.equal(day("2023-01-12").snapshot.s2.phase,"END");
 a.equal(day("2023-01-31").snapshot.s3.researchAction,"KEEP");
 a.equal(day("2023-01-03").snapshot.at,"2023-01-03T22:00:00.000Z");
 a.equal(day("2023-01-01").hasSession,false);
});
t("screen navigation, day stepper, and API route are genuinely wired",()=>{
 const html=fs.readFileSync(path.join(__dirname,"public/index.html"),"utf8");
 const client=fs.readFileSync(path.join(__dirname,"public/app.js"),"utf8");
 const server=fs.readFileSync(path.join(__dirname,"server.js"),"utf8");
 for(const id of ["selective2023","selective23DaySlider","selective23Next",
 "selective23Restart","selective23All","selective23Status","selective23Current",
 "selective23Table","selective23Source","selective23Bars","selective23Events",
 "selective23Watches","selective23Trades"]){
  a.match(html,new RegExp('id="'+id+'"'));
 }
 a.match(html,/href="#selective2023"/);
 a.match(client,/selective23Draw/);
 a.match(client,/selective23Load/);
 a.match(client,/\/api\/model\/2023\/january\/selective-walk/);
 a.match(server,/jan2023Selective\.read\(\)/);
});
