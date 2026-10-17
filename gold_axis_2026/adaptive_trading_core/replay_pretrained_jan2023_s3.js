"use strict";
/**
 * GOLD-ADAPTIVE-MODEL-APP-01: PRETRAINED origin, not cold-start 2023.
 * Pretrain SAME S1+S2+S3 CORE chronologically through the last observation
 * strictly BEFORE 2023-01-01T00:00:00Z. Preserve ALL learned Q, S1 rules,
 * fast/slow phases, pending labels, M4 14/56d experts and state memory.
 * Start only the paper portfolio in CASH $100. Jan23 bars are never fed
 * to pretraining. No time-of-day trading prohibition.
 *
 * Source rows: PRIVATE_M15_2020_2023.json sorted {bar_start_utc,
 * source_id,bid_close,ask_close}. PRIVATE_SLOW_2020_2023.json sorted from
 * S2_SLOW_EV_DUKA_SESSION_AUDIT_2020_2025.sql. No files committed.
 * NOTE: Price provenance is retrospective reconstructed quote-only.
 */
const fs=require("node:fs"),crypto=require("node:crypto");
const core=require("./adaptive_market_core_s1_s2");
const CUTOFF="2023-01-01T00:00:00.000Z";
const MODES=["LEGACY_M15","MULTI_SESSION_RESEARCH","INTEGRATED_LONG_RESEARCH"];
const FEE=.008;
const copy=x=>JSON.parse(JSON.stringify(x));
function validRows(bars,slow){
 if(!Array.isArray(bars)||!bars.length||!Array.isArray(slow))
  throw Error("PRETRAIN_DATA_REQUIRED");
 const sourceId=bars[0].source_id;
 if(!sourceId||typeof sourceId!=="string")throw Error("PRETRAIN_SOURCE_REQUIRED");
 let prev=-Infinity;
 for(const r of bars){
  const t=Date.parse(r.bar_start_utc);
  if(!Number.isFinite(t)||t<=prev||r.source_id!==sourceId||
     !(Number(r.bid_close)>0)||!(Number(r.ask_close)>=Number(r.bid_close)))
   throw Error("PRETRAIN_M15_INVALID_OR_SPLICED");
  prev=t;
 }
 prev=-Infinity;
 for(const x of slow){
  const t=Date.parse(x.session+"T22:00:00Z");
  if(!Number.isFinite(t)||t<=prev||x.source_id!==sourceId)
   throw Error("PRETRAIN_SLOW_INVALID_OR_SPLICED");
  prev=t;
 }
 return sourceId;
}
function barPrice(r){return (Number(r.bid_close)+Number(r.ask_close))/2;}
function replay(bars,slow,{trainingCutoff=CUTOFF,modes=MODES}={}){
 if(trainingCutoff!==CUTOFF)throw Error("PRETRAIN_CUTOFF_FROZEN");
 const sourceId=validRows(bars,slow);
 const train=bars.filter(r=>Date.parse(r.bar_start_utc)+900000<Date.parse(trainingCutoff)),
  exam=bars.filter(r=>Date.parse(r.bar_start_utc)>=Date.parse(trainingCutoff));
 if(train.length<2||exam.length<2)throw Error("PRETRAIN_REQUIRED_BOTH_WINDOWS");
 const lastTrainDate=Date.parse(train.at(-1).bar_start_utc)+900000;
 if(lastTrainDate>=Date.parse(trainingCutoff))throw Error("PRETRAIN_OVERLAPPING_BOUNDARY");
 if(modes.length!==new Set(modes).size||
  modes.some(m=>!MODES.includes(m)))throw Error("PRETRAIN_MODE_INVALID");
 const states=Object.fromEntries(modes.map(mode=>[mode,
  core.create({sourceId,learningMode:"DISCOVERY_FULL_ARCHIVE",
     sourceEvidence:"RECONSTRUCTED_MARKET_ASOF",
     positionResearchMode:mode,shadowResearch:false})]));
 let slowIndex=0,first=null,last=null;
 const evalCounts=Object.fromEntries(modes.map(m=>[m,{}])),trades=[];
 const before={},monthly=[];
  let lastEvalMonth=null;
 let trained=0,evaluated=0;
 function processBar(r,isTraining){
  const t=Date.parse(r.bar_start_utc),end=t+900000,at=new Date(end).toISOString(),price=barPrice(r);
  while(slowIndex<slow.length&&Date.parse(slow[slowIndex].session+"T22:00:00Z")<end){
   const o=slow[slowIndex++],row={...o,n:Number(o.n),valid_quotes:Number(o.valid_quotes),
     max_gap_minutes:Number(o.max_gap_minutes),close_price:Number(o.close_price)};
   for(const state of Object.values(states))core.observeSlowSession(state,row);
  }
  if(!isTraining){
   const month=at.slice(0,7);
   if(lastEvalMonth!==null&&month!==lastEvalMonth){
    monthly.push({month:lastEvalMonth,...Object.fromEntries(modes.map(mode=>{
      const p=states[mode].s3.paper;return[mode,{wealth:p.cash+p.goldOunces*last.price*(1-FEE),
       buys:p.buyCount,sells:p.sellCount}];}))});
   }
   lastEvalMonth=month;first??={at,price};last={at,price};
  }
  const o={asof:at,barStartedAt:new Date(t).toISOString(),priceAvailableAt:at,
    price,priceSource:sourceId,barMinutes:15};
  for(const [mode,state] of Object.entries(states)){
    const was=state.s3.paper.holding,p=core.observe(state,o);
    if(!isTraining){
     const a=p.positionResearch.proposedResearchAction,
       reason=p.positionResearch.researchDecisionReason;
     evalCounts[mode][reason]=(evalCounts[mode][reason]||0)+1;
     if(was!==state.s3.paper.holding)trades.push({mode,at,
      side:state.s3.paper.holding==="GOLD"?"BUY":"SELL",price,
      decisionReason:reason});
    }
  }
  if(isTraining)trained++;else evaluated++;
 }
 for(const r of train)processBar(r,true);
 for(const [mode,state] of Object.entries(states)){
   // Copy trained model to prevent accidental reset of even pending labels.
   const trainedCp=core.checkpoint(state);
   const restored=core.restore(trainedCp);
   states[mode]=restored;
   const crit=restored.s3,p=crit.paper;
   before[mode]={s1Rules:restored.s1.rules.length,s1Anchors:restored.s1.audit?.anchors??null,
      qStates:Object.keys(crit.q).length,
      slowSessionsAccepted:restored.audit.slowAccepted,
      mature14:crit.longCycle.audit.mature14,
      mature56:crit.longCycle.audit.mature56,
      effective56:crit.longCycle.cohorts["ALL#56"]?.independentN??0,
      pendingLongLabels:crit.longCycle.pending.length,
      learned14Updates:crit.longCycle.gatedExperts[14].n,
      learned56Updates:crit.longCycle.gatedExperts[56].n,
      trainingLastBar:train.at(-1).bar_start_utc,
      trainingCutoff};
   // Starting January CASH $100 is not a model-reset: paper-only baseline.
   if(p.holding!=="CASH"||p.cash!==100||p.buyCount!==0||p.sellCount!==0)
     throw Error("PRETRAIN_PAPER_MUST_STAY_DISABLED_AND_EMPTY");
   p.enabled=true;
   p.firstPrice=null;p.buyHoldOunces=0;p.lastPrice=null;
   p.pendingOrder=null;p.equityPeak=100;p.maxDrawdownPct=0;
  }
 for(const r of exam)processBar(r,false);
 monthly.push({month:lastEvalMonth,...Object.fromEntries(modes.map(mode=>{
   const p=states[mode].s3.paper;return[mode,{wealth:p.cash+p.goldOunces*last.price*(1-FEE),
     buys:p.buyCount,sells:p.sellCount}];}))});
 const result=Object.fromEntries(modes.map(mode=>{
   const p=core.summary(states[mode]).positionResearch;
   return[mode,{startLearnedState:before[mode],endNetUSD:p.portfolio.liquidatableNetUsd,
     buyCount:states[mode].s3.paper.buyCount,
     sellCount:states[mode].s3.paper.sellCount,
     decisionReasons:evalCounts[mode],
     endPosition:states[mode].s3.paper.holding,
     finalMatured56:states[mode].s3.longCycle.audit.mature56}];
 }));
 return {project:"GOLD-ADAPTIVE-MODEL-APP-01",kind:"PRETRAINED_STRICT_CHRONOLOGY_RECONSTRUCTED_SOURCE",
   trainThrough:"2022-12-31",evaluation:"2023 January and any later supplied rows",
   sourceId,trainedBars:trained,examBars:evaluated,firstExam:first,lastExam:last,
   bankTradingHourRestriction:false,feePerLeg:FEE,
   firstprintPIT:false,scientificGate:"NOT_PROVEN",
   initialCashUSD:100,passiveGoldNetUSD:100*(1-FEE)**2*last.price/first.price,
   models:result,monthly,trades};
}
if(require.main===module){
 if(process.argv.length!==4)throw Error("Supply private M15 & slow JSON");
 const a=fs.readFileSync(process.argv[2],"utf8"),b=fs.readFileSync(process.argv[3],"utf8");
 console.log(JSON.stringify({trainingDataSHA256:crypto.createHash("sha256").update(a).digest("hex"),
  sessionDataSHA256:crypto.createHash("sha256").update(b).digest("hex"),
  ...replay(JSON.parse(a),JSON.parse(b))},null,2));
}
module.exports={CUTOFF,MODES,replay};
