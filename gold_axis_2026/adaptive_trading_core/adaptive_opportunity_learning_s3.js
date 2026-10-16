"use strict";
/**
 * GOLD-ADAPTIVE-MODEL-APP-01 / M4-M5: learned holding-opportunity evidence.
 * SAME S3, not a separate trading strategy. Research-only.
 * Start/reentry candidates are observed at completed M15 bars. Subsequent
 * valid completed DAILY sessions mature fee-net 5/10/20-session outcomes.
 * No event dates, hindsight extrema, future bars, fixed trading hours or
 * "6 January" entry rule are features. Overlapping labels are downweighted
 * by independent-origin effective sample moments. Economic source claims
 * cannot be manufactured from an S1 price-only forecast.
 */
const VERSION="KAVIS_S3_OPPORTUNITY_MEMORY_V1_20261016";
const HORIZONS=[5,10,20],FEE=.008,DAY=86400000;
const clone=x=>JSON.parse(JSON.stringify(x));
const finite=x=>typeof x==="number"&&Number.isFinite(x);
const stamp=x=>{const t=Date.parse(x);if(!Number.isFinite(t)||typeof x!=="string"||!/(Z|[+-]\d\d:\d\d)$/i.test(x))throw Error("OP_TIME_OFFSET_REQUIRED");return t;};
const direction=d=>d===1?"UP":d===-1?"DOWN":"NONE";
const phase=p=>["START","CONTINUE","REENTRY"].includes(p)?"TREND":p==="PULLBACK"?"PULLBACK":p==="END"?"END":p==="NEUTRAL"?"NEUTRAL":"UNKNOWN";
const fastKey=f=>"FAST:"+phase(f.phase)+":"+direction(f.direction);
const slowKey=l=>l&&l.phase&&!(["WARMUP","GAP","REJECTED_SESSION"].includes(l.phase))?
  "SLOW:"+phase(l.phase)+":"+direction(l.direction):null;
function create(){return {version:VERSION,clock:null,lastAnchorAt:null,
  lastSession:null,lastSource:null,sessionIndex:-1,pending:[],cohorts:{},
  audit:{bars:0,candidates:0,accepted:0,matured:0,censored:0,brokenSessions:0,
    sameSessionSkipped:0,missingEconomicContext:0}};}
function keys(fast,slow){const f=fastKey(fast),s=slowKey(slow);return ["GLOBAL",f,...(s?[f+"|"+s]:[])];}
function observeCandidate(s,o){
 if(s.version!==VERSION)throw Error("OP_VERSION");
 const t=stamp(o.at);
 if(s.clock!==null&&t<=s.clock)throw Error("OP_NONMONOTONIC_BAR");
 if(!finite(o.price)||o.price<=0||!o.sourceId||!o.fast)throw Error("OP_INVALID_BAR");
 s.clock=t;s.audit.bars++;
 const f=o.fast,eligible=(f.phase==="START"||f.phase==="REENTRY")&&[-1,1].includes(f.direction);
 if(!eligible)return {candidate:false,reason:"NOT_A_NEW_EPISODE_PHASE",forecast:null};
 s.audit.candidates++;
 const observedKeys=keys(f,o.slow);
 const prediction=forecastForKeys(s,observedKeys);
 if(s.lastAnchorAt!==null&&t-s.lastAnchorAt<240*60000)
  return {candidate:false,reason:"FOUR_HOUR_INDEPENDENCE_ANCHOR",forecast:prediction};
 s.lastAnchorAt=t;
 const anchorDay=new Date(t+2*3600000).toISOString().slice(0,10);
 for(const h of HORIZONS)s.pending.push({at:o.at,anchorDay,price:o.price,
   sourceId:o.sourceId,h,keys:observedKeys.slice(),startIndex:null});
 s.audit.accepted++;
 if(!o.s1Evidence||o.s1Evidence.provenance==="MARKET_ONLY_UNVALIDATED")
  s.audit.missingEconomicContext++;
 return {candidate:true,reason:"M15_PHASE_CANDIDATE_PENDING_OUTCOME",
   keys:observedKeys,forecast:prediction,authority:"RESEARCH_ONLY_NO_BUY_SELL"};
}
function regular(prev,current){
 if(prev===null)return true;
 const a=new Date(prev+"T00:00:00Z"),b=new Date(current+"T00:00:00Z");
 const gap=(b-a)/DAY,d=a.getUTCDay();
 return (gap===1&&d>=1&&d<=4) ||
  (gap===3&&d===5&&b.getUTCDay()===1) ||
  (gap===4&&d===5&&b.getUTCDay()===2) ||
  (gap===2&&d>=1&&d<=3); // possible non-trading weekday: research only
}
function update(s,key,h,ret,originIdx,at){
 const id=key+"#"+h,c=s.cohorts[id]??(s.cohorts[id]={n:0,mean:0,m2:0,
   independentN:0,independentMean:0,independentM2:0,lastIndependentIndex:null,
   up:0,down:0,lastMaturedAt:null});
 c.n++;const d=ret-c.mean;c.mean+=d/c.n;c.m2+=d*(ret-c.mean);
 if(ret>0)c.up++;else c.down++;
 if(c.lastIndependentIndex===null||originIdx-c.lastIndependentIndex>=h){
  c.independentN++;
  const z=ret-c.independentMean;c.independentMean+=z/c.independentN;
  c.independentM2+=z*(ret-c.independentMean);
  c.lastIndependentIndex=originIdx;
 }
 c.lastMaturedAt=at;
}
function closeSession(s,o){
 if(s.version!==VERSION)throw Error("OP_VERSION");
 const t=stamp(o.availableAt),label=o.session;
 if(!/^\d{4}-\d{2}-\d{2}$/.test(label)||
    t>Date.parse(label+"T22:00:00Z")||!o.sourceId||!finite(o.price)||o.price<=0)
   throw Error("OP_INVALID_SESSION");
 if(s.lastSession!==null&&label<=s.lastSession)throw Error("OP_NONMONOTONIC_SESSION");
 const broken=!regular(s.lastSession,label) || (s.lastSource!==null&&s.lastSource!==o.sourceId);
 if(broken){s.audit.censored+=s.pending.length;s.pending=[];s.audit.brokenSessions++;}
 s.sessionIndex++;
 const keep=[];
 for(const p of s.pending){
  if(p.sourceId!==o.sourceId){s.audit.censored++;continue;}
  if(p.startIndex===null){
   if(label<=p.anchorDay){keep.push(p);s.audit.sameSessionSkipped++;continue;}
   p.startIndex=s.sessionIndex-1;
  }
  if(s.sessionIndex-p.startIndex<p.h){keep.push(p);continue;}
  const net=100*(Math.log(o.price/p.price)+2*Math.log(1-FEE));
  for(const key of p.keys)update(s,key,p.h,net,p.startIndex,label);
  s.audit.matured++;
 }
 s.pending=keep;s.lastSession=label;s.lastSource=o.sourceId;
 return {session:label,matured:s.audit.matured,pending:s.pending.length};
}
function estimate(s,key,h){
 const c=s.cohorts[key+"#"+h];if(!c)return {key,n:0,effectiveN:0,meanNetLogPct:null,stderrPct:null};
 const n=c.independentN;
 return {key,n:c.n,effectiveN:n,meanNetLogPct:n>=2?c.independentMean:null,
  stderrPct:n>=3?Math.sqrt(Math.max(0,c.independentM2/(n-1))/n):null,
  up:c.up,down:c.down,lastMaturedAt:c.lastMaturedAt};
}
function forecastForKeys(s,ks){
 const rows=HORIZONS.map(h=>{
  const estimates=ks.map(key=>estimate(s,key,h));
  const selected=estimates.slice().reverse().find(x=>x.effectiveN>=5&&x.stderrPct!==null)||null;
  const lower=selected?selected.meanNetLogPct-selected.stderrPct:null;
  return {horizonSessions:h,selected,global:estimates[0],
    supportReady:!!selected,conservativeLowerPct:lower,
    estimatedNetLogPct:selected?.meanNetLogPct??null};
 });
 const relevant=rows.filter(x=>x.supportReady&&x.conservativeLowerPct>0);
 return {byHorizon:rows,learnedResearchPreference:relevant.length?
    "GOLD_ENTRY_CANDIDATE":"NO_SUPPORTED_ENTRY_ADVANTAGE",
   evidenceHorizons:relevant.map(x=>x.horizonSessions),
   authority:"RESEARCH_ONLY_NOT_EXECUTION",inference:"OVERLAPPING_RESULTS_AND_RECONSTRUCTED_MID"};
}
function forecast(s,{fast,slow}){return forecastForKeys(s,keys(fast,slow));}
function knowledge(s){
 if(s.version!==VERSION)throw Error("OP_VERSION");
 return {version:VERSION,cohorts:clone(s.cohorts),
  declaredHindsight:"DISCOVERY_FULL_ARCHIVE_IN_SAMPLE_ONLY",trainedAt:s.lastSession};
}
function fromKnowledge(data){
 if(!data||data.version!==VERSION||!data.cohorts||
   data.declaredHindsight!=="DISCOVERY_FULL_ARCHIVE_IN_SAMPLE_ONLY")
   throw Error("OP_INVALID_ARCHIVE_KNOWLEDGE");
 const s=create();s.cohorts=clone(data.cohorts);
 return s;
}
function summary(s){return {version:VERSION,audit:clone(s.audit),
  cohortCount:Object.keys(s.cohorts).length,
  pending:s.pending.length,observedThrough:s.lastSession,
  learned:clone(s.cohorts),liveTradeAuthorized:false};}
function restore(x){const s=clone(x);if(s.version!==VERSION||!Array.isArray(s.pending)||!s.cohorts||!s.audit)
 throw Error("OP_BAD_CHECKPOINT");return s;}
module.exports={VERSION,HORIZONS,create,observeCandidate,closeSession,forecast,knowledge,
 fromKnowledge,summary,restore};
