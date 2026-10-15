"use strict";
/**
 * Month-end learning gate: immutable close report, no retrospective re-fit.
 *
 * 96h post-decision labels are delayed. A Jan 29 shock still has an immature
 * label on Jan 31, and MUST NOT be copied into Feb 1's training memory.
 * Events + human interpretations are research hypotheses, not auto-selected
 * predictive features or permission to place real orders.
 */
const crypto=require("node:crypto");
const engine=require("./engine");
const audit=require("./event_audit_v2");
const H96=96*3600000;
const JAN_CLOSE=Date.parse("2026-01-31T21:00:00Z");
function eligibility(utc,asOf=JAN_CLOSE){
 const t=Date.parse(utc);
 if(!Number.isFinite(t)||!Number.isFinite(asOf))throw new Error("INVALID_TIMELINE");
 const ready=t+H96;
 return {decisionUTC:utc,labelMaturesUTC:new Date(ready).toISOString(),
  maturedAtCutoff:ready<=asOf,status:ready<=asOf?"ELIGIBLE_TO_MEASURE_OUTCOME":"PENDING_FORWARD_LABEL"};
}
function createJanuaryLearningRecord(){
 const runs=engine.runAll(),j=runs.scenarios.event15m,v2=audit.runAudit();
 const count={matured:0,pending:0};
 const decisions=j.actions.map(t=>{
  const label=eligibility(t.utc);
  if(label.maturedAtCutoff)count.matured++;else count.pending++;
  return {utc:t.utc,action:t.action,price:t.price,
   ...label,requiresVerifiedOutcomeFromM15:true,
   economicCause:"UNVERIFIED",performanceAttribution:"PRICE_AND_TIME_SCOPE_ONLY"};
 });
 const nextMonth={
  month:"2026-02",startUTC:"2026-01-31T21:00:00.000Z",
  portfolioAsset:j.terminalAsset,cashUSD:j.terminalAsset==="CASH"?j.finalUSD:0,
  goldOunces:j.goldOunces,
  modelVersion:engine.VERSION,referencePeriod:"2026-01",autoRetrain:false,
  learningCandidateVersion:"V2_DIAGNOSTIC_ONLY",
  riskCalibrationReady:false,
  missingRequirements:v2.requiredBeforeTrading.slice()
 };
 const record={
  schema:"GOLD_GUARD_MONTH_END_LEARNING_GATE_V2",
  month:"2026-01",
  resultStatus:"HISTORICAL_RESEARCH_NOT_INDEPENDENT_VALIDATION",
  closureUTC:new Date(JAN_CLOSE).toISOString(),
  dataFingerprints:runs.inputs,
  frozenExecutionModel:engine.VERSION,
  initialCashUSD:100,finalCashUSD:j.finalUSD,
  firstprintVerifiedEvents:0,causalEventsVerified:0,
  feedback:decisions,feedbackReadiness:count,
  observations:[
   "The raw 92 case aliases contain duplicate time/parent instances; de-duplicate before analog scoring.",
   "Historical case frequency is not a probability. Fixed-clock background controls need separate measurement.",
   "Known Jan29 V1 sale was independently triggered by the frozen price model; causal event benefit remains zero.",
   "The Jan29 sell outcome over the next 96h is NOT known as of Jan31 month end.",
   "Uptrend participation and bank transaction spread remain unvalidated for subsequent months."
  ],
  nextMonth,
  prohibits:["IN_MONTH_RETROSPECTIVE_RETRAIN","AUTOMATIC_MODEL_PARAMETER_TUNING",
   "USING_PENDING_FUTURE_LABELS","CLAIMING_CONFIRMED_CAUSALITY","LIVE_BANK_TRADING"]
 };
 // Stable reproducibility token from byte-identical canonical JSON.
 record.sha256=crypto.createHash("sha256").update(JSON.stringify(record)).digest("hex");
 return record;
}
module.exports={eligibility,createJanuaryLearningRecord};
