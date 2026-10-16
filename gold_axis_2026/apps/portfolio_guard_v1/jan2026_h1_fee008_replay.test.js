"use strict";
const test=require("node:test"),assert=require("node:assert/strict");
const F=require("./jan2026_h1_fee008_replay");
test("No missing source vintage or malformed private BID/ASK is accepted",()=>{
 assert.throws(()=>F.csv("utc,bid_open,bid_close,ask_open,ask_close,source_vintage\n2026-01-01T00:00:00Z,10,10,9,9,RETRIEVED_2026_10_08_NOT_PIT"),/INVALID_SOURCE/);
});
test("Backtest requires H1 prior lookback, never silently synthetic fill",()=>{
 assert.throws(()=>F.run([]),/INSUFFICIENT/);
});
test("CSV must have strict H1 cadence and explicit late provenance",()=>{
 assert.throws(()=>F.csv("utc,bid_open,bid_close,ask_open,ask_close,source_vintage\n2026-01-01T00:00:00Z,10,10,11,11,PRETEND_PIT"),/INVALID_SOURCE/);
});
test("Real bank quote was NEVER claimed to be included",()=>{
 const r=require("fs").readFileSync(require("path").join(__dirname,"JAN_2026_H1_REAL_MARKET_COST008_METHOD_20261016.md"),"utf8");
 assert.match(r,/banka.*değil|banka.*kotasyon.*yok|gerçek.*bank/i);
});
