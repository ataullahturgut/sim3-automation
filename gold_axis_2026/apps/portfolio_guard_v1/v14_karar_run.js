"use strict";
/**
 * V14 causal chronological bank-proxy portfolio experiment.
 * Independent portfolio starts; training state walks from data inception.
 * Research ONLY: retrospective, not blind, not live bank BID/ASK.
 */
const V13=require("./v13_sentez_core");
const V14=require("./v14_karar_ogrenme");
const V13RUN=require("./v13_sentez_run");
const PERIODS=[
 {name:"2023_TO_2026",start:"2023-01-03T06:00:00Z",end:"2026-09-30T12:00:00Z",initial:100},
 {name:"2024",start:"2024-01-02T06:00:00Z",end:"2024-12-31T12:00:00Z",initial:100},
 {name:"2025",start:"2025-01-07T06:00:00Z",end:"2025-12-31T12:00:00Z",initial:100},
 {name:"2026_FEB_SEP",start:"2026-02-02T06:00:00Z",end:"2026-09-30T12:00:00Z",initial:119.753917}
];
const MAX14=14*V13.DAY,MAX56=28*V13.DAY;
const f14Legacy=p=>p.net56;
function one(b,opt={}){
 const start=Date.parse(opt.start||PERIODS[0].start),
   end=Date.parse(opt.end||PERIODS[0].end),initial=opt.initial??100;
 if(!(start<end&&initial>0))throw Error("INVALID_PERIOD");
 const s13=V13.create(),s14=V14.create(opt);
 const q13={14:[],56:[]},q14={7:[],28:[],56:[]};
 const used13={14:new Set(),56:new Set()},used14={7:new Set(),28:new Set(),56:new Set()};
 const ds=b.extended;
 let cash=initial,ounces=0,pending=null,network=null,year=null,prev=-Infinity,peak=initial,maxDD=0;
 const trades=[],monthly=[],feedback=[],diagnostics=[];
 for(const row of ds.bank){
   const now=row.ts;if(now>end)break;
   if(!(now>prev))throw Error("NON_CHRONOLOGICAL_BANK_PRICES");
   prev=now;
   // Delayed feedback: no update at exit instant; ONLY after.
   for(const h of [14,56]){
     while(q13[h].length&&q13[h][0].exitTs<now){
       const old=q13[h].shift();
       V13.applyOutcome(s13,old,{now},h);
     }
   }
   for(const h of [7,28,56]){
     while(q14[h].length&&q14[h][0].exitTs<now){
       const old=q14[h].shift();
       const u=V14.learn(s14,old,now);
       feedback.push(u);
     }
   }
   if(now>=start&&pending&&pending.atTs<now){
     if(pending.target==="GOLD"&&cash>0){
       ounces=cash*(1-V14.FEE)/row.p;cash=0;
       trades.push({at:row.tt,signalAt:pending.at,side:"BUY",why:pending.reason,
         price:row.p,advantage:pending.advantage});
     }else if(pending.target==="CASH"&&ounces>0){
       cash=ounces*row.p*(1-V14.FEE);ounces=0;
       trades.push({at:row.tt,signalAt:pending.at,side:"SELL",why:pending.reason,
         price:row.p,advantage:pending.advantage});
     }
     pending=null;
   }
   const nav=cash+ounces*row.c*(1-V14.FEE);
   if(now>=start){
     peak=Math.max(peak,nav);
     maxDD=Math.max(maxDD,100*(1-nav/peak));
     const month=new Date(now+3*V14.HR).toISOString().slice(0,7);
     const last=monthly.at(-1);
     if(last?.month!==month)monthly.push({month,nav,position:ounces>0?"GOLD":"CASH"});
     else Object.assign(last,{nav,position:ounces>0?"GOLD":"CASH"});
   }
   if(new Date(now).getUTCHours()!==6)continue; // Turkey 09:00
   const y=new Date(now).getUTCFullYear();
   if(year!==y){year=y;network=V13.frozenANN(b.primary,year);}
   const f=ds.featuresByOrigin.get(row.tt);
   if(!f)throw Error("ASOF_FEATURE_MISSING");
   s13.gated=V13.gatedState(s13.gated,f);
   const f13=V13.predict(s13,f,network?.weights?network:null);
   const x=V14.observe(s14,f,f13),forecast=V14.forecast(s14,x);
   const pos=ounces>0?"GOLD":"CASH";
   const choice=V14.action(s14,forecast,pos);
   const old=ds.byOrigin.get(row.tt);
   if(old){
     for(const h of [14,56]){
       const key=Math.floor(now/(h===14?MAX14:MAX56));
       const t=h===14?old.y14:old.y56,exitTs=h===14?old.exit14Ts:old.exit56Ts;
       if(t!==null&&exitTs!=null&&!used13[h].has(key)){
         used13[h].add(key);
         q13[h].push({origin:row.tt,exitTs,target:t,forecast:f13});
       }
     }
   }
   for(const h of [7,28,56]){
     const spacing=h===7?7:h===28?14:28,key=Math.floor(now/(spacing*V14.DAY));
     if(used14[h].has(key))continue;
     const label=V14.label(ds.bank,now,h);
     if(label){
       used14[h].add(key);
       q14[h].push({...label,h,pred:forecast,origin:row.tt});
     }
   }
   if(now>=start){
     if(choice.target!==pos&&!pending){
       pending={target:choice.target,atTs:now,at:row.tt,
         advantage:choice.advantage,reason:choice.reason};
     }
     if(opt.includeDiagnostics)diagnostics.push({
       at:row.tt,position:pos,proposed:choice.target,
       mu:forecast.mu,downside:forecast.downside,uncertainty:forecast.uncertainty,
       netScore:choice.advantage,shortMu:choice.shortMu,old14:f13.net14,old56:f13.net56,
       learn7:s14.heads[7].n,learn28:s14.heads[28].n,learn56:s14.heads[56].n,legacy:f14Legacy(f13),
       gate:s14.gateW.slice(),reason:choice.reason
     });
   }
 }
 if(!monthly.length)throw Error("NO_ROWS");
 const first=b.extended.bank.find(r=>r.ts>start&&r.ts<=end);
 const last=b.extended.bank.filter(r=>r.ts<=end).at(-1);
 const passive=first&&last?initial*(1-V14.FEE)**2*last.p/first.p:null;
 for(const t of trades)if(!(Date.parse(t.at)>Date.parse(t.signalAt)))throw Error("NONCAUSAL_FILL");
 return {version:"V14_ADAPTIVE_ACTION_RESEARCH_20261016",
   initial,final:monthly.at(-1).nav,buyHold:passive,netPct:100*(monthly.at(-1).nav/initial-1),
   tradeCount:trades.length,trades,maxDrawdownPct:maxDD,
   monthly,learned7:s14.heads[7].n,learned28:s14.heads[28].n,learned56:s14.heads[56].n,
   learnedGate:s14.gateW,feedbackCount:feedback.length,
   diagnostics:opt.includeDiagnostics?diagnostics:undefined,
   feedback:opt.includeFeedback?feedback:undefined,
   scientificGate:{promote:false,blind:false,liveTrade:false,verifiedRealBidAsk:false},
   assumptions:{feeEachSide:.008,signals:"09:00 Turkey",fills:"NEXT_CHECKPOINT",
      priorYearAsOf:true,fullHorizonMaturedOnly:true,seen2023to2026:true}};
}
function audit(){
 const b=V13RUN.build(),out=[];
 for(const p of PERIODS){
   for(const variant of ["V14_FULL","V14_NO_GATE","V14_NO_RISK","V14_NO_SHORT_EXIT"]){
     const q=one(b,{...p,disableGate:variant==="V14_NO_GATE",
       disableRisk:variant==="V14_NO_RISK",disableShortExit:variant==="V14_NO_SHORT_EXIT"});
     out.push({period:p.name,variant,initial:q.initial,final:q.final,
       buyHold:q.buyHold,trades:q.tradeCount,maxDD:q.maxDrawdownPct,
       matured7:q.learned7,matured28:q.learned28,matured56:q.learned56,gate:q.learnedGate,
       ledger:q.trades});
   }
 }
 const passive=out.filter(x=>x.variant==="V14_FULL");
 const v13=V13RUN.audit().experiments.filter(x=>x.variant==="SENTEZ_HYBRID")
   .map(x=>({period:x.period,final:x.finalUSD,buyHold:x.buyHoldUSD,trades:x.trades}));
 return {version:"V14_POLICY_AUDIT",scientificGate:{promote:false,blind:false,liveTrade:false},
    description:"Online learned action advantage, downside risk and local recurrent gate",
    sourceRows:b.src.rows.length,experiments:out,v13Benchmark:v13,
    canPromote:false,important:"2023-2026 repeatedly researched: never claim out-of-sample"};
}
if(require.main===module)console.log(JSON.stringify(audit(),null,2));
module.exports={one,audit,PERIODS};
