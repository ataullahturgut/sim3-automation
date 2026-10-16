"use strict";
/**
 * 64 fabricated price worlds × two proportional bank-fee regimes.
 * 8 adversarial scenario classes, deterministic seeded transitions,
 * no real-market dataset. This is research, NOT blind financial validation.
 * All decisions use strictly prefix-only price features.
 */
const Old=require("./v17_kavis_olay_doubleq");
const New=require("./v18_kavis_dayaniqlilik");
const HR=3600000,DAY=24*HR,base=Date.parse("2020-01-01T00:00:00Z");
const dt=(i,h)=>new Date(base+i*DAY+h*HR).toISOString();
function rng(seed){let x=seed>>>0;return()=>{x=(1664525*x+1013904223)>>>0;return x/4294967296;};}
function series(mode,seed){
 const random=rng(seed*971+191),N=300,p=[100],period=25+Math.floor(random()*75);
 for(let t=1;t<N;t++){
  let r=0;
  if(mode==="slow_ramp")r=t<150?.005:-.006;
  if(mode==="gap_crash")r=.004+(t%77===0?-.31:0)+(t%77===2?.16:0);
  if(mode==="false_break")r=t%90<6?.04:t%90<18?-.015:.001;
  if(mode==="flat_trap")r=t<180?.00008:t<240?.02:-.015;
  if(mode==="whipsaw")r=t%6<3?.018:-.019;
  if(mode==="random_walk")r=(random()-.5)*.045;
  if(mode==="fat_tails")r=(random()-.5)*.023+(random()<.025?(random()-.5)*.4:0);
  if(mode==="regime_flip")r=Math.floor(t/period)%2===0?.008:-.009;
  r+=(random()-.5)*(mode==="random_walk"?.007:.009);
  p.push(p.at(-1)*Math.exp(r));
 }
 return p;
}
function features(p,i){
 const last=Math.max(0,i-1),log=j=>Math.log(p[Math.max(0,j)]);
 const window=[];for(let j=Math.max(1,last-11);j<=last;j++)window.push(100*(log(j)-log(j-1)));
 const avg=window.length?window.reduce((a,b)=>a+b,0)/window.length:0;
 const v=window.length?Math.sqrt(window.reduce((a,b)=>a+(b-avg)**2,0)/window.length):0;
 const high=Math.max(...p.slice(Math.max(0,last-50),last+1));
 return {r4:100*(log(last)-log(last-1)),
   r1:100*(log(last)-log(last-3)),r3:100*(log(last)-log(last-8)),
   rv:v,dd:100*Math.log(p[last]/high)};
}
function replay(Model,p,fee){
 const s=Model.create({feePerSide:fee});
 let position="CASH",cash=100,ounces=0,trades=0,peak=100,maxDD=0,minCapital=100,signals=0;
 for(let i=0;i<p.length;i++){
  const sig=Model.signal(s,{asof:dt(i,6),featureAvailableAt:dt(i,6),
    position,market:features(p,i)});
  const fill=Model.quote(s,{at:dt(i,9),price:p[i],isBankCheckpoint:true,
    ...(Model===New?{bankFeePerSide:fee,confirmedExtremeQuote:true}:{})}).fill;
  if(!fill)throw Error("UNEXPECTED_MISSING_FILL");
  if(fill.suggestedAction==="BUY"){ounces=cash*(1-fee)/p[i];cash=0;trades++;}
  if(fill.suggestedAction==="SELL"){cash=ounces*p[i]*(1-fee);ounces=0;trades++;}
  position=fill.positionAfter;
  const nav=cash+ounces*p[i]*(1-fee);
  if(!Number.isFinite(nav)||nav<=0)throw Error("BAD_NET_ASSET_VALUE");
  peak=Math.max(peak,nav);minCapital=Math.min(minCapital,nav);
  maxDD=Math.max(maxDD,100*(1-nav/peak));
  if(sig.action!=="WAIT")signals++;
 }
 return {capital:+(cash+ounces*p.at(-1)*(1-fee)).toFixed(4),
   maxDrawdown:+maxDD.toFixed(3),trades,signals,
   learned:s.learned,minCapital:+minCapital.toFixed(3)};
}
function pct(a,p){const s=[...a].sort((x,y)=>x-y);return s[Math.floor((s.length-1)*p)];}
function run(){
 const modes=["slow_ramp","gap_crash","false_break","flat_trap","whipsaw","random_walk","fat_tails","regime_flip"];
 const rows=[];
 for(const mode of modes)for(let k=1;k<=8;k++){
  const seed=8000+97*k+modes.indexOf(mode)*307,p=series(mode,seed);
  for(const fee of [.008,.025]){
   const v17=replay(Old,p,fee),v18=replay(New,p,fee);
   const hold=100*(1-fee)**2*p.at(-1)/p[0];
   rows.push({mode,seed,fee,v17,v18,hold:+hold.toFixed(4),
     delta:+(v18.capital-v17.capital).toFixed(4)});
  }
 }
 const ds=rows.map(x=>x.delta),cap=rows.map(x=>x.v18.capital),
  mdd=rows.map(x=>x.v18.maxDrawdown);
 return {contract:"128_FICTIONAL_ADVERSARIAL_WORLDS_ONLY",worlds:rows.length,
  simulationIsNotBlindValidation:true,
  summary:{v18Wins:ds.filter(x=>x>0).length,v18Losses:ds.filter(x=>x<0).length,
    ties:ds.filter(x=>x===0).length,deltaMedian:pct(ds,.5),
    v18MedianCapital:pct(cap,.5),v18WorstCapital:Math.min(...cap),
    v18MedianMDD:pct(mdd,.5),v18P95MDD:pct(mdd,.95),
    v18BeatsCash:rows.filter(x=>x.v18.capital>100).length,
    v18BeatsHold:rows.filter(x=>x.v18.capital>x.hold).length,
    meanV17:rows.reduce((a,b)=>a+b.v17.capital,0)/rows.length,
    meanV18:rows.reduce((a,b)=>a+b.v18.capital,0)/rows.length},
  feeBreakdown:[.008,.025].map(f=>{const a=rows.filter(x=>x.fee===f);
   return {fee:f,count:a.length,v18Wins:a.filter(x=>x.delta>0).length,
    medCapital:pct(a.map(x=>x.v18.capital),.5),
    worstCapital:Math.min(...a.map(x=>x.v18.capital))};}),
  rows};
}
if(require.main===module)console.log(JSON.stringify(run(),null,2));
module.exports={rng,series,features,replay,run};
