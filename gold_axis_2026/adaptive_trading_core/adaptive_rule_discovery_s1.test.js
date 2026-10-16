"use strict";
const {test}=require("node:test");
const assert=require("node:assert/strict");
const core=require("./adaptive_rule_discovery_s1");
const step=240*60000;
const start=Date.parse("2023-01-03T09:00:00Z");
const iso=t=>new Date(t).toISOString();
const market=(time,value)=>({value,availableAt:iso(time),observedAt:iso(time),
  source:"SYNTHETIC_TEST_NOT_MARKET_DATA"});
function ob(t,price,a,b,extra={}){
 const x={usd_normalized:market(t,a),silver_confirmation:market(t,b)};
 return {asof:iso(t),price,priceAvailableAt:iso(t),
   barStartedAt:iso(t-15*60000),barMinutes:15,
   features:x,...extra};
}
function initial(options={}){
 return core.create({featureNames:["usd_normalized","silver_confirmation"],
    horizons:[240,1440],anchorMinutes:240,...options});
}
test("Cannot create alpha from calendar, event ID or future target",()=>{
 for(const bad of ["year","event_id","month","future_gold","target_up","timestamp"]){
   assert.throws(()=>core.create({featureNames:[bad,"silver_confirmation"]}),
      /FORBIDDEN|SCHEMA/);
 }
});
test("Only completed bars, observed-at and available-at feature vintage allowed",()=>{
 const s=initial(),t=start;
 const sample=ob(t,1850,-1,1);
 const premature={...sample,barStartedAt:iso(t-10*60000)};
 assert.throws(()=>core.observe(s,premature),/NOT_YET_COMPLETE/);
 assert.equal(s.audit.observations,0);
 assert.throws(()=>core.observe(s,ob(t,1850,-1,1,{
   features:{usd_normalized:market(t+60000,-1),silver_confirmation:market(t,1)}
 })),/FUTURE_OR_REVERSED/);
 assert.equal(s.audit.observations,0);
 assert.throws(()=>core.observe(s,ob(t,1850,-1,1,{
   features:{usd_normalized:{...market(t,-1),kind:"NEWS",firstprintVerified:false},
     silver_confirmation:market(t,1)}
 })),/UNVERIFIED_EVENT_FIRSTPRINT/);
 assert.equal(s.audit.observations,0);
});
test("Missing independent features are missing, never silently fabricated zero",()=>{
 const s=initial(),t=start,q=ob(t,1850,-1,1);
 q.features.silver_confirmation=null;
 const r=core.observe(s,q);
 assert.equal(r.anchored,false);
 assert.equal(s.rules.length,0);
 assert.equal(s.audit.rejectedMissing,1);
 const later=core.observe(s,ob(t+step,1850,-1,1));
 assert.equal(later.anchored,true);
 assert.equal(s.rules[0].center.usd_normalized,-1);
});
test("No future labels: delayed learning updates only after the 4h outcome is observable",()=>{
 const s=initial();
 let r=core.observe(s,ob(start,1850,-1,1));
 assert.equal(r.matured,0);
 assert.equal(s.pending.length,2);
 r=core.observe(s,ob(start+step-15*60000,1851,-1,1));
 assert.equal(r.matured,0);
 r=core.observe(s,ob(start+step,1860,-1,1));
 assert.equal(r.matured,1);
 assert.equal(core.rules(s)[0].outcomes[240].n,1);
 assert.equal(core.rules(s)[0].outcomes[1440].n,0);
 assert.ok(core.rules(s)[0].outcomes[240].meanLogPct>0);
});
test("Expired label is skipped rather than assigned price from the wrong day",()=>{
 const s=initial({maxLateMinutes:60});
 core.observe(s,ob(start,1850,-1,1));
 core.observe(s,ob(start+step+120*60000,1890,-1,1));
 assert.equal(s.audit.labelsSkipped,1);
 assert.equal(core.rules(s)[0].outcomes[240].n,0);
});
test("Synthetic opposing economic states grow distinct data-defined rules and learn opposite outcomes",()=>{
 const s=initial({horizons:[240],maxRules:8});
 let price=1800,last=null;
 for(let i=0;i<100;i++){
   if(last!==null)price*=Math.exp((last==="A"?.6:-.7)/100);
   const regime=(Math.floor(i/10)%2===0)?"A":"B";
   core.observe(s,ob(start+i*step,price,regime==="A"?-1:1,regime==="A"?1:-1));
   last=regime;
 }
 const rr=core.rules(s);
 assert.ok(rr.length>=2,JSON.stringify(rr));
 const pA=core.forecast(s,{asof:iso(start+100*step),features:ob(start+100*step,price,-1,1).features});
 const pB=core.forecast(s,{asof:iso(start+100*step),features:ob(start+100*step,price,1,-1).features});
 assert.ok(pA.byHorizon[0].ready);assert.ok(pB.byHorizon[0].ready);
 assert.ok(pA.byHorizon[0].expectedLogPct>0,
   "opposite signed regimes should be distinguishable "+JSON.stringify(pA.byHorizon));
 assert.ok(pB.byHorizon[0].expectedLogPct<0,
   "opposite signed regimes should be distinguishable "+JSON.stringify(pB.byHorizon));
 assert.ok(rr.some(x=>x.outcomes[240].up>0));
 assert.ok(rr.some(x=>x.outcomes[240].down>0));
 assert.equal(s.audit.anchors,100);
 assert.equal(s.audit.labelsMatured,99);
});
test("Checkpoint restores learned rule and pending horizon labels unchanged",()=>{
 const s=initial();const a=ob(start,1850,-1,1);
 core.observe(s,a);
 core.observe(s,ob(start+step,1860,-1,1));
 const saved=core.checkpoint(s);
 const restored=core.restore(saved);
 assert.deepEqual(restored,s);
 assert.deepEqual(core.rules(restored),core.rules(s));
 core.observe(restored,ob(start+2*step,1870,-1,1));
 core.observe(s,ob(start+2*step,1870,-1,1));
 assert.deepEqual(core.checkpoint(restored),core.checkpoint(s));
});
test("S1 is explicitly NOT a trading policy and never outputs BUY or SELL",()=>{
 const s=initial();
 const d=core.observe(s,ob(start,1850,-1,1));
 assert.equal(d.action,null);
 assert.equal(d.policyStatus,"NOT_IMPLEMENTED_NO_BUY_SELL");
 assert.equal(s.audit.tradeActions,0);
 assert.throws(()=>core.observe(s,ob(start+step,1870,-1,1,{futureReturn:20})),
   /FORBIDDEN_FUTURE_TARGET/);
});
