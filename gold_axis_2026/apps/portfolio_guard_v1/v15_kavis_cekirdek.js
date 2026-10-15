"use strict";
/**
 * V15 KAVIS: causal adaptive action-value learner (research contract).
 * Entirely new decision learner; NOT a fitted full LSTM, full ANFIS,
 * independently novel theorem, or validated profitable trading system.
 * NO historical portfolio simulation in this phase.
 *
 * Position-specific finished-episode COUNTERFACTUALS (percent log-wealth):
 * CASH: buy then liquidate vs remain CASH = 100*(ln(P1/P0)+2ln(1-fee))
 * GOLD: sell then repurchase vs hold GOLD = 100*(-ln(P1/P0)+2ln(1-fee)).
 * Gold exit is evaluated as a round-trip: if terminal liquidation instead,
 * its economic payoff differs; do not misrepresent the objective.
 */
const VERSION="V15_KAVIS_CAUSAL_ACTION_LEARNING_20261016";
const HOUR=3600000,DAY=24*HOUR,HORIZONS=Object.freeze([1,3,7,28,56]);
const FEATURE_NAMES=Object.freeze(["bias","r4","r1","r3","rv","dd","nq6",
 "nqPresent","trendMemory","stressMemory","changeSurprise","verifiedEvent",
 "legacy14","legacy56"]);
const D=FEATURE_NAMES.length,MEM_T=8,MEM_S=9,R=5,HIDDEN=6;
const minmax=(x,lo,hi)=>Math.max(lo,Math.min(hi,x));
function finite(x){return typeof x==="number"&&Number.isFinite(x);}
function bounded(x,scale=1){return finite(x)?minmax(x/scale,-3,3):0;}
function sigmoid(x){return 1/(1+Math.exp(-minmax(x,-20,20)));}
function dot(w,x){return w.reduce((s,v,i)=>s+v*x[i],0);}
function time(t){const z=Date.parse(t);if(!Number.isFinite(z))throw Error("INVALID_ASOF_TIMESTAMP");return z;}
function softmax(v){
 const mx=Math.max(...v),u=v.map(z=>Math.exp(z-mx)),s=u.reduce((a,b)=>a+b,0);
 return u.map(z=>z/s);
}
function newLinear(){return {w:Array(D).fill(0),acc:Array(D).fill(.01)};}
function newFuzzy(){
 return {w:Array.from({length:R},()=>Array(D).fill(0)),
   acc:Array.from({length:R},()=>Array(D).fill(.01))};
}
function newMLP(){
 const w1=Array.from({length:HIDDEN},(_,i)=>
   Array.from({length:D},(_,j)=>.025*Math.sin((i+1)*(j+2))));
 return {w1,b1:Array(HIDDEN).fill(0),w2:Array(HIDDEN).fill(0),b2:0,
   a1:Array.from({length:HIDDEN},()=>Array(D).fill(.01)),
   ab1:Array(HIDDEN).fill(.01),a2:Array(HIDDEN).fill(.01),ab2:.01};
}
function newHead(){
 return {n:0,linear:newLinear(),fuzzy:newFuzzy(),mlp:newMLP(),
   q:newLinear(),logExpertWeight:[0,0,0],expertLoss:[16,16,16],mse:16,residuals:[]};
}
function configOf(o={}){
 const fee=o.feePerSide===undefined?.008:o.feePerSide;
 if(!finite(fee)||fee<0||fee>=.1)throw Error("INVALID_FEE");
 const z=o.confidenceZ===undefined?.35:o.confidenceZ;
 if(!finite(z)||z<0||z>3)throw Error("INVALID_CONFIDENCE");
 const minLabels=o.minMaturedLabels===undefined?6:o.minMaturedLabels;
 if(!Number.isInteger(minLabels)||minLabels<2||minLabels>100)throw Error("INVALID_MIN_LABELS");
 const riskBudget=o.maxHypotheticalDownsidePct??null;
 if(riskBudget!==null&&(!finite(riskBudget)||riskBudget<=0||riskBudget>=100))
   throw Error("INVALID_RISK_BUDGET");
 return {feePerSide:fee,confidenceZ:z,minMaturedLabels:minLabels,
   maxHypotheticalDownsidePct:riskBudget,
   skipLegacy:!!o.skipLegacy,skipFuzzy:!!o.skipFuzzy,
   skipMLP:!!o.skipMLP,skipAdaptiveMemory:!!o.skipAdaptiveMemory,
   researchOnly:true,liveTrade:false};
}
function make(o={}){
 const cfg=configOf(o),heads={ENTRY:{},EXIT:{}};
 for(const act of ["ENTRY","EXIT"])for(const h of HORIZONS)heads[act][h]=newHead();
 return {version:VERSION,config:cfg,heads,
  memory:{trend:0,stress:0,trendW:[0,0,0],stressW:[0,0,0],
    trendAcc:[.01,.01,.01],stressAcc:[.01,.01,.01]},
  centers:[[-1,-1,1,-.8],[-.5,-.2,.6,-.4],[0,0,.2,0],
    [.5,.2,.5,.4],[1,1,.8,.9]],
  market:{lastQuoteAt:null,lastSignalAt:null,lastPrice:null,
    moments:{n:0,mean:0,m2:0},surpriseEma:0},
  queue:[],pending:[],seq:0,lastOriginByH:{},
  learning:{matured:0,missing:0,byH:{},gateUpdates:0,centerUpdates:0},
  risk:{lambda:0,observations:0,model:newLinear(),modelObservations:0}};
}
function weightedCenters(centers,z){
 const distances=centers.map(c=>c.reduce((s,v,i)=>s+(z[i]-v)**2,0));
 return softmax(distances.map(v=>-v/2));
}
function modelInput(s,ob){
 if(!ob||typeof ob!=="object")throw Error("BAD_OBSERVATION");
 const asof=time(ob.asof),featureKnownAt=time(ob.featureAvailableAt);
 if(featureKnownAt>asof)throw Error("FUTURE_FEATURE_BLOCKED");
 if(s.market.lastSignalAt!==null&&asof<=s.market.lastSignalAt)
   throw Error("NONMONOTONE_SIGNAL");
 if(s.market.lastQuoteAt!==null&&asof<s.market.lastQuoteAt)
   throw Error("SIGNAL_BEFORE_ALREADY_INGESTED_QUOTE");
 const f=ob.market||{};
 for(const k of ["r4","r1","r3"]){if(!finite(f[k]))throw Error("MISSING_CORE_FEATURE_"+k);}
 for(const k of ["rv","dd","nq6"]){if(f[k]!=null&&!finite(f[k]))throw Error("NONFINITE_FEATURE_"+k);}
 const events=ob.events||[];
 if(!Array.isArray(events))throw Error("BAD_EVENTS");
 let eventScore=0;
 for(const e of events){
   if(e?.verifiedFirstPublication!==true)throw Error("UNVERIFIED_EVENT_BLOCKED");
   if(time(e.firstAvailableAt)>asof)throw Error("FUTURE_EVENT_BLOCKED");
   if(!finite(e.score)||e.score< -1||e.score>1)throw Error("BAD_EVENT_SCORE");
   eventScore+=e.score;
 }
 let legacy14=0,legacy56=0;
 if(ob.legacy&&!s.config.skipLegacy){
   if(time(ob.legacy.availableAt)>asof)throw Error("FUTURE_LEGACY_BLOCKED");
   if(!finite(ob.legacy.net14)||!finite(ob.legacy.net56))
     throw Error("INVALID_LEGACY");
   legacy14=bounded(ob.legacy.net14,10);legacy56=bounded(ob.legacy.net56,15);
 }
 const ret=bounded(f.r4,3),r1=bounded(f.r1,6),r3=bounded(f.r3,10),
  rv=bounded(f.rv,3),dd=bounded(f.dd,6),nq=bounded(f.nq6,5);
 const m=s.memory,gateX=[1,rv,Math.max(0,-ret)];
 const gT=s.config.skipAdaptiveMemory?.7:sigmoid(dot(m.trendW,gateX));
 const gS=s.config.skipAdaptiveMemory?.7:sigmoid(dot(m.stressW,gateX));
 const trendCandidate=Math.tanh((r1+r3)/2);
 const stressCandidate=Math.tanh(Math.max(0,-ret)+Math.max(0,rv)/2);
 const oldT=m.trend,oldS=m.stress;
 const trend=gT*oldT+(1-gT)*trendCandidate,
   stress=gS*oldS+(1-gS)*stressCandidate;
 const dTrend=gateX.map(x=>s.config.skipAdaptiveMemory?0:
   (oldT-trendCandidate)*gT*(1-gT)*x);
 const dStress=gateX.map(x=>s.config.skipAdaptiveMemory?0:
   (oldS-stressCandidate)*gS*(1-gS)*x);
 const mom=s.market.moments,sd=mom.n>=8?
   Math.sqrt(Math.max(.01,mom.m2/(mom.n-1))):1;
 const zScore=(ret-mom.mean)/sd;
 const changeSurprise=minmax(Math.abs(zScore),0,5);
 // As-of filter: first produce the feature using strictly prior moments,
 // then include this known observation in the state.
 mom.n++;const delta=ret-mom.mean;mom.mean+=delta/mom.n;
 mom.m2+=delta*(ret-mom.mean);
 s.market.surpriseEma=.9*s.market.surpriseEma+.1*changeSurprise;
 m.trend=trend;m.stress=stress;
 const x=[1,ret,r1,r3,rv,dd,nq,f.nq6==null?0:1,
  trend,stress,changeSurprise/5,minmax(eventScore,-3,3),
  legacy14,legacy56];
 const fuzzyInput=[r1,r3,rv,trend];
 const memberships=weightedCenters(s.centers,fuzzyInput);
 return {at:asof,x,fuzzyInput,memberships,dTrend,dStress,
   eventCount:events.length,legacyUsed:!!ob.legacy&&!s.config.skipLegacy,
   source:"MARKET_FEATURES_POINT_IN_TIME"};
}
function linearForward(m,x){return dot(m.w,x);}
function fuzzyForward(m,x,p){
 return p.reduce((sum,w,k)=>sum+w*dot(m.w[k],x),0);
}
function mlpForward(m,x){
 const h=m.w1.map((w,j)=>Math.tanh(dot(w,x)+m.b1[j]));
 return {y:dot(m.w2,h)+m.b2,h};
}
function modelPredict(s,act,h,snap){
 const m=s.heads[act][h],x=snap.x,phi=snap.memberships;
 const raw=[linearForward(m.linear,x),fuzzyForward(m.fuzzy,x,phi),
    mlpForward(m.mlp,x).y];
 const enabled=[true,!s.config.skipFuzzy,!s.config.skipMLP];
 const logw=m.logExpertWeight.map((v,i)=>enabled[i]?v:-1e9);
 const weights=softmax(logw),mean=dot(weights,raw);
 const q=linearForward(m.q,x);
 // Result is per-horizon, cost-adjusted action premium, NOT a raw price
 // prediction, and never mixed across different label horizons.
 const uncertainty=Math.sqrt(Math.max(.01,m.mse));
 const ciPenalty=s.config.confidenceZ*uncertainty/Math.sqrt(Math.max(1,m.n));
 const netScore=mean-ciPenalty;
 const lowerTail=m.n>=s.config.minMaturedLabels?Math.min(q,mean):null;
 return {action:act,h,n:m.n,mean,netScore,ciPenalty,lowerTail,
    raw,weights,uncertainty,feePerSide:s.config.feePerSide,
    scoreUnit:"LOG_WEALTH_PERCENT_POINTS"};
}
function choose(s,snap,position){
 if(!["CASH","GOLD"].includes(position))throw Error("INVALID_POSITION");
 const act=position==="CASH"?"ENTRY":"EXIT";
 const allowed=position==="CASH"?[28,56]:[1,3,7,28,56];
 const candidates=allowed.map(h=>modelPredict(s,act,h,snap));
 const ready=candidates.filter(c=>c.n>=s.config.minMaturedLabels);
 // Completed finite-horizon switching premia are different investments.
 // Compare the log-wealth advantage PER CALENDAR DAY rather than selecting
 // whichever raw cumulative return has the longest horizon.
 // This is an explicit time-normalization heuristic, not Bellman optimality.
 const selected=ready.sort((a,b)=>b.netScore/b.h-a.netScore/a.h)[0]||null;
 let score=selected===null?null:selected.netScore/selected.h;
 let goldDownside28=null,riskAdjustmentPerDay=0;
 if(selected&&s.config.maxHypotheticalDownsidePct!==null){
   // Lambda penalizes CASH->GOLD and encourages GOLD->CASH when the same
   // 28-day gold downside *holding* risk breaches the supplied budget.
   // Never penalize a protective EXIT for exposure it eliminates.
   goldDownside28=Math.max(0,dot(s.risk.model.w,snap.x));
   const excess=Math.max(0,goldDownside28-s.config.maxHypotheticalDownsidePct);
   riskAdjustmentPerDay=s.risk.lambda*excess/28;
   score+=act==="ENTRY"?-riskAdjustmentPerDay:riskAdjustmentPerDay;
 }
 const switchAsset=selected!==null&&score>0;
 return {position,target:switchAsset?(position==="CASH"?"GOLD":"CASH"):position,
   action:switchAsset?(position==="CASH"?"BUY":"SELL"):"WAIT",
   selectedHorizon:selected?.h??null,score,scoreUnit:"LOG_WEALTH_PERCENT_POINTS_PER_DAY",
   goldDownside28,riskAdjustmentPerDay,selected: selected?{...selected}:null,
   candidates,reasons:!selected?["INSUFFICIENT_MATURED_EPISODES"]:
     switchAsset?["POSITIVE_COSTED_ACTION_PREMIUM"]:
        ["COST_AND_UNCERTAINTY_DOMINATE"],
   costAlreadyIncludedInTarget:true,provenProfitable:false};
}
function adamStep(w,acc,grad,lr=.06){
 for(let i=0;i<w.length;i++){
   const g=minmax(grad[i],-30,30);
   acc[i]+=g*g;w[i]=minmax(w[i]-lr*g/Math.sqrt(acc[i]),-40,40);
 }
}
function updateMLP(m,x,y,lr=.035){
 const f=mlpForward(m,x),err=minmax(f.y-y,-40,40),
   oldW2=m.w2.slice();
 const gradW2=f.h.map(h=>err*h),gradB2=err;
 const gradW1=f.h.map((h,j)=>x.map(v=>err*oldW2[j]*(1-h*h)*v));
 const gradB1=f.h.map((h,j)=>err*oldW2[j]*(1-h*h));
 adamStep(m.w2,m.a2,gradW2,lr);
 for(let j=0;j<HIDDEN;j++){
   adamStep(m.w1[j],m.a1[j],gradW1[j],lr/2);
   const g=gradB1[j];m.ab1[j]+=g*g;
   m.b1[j]=minmax(m.b1[j]-lr/2*g/Math.sqrt(m.ab1[j]),-10,10);
 }
 m.ab2+=gradB2*gradB2;
 m.b2=minmax(m.b2-lr*gradB2/Math.sqrt(m.ab2),-30,30);
}
function updateHead(s,act,h,snapshot,target){
 const head=s.heads[act][h],x=snapshot.x,phi=snapshot.memberships;
 const p=snapshot.predictions[act][h],err=minmax(p.mean-target,-40,40);
 // Use the pre-update memory coefficients when computing the local
 // derivative. Using post-SGD linear weights is temporally inconsistent.
 const preUpdateMemoryWeights=[head.linear.w[MEM_T],head.linear.w[MEM_S]];
 // Matured, action-specific prediction losses update the mixture.
 const weights=head.logExpertWeight;
 for(let i=0;i<3;i++){
   const e=minmax(p.raw[i]-target,-30,30),loss=e*e;
   head.expertLoss[i]=head.n===0?loss:.94*head.expertLoss[i]+.06*loss;
   // Bounded EMA reliability prevents permanent expert starvation after a
   // temporary regime change. Disabled experts get zero mixture mass.
   weights[i]=-Math.min(12,head.expertLoss[i]/16);
 }
 const mw=Math.max(...weights);
 for(let i=0;i<3;i++)weights[i]-=mw;
 const lin=head.linear,el=minmax(dot(lin.w,x)-target,-40,40);
 const den=1+x.reduce((a,v)=>a+v*v,0);
 adamStep(lin.w,lin.acc,x.map(v=>el*v/den),.12);
 if(!s.config.skipFuzzy){
   const fuzzy=head.fuzzy,ferr=minmax(fuzzyForward(fuzzy,x,phi)-target,-40,40);
   // Supervised center gradient for normalized Gaussian-like fuzzy rules:
   // dPrediction/dCenter_ij = phi_i*(rule_i-fuzzyPrediction)*(z_j-c_ij).
   // An unsupervised centroid drift does NOT minimize forecasting error.
   if(h===1&&act==="ENTRY"){
     const z=snapshot.fuzzyInput,fuzzyPred=fuzzyForward(fuzzy,x,phi);
     const rules=fuzzy.w.map(w=>dot(w,x));
     const steps=[];
     for(let i=0;i<R;i++)for(let j=0;j<z.length;j++){
       const g=ferr*phi[i]*(rules[i]-fuzzyPred)*(z[j]-s.centers[i][j]);
       const delta=-.035*minmax(g/den,-10,10);
       steps.push([i,j,delta]);
     }
     if(steps.some(([i,j,delta])=>s.centers[i][j]+delta!==s.centers[i][j])){
       for(const [i,j,delta] of steps)s.centers[i][j]=minmax(
         s.centers[i][j]+delta,-3,3);
       s.learning.centerUpdates++;
     }
   }
   for(let i=0;i<R;i++)adamStep(fuzzy.w[i],fuzzy.acc[i],
       x.map(v=>ferr*phi[i]*v/den),.09);
 }
 if(!s.config.skipMLP)updateMLP(head.mlp,x,target);
 const q=head.q,qf=linearForward(q,x);
 // Pinball loss at alpha=0.1 for learned downside quantile.
 const qError=qf>target?.9:-.1;
 adamStep(q.w,q.acc,x.map(v=>qError*v/den),.05);
 head.mse=head.n===0?err*err:.95*head.mse+.05*err*err;
 head.residuals.push(target-p.mean);if(head.residuals.length>120)head.residuals.shift();
 head.n++;
 if(h===1&&act==="ENTRY"&&!s.config.skipAdaptiveMemory){
   // Local recurrent derivative; not full backpropagation through time.
   for(const [name,index,deriv] of [
     ["trend",MEM_T,snapshot.dTrend],["stress",MEM_S,snapshot.dStress]]){
     const m=s.memory,g=minmax(err*preUpdateMemoryWeights[index===MEM_T?0:1],-40,40);
     const w=name==="trend"?m.trendW:m.stressW;
     const acc=name==="trend"?m.trendAcc:m.stressAcc;
     adamStep(w,acc,deriv.map(v=>g*v/den),.025);
   }
   s.learning.gateUpdates++;
 }

}
function startEpisodes(s,pending,at,price){
 const started=[];
 for(const h of HORIZONS){
   const spacing=(h<=7?h:h/2)*DAY,last=s.lastOriginByH[h];
   if(last!=null&&at-last<spacing)continue;
   s.lastOriginByH[h]=at;
   s.queue.push({h,origin:pending.id,signalAt:pending.at,entryAt:at,
     dueAt:at+h*DAY,entryPrice:price,minRel:0,maxRel:0,
     snapshot:pending.snapshot});
   started.push(h);
 }
 return started;
}
function updateRisk(s,ep,worstLoss){
 if(s.config.maxHypotheticalDownsidePct===null||ep.h!==28)return;
 // Dual gradient for a fixed investor-specified *hypothetical* loss budget.
 const budget=s.config.maxHypotheticalDownsidePct;
 const model=s.risk.model,x=ep.snapshot.x;
 const delta=minmax(dot(model.w,x)-worstLoss,-40,40);
 const den=1+x.reduce((a,v)=>a+v*v,0);
 adamStep(model.w,model.acc,x.map(v=>delta*v/den),.10);
 s.risk.modelObservations++;
 s.risk.lambda=minmax(s.risk.lambda+.003*(worstLoss-budget),0,3);
 s.risk.observations++;
}
function settle(s,ep,price,at){
 if(!(at>=ep.dueAt&&at>ep.entryAt))throw Error("EARLY_OUTCOME");
 const fee=2*100*Math.log(1-s.config.feePerSide);
 const gross=100*Math.log(price/ep.entryPrice);
 const entry=gross+fee,exit=-gross+fee;
 const label={h:ep.h,origin:ep.origin,signalAt:ep.signalAt,
   entryAt:ep.entryAt,knownAt:at,gross,entry,exit,
   worstHoldingLoss:-ep.minRel,worstExitMissedRise:ep.maxRel};
 updateHead(s,"ENTRY",ep.h,ep.snapshot,entry);
 updateHead(s,"EXIT",ep.h,ep.snapshot,exit);
 updateRisk(s,ep,label.worstHoldingLoss);
 s.learning.matured++;s.learning.byH[ep.h]=(s.learning.byH[ep.h]||0)+1;
 return label;
}
function receiveQuote(s,quote){
 if(!finite(quote?.price)||quote.price<=0)throw Error("BAD_BANK_PROXY_PRICE");
 const at=time(quote.at),prev=s.market.lastQuoteAt;
 if(prev!==null&&at<=prev)throw Error("NONMONOTONE_QUOTE");
 s.market.lastQuoteAt=at;s.market.lastPrice=quote.price;
 const matured=[],remaining=[];
 for(const ep of s.queue){
   const change=100*Math.log(quote.price/ep.entryPrice);
   ep.minRel=Math.min(ep.minRel,change);ep.maxRel=Math.max(ep.maxRel,change);
   if(at>=ep.dueAt){
     if(at-ep.dueAt>78*HOUR){
       s.learning.missing++;
     }else matured.push(settle(s,ep,quote.price,at));
   }else remaining.push(ep);
 }
 s.queue=remaining;
 const fills=[],keep=[];
 for(const p of s.pending){
   if(at<=p.at){keep.push(p);continue;}
   if(at-p.at>96*HOUR){s.learning.missing++;continue;}
   if(quote.isBankCheckpoint!==true){keep.push(p);continue;}
   const eligible=startEpisodes(s,p,at,quote.price);
   fills.push({id:p.id,signalAt:new Date(p.at).toISOString(),
     fillAt:new Date(at).toISOString(),price:quote.price,
     intendedAction:p.decision.action,intendedPosition:p.decision.target,
     startedLearningHorizons:eligible,notAnActualBankOrder:true});
 }
 s.pending=keep;
 return {asof:quote.at,matured,fills,stillOpen:s.queue.length,
   readySignals:s.pending.length,decisionMade:false};
}
function signal(s,ob){
 if(s.pending.length>0)throw Error("PENDING_SIGNAL_AWAITING_BANK_CHECKPOINT");
 if(!ob||!["CASH","GOLD"].includes(ob.position))
   throw Error("INVALID_POSITION");
 const snap=modelInput(s,ob);
 snap.predictions={ENTRY:{},EXIT:{}};
 for(const act of ["ENTRY","EXIT"])
   for(const h of HORIZONS)snap.predictions[act][h]=modelPredict(s,act,h,snap);
 const d=choose(s,snap,ob.position);
 s.seq++;s.market.lastSignalAt=snap.at;
 const id="V15-"+s.seq;
 s.pending.push({id,at:snap.at,decision:{action:d.action,target:d.target},
   snapshot:JSON.parse(JSON.stringify(snap))});
 return {id,asof:ob.asof,decision:d,
   provenance:{featureKnownAt:ob.featureAvailableAt,eventCount:snap.eventCount,
     legacyUsed:snap.legacyUsed,validatedPointInTime:true},
   training:{queued:s.queue.length,matured:s.learning.matured},
   orderSent:false,liveTradingAuthorized:false};
}
function checkpoint(s){return JSON.parse(JSON.stringify(s));}
function restore(payload){
 const v=typeof payload==="string"?JSON.parse(payload):payload;
 if(!v||v.version!==VERSION||!v.heads||!v.memory||!v.market)
   throw Error("INCOMPATIBLE_MODEL_CHECKPOINT");
 const obj=JSON.parse(JSON.stringify(v));
 configOf(obj.config);return obj;
}
module.exports={VERSION,HOUR,DAY,HORIZONS,FEATURE_NAMES,make,signal,receiveQuote,
 modelInput,modelPredict,choose,settle,checkpoint,restore};
