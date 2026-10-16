"use strict";
/**
 * GOLD-ADAPTIVE-MODEL-APP-01 / S2: causal price-episode lifecycle component
 * for the SAME adaptive CORE pipeline, not a separate trade strategy.
 * This pilot is research-only. All features derive from completed M15 bars.
 * A gap censors the active episode and all unknown multi-horizon outcomes.
 * Hazard reference episodes enter training only AFTER their end is observable.
 * Structural phase definitions are hypotheses, not discovered causes/alpha.
 */
const VERSION="KAVIS_S2_CAUSAL_EPISODE_PILOT_20261016";
const STEP=15*60000,HOUR=60*60000;
const DEFAULT_HORIZONS=[240,1440,4320,10080,20160]; // 4h, 1d, 3d, 1w, 2w
const STATES=["NEUTRAL","START","CONTINUE","PULLBACK","END","REENTRY","WARMUP","GAP"];
const finite=x=>typeof x==="number"&&Number.isFinite(x);
const iso=t=>new Date(t).toISOString();
const stamp=x=>{
 if(typeof x!=="string"||!/(?:Z|[+-]\d\d:\d\d)$/i.test(x)||
    !Number.isFinite(Date.parse(x)))throw Error("S2_OFFSET_TIME_REQUIRED");
 return Date.parse(x);
};
const copy=x=>JSON.parse(JSON.stringify(x));
const fixed=x=>Math.max(-6,Math.min(6,x));
function create(options={}){
 const o=options;
 const learningMode=o.learningMode??"DISCOVERY_FULL_ARCHIVE";
 if(!["DISCOVERY_FULL_ARCHIVE","STRICT_WALK_FORWARD"].includes(learningMode))
  throw Error("S2_INVALID_LEARNING_MODE");
 const registry=o.sourceRegistry;
 if(!registry||typeof registry!=="object"||!Object.keys(registry).length)
  throw Error("S2_PRICE_SOURCE_REGISTRY_REQUIRED");
 for(const [k,v] of Object.entries(registry)){
  if(!k||!v||v.kind!=="MARKET"||
     !["RECONSTRUCTED_MARKET_ASOF","VERIFIED_PIT","SYNTHETIC_ONLY"].includes(v.evidenceStatus))
   throw Error("S2_BAD_SOURCE_REGISTRY");
 }
 const anchors=o.anchorMinutes??240,horizon=o.horizonMinutes??240,minReady=o.minReady??12;
 const horizons=o.horizonsMinutes??DEFAULT_HORIZONS;
 if(anchors!==240||horizon!==240||!Number.isInteger(minReady)||minReady<5||
    !Array.isArray(horizons)||!horizons.includes(240)||
    horizons.some((h,i)=>!Number.isInteger(h)||h<240||h>20160||
      (i>0&&h<=horizons[i-1])) )
  throw Error("S2_UNREGISTERED_HORIZON_OR_SUPPORT");
 return {version:VERSION,learningMode,registry:copy(registry),
  config:{lookbackBars:16,entryZ:1.25,exitZ:0.2,
   pullbackNorm:0.7,anchorMinutes:anchors,horizonMinutes:horizon,
   minReady,horizonsMinutes:horizons.slice()},lastAt:null,lastPrice:null,lastSource:null,window:[],lastAnchor:null,
  active:null,nextEpisodeId:1,completed:[],censoredEpisodes:[],censored:0,
  endedAt:{},censoredAt:{},pending:[],observations:0,
  scores:{issued:0,ready:0,scored:0,scoredYear:{},brier:0,brierBaseline:0,
   correct:0,correctBaseline:0,censoredPredictions:0,
   perEpisode:{},byHorizon:Object.fromEntries(horizons.map(h=>[h,{
    issued:0,ready:0,scored:0,censored:0,positive:0,negative:0,
    correct:0,baselineCorrect:0,brier:0,brierBaseline:0,byYear:{},perEpisode:{}
   }]))},
  phaseCounts:Object.fromEntries(STATES.map(k=>[k,0])),
  transitionCounts:{},completedDurationsMinutes:[],episodeAudit:[]};
}
function valid(s,ob){
 if(!ob||typeof ob!=="object"||["futureReturn","futurePhase","oracle",
  "target","episodeEnd"].some(k=>k in ob))throw Error("S2_FUTURE_TARGET_FORBIDDEN");
 const t=stamp(ob.asof),started=stamp(ob.barStartedAt),
   available=stamp(ob.priceAvailableAt);
 if(!finite(ob.price)||ob.price<=0||ob.barMinutes!==15||started+STEP!==t||
    available<t||available>t)
   throw Error("S2_INCOMPLETE_OR_FUTURE_PRICE");
 const source=s.registry[ob.priceSource];
 if(!source||source.kind!=="MARKET")throw Error("S2_UNKNOWN_PRICE_SOURCE");
 if(s.learningMode==="STRICT_WALK_FORWARD"&&source.evidenceStatus!=="VERIFIED_PIT"&&
    source.evidenceStatus!=="SYNTHETIC_ONLY")
   throw Error("S2_RECONSTRUCTED_NOT_PIT");
 if(s.lastAt!==null&&t<=s.lastAt)throw Error("S2_TIME_NOT_MONOTONIC");
 return t;
}
function signal(window){
 if(window.length<17)return null;
 const old=window[window.length-17],now=window[window.length-1];
 const log4=Math.log(now/old);
 let varsum=0;
 for(let i=window.length-16;i<window.length;i++)
  varsum+=Math.pow(Math.log(window[i]/window[i-1]),2);
 const volatility=Math.sqrt(varsum);
 return {trendZ:fixed(log4/Math.max(.0001,volatility)),
   volatility:Math.max(.0001,volatility),
   log4:100*log4};
}
/** Empirical conditional competing status for H minutes.
 * Completed episodes are usable only after their END was observed.
 * Right-censored episodes enter the denominator as confirmed survivors
 * only when their observed span exceeds age+H (never as invented END).
 */
function hazard(s,age,dir,phase,horizonMinutes){
 const H=horizonMinutes;
 const ended=s.completed.filter(e=>e.durationMinutes>age);
 const survived=s.censoredEpisodes.filter(e=>e.durationMinutes>=age+H);
 const risk=[...ended.map(e=>({...e,ended:true})),
   ...survived.map(e=>({...e,ended:false}))];
 const sameDirection=risk.filter(e=>e.direction===dir);
 const matchedPhase=e=>{
  let nearest=null;
  for(const snap of e.snapshots){
   if(snap.ageMinutes<=age&&(!nearest||snap.ageMinutes>nearest.ageMinutes))
    nearest=snap;
  }
  return !!nearest&&nearest.phase===phase&&
    age-nearest.ageMinutes<=s.config.anchorMinutes;
 };
 const phasePool=sameDirection.filter(matchedPhase);
 const enough=s.config.minReady;
 const eligible=phasePool.length>=enough?phasePool:sameDirection;
 const calc=pool=>pool.length?
   (1+pool.filter(e=>e.ended&&e.durationMinutes<=age+H).length)/(2+pool.length):null;
 return {horizonMinutes:H,
  ready:eligible.length>=enough,p:eligible.length>=enough?calc(eligible):null,
  baselineReady:risk.length>=enough,
  baselineP:risk.length>=enough?calc(risk):null,
  riskN:eligible.length,phaseRiskN:phasePool.length,globalRiskN:risk.length,
  censoredKnownSurvivors:risk.filter(e=>!e.ended).length,
  method:phasePool.length>=enough?"PHASE_AND_DIRECTION":"DIRECTION_ONLY_FALLBACK"};
}
function scoreOne(s,q,label,t){
 const h=q.horizonMinutes??240,st=s.scores.byHorizon[h];
 if(!st)throw Error("S2_UNREGISTERED_SCORE_HORIZON");
 if(q.modelP===null||q.baselineP===null)return;
 st.scored++;st.positive+=label;st.negative+=1-label;
 st.brier+=(q.modelP-label)**2;
 st.brierBaseline+=(q.baselineP-label)**2;
 st.correct+=Number((q.modelP>=.5)===Boolean(label));
 st.baselineCorrect+=Number((q.baselineP>=.5)===Boolean(label));
 const diff=(q.baselineP-label)**2-(q.modelP-label)**2;
 const cluster=st.perEpisode[q.episodeId]??{n:0,delta:0};
 cluster.n++;cluster.delta+=diff;
 st.perEpisode[q.episodeId]=cluster;
 const year=String(new Date(q.at).getUTCFullYear());
 if(!st.byYear[year])st.byYear[year]=
   {n:0,positive:0,negative:0,brier:0,baseBrier:0,modelCorrect:0,baseCorrect:0};
 const z=st.byYear[year];z.n++;z.positive+=label;z.negative+=1-label;
 z.brier+=(q.modelP-label)**2;z.baseBrier+=(q.baselineP-label)**2;
 z.modelCorrect+=Number((q.modelP>=.5)===Boolean(label));
 z.baseCorrect+=Number((q.baselineP>=.5)===Boolean(label));
 // Legacy 4-hour report fields remain exactly the same unit (H=240).
 if(h===240){
  const x=s.scores;
  x.scored++;x.brier+=(q.modelP-label)**2;
  x.brierBaseline+=(q.baselineP-label)**2;
  const c=x.perEpisode[q.episodeId]??{n:0,delta:0};
  c.n++;c.delta+=diff;x.perEpisode[q.episodeId]=c;
  x.correct+=Number((q.modelP>=.5)===Boolean(label));
  x.correctBaseline+=Number((q.baselineP>=.5)===Boolean(label));
  if(!x.scoredYear[year])x.scoredYear[year]=
    {n:0,modelBrier:0,baseBrier:0,modelCorrect:0,baseCorrect:0};
  const by=x.scoredYear[year];by.n++;
  by.modelBrier+=(q.modelP-label)**2;
  by.baseBrier+=(q.baselineP-label)**2;
  by.modelCorrect+=Number((q.modelP>=.5)===Boolean(label));
  by.baseCorrect+=Number((q.baselineP>=.5)===Boolean(label));
 }
}
function mature(s,t){
 const keep=[];
 for(const q of s.pending){
  const h=q.horizonMinutes??240;
  const ended=s.endedAt[q.episodeId],censored=s.censoredAt[q.episodeId];
  // A real END is an irrevocable positive label as soon as observed,
  // even if H is 14d. Never wait through a weekend to re-discover it.
  if(ended!==undefined&&ended<=t&&ended<=q.due){
   scoreOne(s,q,1,t);
   continue;
  }
  if(censored!==undefined&&censored<=t){
   s.scores.byHorizon[h].censored++;
   if(h===240)s.scores.censoredPredictions++;
   continue;
  }
  if(t<q.due){keep.push(q);continue;}
  if(t!==q.due)throw Error("S2_PREDICTION_MATURITY_GAP");
  // Observed active episode at the exact maturity => verified survival.
  scoreOne(s,q,0,t);
 }
 s.pending=keep;
}
function transition(s,from,to){
 if(from!==to)s.transitionCounts[from+"->"+to]=(s.transitionCounts[from+"->"+to]||0)+1;
}
function endEpisode(s,t,{censor=false}={}){
 const ep=s.active;if(!ep)return;
 ep.durationMinutes=(t-ep.startedAt)/60000;
 if(censor){
  s.censoredAt[ep.id]=t;s.censored++;
  s.censoredEpisodes.push({id:ep.id,direction:ep.direction,
    durationMinutes:ep.durationMinutes,censoredAt:t,snapshots:ep.snapshots});
 }else{
  s.endedAt[ep.id]=t;
  s.completed.push({id:ep.id,direction:ep.direction,
   durationMinutes:ep.durationMinutes,endedAt:t,snapshots:ep.snapshots});
  s.completedDurationsMinutes.push(ep.durationMinutes);
  s.episodeAudit.push({direction:ep.direction,durationMinutes:ep.durationMinutes,
   endedAt:iso(t),sampledPhases:ep.snapshots.length});
 }
 s.active=null;
}
function phaseOutput(s,t,phase,z,drawdown,isAnchor){
 const ep=s.active,age=ep?(t-ep.startedAt)/60000:0;
 const hazards=ep&&isAnchor?Object.fromEntries(s.config.horizonsMinutes.map(h=>[
  h,hazard(s,age,ep.direction,phase,h)])):null;
 return {at:iso(t),phase,direction:ep?.direction??0,
   episodeAgeMinutes:age,trendZ:z?.trendZ??null,
   retracementNorm:drawdown,activeEpisode:!!ep,
   hazardsByHorizon:hazards,hazard4h:hazards?.[240]??null,
   action:null,authority:"RESEARCH_PHASE_ONLY_NOT_TRADE"};
}
function observe(s,ob){
 if(s.version!==VERSION)throw Error("S2_BAD_VERSION");
 const t=valid(s,ob);
 if(s.lastAt!==null&&(t-s.lastAt!==STEP||
    (s.lastSource!==null&&ob.priceSource!==s.lastSource))){
  // This is right censoring: no artificial weekend turning points, no
  // interpolation, and no carrying incomplete 4h forecasts over missing bars.
  endEpisode(s,s.lastAt,{censor:true});
  for(const p of s.pending){
   const h=p.horizonMinutes??240;
   s.scores.byHorizon[h].censored++;
   if(h===240)s.scores.censoredPredictions++;
  }
  s.pending=[];
  s.window=[];s.lastAnchor=null;s.lastPrice=null;
 }
 // A terminated episode is known at this bar close, but any forecast
 // made on a previous bar is immutable until its exact due bar matures.
 const previous=s.lastPrice;
 s.window.push(ob.price);
 if(s.window.length>17)s.window.shift();
 const z=signal(s.window);
 let phase="WARMUP",retreat=null;
 if(z){
  const prior=s.active;
  if(!prior){
   if(Math.abs(z.trendZ)>=s.config.entryZ){
    const direction=Math.sign(z.trendZ);
    s.active={id:s.nextEpisodeId++,direction,startedAt:t,
     startPrice:ob.price,extremePrice:ob.price,misses:0,
     phase:"START",snapshots:[]};
    phase="START";transition(s,"NEUTRAL","START");
   }else phase="NEUTRAL";
  }else{
   const d=prior.direction;
   const oldPhase=prior.phase;
   const against=d*z.trendZ<=s.config.exitZ;
   prior.misses=against?prior.misses+1:0;
   if(prior.misses>=2){
    transition(s,oldPhase,"END");endEpisode(s,t);phase="END";
   }else{
    const candidate=d===1?Math.max(prior.extremePrice,ob.price):
      Math.min(prior.extremePrice,ob.price);
    prior.extremePrice=candidate;
    retreat=d===1?Math.log(candidate/ob.price)/z.volatility:
      Math.log(ob.price/candidate)/z.volatility;
    const fallback=retreat>=s.config.pullbackNorm;
    if(fallback)phase="PULLBACK";
    else if(oldPhase==="PULLBACK")phase="REENTRY";
    else phase="CONTINUE";
    transition(s,oldPhase,phase);prior.phase=phase;
   }
  }
 }
 // A new 4h decision is only made AFTER the current completed M15 observation.
 // Completed episodes from THIS bar may be used at this timestamp; none of
 // their unobserved future data existed in previous forecasts.
 mature(s,t);
 const last=s.lastAnchor;
 const anchored=!!s.active&&(!last||t-last>=s.config.anchorMinutes*60000);
 let out=phaseOutput(s,t,phase,z,retreat,anchored);
 if(anchored){
  s.lastAnchor=t;
  const ep=s.active;
  ep.snapshots.push({ageMinutes:out.episodeAgeMinutes,phase,direction:ep.direction});
  for(const minutes of s.config.horizonsMinutes){
   const h=out.hazardsByHorizon[minutes],score=s.scores.byHorizon[minutes];
   score.issued++;if(h.ready)score.ready++;
   if(minutes===240){s.scores.issued++;if(h.ready)s.scores.ready++;}
   s.pending.push({at:t,due:t+minutes*60000,horizonMinutes:minutes,
     episodeId:ep.id,modelP:h.ready?h.p:null,
     baselineP:h.baselineReady?h.baselineP:null});
  }
 }
 s.lastAt=t;s.lastPrice=ob.price;s.lastSource=ob.priceSource;
 s.observations++;s.phaseCounts[phase]++;
 return out;
}
function intervalByEpisode(clusters){
 const a=Object.values(clusters);
 if(a.length<20)return {episodes:a.length,ci95:null,method:"TOO_FEW_EPISODES"};
 const totalN=a.reduce((z,x)=>z+x.n,0),totalD=a.reduce((z,x)=>z+x.delta,0);
 let seed=21061923;
 const rand=()=>{seed=(Math.imul(1664525,seed)+1013904223)>>>0;return seed/4294967296;};
 const draws=[];
 for(let k=0;k<1000;k++){
  let n=0,d=0;
  for(let j=0;j<a.length;j++){
   const x=a[Math.floor(rand()*a.length)];n+=x.n;d+=x.delta;
  }
  draws.push(d/n);
 }
 draws.sort((x,y)=>x-y);
 return {episodes:a.length,meanImprovement:totalD/totalN,
  ci95:[draws[24],draws[974]],
  method:"COMPLETED_AND_OPEN_EPISODE_CLUSTER_BOOTSTRAP_1000_RETROSPECTIVE"};
}
function summary(s){
 const k=s.scores,aggregate=k.scored?{
  scored:k.scored,correct:k.correct,baselineCorrect:k.correctBaseline,
  brier:k.brier/k.scored,baselineBrier:k.brierBaseline/k.scored}:{
    scored:0,correct:0,baselineCorrect:0,brier:null,baselineBrier:null};
 const byYear={};
 for(const [y,v]of Object.entries(k.scoredYear))
  byYear[y]={n:v.n,correct:v.modelCorrect,baselineCorrect:v.baseCorrect,
   brier:v.modelBrier/v.n,baselineBrier:v.baseBrier/v.n};
 const horizonStats={};
 for(const h of s.config.horizonsMinutes){
  const z=k.byHorizon[h],years={};
  for(const [y,v] of Object.entries(z.byYear))
   years[y]={n:v.n,positive:v.positive,negative:v.negative,
    brier:v.n?v.brier/v.n:null,baselineBrier:v.n?v.baseBrier/v.n:null,
    correct:v.modelCorrect,baselineCorrect:v.baseCorrect};
  horizonStats[h]={horizonMinutes:h,issued:z.issued,ready:z.ready,
   scored:z.scored,knownEnd:z.positive,verifiedSurvival:z.negative,
   censored:z.censored,
   brier:z.scored?z.brier/z.scored:null,
   baselineBrier:z.scored?z.brierBaseline/z.scored:null,
   correct:z.correct,baselineCorrect:z.baselineCorrect,
   estimable:z.positive>=12&&z.negative>=12,
   // 1w/2w observations may be one-sided due to weekend/source gaps:
   // no gate PASS or alpha claim without both outcome classes.
   scienceWarning:z.positive<12||z.negative<12?
     "ONE_SIDED_OR_SPARSE_HORIZON_UNESTIMABLE":"RESEARCH_ONLY_NOT_BLIND_OOS",
   byYear:years,episodeClusterImprovement:intervalByEpisode(z.perEpisode)};
 }
 const completed=s.completedDurationsMinutes.slice().sort((a,b)=>a-b);
 const percentile=q=>completed.length?completed[Math.floor(q*(completed.length-1))]:null;
 return {version:VERSION,learningMode:s.learningMode,
  status:"S2_DEVELOPMENT_RESEARCH_NOT_ACCEPTED",dataVintage:"HISTORICAL_RECONSTRUCTED",
  observations:s.observations,completeEpisodes:s.completed.length,
  censoredEpisodes:s.censored,pendingForecasts:s.pending.length,
  phaseCounts:copy(s.phaseCounts),transitions:copy(s.transitionCounts),
  episodeDurationHours:{p25:percentile(.25)/60||null,
    median:percentile(.50)/60||null,p75:percentile(.75)/60||null},
  prediction:{...aggregate,byYear,issued:k.issued,ready:k.ready,
   censored:k.censoredPredictions,
   episodeClusterImprovement:intervalByEpisode(k.perEpisode)},
  continuationAndEndByHorizon:horizonStats,
  financialTrades:0,profitabilityClaim:false};
}
function checkpoint(s){return copy(s);}
function restore(s){
 const v=copy(s);
 if(v.version!==VERSION||!Array.isArray(v.completed)||!Array.isArray(v.pending)||
   !Array.isArray(v.window)||!v.registry||!v.config)throw Error("S2_BAD_CHECKPOINT");
 if(v.window.length>17)throw Error("S2_INVALID_CHECKPOINT_WINDOW");
 if(!v.scores.perEpisode)v.scores.perEpisode={};
 if(!Array.isArray(v.config.horizonsMinutes)||!v.config.horizonsMinutes.includes(240)||
   !v.scores.byHorizon||!Array.isArray(v.censoredEpisodes))
  throw Error("S2_MULTIHORIZON_CHECKPOINT_INCOMPATIBLE");
 if(v.lastSource===undefined)v.lastSource=null;
 return v;
}
function closeAtEndOfSample(s){
 if(s.lastAt!==null)endEpisode(s,s.lastAt,{censor:true});
 for(const q of s.pending){
  const h=q.horizonMinutes??240;
  s.scores.byHorizon[h].censored++;
  if(h===240)s.scores.censoredPredictions++;
 }
 s.pending=[];
}
module.exports={VERSION,DEFAULT_HORIZONS,create,observe,summary,checkpoint,restore,closeAtEndOfSample};