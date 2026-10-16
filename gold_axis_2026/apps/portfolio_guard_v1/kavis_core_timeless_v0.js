"use strict";
/*
 KAVIS CORE V0: Timeless state/event encoder + delayed multi-horizon
 net-cost optimal-switch prototype. NOT trained; NO claims of alpha.
 Absolute dates are used ONLY for availability, maturation and audit.
 Time-based constants are elapsed horizons, not month/year identities.
*/
const FAMILIES=Object.freeze(["G01_RATES_USD","G02_TRADE_TARIFF",
 "G03_GEOPOLITICS","G04_PHYSICAL_CB","G05_FINANCIAL_STRESS",
 "G06_LIQUIDATION","G07_UNKNOWN"]);
const SIGNALS=Object.freeze([
 "goldR1hPct","goldR4hPct","goldR1dPct","goldVol1dPct",
 "goldDrawdownPct","silverR4hPct","platinumR4hPct",
 "palladiumR4hPct","nasdaqR4hPct","sp500R4hPct",
 "usdR4hPct","bondR4hPct","oilR4hPct","etfFlowZ",
 "liquidityStressZ"
]);
const HORIZONS=Object.freeze([240,1440,4320,10080]); // elapsed minutes, not calendar dates
const FEE=.008,LEGS_COST_PCT=-200*Math.log(1-FEE);
const NFEATURES=1+SIGNALS.length+4+FAMILIES.length+3;
const cap=(v,l,h)=>Math.max(l,Math.min(h,v));
const number=v=>typeof v==="number"&&Number.isFinite(v);
const numeric=v=>number(v)?v:null;
const stamp=s=>{const t=Date.parse(s);if(!Number.isFinite(t))throw Error("CORE_BAD_TIMESTAMP");return t;};
const atLeast=(x,y)=>{if(x<y)throw Error("CORE_FUTURE_INFORMATION");};
const hashlessCopy=x=>JSON.parse(JSON.stringify(x));
function encode(ob){
 if(!ob||typeof ob!=="object")throw Error("CORE_BAD_OBSERVATION");
 const now=stamp(ob.asof);
 if(!number(ob.price)||ob.price<=0)throw Error("CORE_BAD_PRICE");
 if(!ob.priceAvailableAt)throw Error("CORE_NO_PRICE_LINEAGE");
 atLeast(now,stamp(ob.priceAvailableAt));
 const vec=[1],missing=[];
 for(const key of SIGNALS){
  const z=ob.market?.[key];
  if(z==null){vec.push(0);missing.push(key);continue;}
  if(!number(z.value)||!z.availableAt)throw Error("CORE_INVALID_MARKET_"+key);
  atLeast(now,stamp(z.availableAt));
  vec.push(cap(z.value/4,-3,3));
 }
 // MISSINGNESS is explicit. Zero-mapped unavailable signals do not masquerade as observations.
 const weights={"cross":0,"metal":0,"macro":0,"price":0};
 for(const key of missing){
  if(/silver|platinum|palladium/.test(key))weights.metal++;
  else if(/gold/.test(key))weights.price++;
  else if(/nasdaq|sp500|etf/.test(key))weights.cross++;
  else weights.macro++;
 }
 vec.push(...["price","metal","cross","macro"].map(k=>weights[k]/SIGNALS.length));
 const family=Array(FAMILIES.length).fill(0);
 let signed=0,activity=0,count=0;
 for(const e of (ob.events??[])){
  if(!e||!e.firstAvailableAt||!FAMILIES.includes(e.mechanismFamily)||
    !number(e.signedSurprise)||!number(e.sourceConfidence)||
    e.sourceConfidence<0||e.sourceConfidence>1)throw Error("CORE_INVALID_EVENT");
  const published=stamp(e.firstAvailableAt);
  atLeast(now,published);
  // Age is relative; no month/year identity, headline text or event ID in features.
  const ageH=(now-published)/3600000;
  const decay=Math.exp(-ageH/48)*e.sourceConfidence;
  if(decay<1e-5)continue;
  family[FAMILIES.indexOf(e.mechanismFamily)]+=
    decay*cap(e.signedSurprise,-4,4);
  signed+=decay*cap(e.signedSurprise,-4,4);
  activity+=decay;count++;
 }
 vec.push(...family.map(z=>cap(z/4,-3,3)));
 vec.push(cap(signed/4,-3,3),cap(activity/4,0,3),cap(count/8,0,3));
 if(vec.length!==NFEATURES||vec.some(v=>!number(v)))
  throw Error("CORE_FEATURE_VECTOR_INVALID");
 return {x:vec,missing,quality:{available: SIGNALS.length-missing.length,
  missing:missing.length,eventsUsed:count}};
}
const dot=(a,b)=>a.reduce((s,z,i)=>s+z*b[i],0);
function head(h){
 return {h,wReturn:Array(NFEATURES).fill(0),
  wDown:Array(NFEATURES).fill(0),
  accReturn:Array(NFEATURES).fill(.01),
  accDown:Array(NFEATURES).fill(.01),
  n:0,mse:1,downMse:1,mae:0,labelsSkipped:0,updates:0,
  pending:[]};
}
function create(config={}){
 if(config.feePerSide!==undefined&&config.feePerSide!==FEE)
   throw Error("CORE_COST_PREREG_FROZEN");
 return {version:"KAVIS_CORE_TIMELESS_V0",feePerSide:FEE,
  constraints:{riskLambda:.2,uncertaintyLambda:.4,learningRate:.008,
    hedgeEta:.25,initialPriceFloor:1,maximumSlippagePct:null},
  heads:HORIZONS.map(head),
  lastTime:null,lastPrice:null,decisions:0,observations:0,
  totalMatured:0,totalNonzeroUpdates:0,missingData:0,
  portfolio:{cash:100,ounces:0,position:"CASH",lastNav:100,
    peak:100,maxDDPct:0,trades:0,feesPaidUSD:0},
  trades:[],audit:{droppedStaleLabels:0,causalRejected:0}};
}
function train(h,x,y,kind,step){
 const w=kind==="return"?h.wReturn:h.wDown,
  acc=kind==="return"?h.accReturn:h.accDown;
 const pred=dot(w,x),err=cap(pred-y,-50,50),norm=1+dot(x,x);
 let changed=false;
 for(let i=0;i<w.length;i++){
  const grad=cap(err*x[i]/norm,-50,50);
  acc[i]=Math.min(1e7,acc[i]+grad*grad);
  const next=cap(w[i]-step*grad/Math.sqrt(acc[i]),-25,25);
  changed||=Math.abs(next-w[i])>1e-13;
  w[i]=next;
 }
 return {error:err,changed};
}
function mature(s,now,price){
 const step=s.constraints.learningRate;
 for(const h of s.heads){
  for(const p of h.pending)p.pathMin=Math.min(p.pathMin,price);
  const remain=[];
  for(const p of h.pending){
   if(now<p.due){remain.push(p);continue;}
   const maxLateness=Math.max(30,h.h*.10)*60000;
   if(now-p.due>maxLateness){
    h.labelsSkipped++;s.audit.droppedStaleLabels++;continue;
   }
   const move=cap(100*Math.log(price/p.price),-30,30);
   const downside=cap(Math.max(0,100*Math.log(p.price/p.pathMin)),0,30);
   const ret=train(h,p.x,move,"return",step);
   const down=train(h,p.x,downside,"down",step);
   h.mse=h.n===0?ret.error**2:.95*h.mse+.05*ret.error**2;
   h.downMse=h.n===0?down.error**2:.95*h.downMse+.05*down.error**2;
   h.mae=(h.mae*h.n+Math.abs(ret.error))/(h.n+1);
   h.n++;h.updates++;s.totalMatured++;
   if(ret.changed||down.changed)s.totalNonzeroUpdates++;
  }
  h.pending=remain;
 }
}
function forecasts(s,x){
 const ready=s.heads.filter(h=>h.n>=8);
 if(!ready.length)return {ready:false,regime:null,netEdge:null,
  valueByHorizon:[]};
 const exps=s.heads.map(h=>h.n>=8?
   Math.exp(-s.constraints.hedgeEta*Math.sqrt(h.mse)):0);
 const z=exps.reduce((a,b)=>a+b,0);
 const values=s.heads.map((h,j)=>{
  const weight=z>0?exps[j]/z:0,
    mean=cap(dot(h.wReturn,x),-30,30),
    downside=cap(dot(h.wDown,x),0,30),
    error=Math.sqrt(Math.max(0,h.mse)),
    advantage=mean-s.constraints.riskLambda*downside;
  return {horizonMinutes:h.h,n:h.n,weight,meanPct:mean,
    downsidePct:downside,uncertaintyPct:error,
    expectedHoldGoldValuePct:advantage};
 });
 // Risk and fee values are both in percentage-log-wealth units.
 const goldUtility=values.reduce((sum,v)=>
   sum+v.weight*v.expectedHoldGoldValuePct,0);
 const uncert=values.reduce((sum,v)=>
   sum+v.weight*v.uncertaintyPct,0);
 return {ready:true,goldUtilityPct:goldUtility,
   uncertaintyPct:uncert,values,
   lowerBuyingEdge:goldUtility-LEGS_COST_PCT-s.constraints.uncertaintyLambda*uncert,
   lowerSellingEdge:-goldUtility-LEGS_COST_PCT-s.constraints.uncertaintyLambda*uncert};
}
function observe(s,ob){
 if(s.version!=="KAVIS_CORE_TIMELESS_V0")throw Error("CORE_BAD_VERSION");
 const now=stamp(ob.asof);
 if(s.lastTime!==null&&now<=s.lastTime)throw Error("CORE_NONMONOTONIC");
 const {x,missing,quality}=encode(ob);
 mature(s,now,ob.price);
 const f=forecasts(s,x),position=s.portfolio.position;
 const lowerEdge=position==="CASH"?f.lowerBuyingEdge:f.lowerSellingEdge;
 const action=f.ready&&lowerEdge>0?
   (position==="CASH"?"BUY":"SELL"):"WAIT";
 for(const h of s.heads)h.pending.push({
  due:now+h.h*60000,x:x.slice(),price:ob.price,
  pathMin:ob.price});
 s.lastTime=now;s.lastPrice=ob.price;
 s.observations++;s.decisions++;
 s.missingData+=missing.length;
 mark(s,ob.price);
 return {action,sourceTime:ob.asof,modelVersion:s.version,
  positionBefore:position,
  lowerSwitchAdvantagePct:f.ready?lowerEdge:null,
  costTwoLegPct:LEGS_COST_PCT,
  learningLabels:s.totalMatured,quality,
  forecast:f};
}
function mark(s,price){
 const p=s.portfolio,nav=p.cash+p.ounces*price*(1-FEE);
 p.lastNav=nav;p.peak=Math.max(p.peak,nav);
 p.maxDDPct=Math.max(p.maxDDPct,100*(1-nav/p.peak));
}
function fill(s,decision,fill){
 if(!decision||!["BUY","SELL","WAIT"].includes(decision.action))
  throw Error("CORE_INVALID_INTENDED_ACTION");
 if(decision.modelVersion!==s.version||
   stamp(decision.sourceTime)!==s.lastTime)
  throw Error("CORE_DECISION_STATE_MISMATCH");
 if(!fill||!number(fill.price)||fill.price<=0||
    !fill.at||!fill.quoteFirstAvailableAt)
   throw Error("CORE_INVALID_BANK_QUOTE");
 const at=stamp(fill.at),available=stamp(fill.quoteFirstAvailableAt);
 if(at<s.lastTime||available>at)throw Error("CORE_FUTURE_BANK_QUOTE");
 const p=s.portfolio,prior=p.position,act=decision.action;
 if(act==="BUY"&&prior!=="CASH"||
    act==="SELL"&&prior!=="GOLD")
  throw Error("CORE_POSITION_MISMATCH");
 if(act==="BUY"){
  p.feesPaidUSD+=p.cash*FEE;
  p.ounces=p.cash*(1-FEE)/fill.price;
  p.cash=0;p.position="GOLD";p.trades++;
 }else if(act==="SELL"){
  p.feesPaidUSD+=p.ounces*fill.price*FEE;
  p.cash=p.ounces*fill.price*(1-FEE);
  p.ounces=0;p.position="CASH";p.trades++;
 }
 mark(s,fill.price);
 if(act!=="WAIT")s.trades.push({
  at:fill.at,action:act,midPrice:fill.price,
  feePerSide:FEE,resultNAV:p.lastNav,lowerAdvantagePct:
    decision.lowerSwitchAdvantagePct});
 return {action:act,positionAfter:p.position,capitalNetLiquidation:p.lastNav,
  trades:p.trades};
}
function checkpoint(s){
 if(s.version!=="KAVIS_CORE_TIMELESS_V0")throw Error("CORE_BAD_VERSION");
 return hashlessCopy(s);
}
function restore(obj){
 const s=hashlessCopy(obj);
 if(s?.version!=="KAVIS_CORE_TIMELESS_V0"||
   !Array.isArray(s.heads)||s.heads.length!==HORIZONS.length||
   s.heads.some((h,i)=>h.h!==HORIZONS[i]||
      !Array.isArray(h.wReturn)||h.wReturn.length!==NFEATURES||
      !Array.isArray(h.wDown)||h.wDown.length!==NFEATURES||
      h.wReturn.some(z=>!number(z))||h.wDown.some(z=>!number(z)))||
   !s.portfolio||!["CASH","GOLD"].includes(s.portfolio.position)||
   !number(s.portfolio.lastNav)||s.portfolio.lastNav<=0||
   !number(s.portfolio.cash)||s.portfolio.cash<0||
   !number(s.portfolio.ounces)||s.portfolio.ounces<0)
   throw Error("CORE_CORRUPT_CHECKPOINT");
 return s;
}
module.exports={FAMILIES,SIGNALS,HORIZONS,NFEATURES,FEE,LEGS_COST_PCT,
 encode,create,observe,forecasts,fill,checkpoint,restore,mature};
