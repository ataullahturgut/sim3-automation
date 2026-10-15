"use strict";
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const {parseCSV,replayV6} = require("./adaptive_v7.js");
const DATA = path.join(__dirname,"..","..","adaptive_volatility_learning","portfolio_protection","verified_3h_asof_features_2025_2026_v0.csv");
const rows = parseCSV(fs.readFileSync(DATA,"utf8"));
const close = (a,b,eps=1e-7) => assert.ok(Math.abs(a-b)<eps, String(a)+" vs "+String(b));

test("source contains 3511 chronological checkpoint rows", () => {
 assert.equal(rows.length,3511);
 assert.equal(rows[0].tt,"2025-01-07T00:00:00.000Z");
 assert.equal(rows.at(-1).tt,"2026-09-30T21:00:00.000Z");
});
test("Feb-Sep V6 result is reproducible with fee", () => {
 const r=replayV6(rows);
 close(r.final_usd,123.52954535978293);
 close(r.hold_gold_usd,108.44434219692778);
 assert.equal(r.trades.length,4);
 assert.deepEqual(r.trades.map(x=>x.action),["BUY","SELL","BUY","SELL"]);
 assert.equal(r.training_counts.verifiedEconomicCheckpoints,0);
 assert.equal(r.configuration.fee_each_leg,.008);
 assert.equal(r.configuration.initial,119.753917);
});
test("learning freeze and stress ablation change returns", () => {
 const online=replayV6(rows);
 const freeze=replayV6(rows,{freeze_learning_at:"2026-01-01T00:00:00Z"});
 const noStress=replayV6(rows,{disable_stress:true});
 const onlyPrice=replayV6(rows,{price_only:true});
 close(freeze.final_usd,105.18177145259395);
 close(noStress.final_usd,108.44434219692778);
 close(onlyPrice.final_usd,online.final_usd);
 assert.ok(online.final_usd>freeze.final_usd);
 assert.ok(online.final_usd>noStress.final_usd);
});
test("2025 underperforms passive gold", () => {
 const x=replayV6(rows,{start:"2025-01-07T06:00:00Z",stop:"2025-12-31T12:00:00Z",initial_usd:100});
 close(x.final_usd,104.27573426448016);
 assert.ok(x.final_usd<x.hold_gold_usd);
});
test("future price changes cannot affect earlier decision log", () => {
 const stop="2026-06-30T12:00:00Z";
 const a=replayV6(rows,{stop,include_decisions:true});
 const future=rows.map(r=>r.tt>stop?{...r,p:(r.p||1)*1.8,c:(r.c||1)*1.8}:r);
 const b=replayV6(future,{stop,include_decisions:true});
 assert.deepEqual(a.decisionLog,b.decisionLog);
 close(a.final_usd,b.final_usd);
});
test("unverified, future and impossible-clock macro cases ignored", () => {
 const baseline=replayV6(rows);
 const fake=[
  {event_id:"AFTER_END",org:"ORG01",status:"VERIFIED",firstprint_utc:"2027-01-01T12:00:00Z",available_at_utc:"2027-01-01T12:01:00Z",source_url:"https://example.org/a"},
  {event_id:"UNVERIFIED",org:"ORG01",status:"UNVERIFIED",firstprint_utc:"2025-01-01T12:00:00Z",available_at_utc:"2025-01-01T12:01:00Z",source_url:"https://example.org/b"},
  {event_id:"BAD_CLOCK",org:"ORG02",status:"VERIFIED",firstprint_utc:"2025-01-01T12:00:00Z",available_at_utc:"2024-12-31T12:00:00Z",source_url:"https://example.org/c"}
 ];
 const candidate=replayV6(rows,{events:fake});
 close(candidate.final_usd,baseline.final_usd);
 assert.equal(candidate.training_counts.verifiedEconomicCheckpoints,0);
});
test("duplicate time series timestamps must fail", () => {
 assert.throws(()=>replayV6([rows[0],rows[0]]),/Duplicate checkpoint/);
});
