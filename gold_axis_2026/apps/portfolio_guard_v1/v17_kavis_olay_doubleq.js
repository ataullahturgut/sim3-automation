"use strict";
/**
 * V16 KAVIS-S: multi-step full-information, off-policy Q learner.
 *
 * Research ONLY. No real orders, no historical data runner, no trading
 * performance claims.  Two actions per holding (KEEP, SWITCH), 2 holdings
 * (CASH, GOLD). Observed exogenous spot movement gives the one-interval
 * counterfactual payoff for all four state/actions after a NEXT
 * BANK checkpoint. Learn from matured intervals only.
 *
 * Bellman backup uses ONLY the current as-of state frozen at signal
 * and the elapsed return known at next checkpoint. One side of fee per
 * switch: no charge on KEEP. Any terminal liquidation fee is outside
 * the finite continuing-portfolio Q objective.
 *
 * Can approximate discounted sequential log wealth under exogenous
 * prices, but is NOT proven Q* (function approximation, selection bias,
 * missing features, market impact, and limited calibration).
 */
const V="V17_KAVIS_EVENT_DOUBLE_Q_20261016";
const HR=3600000,DAY=24*HR;
const STATES=Object.freeze(["CASH","GOLD"]),ACTS=Object.freeze(["KEEP","SWITCH"]);
const KEYS=Object.freeze(["CASH_KEEP","CASH_SWITCH","GOLD_KEEP","GOLD_SWITCH"]);
const FEATURES=Object.freeze(["bias","r4","r1","r3","rv","dd","nq6","nq_present",
 "v15_edge","v15_present","memory_trend","memory_stress",
 "verified_event_polarity","regime_surprise"]);
const D=FEATURES.length;
const clamp=(x,l,h)=>Math.min(h,Math.max(l,x));
const num=x=>typeof x==="number"&&Number.isFinite(x);
const scaled=(x,k)=>num(x)?clamp(x/k,-3,3):0;
const sigmoid=x=>1/(1+Math.exp(-clamp(x,-20,20)));
const dot=(a,x)=>a.reduce((s,w,i)=>s+w*x[i],0);
function stamp(x){
 if(typeof x!=="string"||!/(?:Z|[+-]\d\d:\d\d)$/.test(x))
   throw Error("V16_EXPLICIT_TIMEZONE_REQUIRED");
 const a=Date.parse(x);
 if(!Number.isFinite(a))throw Error("V16_BAD_TIMESTAMP");
 return a;
}
function settings(o={}){
 const f=o.feePerSide??.008,discount=o.gammaPerDay??.94,
  lr=o.learningRate??.18,n=o.minimumMaturedIntervals??12,
  maxGap=o.maxIntervalHours??80,unc=o.uncertaintyScale??.10,
  hours=o.bankCheckpointHoursUTC??[6,9,12],budget=o.goldDownsideBudgetPct??null,
  criticDisagreementPenalty=o.criticDisagreementPenalty??.16,
  regimePenalty=o.regimePenalty??.05,
  gradientMemory=o.gradientMemory??.985,regimeMemory=o.regimeMemory??.93;
 if(!num(f)||f<0||f>=.1)throw Error("V16_BAD_FEE");
 if(!num(discount)||discount<0||discount>1)throw Error("V16_BAD_GAMMA");
 if(!num(lr)||lr<=0||lr>1)throw Error("V16_BAD_LR");
 if(!Number.isInteger(n)||n<2||n>500)throw Error("V16_BAD_WARMUP");
 if(!num(maxGap)||maxGap<1||maxGap>336)throw Error("V16_BAD_GAP");
 if(!num(unc)||unc<0||unc>5)throw Error("V17_BAD_UNCERTAINTY");
 if(!num(criticDisagreementPenalty)||criticDisagreementPenalty<0||criticDisagreementPenalty>2||
  !num(regimePenalty)||regimePenalty<0||regimePenalty>2)throw Error("V17_BAD_PENALTY");
 if(!num(gradientMemory)||gradientMemory<.9||gradientMemory>=1||
  !num(regimeMemory)||regimeMemory<.5||regimeMemory>=1)
    throw Error("V17_BAD_FORGETTING");
 if(!Array.isArray(hours)||hours.length===0||hours.length>12||
  hours.some(x=>!Number.isInteger(x)||x<0||x>23)||
  new Set(hours).size!==hours.length)throw Error("V16_BAD_CHECKPOINTS");
 if(budget!==null&&(!num(budget)||budget<=0||budget>=100))
   throw Error("V16_BAD_BUDGET");
 return {feePerSide:f,gammaPerDay:discount,learningRate:lr,
  minimumMaturedIntervals:n,maxIntervalHours:maxGap,uncertaintyScale:unc,
  bankCheckpointHoursUTC:[...hours].sort((a,b)=>a-b),
  goldDownsideBudgetPct:budget,criticDisagreementPenalty,regimePenalty,
  gradientMemory,regimeMemory,
  liveTrade:false,researchOnly:true};
}
function newHead(){
 return {w:Array(D).fill(0),acc:Array(D).fill(.05),
  n:0,mse:16,lastTD:0};
}
function create(o={}){
 return {version:V,config:settings(o),
  q:Object.fromEntries(KEYS.map(k=>[k,newHead()])),
  qb:Object.fromEntries(KEYS.map(k=>[k,newHead()])),
  risk:{head:newHead(),dual:0,matured:0},
  memory:{trend:0,stress:0},
  regime:{n:0,mean:0,m2:0,var:.25,lastSurprise:0},
  lastSignalAt:null,lastQuoteAt:null,
  virtualPosition:null,seq:0,pending:null,
  lastExecution:null,learned:0,skipped:0,
  audit:{switchFeeObserved:0,trainingPairs:0,
   warmupDecisions:0,wrongTimeRejected:0,updatedA:0,updatedB:0,eventObservations:0}};
}
function target(position,act){
 if(!STATES.includes(position)||!ACTS.includes(act))throw Error("V16_BAD_ACTION");
 return act==="KEEP"?position:position==="CASH"?"GOLD":"CASH";
}
function key(p,a){return p+"_"+a;}
function features(s,o){
 const f=o.market;
 if(!f||!num(f.r4)||!num(f.r1)||!num(f.r3))
   throw Error("V16_MISSING_MARKET_FEATURES");
 for(const v of ["rv","dd","nq6"])
  if(f[v]!=null&&!num(f[v]))throw Error("V16_BAD_MARKET_FEATURE");
 let e=0,flag=0;
 if(o.v15Expert!==undefined){
  const z=o.v15Expert;
  if(!z||stamp(z.availableAt)>stamp(o.asof)||!num(z.actionEdge))
    throw Error("V16_UNVERIFIED_V15_EXPERT_TIMESTAMP_OR_VALUE");
  if(z.position!==o.position)throw Error("V16_V15_POSITION_MISMATCH");
  e=scaled(z.actionEdge,4);flag=1;
 }
 const ev=o.events??[];
 if(!Array.isArray(ev)||ev.length>16)throw Error("V17_BAD_EVENTS");
 let eventPolarity=0;
 for(const e of ev){
  if(!e||e.verifiedFirstPublication!==true||
    !["G01","G02","G03","G04","G05","G06","G07"].includes(e.family)||
    typeof e.evidenceId!=="string"||e.evidenceId.length<4)
    throw Error("V17_EVENT_UNVERIFIED");
  if(stamp(e.firstAvailableAt)>stamp(o.asof))
    throw Error("V17_FUTURE_EVENT_BLOCKED");
  if(!num(e.polarity)||Math.abs(e.polarity)>1)
    throw Error("V17_BAD_EVENT_POLARITY");
  eventPolarity+=e.polarity;
 }
 const r=s.regime,z=scaled(f.r4,3),oldStd=r.n>=8?
   Math.sqrt(Math.max(.04,r.var)):1;
 const surprise=r.n>=8?clamp(Math.abs(z-r.mean)/oldStd/3,0,3):0;
 const m=s.memory,oldTrend=m.trend,oldStress=m.stress;
 const trend=Math.tanh((scaled(f.r1,6)+scaled(f.r3,9))/2);
 const stress=Math.tanh(Math.max(0,-scaled(f.r4,3))+
   .3*Math.max(0,scaled(f.rv,2)));
 // Observable gated state: bounded, fixed safe baseline. Unlike V15,
 // V16's newly learned layer is Q; no false trainable-LSTM claim.
 const gt=sigmoid(1-.3*Math.max(0,scaled(f.rv,3)));
 const gs=sigmoid(1-.4*Math.max(0,-scaled(f.r4,3)));
 const t=gt*oldTrend+(1-gt)*trend,
   st=gs*oldStress+(1-gs)*stress;
 const x=[1,scaled(f.r4,3),scaled(f.r1,6),scaled(f.r3,9),
   scaled(f.rv,3),scaled(f.dd,6),scaled(f.nq6,5),
   f.nq6==null?0:1,e,flag,t,st,clamp(eventPolarity,-3,3),surprise];
 // Only as-of observations update the running moments. Date/weekday/year
 // NEVER enters feature x, but elapsed duration remains causal discount.
 r.n++;
 const prevMean=r.mean,decay=s.config.regimeMemory,rate=1-decay;
 r.mean=decay*r.mean+rate*z;
 const residual=z-prevMean;
 r.var=Math.max(.04,decay*r.var+rate*residual*residual);
 r.m2+=residual*(z-r.mean); // unused historic audit
 r.lastSurprise=surprise;s.audit.eventObservations+=ev.length;
 return {x,nextMemory:{trend:t,stress:st},
   at:stamp(o.asof),v15Included:flag===1};
}
function maskExpert(x,queryPosition,observedPosition){
 // V15 advice is conditional on actual CASH/GOLD. Reuse its value ONLY
 // in the position that produced it. Otherwise it is not a valid
 // counterfactual state feature and must be masked, not extrapolated.
 if(queryPosition===observedPosition||x[9]===0)return x;
 const a=x.slice();a[8]=0;a[9]=0;return a;
}
function qValue(s,x,p,a){
 const k=key(p,a);return .5*(dot(s.q[k].w,x)+dot(s.qb[k].w,x));
}
function riskValue(s,x){return Math.max(0,dot(s.risk.head.w,x));}
function rank(s,x,p){
 const hold=qValue(s,x,p,"KEEP"),switchQ=qValue(s,x,p,"SWITCH");
 const h1=s.q[key(p,"KEEP")],h2=s.q[key(p,"SWITCH")],
   b1=s.qb[key(p,"KEEP")],b2=s.qb[key(p,"SWITCH")];
 const estimateA=dot(h2.w,x)-dot(h1.w,x),
   estimateB=dot(b2.w,x)-dot(b1.w,x);
 const disagreement=Math.abs(estimateA-estimateB);
 const errorScale=Math.sqrt(Math.max(.01,h1.mse)+Math.max(.01,h2.mse)+
   Math.max(.01,b1.mse)+Math.max(.01,b2.mse))/2;
 const uncertainty=s.config.uncertaintyScale*errorScale/
   Math.sqrt(Math.max(1,Math.min(h1.n,h2.n,b1.n,b2.n)))+
   s.config.criticDisagreementPenalty*disagreement+
   s.config.regimePenalty*x[D-1];
 let riskDelta=0,estimatedDownside=null;
 if(s.config.goldDownsideBudgetPct!==null){
  estimatedDownside=riskValue(s,maskExpert(x,"GOLD",p));
  const exceed=Math.max(0,estimatedDownside-s.config.goldDownsideBudgetPct);
  riskDelta=s.risk.dual*exceed;
 }
 // Risk discourages BUY and supports SELL. The risk proxy is the
 // one-interval downside of holding GOLD, not portfolio drawdown or CVaR.
 const signedRisk=p==="CASH"?-riskDelta:riskDelta;
 const edge=switchQ-hold+signedRisk-uncertainty;
 const warm=s.learned>=s.config.minimumMaturedIntervals;
 return {action:warm&&edge>0?"SWITCH":"KEEP",
   edge,rawAdvantage:switchQ-hold,uncertainty,disagreement,regimeSurprise:x[D-1],
   signedRisk,riskDownside:estimatedDownside,
   qKeep:hold,qSwitch:switchQ,ready:warm,
   reason:warm?(edge>0?"Q_SWITCH_POSITIVE":"Q_KEEP_FEE_OR_RISK"):
     "Q_WARMUP"};
}
function signal(s,ob){
 if(s.pending!==null)throw Error("V16_PENDING_SIGNAL");
 if(!ob||!STATES.includes(ob.position))throw Error("V16_BAD_POSITION");
 const at=stamp(ob.asof),available=stamp(ob.featureAvailableAt);
 if(available>at)throw Error("V16_FUTURE_MARKET_BLOCKED");
 if(s.lastSignalAt!==null&&at<=s.lastSignalAt)
   throw Error("V16_NONMONOTONE_SIGNAL");
 if(s.lastQuoteAt!==null&&at<s.lastQuoteAt)
   throw Error("V16_SIGNAL_BEFORE_QUOTE");
 if(s.virtualPosition!==null&&s.virtualPosition!==ob.position)
   throw Error("V16_VIRTUAL_POSITION_MISMATCH");
 // Validation before state mutation.
 const snap=features(s,ob),choice=rank(s,snap.x,ob.position);
 s.memory=snap.nextMemory;
 if(s.virtualPosition===null)s.virtualPosition=ob.position;
 s.lastSignalAt=at;s.seq++;
 const id="V16-"+s.seq;
 s.pending={id,at,position:ob.position,choice:choice.action,
  x:snap.x,reason:choice.reason};
 if(!choice.ready)s.audit.warmupDecisions++;
 return {id,at:ob.asof,position:ob.position,
   action:choice.action==="KEEP"?"WAIT":ob.position==="CASH"?"BUY":"SELL",
   expectedPosition:target(ob.position,choice.action),readiness:choice.ready,
   actionGap:choice.edge,rawAdvantage:choice.rawAdvantage,
   uncertainty:choice.uncertainty,criticDisagreement:choice.disagreement,
   regimeSurprise:choice.regimeSurprise,learnedIntervals:s.learned,
   v15ExpertUsed:snap.v15Included,
   noLiveOrders:true,notAValidatedForecast:true};
}
function ada(w,acc,gradient,lr,memory=.985){
 for(let j=0;j<w.length;j++){
  const g=clamp(gradient[j],-50,50);
  // Decaying RMS gradient statistics adapt after distribution shift.
  acc[j]=Math.max(.05,memory*acc[j]+(1-memory)*g*g);
  w[j]=clamp(w[j]-lr*g/Math.sqrt(acc[j]),-100,100);
 }
}
function backup(s,old,newExecutionAt,price,nextX,nextObservedPosition){
 const timeGap=newExecutionAt-old.at;
 if(!(timeGap>0))throw Error("V16_INVALID_EXECUTION_INTERVAL");
 if(timeGap>s.config.maxIntervalHours*HR){
  s.skipped++;return {accepted:false,reason:"GAP_TOO_LONG"};
 }
 const logMove=100*(Math.log(price)-Math.log(old.price));
 const fee=100*Math.log(1-s.config.feePerSide);
 const gamma=Math.pow(s.config.gammaPerDay,timeGap/DAY);
 const trainA=s.learned%2===0,train=trainA?s.q:s.qb,
   evaluate=trainA?s.qb:s.q,originals={},opposites={};
 for(const p of STATES)for(const a of ACTS){
  const k=key(p,a);originals[k]={w:train[k].w.slice()};
  opposites[k]={w:evaluate[k].w.slice()};
 }
 const nextValues={};
 for(const p of STATES){
  const xn=maskExpert(nextX,p,nextObservedPosition);
  const k0=key(p,"KEEP"),k1=key(p,"SWITCH");
  const greedy=dot(originals[k0].w,xn)>=dot(originals[k1].w,xn)?k0:k1;
  nextValues[p]=dot(opposites[greedy].w,xn);
 }
 const upd=[];
 for(const p of STATES)for(const a of ACTS){
  const k=key(p,a),to=target(p,a),head=train[k],
    x=maskExpert(old.x,p,old.startingPosition);
  // Exactly ONE executed side when switching at entry of interval.
  const reward=(a==="SWITCH"?fee:0)+(to==="GOLD"?logMove:0);
  const future=gamma*nextValues[to],y=reward+future;
  const prior=dot(originals[k].w,x),error=clamp(prior-y,-100,100);
  upd.push({k,head,error,prior,y,reward,to,x});
 }
 for(const u of upd){
  const den=1+u.x.reduce((v,z)=>v+z*z,0);
  ada(u.head.w,u.head.acc,u.x.map(v=>u.error*v/den),
   s.config.learningRate,s.config.gradientMemory);
  u.head.mse=u.head.n===0?u.error*u.error:
   .96*u.head.mse+.04*u.error*u.error;
  u.head.n++;u.head.lastTD=u.error;
 }
 if(s.config.goldDownsideBudgetPct!==null){
  const h=s.risk.head,downside=Math.max(0,-logMove),
   x=maskExpert(old.x,"GOLD",old.startingPosition),
   err=clamp(dot(h.w,x)-downside,-50,50),
   den=1+x.reduce((v,z)=>v+z*z,0);
  ada(h.w,h.acc,x.map(v=>err*v/den),s.config.learningRate/2,s.config.gradientMemory);
  h.mse=h.n===0?err*err:.96*h.mse+.04*err*err;
  h.n++;h.lastTD=err;
  s.risk.dual=clamp(s.risk.dual+.005*(downside-
   s.config.goldDownsideBudgetPct),0,5);
  s.risk.matured++;
 }
 s.learned++;s.audit.trainingPairs+=4;
 if(trainA)s.audit.updatedA++;else s.audit.updatedB++;
 s.audit.switchFeeObserved+=2; // 2 hypothetical SWITCH actions, not cash charge
 return {accepted:true,maturedFrom:new Date(old.at).toISOString(),
   maturedAt:new Date(newExecutionAt).toISOString(),
   intervalDays:timeGap/DAY,knownReturnPct:logMove,
   discount:gamma,hypotheticalSwitchFeePerAction:fee,
   trainedEstimator:trainA?"A":"B",
   trainedHeads:upd.map(z=>({head:z.k,reward:z.reward,target:z.y})),
   fullInformationCounterfactual:true};
}
function quote(s,o){
 if(!num(o?.price)||o.price<=0)throw Error("V16_INVALID_PRICE");
 const at=stamp(o.at);
 if(s.lastQuoteAt!==null&&at<=s.lastQuoteAt)
  throw Error("V16_NONMONOTONE_QUOTE");
 if(o.isBankCheckpoint===true&&
   !s.config.bankCheckpointHoursUTC.includes(new Date(at).getUTCHours()))
  throw Error("V16_INVALID_BANK_CHECKPOINT");
 // If current lock exists the quote may be a valid nonbank observation,
 // but it must not fill at or before its signal.
 if(s.pending&&at<=s.pending.at&&o.isBankCheckpoint===true)
  throw Error("V16_SAME_BAR_FILL_PROHIBITED");
 s.lastQuoteAt=at;
 if(!s.pending)return {at:o.at,fill:null,update:null,ordersSent:0};
 if(o.isBankCheckpoint!==true||
    at<=s.pending.at)return{at:o.at,fill:null,update:null,ordersSent:0};
 if(at-s.pending.at>s.config.maxIntervalHours*HR){
  s.pending=null;s.skipped++;
  return {at:o.at,fill:null,update:null,expired:true,ordersSent:0};
 }
 const p=s.pending,update=s.lastExecution?
   backup(s,s.lastExecution,at,o.price,p.x,p.position):null;
 const endPosition=target(p.position,p.choice);
 s.lastExecution={at,price:o.price,x:p.x,
   startingPosition:p.position,chosenAction:p.choice,endPosition};
 s.virtualPosition=endPosition;
 s.pending=null;
 return {at:o.at,update,ordersSent:0,
   fill:{signalId:p.id,signalAt:new Date(p.at).toISOString(),
    at:o.at,price:o.price,
    suggestedAction:p.choice==="KEEP"?"WAIT":
      p.position==="CASH"?"BUY":"SELL",
    positionBefore:p.position,positionAfter:endPosition,
    feeLegIfSwitched:p.choice==="SWITCH"?s.config.feePerSide:0,
    simulatedExecutionOnly:true}};
}
function save(s){return JSON.parse(JSON.stringify(s));}
function restore(x){
 const s=typeof x==="string"?JSON.parse(x):x;
 if(!s||s.version!==V||!s.q||!s.qb||!s.config||!s.risk||
  !s.memory||!s.audit||!STATES.includes(s.virtualPosition)&&
    s.virtualPosition!==null)throw Error("V16_INVALID_CHECKPOINT");
 const a=JSON.parse(JSON.stringify(s)),cfg=settings(a.config);
 for(const k of KEYS)for(const h of [a.q[k],a.qb[k]]){
  if(!h||!Array.isArray(h.w)||h.w.length!==D||
   !Array.isArray(h.acc)||h.acc.length!==D||
   h.w.some(v=>!num(v))||h.acc.some(v=>!num(v)||v<=0)||
   !Number.isInteger(h.n)||h.n<0||
   !num(h.mse)||h.mse<0)throw Error("V17_BAD_Q_CHECKPOINT");
 }
 const validVector=x=>Array.isArray(x)&&x.length===D&&x.every(num);
 if(!Number.isInteger(a.learned)||a.learned<0||
   !Number.isInteger(a.seq)||a.seq<0||
   !num(a.memory.trend)||!num(a.memory.stress)||
   !a.regime||!Number.isInteger(a.regime.n)||a.regime.n<0||
   !num(a.regime.mean)||!num(a.regime.m2)||!num(a.regime.var)||a.regime.var<.04||
   !num(a.risk.dual)||a.risk.dual<0||
   !a.risk.head||!validVector(a.risk.head.w)||
   !validVector(a.risk.head.acc)||
   a.pending!==null&&(!num(a.pending.at)||
      !STATES.includes(a.pending.position)||
      !ACTS.includes(a.pending.choice)||
      !validVector(a.pending.x))||
   a.lastExecution!==null&&(!num(a.lastExecution.at)||
      !num(a.lastExecution.price)||a.lastExecution.price<=0||
      !STATES.includes(a.lastExecution.startingPosition)||
      !ACTS.includes(a.lastExecution.chosenAction)||
      !validVector(a.lastExecution.x))||
   a.pending!==null&&a.lastSignalAt!==a.pending.at)
   throw Error("V16_BAD_LIFECYCLE_CHECKPOINT");
 a.config=cfg;return a;
}
module.exports={VERSION:V,FEATURES,HR,DAY,create,signal,quote,save,restore};
