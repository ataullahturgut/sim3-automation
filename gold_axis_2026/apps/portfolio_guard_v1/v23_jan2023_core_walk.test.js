"use strict";
const test=require("node:test"),A=require("node:assert/strict");
const R=require("./v23_jan2023_core_walk"),C=require("./kavis_core_timeless_v0");
const START=Date.parse("2023-01-03T03:30:00Z"),STEP=900000;
function prices(n){
 return Array.from({length:n},(_,i)=>({t:START+i*STEP,asof:new Date(START+i*STEP).toISOString(),
  close:1840*(1+.00001*i),open:1840*(1+.00001*i)}));
}
test("Jan-only source adapter rejects future Feb prices",()=>{
 const src="tt,close,p\n2023-01-03T03:30:00.000Z,1840,1840\n2023-02-01T00:00:00.000Z,1841,1841";
 A.throws(()=>R.readPrices(src),/JAN_2023_ONLY/);
});
test("Only fully released, paired verified Jan macros enter news pool",()=>{
 const h="event_type,event_ts_utc,actual,consensus,surprise,actual_available_as_of_utc,consensus_available_as_of_utc,surprise_ready_at_utc,pair_complete,actual_lineage_id,consensus_lineage_id,pit_use";
 const good="CPI,2023-01-12 13:30:00+00:00,0.1,0.2,-0.1,2023-01-12 13:30:00+00:00,2023-01-12 13:30:00+00:00,2023-01-12 13:30:00+00:00,True,official,consensus,POST_RELEASE_ONLY";
 const bad="FOMC,2023-01-13 19:00:00+00:00,,,,,,,False,id,,EVENT_TIMESTAMP_ONLY";
 const feb=good.replaceAll("2023-01","2023-02");
 const r=R.readReleases(h+"\n"+bad+"\n"+good+"\n"+feb);
 A.equal(r.length,1);
 A.equal(r[0].type,"CPI");
 A.equal(r[0].mechanismFamily,"G01_RATES_USD");
 A.ok(r[0].z<0);
});
test("Source lagged price inputs and intentional unavailable other asset masks",()=>{
 const a=prices(110);
 const m=R.market(a,109);
 A.ok(m.goldR4hPct.value>0);
 A.ok(m.goldDrawdownPct.value===0);
 A.equal(m.nasdaqR4hPct,undefined);
 const encoded=C.encode({asof:a[109].asof,price:a[109].close,priceAvailableAt:a[109].asof,market:m,events:[]});
 A.ok(encoded.quality.missing>0);
});
test("Causal historical episode summaries are AFTER completed four-hour prices",()=>{
 const a=prices(130);
 const m=R.impactfulMovements(a);
 A.ok(m.length>0);
 A.ok(m.every(z=>z.selection==="EXPOST_DESCRIPTION_NOT_CORE_SIGNAL"));
});
test("No future events pretrigger in chronological January runner",()=>{
 const a=prices(850);
 const r=R.run(a,[{type:"CPI",published:START+500*STEP,z:-1,
  mechanismFamily:"G01_RATES_USD",proof:{actual:"official",consensus:"consensus"}}]);
 A.equal(r.scope,"2023-01_ONLY");
 A.equal(r.releaseRecords,1);
 A.ok(r.maturedEconomicOutcomeLabels>0);
 A.ok(r.acceptedBankChecks>0);
 A.equal(r.costPctPerLeg,.8);
 A.ok(r.headStats.length===4);
 A.ok(r.barsWithPublishedNewsActive<r.bars);
});
