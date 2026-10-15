"use strict";
/**
 * V9 shadow-expert online portfolio selector.
 *
 * Distinct from an oracle: each expert is replayed in chronological order,
 * the metapolicy can inspect only NAVs and positions through NOW,
 * decisions fill at NEXT permitted Turkey bank checkpoint.
 *
 * Shadow NAVs are computed after transaction costs, liquidated at each bar
 * for comparison; the live ensemble pays transaction fees again on its own trades.
 * The CASH arm is included to support abstention.
 */
const {loadFullRows}=require("./v8_regret_engine");
const {replay:episode,DEFAULT}=require("./v9_episode_guard");
const {regime,FEE}=require("./v9_state_transition");
const HOUR=3600000,EXPERTS=["BASE","SLOW_EXIT","STRICT_ENTRY","POSTERIOR","CASH"];
const CONFIG={
 BASE:DEFAULT,
 SLOW_EXIT:{...DEFAULT,exit1:-4,exit3:-3,confirmExit:2},
 STRICT_ENTRY:{...DEFAULT,entry1:2,entry3:2,confirmEntry:3},
 POSTERIOR:{...DEFAULT,requirePosterior:true}
};
function prepareShadows(rows,stop){
 const first="2023-01-03T06:00:00Z";
 const experts=Object.fromEntries(Object.entries(CONFIG).map(([k,cfg])=>[k,
  episode(rows,{start:first,end:stop,initial:100,config:cfg,includeCurve:true}).curve]));
 if(Object.values(experts).some(x=>!x.length))throw Error("EMPTY_EXPERT_CURVE");
 const length=experts.BASE.length;
 for(const [k,curve] of Object.entries(experts)){
  if(curve.length!==length||curve.some((v,i)=>v.utc!==experts.BASE[i].utc))
    throw Error("SHADOW_CHECKPOINT_MISALIGN:"+k);
 }
 experts.CASH=experts.BASE.map(q=>({utc:q.utc,netUSD:100,position:"CASH"}));
 return experts;
}
function trailingScore(curve,i,window,lambda=.8){
 const from=Math.max(0,i-window);
 if(i-from<30)return 0;
 const series=curve.slice(from,i+1),start=series[0].netUSD,end=series.at(-1).netUSD;
 let peak=series[0].netUSD,maxDD=0;
 for(const q of series){peak=Math.max(peak,q.netUSD);maxDD=Math.max(maxDD,1-q.netUSD/peak);}
 const momentum=Math.log(Math.max(1e-8,end)/Math.max(1e-8,start));
 return momentum-lambda*maxDD;
}
function scoreSelector(shadows,i,settings){
 const window=settings.window||126;
 const scores=Object.fromEntries(EXPERTS.map(k=>[k,trailingScore(shadows[k],i,window,settings.riskPenalty??.8)]));
 const ranks=EXPERTS.slice().sort((x,y)=>scores[y]-scores[x]);
 const highest=ranks[0],bestExcess=scores[highest]-scores.CASH;
 let vote=0,total=0;
 const amp=settings.beta??20;
 for(const k of EXPERTS){
   const w=Math.exp(Math.max(-15,Math.min(15,amp*scores[k])));
   total+=w;if(shadows[k][i].position==="GOLD")vote+=w;
 }
 vote/=total;
 const band=settings.band??.62;
 const minEdge=settings.minEdge??.0162; // bank break-even 1.62% floor
 let gold=settings.mode==="best"?
   highest!=="CASH"&&bestExcess>minEdge&&shadows[highest][i].position==="GOLD":
   vote>band&&bestExcess>minEdge;
 return {gold,best:highest,score:scores[highest],cashScore:scores.CASH,
   margin:bestExcess,vote,scores,knownAsOf:shadows.BASE[i].utc};
}
function simulate(rows,settings={}){
 const start=Date.parse(settings.start||"2026-02-02T06:00:00Z");
 const stop=Date.parse(settings.end||"2026-09-30T12:00:00Z");
 const initial=settings.initial??119.753917,shadow=prepareShadows(rows,new Date(stop).toISOString());
 let cash=initial,ounces=0,lastSell=-Infinity,lastBuy=-Infinity,pending=null;
 const decisions=[],trades=[],monthly=[];
 const bankRows=rows.filter(x=>{
  const t=Date.parse(x.tt);return t<=stop&&[6,9,12].includes(new Date(t).getUTCHours());
 });
 if(shadow.BASE.length!==bankRows.length)throw Error("MIXED_SHADOW_ROWS");
 for(let i=0;i<bankRows.length;i++){
  const row=bankRows[i],t=Date.parse(row.tt);
  if(t<start)continue;
  // Before seeing the current row, execute only an order issued at the prior eligible checkpoint.
  if(pending&&pending.created<t){
   const desired=pending.gold;
   if(desired&&!ounces){
     ounces=cash*(1-FEE)/row.p;cash=0;lastBuy=t;
     trades.push({utc:row.tt,side:"BUY",price:row.p,asOf:pending.createdUTC,
       why:pending.reason});
   }else if(!desired&&ounces){
     cash=ounces*row.p*(1-FEE);ounces=0;lastSell=t;
     trades.push({utc:row.tt,side:"SELL",price:row.p,asOf:pending.createdUTC,
       why:pending.reason});
   }
   pending=null;
  }
  const currentNet=cash+ounces*row.c*(1-FEE);
  const mo=new Date(t+3*HOUR).toISOString().slice(0,7);
  if(!monthly.length||monthly.at(-1).month!==mo)
    monthly.push({month:mo,initialUSD:monthly.length?monthly.at(-1).netUSD:initial,
      netUSD:currentNet,position:ounces?"GOLD":"CASH"});
  else{monthly.at(-1).netUSD=currentNet;monthly.at(-1).position=ounces?"GOLD":"CASH";}
  const meta=scoreSelector(shadow,i,settings);
  const reg=regime(row);
  const stress=reg==="STRESS";
  let target=meta.gold&&!stress;
  if(target&&!ounces&&t-lastSell<96*HOUR)target=false;
  if(!target&&ounces&&t-lastBuy<72*HOUR&&!stress)target=true;
  let reason=stress?"STRESS_OVERRIDE":"ONLINE_SHADOW_RISK_ADJUSTED";
  if(target!==!!ounces)pending={gold:target,created:t,createdUTC:row.tt,reason};
  decisions.push({utc:row.tt,asOf:meta.knownAsOf,position:ounces?"GOLD":"CASH",
    signal:target?"GOLD":"CASH",score:meta.score,margin:meta.margin,
    vote:meta.vote,leader:meta.best,regime:reg,nav:currentNet});
 }
 return {version:"V9_SHADOW_REGRET_SELECTOR_V1",start:new Date(start).toISOString(),
  end:new Date(stop).toISOString(),initial,final:monthly.at(-1)?.netUSD,
  profitPct:100*(monthly.at(-1)?.netUSD/initial-1),
  settings:{window:settings.window||126,mode:settings.mode||"vote",
     beta:settings.beta??20,riskPenalty:settings.riskPenalty??.8,
     band:settings.band??.62,minEdge:settings.minEdge??.0162},
  monthly,trades,decisions:settings.includeDecisions?decisions:undefined,
  last:decisions.at(-1),sourceRows:rows.length,
  liveAuthorized:false,independentBlind:false,asOfLag:true,
  realBankBidAsk:false,costEachSide:FEE};
}
function audit(){
 const data=loadFullRows();
 const years=[
  {year:"2024",start:"2024-01-02T06:00:00Z",end:"2024-12-31T12:00:00Z",initial:100},
  {year:"2025",start:"2025-01-07T06:00:00Z",end:"2025-12-31T12:00:00Z",initial:100},
  {year:"2026",start:"2026-02-02T06:00:00Z",end:"2026-09-30T12:00:00Z",initial:119.753917}
 ];
 const candidates=[
  {name:"VOTE_42D",window:126,mode:"vote",band:.6,minEdge:.0162},
  {name:"VOTE_84D",window:252,mode:"vote",band:.6,minEdge:.0162},
  {name:"BEST_42D",window:126,mode:"best",minEdge:.0162},
  {name:"BEST_84D",window:252,mode:"best",minEdge:.0162},
  {name:"SAFETY_42D",window:126,mode:"vote",band:.75,minEdge:.0324}
 ];
 const results=[];
 for(const c of candidates)for(const p of years){
  const d=simulate(data.rows,{...c,...p});
  results.push({name:c.name,year:p.year,initial:d.initial,final:d.final,
    trades:d.trades.length,monthly:d.monthly});
 }
 return{version:"V9_SHADOW_META_SELECTOR_AUDIT",status:"NO_BLIND_VALIDATION",
  data:data.data,results,autoPromotion:false,bidAskVerified:false};
}
module.exports={EXPERTS,CONFIG,prepareShadows,trailingScore,scoreSelector,simulate,audit};
