#!/usr/bin/env node
"use strict";
/**
 * JAN 2026 NEW MONTH WALK — V1 (exploratory, no live trading).
 * 15m origin-safe replay. At each *observed* M15 checkpoint evaluates the
 * 5 frozen price questions + 92 pre-2026 matured OLAY-02 analog examples.
 * On all 2976 calendar slots, unobserved periods remain NO_ACTION.
 * Finance: 0.8% for buy, 0.8% for sell; no bank bid/ask or slippage.
 * Not a GPT interpretation of 2976 individual news states.
 *
 * node JAN_2026_NEW_EVENT_MONTH_WALK_V1_REPLAY.js [panel] [OLAY02] [outcomes]
 */
const fs=require("fs"),path=require("path");
const ROOT=__dirname;
const argv=process.argv.slice(2);
const panelFile=argv[0]||path.join(ROOT,"JAN_2026_NEW_EVENT_MONTH_WALK_V1_15M_ASOF_PANEL.csv");
const libraryFile=argv[1]||path.join(ROOT,"../../../OLAY_02_96_TUM_VAKA_EVRENSEL_ORUNTU_MATRIKS_20261015.csv");
const outcomesFile=argv[2]||path.join(ROOT,"../../portfolio_protection/historical_96h_case_outcomes_v0.csv");
const beginning=Date.parse("2025-12-31T21:00:00Z");
const end=Date.parse("2026-01-31T21:00:00Z");
const ms15=900000,fee=.008;
const fmt=new Intl.DateTimeFormat("sv-SE",{timeZone:"Europe/Istanbul",year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",hour12:false});
function parseCsv(src){
 const data=[],row=[];let str="",quoted=false;
 for(let i=0;i<src.length;i++){
  const c=src[i];if(c==='"'){if(quoted&&src[i+1]==='"'){str+='"';i++;}else quoted=!quoted;}
  else if(c===','&&!quoted){row.push(str);str="";}
  else if((c==='
'||c==='')&&!quoted){if(c===''&&src[i+1]==='
')i++;row.push(str);if(row.length>1)data.push(row.slice());row.length=0;str="";}
  else str+=c;
 }
 if(row.length||str){row.push(str);data.push(row);}
 const fields=data.shift();return data.map(r=>Object.fromEntries(fields.map((f,i)=>[f,r[i]||""])));
}
const csv=(file)=>parseCsv(fs.readFileSync(file,"utf-8"));
function num(z){if(z===null||z===undefined||z==="")return null;const v=+z;return Number.isFinite(v)?v:null;}
const feat=[
 ["r4","asof_ret4h_pct",1.2,1],["rv","asof_rv4h_pct",.65,1],
 ["ds","asof_downside_var_share4h",.45,.5],["eff","asof_path_efficiency4h",.55,.5],
 ["loc","asof_close_location4h",.55,.4],["dd4","asof_from_high_dd4h_pct",1.5,1],
 ["nq1","asof_nq_return_h1_pct",.65,.5],["zn1","asof_zn_futures_price_return_h1_pct",.15,.25]
];
const matureOutcomes=Object.fromEntries(csv(outcomesFile).map(r=>[r.case_id,r]));
const historical=csv(libraryFile).filter(r=>
 r.asof_price_quality==="COMPLETE" &&
 Date.parse(r.checkpoint_utc)+96*3600000<=beginning &&
 matureOutcomes[r.case_id] && num(matureOutcomes[r.case_id].ct)>=40
).map(r=>({
 id:r.case_id,org:r.org_plot_candidate,
 low:num(matureOutcomes[r.case_id].low96),
 feat:Object.fromEntries(feat.map(([k,k2])=>[k,num(r[k2])]))
}));
if(historical.length!==92)throw Error("Invalid mature archive: expected 92, got "+historical.length);
const panel=csv(panelFile).map(row=>Object.fromEntries(Object.entries(row).map(([k,v])=>[k,k==="tt"?v:num(v)])));
if(panel.length!==1804)throw Error("Invalid panel count; preserve exact M15 source");
const timeMap=new Map(panel.map(r=>[Date.parse(r.tt),r]));
function analog(r){
 const nearest=historical.map(h=>{
  let sum=0,norm=0;
  for(const [key,unused,scale,w]of feat){
   const a=r[key],b=h.feat[key];
   if(a===null||b===null)continue;
   sum+=w*Math.pow((a-b)/scale,2);norm+=w;
  }
  return {...h,distance:Math.sqrt(sum/norm)};
 }).sort((a,b)=>a.distance-b.distance).slice(0,9);
 let down=0,total=0;
 for(const x of nearest){const weight=Math.pow(x.distance+.35,-2);total+=weight;if(x.low<=-3)down+=weight;}
 return {risk:down/total,distance:nearest[0].distance,near:nearest.slice(0,3).map(x=>x.id)};
}
const releases=[
 ["JOLTS_2025_11","2026-01-07T15:00:00Z"],
 ["NFP_2025_12","2026-01-09T13:30:00Z"],
 ["CPI_2025_12","2026-01-13T13:30:00Z"],
 ["PPI_2025_11","2026-01-14T13:30:00Z"],
 ["FOMC","2026-01-28T19:00:00Z"],
 ["PRODUCTIVITY_Q3_2025","2026-01-29T13:30:00Z"],
 ["PPI_2025_12","2026-01-30T13:30:00Z"]
].map(([id,ts])=>({id,at:Date.parse(ts)}));
let cash=100,oz=0,highSinceBuy=0,lastSell=-Infinity,lastClose=null,
 portfolioPeak=100,maxDrawdown=0,valid=0,tx=[],ledger=[];
for(let t=beginning;t<end;t+=ms15){
 const r=timeMap.get(t),tr=fmt.format(new Date(t));
 let event="NONE",phase="P0_NO_VERIFIED_NEW_RELEASE";
 let action=oz?"HOLD_GOLD":"HOLD_CASH",reason="NO_NEW_COMPLETE_M15",risk=null,dist=null;
 if(r){
  valid++;lastClose=r.c;
  const a=analog(r);risk=a.risk;dist=a.distance;
  const active=releases.filter(e=>t>e.at&&t-e.at<=6*3600000).at(-1);
  event=active?.id||"NONE";
  phase=active?"P2_G01_RELEASE_OBSERVED_CAUSE_UNRESOLVED":"P0_PRICE_STATE_UNKNOWN_CAUSE";
  const coSell=r.r4<=-1&&r.nq6!==null&&r.nq6<=-1;
  const novelty=a.distance>=1&&r.rv>=.8;
  if(coSell)phase="P2_CROSS_MARKET_SELLING_CANDIDATE";
  if(novelty)phase="P2_OUT_OF_DISTRIBUTION_MOVE_UNKNOWN_CAUSE";
  if(active&&novelty)phase="P2_EVENT_PLUS_OUTLIER_CAUSE_UNRESOLVED";
  if(oz){
   highSinceBuy=Math.max(highSinceBuy,r.c);
   const trail=100*(r.c/highSinceBuy-1);
   const why=coSell&&(a.risk>=.2||novelty)?"CROSS_SELL_EVENT_NOVELTY":
     (r.r4<=-2&&r.rv>=1.2&&a.distance>=1)?"NEW_UNSEEN_SHOCK":
     trail<=-3.5?"TRAILING_SHOCK":
     r.r4<=-2?"FAST_DOWN":
     r.r92<=-2&&r.r4<0?"R92_BREAK":
     r.r276<-2&&r.r4<-.5?"R276_BREAK":null;
   if(why){
    cash=oz*r.p*(1-fee);oz=0;lastSell=t;highSinceBuy=0;
    action="SELL_TO_CASH";reason=why;
    tx.push({utc:r.tt,tr,action,p:r.p,cash,why,risk,distance:dist,near:a.near});
   }else reason="NO_CONFIRMED_MARGINALLY_AVOIDABLE_DOWN";
  }else{
   const entry=r.r92>=1&&r.r276>=0&&r.r4>=-.25&&r.dd276>=-3.5&&r.v92<=4;
   if(entry&&t-lastSell>=12*3600000){
    oz=cash*(1-fee)/r.p;cash=0;highSinceBuy=r.p;
    action="BUY_GOLD";reason="PRICE5_WITH_ARCHIVED_EVENT_CROSSCHECK";
    tx.push({utc:r.tt,tr,action,p:r.p,ounces:oz,why:reason,risk,distance:dist,near:a.near});
   }else reason="NO_PROFITABLE_CONFIRMED_UP_GATE";
  }
 }
 const net=oz&&lastClose!==null?oz*lastClose*(1-fee):cash;
 portfolioPeak=Math.max(portfolioPeak,net);
 maxDrawdown=Math.max(maxDrawdown,100*(1-net/portfolioPeak));
 ledger.push({utc:new Date(t).toISOString(),tr,
 available:!!r,phase,event,action,reason,risk,dist,gold_oz:oz,cash_usd:cash,nav_if_liquidated:net});
}
if(valid!==1804||ledger.length!==2976||tx.length!==2||Math.abs(cash-119.7539172)>.0001)
 throw Error("Failed result regression; inspect input source/calculation");
console.log(JSON.stringify({status:"RESEARCH_ONLY_NOT_ECONOMICALLY_VALIDATED",
 validM15:valid,calendarSlots:ledger.length,trades:tx,
 endingCash:cash,maxDrawdownPct:maxDrawdown,
 incrementalEconomicDNAUsd:0,realBankBidAskIncluded:false},null,2));
