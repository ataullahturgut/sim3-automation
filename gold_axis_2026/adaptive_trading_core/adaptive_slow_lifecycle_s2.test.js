"use strict";
const {test}=require("node:test"),assert=require("node:assert/strict");
const life=require("./adaptive_slow_lifecycle_s2");
const bridge=require("./adaptive_market_core_s1_s2");
const FROM=Date.parse("2023-01-02T00:00:00Z");
const ID="HISTORICAL_TEST_SOURCE",ALT="TEST_2025_SOURCE",D=86400000;
const reg={ [ID]:{kind:"MARKET",evidenceStatus:"SYNTHETIC_ONLY"},
 [ALT]:{kind:"MARKET",evidenceStatus:"SYNTHETIC_ONLY"} };
function days(count=60,start=FROM){
 const out=[];let d=start;
 while(out.length<count){
  const day=new Date(d).getUTCDay();
  if(day>=1&&day<=5)out.push(new Date(d).toISOString().slice(0,10));
  d+=D;
 }
 return out;
}
function session(label,price,extra={}){
 const end=Date.parse(label+"T22:00:00Z");
 return {session:label,source_id:ID,n:92,full_n:92,
  first_bar:new Date(end-23*3600000).toISOString(),
  last_bar:new Date(end-15*60000).toISOString(),
  last_native_minute_bars:15,max_gap_minutes:15,close_price:price,...extra};
}
function bars(start=1800){
 return Array.from({length:95},(_,i)=>{
   // several large multi-week directions, not one intraday 4-hour episode.
   if(i<25)return start*Math.pow(1.006,i);
   if(i<48)return start*Math.pow(1.006,25)*Math.pow(.992,i-25);
   if(i<72)return start*Math.pow(1.006,25)*Math.pow(.992,23)*Math.pow(1.008,i-48);
   return start*Math.pow(1.006,25)*Math.pow(.992,23)*Math.pow(1.008,24)*Math.pow(.993,i-72);
 });
}
const m15=(t,p)=>({asof:new Date(t).toISOString(),
 barStartedAt:new Date(t-15*60000).toISOString(),
 barMinutes:15,price:p,priceAvailableAt:new Date(t).toISOString(),
 priceSource:ID});
test("A full Friday-to-Monday scheduled market closure is not an artificial episode/data gap",()=>{
 const s=life.create({sourceRegistry:reg});
 const d=days(11);
 for(let i=0;i<11;i++)life.observe(s,session(d[i],1800*Math.pow(1.01,i)));
 assert.equal(s.sessionBreaks,0);
 assert.equal(s.eligibleSessions,11);
 assert.ok(s.phases.START>=1);
 assert.ok(s.active);
});
test("Missing weekday censored while weekend passes; no fabricated endpoint or survival",()=>{
 const s=life.create({sourceRegistry:reg});
 const d=days(19);
 for(let i=0;i<14;i++)life.observe(s,session(d[i],1800*Math.pow(1.007,i)));
 assert.ok(s.active);
 const pending=s.pending.length,valid=s.complete.length;
 life.observe(s,session(d[16],1950)); // skip TWO expected weekdays
 assert.ok(s.sessionBreaks>=1);
 assert.equal(s.complete.length,valid);
 assert.ok(s.censored.length>=1);
 assert.equal(s.pending.length,0);
 assert.ok(Object.values(s.stats).reduce((n,x)=>n+x.censored,0)>=pending);
});
test("An incomplete closing bar, or 2023 undercovered session, is quarantined",()=>{
 const s=life.create({sourceRegistry:reg}),d=days(4);
 life.observe(s,session(d[0],1800));
 const q=life.observe(s,session(d[1],1810,{n:65,full_n:65}));
 assert.equal(q.phase,"REJECTED_SESSION");
 assert.equal(s.rejectedSessions,1);
 const bad=life.observe(s,session(d[2],1820,{n:92,full_n:92,
  last_native_minute_bars:14}));
 assert.equal(bad.phase,"REJECTED_SESSION");
 assert.equal(s.eligibleSessions,1);
});
test("A degraded-but-closed terminal bar may support a research session, quality is counted",()=>{
 const s=life.create({sourceRegistry:reg});
 const d=days(2);
 life.observe(s,session(d[0],1800,{n:92,full_n:90}));
 assert.equal(s.minorDegradedSessions,1);
 assert.equal(s.eligibleSessions,1);
 assert.equal(life.summary(s).scienceGate,"NOT_PROVEN");
});
test("Slow regime has episodes with days/weeks duration, not recycled 4h episode labels",()=>{
 const s=life.create({sourceRegistry:reg});
 const d=days(95),prices=bars();
 const got=d.map((day,i)=>life.observe(s,session(day,prices[i])));
 assert.ok(got.some(x=>x.phase==="START"));
 assert.ok(got.some(x=>x.phase==="CONTINUE"));
 assert.ok(got.some(x=>x.phase==="END"));
 assert.ok(s.complete.length>=2);
 assert.ok(s.complete.some(x=>x.sessions>=5));
 assert.ok(s.complete.every(x=>x.sessions>0));
 assert.ok(got.every(x=>x.action===null));
});
test("Slow signal conditions are known only at session UTC22 close; cannot enter earlier M15 rule",()=>{
 const model=bridge.create({sourceId:ID,sourceEvidence:"SYNTHETIC_ONLY",
  learningMode:"STRICT_WALK_FORWARD"});
 const d=days(15);
 for(let i=0;i<d.length;i++)
  bridge.observeSlowSession(model,session(d[i],1800*Math.pow(1.009,i)));
 const closing=Date.parse(d.at(-1)+"T22:00:00Z");
 const pre=bridge.observe(model,m15(closing-15*60000,1900));
 assert.equal(pre.action,null);
 assert.equal(model.s1.rules.length,0); // no intraday context or premature slow context
 bridge.observe(model,m15(closing+15*60000,1901));
 const nowKeys=Object.keys(model.s1.rules[0].center);
 assert.ok(nowKeys.includes("slow_trend_z"));
 assert.equal(bridge.summary(model).tradeAllowed,false);
});
test("Feed changes right-censor long trend rather than treating futures vendor continuity as one observed regime",()=>{
 const s=life.create({sourceRegistry:reg}),d=days(18);
 for(let i=0;i<15;i++)life.observe(s,session(d[i],1800*Math.pow(1.008,i)));
 assert.ok(s.active);
 life.observe(s,session(d[15],2000,{source_id:ALT}));
 assert.equal(s.sourceBreaks,1);
 assert.ok(s.censored.length>0);
 assert.equal(s.active,null);
});
test("Censored reference cannot pretend to end; all horizon forecasts are per-market-session units",()=>{
 const s=life.create({sourceRegistry:reg,minReady:5}),d=days(35);
 for(let i=0;i<35;i++)life.observe(s,session(d[i],1800*Math.pow(1.006,i)));
 const p=life.summary(s).byHorizon;
 for(const H of life.HORIZONS){
  assert.equal(p[H].horizonSessions,H);
  assert.ok(p[H].issued>0);
  assert.ok(p[H].end===0);
  assert.equal(p[H].scored,0);
 }
 assert.equal(life.summary(s).timeUnit,"COMPLETED_TRADING_SESSIONS_NOT_CALENDAR_DAYS");
});
test("Daily long-horizon checkpoint can be restored identically and unknown-horizon returns rejected",()=>{
 const s=life.create({sourceRegistry:reg}),d=days(35),prices=bars();
 for(let i=0;i<21;i++)life.observe(s,session(d[i],prices[i]));
 const restored=life.restore(life.checkpoint(s));
 for(let i=21;i<35;i++){
  const row=session(d[i],prices[i]);
  assert.deepEqual(life.observe(s,row),life.observe(restored,row));
 }
 assert.deepEqual(life.summary(s),life.summary(restored));
 assert.throws(()=>life.observe(s,{...session(d.at(-1),1850),
  availableAt:"2027-01-01T00:00:00Z"}),/S2S_NONMONOTONIC_SESSION/);
});
