"use strict";
/**
 * GOLD-ADAPTIVE-MODEL-APP-01 S2 SLOW SESSION LIFECYCLE (one CORE component).
 * One observation = one completed qualified gold trading session.
 * Session roll: fixed 22:00 UTC research convention (NOT official exchange
 * settlement; summer last close may be stale up to 90min). Shift raw M15
 * timestamp by 2h to associate Sun evening trade with Monday.
 * Only Fri->Mon is treated as a scheduled nontrading gap. Unknown missing
 * weekday/holiday -> right-censor; no interpolation. Cross-source -> censor.
 * Horizons are 1,3,5,10 COMPLETED TRADING SESSIONS, not calendar days.
 * END probability from *previously observed* completed episodes; early END
 * labels scored when known, continued episodes at exact horizon session.
 * Research-only. No portfolio / trade API.
 */
const VERSION="KAVIS_S2_SLOW_SESSION_LIFECYCLE_20261016";
const HORIZONS=[1,3,5,10],DAY=86400000;
const PHASES=["WARMUP","NEUTRAL","START","CONTINUE","PULLBACK","REENTRY","END"];
const copy=x=>JSON.parse(JSON.stringify(x));
const iso=x=>new Date(x).toISOString();
const finite=x=>typeof x==="number"&&Number.isFinite(x);
function parse(t){if(typeof t!=="string"||!/(?:Z|[+-]\d\d:\d\d)$/i.test(t)||!Number.isFinite(Date.parse(t)))
 throw Error("S2S_DATE_OFFSET_REQUIRED");return Date.parse(t);}
function isRegularTransition(a,b){
 if(a===null)return true;
 const prev=new Date(a+"T00:00:00Z"),next=new Date(b+"T00:00:00Z");
 const delta=(next-prev)/DAY,day=prev.getUTCDay();
 return delta===1&&day>=1&&day<=4 ||
  delta===3&&day===5&&next.getUTCDay()===1;
}
function create({sourceRegistry,minReady=8}={}){
 if(!sourceRegistry||!Object.keys(sourceRegistry).length)throw Error("S2S_SOURCE_REGISTRY");
 for(const [id,x]of Object.entries(sourceRegistry))
  if(!id||x.kind!=="MARKET"||!["RECONSTRUCTED_MARKET_ASOF","SYNTHETIC_ONLY","VERIFIED_PIT"].includes(x.evidenceStatus))
   throw Error("S2S_INVALID_SOURCE");
 if(!Number.isInteger(minReady)||minReady<5)throw Error("S2S_BAD_MIN_READY");
 return {version:VERSION,registry:copy(sourceRegistry),minReady,
  lastSession:null,lastSource:null,sessionIndex:-1,window:[],active:null,
  nextEpisodeId:1,complete:[],censored:[],endedAt:{},censoredAt:{},
  pending:[],transitions:{},phases:Object.fromEntries(PHASES.map(x=>[x,0])),
  eligibleSessions:0,rejectedSessions:0,minorDegradedSessions:0,
  sessionBreaks:0,sourceBreaks:0,
  stats:Object.fromEntries(HORIZONS.map(h=>[h,{issued:0,ready:0,scored:0,
   end:0,continue:0,censored:0,brier:0,baselineBrier:0,correct:0,
   baselineCorrect:0,byYear:{},byEpisode:{}}]))};
}
function validate(s,r){
 if(!r||!r.session||!r.source_id||!finite(r.close_price)||r.close_price<=0||
  !Number.isInteger(r.n)||!Number.isInteger(r.full_n)||
  !finite(r.max_gap_minutes)||!r.first_bar||!r.last_bar||
  !Number.isInteger(r.last_native_minute_bars))
  throw Error("S2S_INCOMPLETE_SESSION_RECORD");
 const label=r.session;
 if(!/^\d{4}-\d\d-\d\d$/.test(label))throw Error("S2S_INVALID_SESSION");
 const end=Date.parse(label+"T22:00:00Z"),first=parse(r.first_bar),last=parse(r.last_bar);
 const dow=new Date(label+"T00:00:00Z").getUTCDay();
 if(dow<1||dow>5)throw Error("S2S_NONTRADING_SESSION");
 if(s.lastSession!==null&&label<=s.lastSession)
  throw Error("S2S_NONMONOTONIC_SESSION");
 const source=s.registry[r.source_id];
 if(!source||source.kind!=="MARKET")throw Error("S2S_UNREGISTERED_SOURCE");
 if(r.availableAt&&parse(r.availableAt)>end)throw Error("S2S_FUTURE_AVAILABLE");
 if(last+15*60000>end||first>end||first<end-25*3600000)
  throw Error("S2S_BAR_TIME_OUTSIDE_SESSION");
 // Daily endpoint quality: allow ≤2 isolated degraded intraday M15 bars,
 // but NEVER a partial terminal bar, absent 5+ hours, or a stale session close.
 // Research quality grade remains IMPERFECT_SESSION, not full PIT quality.
 const valid=r.n>=80&&r.full_n>=r.n-2&&r.last_native_minute_bars===15&&
  r.max_gap_minutes<=90&&(end-(last+15*60000))<=90*60000 &&
  (first>=end-24*3600000)&&
  (first<=end-20*3600000);
 return {label,end,valid};
}
function zscore(w){
 if(w.length<11)return null;
 const l=w.slice(-11).map(p=>Math.log(p));
 let sum=0,v=0;
 for(let i=1;i<l.length;i++){const r=l[i]-l[i-1];sum+=r;v+=r*r;}
 return sum/Math.max(.0001,Math.sqrt(v));
}
function mark(s,from,to){if(from!==to)s.transitions[from+"->"+to]=(s.transitions[from+"->"+to]||0)+1;}
function close(s,{censor=false}={}){
 const e=s.active;if(!e)return;
 const completed={id:e.id,direction:e.direction,
  sessions:s.sessionIndex-e.startedIndex,
  knownAt:s.sessionIndex,snapshots:copy(e.snapshots)};
 if(censor){
  s.censored.push(completed);s.censoredAt[e.id]=s.sessionIndex;
 }else{
  s.complete.push(completed);s.endedAt[e.id]=s.sessionIndex;
 }
 s.active=null;
}
function risk(s,age,dir,phase,H){
 const alive=s.complete.filter(e=>e.sessions>age);
 const verified=s.censored.filter(e=>e.sessions>=age+H);
 const all=[...alive.map(e=>({...e,isEnded:true})),
   ...verified.map(e=>({...e,isEnded:false}))];
 const same=all.filter(e=>e.direction===dir);
 const phaseMatched=same.filter(e=>{
  const a=e.snapshots.filter(z=>z.age<=age).at(-1);
  return !!a&&a.phase===phase&&age-a.age<=1;
 });
 const chosen=phaseMatched.length>=s.minReady?phaseMatched:same;
 const prob=x=>(1+x.filter(e=>e.isEnded&&e.sessions<=age+H).length)/(2+x.length);
 return {horizonSessions:H,ready:chosen.length>=s.minReady,
  pEnd:chosen.length>=s.minReady?prob(chosen):null,
  pContinue:chosen.length>=s.minReady?1-prob(chosen):null,
  baselineReady:all.length>=s.minReady,
  baselineP:all.length>=s.minReady?prob(all):null,
  riskN:chosen.length,baselineN:all.length,
  basis:phaseMatched.length>=s.minReady?"PHASE_DIRECTION":"DIRECTION"};
}
function score(s,q,y){
 const st=s.stats[q.horizonSessions];
 if(!st||q.modelP===null||q.baseP===null)return;
 st.scored++;if(y)st.end++;else st.continue++;
 st.brier+=(q.modelP-y)**2;st.baselineBrier+=(q.baseP-y)**2;
 st.correct+=Number((q.modelP>=.5)===Boolean(y));
 st.baselineCorrect+=Number((q.baseP>=.5)===Boolean(y));
 const cl=st.byEpisode[q.episodeId]??{n:0,improvement:0};
 cl.n++;cl.improvement+=(q.baseP-y)**2-(q.modelP-y)**2;
 st.byEpisode[q.episodeId]=cl;
 const year=q.session.slice(0,4);
 if(!st.byYear[year])st.byYear[year]={n:0,end:0,continue:0,brier:0,base:0};
 const v=st.byYear[year];v.n++;v.end+=y;v.continue+=1-y;
 v.brier+=(q.modelP-y)**2;v.base+=(q.baseP-y)**2;
}
function settle(s){
 const remaining=[];
 for(const q of s.pending){
  const ended=s.endedAt[q.episodeId],cens=s.censoredAt[q.episodeId];
  if(ended!==undefined&&ended<=s.sessionIndex&&ended<=q.dueIndex){
   score(s,q,1);continue;
  }
  if(cens!==undefined&&cens<=s.sessionIndex){
   s.stats[q.horizonSessions].censored++;continue;
  }
  if(s.sessionIndex<q.dueIndex){remaining.push(q);continue;}
  if(s.sessionIndex!==q.dueIndex)throw Error("S2S_MISSING_SESSION_MATURITY");
  score(s,q,0);
 }
 s.pending=remaining;
}
function censorPending(s){
 for(const p of s.pending)s.stats[p.horizonSessions].censored++;
 s.pending=[];
}
function observe(s,r){
 if(s.version!==VERSION)throw Error("S2S_VERSION");
 const v=validate(s,r);
 // Session is only known at 22:00 UTC after all included M15 bars end.
 if(!v.valid){
  s.rejectedSessions++;
  close(s,{censor:true});censorPending(s);
  s.window=[];s.lastSession=v.label;s.lastSource=r.source_id;
  return {session:v.label,phase:"REJECTED_SESSION",action:null};
 }
 if(s.lastSession!==null&&!isRegularTransition(s.lastSession,v.label)){
  s.sessionBreaks++;close(s,{censor:true});censorPending(s);s.window=[];
 }
 if(s.lastSource!==null&&s.lastSource!==r.source_id){
  s.sourceBreaks++;close(s,{censor:true});censorPending(s);s.window=[];
 }
 s.lastSession=v.label;s.lastSource=r.source_id;
 s.sessionIndex++;s.eligibleSessions++;
 if(r.full_n!==r.n)s.minorDegradedSessions++;
 s.window.push(r.close_price);if(s.window.length>11)s.window.shift();
 const z=zscore(s.window);
 let phase="WARMUP";
 if(z!==null){
  if(!s.active){
   if(Math.abs(z)>=1.15){
    s.active={id:s.nextEpisodeId++,direction:Math.sign(z),
     startedIndex:s.sessionIndex,extreme:r.close_price,phase:"START",
     misses:0,snapshots:[]};
    phase="START";mark(s,"NEUTRAL","START");
   }else phase="NEUTRAL";
  }else{
   const e=s.active,old=e.phase;
   const opp=e.direction*z<=.2;
   e.misses=opp?e.misses+1:0;
   if(e.misses>=2){
    mark(s,old,"END");close(s);phase="END";
   }else{
    e.extreme=e.direction===1?Math.max(e.extreme,r.close_price):
      Math.min(e.extreme,r.close_price);
    const retr=e.direction===1?Math.log(e.extreme/r.close_price):
      Math.log(r.close_price/e.extreme);
    const recentRets=s.window.slice(1).map((p,i)=>
      Math.abs(Math.log(p/s.window[i])));
    const base=recentRets.reduce((a,b)=>a+b,0)/recentRets.length;
    const pulling=retr>Math.max(.0001,base)*1.4;
    phase=pulling?"PULLBACK":old==="PULLBACK"?"REENTRY":"CONTINUE";
    mark(s,old,phase);e.phase=phase;
   }
  }
 }
 settle(s);
 const age=s.active?s.sessionIndex-s.active.startedIndex:0;
 const hazards=s.active?Object.fromEntries(HORIZONS.map(H=>[H,
  risk(s,age,s.active.direction,phase,H)])):null;
 if(s.active){
  s.active.snapshots.push({age,phase});
  for(const H of HORIZONS){
   const z=hazards[H],st=s.stats[H];st.issued++;if(z.ready)st.ready++;
   s.pending.push({session:v.label,episodeId:s.active.id,
    dueIndex:s.sessionIndex+H,horizonSessions:H,
    modelP:z.ready?z.pEnd:null,baseP:z.baselineReady?z.baselineP:null});
  }
 }
 if(PHASES.includes(phase))s.phases[phase]++;
 return {session:v.label,phase,direction:s.active?.direction??0,
  episodeAgeSessions:age,trendZ:z,hazards,action:null,
  authority:"S2_RESEARCH_ONLY_NOT_TRADE"};
}
function uncertainty(clusters){
 const a=Object.values(clusters);
 if(a.length<20)return {clusters:a.length,ci95:null};
 const mean=a.reduce((v,x)=>v+x.improvement,0)/a.reduce((v,x)=>v+x.n,0);
 let seed=34121;const rnd=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
 const b=[];for(let i=0;i<700;i++){
  let n=0,d=0;
  for(let j=0;j<a.length;j++){const x=a[Math.floor(rnd()*a.length)];n+=x.n;d+=x.improvement;}
  b.push(d/n);
 }
 b.sort((a,b)=>a-b);
 return {clusters:a.length,meanImprovement:mean,ci95:[b[17],b[682]],
   method:"EPISODE_CLUSTER_BOOTSTRAP_700_EXPLORATORY"};
}
function summary(s){
 const table={};
 for(const H of HORIZONS){
  const st=s.stats[H],yrs={};
  for(const [y,v]of Object.entries(st.byYear))
   yrs[y]={n:v.n,end:v.end,continue:v.continue,brier:v.brier/v.n,
    baselineBrier:v.base/v.n};
  table[H]={horizonSessions:H,issued:st.issued,ready:st.ready,
   scored:st.scored,end:st.end,continue:st.continue,censored:st.censored,
   brier:st.scored?st.brier/st.scored:null,
   baselineBrier:st.scored?st.baselineBrier/st.scored:null,
   estimable:st.end>=12&&st.continue>=12,byYear:yrs,
   bootstrap:uncertainty(st.byEpisode)};
 }
 const durations=s.complete.map(x=>x.sessions).sort((a,b)=>a-b);
 const median=durations.length?durations[Math.floor((durations.length-1)/2)]:null;
 return {version:VERSION,mode:"DISCOVERY_FULL_ARCHIVE_RESEARCH",
  timeUnit:"COMPLETED_TRADING_SESSIONS_NOT_CALENDAR_DAYS",
  sessionConvention:"UTC22_CLOSE_FIXED_RESEARCH_NO_EXCHANGE_SETTLEMENT_CERT",
  completedSessions:s.eligibleSessions,rejectedSessions:s.rejectedSessions,
  minorDegradedSessions:s.minorDegradedSessions,
  completeEpisodes:s.complete.length,censoredEpisodes:s.censored.length,
  calendarBreaks:s.sessionBreaks,sourceBreaks:s.sourceBreaks,
  medianEpisodeSessions:median,phases:copy(s.phases),
  byHorizon:table,tradeActions:0,scienceGate:"NOT_PROVEN",
  knownLimitations:["RECONSTRUCTED_DATA_NOT_PIT",
   "HOLIDAYS_WITHOUT_OFFICIAL_CALENDAR_CENSORED",
   "UTC22_RESEARCH_CUTOFF_NOT_OFFICIAL_SETTLEMENT",
   "UP_TO_TWO_PARTIAL_INTRADAY_M15_BARS_ALLOW_RESEARCH_ONLY",
   "MONTH_YEAR_EXPERIMENTS_ARE_RETROSPECTIVE_NOT_BLIND_OOS"]};
}
function checkpoint(s){return copy(s);}
function restore(data){
 const s=copy(data);
 if(s.version!==VERSION||!s.registry||!s.stats||
  !Array.isArray(s.pending)||!Array.isArray(s.complete))
  throw Error("S2S_BAD_CHECKPOINT");
 return s;
}
function closeAtEnd(s){close(s,{censor:true});censorPending(s);}
module.exports={VERSION,HORIZONS,create,observe,summary,checkpoint,restore,closeAtEnd};
