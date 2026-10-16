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
 assert.ok(s.scores.censoredPredictions>=n);
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
 assert.ok(s.scores.censoredPredictions>=n);
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
