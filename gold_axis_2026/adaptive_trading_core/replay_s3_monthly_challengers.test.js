"use strict";
const {test}=require("node:test"),assert=require("node:assert/strict");
const {run,MODES}=require("./replay_s3_monthly_challengers");
const src="TEST_SOURCE";
function sample(n,base=0){
 const ts=Date.parse("2023-01-03T10:00:00Z");
 return Array.from({length:n},(_,i)=>({
  bar_start_utc:new Date(ts+i*900000).toISOString(),source_id:src,
  bid_close:1800+base+i*.15,ask_close:1800+base+i*.15+.04}));
}
test("M1-to-M5 3-mode replay keeps source, fee, initial cash and full chronology",()=>{
 const out=run(sample(48),[]);
 assert.deepEqual(Object.keys(out.models),MODES);
 assert.equal(out.bars,48);
 assert.equal(out.feePerLeg,.008);
 assert.equal(out.priceProvenance,"RECONSTRUCTED_MID_NOT_BANK_QUOTE");
 assert.equal(out.tradeAllowed,false);
 assert.equal(out.scientificApproval,false);
 assert.equal(out.monthly.length,1);
 for(const s of Object.values(out.models)){
  assert.equal(s.s1Predictions,48);
  assert.equal(s.shadowModeOnly,true);
 }
});
test("No oracle contamination: mutating later prices cannot rewrite earlier decisions",()=>{
 const a=sample(33),b=sample(70),c=sample(70);
 for(let i=33;i<c.length;i++){c[i].bid_close+=500;c[i].ask_close+=500;}
 const q=run(a,[]),r=run(b,[]),s=run(c,[]);
 assert.equal(q.models.LEGACY_M15.s1Predictions,33);
 assert.deepEqual(r.trades.filter(x=>x.at<="2023-01-03T18:15:00.000Z"),
   s.trades.filter(x=>x.at<="2023-01-03T18:15:00.000Z"));
});
test("Malformed and multi-source price streams abort instead of silently rejoining",()=>{
 const a=sample(3);
 assert.throws(()=>run([],[]),/ROWS_REQUIRED/);
 assert.throws(()=>run([a[1],a[0]],[]),/NONMONOTONIC/);
 assert.throws(()=>run([{...a[0],source_id:"X"},...a.slice(1)],[]),/PRICE_SOURCE/);
 assert.throws(()=>run([{...a[0],ask_close:0},...a.slice(1)],[]),/INVALID_PRICE/);
});
