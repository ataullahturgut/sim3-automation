"use strict";
/**
 * Episode policy benchmark — long-horizon gold holding with hysteresis and
 * delayed learning from non-overlapping 336h opportunity labels.
 * Source timestamp known BEFORE NEXT bank checkpoint is executed.
 */
const {loadFullRows}=require("./v8_regret_engine");
const {regime,FEE}=require("./v9_state_transition");
const HR=3600000,DAY=24*HR;
const DEFAULT=Object.freeze({entry1:1,entry3:1,exit1:-3,exit3:-2,
  confirmEntry:2,confirmExit:2,cooldownHours:96,minHoldHours:72,
  requirePosterior:false,stopLossPct:0,exitShock:true,recovery:true});
function init(initial){return{cash:initial,ounces:0,entryTime:-Infinity,exitTime:-Infinity,
  peakPrice:0,entryMid:0,pending:null,transactions:[],history:[]};}
function replay(rows,opts={}){
 const cfg={...DEFAULT,...(opts.config||{})};
 const start=Date.parse(opts.start||"2026-02-02T06:00:00Z");
 const end=Date.parse(opts.end||"2026-09-30T12:00:00Z"),initial=opts.initial??119.753917;
 if(start>=end||!Number.isFinite(start)||!Number.isFinite(end))throw Error("BAD_PERIOD");
 const portfolio=init(initial),months=[];
 let entryStreak=0,exitStreak=0,lastShock=-Infinity,anchorLast=-Infinity;
 const pending=[],learned=[],errors={opportunityUp:0,avoidedDown:0,lateExit:0},
   stats={UP:{n:0,win:0,mean:0},DOWN:{n:0,win:0,mean:0},
      STRESS:{n:0,win:0,mean:0},RANGE:{n:0,win:0,mean:0}};
 const decisions=[];
 const asof=(v,t)=>v.created<t;
 for(const row of rows){
   const t=Number.isFinite(row.ts)?row.ts:Date.parse(row.tt);
   if(t>end)break;
   const rg=regime(row);
   if(rg==="STRESS")lastShock=t;
   if(new Date(t).getUTCHours()===6&&t-anchorLast>=336*HR){
     anchorLast=t;
     pending.push({origin:row.tt,time:t,due:t+336*HR,price:row.c,regime:rg});
   }
   for(let i=pending.length-1;i>=0;i--){
     const q=pending[i];if(q.due>t)continue;
     pending.splice(i,1);
     if(t-q.due>78*HR)continue;
     const net=100*((1-FEE)**2*row.c/q.price-1);
     const s=stats[q.regime];
     s.n++;s.win+=net>0?1:0;s.mean+=(net-s.mean)/s.n;
     learned.push({origin:q.origin,labelKnown:row.tt,regime:q.regime,
       valueNetPct:net,overlapFreeAtOrigin:true});
   }
   const hour=new Date(t).getUTCHours();
   if(![6,9,12].includes(hour))continue;
   // Defer EVERY action until the next bank checkpoint to guard as-of availability.
   if(portfolio.pending&&asof(portfolio.pending,t)&&t>=start){
     const p=portfolio.pending;
     if(p.buy&&!portfolio.ounces){
       const q=portfolio.cash*(1-FEE)/row.p;portfolio.cash=0;portfolio.ounces=q;
       portfolio.entryMid=row.p;portfolio.entryTime=t;portfolio.peakPrice=row.p;
       portfolio.transactions.push({at:row.tt,side:"BUY",mid:row.p,why:p.reason});
     }else if(!p.buy&&portfolio.ounces){
       portfolio.cash=portfolio.ounces*row.p*(1-FEE);portfolio.ounces=0;
       portfolio.exitTime=t;portfolio.peakPrice=0;
       portfolio.transactions.push({at:row.tt,side:"SELL",mid:row.p,why:p.reason});
     }
     portfolio.pending=null;
   }
   if(t<start)continue;
   if(portfolio.ounces)portfolio.peakPrice=Math.max(row.c,portfolio.peakPrice);
   const nav=portfolio.cash+portfolio.ounces*row.c*(1-FEE);
   const month=new Date(t+3*HR).toISOString().slice(0,7);
   if(!months.length||months.at(-1).month!==month){
      months.push({month,initialUSD:months.length?months.at(-1).terminalUSD:initial,terminalUSD:nav,position:portfolio.ounces?"GOLD":"CASH"});
   }else{
      months.at(-1).terminalUSD=nav;
      months.at(-1).position=portfolio.ounces?"GOLD":"CASH";
   }
   const r1=row.r1,r3=row.r3,r4=row.r4,nq6=row.nq6;
   const stress=rg==="STRESS";
   const recovery=(t-lastShock>=DAY&&t-lastShock<=42*DAY&&r1>-.5&&r3>-1&&r4>.5&&
     (nq6==null||nq6>-1.25));
   const entry=(!stress&&r1>cfg.entry1&&r3>cfg.entry3&&(r4==null||r4>-.7))||
     (cfg.recovery&&!stress&&recovery);
   const exit=stress||
     (r1<cfg.exit1&&r3<cfg.exit3)||
     (cfg.stopLossPct>0&&portfolio.ounces&&
      100*(row.c/portfolio.peakPrice-1)<=-cfg.stopLossPct);
   entryStreak=entry?entryStreak+1:0;
   exitStreak=exit?exitStreak+1:0;
   const s=stats[rg];
   const posteriorP=(s.win+2)/(s.n+4);
   const posteriorAllowed=!cfg.requirePosterior||s.n<5||posteriorP>=.45;
   const readyToEnter=entryStreak>=cfg.confirmEntry&&posteriorAllowed&&
     t-portfolio.exitTime>=cfg.cooldownHours*HR;
   const readyToExit=(stress&&cfg.exitShock)||(
    exitStreak>=cfg.confirmExit&&t-portfolio.entryTime>=cfg.minHoldHours*HR
   );
   let proposed=portfolio.ounces>0,reason="STAY";
   if(!portfolio.ounces&&readyToEnter){proposed=true;reason=recovery?"CONFIRMED_RECOVERY":"CONFIRMED_UP_EPISODE";}
   else if(portfolio.ounces&&readyToExit){proposed=false;reason=stress?"RISK_SHOCK":"END_OF_UP_EPISODE";}
   if(proposed!==!!portfolio.ounces)
     portfolio.pending={buy:proposed,created:t,reason};
   decisions.push({time:row.tt,knownRegime:rg,posteriorP,
     nextCheckpointExecution:true,desired:proposed?"GOLD":"CASH",cash:portfolio.cash,nav,
     entryStreak,exitStreak,reason,trainingN:s.n,earliestLearningFrom:learned.at(-1)?.labelKnown??null});
 }
 const final=months.at(-1)?.terminalUSD;
 if(!Number.isFinite(final))throw Error("NO_MONTHS");
 return{initial,final,netPct:100*(final/initial-1),trades:portfolio.transactions,monthly:months,
  config:cfg,trained336:learned.length,regimeStats:stats,learnedLabels:opts.includeLabels?learned:undefined,
  decisions:opts.includeDecisions?decisions:undefined,
  status:"RESEARCH_NOT_BLIND",feePerSide:FEE,
  executionLagged:true,bankBidAskIncluded:false,macroEventsValidated:0,
  automaticPromotion:false};
}
function audit(){
 const data=loadFullRows(),periods=[
  {year:"2024",start:"2024-01-02T06:00:00Z",end:"2024-12-31T12:00:00Z",initial:100},
  {year:"2025",start:"2025-01-07T06:00:00Z",end:"2025-12-31T12:00:00Z",initial:100},
  {year:"2026",start:"2026-02-02T06:00:00Z",end:"2026-09-30T12:00:00Z",initial:119.753917}];
 const variants={
  BASE:DEFAULT,
  SLOW_EXIT:{...DEFAULT,exit1:-4,exit3:-3,confirmExit:2},
  STRICT_ENTRY:{...DEFAULT,entry1:2,entry3:2,confirmEntry:3},
  NO_RECOVERY:{...DEFAULT,recovery:false},
  POSTERIOR:{...DEFAULT,requirePosterior:true},
  NO_SHOCK:{...DEFAULT,exitShock:false}
 };
 const results=[];
 for(const [name,config] of Object.entries(variants))
  for(const p of periods){
   const t=replay(data.rows,{...p,config});
   results.push({variant:name,year:p.year,final:t.final,netPct:t.netPct,
     initial:t.initial,trades:t.trades.length});
  }
 return{version:"V9_EPISODE_HYSTERESIS_EXPERIMENT",results,config:DEFAULT,source:data.data,
  blind:false,realBank:false,autoPromotion:false};
}
module.exports={DEFAULT,replay,audit};
