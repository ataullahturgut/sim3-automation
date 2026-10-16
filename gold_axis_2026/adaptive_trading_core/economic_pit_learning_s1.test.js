"use strict";
const {test}=require("node:test"),assert=require("node:assert/strict");
const {atDecision,pairedReplay}=require("./economic_pit_learning_s1");
const core=require("./adaptive_rule_discovery_s1");
const t0="2023-01-06T13:30:00Z";
const iso=x=>new Date(x).toISOString();
const release={type:"NFP",scheduledUtc:t0,actual:223,consensus:200};
const scale={NFP:100,AHE:1,CPI:1,UNEMP:1};
const evidence={status:"CONTEMPORANEOUS_CAPTURE",origin:"INDEPENDENT_TIMESTAMPED_LOG",
  actual:{recordId:"a",contentHash:"aa",sourceUrl:"https://bls.gov/original",observedAt:"2023-01-06T13:30:01Z",loggedAt:"2023-01-06T13:30:10Z"},
  consensus:{recordId:"c",contentHash:"cc",sourceUrl:"https://archive.org/consensus",observedAt:"2023-01-06T13:25:00Z",loggedAt:"2023-01-06T13:25:10Z"},
  firstprint:{recordId:"f",contentHash:"ff",sourceUrl:"https://bls.gov/firstprint",observedAt:"2023-01-06T13:30:01Z",loggedAt:"2023-01-06T13:30:10Z"}};
const decision="2023-01-06T16:00:00Z";
test("Real 2023 official archive alone is not sufficient as-of surprise feature evidence",()=>{
 const e=atDecision(decision,[release],scale,"BLS_PIT");
 assert.equal(Object.keys(e.features).length,0);
 assert.equal(e.admitted.length,0);
 assert.match(e.quarantined[0].reason,/FIRST_ACCESS/);
});
test("A complete independently timestamped synthetic capture enters the existing S1 CORE",()=>{
 const e=atDecision(decision,[{...release,pit:evidence}],scale,"BLS_PIT");
 assert.equal(e.admitted.length,1);
 assert.equal(e.features.nfp_surprise_z.value,.23);
 const s=core.create({featureNames:["gold_1h","nq_1h","nfp_surprise_z"],horizons:[240],
 sourceRegistry:{TEST:{kind:"MARKET",evidenceStatus:"SYNTHETIC_ONLY"},
 BLS_PIT:{kind:"EVENT",evidenceStatus:"VERIFIED_PIT"}}});
 const m=x=>({value:x,kind:"MARKET",source:"TEST",observedAt:decision,availableAt:decision});
 const ob={asof:decision,barStartedAt:"2023-01-06T15:45:00Z",barMinutes:15,
 priceAvailableAt:decision,priceSource:"TEST",price:1870,
 features:{gold_1h:m(.1),nq_1h:m(.2),...e.features}};
 assert.equal(core.observe(s,ob).action,null);
 assert.equal(core.rules(s).length,1);
 assert.ok("nfp_surprise_z" in core.rules(s)[0].center);
});
test("Post-facto consensus, fabricated early actual, future captured evidence are quarantined",()=>{
 const a=atDecision(decision,[{...release,pit:{...evidence,consensus:{...evidence.consensus,observedAt:decision}}}],scale,"BLS_PIT");
 assert.equal(a.quarantined[0].reason,"CONSENSUS_NOT_PRIOR_TO_RELEASE");
 const b=atDecision(decision,[{...release,pit:{...evidence,actual:{...evidence.actual,observedAt:"2023-01-06T13:29:00Z"}}}],scale,"BLS_PIT");
 assert.equal(b.quarantined[0].reason,"ACTUAL_OR_FIRSTPRINT_PRE_RELEASE");
 const c=atDecision(decision,[{...release,pit:{...evidence,firstprint:{...evidence.firstprint,loggedAt:"2026-10-16T12:00:00Z"}}}],scale,"BLS_PIT");
 assert.equal(c.quarantined[0].reason,"PROVENANCE_RECORDED_AFTER_DECISION");
});
test("Several simultaneous macro components remain distinct features, never separate release claims",()=>{
 const r={...release,pit:evidence};
 const e=atDecision(decision,[r,{...r,type:"AHE",actual:.3,consensus:.4}],scale,"BLS_PIT");
 assert.deepEqual(Object.keys(e.features).sort(),["ahe_surprise_z","nfp_surprise_z"]);
 assert.throws(()=>atDecision(decision,[r,r],scale,"BLS_PIT"),/DUPLICATE/);
});
test("No certified event: prequential economic-vs-market ablation must be identical",()=>{
 const base=Date.parse("2023-01-06T12:00:00Z"),step=240*60000;
 const rows=[];for(let i=0;i<17;i++){
  const now=base+i*step,at=iso(now);
  const m=v=>({kind:"MARKET",value:v,observedAt:at,availableAt:at,source:"MARKET_TEST"});
  rows.push({asof:at,price:1800+7*i+(i%2===0?3:0),priceAvailableAt:at,
    priceSource:"MARKET_TEST",barStartedAt:iso(now-15*60000),barMinutes:15,
    features:{gold_1h:m(.03*(i%3)),nq_1h:m(-.03*(i%2))}});
 }
 const a=pairedReplay({marketRows:rows,releases:[release],scales:scale,
 featureNames:["gold_1h","nq_1h","nfp_surprise_z"],eventSource:"BLS_PIT",
 sourceRegistry:{MARKET_TEST:{kind:"MARKET",evidenceStatus:"SYNTHETIC_ONLY"},
 BLS_PIT:{kind:"EVENT",evidenceStatus:"VERIFIED_PIT"}}});
 assert.equal(a.status,"NO_CERTIFIED_EVENT_EVIDENCE");
 assert.equal(a.admitted,0);
 assert.equal(a.compared>0,true);
 assert.equal(a.withBrier,a.withoutBrier);
 assert.deepEqual(a.learnedWith,a.learnedWithout);
});
