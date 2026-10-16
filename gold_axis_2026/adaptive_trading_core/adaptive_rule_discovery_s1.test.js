"use strict";
const {test}=require("node:test");
const assert=require("node:assert/strict");
const core=require("./adaptive_rule_discovery_s1");
const step=240*60000;
const start=Date.parse("2023-01-03T09:00:00Z");
const iso=t=>new Date(t).toISOString();
const market=(time,value)=>({value,availableAt:iso(time),observedAt:iso(time),
  source:"SYNTHETIC_TEST_NOT_MARKET_DATA",kind:"MARKET"});
function ob(t,price,a,b,extra={}){
 const x={usd_normalized:market(t,a),silver_confirmation:market(t,b)};
 return {asof:iso(t),price,priceAvailableAt:iso(t),
   priceSource:"SYNTHETIC_TEST_NOT_MARKET_DATA",
   barStartedAt:iso(t-15*60000),barMinutes:15,
   features:x,...extra};
}
function initial(options={}){
 return core.create({featureNames:["usd_normalized","silver_confirmation"],
    horizons:[240,1440],anchorMinutes:240,
    sourceRegistry:{
      SYNTHETIC_TEST_NOT_MARKET_DATA:{kind:"MARKET",evidenceStatus:"SYNTHETIC_ONLY"},
      VERIFIED_EVENT_TEST:{kind:"EVENT",evidenceStatus:"VERIFIED_PIT"}
    },...options});
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
   features:{usd_normalized:{...market(t,-1),kind:"EVENT",source:"VERIFIED_EVENT_TEST",firstprintVerified:false},
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
 const s=initial({maxLateMinutes:15});
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

test("Retrospective forecast cannot borrow coefficients learned later",()=>{
  const s=initial({horizons:[240]});
  core.observe(s,ob(start,1850,-1,1));
  for(let i=1;i<=12;i++)core.observe(s,ob(start+i*step,1850+i*8,-1,1));
  assert.ok(core.forecast(s,{asof:iso(start+12*step),features:ob(start+12*step,1946,-1,1).features}).byHorizon[0].ready);
  assert.throws(()=>core.forecast(s,{asof:iso(start),features:ob(start,1850,-1,1).features}),/HISTORICAL_FORECAST/);
});
test("75 minute late observation does not silently become a 4 hour outcome label",()=>{
 const s=initial({horizons:[240]});
 core.observe(s,ob(start,1850,-1,1));
 core.observe(s,ob(start+step+75*60000,1890,-1,1));
 assert.equal(s.audit.labelsSkipped,1);
 assert.equal(core.rules(s)[0].outcomes[240].n,0);
});
test("Unknown or merely named research sources cannot generate rules",()=>{
 const s=initial();
 const forged=ob(start,1800,-1,1);
 forged.features.usd_normalized.source="FAKE_UNVERIFIED_SOURCE";
 assert.throws(()=>core.observe(s,forged),/UNREGISTERED_FEATURE_SOURCE/);
 assert.equal(s.rules.length,0);
 const forgedPrice=ob(start,1800,-1,1);
 forgedPrice.priceSource="FAKE_UNVERIFIED_SOURCE";
 assert.throws(()=>core.observe(s,forgedPrice),/UNREGISTERED_PRICE_SOURCE/);
 assert.equal(s.audit.observations,0);
});
test("Rule-cap saturation abstains rather than mislabels unrelated regimes",()=>{
 const s=initial({horizons:[240],maxRules:2});
 core.observe(s,ob(start,1800,-3,-3));
 core.observe(s,ob(start+step,1790,3,3));
 const third=core.observe(s,ob(start+2*step,1810,3,-3));
 assert.equal(s.rules.length,2);
 assert.equal(third.anchored,false);
 assert.equal(s.audit.rulesSaturated,1);
});

test("A contradicted mature-outcome rule splits into conditional daughters without losing labels",()=>{
 const s=initial({horizons:[240],noveltyDistance:1.25,maxRules:8});
 let price=1800,last=null;
 for(let i=0;i<105;i++){
   const feature=Math.floor(i/12)%2===0?-.2:.2;
   if(last!==null)price*=Math.exp((last<0?.8:-.8)/100);
   core.observe(s,ob(start+i*step,price,feature,.1));
   last=feature;
 }
 assert.equal(s.audit.ruleCreated,1); // both feature states initially one rule
 assert.equal(s.audit.ruleSplit,1);
 assert.equal(s.rules.length,2);
 const rr=core.rules(s), old=s.splitRoutes.R0001;
 assert.ok(old);
 assert.equal(rr.reduce((z,x)=>z+x.outcomes[240].n,0),s.audit.labelsMatured);
 const up=rr.find(x=>x.center.usd_normalized<0),down=rr.find(x=>x.center.usd_normalized>0);
 assert.ok(up.outcomes[240].meanLogPct>.5);
 assert.ok(down.outcomes[240].meanLogPct<-.5);
 assert.deepEqual(core.checkpoint(core.restore(core.checkpoint(s))),core.checkpoint(s));
});
test("Noise-free identical outcomes across contradictory features do NOT cause false splits",()=>{
 const s=initial({horizons:[240],noveltyDistance:1.25,maxRules:8});
 let price=1800;
 for(let i=0;i<85;i++){
   if(i>0)price*=Math.exp(.4/100);
   core.observe(s,ob(start+i*step,price,i%2===0?-.2:.2,.1));
 }
 assert.equal(s.audit.ruleSplit,0);
 assert.equal(s.rules.length,1);
});
