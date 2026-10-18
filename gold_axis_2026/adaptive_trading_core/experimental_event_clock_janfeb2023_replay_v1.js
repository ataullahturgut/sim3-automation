"use strict";
/** GOLD-ADAPTIVE-MODEL-APP-01: Jan-Feb 2023 read-only three-arm event metric replay.
 * Research only. This REPRODUCES FAST S2 prices/phase in shadow; it does NOT run
 * actual S1 forecasting, actual S3 trades or certified macro firstprint.
 * Run: node experimental_event_clock_janfeb2023_replay_v1.js < observations.json
 * stdin: {bars:[{bar_start_utc,bid_close,ask_close}],events:[{id,release,conditions}]}
 */
const STEP=900000, MIN=60000;
function s2state(){return {window:[],active:null,lastAt:null,starts:0,ends:0,gaps:0,resets:0};}
function s2(s,t,price,reset){
 if(reset){s.window=[];s.active=null;s.lastAt=null;s.resets++;}
 if(s.lastAt!==null&&t-s.lastAt!==STEP){s.window=[];s.active=null;s.gaps++;}
 s.window.push(price);if(s.window.length>17)s.window.shift();
 let z=null,phase="WARMUP";
 if(s.window.length===17){
  const w=s.window;let sq=0;
  for(let i=1;i<17;i++)sq+=Math.log(w[i]/w[i-1])**2;
  const vol=Math.max(.0001,Math.sqrt(sq));
  z=Math.max(-6,Math.min(6,Math.log(price/w[0])/vol));
  if(!s.active){
   if(Math.abs(z)>=1.25){
    s.active={direction:Math.sign(z),extreme:price,misses:0,phase:"START"};
    s.starts++;phase="START";
   }else phase="NEUTRAL";
  }else{
   const a=s.active;a.misses=a.direction*z<=.2?a.misses+1:0;
   if(a.misses>=2){s.active=null;s.ends++;phase="END";}
   else{
    a.extreme=a.direction>0?Math.max(a.extreme,price):Math.min(a.extreme,price);
    const retreat=a.direction>0?Math.log(a.extreme/price)/vol:Math.log(price/a.extreme)/vol;
    phase=retreat>=.7?"PULLBACK":a.phase==="PULLBACK"?"REENTRY":"CONTINUE";
    a.phase=phase;
   }
  }
 }
 s.lastAt=t;
 return {phase,direction:s.active?.direction??0,trendZ:z===null?null:+z.toFixed(5),ready:z!==null};
}
function replay({bars,events}){
 const quote=bars.map(x=>({t:Date.parse(x.bar_start_utc)+STEP,p:(+x.bid_close+ +x.ask_close)/2}));
 for(let i=1;i<quote.length;i++)if(!(quote[i].t>quote[i-1].t))throw Error("NONMONOTONE_OR_DUPLICATE_BARS");
 const at=new Map(quote.map(x=>[x.t,x]));
 const active=events.map(x=>({...x,t:Date.parse(x.release),seen:false,base:null,preVol:null}));
 const G=s2state(),RESET=s2state(),all=[],audit={bars:quote.length,quietBars:0,eventBars:0,firstEvents:0};
 for(const q of quote){
  let newEvent=null;
  for(const e of active)if(!e.seen&&q.t>e.t&&q.t<=e.t+STEP){
   newEvent=e;e.seen=true;e.base=at.get(e.t)?.p??null;
   const pre=[];for(let i=16;i>=0;i--){let b=at.get(e.t-i*STEP);if(b)pre.push(b.p);}
   if(pre.length===17){let sq=0;for(let i=1;i<17;i++)sq+=Math.log(pre[i]/pre[i-1])**2;e.preVol=Math.sqrt(sq);}
   audit.firstEvents++;break;
  }
  const g=s2(G,q.t,q.p,false),b=s2(RESET,q.t,q.p,!!newEvent);
  let isEvent=false;
  for(const e of active){
   const elapsed=(q.t-e.t)/MIN;if(!e.seen||elapsed<15||elapsed>240||elapsed%15)continue;
   isEvent=true;
   const pricePct=e.base===null?null:100*Math.log(q.p/e.base);
   const eventZ=pricePct!==null&&e.preVol!==null&&e.preVol>0?pricePct/(100*e.preVol*Math.sqrt(elapsed/240)):null;
   const direction=eventZ!==null&&Math.abs(eventZ)>=1.25?Math.sign(eventZ):0;
   const fwd=m=>at.get(q.t+m*MIN)?.p;
   const futur=m=>fwd(m)===undefined?null:+(100*Math.log(fwd(m)/q.p)).toFixed(5);
   all.push({id:e.id,elapsedMinutes:elapsed,at:new Date(q.t).toISOString(),
    A:g,B:b,C:{global:g,eventPct:pricePct===null?null:+pricePct.toFixed(5),
      eventVolZ:eventZ===null?null:+eventZ.toFixed(4),eventDirection:direction,
      eventReady:elapsed>=30&&eventZ!==null},
    future60Pct:futur(60),future240Pct:futur(240)});
  }
  if(isEvent)audit.eventBars++;else audit.quietBars++;
 }
 const scores={};for(const elapsed of [15,30,60,120,240]){
  const arr=all.filter(x=>x.elapsedMinutes===elapsed&&x.future60Pct!==null);
  const perf=side=>{
   const predict=x=>side==="A"?{ready:x.A.ready,d:x.A.direction}:side==="B"?{ready:x.B.ready,d:x.B.direction}:{ready:x.C.eventReady,d:x.C.eventDirection};
   return {n:arr.length,correct:arr.filter(x=>predict(x).ready&&predict(x).d!==0&&Math.sign(x.future60Pct)===predict(x).d).length,
    wrong:arr.filter(x=>predict(x).ready&&predict(x).d!==0&&Math.sign(x.future60Pct)!==predict(x).d).length,
    abstain:arr.filter(x=>!predict(x).ready||predict(x).d===0).length};
  };
  scores[elapsed]={A:perf("A"),B:perf("B"),eventOnlyC:perf("C")};
 }
 return {audit:{...audit,A:{starts:G.starts,ends:G.ends,gaps:G.gaps},B:{starts:RESET.starts,ends:RESET.ends,gaps:RESET.gaps,resets:RESET.resets}},events:active.map(e=>({id:e.id,release:e.release,conditions:e.conditions,firstPriceBefore:e.base,pre4hVol:e.preVol})),scoresNext60:scores,records:all};
}
const DEFAULT_EVENTS=[
 {id:"NFP_2023-01-06",release:"2023-01-06T13:30:00Z",conditions:["K03","K18","K19"]},
 {id:"CPI_2023-01-12",release:"2023-01-12T13:30:00Z",conditions:["K02"]},
 {id:"NFP_2023-02-03",release:"2023-02-03T13:30:00Z",conditions:["K03","K19"]},
 {id:"CPI_2023-02-14",release:"2023-02-14T13:30:00Z",conditions:["K05"]}
];
module.exports={replay,s2,s2state,DEFAULT_EVENTS};
if(require.main===module){
 const fs=require("node:fs");
 const input=JSON.parse(fs.readFileSync(0,"utf8"));
 const result=replay({bars:input.bars,events:input.events??DEFAULT_EVENTS});
 process.stdout.write(JSON.stringify(result,null,2)+"\n");
}
