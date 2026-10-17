"use strict";
/**
 * GOLD-ADAPTIVE-MODEL-APP-01. One actual CORE, two identical research-only
 * portfolios, 2020-22 learning then $100 CASH on 2023 origin, 2023-25 evaluation.
 * No same-source splice, no raw data persistence, no user bank time rule.
 * Macroeconomic archive is POST_RELEASE_ONLY / not certified firstprint-PIT;
 * assumed release+60 minutes availability is research convention, not fact.
 */
const fs=require("node:fs"),crypto=require("node:crypto");
const {csv}=require("./economic_evidence_s1");
const core=require("./adaptive_market_core_s1_s2");
const FEE=.008, SOURCE_EVENT="MACRO_ARCHIVE_POST_RELEASE_PAIR_UNVERIFIED";
const SCALE={NFP:100,AHE:1,UNEMP:1,CPI:1},RESEARCH_PRETRAIN_CUTOFF=Date.parse("2023-01-01T00:00:00Z");
const iso=t=>new Date(t).toISOString(),num=x=>Number.isFinite(x);
function releasesFromLedger(text){
 const rows=csv(text),m=new Map(),seen=new Set();
 for(const r of rows){
  if(!Object.hasOwn(SCALE,r.event_type)||r.pair_complete!=="True"||
     r.pit_use!=="POST_RELEASE_ONLY"||!r.actual_lineage_id||
     !r.consensus_lineage_id||!num(Number(r.surprise)))continue;
  const ts=Date.parse(r.event_ts_utc);
  if(!num(ts)||ts<RESEARCH_PRETRAIN_CUTOFF||ts>=Date.parse("2026-01-01Z"))continue;
  const id=iso(ts),k=id+"/"+r.event_type;
  if(seen.has(k))throw Error("DUPLICATE_LEDGER_COMPONENT");seen.add(k);
  const x=m.get(id)||{id,ts,features:{}};
  const typ=r.event_type,n=typ==="UNEMP"?"unemployment":typ.toLowerCase();
  x.features[n+"_surprise_z"]={
   value:Math.max(-5,Math.min(5,Number(r.surprise)/SCALE[typ])),
   source:SOURCE_EVENT,kind:"EVENT",observedAt:id,availableAt:iso(ts+3600000),
   firstprintVerified:false,researchOnly:true,assumedAccessDelayMinutes:60,
   researchReleaseConfidence:"RETROSPECTIVE_LEDGER_POST_EVENT_PAIR_UNVERIFIED",
   researchReleaseGrade:"POST_RELEASE_ONLY_NOT_PIT",
   actualLineageId:r.actual_lineage_id,consensusLineageId:r.consensus_lineage_id
  };
  m.set(id,x);
 }
 return [...m.values()].filter(x=>{
  const ns=Object.keys(x.features),emp=ns.filter(n=>n!=="cpi_surprise_z");
  return ns.includes("cpi_surprise_z")&&emp.length===0 ||
   !ns.includes("cpi_surprise_z")&&emp.length===3&&
   ["nfp_surprise_z","ahe_surprise_z","unemployment_surprise_z"].every(n=>ns.includes(n));
 }).sort((a,b)=>a.ts-b.ts);
}
function portfolioValue(s,price){const p=s.s3.paper;return p.cash+p.goldOunces*price*(1-FEE);}
function activateEvaluation(s){
 const p=s.s3.paper;
 if(p.buyCount||p.sellCount||p.holding!=="CASH"||p.cash!==100)
  throw Error("PRETRAINING_MUST_NOT_CREATE_SHADOW_TRADES");
 Object.assign(p,{enabled:true,valid:true,invalidReason:null,cash:100,goldOunces:0,
  holding:"CASH",pendingOrder:null,firstPrice:null,lastPrice:null,buyHoldOunces:0,
  equityPeak:100,maxDrawdownPct:0,buyCount:0,sellCount:0,fees:0});
 s.s3.audit.shadowTrades=0;
}
function run(bars,sessions,ledgerText){
 if(!Array.isArray(bars)||bars.length<10000||!Array.isArray(sessions)||!ledgerText)
  throw Error("REAL_ARCHIVE_REQUIRED");
 const sourceId=bars[0].source_id;
 const ev=releasesFromLedger(ledgerText);
 const registry={[SOURCE_EVENT]:{kind:"EVENT",evidenceStatus:"RECONSTRUCTED_RELEASE_RESEARCH"}};
 const ms=["ECONOMIC_ON","MARKET_ONLY"];
 const models=Object.fromEntries(ms.map(mode=>[mode,core.create({sourceId,
  sourceEvidence:"RECONSTRUCTED_MARKET_ASOF",learningMode:"DISCOVERY_FULL_ARCHIVE",
  positionResearchMode:"CONDITIONAL_ECONOMIC_RESEARCH",shadowResearch:false,
  economicSources:registry})]));
 const tradeEntries=Object.fromEntries(ms.map(z=>[z,[]]));
 const evaluatedByYear={},eventWaves=new Set();
 let prev=-Infinity,si=0,ei=0,evalMode=false,trainBars=0,testBars=0;
 let evalFirst=null,evalLast=null,currentYear=null,prevClose=null;
 let pretrain={};
 function snap(year,p){const result={year,lastDate:evalLast?.at||null,
    passiveBuyHoldNetUsd:evalFirst&&evalLast?
     100*(1-FEE)**2*evalLast.price/evalFirst.price:null,
    cashBaselineUsd:100};
  for(const mode of ms){
   result[mode]={endNetUsd:portfolioValue(models[mode],p),
    holding:models[mode].s3.paper.holding,
    trades:models[mode].s3.paper.buyCount+models[mode].s3.paper.sellCount,
    economicAnchors:models[mode].s3.conditional.audit.economicAnchors,
    maturedLabels:models[mode].s3.conditional.audit.labelsMatured,
    activeCoho:models[mode].s3.conditional.summary?null:Object.keys(models[mode].s3.conditional.cohorts).length};
  }
  evaluatedByYear[year]=result;
 }
 for(const r of bars){
  const t=Date.parse(r.bar_start_utc),end=t+900000,p=(Number(r.bid_close)+Number(r.ask_close))/2;
  if(!num(t)||t<=prev||r.source_id!==sourceId||
     !(Number(r.bid_close)>0)||!(Number(r.ask_close)>=Number(r.bid_close)))
   throw Error("INVALID_OR_SPLICED_SAME_SOURCE");
  prev=t;
  const pre=t<RESEARCH_PRETRAIN_CUTOFF;
  if(!pre&&!evalMode){
   for(const mode of ms){
    const s=models[mode];
    pretrain[mode]={s1Rules:s.s1.rules.length,
     s1Labels:s.s1.audit.labelsMatured,
     learnedConditionalCohorts:Object.keys(s.s3.conditional.cohorts).length,
     learnedConditionalLabels:s.s3.conditional.audit.labelsMatured,
     learnedQStates:Object.keys(s.s3.q).length};
    activateEvaluation(s);
   }
   evalMode=true;
  }
  const at=iso(end);
  while(si<sessions.length&&Date.parse(sessions[si].session+"T22:00:00Z")<end){
   const ss=sessions[si++];
   if(ss.source_id!==sourceId)throw Error("MIXED_SLOW_SOURCE");
   for(const model of Object.values(models))core.observeSlowSession(model,ss);
  }
  const year=at.slice(0,4);
  if(!pre){
   if(currentYear!==null&&year!==currentYear)snap(currentYear,prevClose);
   currentYear=year;
   if(!evalFirst)evalFirst={at,price:p};
   evalLast={at,price:p};prevClose=p;testBars++;
  }else trainBars++;
  // Allow macro surprise only after assumed research 60min access and before 4h expiration.
  // Every 15m evaluation point uses information already hypothetically available by then.
  while(ei<ev.length&&ev[ei].ts+4*3600000<=end)ei++;
  const current=ev[ei];
  const active=current&&end>=current.ts+3600000&&end<current.ts+4*3600000?current:null;
  if(active&&!pre)eventWaves.add(active.id);
  for(const mode of ms){
   const s=models[mode],holding=s.s3.paper.holding;
   const ob={asof:at,barStartedAt:iso(t),priceAvailableAt:at,
    barMinutes:15,price:p,priceSource:sourceId};
   if(mode==="ECONOMIC_ON"&&active)ob.economicFeatures=active.features;
   core.observe(s,ob);
   if(!pre&&s.s3.paper.holding!==holding)
     tradeEntries[mode].push({at,side:s.s3.paper.holding==="GOLD"?"BUY":"SELL",
      reason:s.s3.lastProposedResearchAction||"PROPOSED_RESEARCH",economicContextPresent:mode==="ECONOMIC_ON"&&!!active});
  }
 }
 if(!evalMode)throw Error("NO_EVALUATION_PERIOD");
 snap(currentYear,evalLast.price);
 const final=Object.fromEntries(ms.map(mode=>{
  const state=models[mode],v=core.summary(state).positionResearch,p=v.portfolio;
  return [mode,{endNetUsd:p.liquidatableNetUsd,holding:p.cashHolding,
    buyCount:state.s3.paper.buyCount,sellCount:state.s3.paper.sellCount,
    maxDrawdownPct:p.maxDrawdownPct,conditionalAudit:v.conditionalPositionMemory.audit,
    decisions:v.audit.decisionsByReason,
    tradeExamples:tradeEntries[mode].slice(0,35),totalTradeLog:tradeEntries[mode].length}];
 }));
 return {project:"GOLD-ADAPTIVE-MODEL-APP-01",
  evaluation:"2023–2025",pretrain:"2020–2022",sourceId,
  origin:evalFirst.at,finalTime:evalLast.at,trainBars,testBars,
  macroWavesFromRetrospectiveLedger:ev.length,macroWavesEncountered:eventWaves.size,
  economicDataProvenance:"RECONSTRUCTED_POST_RELEASE_ONLY_NOT_VERIFIED_PIT",
  assumedEconomicAvailabilityMinutes:60,priceProvenance:"EV_DUKA_RECONSTRUCTED_VENDOR_BIDASK",
  executionPrice:"MID_PROXY_ONLY_NOT_BANK_BIDASK",feePerLeg:FEE,
  tradeAllowed:false,scientificGate:"NOT_PROVEN",blindOOS:false,
  passiveGoldNet2023to2025USD:100*(1-FEE)**2*evalLast.price/evalFirst.price,
  pretrain,yearlySnapshots:evaluatedByYear,models:final,
  incrementalEconomicEndWealthUsd:final.ECONOMIC_ON.endNetUsd-final.MARKET_ONLY.endNetUsd};
}
if(require.main===module){
 const [p1,p2,p3]=process.argv.slice(2);
 if(!p1||!p2||!p3)throw Error("PRIVATE_M15 PRIVATE_SLOW LEDGER_CSV required");
 const a=fs.readFileSync(p1,"utf8"),b=fs.readFileSync(p2,"utf8"),
  c=fs.readFileSync(p3,"utf8");
 const result=run(JSON.parse(a),JSON.parse(b),c);
 console.log(JSON.stringify({inputHashes:[a,b,c].map(x=>crypto.createHash("sha256").update(x).digest("hex").slice(0,16)),
  ...result},null,2));
}
module.exports={run,releasesFromLedger};
