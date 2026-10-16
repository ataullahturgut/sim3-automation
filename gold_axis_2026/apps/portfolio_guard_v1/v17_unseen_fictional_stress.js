"use strict";
/**
 * Independently seeded FICTIONAL stress cases.
 * Frozen V17 parameters; script does not optimize any of them.
 * Not actual XAU/bank series and NOT a claim of external validation.
 */
const A=require("./v16_kavis_siralama"),B=require("./v17_kavis_olay_doubleq");
const f=require("./v17_fictional_scenarios").features;
const day=24*3600000,hr=3600000,base=Date.parse("2020-01-01T00:00:00Z");
const at=(d,h)=>new Date(base+d*day+h*hr).toISOString();
function noise(seed){let x=(seed*9973+887)>>>0;return ()=>{x=(1664525*x+1013904223)>>>0;return x/4294967296;};}
function build(seed){
 const gen=noise(seed),N=360,p=[100];
 let block=40+Math.floor(gen()*55);
 let drift=(gen()-.5)*.03;
 for(let i=1;i<N;i++){
  if(i%block===0){block=40+Math.floor(gen()*55);drift=(gen()-.5)*.03;}
  const ret=drift+.012*(gen()-.5)+(gen()<.012?(gen()-.5)*.17:0);
  p.push(p.at(-1)*Math.exp(ret));
 }
 return p;
}
function run(Model,prices){
 const s=Model.create(),fee=.008;let cash=100,gold=0,pos="CASH",trades=0,peak=100,mdd=0;
 for(let d=0;d<prices.length;d++){
  Model.signal(s,{asof:at(d,6),featureAvailableAt:at(d,6),position:pos,
   market:f(prices,d)});
  const x=Model.quote(s,{at:at(d,9),price:prices[d],isBankCheckpoint:true}).fill;
  if(x.suggestedAction==="BUY"){gold=cash*(1-fee)/prices[d];cash=0;trades++;}
  if(x.suggestedAction==="SELL"){cash=gold*prices[d]*(1-fee);gold=0;trades++;}
  pos=x.positionAfter;
  const nav=cash+gold*prices[d]*(1-fee);
  peak=Math.max(peak,nav);mdd=Math.max(mdd,100*(1-nav/peak));
 }
 return {capital:+(cash+gold*prices.at(-1)*(1-fee)).toFixed(4),
  trades,mdd:+mdd.toFixed(2)};
}
function report(){
 const worlds=[];
 for(let seed=101;seed<=116;seed++){
  const price=build(seed);
  const v16=run(A,price),v17=run(B,price);
  const passive=100*(1-.008)**2*price.at(-1)/price[0];
  worlds.push({seed,v16,v17,passive:+passive.toFixed(4),
    delta:+(v17.capital-v16.capital).toFixed(4)});
 }
 const win=worlds.filter(r=>r.delta>0).length,lose=worlds.filter(r=>r.delta<0).length;
 return {contract:"NEW_DETERMINISTIC_SYNTHETIC_SEEDS_NO_REAL_PRICES",
  parametersFrozenBeforeThisReport:true,worlds,
  summary:{win,lose,tied:worlds.length-win-lose,
    meanV16:worlds.reduce((s,x)=>s+x.v16.capital,0)/worlds.length,
    meanV17:worlds.reduce((s,x)=>s+x.v17.capital,0)/worlds.length,
    meanPass:worlds.reduce((s,x)=>s+x.passive,0)/worlds.length,
    positiveVsCashV17:worlds.filter(x=>x.v17.capital>100).length}};
}
if(require.main===module)console.log(JSON.stringify(report(),null,2));
module.exports={build,run,report};
