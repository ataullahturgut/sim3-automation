"use strict";
const test=require("node:test"),assert=require("node:assert/strict");
const v6=require("./crossmarket_v6"),v4=require("./recovery_v4"),v3=require("./recovery_v3");
test("closed H1 bars for cross-market 6h only; gaps remain UNKNOWN",()=>{
 const d=v6.loadCross();
 assert.equal(d.store.size,4107);
 for(const item of d.store.values()){
  for(const x of ["nq","zn","si","cl"]){
   const value=item[x+"6"],age=item["age_"+x];
   if(value!==null){
    assert.ok(Number.isFinite(value));assert.ok(Number.isInteger(age));
    assert.ok(age>=1&&age<=4);
   }
  }
 }
 const sparse=Array.from(d.store.values()).filter(x=>x.si6!==null).length;
 assert.ok(sparse<d.store.size/10);
 const full=Array.from(d.store.values()).find(x=>x.nq6!==null&&x.zn6!==null);
 assert.ok(full);
 const nothing=v6.classifyCross({nq6:null,zn6:-1});
 assert.equal(nothing.state,"UNKNOWN_DATA");
 assert.equal(nothing.causalMechanism,"UNRESOLVED");
});
test("economic OLAY-02 audit must not treat hypotheses as verified causes",()=>{
 const a=v6.auditEventDNA();
 assert.ok(a.totalCases>=70);
 assert.ok(a.economicCandidates.length>=2);
 assert.equal(a.provenCauses,0);
 assert.equal(a.asOfValidatedForTrading,0);
 assert.equal(a.hasEconomicFirstprintEvidence,a.confirmedFirstprints>0);
});
test("V6 overlay does not mutate frozen V4 and cash state is carried month to month",()=>{
 const data=v6.runResearch();
 assert.equal(data.automaticPromotionAuthorized,false);
 assert.equal(data.continuity.openingCashUSD,119.75391720039644);
 assert.equal(data.months.length,8);
 assert.deepEqual(data.annual.map(x=>x.year),[2023,2024,2025]);
 assert.ok(Math.abs(data.continuity.v4USD-96.70696771810788)<1e-8);
 assert.ok(data.annual.every(a=>a.V4>0&&a.V6>0));
 assert.equal(data.evidence.actualBankBidAskIncluded,false);
 assert.equal(data.evidence.prospectivelyBlind,false);
 assert.equal(data.evidence.verifiedEconomicCausality,false);
 assert.ok(data.continuity.v6Orders.every(o=>["BUY_GOLD","SELL_TO_CASH"].includes(o.action)));
 for(const order of data.continuity.v6Orders)
  assert.ok([9,12,15].includes(Number(order.tr.slice(11,13))));
});
test("V6 calculation is deterministic and risk-off price veto uses NQ and ZN together",()=>{
 const a=v6.runResearch(),b=v6.runResearch();
 assert.deepEqual(a,b);
 assert.equal(v6.classifyCross({nq6:-1,zn6:-.2}).state,"BROAD_COSELL_PRICE_PROXY");
 assert.equal(v6.classifyCross({nq6:-1,zn6:+.2}).state,"NO_JOINT_STRESS");
 assert.equal(v6.classifyCross({nq6:+.5,zn6:-.3}).state,"NO_JOINT_STRESS");
});
test("historical year V4 clone and true untouched V4 have identical positions",()=>{
 const hist=v3.loadHistorical(),training=v4.trainBefore(hist,Date.parse("2025-01-01T00:00:00Z"));
 const rows=hist.filter(r=>r.tt.startsWith("2025"));
 const proxy=v6.simulate(rows,training,v6.loadCross(),{startUSD:100,overlay:false});
 const actual=v4.simulate(rows,training,{initialUSD:100,id:"CHECK"});
 assert.ok(Math.abs(actual.finalUSD-proxy.finalUSD)<1e-9);
 assert.deepEqual(actual.actions.map(x=>x.utc),proxy.actions.map(x=>x.utc));
});
