"use strict";
const test=require("node:test");
const assert=require("node:assert/strict");
const {loadRows}=require("./adaptive_v7_app");
const {FEE,quoteByMonth,maximizeCompletedRounds,runIntramonthOracle}=require("./intramonth_oracle_v7");
const eq=(a,b)=>assert.ok(Math.abs(a-b)<0.00003,String(a)+" vs "+String(b));

test("hindsight DP covers 2026 observed 09:00–15:00 Turkey quotes only",()=>{
 const source=quoteByMonth(loadRows());assert.equal(source.length,9);
 assert.equal(source[0].month,"2026-01");
 assert.equal(source.at(-1).month,"2026-09");
 for(const m of source){
  assert.ok(m.quotes.length>=40);
  for(const q of m.quotes)assert.ok([6,9,12].includes(new Date(q.utc).getUTCHours()));
 }
 assert.equal(FEE,.008);
});
test("January one roundtrip improves monthly passive buy/hold ex post",()=>{
 const a=runIntramonthOracle();
 const jan=a.months[0];
 eq(jan.bestOneRound.finalUSD,124.96347658460691);
 eq(jan.holdGoldNetUSD,115.36646310370527);
 assert.equal(jan.bestOneRound.buys,1);
 assert.deepEqual(jan.bestOneRound.actions.map(a=>a.side),["BUY","SELL"]);
 assert.equal(jan.bestOneRound.actions[0].utc,"2026-01-02T06:00:00.000Z");
 assert.equal(jan.bestOneRound.actions[1].utc,"2026-01-29T06:00:00.000Z");
});
test("months losing buy-and-hold can contain profitable intramonth swing",()=>{
 const a=runIntramonthOracle(),march=a.months.find(m=>m.month==="2026-03"),
 september=a.months.find(m=>m.month==="2026-09");
 assert.ok(march.holdGoldNetUSD<100);
 assert.ok(march.bestOneRound.finalUSD>105);
 eq(march.bestOneRound.finalUSD,105.98818348475373);
 eq(september.bestOneRound.finalUSD,102.43038770560982);
});
test("increasing completed trade cap never reduces hindsight optimum",()=>{
 const a=runIntramonthOracle();
 for(const m of a.months){
  assert.ok(m.bestAnyUpTo15Rounds.finalUSD+1e-9>=m.bestTwoRounds.finalUSD);
  assert.ok(m.bestTwoRounds.finalUSD+1e-9>=m.bestOneRound.finalUSD);
  assert.ok(m.bestOneRound.finalUSD+1e-9>=m.bestOfMonthlyCashGoldUSD);
  for(const key of ["bestOneRound","bestTwoRounds","bestAnyUpTo15Rounds"]){
    const t=m[key].actions;for(let i=0;i<t.length;i++){
      assert.equal(t[i].side,i%2===0?"BUY":"SELL");
      if(i>0)assert.ok(Date.parse(t[i].utc)>Date.parse(t[i-1].utc));
    }
  }
 }
});
test("February to September chained hindsight cap benchmarks are known but untradeable",()=>{
 const a=runIntramonthOracle();
 eq(a.continuationUSD.one,189.7413455722961);
 eq(a.continuationUSD.two,211.26365290088182);
 eq(a.continuationUSD.upto15,222.56410866414694);
 eq(a.continuationUSD.hold24,221.4031427074753);
 assert.equal(a.status,"EX_POST_UNTRADEABLE_ORACLE");
 assert.equal(a.liveTradingAuthorized,false);
 assert.equal(a.independentBlindTest,false);
 assert.equal(a.costs.realBankBidAsk,false);
});
test("altering September prices cannot affect August oracle or any earlier month",()=>{
 const rows=loadRows();
 const prev=runIntramonthOracle(rows);
 const changed=rows.map(r=>r.tt>="2026-09-01"?{...r,p:r.p*1.1,c:r.c*1.1}:r);
 const next=runIntramonthOracle(changed);
 assert.deepEqual(next.months.slice(0,8),prev.months.slice(0,8));
});
test("edge-case no profitable trade stays in cash",()=>{
 const quotes=[{utc:"2026-02-02T06:00:00.000Z",time:Date.parse("2026-02-02T06:00:00Z"),price:4500},
 {utc:"2026-02-02T09:00:00.000Z",time:Date.parse("2026-02-02T09:00:00Z"),price:4500}];
 const x=maximizeCompletedRounds(quotes,2);
 eq(x.finalUSD,100);assert.equal(x.actions.length,0);
});
