"use strict";
/** Chronological gold M15 downside alarm → archived scheduled macro calendar audit.
 * No fabricated firstprint; date-only journal items never acquire made-up times.
 * Labels use future prices ONLY after alarm timestamp is frozen, never trading input.
 * Outcomes are overlapping research windows, not independent trading returns.
 */
const fall=require("./downside_news_onset_v1");
const STEP=900000,DAY=86400000,H=3600000;
function fail(message){throw Error("GOLD_NEWS_JOIN_"+message);}
function dt(x){const n=Date.parse(x);if(!Number.isFinite(n))fail("INVALID_TIME_"+x);return n;}
function sampleAlerts(bars){
 const state=fall.create({sourceId:"M15_RESEARCH_ARCHIVE_ONLY"});
 const price=[],alerts=[],gapAlerts=[];
 let prev=-Infinity;
 for(let i=0;i<bars.length;i++){
  const b=bars[i],start=dt(b.bar_start_utc),at=start+STEP;
  if(at<=prev)fail("BARS_NOT_IN_ORDER");
  const mid=(+b.bid_close + +b.ask_close)/2;
  if(!Number.isFinite(mid)||mid<=0||+b.bid_close>+b.ask_close)fail("BAD_BIDASK");
  const obs=fall.observe(state,{asof:new Date(at).toISOString(),
   barStartedAt:b.bar_start_utc,priceAvailableAt:new Date(at).toISOString(),
   price:mid,priceSource:"M15_RESEARCH_ARCHIVE_ONLY",barMinutes:15});
  const entry={time:at,price:mid};
  price.push(entry);prev=at;
  if(obs.newPriceWeakness){
   const alert={alert_id:"DA_"+String(alerts.length+1).padStart(4,"0"),
    index:i,time_utc:entry.time,observed_at:new Date(at).toISOString(),
    alert_kind:obs.gapOpenDislocation?"GAP_OPEN_PRICE_DOWN":"CONTIGUOUS_PRICE_EARLY_WEAKNESS",
    observed_drawdown_pct:obs.drawdownPct,observed_state:obs.phase,
    xau_mid:mid,news_linked_by_early_observer:[],
    trading_action:null,causal_attribution:"UNVERIFIED"};
   alerts.push(alert);if(obs.gapOpenDislocation)gapAlerts.push(alert);
  }
 }
 return {price,alerts,gapAlerts,stateAudit:state.audit};
}
function buildNews(macro,stories){
 const releases=macro.map(x=>{
  if(!x.release_utc||!["CPI","NFP","FOMC"].includes(x.kind))fail("BAD_RELEASE");
  const tm=dt(x.release_utc);
  if(tm<dt("2023-01-01T00:00:00Z")||tm>=dt("2026-01-01T00:00:00Z"))fail("RELEASE_OUTSIDE_2023_2025");
  return {id:x.release_id,kind:x.kind,at:tm,time_utc:x.release_utc,
   provenance:"RESEARCH_MACRO_SCHEDULE_RELEASE_CLOCK_NOT_ORIGINAL_PIT_FIRSTPRINT",
   firstprintCertified:false,mechanismCandidate:(x.kind==="FOMC"?"ORG01|ORG02":"ORG01|ORG02"),isAReleaseCandidate:true};
 }).sort((a,b)=>a.at-b.at);
 const dated=stories.map(x=>{
  if(!/^\d{4}-\d\d-\d\d$/.test(x.newsDate))fail("DATE_ONLY_INVALID");
  return {id:x.id,kind:x.precision||"DATED_HEADLINE",headline:x.headline||"",
   newsDate:x.newsDate,
   reliableHour:typeof x.exactUtc==="string"&&!x.precision?.includes("APPROX")?dt(x.exactUtc):null,
   provenance:x.precision||"UNKNOWN",
   url:x.url||null,firstprintCertified:false};
 });
 return {releases,dated};
}
function horizonLabel(price,i,barCount){
 if(i+barCount>=price.length)return null;
 const origin=price[i].price;
 let low=origin,high=origin;
 for(let k=i+1;k<=i+barCount;k++){
  if(price[k].price<low)low=price[k].price;
  if(price[k].price>high)high=price[k].price;
 }
 return {lowFromAlertPct:+((low/origin-1)*100).toFixed(5),
  highFromAlertPct:+((high/origin-1)*100).toFixed(5),
  furtherDownAtLeast4Pct:low/origin<=.96,
  futureBarCount:barCount,
  // Bar-count horizon; includes weekends/holidays between vendor observations.
  scope:"FUTURE_RESEARCH_LABEL_ONLY_NOT_A_REALTIME_FEATURE"};
}
function audit({bars,macro,stories=[]}){
 if(!Array.isArray(bars)||!Array.isArray(macro)||!Array.isArray(stories))fail("INVALID_DATA");
 const {price,alerts,gapAlerts,stateAudit}=sampleAlerts(bars);
 const {releases,dated}=buildNews(macro,stories);
 const groups={PRE_0_4H:[],PRE_4_24H:[],COINCIDENT_RELEASE_BAR_CLOSE_UNRESOLVED:[],POST_0_4H:[],POST_4_24H:[],NO_HOURLY_MACRO_WITHIN_24H:[]};
 for(const a of alerts){
  const before=releases.filter(r=>r.at<a.time_utc && a.time_utc-r.at<=24*H);
  const coincide=releases.filter(r=>r.at===a.time_utc);
  const after=releases.filter(r=>r.at>a.time_utc && r.at-a.time_utc<=24*H);
  const nearBefore=before.length?before[before.length-1]:null;
  const nearAfter=after.length?after[0]:null;
  const preLag=nearBefore?(a.time_utc-nearBefore.at)/H:null;
  const postLag=nearAfter?(nearAfter.at-a.time_utc)/H:null;
  const role=coincide.length?"COINCIDENT_RELEASE_BAR_CLOSE_UNRESOLVED":
   preLag!==null?(preLag<=4?"PRE_0_4H":"PRE_4_24H"):
   postLag!==null?(postLag<=4?"POST_0_4H":"POST_4_24H"):
   "NO_HOURLY_MACRO_WITHIN_24H";
  const day=new Date(a.time_utc).toISOString().slice(0,10),dayN=dt(day+"T00:00:00Z");
  const storiesNear=dated.filter(s=>Math.abs((dt(s.newsDate+"T00:00:00Z")-dayN)/DAY)<=3)
    .map(s=>({id:s.id,date:s.newsDate,kind:s.kind,headline:s.headline,
      relation:dt(s.newsDate+"T00:00:00Z")<dayN?"BEFORE_ALERT_CALENDAR_DAY":
       dt(s.newsDate+"T00:00:00Z")>dayN?"AFTER_ALERT_CALENDAR_DAY":
       "SAME_CALENDAR_DAY_ORDER_UNKNOWN",
      firstprintTimeKnown:false}));
  a.coincident_macro_at_price_bar_close=coincide.map(x=>({id:x.id,kind:x.kind,time_utc:x.time_utc}));
  a.closest_macro_before=nearBefore?{id:nearBefore.id,kind:nearBefore.kind,
   release_at:nearBefore.time_utc,lag_hours:+preLag.toFixed(2)}:null;
  a.closest_macro_after=nearAfter?{id:nearAfter.id,kind:nearAfter.kind,
   release_at:nearAfter.time_utc,lead_hours:+postLag.toFixed(2)}:null;
  a.macro_chronology_group=role;
  a.other_news_date_only=storiesNear;
  a.future5x96Bars=horizonLabel(price,a.index,480);
  a.future20x96Bars=horizonLabel(price,a.index,1920);
  groups[role].push(a);
 }
 const groupStats=Object.fromEntries(Object.entries(groups).map(([k,x])=>{
  const elig=x.filter(a=>a.future5x96Bars!==null);
  const falls=elig.filter(a=>a.future5x96Bars.furtherDownAtLeast4Pct);
  return [k,{alarms:x.length,eligible5x96:elig.length,
   further4pct5x96:falls.length,
   ratePct:elig.length?+(100*falls.length/elig.length).toFixed(2):null}];
 }));
 const macroByYear=Object.fromEntries([2023,2024,2025].map(y=>[y,releases.filter(e=>
  new Date(e.at).getUTCFullYear()===y).length]));
 const alertsByYear=Object.fromEntries([2023,2024,2025].map(y=>[y,{
  n:alerts.filter(e=>new Date(e.time_utc).getUTCFullYear()===y).length,
  macroBefore24h:alerts.filter(e=>new Date(e.time_utc).getUTCFullYear()===y&&
   e.closest_macro_before!==null).length,
  macroAfter24h:alerts.filter(e=>new Date(e.time_utc).getUTCFullYear()===y&&
   e.closest_macro_after!==null).length,
  dateOnlyStoryWithin3d:alerts.filter(e=>new Date(e.time_utc).getUTCFullYear()===y&&
   e.other_news_date_only.length>0).length}]));
 const events=releases.map(r=>{
  const next4=alerts.filter(a=>a.time_utc>r.at&&a.time_utc<=r.at+4*H);
  const coincident=alerts.filter(a=>a.time_utc===r.at);
  const next24=alerts.filter(a=>a.time_utc>r.at&&a.time_utc<=r.at+24*H);
  const before4=alerts.filter(a=>a.time_utc<r.at&&a.time_utc>=r.at-4*H);
  return {id:r.id,kind:r.kind,release_utc:r.time_utc,original_firstprint_certified:false,
   alerts_pre4h:before4.map(a=>a.alert_id),
   alerts_at_exact_release_close_UNRESOLVED:coincident.map(a=>a.alert_id),
   alerts_post4h:next4.map(a=>a.alert_id),
   alerts_post24h:next24.map(a=>a.alert_id),
   earliest_post4h_hours:next4.length?+((next4[0].time_utc-r.at)/H).toFixed(2):null,
   causal_start_proven:false};
 });
 const alertsFuture=alerts.filter(a=>a.future5x96Bars);
 const baseline=price.map((x,i)=>({i,time:x.time})).filter(x=>x.i>=96&&x.i%16===0&&x.i+480<price.length);
 const baselineDown=baseline.filter(x=>horizonLabel(price,x.i,480).furtherDownAtLeast4Pct).length;
 const alertsNewsBefore=alerts.filter(a=>a.closest_macro_before);
 const alertsNewsAfter=alerts.filter(a=>a.closest_macro_after);
 const knownDayCases=alerts.filter(a=>a.other_news_date_only.length);
 return {
  schema:"GOLD_M15_744_ALERT_TO_MACRO_NEWS_MATCH_V1",
  scope:"2023-2025 vendor M15, 85 archived macro scheduled releases and 17 curated date-only/mixed event candidates.",
  dataQuality:{macroReleaseEvents:releases.length,macroByYear,
   datedResearchHeadlineCandidates:dated.length,actualOriginalFirstprintVerified:0,
   warnings:["85 events only CPI/NFP/FOMC; NOT all global headlines.",
    "Macro schedule does not independently certify as-of firstprint actual/surprise.",
    "17 source stories were selected for known drops and cannot validate population-level association; published day may be posthoc market commentary.",
    "A same-day date-only news entry NEVER acquires a fake noon timestamp.",
    "Events within 24h are time-near, NOT caused alarms.","Next 5x96 observed bars are NOT five calendar days."]},
  alertCounts:{bars:price.length,marketOnlyAlertTotal:alerts.length,gapOpen:gapAlerts.length,
   alertsWithMacroBefore24h:alertsNewsBefore.length,
   alertsWithMacroAfter24h:alertsNewsAfter.length,
   alertsWithAnyMacroWithin24h:alerts.filter(a=>a.closest_macro_before||a.closest_macro_after||a.coincident_macro_at_price_bar_close.length).length,
   alertsAtMacroExactBarCloseUnresolved:alerts.filter(a=>a.coincident_macro_at_price_bar_close.length).length,
   alertsNoMacroWithin24h:alerts.filter(a=>!a.closest_macro_before&&!a.closest_macro_after&&!a.coincident_macro_at_price_bar_close.length).length,
   alarmsWithSelectedHeadlineWithin3calendarDays:knownDayCases.length},
  alertsByYear,
  chronologyGroups:groupStats,
  forwardResearch:{warning:"Outcome labels are future prices for AFTER-THE-FACT scoring; never exposed to online alarm.",
   alert5x96:{eligible:alertsFuture.length,further4:alertsFuture.filter(a=>a.future5x96Bars.furtherDownAtLeast4Pct).length},
   fixed4hAnchor5x96:{eligible:baseline.length,further4:baselineDown}},
  scheduledReleaseEventStudy:{n:events.length,releasesWithAlertWithin4h:events.filter(x=>x.alerts_post4h.length).length,
   releasesWithAlertWithin24h:events.filter(x=>x.alerts_post24h.length).length},
  alertRecords:alerts,macroEventRecords:events,dateOnlyStories:dated,
  sourceIntegrity:stateAudit,
  warnings:["This output cannot say 'X economic news caused Y price decline' without firstprint and counterfactual proof.",
   "The 744 are PRICE ALERTS, not news events or sell orders."],
  tradingActions:0};
}
module.exports={audit,buildNews,horizonLabel};
