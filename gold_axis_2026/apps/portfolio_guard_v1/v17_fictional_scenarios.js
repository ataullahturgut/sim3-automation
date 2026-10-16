"use strict";
/**
 * Deterministic fictional stress worlds. NO ACTUAL XAU/BANK DATA.
 * Prices for t are revealed ONLY at the t execution checkpoint.
 * Decision features at t use prices through t-1 (never t+).
 */
const V16=require("./v16_kavis_siralama");
const V17=require("./v17_kavis_olay_doubleq");
const DAY=24*3600000,HOUR=3600000;
const base=Date.parse("2020-01-01T00:00:00Z");
const date=(d,h)=>new Date(base+d*DAY+h*HOUR).toISOString();
const fee=.008;
function rng(seed){let x=seed>>>0;return ()=>{x=(1664525*x+1013904223)>>>0;return x/4294967296;};}
function series(kind){
 const random=rng(91417),steps=kind==="three_regimes"?360:kind==="flash_recovery"?320:300;
 const logPrices=[Math.log(100)];
 for(let d=1;d<steps;d++){
  const u=random()-.5;
  let drift=0;
  if(kind==="three_regimes")drift=d<115?.009:d<235?-.011:.009;
  else if(kind==="flat_noise")drift=.0016*(u*2);
  else if(kind==="whipsaw")drift=d%8<4?.015:-.015;
  else if(kind==="flash_recovery")
    drift=d<120?.0045:d<125?-.05:d<210?.009:0;
  else if(kind==="random_shocks")
    drift=.0008+.018*u+(d%79===4?-.075:0)+(d%91===40?.065:0);
  logPrices.push(logPrices.at(-1)+drift);
 }
 return logPrices.map(x=>Math.exp(x));
}
function features(prices,d){
 const last=Math.max(0,d-1);
 const ln=i=>Math.log(prices[Math.max(0,i)]);
 const r=(n)=>100*(ln(last)-ln(last-n));
 const prev=[];
 for(let j=Math.max(1,last-9);j<=last;j++)
  prev.push(100*(ln(j)-ln(j-1)));
 const mu=prev.length?prev.reduce((a,b)=>a+b,0)/prev.length:0;
 const rv=prev.length?Math.sqrt(prev.reduce((a,b)=>a+(b-mu)**2,0)/prev.length):0;
 const pk=Math.max(...prices.slice(Math.max(0,last-40),last+1));
 return {r4:r(1),r1:r(3),r3:r(8),rv,dd:100*Math.log(prices[last]/pk)};
}
function run(kind,Version,options={},allowEvents=false){
 const prices=series(kind),state=Version.create(options);
 let cash=100,gold=0,pos="CASH",peak=100,mdd=0;
 const moves=[],scoreSample=[],net=[];
 for(let d=0;d<prices.length;d++){
  const event=(allowEvents&&kind==="flash_recovery"&&d===120)?
    [{verifiedFirstPublication:true,firstAvailableAt:date(d,6),
      family:"G05",evidenceId:"SYNTHETIC-PRICE-STRESS",polarity:-.95}]:[];
  const signal=Version.signal(state,{asof:date(d,6),featureAvailableAt:date(d,6),
     position:pos,market:features(prices,d),...(Version===V17?{events:event}:{})});
  const fill=Version.quote(state,{at:date(d,9),price:prices[d],isBankCheckpoint:true}).fill;
  if(fill.suggestedAction==="BUY"){gold=cash*(1-fee)/prices[d];cash=0;}
  else if(fill.suggestedAction==="SELL"){cash=gold*prices[d]*(1-fee);gold=0;}
  pos=fill.positionAfter;
  if(fill.suggestedAction!=="WAIT")moves.push({index:d,action:fill.suggestedAction,
    knownScore:+signal.actionGap.toFixed(3),price:+prices[d].toFixed(2)});
  const nav=cash+gold*prices[d]*(1-fee);
  peak=Math.max(peak,nav);mdd=Math.max(mdd,100*(1-nav/peak));
  net.push(nav);
  if([20,115,124,150,234,250,300].includes(d)&&d<prices.length)
   scoreSample.push({i:d,signal:signal.action,edge:+signal.actionGap.toFixed(3),
    prevPrice:+prices[Math.max(0,d-1)].toFixed(2),fillPrice:+prices[d].toFixed(2)});
 }
 const buyHold=100*(1-fee)**2*prices.at(-1)/prices[0];
 return {scenario:kind,model:Version===V17?"V17":"V16",capital:+net.at(-1).toFixed(3),
  hold:+buyHold.toFixed(3),cash:100,
  peakDrawdownPct:+mdd.toFixed(2),trades:moves.length,moves:moves.slice(0,24),
  learnedIntervals:state.learned,criticUpdates:Version===V17?{
    A:state.audit.updatedA,B:state.audit.updatedB}:null,
  scoreSample,fictional:true};
}
function study(){
 const cases=["three_regimes","flat_noise","whipsaw","flash_recovery","random_shocks"];
 return {status:"FICTIONAL_SYNTHETIC_ONLY",asof:"previous bank price only, current execution revealed after signal",
  feeEachSide:fee,scenarioCount:cases.length,
  rows:cases.flatMap(c=>[run(c,V16),run(c,V17,{},true)])};
}
if(require.main===module)console.log(JSON.stringify(study(),null,2));
module.exports={series,features,run,study};
