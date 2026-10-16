"use strict";
const {test}=require("node:test"),assert=require("node:assert/strict");
const core=require("./adaptive_rule_discovery_s1");
const m=require("./replay_macro_waves_in_existing_core_s1");
const hour=3600000,day=24*hour,start=Date.parse("2023-01-06T13:30:00Z");
const iso=x=>new Date(x).toISOString();
const nlog=(p,ret)=>p*Math.exp(ret/100);
const header="event_type,event_ts_utc,actual,consensus,surprise,actual_available_as_of_utc,consensus_available_as_of_utc,surprise_ready_at_utc,pair_complete,actual_lineage_id,consensus_lineage_id,pit_use";
function dataset(n=24){
 const ledger=[header],rows=[];
 for(let i=0;i<n;i++){
  const release=start+i*14*day,at=release+hour,ts=iso(release);
  const employment=i%2===0,family=employment?"EMP":"CPI";
  const q=i%4<2?1:-1,ret=(q===1?.8:-.7),p=1900+i;
  const components=employment?{NFP:q*120,AHE:q*.2,UNEMP:-q*.1}:{CPI:q*.3};
  for(const [kind,surprise]of Object.entries(components)){
   ledger.push([kind,ts,1,0,surprise,ts,ts,ts,"True","actual_"+i+"_"+kind,
     "consensus_"+i+"_"+kind,"POST_RELEASE_ONLY"].join(","));
  }
  rows.push({kind:"EVENT",release_utc:ts,release_family:family,
    anchor_utc:iso(at),pre1h:q*.2,pre2h:q*.1,next4h:ret,
    anchor_price:p,due_price:nlog(p,ret),
    nfp:components.NFP??null,ahe:components.AHE??null,
    unemp:components.UNEMP??null,cpi:components.CPI??null});
  for(let j=0;j<4;j++){
   const a=at+(j+1)*day,k=j%2===0?.2:-.2,price=1900+i+j*.2;
   rows.push({kind:"CONTROL",release_utc:ts,anchor_utc:iso(a),
     pre1h:q*.1,pre2h:j*.02,next4h:k,anchor_price:price,
     due_price:nlog(price,k),nfp:null,ahe:null,unemp:null,cpi:null});
  }
 }
 return {rows,ledger:ledger.join("\n")+"\n"};
}
test("Existing S1 CORE is the learning engine and all independent macro events receive matured labels",()=>{
 const {rows,ledger}=dataset();
 const v=m.run(rows,ledger);
 assert.equal(v.model,"EXISTING_ADAPTIVE_RULE_DISCOVERY_S1");
 assert.equal(v.completeReleaseWaves,24);
 assert.equal(v.settled,120);
 assert.equal(v.eventCases,24);
 assert.equal(v.controlCases,96);
 assert.ok(v.economicRuleCount>=2);
 assert.ok(v.economicRuleMatureSupport.reduce((s,r)=>s+r.independentMatured4h,0)===24);
 assert.equal(v.tradePolicy,"NOT_IMPLEMENTED");
 assert.equal(v.modelGate,"FAIL");
 assert.equal(v.strictWalkForward,false);
 assert.equal(v.scoredBoth>0,true);
 assert.ok(!JSON.stringify(v).includes('"anchor_price"'));
});
test("Real labels must mature 4h after event; no future returns in CORE observation features",()=>{
 const {rows,ledger}=dataset(1);
 const v=m.observations(rows,ledger);
 const event=v.events.find(x=>x.anchor&&x.anchor.kind==="EVENT");
 const s=m.make(),features=event.anchor.features,asof=iso(event.at);
 const o={asof,barStartedAt:iso(event.at-15*60000),barMinutes:15,
  price:event.price,priceAvailableAt:asof,priceSource:Object.keys(m.registry())[0],
  features};
 assert.equal(core.observe(s,o).matured,0);
 assert.equal(s.audit.labelsMatured,0);
 assert.equal(s.pending.length,1);
 const d=iso(event.at+4*hour);
 const r=core.observe(s,{asof:d,barStartedAt:iso(event.at+4*hour-15*60000),
  barMinutes:15,price:event.anchor.duePrice,priceAvailableAt:d,
  priceSource:Object.keys(m.registry())[0],features:{}});
 assert.equal(r.matured,1);
 assert.equal(s.audit.labelsMatured,1);
 assert.equal(core.rules(s)[0].outcomes[240].n,1);
});
test("Retrospective ledger economic feature stays forbidden in STRICT_WALK_FORWARD",()=>{
 const {rows,ledger}=dataset(1),v=m.observations(rows,ledger);
 const a=v.events.find(x=>x.anchor?.kind==="EVENT"),t=iso(a.at);
 const strict=core.create({learningMode:"STRICT_WALK_FORWARD",
  featureNames:["gold_1h","gold_prev_1h","nfp_surprise_z","ahe_surprise_z","unemp_surprise_z","cpi_surprise_z"],
  horizons:[240],sourceRegistry:m.registry()});
 const ob={asof:t,barStartedAt:iso(a.at-15*60000),barMinutes:15,
  price:a.price,priceAvailableAt:t,priceSource:Object.keys(m.registry())[0],
  features:a.anchor.features};
 assert.throws(()=>core.observe(strict,ob),/EVENT_SOURCE_NOT_PIT_VERIFIED/);
 assert.equal(strict.audit.observations,0);
});
test("Release knowledge before 60min latency is rejected",()=>{
 const {rows,ledger}=dataset(1),v=m.observations(rows,ledger);
 const e=v.events.find(x=>x.anchor?.kind==="EVENT");
 assert.throws(()=>m.eventFeatures({release_family:"EMP",release_utc:iso(e.at-hour)},
   e.at-1, new Map()),/EVENT_ARRIVED_BEFORE/);
});
test("Price label tampering and missing macro lineage cannot enter a trained prototype",()=>{
 const a=dataset(2);
 a.rows[0].due_price*=1.01;
 assert.throws(()=>m.run(a.rows,a.ledger),/DUE_PRICE_RETURN_CONFLICT/);
 const b=dataset(2);
 b.ledger=b.ledger.replace("actual_0_NFP","").replace("actual_0_AHE","");
 assert.throws(()=>m.run(b.rows,b.ledger),/LEDGER_FEATURE_VALUE_OR_PROVENANCE_MISMATCH/);
});
test("Repeated negative-control timestamps counted once, not four times",()=>{
 const a=dataset(3);
 const w=a.rows.find(x=>x.kind==="CONTROL");
 a.rows.push({...w});
 const v=m.run(a.rows,a.ledger);
 assert.equal(v.controlAssignments,13);
 assert.equal(v.uniqueControls,12);
 assert.equal(v.controlCases,12);
});
test("A missing-release price does not become a simulated label or a market-only macro case",()=>{
 const d=dataset(3);
 d.rows[0]={...d.rows[0],anchor_utc:null,pre1h:null,pre2h:null,next4h:null,anchor_price:null,due_price:null};
 const v=m.run(d.rows,d.ledger);
 assert.equal(v.incompleteReleaseWaves,1);
 assert.equal(v.completeReleaseWaves,2);
 assert.equal(v.eventCases,2);
});


test("Completed NQ bar can condition existing CORE; unavailable silver remains missing",()=>{
 const d=dataset(2),a=d.rows.find(x=>x.kind==="EVENT"),at=Date.parse(a.anchor_utc);
 a.nq_1h=.35;a.nq_known_end_utc=iso(at-hour);
 a.si_1h=null;a.si_known_end_utc=null;
 const wave=m.observations(d.rows,d.ledger,{crossAssets:true});
 const event=wave.events.find(x=>x.anchor?.kind==="EVENT");
 assert.ok(event.anchor.features.nq_1h);
 assert.equal(event.anchor.features.nq_1h.kind,"MARKET");
 assert.ok(!Object.hasOwn(event.anchor.features,"si_1h"));
 const v=m.run(d.rows,d.ledger,{marketContext:"XAU_PLUS_RECONSTRUCTED_CME"});
 assert.equal(v.marketContext,"XAU_PLUS_RECONSTRUCTED_CME");
 assert.equal(v.strictWalkForward,false);
});
test("CME bar from future or earlier than the allowed freshness window is rejected",()=>{
 const d=dataset(1),a=d.rows.find(x=>x.kind==="EVENT"),at=Date.parse(a.anchor_utc);
 a.nq_1h=.25;a.nq_known_end_utc=iso(at+60000);
 assert.throws(()=>m.observations(d.rows,d.ledger,{crossAssets:true}),/STALE_OR_FUTURE_CROSS_ASSET/);
 a.nq_known_end_utc=iso(at-76*60000);
 assert.throws(()=>m.observations(d.rows,d.ledger,{crossAssets:true}),/STALE_OR_FUTURE_CROSS_ASSET/);
 a.nq_1h=null;
 assert.throws(()=>m.observations(d.rows,d.ledger,{crossAssets:true}),/INCOMPLETE_CROSS_ASSET_PAIR/);
});
test("Cross-market SQL must use completed, not future, CME H1 prices and admit missing SI",()=>{
 const d=dataset();
 const sql=require("./independent_event_research_query_s1").buildCrossAssetSql(d.ledger);
 assert.match(sql,/z\.known_end_utc<=b\.anchor_utc/);
 assert.match(sql,/z\.ts_event-z\.previous_start=interval '1h'/);
 assert.match(sql,/SI\.c\.0/);
 assert.match(sql,/EX-POST|hindsight-adjusted/i);
});
