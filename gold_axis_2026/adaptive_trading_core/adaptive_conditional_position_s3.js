"use strict";
/**
 * GOLD-ADAPTIVE-MODEL-APP-01 / existing M4/S3 research extension.
 * Learns conditional BUY-vs-CASH and SELL-vs-HOLD advantages from matured,
 * independent daily-session price outcomes. It does NOT infer macro causality,
 * certify historical first access, or authorize trades.
 */
const VERSION="KAVIS_S3_CONDITIONAL_POSITION_RESEARCH_V1_20261017";
const FEE=.008, HORIZONS=[5,10,20], DAY=86400000;
const finite=x=>typeof x==="number"&&Number.isFinite(x);
const clone=x=>JSON.parse(JSON.stringify(x));
function stamp(s){if(typeof s!=="string"||!/(?:Z|[+-]\d\d:\d\d)$/i.test(s)||!Number.isFinite(Date.parse(s)))throw Error("CP_TIMESTAMP_OFFSET_REQUIRED");return Date.parse(s);}
function phase(f){return ["START","CONTINUE","PULLBACK","END","REENTRY","NEUTRAL"].includes(f?.phase)?f.phase:"UNKNOWN";}
function sign(d){return d===1?"UP":d===-1?"DOWN":"NONE";}
function researchEvidence(e){return e&&["RESEARCH_MACRO_UNVERIFIED","VERIFIED_PIT_BUT_ALPHA_NOT_PROVEN"].includes(e.provenance);}
function marketKey(fast){return "MKT:"+phase(fast)+":"+sign(fast?.direction);}
function economicKey(market,e){
 if(!researchEvidence(e)||!e.economicState)return null;
 const v=e.economicState;
 if(!v||!["EMP","CPI"].includes(v.family)||!/[a-z]/i.test(v.dominant||"")||
    !/^(POS|NEG|ZERO)$/.test(v.sign)||!Number.isFinite(v.magnitude)||v.magnitude<0||v.magnitude>5)
   throw Error("CP_INVALID_ECONOMIC_STATE");
 return market+"|ECO:"+v.family+":"+v.dominant+":"+v.sign;
}
function create({minIndependent=8,anchorMinutes=240}={}){
 if(!Number.isInteger(minIndependent)||minIndependent<5||!Number.isInteger(anchorMinutes)||anchorMinutes<60)
   throw Error("CP_INVALID_CONFIG");
 return {version:VERSION,config:{minIndependent,anchorMinutes},clock:null,lastAnchor:null,
   lastSession:null,lastSource:null,sessionIndex:-1,pending:[],cohorts:{},
   audit:{bars:0,anchors:0,labelsMatured:0,censored:0,sourceBreaks:0,economicAnchors:0,
     economicEvidenceUnverified:0,decisionsResearchOnly:0}};
}
function cohort(s,key,h){const id=key+"#"+h;
 return s.cohorts[id]??(s.cohorts[id]={n:0,mean:0,m2:0,independentN:0,
 independentMean:0,independentM2:0,lastOriginIndex:null,lastMaturedAt:null});}
function add(s,key,h,v,origin,day){const c=cohort(s,key,h);
 c.n++;const d=v-c.mean;c.mean+=d/c.n;c.m2+=d*(v-c.mean);
 if(c.lastOriginIndex===null||origin-c.lastOriginIndex>=h){
  c.independentN++;const z=v-c.independentMean;c.independentMean+=z/c.independentN;
  c.independentM2+=z*(v-c.independentMean);c.lastOriginIndex=origin;
 }
 c.lastMaturedAt=day;
}
function get(s,key,h){if(!key)return null;
 const c=s.cohorts[key+"#"+h];if(!c)return null;
 const n=c.independentN;
 return {key,rawN:c.n,effectiveN:n,
  meanNetPct:n>=2?c.independentMean:null,
  stderrPct:n>=3?Math.sqrt(Math.max(0,c.independentM2/(n-1))/n):null,
  lastMaturedAt:c.lastMaturedAt};
}
function score(s,fast,e,holding){
 if(!["CASH","GOLD"].includes(holding))throw Error("CP_BAD_HOLDING");
 const m=marketKey(fast),ek=economicKey(m,e),side=holding==="CASH"?"BUY":"SELL";
 const candidates=HORIZONS.map(h=>{
  const base=get(s,m+"|"+side,h),conditional=get(s,ek?ek+"|"+side:null,h);
  const ready=x=>x&&x.effectiveN>=s.config.minIndependent&&x.stderrPct!==null;
  // Economic cohort nests inside the market cohort. Require a conservative
  // incremental edge proxy before crediting the event, not merely profit.
  // Covariance is unknown: this guardrail is NOT a calibrated confidence interval.
  const incrementalMargin=ready(conditional)&&ready(base)?
    conditional.meanNetPct-base.meanNetPct-
      1.96*Math.hypot(conditional.stderrPct,base.stderrPct):null;
  const selected=incrementalMargin!==null&&incrementalMargin>0?conditional:
    ready(base)?base:null;
  const bound=selected?selected.meanNetPct-1.96*selected.stderrPct:null;
  return {horizonSessions:h,market:base,economic:conditional,
    incrementalMarginPct:incrementalMargin,selected,source:selected?.key.includes("|ECO:")?"CONDITIONAL_ECONOMIC":
      selected?"MARKET_FALLBACK":"INSUFFICIENT_EVIDENCE",lowerBoundPct:bound};
 });
 // Multiple horizons are hypotheses, not independent votes. Never sum profits.
 const qualified=candidates.filter(x=>x.selected&&x.lowerBoundPct>0);
 qualified.sort((a,b)=>b.lowerBoundPct-a.lowerBoundPct);
 const best=qualified[0]||null;
 return {actionCandidate:best?side:"KEEP",best,byHorizon:candidates,
   eventPresent:!!ek,conditionKey:ek,marketKey:m,
   reason:best?(best.source==="CONDITIONAL_ECONOMIC"?"ECONOMIC_CONDITION_MATURED_NET_ADVANTAGE":"MARKET_MATURED_NET_ADVANTAGE"):
     ek?"NO_SUPPORTED_CONDITIONAL_NET_ADVANTAGE":"NO_SUPPORTED_MARKET_NET_ADVANTAGE",
   authority:"RESEARCH_ONLY_NOT_LIVE",bankBidAskCertified:false};
}
function observe(s,{at,price,sourceId,fast,s1Evidence,holding="CASH"}){
 if(s.version!==VERSION)throw Error("CP_VERSION");
 const t=stamp(at);if(s.clock!==null&&t<=s.clock)throw Error("CP_NONMONOTONIC");
 if(!finite(price)||price<=0||!sourceId||!fast)throw Error("CP_INVALID_PRICE_OBSERVATION");
 const ek=economicKey(marketKey(fast),s1Evidence);
 const forecast=score(s,fast,s1Evidence,holding); // BEFORE new labels/anchor
 s.clock=t;s.audit.bars++;s.audit.decisionsResearchOnly++;
 if(s.lastAnchor===null||t-s.lastAnchor>=s.config.anchorMinutes*60000){
  s.lastAnchor=t;s.audit.anchors++;
  const keys=[marketKey(fast),...(ek?[ek]:[])];
  const anchorDay=new Date(t+2*3600000).toISOString().slice(0,10);
  for(const h of HORIZONS)s.pending.push({at,anchorDay,sourceId,price,h,keys,startIndex:null});
  if(ek){s.audit.economicAnchors++;if(s1Evidence.provenance!=="VERIFIED_PIT_BUT_ALPHA_NOT_PROVEN")
   s.audit.economicEvidenceUnverified++;}
 }
 return {...forecast,action:null,tradeAllowed:false};
}
function regular(previous,current){if(previous===null)return true;
 const p=Date.parse(previous+"T00:00:00Z"),n=Date.parse(current+"T00:00:00Z"),gap=(n-p)/DAY,d=new Date(p).getUTCDay();
 return gap===1||(gap===3&&d===5)||(gap===4&&d===5&&new Date(n).getUTCDay()===2)||gap===2;
}
function completedSession(s,{session,price,sourceId,availableAt}){
 if(s.version!==VERSION)throw Error("CP_VERSION");
 const t=stamp(availableAt),end=Date.parse(session+"T22:00:00Z");
 if(!/^\d{4}-\d{2}-\d{2}$/.test(session)||!Number.isFinite(end)||t>end||
    !finite(price)||price<=0||!sourceId)throw Error("CP_INVALID_SESSION");
 if(s.lastSession!==null&&session<=s.lastSession)throw Error("CP_NONMONOTONIC_SESSION");
 if(!regular(s.lastSession,session)||(s.lastSource&&s.lastSource!==sourceId)){
  s.audit.censored+=s.pending.length;s.pending=[];s.audit.sourceBreaks++;
 }
 s.sessionIndex++;
 const keep=[];
 for(const p of s.pending){
  if(p.sourceId!==sourceId){s.audit.censored++;continue;}
  if(p.startIndex===null){
   if(session<=p.anchorDay){keep.push(p);continue;}
   p.startIndex=s.sessionIndex-1;
  }
  if(s.sessionIndex-p.startIndex<p.h){keep.push(p);continue;}
  const netBuy=100*(Math.log(price/p.price)+2*Math.log(1-FEE));
  const netSell=100*(-Math.log(price/p.price)+2*Math.log(1-FEE));
  for(const k of p.keys){add(s,k+"|BUY",p.h,netBuy,p.startIndex,session);
                      add(s,k+"|SELL",p.h,netSell,p.startIndex,session);}
  s.audit.labelsMatured++;
 }
 s.pending=keep;s.lastSession=session;s.lastSource=sourceId;
 return {labelsMatured:s.audit.labelsMatured,pending:s.pending.length};
}
function summary(s){return {version:VERSION,audit:clone(s.audit),cohorts:Object.keys(s.cohorts).length,
 pending:s.pending.length,tradeAllowed:false,scienceGate:"NOT_PROVEN"};}
function checkpoint(s){return clone(s);}
function restore(x){const s=clone(x);if(!s||s.version!==VERSION||!s.config||!Array.isArray(s.pending)||!s.cohorts)
 throw Error("CP_BAD_CHECKPOINT");return s;}
module.exports={VERSION,create,observe,completedSession,score,summary,checkpoint,restore};
