"use strict";
/**
 * GOLD Portfolio Guard V1 — deterministic historical replay.
 * FROZEN Jan 2026 inputs; no broker connectivity; no unseen external requests.
 * Business rules here, not in the HTML page. Requires Node.js 18+.
 */
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const REPO = path.resolve(__dirname, "../../..");
const DATA = Object.freeze({
  panel: {path: "gold_axis_2026/adaptive_volatility_learning/months/2026-01-new-learning/JAN_2026_NEW_EVENT_MONTH_WALK_V1_15M_ASOF_PANEL.csv", blob: "c0dc3171862d79865bc2444746137ab17af7f756"},
  archive: {path: "gold_axis_2026/OLAY_02_96_TUM_VAKA_EVRENSEL_ORUNTU_MATRIKS_20261015.csv", blob: "4b6c8fd84ea291ae22ddc9b0d5d545ce2d8fa527"},
  outcomes: {path: "gold_axis_2026/adaptive_volatility_learning/portfolio_protection/historical_96h_case_outcomes_v0.csv", blob: "c4fcf4ec622abe66d289684589a856dc8d45d787"}
});
const VERSION = "PORTFOLIO_GUARD_JAN2026_V1_FROZEN";
const ORIGIN = Date.parse("2025-12-31T21:00:00.000Z");
const END = Date.parse("2026-01-31T21:00:00.000Z");
const M15 = 15 * 60000;
const FEE = 0.008;
const TIME = new Intl.DateTimeFormat("sv-SE", {timeZone:"Europe/Istanbul",year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",hour12:false});
const FEATURES = [
  ["r4","asof_ret4h_pct",1.2,1],
  ["rv","asof_rv4h_pct",0.65,1],
  ["ds","asof_downside_var_share4h",0.45,0.5],
  ["eff","asof_path_efficiency4h",0.55,0.5],
  ["loc","asof_close_location4h",0.55,0.4],
  ["dd4","asof_from_high_dd4h_pct",1.5,1],
  ["nq1","asof_nq_return_h1_pct",0.65,0.5],
  ["zn1","asof_zn_futures_price_return_h1_pct",0.15,0.25]
];
const RELEASES = [
 ["JOLTS_2025_11","2026-01-07T15:00:00Z"],
 ["NFP_2025_12","2026-01-09T13:30:00Z"],
 ["CPI_2025_12","2026-01-13T13:30:00Z"],
 ["PPI_2025_11","2026-01-14T13:30:00Z"],
 ["FOMC","2026-01-28T19:00:00Z"],
 ["PRODUCTIVITY_Q3_2025","2026-01-29T13:30:00Z"],
 ["PPI_2025_12","2026-01-30T13:30:00Z"]
].map(function(x){return {id:x[0],ms:Date.parse(x[1])};});

function csvParse(input) {
 const all=[],row=[]; let cell="",quoted=false;
 for(let i=0;i<input.length;i++){
  const c=input[i];
  if(c==='"'){
   if(quoted && input[i+1]==='"'){cell+='"';i++;}
   else quoted=!quoted;
  }else if(c==="," && !quoted){row.push(cell);cell="";}
  else if((c==="\n"||c==="\r")&&!quoted){
   if(c==="\r"&&input[i+1]==="\n")i++;
   row.push(cell);if(row.length>1)all.push(row.slice());
   row.length=0;cell="";
  }else cell+=c;
 }
 if(quoted)throw new Error("Unclosed CSV quote");
 if(row.length||cell){row.push(cell);all.push(row.slice());}
 const head=all.shift();
 if(!head)throw new Error("Empty CSV");
 return all.map(function(line){
  if(line.length!==head.length)throw new Error("Invalid CSV column count");
  return Object.fromEntries(head.map(function(k,i){return [k,line[i]];}));
 });
}
function numerical(x) {
 if(x===null||x===undefined||x==="")return null;
 const v=Number(x);
 return Number.isFinite(v)?v:null;
}
function gitBlobHash(bytes) {
 const head=Buffer.from("blob "+bytes.length+"\0");
 return crypto.createHash("sha1").update(head).update(bytes).digest("hex");
}
/**
 * Git for Windows may check out UTF-8 CSV as CRLF even when the pinned Git
 * blob stores LF. Verify the *canonical content* against the original Git blob
 * SHA, never bypass the integrity check. Any changed data still fail closed.
 */
function decodePinnedSource(spec,raw) {
 const rawHash=gitBlobHash(raw);
 let checked=raw,converted=false;
 if(rawHash!==spec.blob) {
  checked=Buffer.from(raw.toString("utf8").replace(/\r\n/g,"\n"),"utf8");
  converted=gitBlobHash(checked)===spec.blob;
  if(!converted)throw new Error("DATA_VERSION_MISMATCH: "+spec.path+" expected "+spec.blob+" received "+rawHash);
 }
 return {rows:csvParse(checked.toString("utf8")),gitBlob:spec.blob,bytes:checked.length,
  windowsLineEndingsNormalized:converted};
}
function loadSource(spec) {
 return decodePinnedSource(spec,fs.readFileSync(path.join(REPO,spec.path)));
}
function loadFrozen() {
 const panel=loadSource(DATA.panel),archive=loadSource(DATA.archive),outcomes=loadSource(DATA.outcomes);
 const rows=panel.rows.map(function(row){
  const x={tt:row.tt,time:Date.parse(row.tt)};
  for(const [k,v] of Object.entries(row)){if(k!=="tt")x[k]=numerical(v);}
  if(!Number.isFinite(x.time)||!Number.isFinite(x.p)||!Number.isFinite(x.c))throw new Error("BAD_PRICE_ROW");
  return x;
 });
 if(rows.length!==1804||rows[0].time!==ORIGIN||rows.at(-1).tt!=="2026-01-30T21:30:00.000Z")throw new Error("UNEXPECTED_JAN2026_SOURCE_SCOPE");
 for(let i=1;i<rows.length;i++)if(rows[i].time<=rows[i-1].time)throw new Error("PRICE_TIMESTAMPS_NOT_INCREASING");
 const label=Object.fromEntries(outcomes.rows.map(function(r){return [r.case_id,r];}));
 const events=archive.rows.filter(function(r){
  const t=Date.parse(r.checkpoint_utc);
  return r.asof_price_quality==="COMPLETE" &&
    Number.isFinite(t) && t+96*3600000<=ORIGIN &&
    label[r.case_id] && numerical(label[r.case_id].ct)>=40;
 }).map(function(r){
  return {
   id:r.case_id,org:r.org_plot_candidate,low:numerical(label[r.case_id].low96),
   feat:Object.fromEntries(FEATURES.map(function(f){return [f[0],numerical(r[f[1]])];}))
  };
 });
 if(events.length!==92)throw new Error("ARCHIVE_IS_NOT_FROZEN_92");
 return {rows,events,inputs:Object.fromEntries(Object.entries(DATA).map(function(k){return [k[0],{gitBlob:k[1].blob,path:k[1].path}]}))};
}
function analog(row,history){
 const near=history.map(function(event){
  let d=0,w=0;
  for(const f of FEATURES){
   const key=f[0],scale=f[2],weight=f[3],a=row[key],b=event.feat[key];
   if(a===null||b===null)continue;
   d+=weight*Math.pow((a-b)/scale,2);w+=weight;
  }
  if(w===0)throw new Error("UNCOMPARABLE_EVENT");
  return {id:event.id,org:event.org,low:event.low,distance:Math.sqrt(d/w)};
 }).sort(function(a,b){return a.distance-b.distance;}).slice(0,9);
 let denom=0,bad=0;
 for(const x of near){const weight=1/Math.pow(x.distance+0.35,2);denom+=weight;if(x.low<=-3)bad+=weight;}
 return {riskScore:bad/denom,distance:near[0].distance,nearest:near.slice(0,3).map(function(x){return {id:x.id,org:x.org,distance:x.distance};})};
}
function benchmark(rows,mode) {
 const first=rows[0].p;
 let last=rows.at(-1);
 if(mode==="legacy3h")last=rows.filter(function(r){return new Date(r.time).getUTCMinutes()===0 && new Date(r.time).getUTCHours()%3===0;}).at(-1);
 return 100*(1-FEE)/first*last.c*(1-FEE);
}
function simulate(dataset,mode) {
 if(!["event15m","price15m","legacy3h"].includes(mode))throw new Error("UNSUPPORTED_MODEL_VERSION");
 const rows=dataset.rows,lookup=new Map(rows.map(function(r){return [r.time,r];}));
 let cash=100,oz=0,peak=0,lastSale=-Infinity,lastObservedPrice=null,maxValue=100,maxDD=0,checked=0;
 const trades=[],ledger=[];
 for(let t=ORIGIN;t<END;t+=M15){
  const row=lookup.get(t),tr=TIME.format(new Date(t));
  let action=oz?"HOLD_GOLD":"HOLD_CASH",reason="MARKET_CLOSED_OR_INSUFFICIENT_DATA";
  let phase="NO_FRESH_VERIFIED_PRICE",release="NONE",score=null;
  if(row){
   lastObservedPrice=row.c;
   const isDecision=mode!=="legacy3h" || (new Date(t).getUTCMinutes()===0 && new Date(t).getUTCHours()%3===0);
   const published=RELEASES.filter(function(x){return t>x.ms && t-x.ms<=6*3600000;}).at(-1);
   release=published?published.id:"NONE";
   phase=published?"G01_MACRO_WINDOW_CAUSALITY_UNRESOLVED":"PRICE_PHASE_UNKNOWN_CAUSE";
   if(isDecision){
    checked++;
    if(mode==="event15m"){
     score=analog(row,dataset.events);
     if(score.distance>=1 && row.rv>=.8)phase="OUT_OF_DISTRIBUTION_SHOCK_CAUSE_UNKNOWN";
     if(release!=="NONE"&&score.distance>=1&&row.rv>=.8)phase="MACRO_WINDOW_AND_UNKNOWN_SHOCK";
    }
    if(oz){
     peak=Math.max(peak,row.c);
     const trailing=100*(row.c/peak-1);
     let exitReason=null;
     if(mode==="event15m"){
      const coSell=row.r4<=-1&&row.nq6!==null&&row.nq6<=-1;
      const novelty=score.distance>=1&&row.rv>=.8;
      if(coSell && (score.riskScore>=.2||novelty))exitReason="CROSS_MARKET_UNKNOWN_SHOCK";
      else if(row.r4<=-2&&row.rv>=1.2&&score.distance>=1)exitReason="UNFAMILIAR_PRICE_SHOCK";
     }
     if(!exitReason){
      exitReason=trailing<=-3.5?"TRAILING_DRAWDOWN":
       row.r4<=-2?"FAST_PRICE_DROP":
       row.r92<=-2&&row.r4<0?"MEDIUM_TREND_DOWN":
       row.r276<-2&&row.r4<-.5?"LONGER_TREND_DOWN":null;
     }
     if(exitReason){
      cash=oz*row.p*(1-FEE);oz=0;peak=0;lastSale=t;
      action="SELL_TO_CASH";reason=exitReason;
      trades.push({tr,utc:row.tt,action,price:row.p,cashAfter:cash,reason,phase,
        riskScore:score&&score.riskScore,nearestDistance:score&&score.distance,
        nearestCases:score&&score.nearest});
     }else reason="HOLD_NO_CONFIRMED_LARGE_DOWN";
    }else{
     const entry=row.r92>=1&&row.r276>=0&&row.r4>=-.25&&row.dd276>=-3.5&&row.v92<=4;
     if(entry && t-lastSale>=12*3600000){
      oz=cash*(1-FEE)/row.p;cash=0;peak=row.p;
      action="BUY_GOLD";reason="FROZEN_FIVE_PRICE_QUESTIONS";
      trades.push({tr,utc:row.tt,action,price:row.p,ounces:oz,reason,phase,
       riskScore:score&&score.riskScore,nearestDistance:score&&score.distance,
       nearestCases:score&&score.nearest});
     }else reason="WAIT_NO_CONFIRMED_MARGINAL_UP";
    }
   }else reason="FROZEN_THREE_HOUR_SCHEDULE_WAIT";
  }
  const nav=oz>0 && lastObservedPrice!==null?oz*lastObservedPrice*(1-FEE):cash;
  maxValue=Math.max(maxValue,nav);maxDD=Math.max(maxDD,100*(1-nav/maxValue));
  ledger.push({utc:new Date(t).toISOString(),turkey:tr,hasNewBar:!!row,action,reason,
   position:oz>0?"GOLD":"CASH",phase,macroWindow:release,riskScore:score&&score.riskScore,
   caseDistance:score&&score.distance,nav:Math.round(nav*10000)/10000});
 }
 const last=rows.at(-1);
 const final=oz>0?oz*last.c*(1-FEE):cash;
 const days=[];
 for(let d=1;d<=31;d++){
  const label="2026-01-"+String(d).padStart(2,"0");
  const day=ledger.filter(function(r){return r.turkey.slice(0,10)===label;});
  const lastDay=day.at(-1);
  days.push({date:label,position:lastDay.position,netValue:lastDay.nav,
   completeBars:day.filter(function(r){return r.hasNewBar;}).length,
   actions:day.filter(function(r){return r.action==="BUY_GOLD"||r.action==="SELL_TO_CASH";}).map(function(r){return {when:r.turkey.slice(11),action:r.action};}),
   macroWindows:[...new Set(day.map(function(r){return r.macroWindow;}).filter(function(s){return s!=="NONE";}))]});
 }
 return {
  model:mode,version:VERSION,period:"Ocak 2026",startUSD:100,finalUSD:final,returnPct:final-100,
  maxDrawdownPct:maxDD,benchmarkBuyHoldUSD:benchmark(rows,mode),
  terminalAsset:oz>0?"GOLD":"CASH",goldOunces:oz,checks:checked,
  fullCalendarSlots:ledger.length,completePriceBars:rows.length,archiveCases:dataset.events.length,
  actions:trades,days,ledger
 };
}
function runAll() {
 const data=loadFrozen();
 const event=simulate(data,"event15m");
 const price=simulate(data,"price15m");
 const legacy=simulate(data,"legacy3h");
 if(Math.abs(event.finalUSD-119.75391720039644)>1e-6||
    Math.abs(price.finalUSD-event.finalUSD)>1e-9||
    Math.abs(legacy.finalUSD-118.337853)>0.00002||
    event.actions.length!==2||event.fullCalendarSlots!==2976)throw new Error("FROZEN_REFERENCE_TEST_FAILED");
 return {version:VERSION,inputs:data.inputs,scenarios:{event15m:event,price15m:price,legacy3h:legacy}};
}
module.exports={VERSION,DATA,csvParse,gitBlobHash,decodePinnedSource,loadFrozen,analog,simulate,runAll};
