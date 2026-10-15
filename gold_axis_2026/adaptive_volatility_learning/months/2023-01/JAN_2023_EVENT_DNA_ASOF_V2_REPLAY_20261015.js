#!/usr/bin/env node
/**
 * JAN-2023 OLAY / DNA / PORTFOLIO V2
 * Reproducible origin-safe 15m January 2023 exploratory replay.
 * INPUT: JAN_2023_EVENT_DNA_ASOF_V2_PANEL_20261015.csv
 * OUTPUTS: Jan event ledger (2976 clock slots), result JSON.
 *
 * DISCLAIMER: This is NOT a trained economic-causal model, a validated OOS
 * model, or a direct bank quote. Economic group hypotheses are candidates.
 * Macro event dates are source-calendar release availability times, NEVER
 * a license to use revised reports or later prices before publication.
 */
"use strict";
const fs = require("fs");
const fee = 0.008;
const START = Date.parse("2022-12-31T21:00:00.000Z"); // 2023-01-01 00:00 TRT
const END = Date.parse("2023-01-31T21:00:00.000Z"); // 2023-02-01 00:00 TRT
const TICK = 15 * 60 * 1000;
const DTF = new Intl.DateTimeFormat("sv-SE", {timeZone:"Europe/Istanbul",
  year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",hour12:false});
const releases = [
 ["JOLTS","2023-01-04T15:00:00Z","BLS"],
 ["FOMC_MINUTES","2023-01-04T19:00:00Z","Federal Reserve"],
 ["NFP","2023-01-06T13:30:00Z","BLS"],
 ["CPI","2023-01-12T13:30:00Z","BLS"],
 ["PPI_RETAIL","2023-01-18T13:30:00Z","BLS + US Census"],
 ["GDP","2023-01-26T13:30:00Z","BEA"],
 ["PCE","2023-01-27T13:30:00Z","BEA"],
 ["ECI","2023-01-31T13:30:00Z","BLS"]
].map(([id,iso,source])=>({id,iso,source,ms:Date.parse(iso)}));

const HEADER = ["tt","close","p","r4","r92","r276","rise400","dd92","nq1","nq6","zn1"];
function parsePanel(path) {
 const lines = fs.readFileSync(path,"utf8").trim().split(/\r?\n/);
 if(lines[0] !== HEADER.join(","))throw new Error("Unexpected panel columns");
 const ans = lines.slice(1).map(line=>{
  const x=line.split(","),r={tt:x[0]};
  for(let j=1;j<HEADER.length;j++)r[HEADER[j]]=x[j]===""?null:Number(x[j]);
  r.ms=Date.parse(r.tt);
  if(!Number.isFinite(r.ms) || !Number.isFinite(r.close) || !Number.isFinite(r.p))throw new Error("Bad row");
  return r;
 });
 for(let i=1;i<ans.length;i++)if(ans[i].ms<=ans[i-1].ms)throw new Error("Non-monotone panel");
 if(ans.length!==1764)throw new Error("Panel count changed: validate source and rerun audit");
 return ans;
}
function eventAt(row,all){
 const release=releases.filter(z=>row.ms>z.ms&&row.ms-z.ms<=6*3600*1000).at(-1);
 if(!release)return {event:"NONE",phase:"P0_OR_NO_VERIFIED_RELEASE",up:false,down:false};
 const before=all.filter(z=>z.ms<=release.ms).at(-1);
 if(!before)return {event:release.id,phase:"G07_UNRESOLVED_NO_ANCHOR",up:false,down:false};
 const reaction=100*(row.close/before.close-1);
 const up=reaction>=.45&&row.r4>=.3&&row.nq1!==null&&row.nq1>=-.25&&row.zn1!==null&&row.zn1>=.02;
 const down=reaction<=-1.5&&row.r4<=-1&&row.nq1!==null&&row.nq1<=-.5&&row.zn1!==null&&row.zn1<=-.04;
 return {event:release.id,phase:up?"P2_G01A_CANDIDATE":down?"P2_G01B_CANDIDATE":"P2_G07_UNRESOLVED",up,down,reaction_pct:+reaction.toFixed(4)};
}
function esc(v){let s=String(v??"");return /[",\n]/.test(s)?'"'+s.replace(/"/g,'""')+'"':s}
function replay(panel){
 const lookup=new Map(panel.map(x=>[x.ms,x]));
 let qty=0,cash=100,lastClose=null,peak=0,peakEq=100,drawMax=0,lastExit=-Infinity;
 let eventsSeen=[],trades=[],ledger=[],tradesByDay={},qualified=0,phaseCounts={},sideChecks=0;
 for(let ms=START;ms<END;ms+=TICK){
  const row=lookup.get(ms),iso=new Date(ms).toISOString(),tr=DTF.format(new Date(ms));
  let action=qty?"HOLD_GOLD":"HOLD_CASH",basis="NO_FRESH_QUALIFIED_M15",phase="P0_OR_NO_VERIFIED_RELEASE",event="NONE",reaction=null;
  if(row){
   qualified++;lastClose=row.close;
   const m=eventAt(row,panel);
   phase=m.phase;event=m.event;reaction=m.reaction_pct??null;
   phaseCounts[phase]=(phaseCounts[phase]||0)+1;
   const hasMarket=row.nq1!==null&&row.zn1!==null;
   if(hasMarket)sideChecks++;
   const trend=(row.rise400>=3&&row.r4>=.25&&row.r92>=0&&row.r276>=0&&
      hasMarket&&row.nq1>=-.25&&row.zn1>=-.10);
   const macro=(m.up&&row.r4>=.3&&row.r92>=0);
   if(qty===0 && ms-lastExit>=72*3600*1000 && (trend||macro)){
    qty=cash*(1-fee)/row.p;cash=0;peak=row.close;
    action="BUY_GOLD";basis=trend?"PRICE_AND_CROSS_ASSET":"PUBLISHED_MACRO_AND_CROSS_ASSET";
    const tx={time_utc:iso,time_tr:tr,action,price:row.p,quantity:qty,reason:basis,phase,event,
      r4:row.r4,r92:row.r92,r276:row.r276,rise400:row.rise400,nq1:row.nq1,zn1:row.zn1};
    trades.push(tx);
   } else if(qty>0) {
    peak=Math.max(peak,row.close);
    const trailing=100*(row.close/peak-1);
    const joint=row.r4<=-1.5&&row.nq6!==null&&row.nq6<=-1;
    const breakdown=trailing<=-3&&row.r4<=-.8&&(
      row.nq6!==null&&row.nq6<=-.8||row.zn1!==null&&row.zn1<=-.1);
    const macroDn=m.down&&row.r4<=-1.5;
    if(joint||breakdown||macroDn){
     cash=qty*row.p*(1-fee);qty=0;lastExit=ms;
     action="PROTECT_TO_CASH";basis=joint?"CROSS_ASSET_SELL":breakdown?"CONFIRMED_BREAKDOWN":"PUBLISHED_MACRO_DOWN";
     trades.push({time_utc:iso,time_tr:tr,action,price:row.p,cash_after:cash,reason:basis,event,phase,
       r4:row.r4,nq6:row.nq6,zn1:row.zn1,trailing});
    }else basis="PRICE_OR_EVENT_RISK_BELOW_NET_COST_GATE";
   } else basis="NO_CONFIRMED_MAJOR_UP_EVENT";
   eventsSeen.push({utc:iso,event,phase,reaction_pct:reaction});
  }
  const nav=qty>0&&lastClose!==null?qty*lastClose*(1-fee):cash;
  peakEq=Math.max(peakEq,nav);
  drawMax=Math.max(drawMax,100*(1-nav/peakEq));
  ledger.push({time_utc:iso,time_tr:tr,source_status:row?"FULL_M15_ASOF_COMPLETE":"CLOSED_OR_INSUFFICIENT_LOOKBACK",
    event,phase,action,reason:basis,position:qty?"GOLD":"CASH",gold_oz:qty,cash_usd:cash,
    xau_mid:lastClose,nav_if_liquidated:nav,event_reaction:reaction,
    r4:row?.r4,r92:row?.r92,r276:row?.r276,rise400:row?.rise400,nq1:row?.nq1,zn1:row?.zn1});
 }
 const last=panel.at(-1);
 if(last.ms!==END)throw new Error("Missing next-boundary final valuation");
 const janEndingQty=qty,janEndingCash=cash;
 const marked=qty?qty*last.close:cash;
 const ifLiquidated=qty?qty*last.close*(1-fee):cash;
 const benchmarkBuy=1826.197; // Earliest complete M15 open on 2023-01-02 23:15 UTC.
 const benchmark=100*(1-fee)/benchmarkBuy*last.close*(1-fee);
 return {ledger,trades,eventsSeen,result:{
  portfolio_start_usd:100,start_asset:"CASH",end_asset:qty?"GOLD":"CASH",
  ending_gold_oz:janEndingQty,ending_cash_usd:janEndingCash,
  gold_mid_final: last.close,mtm_before_hypothetical_sale_fee:marked,
  nav_if_liquidated:ifLiquidated,net_pct_if_liquidated:ifLiquidated-100,
  buyhold_same_vendor_first_full_bar_price:benchmarkBuy,
  buyhold_if_liquidated:benchmark,passive_advantage_usd:benchmark-ifLiquidated,
  max_dd_liquidation_marked_pct:drawMax,trades,clock_slots:ledger.length,
  fresh_qualified_slots:qualified,no_or_insufficient_data_slots:ledger.length-qualified,
  valid_complete_crossasset_checks:sideChecks,phaseCounts,
  month_boundary_time_utc:last.tt,source_id:"HISTDATA_XAUUSD_M1_FIXED_EST_M15_2022_2024_QC_CANDIDATE_V1",
  market_vintage:"HISTORICAL_RETRIEVED_IN_2026_NOT_LIVE",
  fills:"NEXT_M15_OPEN_MID_PROXY",fee_each_side:fee,bank_spread_included:false,
  validation:"EX_POST_DISCOVERY_NOT_BLIND",automatic_live_use:false
 }};
}
function main(){
 const input=process.argv[2]||"JAN_2023_EVENT_DNA_ASOF_V2_PANEL_20261015.csv";
 const prefix=process.argv[3]||"JAN_2023_EVENT_DNA_ASOF_V2";
 const results=replay(parsePanel(input));
 const fields=["time_utc","time_tr","source_status","event","phase","action","reason","position",
 "gold_oz","cash_usd","xau_mid","nav_if_liquidated","event_reaction","r4","r92","r276","rise400","nq1","zn1"];
 fs.writeFileSync(prefix+"_15M_LEDGER.csv",fields.join(",")+"\n"+results.ledger.map(x=>fields.map(k=>esc(x[k])).join(",")).join("\n")+"\n");
 fs.writeFileSync(prefix+"_RESULT.json",JSON.stringify(results.result,null,2)+"\n");
 console.log(JSON.stringify({...results.result,trades:results.trades},null,2));
}
if(require.main===module)main();
module.exports={parsePanel,replay};
