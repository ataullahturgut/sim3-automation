"use strict";
/**
 * M4/M5 component INSIDE GOLD-ADAPTIVE-MODEL-APP-01 S3.
 * A multi-session NET position-opportunity learner using only completed,
 * sequentially observed slow sessions. Each input session is a historical
 * reconstructed quote-only proxy, NOT bank execution or firstprint PIT.
 *
 * Nothing is a live AL/SAT action. 1/3/5/10 complete TRADING sessions
 * are observed on their MATURITY dates; cohorts overlap and therefore
 * their raw count is NOT independent episode evidence.
 */
const VERSION="KAVIS_S3_MATURED_POSITION_MEMORY_20261016";
const HORIZONS=[1,3,5,10],COST=Math.log(.992)*2,DAY=86400000;
const clone=x=>JSON.parse(JSON.stringify(x));
const finite=x=>typeof x==="number"&&Number.isFinite(x);
const phaseKey=(phase,dir)=>{
 const phaseClass=["START","CONTINUE","REENTRY"].includes(phase)?"TREND":
   phase==="PULLBACK"?"PULLBACK":
   phase==="NEUTRAL"?"NEUTRAL":phase==="END"?"END":"NO_SLOW";
 return phaseClass+":"+(dir===1?"UP":dir===-1?"DOWN":"NONE");
};
function regular(a,b){
 if(a===null)return true;
 const before=new Date(a+"T00:00:00Z"),after=new Date(b+"T00:00:00Z");
 const days=(after-before)/DAY;
 return (days===1&&before.getUTCDay()>=1&&before.getUTCDay()<=4)||
   (days===3&&before.getUTCDay()===5&&after.getUTCDay()===1);
}
function create(){return {version:VERSION,last:null,index:-1,pending:[],cohorts:{},
 audit:{acceptedSessions:0,maturedLabels:0,censoredLabels:0,
  brokenSessions:0,sourceBreaks:0,predictionsReady:0}};}
function cohortKey(state,h){return state+"#"+h;}
function completed(s,{session,sourceId,price,phase,direction=0,availableAt}){
 if(s.version!==VERSION)throw Error("POSITION_MEMORY_VERSION");
 const time=Date.parse(session+"T22:00:00Z");
 if(!/^\d{4}-\d{2}-\d{2}$/.test(session)||!Number.isFinite(time)||
   new Date(time).getUTCDay()<1||new Date(time).getUTCDay()>5||
   typeof sourceId!=="string"||!sourceId||!finite(price)||price<=0||
   typeof phase!=="string"||![-1,0,1].includes(direction)||
   typeof availableAt!=="string"||!Number.isFinite(Date.parse(availableAt))||
   Date.parse(availableAt)>time)
   throw Error("POSITION_MEMORY_INVALID_SESSION");
 if(s.last&&session<=s.last.session)throw Error("POSITION_MEMORY_NONMONOTONIC");
 const broken=!!s.last&&!regular(s.last.session,session);
 const changed=!!s.last&&s.last.sourceId!==sourceId;
 if(broken||changed){
   s.audit.censoredLabels+=s.pending.length;s.pending=[];
   if(broken)s.audit.brokenSessions++;
   if(changed)s.audit.sourceBreaks++;
 }
 s.index++;s.audit.acceptedSessions++;
 const kept=[];
 for(const p of s.pending){
   if(p.dueIndex>s.index){kept.push(p);continue;}
   if(p.dueIndex!==s.index)throw Error("POSITION_MEMORY_DUE_INDEX_SKIPPED");
   const net=100*(Math.log(price/p.price)+COST);
   const key=cohortKey(p.state,p.h);
   const st=s.cohorts[key]??(s.cohorts[key]={n:0,mean:0,m2:0,positive:0,negative:0,
     firstKnownAt:null,lastKnownAt:null});
   st.n++;
   const delta=net-st.mean;st.mean+=delta/st.n;st.m2+=delta*(net-st.mean);
   if(net>0)st.positive++;else st.negative++;
   st.firstKnownAt??=session;st.lastKnownAt=session;
   s.audit.maturedLabels++;
 }
 s.pending=kept;
 const state=phaseKey(phase,direction);
 for(const h of HORIZONS)s.pending.push({state,h,index:s.index,dueIndex:s.index+h,price});
 s.last={session,sourceId,price,state};
 return {asof:new Date(time).toISOString(),state,matured:s.audit.maturedLabels,
    pending:s.pending.length,authority:"RESEARCH_ONLY_NO_LIVE_TRADE"};
}
function forecast(s,state,{minSupport=8}={}){
 if(s.version!==VERSION)throw Error("POSITION_MEMORY_VERSION");
 const rows=HORIZONS.map(h=>{
  const c=s.cohorts[cohortKey(state,h)],n=c?.n??0;
  const std=n>1?Math.sqrt(Math.max(0,c.m2/(n-1))):null;
  const stderr=std===null?null:std/Math.sqrt(n);
  const ready=n>=minSupport;
  return {sessions:h,n,ready,
   netGoldVsCashLogPct:ready?c.mean:null,
   stderrPct:ready?stderr:null,
   conservativeLowerPct:ready?c.mean-1.96*stderr:null,
   positiveN:c?.positive??0,negativeN:c?.negative??0,
   lastKnownAt:c?.lastKnownAt??null};
 });
 if(rows.some(x=>x.ready))s.audit.predictionsReady++;
 return {state,byHorizon:rows,bankRoundTripFeeFraction:1-.992*.992,
  scienceGate:"NOT_PROVEN_OVERLAPPING_SESSIONS"};
}
function summary(s){return {version:VERSION,horizonsSessions:HORIZONS,
  cohortCount:Object.keys(s.cohorts).length,audit:clone(s.audit),
  learnedCohorts:Object.fromEntries(Object.entries(s.cohorts).map(([k,v])=>[k,
   {n:v.n,meanNetGoldVsCashLogPct:v.mean,positive:v.positive,negative:v.negative,
    firstKnownAt:v.firstKnownAt,lastKnownAt:v.lastKnownAt}])),
  scienceGate:"NOT_PROVEN_OVERLAPPING_SESSIONS",liveTradeAuthorized:false};}
function restore(v){const s=clone(v);
 if(s.version!==VERSION||!s.cohorts||!s.audit||!Array.isArray(s.pending))
  throw Error("POSITION_MEMORY_BAD_CHECKPOINT");
 return s;}
module.exports={VERSION,HORIZONS,create,completed,forecast,summary,restore,phaseKey};
