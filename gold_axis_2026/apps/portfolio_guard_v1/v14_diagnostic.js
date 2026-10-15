"use strict";
const R=require("./v14_karar_run"),B=require("./v13_sentez_run").build();
const x=R.one(B,{start:"2023-01-03T06:00:00Z",end:"2026-09-30T12:00:00Z",
   initial:100,includeDiagnostics:true});
const d=x.diagnostics||[],ready=d.filter(z=>z.learn7>=8&&z.learn28>=3);
const top=ready.slice().sort((a,b)=>b.netScore-a.netScore).slice(0,12)
 .map(z=>({date:z.at,mu:z.mu,down:z.downside,score:z.netScore,
   n7:z.learn7,n28:z.learn28,position:z.position}));
const buckets={};
for(const z of ready){const y=z.at.slice(0,4);
 let a=buckets[y]??(buckets[y]={n:0,max:-Infinity,min:Infinity,pos:0,overFee:0});
 a.n++;a.max=Math.max(a.max,z.netScore);a.min=Math.min(a.min,z.netScore);
 a.pos+=+(z.netScore>0);a.overFee+=+(z.netScore>1.6065);}
console.log(JSON.stringify({final:x.final,trades:x.trades.length,
 feedback:x.feedbackCount,learnt7:x.learned7,learnt28:x.learned28,
 gate:x.learnedGate,ready:ready.length,year:buckets,top},null,2));
