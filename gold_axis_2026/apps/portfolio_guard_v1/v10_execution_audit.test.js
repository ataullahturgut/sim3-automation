"use strict";
const test=require("node:test"),assert=require("node:assert/strict");
const vm=require("node:vm"),fs=require("node:fs"),path=require("node:path");
const {loadRows}=require("./adaptive_v7_app");
const {replayV6:lagged}=require("./v10_lagged_v7_engine");
const {audit,VERSION,crossCheckTrades}=require("./v10_execution_audit");
const near=(a,b)=>assert.ok(Math.abs(a-b)<0.000025,String(a)+" vs "+String(b));
let cached;
const result=()=>cached??(cached=audit());

test("V7 same checkpoint execution is not a permissible V10 order fill",()=>{
 const x=result();
 near(x.base2026.v7OriginalSameBarUSD,123.52954535978293);
 near(x.base2026.v7DelayedBankUSD,116.50002607739015);
 near(x.base2026.v10BankRecoveryUSD,130.6663238249077);
 assert.ok(x.base2026.v7DelayedBankUSD<x.base2026.cashUSD);
 assert.equal(x.contracts.barSignalNotSameBarFill,true);
 assert.equal(x.contracts.realBankBidAskPresent,false);
});

test("V10 strict 336h plus revalidated positive regime blocks March relong",()=>{
 const x=result();
 assert.equal(x.model.saleToReentryMinimumHours,336);
 assert.equal(x.deniedBuys.total,18);
 assert.equal(x.transactions.delayedBaseline.length,4);
 assert.equal(x.transactions.guarded.length,2);
 assert.deepEqual(x.transactions.guarded.map(t=>t.side),["BUY","SELL"]);
 assert.ok(x.deniedBuys.examples.every(q=>q.decision==="BLOCK_BUY"));
 assert.ok(x.deniedBuys.examples.every(q=>q.at.startsWith("2026-03")));
 assert.ok(x.deniedBuys.examples.some(q=>q.reentryAgeHours<336));
});

test("original negative controls: protection has not independently succeeded before 2026",()=>{
 const x=result();
 assert.equal(x.negativeControl2025.deniedBuys,0);
 near(x.negativeControl2025.delayedV7USD,101.4365705394282);
 near(x.negativeControl2025.guardedV10USD,101.4365705394282);
 assert.ok(x.negativeControl2025.guardedV10USD<x.negativeControl2025.passiveGoldUSD);
 const y24=x.historicalControl.find(q=>q.period==="2024_2023HISTORY");
 const y25=x.historicalControl.find(q=>q.period==="2025_2023HISTORY");
 near(y24.finalUSD,108.61461132260524);
 near(y25.finalUSD,110.66472314789095);
 assert.ok(y24.finalUSD<y24.passiveGoldUSD);
 assert.ok(y25.finalUSD<y25.passiveGoldUSD);
 assert.equal(y25.gateBlocked,2);
});

test("deferred 1-3 checkpoint latency and additional fee stress test never invents bank asks",()=>{
 const x=result();
 assert.equal(x.costLatencySensitivity.length,9);
 assert.equal(x.contracts.feePerDirection,.008);
 for(const q of x.costLatencySensitivity){
  assert.ok(q.finalUSD>119.753917); // observed 2026-only, NOT guarantee
  assert.ok([1,2,3].includes(q.executionBankCheckpoints));
  assert.ok([.008,.0095,.0105].includes(q.feePerSide));
  assert.equal(q.tradeCount,2);
 }
 const p=x.costLatencySensitivity.filter(q=>q.feePerSide===.008);
 assert.ok(p[0].finalUSD>p[1].finalUSD&&p[1].finalUSD>p[2].finalUSD);
 assert.equal(x.scientificGate.automaticPromotion,false);
 assert.equal(x.scientificGate.liveTradingAuthorized,false);
 assert.equal(x.scientificGate.validationPassed,false);
});

test("every actual AL/SAT fill is later than signal, no lookahead even weekends",()=>{
 const x=result();
 for(const trade of x.transactions.guarded){
  assert.ok(Date.parse(trade.at)>Date.parse(trade.signalAt));
  assert.ok([6,9,12].includes(new Date(trade.at).getUTCHours()));
 }
 const r=lagged(loadRows(),{reentry_protocol:"matured_recovery"});
 assert.doesNotThrow(()=>crossCheckTrades(r));
 assert.equal(r.unfilledPendingOrder,null);
 assert.ok(r.queuedSignals.every(s=>s.executionEarliestNextCheckpoint));
});

test("shifting future bars cannot change as-of decisions in the past",()=>{
 const source=loadRows(),opts={start:"2026-02-02T06:00:00Z",stop:"2026-05-29T12:00:00Z",
  reentry_protocol:"matured_recovery",include_decisions:true};
 const before=lagged(source,opts);
 const shifted=source.map(r=>r.tt>opts.stop?{...r,p:r.p*1.6,c:r.c*1.6,r4:70,r1:70,r3:70}:r);
 const after=lagged(shifted,opts);
 near(before.final_usd,after.final_usd);
 assert.deepEqual(before.trades,after.trades);
 assert.deepEqual(before.decisionLog,after.decisionLog);
});

test("strict API fail-closed; V7 is not modified by V10 experiment",()=>{
 const x=result();
 assert.equal(x.version,VERSION);
 assert.equal(x.source.verifiedRows,3511);
 assert.equal(x.source.extendedRows,6724);
 assert.equal(x.contracts.independentBlindValidation,false);
 assert.equal(x.contracts.verifiedMacroFirstprints,0);
 assert.equal(x.model.reentryGateOrigin,"hypothesis_informed_by_inspected_2026");
 const {requestHandler}=require("./server");
 function get(method,url){
  let status,body;
  requestHandler({method,url},{writeHead(s){status=s},end(data){body=data}});
  return {status,body:body?JSON.parse(body):null};
 }
 const api=get("GET","/api/algorithm/v10/evidence");
 assert.equal(api.status,200);
 assert.equal(api.body.version,VERSION);
 assert.equal(api.body.scientificGate.liveTradingAuthorized,false);
 assert.equal(get("POST","/api/algorithm/v10/evidence").status,405);
 assert.equal(get("GET","/api/health").status,200);
 const html=fs.readFileSync(path.join(__dirname,"public/index.html"),"utf8");
 assert.match(html,/id="runV10Evidence"/);
 const app=fs.readFileSync(path.join(__dirname,"public/app.js"),"utf8");
 assert.doesNotThrow(()=>new vm.Script(app));
});
