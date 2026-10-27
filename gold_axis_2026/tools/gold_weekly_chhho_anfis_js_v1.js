"use strict";
/* Research-only weekly ChHHO-ANFIS: chronological source-aligned 4-metal weekly means.
 * New horizon-specific CHHHO adaptation, NOT a reuse of monthly weights.
 * Five Gaussian fuzzy rules, first-order Sugeno consequents (LSE/ridge stabilization).
 * Chaotic-logistic HHO premise selection on 2010-21 training, 2022-24 checking,
 * first-order ANFIS gradient refinement; frozen 2025/2026 transport.
 */
const METALS=["au","ag","pt","pd"],R=5,D=4,K=R*(D+1),T=R*D*2;
const LOW=Array.from({length:T},(_,j)=>j<R*D?-4:Math.log(.2));
const HIGH=Array.from({length:T},(_,j)=>j<R*D?4:Math.log(4));
function check(x,msg){if(!x)throw Error("WEEK_CHHHO_INVALID_"+msg);}
function rnd(seed){let z=seed>>>0;return ()=>((z=(1664525*z+1013904223)>>>0)/4294967296)}
function mean(v){return v.reduce((a,b)=>a+b,0)/v.length}
function std(v,m){return Math.sqrt(mean(v.map(x=>(x-m)**2)))||1}
function scale(raw,mu,sd){return raw.map(x=>x.map((z,i)=>(z-mu[i])/sd[i]))}
function clamp(x,l,h){return Math.max(l,Math.min(h,x))}
function designRow(x,t){
 const logs=new Float64Array(R);let high=-Infinity;
 for(let r=0;r<R;r++){let a=0;for(let j=0;j<D;j++){
  const delta=(x[j]-t[r*D+j])/Math.exp(t[R*D+r*D+j]);
  a+=delta*delta;
 }logs[r]=-0.5*a;if(logs[r]>high)high=logs[r];}
 let norm=0;for(let r=0;r<R;r++){logs[r]=Math.exp(logs[r]-high);norm+=logs[r];}
 const out=new Float64Array(K);
 for(let r=0;r<R;r++){const w=logs[r]/norm;const o=r*(D+1);out[o]=w;for(let j=0;j<D;j++)out[o+j+1]=w*x[j];}
 return out;
}
function solve(chol,vec){
 const n=K;const z=new Float64Array(n),out=new Float64Array(n);
 for(let i=0;i<n;i++){let s=vec[i];for(let j=0;j<i;j++)s-=chol[i*n+j]*z[j];z[i]=s/chol[i*n+i];}
 for(let i=n-1;i>=0;i--){let s=z[i];for(let j=i+1;j<n;j++)s-=chol[j*n+i]*out[j];out[i]=s/chol[i*n+i];}
 return out;
}
function fit(t,X,Y,evalX=null,evalY=null,needGrad=false){
 const n=X.length;const G=new Float64Array(K*K),B=Array.from({length:D},()=>new Float64Array(K));
 const rows=needGrad?[]:null;
 for(let a=0;a<n;a++){
  const v=designRow(X[a],t);if(rows)rows.push(v);
  for(let j=0;j<K;j++){const vv=v[j];for(let o=0;o<D;o++)B[o][j]+=vv*Y[a][o];
   for(let k=0;k<=j;k++)G[j*K+k]+=vv*v[k];}
 }
 for(let j=0;j<K;j++){for(let k=0;k<j;k++)G[k*K+j]=G[j*K+k];G[j*K+j]+=.002;}
 const C=new Float64Array(K*K);let okay=true;
 for(let i=0;i<K;i++){for(let j=0;j<=i;j++){
  let s=G[i*K+j];for(let k=0;k<j;k++)s-=C[i*K+k]*C[j*K+k];
  if(i===j){if(s<=1e-14||!Number.isFinite(s)){okay=false;break;}C[i*K+j]=Math.sqrt(s);}
  else C[i*K+j]=s/C[j*K+j];
 }if(!okay)break;}
 if(!okay)return {loss:1e9,betas:null};
 const betas=B.map(z=>solve(C,z));
 const testX=evalX||X,testY=evalY||Y;
 let ae=0, mse=0;
 for(let a=0;a<testX.length;a++){
  const v=evalX?designRow(testX[a],t):(rows?rows[a]:designRow(X[a],t)); const out=new Float64Array(D);
  for(let o=0;o<D;o++){for(let j=0;j<K;j++)out[o]+=v[j]*betas[o][j];
   const err=out[o]-testY[a][o];ae+=(o===0?.7+.3/D:.3/D)*Math.abs(err);mse+=err*err;}
 }
 return {loss:ae/testX.length,mse:mse/(testX.length*D),betas};
}
function forecast(t,betas,x){const v=designRow(x,t),out=[];
 for(let o=0;o<D;o++){let a=0;for(let j=0;j<K;j++)a+=v[j]*betas[o][j];out.push(a);}
 return out;
}
function gradStep(t,X,Y,rate){
 const z=fit(t,X,Y,null,null,false);if(!z.betas)return {theta:t,mse:Infinity};
 const g=new Float64Array(T);let mse=0;
 for(let a=0;a<X.length;a++){
  const x=X[a],v=designRow(x,t),w=Array.from({length:R},(_,r)=>v[r*(D+1)]);
  const fo=Array.from({length:R},()=>new Float64Array(D));
  const yh=new Float64Array(D);
  for(let r=0;r<R;r++)for(let o=0;o<D;o++){
   let val=z.betas[o][r*(D+1)];
   for(let j=0;j<D;j++)val+=x[j]*z.betas[o][r*(D+1)+j+1];
   fo[r][o]=val;yh[o]+=w[r]*val;
  }
  for(let o=0;o<D;o++)mse+=(yh[o]-Y[a][o])**2;
  for(let r=0;r<R;r++){
   let inf=0;
   for(let o=0;o<D;o++)inf+=(yh[o]-Y[a][o])*w[r]*(fo[r][o]-yh[o]);
   inf*=2/(X.length*D);
   for(let j=0;j<D;j++){
    const p=r*D+j,dx=x[j]-t[p],s2=Math.exp(2*t[R*D+p]);
    g[p]+=inf*dx/s2;g[R*D+p]+=inf*dx*dx/s2;
   }
  }
 }
 let gn=Math.sqrt(g.reduce((s,v)=>s+v*v,0));const next=t.slice();
 if(Number.isFinite(gn)&&gn>1e-13)for(let j=0;j<T;j++)next[j]=clamp(t[j]-rate*g[j]/gn,LOW[j],HIGH[j]);
 return {theta:next,mse:mse/(X.length*D)};
}
function initAnchor(X){
 // Deterministic train-only 5-centre farthest-first approximation to ANFIS kmeans.
 const centers=[X[Math.floor(X.length/2)].slice()];
 while(centers.length<R){
  let idx=0,mx=-1;
  for(let i=0;i<X.length;i++){let md=Infinity;for(const c of centers){let v=0;for(let j=0;j<D;j++)v+=(X[i][j]-c[j])**2;md=Math.min(md,v);}
   if(md>mx){idx=i;mx=md;}}
  centers.push(X[idx].slice());
 }
 const t=Array.from({length:T},()=>0);
 for(let r=0;r<R;r++)for(let j=0;j<D;j++)t[r*D+j]=clamp(centers[r][j],-4,4);
 return t;
}
function chaoticInit(anchor,seed,pop){
 const rng=rnd(seed);let q=.1+.8*rng(),P=[];
 for(let i=0;i<pop;i++){const vec=[];
  for(let j=0;j<T;j++){q=4*q*(1-q);vec.push(LOW[j]+q*(HIGH[j]-LOW[j]));}
  P.push(i===0?anchor.slice():vec);
 }return P;
}
function hho(seed,anchor,X,Y,Xv,Yv,pop,gens){
 const rng=rnd(seed),P=chaoticInit(anchor,seed,pop);
 let F=P.map(t=>fit(t,X,Y).loss),vb=null,vf=Infinity;
 function update(){
  const ranked=Array.from({length:pop},(_,i)=>i).sort((a,b)=>F[a]-F[b]);
  for(const idx of ranked.slice(0,Math.max(3,Math.floor(pop/4)))){
   const loss=fit(P[idx],X,Y,Xv,Yv).loss;if(loss<vf){vf=loss;vb=P[idx].slice();}
  }
 }
 update();
 for(let epoch=0;epoch<gens;epoch++){
  const bi=F.indexOf(Math.min(...F)),rabbit=P[bi],E1=2*(1-(epoch+1)/gens);
  const avg=Array.from({length:T},(_,j)=>mean(P.map(t=>t[j])));
  for(let i=0;i<pop;i++){
   const E=E1*(2*rng()-1),q=rng(),J=2*(1-rng());let cand=new Array(T);
   if(Math.abs(E)>=1){
    if(q>=.5){const other=P[Math.floor(rng()*pop)];for(let j=0;j<T;j++)cand[j]=other[j]-rng()*Math.abs(other[j]-2*rng()*P[i][j]);}
    else for(let j=0;j<T;j++)cand[j]=(rabbit[j]-avg[j])-rng()*(LOW[j]+rng()*(HIGH[j]-LOW[j]));
   }else if(rng()>=.5){for(let j=0;j<T;j++)cand[j]=rabbit[j]-E*Math.abs(J*rabbit[j]-P[i][j]);}
   else{
    const yc=rabbit.map((x,j)=>clamp(x-E*Math.abs(J*x-P[i][j]),LOW[j],HIGH[j]));
    const z=yc.map(x=>x+.01*Math.tan(Math.PI*(rng()-.5)));
    const c2=z.map((x,j)=>clamp(x,LOW[j],HIGH[j]));
    cand=fit(yc,X,Y).loss<=fit(c2,X,Y).loss?yc:c2;
   }
   cand=cand.map((x,j)=>clamp(x,LOW[j],HIGH[j]));
   const loss=fit(cand,X,Y).loss;
   if(loss<F[i]){P[i]=cand;F[i]=loss;}
  }update();
 }
 return {theta:vb,val: vf};
}
function run(data,opt={}){
 const pop=opt.pop||24,gens=opt.gens||45,repeats=opt.repeats||3,local=opt.local||30;
 check(data.length>850,"SHORT_HISTORY");
 const w=data.map(x=>({week:String(x.wk).slice(0,10),mean:METALS.map(m=>Number(x[m])),days:Number(x.cnt)}))
  .filter(x=>x.days>=3).sort((a,b)=>a.week.localeCompare(b.week));
 check(w[0].week==="2010-01-04"&&w.some(x=>x.week==="2026-02-23"),"MISMATCHED_SOURCE");
 const sample=[];
 for(let i=2;i<w.length;i++){
  const prev=w[i-1],back=w[i-2],cur=w[i];
  const feat=prev.mean.map((v,j)=>Math.log(v/back.mean[j]));
  const y=cur.mean.map((v,j)=>Math.log(v/prev.mean[j]));
  sample.push({week:cur.week,X:feat,Y:y,origin:prev.mean[0],actual:cur.mean[0]});
 }
 const train=sample.filter(x=>x.week<"2022-01-01");
 const val=sample.filter(x=>x.week>="2022-01-01"&&x.week<"2025-01-01");
 const test=sample.filter(x=>x.week>="2025-01-01"&&x.week<"2026-01-01");
 const stressEnd=opt.stressEnd||"2026-09-21";
 const stress=sample.filter(x=>x.week>="2026-01-01"&&x.week<=stressEnd);
 check(train.length>600&&val.length>150&&test.length===52&&stress.length===(stressEnd==="2026-10-19"?42:38),"SPLIT");
 const xm=Array.from({length:D},(_,j)=>mean(train.map(x=>x.X[j])));
 const xs=Array.from({length:D},(_,j)=>std(train.map(x=>x.X[j]),xm[j]));
 const ym=Array.from({length:D},(_,j)=>mean(train.map(x=>x.Y[j])));
 const ys=Array.from({length:D},(_,j)=>std(train.map(x=>x.Y[j]),ym[j]));
 const Xtr=scale(train.map(z=>z.X),xm,xs),Ytr=scale(train.map(z=>z.Y),ym,ys);
 const Xv=scale(val.map(z=>z.X),xm,xs),Yv=scale(val.map(z=>z.Y),ym,ys);
 const anchor=initAnchor(Xtr);
 let best={val:Infinity};const reps=[];
 for(let i=0;i<repeats;i++){
  const seed=771100+1009*i+20260105;
  const result=hho(seed,anchor,Xtr,Ytr,Xv,Yv,pop,gens);
  reps.push({repeat:i,seed,validation_loss:result.val});
  if(result.val<best.val)best={...result,repeat:i};
 }
 check(best.theta&&Number.isFinite(best.val),"NO_MODEL_SELECTED");
 // As in canonical monthly protocol: tune number of local gradients on checking
 // sample using inner-train consequents only, then refit consequents on all pre-2025.
 let th=best.theta.slice(),bestEpoch=0,bestMse=Infinity,step=.01;
 for(let ep=0;ep<local;ep++){
  const vl=fit(th,Xtr,Ytr,Xv,Yv).mse;
  if(vl<bestMse){bestMse=vl;bestEpoch=ep;}
  th=gradStep(th,Xtr,Ytr,step).theta;
 }
 // 2010-2024 all is available by 2025-01; fixed scale from train period
 // remains a pre-target transform and no 2025/2026 labels are ever fitted.
 const full=train.concat(val),XF=scale(full.map(z=>z.X),xm,xs),YF=scale(full.map(z=>z.Y),ym,ys);
 th=best.theta.slice();
 for(let ep=0;ep<bestEpoch;ep++)th=gradStep(th,XF,YF,step).theta;
 const fitFull=fit(th,XF,YF);check(fitFull.betas!==null,"FINAL_FIT_FAILED");
 function evaluate(rows){
  return rows.map(x=>{
   const zx=x.X.map((v,j)=>(v-xm[j])/xs[j]);
   const p=forecast(th,fitFull.betas,zx);
   const fp=x.origin*Math.exp(p[0]*ys[0]+ym[0]);
   const risk=["2026-02-23","2026-03-02","2026-03-09"].includes(x.week);
   return {week:x.week,forecast:+fp.toFixed(6),actual:+x.actual.toFixed(6),
    origin:+x.origin.toFixed(6),abs_error:+Math.abs(fp-x.actual).toFixed(6),
    ape:100*Math.abs(fp-x.actual)/x.actual,
    correct:+(Math.sign(fp-x.origin)===Math.sign(x.actual-x.origin)),
    source_anomaly_exposure:risk};
  });
 }
 const scored={dev:evaluate(val),test2025:evaluate(test),stress2026:evaluate(stress)};
 function metric(rows){return {n:rows.length,MAPE:mean(rows.map(x=>x.ape)),sumAE:rows.reduce((a,x)=>a+x.abs_error,0),
  direction:rows.reduce((a,x)=>a+x.correct,0),pctDirection:100*mean(rows.map(x=>x.correct))};}
 const cleaned=scored.stress2026.filter(z=>!z.source_anomaly_exposure);
 const result={status:"WEEKLY_CHHHO_ANFIS_REAL_NUMERICAL_RUN_RESEARCH_ONLY",
  architecture:"FIRST_ORDER_SUGENO_FIVE_GAUSSIAN_RULES_FOUR_METAL_RETURNS_4_INPUT_4_OUTPUT",
  caveat:"NEW_WEEKLY_ADAPTATION_NOT_ORIGINAL_MONTHLY_CHHHO_WEIGHTS; FOUR_INPUTS_VS_ANN_SIXTEEN; RESEARCH_PRICE_NOT_FIRSTPRINT",
  optimizer:{name:"CHAOTIC_HHO_PREMISE_AND_ANFIS_LOCAL_GRADIENT",population:pop,generations:gens,
   repeats,validation_repeats:reps,local_epochs_selected:bestEpoch,
   local_mse:bestMse,validation_loss:best.val,ridge:.002},
  training:{trainFrom:train[0].week,trainTo:train.at(-1).week,trainN:train.length,stressEnd,checkFrom:val[0].week,
   checkTo:val.at(-1).week,checkN:val.length,frozenFitEnd:full.at(-1).week,
   fittedUsing2025:false,fittedUsing2026:false},metrics:{
   CHECK_2022_2024_IN_SAMPLE_FINAL_REFIT_NOT_OOS:metric(scored.dev),TEST_2025:metric(scored.test2025),STRESS_2026:metric(scored.stress2026),
   STRESS_2026_QUARANTINE_3W:metric(cleaned)
  },periods:{stress2026:scored.stress2026,test2025:scored.test2025},
  priceSource:{repository:"lbruton/StakTrakr",oldCommit:"ed2e549f82ba0d1cd3ca32842b82d3888d301e01",
   newCommit:"02964d0324dde362099976c867f5077a369acaa5",db:"Gold Control Neon",readOnly:true},
  exclusion:["2026-02-23","2026-03-02","2026-03-09"]};
 return result;
}
if(typeof module!=="undefined")module.exports={run};
