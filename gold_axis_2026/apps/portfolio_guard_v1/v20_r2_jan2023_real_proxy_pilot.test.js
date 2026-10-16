"use strict";
const test=require("node:test"),A=require("node:assert/strict");
const Pilot=require("./v20_r2_jan2023_real_proxy_pilot");
const START=Date.parse(Pilot.START);
test("Historic dataset has real-source pinned SHA, correct 3 Jan 2023 initial window",()=>{
 const d=Pilot.loadPinned();
 A.equal(d.lineage.length,2);
 A.equal(d.lineage[1].first,Pilot.START);
 A.ok(d.lineage[0].rows>100);
 A.ok(d.lineage[1].rows>3000);
});
test("Jan pilot actually replays from 09:00 Turkey with 100 USD cash",()=>{
 const p=Pilot.run();
 A.equal(p.signals[0].timeUTC,Pilot.START);
 A.equal(p.signals[0].position,"CASH");
 A.equal(p.startCapitalUSD,100);
 A.ok(p.numberOfSignals>20);
 A.ok(p.numberOfFills>20);
 A.equal(p.contract,"REAL_HISTORICAL_GOLD_MID_PROXY_NOT_BANK_BID_ASK");
 A.equal(p.noRealBankBidAsk,true);
 A.equal(p.noEventsValidated,true);
});
test("As-of market inputs NEVER include same-bar or future price data",()=>{
 const p=Pilot.run();
 for(const x of p.signals){
  A.ok(Date.parse(x.featureAt)<Date.parse(x.timeUTC));
  A.ok(x.featureAgeHours<=96);
  A.ok([6,9].includes(new Date(x.timeUTC).getUTCHours()));
 }
 for(const x of p.fills){
  A.ok([6,9,12].includes(new Date(x.timeUTC).getUTCHours()));
 }
 for(const t of p.trades){
  A.ok([6,9,12].includes(new Date(t.atUTC).getUTCHours()));
  A.ok(Date.parse(t.fromSignal)<Date.parse(t.atUTC));
 }
});
test("Future-price perturbation does not change earlier Jan decisions",()=>{
 const d=Pilot.loadPinned(),a=Pilot.walk(d.rows);
 const changed=d.rows.map(x=>({...x}));
 for(const r of changed){
  if(r.tt>="2023-01-19T00:00:00.000Z")r.p*=1.01;
 }
 const b=Pilot.walk(changed);
 const prefix=x=>x.signals.filter(v=>v.timeUTC<"2023-01-18T00:00:00.000Z");
 A.deepEqual(prefix(a),prefix(b));
});
test("No Jan 2026 files, no synthetic prices, no unverified economic events",()=>{
 const p=Pilot.run();
 A.equal(p.signals.every(x=>x.verifiedEconomicEvents===0),true);
 A.ok(p.dataLineage.every(x=>x.file.includes("RECOVERY_HIST_3H_")));
 A.equal(p.riskAdvisorOverrides,0);
});
test("Jan pilot bit-reproducible decisions, fills, benchmarks, fees",()=>{
 const x=Pilot.run(),y=Pilot.run();
 for(const k of ["endNAVUSD","maxDrawdownPct","tradesCount",
  "numberOfSignals","numberOfFills","feeDebitedUSD","benchmarks"])
  A.deepEqual(x[k],y[k]);
 A.deepEqual(x.trades,y.trades);
 A.deepEqual(x.signals,y.signals);
 A.ok(x.benchmarks.passiveGoldAfterTwoFeeLegsUSD>0);
});
test("No future data rows accepted in asof feature calculation",()=>{
 const past=[{tt:"2023-01-03T06:00:00.000Z",ts:START,p:1850}];
 for(let i=60;i>0;i--)past.unshift({
  tt:new Date(START-(i+1)*3600000).toISOString(),
  ts:START-(i+1)*3600000,p:1830+i*.01
 });
 A.throws(()=>Pilot.features(past,START),/FUTURE_FEATURE/);
});
