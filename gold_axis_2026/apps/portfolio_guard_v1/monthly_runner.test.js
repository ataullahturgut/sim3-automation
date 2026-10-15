"use strict";
const test=require("node:test"),assert=require("node:assert/strict");
const jan=require("./engine");
const feb=require("./monthly_runner");
test("February price panel is pinned, complete and strictly February-only",()=>{
 const data=feb.loadFebruary();
 assert.equal(data.checksumVerified,true);
 assert.equal(data.rows.length,1723);
 assert.equal(data.rows[0].tt,"2026-02-02T03:45:00.000Z");
 assert.equal(data.rows.at(-1).tt,"2026-02-27T21:30:00.000Z");
 assert.ok(data.rows.every(x=>x.time>=Date.parse("2026-01-31T21:00:00Z")&&x.time<Date.parse("2026-02-28T21:00:00Z")));
});
test("Feb 2026 starts with Jan terminal CASH and no hypothetical January re-entry",()=>{
 const r=feb.runFebruary(),p=r.scenarios.price15m,janRef=jan.runAll().scenarios.event15m;
 assert.equal(janRef.terminalAsset,"CASH");
 assert.ok(Math.abs(p.startUSD-janRef.finalUSD)<1e-9);
 assert.equal(p.fullCalendarSlots,2688);
 assert.equal(p.completePriceBars,1723);
 assert.equal(p.days.length,28);
 assert.equal(p.days[0].date,"2026-02-01");
 assert.equal(p.days.at(-1).date,"2026-02-28");
 assert.equal(p.days[0].completeBars,0);
 assert.equal(p.terminalAsset,"GOLD");
 assert.ok(Math.abs(p.finalUSD-114.27446809487914)<1e-5);
});
test("February price-only actions are deterministic and retain final GOLD position",()=>{
 const a=feb.runFebruary(),b=feb.runFebruary();
 assert.deepEqual(a,b);
 const p=a.scenarios.price15m;
 assert.equal(p.actions.length,7);
 assert.equal(p.actions[0].utc,"2026-02-09T14:45:00.000Z");
 assert.equal(p.actions[0].action,"BUY_GOLD");
 assert.equal(p.actions[1].utc,"2026-02-12T16:15:00.000Z");
 assert.equal(p.actions[1].action,"SELL_TO_CASH");
 assert.equal(p.actions.at(-1).utc,"2026-02-25T14:15:00.000Z");
 assert.equal(p.actions.at(-1).action,"BUY_GOLD");
 assert.equal(p.hypotheticalExitFeeDeducted,true);
 assert.ok(p.markToMarketBeforeHypotheticalSale>p.finalUSD);
});
test("February economic overlay is research-only and never uses future February outcomes",()=>{
 const r=feb.runFebruary();
 assert.equal(r.feedbackModelChangeSinceJanuary,false);
 assert.equal(r.independentOutOfSample,false);
 assert.equal(r.economicCausalityProven,false);
 assert.equal(r.bankSpreadIncluded,false);
 assert.equal(r.comparison.length,3);
 assert.ok(r.scenarios.event15m.actions.length>=1);
 for(const m of Object.values(r.scenarios)){
  assert.equal(m.startUSD,r.scenarios.price15m.startUSD);
  assert.ok(m.actions.every(x=>x.utc.startsWith("2026-02")));
 }
});
