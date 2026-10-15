"use strict";
/**
 * V10 scientific chronological evidence audit, not a live order engine.
 * Price source pinned by V7/V8; all model decisions are retrospective.
 */
const {loadRows,DATA_BLOB_SHA}=require("./adaptive_v7_app");
const {replayV6:oldV7}=require("./adaptive_v7_engine");
const {replayV6:laggedV10}=require("./v10_lagged_v7_engine");
const {loadFullRows}=require("./v8_regret_engine");
const VERSION="V10_BANK_LAG_RECOVERY_GUARD_20261015";
const START_2026="2026-02-02T06:00:00Z";
const END_2026="2026-09-30T12:00:00Z";
const INITIAL_2026=119.753917;
const CONTRACT_2025={start:"2025-01-07T06:00:00Z",stop:"2025-12-31T12:00:00Z",initial_usd:100};
const CONTRACT_2026={start:START_2026,stop:END_2026,initial_usd:INITIAL_2026};
function crossCheckTrades(record){
 for(const q of record.trades){
  if(!(Date.parse(q.time)>Date.parse(q.signal_at)))throw Error("LOOKAHEAD_FILL_V10");
  const hh=new Date(q.time).getUTCHours();
  if(![6,9,12].includes(hh))throw Error("OUTSIDE_TRADING_WINDOW_V10");
 }
}
function monthlyValues(r){
 return Object.entries(r.per_month).map(([month,v])=>({month,netUSD:v.nav,position:v.position,
   lastCheckpoint:v.lastCheckpoint}));
}
let memo;
function audit(){
 if(memo)return memo;
 const rows=loadRows(),history=loadFullRows();
 const old=oldV7(rows,CONTRACT_2026);
 const lag=laggedV10(rows,CONTRACT_2026);
 const guarded=laggedV10(rows,{...CONTRACT_2026,reentry_protocol:"matured_recovery"});
 const previous2025=oldV7(rows,CONTRACT_2025);
 const lagged2025=laggedV10(rows,CONTRACT_2025);
 const guarded2025=laggedV10(rows,{...CONTRACT_2025,reentry_protocol:"matured_recovery"});
 const historic2024=laggedV10(history.rows,{start:"2024-01-02T06:00:00Z",
   stop:"2024-12-31T12:00:00Z",initial_usd:100,reentry_protocol:"matured_recovery"});
 const historic2025=laggedV10(history.rows,{...CONTRACT_2025,reentry_protocol:"matured_recovery"});
 const historic2026=laggedV10(history.rows,{...CONTRACT_2026,reentry_protocol:"matured_recovery"});
 const fees=[.008,.0095,.0105],delays=[1,2,3],grid=[];
 for(const fee of fees)for(const delay of delays){
   const q=laggedV10(rows,{...CONTRACT_2026,fee,
     execution_delay_bank_checkpoints:delay,
     reentry_protocol:"matured_recovery"});
   crossCheckTrades(q);
   grid.push({feePerSide:fee,executionBankCheckpoints:delay,
     finalUSD:q.final_usd,tradeCount:q.trades.length,
     buyBlocked:q.gateAudit.length});
 }
 for(const q of [lag,guarded,lagged2025,guarded2025,historic2024,historic2025,historic2026])
   crossCheckTrades(q);
 const close=(a,b)=>Number.isFinite(a)&&Math.abs(a-b)<.000025;
 if(!close(old.final_usd,123.52954535978293)||
    !close(lag.final_usd,116.50002607739015)||
    !close(guarded.final_usd,130.6663238249077)||
    !close(lagged2025.final_usd,101.4365705394282)||
    !close(guarded2025.final_usd,lagged2025.final_usd)||
    !close(historic2024.final_usd,108.61461132260524)||
    !close(historic2025.final_usd,110.6634961560752)||
    !close(historic2026.final_usd,guarded.final_usd))
   throw Error("V10_LOCKED_RESEARCH_CHECKSUM_MISMATCH");
 // The policy gate did not activate on 2024 or 2025, so its 2026 apparent
 // effect is not supported by any independent prior observed protection.
 const historicControls=[
   {period:"2024_2023HISTORY",initialUSD:100,finalUSD:historic2024.final_usd,
    passiveGoldUSD:historic2024.hold_gold_usd,gateBlocked:historic2024.gateAudit.length},
   {period:"2025_2023HISTORY",initialUSD:100,finalUSD:historic2025.final_usd,
    passiveGoldUSD:historic2025.hold_gold_usd,gateBlocked:historic2025.gateAudit.length},
   {period:"2026_2023HISTORY",initialUSD:INITIAL_2026,finalUSD:historic2026.final_usd,
    passiveGoldUSD:historic2026.hold_gold_usd,gateBlocked:historic2026.gateAudit.length}
 ];
 memo={
  version:VERSION,
  status:"SCIENTIFIC_SHADOW_CANDIDATE_NOT_VALIDATED",
  source:{verifiedRows:rows.length,sha:DATA_BLOB_SHA,
    extendedRows:history.rows.length,extended2025Overlap:history.data.overlapVerified},
  contracts:{feePerDirection:.008,bankHoursTR:[9,12,15],barSignalNotSameBarFill:true,
    nextBankCheckpointFill:true,realBankBidAskPresent:false,verifiedMacroFirstprints:0,
    2026AlreadyInspected:true,independentBlindValidation:false},
  model:{
    sameV7Predictors:true,onlyExecutionAndReentryPolicyAltered:true,
    saleToReentryMinimumHours:336,
    requireAsOfPositiveR1:true,requireAsOfPositiveR3:true,
    requireAsOfR4AboveMinusHalf:true,
    reentryGateOrigin:"hypothesis_informed_by_inspected_2026",
    lifecycle:["GOLD","STRESS_SELL","WAIT_336H","REGIME_RECONFIRM","REENTER_OR_CASH"],
    learnedFeedbackStillChronologicallyMatured:true
  },
  base2026:{initialUSD:INITIAL_2026,
    v7OriginalSameBarUSD:old.final_usd,
    v7DelayedBankUSD:lag.final_usd,
    v10BankRecoveryUSD:guarded.final_usd,
    cashUSD:INITIAL_2026,passiveGoldUSD:lag.hold_gold_usd,
    causalPolicyDifferenceUSD:guarded.final_usd-lag.final_usd,
    executionAssumptionDifferenceUSD:lag.final_usd-old.final_usd
  },
  negativeControl2025:{
    originalV7USD:previous2025.final_usd,
    delayedV7USD:lagged2025.final_usd,
    guardedV10USD:guarded2025.final_usd,
    passiveGoldUSD:guarded2025.hold_gold_usd,
    deniedBuys:guarded2025.gateAudit.length,
    warning:"The guard never blocked an entry in 2025, so no independent 2025 evidence supports it"
  },
  historicalControl:historicControls,
  transactions:{
    original:old.trades.map(x=>({at:x.time,side:x.action,reason:x.reason,mid:x.fill_proxy})),
    delayedBaseline:lag.trades.map(x=>({at:x.time,signalAt:x.signal_at,side:x.action,
      reason:x.reason,mid:x.fill_proxy,netUSD:x.nav})),
    guarded:guarded.trades.map(x=>({at:x.time,signalAt:x.signal_at,side:x.action,
      reason:x.reason,mid:x.fill_proxy,netUSD:x.nav}))
  },
  monthResults:{
    delayedBaseline:monthlyValues(lag),
    guarded:monthlyValues(guarded)
  },
  deniedBuys:{total:guarded.gateAudit.length,examples:guarded.gateAudit.slice(0,15)},
  costLatencySensitivity:grid,
  scientificGate:{
    automaticPromotion:false,liveTradingAuthorized:false,validationPassed:false,
    reason:"2026_KNOWN_AT_DESIGN__NO_INDEPENDENT_2024_2025_GATE_EFFECT__BANK_BID_ASK_MISSING",
    required:["Reentry protection demonstrated on multiple prior independent shock episodes",
      "Prospective/time-block holdout plus block bootstrap on non-overlapping episodes",
      "Same execution contract for all comparators and true bank BID/ASK + slippage",
      "Economic first publication time verification for event library",
      "Real-time persistable state and instrument-specific commission audit"]
  }
 };
 return memo;
}
module.exports={VERSION,CONTRACT_2025,CONTRACT_2026,audit,crossCheckTrades};
