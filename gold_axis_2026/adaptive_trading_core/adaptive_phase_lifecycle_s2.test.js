"use strict";
const {test}=require("node:test");
const assert=require("node:assert/strict");
const life=require("./adaptive_phase_lifecycle_s2");
const model=require("./adaptive_market_core_s1_s2");
const MIN=60000;
const first=Date.parse("2023-01-02T09:00:00Z"),SRC="SYNTHETIC_XAU_COMPLETE_M15";
const stamp=t=>new Date(t).toISOString();
const registry=type=>({[SRC]:{kind:"MARKET",evidenceStatus:type}});
function bar(t,price){
 return {asof:stamp(t),barStartedAt:stamp(t-15*MIN),barMinutes:15,
  price,priceAvailableAt:stamp(t),priceSource:SRC};
}
function series(s,from,prices){
 const events=[];
 for(let i=0;i<prices.length;i++)events.push(life.observe(s,bar(from+i*15*MIN,prices[i])));
 return events;
}
const increasing=(n,p=1800)=>Array.from({length:n},(_,i)=>p*Math.pow(1.002,i));
test("Phase lifecycle and its S1 composition are one model with no trade decisions",()=>{
 const s=life.create({sourceRegistry:registry("SYNTHETIC_ONLY")});
 const prices=increasing(44);
 const obs=series(s,first,prices);
 assert.equal(obs[0].phase,"WARMUP");
 assert.ok(obs.some(x=>x.phase==="START"));
 assert.ok(obs.some(x=>x.phase==="CONTINUE"));
 assert.ok(!obs.some(x=>x.action!==null));
 assert.equal(s.completed.length,0); // Still rising; no future end label
 assert.equal(s.scores.scored,0);
 const bridge=model.create({sourceId:SRC,sourceEvidence:"SYNTHETIC_ONLY",
  learningMode:"STRICT_WALK_FORWARD"});
 let n=0;for(let i=0;i<prices.length;i++){
  const x=model.observe(bridge,bar(first+i*15*MIN,prices[i]));
  assert.equal(x.tradeAllowed,false);n++;
 }
 const summary=model.summary(bridge);
 assert.equal(summary.lifecycle.observations,n);
 assert.equal(summary.ruleDiscovery.observations,n);
 assert.equal(summary.bankTrades,0);
 assert.ok(summary.ruleDiscovery.anchors>0);
 assert.deepEqual(model.checkpoint(model.restore(model.checkpoint(bridge))),
  model.checkpoint(bridge));
});
test("Opposite movement ends a completed episode and only then trains the empirical duration memory",()=>{
 const s=life.create({sourceRegistry:registry("SYNTHETIC_ONLY")});
 const up=increasing(40);
 series(s,first,up);
 assert.equal(s.completed.length,0);
 const decline=Array.from({length:30},(_,i)=>up.at(-1)*Math.pow(.992,i+1));
 const events=series(s,first+up.length*15*MIN,decline);
 assert.ok(events.some(x=>x.phase==="END"),"need a causal end observation");
 assert.ok(s.completed.length>=1);
 assert.ok(s.completed[0].durationMinutes>0);
 assert.equal(s.completedDurationsMinutes.length,s.completed.length);
 assert.ok(s.endedAt[s.completed[0].id]>=first);
});
test("Missing 15m bar right-censors open episode and unresolved forecasts",()=>{
 const s=life.create({sourceRegistry:registry("SYNTHETIC_ONLY")});
 series(s,first,increasing(30));
 assert.ok(s.active);
 assert.equal(s.completed.length,0);
 const n=s.pending.length;
 const last=s.lastAt;
 const out=life.observe(s,bar(last+3*60*MIN,1900));
 assert.equal(out.phase,"WARMUP");
 assert.equal(s.active,null);
 assert.equal(s.censored,1);
 assert.equal(s.completed.length,0);
 assert.equal(s.pending.length,0);
 assert.ok(Object.values(s.scores.byHorizon).reduce((z,h)=>z+h.censored,0)>=n);
 assert.ok(s.scores.censoredPredictions>0);
});
test("Price first-access, complete M15 and strict provenance prevent time travel",()=>{
 const s=life.create({sourceRegistry:registry("RECONSTRUCTED_MARKET_ASOF"),
  learningMode:"STRICT_WALK_FORWARD"});
 assert.throws(()=>life.observe(s,bar(first,1800)),/S2_RECONSTRUCTED_NOT_PIT/);
 assert.equal(s.observations,0);
 const v=life.create({sourceRegistry:registry("SYNTHETIC_ONLY")});
 const o=bar(first,1800);
 assert.throws(()=>life.observe(v,{...o,priceAvailableAt:stamp(first+MIN)}),
   /S2_INCOMPLETE_OR_FUTURE_PRICE/);
 assert.throws(()=>life.observe(v,{...o,futurePhase:"END"}),
   /S2_FUTURE_TARGET_FORBIDDEN/);
 assert.throws(()=>life.observe(v,{...o,barMinutes:60}),
   /S2_INCOMPLETE_OR_FUTURE_PRICE/);
 life.observe(v,o);
 assert.throws(()=>life.observe(v,o),/S2_TIME_NOT_MONOTONIC/);
 assert.equal(v.observations,1);
});
test("A missing price bar must not be reinterpreted as a confirmed phase end",()=>{
 const s=life.create({sourceRegistry:registry("SYNTHETIC_ONLY")});
 series(s,first,increasing(25));
 const before=s.completed.length;
 life.observe(s,bar(s.lastAt+48*60*MIN,2050));
 assert.equal(s.completed.length,before);
 assert.ok(s.censored>0);
});
test("A restored lifecycle checkpoint produces byte-identical continuation and hazard",()=>{
 const s=life.create({sourceRegistry:registry("SYNTHETIC_ONLY")});
 const prices=[...increasing(40),...Array.from({length:32},(_,i)=>1900*Math.pow(.996,i))];
 series(s,first,prices.slice(0,45));
 const copy=life.restore(life.checkpoint(s));
 for(let i=45;i<prices.length;i++){
  const t=first+i*15*MIN,o=bar(t,prices[i]);
  assert.deepEqual(life.observe(s,o),life.observe(copy,o));
 }
 assert.deepEqual(life.summary(s),life.summary(copy));
});
test("Lifecycle never claims bank fees, trading readiness, or science success",()=>{
 const s=life.create({sourceRegistry:registry("SYNTHETIC_ONLY")});
 series(s,first,increasing(28));
 const r=life.summary(s);
 assert.equal(r.financialTrades,0);
 assert.equal(r.profitabilityClaim,false);
 assert.equal(r.status,"S2_DEVELOPMENT_RESEARCH_NOT_ACCEPTED");
 assert.equal(r.prediction.brier,null);
});


test("Different 2025 price source switches must right-censor, even on adjacent M15 bars",()=>{
 const other="OTHER_HISTORICAL_SOURCE";
 const s=life.create({sourceRegistry:{[SRC]:{kind:"MARKET",evidenceStatus:"RECONSTRUCTED_MARKET_ASOF"},
   [other]:{kind:"MARKET",evidenceStatus:"RECONSTRUCTED_MARKET_ASOF"}}});
 series(s,first,increasing(30));
 const n=s.pending.length;
 const t=s.lastAt+15*MIN;
 life.observe(s,{...bar(t,2000),priceSource:other});
 assert.equal(s.censored,1);
 assert.equal(s.completed.length,0);
 assert.equal(s.pending.length,0);
 assert.ok(Object.values(s.scores.byHorizon).reduce((z,h)=>z+h.censored,0)>=n);
 assert.ok(s.scores.censoredPredictions>0);
});
test("S2 integration rejects unregistered sources and preserves no-trade authority",()=>{
 const b=model.create({sourceId:SRC,sourceEvidence:"SYNTHETIC_ONLY",
  learningMode:"STRICT_WALK_FORWARD"});
 assert.throws(()=>model.observe(b,{...bar(first,1700),priceSource:"FORGED"}),
   /MODEL_UNDECLARED_SOURCE/);
 assert.equal(b.audit.observed,0);
 const done=model.observe(b,bar(first,1700));
 assert.equal(done.action,null);
 assert.equal(done.tradeAllowed,false);
});


test("Five horizons are issued once per independent 4h anchor and have separate outcome ledgers",()=>{
 const s=life.create({sourceRegistry:registry("SYNTHETIC_ONLY")});
 const events=series(s,first,increasing(26));
 const start=events.find(x=>x.phase==="START");
 assert.ok(start);
 assert.deepEqual(life.DEFAULT_HORIZONS,[240,1440,4320,10080,20160]);
 assert.ok(start.hazardsByHorizon);
 assert.deepEqual(Object.keys(start.hazardsByHorizon),["240","1440","4320","10080","20160"]);
 for(const H of life.DEFAULT_HORIZONS){
   assert.equal(s.scores.byHorizon[H].issued,1);
   assert.equal(s.scores.byHorizon[H].scored,0);
 }
 assert.equal(s.pending.length,5);
 assert.equal(start.hazard4h.horizonMinutes,240);
 assert.equal(start.hazardsByHorizon[20160].continuationP,null); // no support, no magic future
});
test("A short completed episode proves a long-horizon END early, never fake horizon survival",()=>{
 const s=life.create({sourceRegistry:registry("SYNTHETIC_ONLY"),minReady:5});
 // Synthetic PREVIOUSLY ENDED episodes available before this test's first bar.
 for(let i=0;i<16;i++){
  s.completed.push({id:500+i,direction:1,durationMinutes:120+i*15,
    endedAt:first-(i+1)*24*60*MIN,snapshots:[]});
 }
 const up=increasing(40),down=Array.from({length:30},(_,i)=>
   up.at(-1)*Math.pow(.991,i+1));
 series(s,first,[...up,...down]);
 assert.ok(s.scores.byHorizon[1440].positive>0);
 assert.equal(s.scores.byHorizon[1440].negative,0);
 assert.ok(s.scores.byHorizon[20160].positive>0);
 const long=life.summary(s).continuationAndEndByHorizon;
 assert.equal(long[20160].estimable,false); // all positive != predictive skill
 assert.match(long[20160].scienceWarning,/ONE_SIDED/);
});
test("At a missing future span, long-horizon survival must be censored, not 0-labelled",()=>{
 const s=life.create({sourceRegistry:registry("SYNTHETIC_ONLY")});
 series(s,first,increasing(32));
 const due=s.pending.filter(q=>q.horizonMinutes===20160);
 assert.ok(due.length>0);
 const old=s.scores.byHorizon[20160].negative;
 life.observe(s,bar(s.lastAt+24*60*MIN,1980));
 assert.equal(s.scores.byHorizon[20160].negative,old);
 assert.ok(s.scores.byHorizon[20160].censored>=due.length);
});
