"use strict";
/**
 * Chronological XAU trading ANN evidence protocol:
 * - labels: actual next eligible TR 12:00 entry (after TR 09:00 signal),
 *   liquidation at earliest eligible bank 09/12/15 local >= 96h / 336h;
 * - each label is NET: (1-.008)^2 * exitMID/entryMID - 1;
 * - only labels with both exits STRICTLY before training cutoff are fed to ANN.
 * - no lookahead at fill; signal at 09TR, fill at NEXT bank checkpoint.
 * - all strategies are RESEARCH ONLY, not authorized for banking.
 */
const {loadFullRows}=require("./v8_regret_engine");
const ANN=require("./v11_ann_mlp");
const FEE=.008,HR=3600000,DAY=24*HR;
function date(t){return Date.parse(t);}
function isBank(r){return [6,9,12].includes(new Date(r.tt).getUTCHours());}
function isOrigin(r){return new Date(r.tt).getUTCHours()===6;}
function upperBound(bank,t){
 let lo=0,hi=bank.length;
 while(lo<hi){const mid=(lo+hi)>>1;
  if(bank[mid].ts<=t)lo=mid+1;else hi=mid;
 }
 return lo<bank.length?bank[lo]:null;
}
function atOrAfter(bank,t){
 let lo=0,hi=bank.length;
 while(lo<hi){const mid=(lo+hi)>>1;
  if(bank[mid].ts<t)lo=mid+1;else hi=mid;
 }
 return lo<bank.length?bank[lo]:null;
}
function inputs(rows,i){
 const r=rows[i],at=j=>j>=0&&rows[j].c>0?rows[j].c:null;
 const pct=(old)=>old==null?0:100*(r.c/old-1);
 const finite=(v)=>Number.isFinite(v)?v:0;
 return [
  finite(r.r4),finite(r.r1),finite(r.r3),finite(r.rv),
  finite(r.ds),finite(r.eff),finite(r.loc),finite(r.dd),
  finite(r.nq6),finite(r.zn1),
  Number.isFinite(r.nq6)?1:0,Number.isFinite(r.zn1)?1:0,
  pct(at(i-6)),pct(at(i-40))
 ];
}
function dataset(rows){
 const bank=rows.filter(isBank).map(x=>({...x,ts:date(x.tt)}));
 const samples=[];
 for(let i=0;i<rows.length;i++){
  const row=rows[i];if(!isOrigin(row))continue;
  const ts=date(row.tt),entry=upperBound(bank,ts);
  if(!entry||entry.ts-ts>72*HR)continue;
  const exit4=atOrAfter(bank,entry.ts+96*HR),exit14=atOrAfter(bank,entry.ts+336*HR);
  if(!exit4||!exit14||exit4.ts-entry.ts-96*HR>78*HR||
     exit14.ts-entry.ts-336*HR>78*HR)continue;
  const y=[exit4,exit14].map(ex=>100*((1-FEE)**2*ex.p/entry.p-1));
  samples.push({at:row.tt,ts,entryUTC:entry.tt,entryTs:entry.ts,
   exit4UTC:exit4.tt,exit4Ts:exit4.ts,
   exit14UTC:exit14.tt,exit14Ts:exit14.ts,
   priceAtEntry:entry.p,y,features:inputs(rows,i)});
 }
 const byOrigin=new Map(samples.map(s=>[s.at,s]));
 return {bank,samples,byOrigin,records:rows.length,sampleCount:samples.length};
}
function chronologicalTraining(ds,cutoff){
 const t=date(cutoff);
 const train=ds.samples.filter(s=>s.exit14Ts<t&&s.exit4Ts<t&&s.ts<t);
 if(train.some(s=>s.exit14Ts>=t))throw Error("FUTURE_LABEL_IN_TRAIN");
 return train;
}
const POLICIES={
 netPositive:{buyNet14:0,stopNet4:-3.2,sellNet14:-1.8,
   minHoldHours:96,liquidateRisk:false,monthlyRetrain:false},
 cautious:{buyNet14:1.5,stopNet4:-4.5,sellNet14:-2.6,
   minHoldHours:96,liquidateRisk:false,monthlyRetrain:false},
 shockGuard:{buyNet14:1.5,stopNet4:-4.5,sellNet14:-2.6,
   minHoldHours:96,liquidateRisk:true,monthlyRetrain:false},
 adaptiveMonthly:{buyNet14:1.5,stopNet4:-4.5,sellNet14:-2.6,
   minHoldHours:96,liquidateRisk:true,monthlyRetrain:true}
};
function simulate(ds,opts={}){
 const cutoff=opts.start||"2026-02-02T06:00:00Z",
  stop=opts.end||"2026-09-30T12:00:00Z",initial=opts.initial??119.753917;
 const policyName=opts.policy||"netPositive",policy=POLICIES[policyName];
 if(!policy)throw Error("INVALID_ANN_POLICY");
 const start=date(cutoff),end=date(stop);
 let train=chronologicalTraining(ds,cutoff);
 let ann=ANN.fit(train,{seed:17,epochs:75,lr:.006});
 let trainUpdates=[{asOf:cutoff,maturedN:train.length,lastTrainingOrigin:train.at(-1)?.at||null,
   bestEpoch:ann.bestEpoch,validationMAE14Pct:ann.validationMAE14Pct}];
 let month=new Date(start+3*HR).toISOString().slice(0,7);
 let cash=initial,ounces=0,pending=null,entryTime=-Infinity,lastSale=-Infinity;
 let trades=[],signals=[],monthly=[],predictions=[],seenOrigins=0;
 // Parse source-derived point-in-time evidence only after close of today's 09TR bar.
 for(const row of ds.bank){
  const t=row.ts;
  if(t<start||t>end)continue;
  const currentMonth=new Date(t+3*HR).toISOString().slice(0,7);
  if(policy.monthlyRetrain&&currentMonth!==month){
   month=currentMonth;
   const newTrain=chronologicalTraining(ds,row.tt);
   if(newTrain.length>train.length+1){
    train=newTrain;ann=ANN.fit(train,{seed:17,epochs:75,lr:.006});
    trainUpdates.push({asOf:row.tt,maturedN:train.length,
      lastTrainingOrigin:train.at(-1)?.at||null,bestEpoch:ann.bestEpoch,
      validationMAE14Pct:ann.validationMAE14Pct});
   }
  }
  // Apply only a signal issued at a STRICTLY earlier bank checkpoint.
  if(pending&&pending.ts<t){
   if(pending.side==="BUY"&&!ounces){
    ounces=cash*(1-FEE)/row.p;cash=0;entryTime=t;
    trades.push({side:"BUY",at:row.tt,asOf:pending.at,mid:row.p,
      why:pending.why});
   }else if(pending.side==="SELL"&&ounces){
    cash=ounces*row.p*(1-FEE);ounces=0;lastSale=t;
    trades.push({side:"SELL",at:row.tt,asOf:pending.at,mid:row.p,
      why:pending.why});
   }
   pending=null;
  }
  const nav=cash+ounces*row.c*(1-FEE);
  if(!monthly.length||monthly.at(-1).month!==currentMonth)
   monthly.push({month:currentMonth,finalUSD:nav,position:ounces?"GOLD":"CASH"});
  else{monthly.at(-1).finalUSD=nav;monthly.at(-1).position=ounces?"GOLD":"CASH";}
  if(!isOrigin(row))continue;
  const origin=ds.byOrigin.get(row.tt);
  // Even if a label is missing past dataset end, input is still as-of.
  const feat=origin?.features||inputs(opts.rawRows||[],0);
  if(!origin){continue;}
  const prediction=ANN.predict(ann,feat);
  const shock=row.r4!=null&&row.r4<=-1&&row.nq6!=null&&row.nq6<=-1;
  const longOK=prediction.net14>policy.buyNet14&&prediction.net4> -4;
  const out=prediction.net4<policy.stopNet4||
    prediction.net14<policy.sellNet14||(policy.liquidateRisk&&shock);
  let desired=ounces?"GOLD":"CASH",why="NO_COSTED_EDGE";
  if(!ounces&&t-lastSale>=96*HR&&longOK&&!shock){
   desired="GOLD";why="ANN_14D_NET_OPPORTUNITY";
  }else if(ounces&&((t-entryTime>=policy.minHoldHours*HR&&out)||(policy.liquidateRisk&&shock))){
   desired="CASH";why=shock&&policy.liquidateRisk?"XAU_NQ_STRESS":"ANN_4D_DOWNSIDE";
  }
  const side=desired==="GOLD"?"BUY":"SELL";
  predictions.push({at:row.tt,net4:prediction.net4,net14:prediction.net14,
    actual4:origin.y[0],actual14:origin.y[1],
    regime:shock?"STRESS":"OTHER",wasHolding:!!ounces,desired});
  if(desired!==(ounces?"GOLD":"CASH")&&!pending){
   pending={side,at:row.tt,ts:t,why};
   signals.push({...pending,expectedNet14:prediction.net14,expectedNet4:prediction.net4});
  }
  seenOrigins++;
 }
 const last=monthly.at(-1);
 if(!last)throw Error("NO_BANK_CHECKPOINTS");
 return {version:"V11_REAL_ANN_BACKPROP_COST_TARGET",policy:policyName,
  initial,final:last.finalUSD,netPct:100*(last.finalUSD/initial-1),
  trials:seenOrigins,training:trainUpdates,firstTrainN:trainUpdates[0].maturedN,
  trades,signals,monthly,
  predictionErrors:predictions.filter(x=>x.at<=
     new Date(end-21*DAY).toISOString()).length,
  predictions:opts.includePredictions?predictions:undefined,
  fees:{eachLeg:FEE,roundTripNoPriceChange:(1-FEE)**2,
     realBankBidAsk:false},
  chronological:{
    allTrainLabelsMaturedBeforeCutoff:true,signalAt0900TR:true,
    executionAtNextBankCheckpoint:true,
    noHeldoutLabelsUsedToChoosePolicy:true
  },status:"SHADOW_NOT_INDEPENDENT_BLIND",liveTradingAuthorized:false,
  sourceRows:ds.records};
}
function research(){
 const src=loadFullRows(),ds=dataset(src.rows);
 const years=[
  {name:"2024",start:"2024-01-02T06:00:00Z",end:"2024-12-31T12:00:00Z",initial:100},
  {name:"2025",start:"2025-01-07T06:00:00Z",end:"2025-12-31T12:00:00Z",initial:100},
  {name:"2026_FEB_SEP",start:"2026-02-02T06:00:00Z",end:"2026-09-30T12:00:00Z",initial:119.753917}
 ];
 const experiments=[];
 for(const y of years)for(const policy of Object.keys(POLICIES)){
  const r=simulate(ds,{...y,policy});
  experiments.push({year:y.name,policy,initial:r.initial,final:r.final,
    netPct:r.netPct,nTrades:r.trades.length,training:r.training,
    monthly:r.monthly,trades:r.trades,signals:r.signals});
 }
 return{version:"V11_ANN_CORRECTLY_SUPERVISED_20261016",
  status:"RESEARCH_NOT_PROMOTED",
  source:{rows:src.rows.length,trainLabels:ds.sampleCount,verifiedOverlap:src.data.overlapVerified},
  model:{layers:[ANN.INPUTS,ANN.WIDTH1,ANN.WIDTH2,ANN.OUTPUTS],
    learnAlgorithm:"FULL_BACKPROP_ADAM_HUBER",
    outputs:"4D_AND_14D_NET_ROUNDTRIP_PCT",
    asofTargetEntry:"NEXT_ELIGIBLE_BANK_CHECKPOINT_AFTER_09TR",
    asofTargetExit:"FIRST_ELIGIBLE_BANK_CHECKPOINT_AFTER_HORIZON",
    validation:"CHRONOLOGICAL_80_20_WITH_21_DAY_LABEL_EMBARGO",
    evaluation:"TRAINING_LABEL_EXIT_BEFORE_YEAR_START_PLUS_MONTHLY_PAST_UPDATES"},
  experiments,
  gate:{promote:false,realBankAskBid:false,independentBlindTest:false,
    modelTunedAgainst2026:false,macroFirstprintVerified:0,
    reason:"HISTORICALLY_INSPECTED_PERIODS_PLUS_NEED_SAME_BANK_EXECUTION_AND_UNSEEN_PROSPECTIVE"}
 };
}
module.exports={FEE,POLICIES,isBank,isOrigin,upperBound,atOrAfter,inputs,
  dataset,chronologicalTraining,simulate,research};
