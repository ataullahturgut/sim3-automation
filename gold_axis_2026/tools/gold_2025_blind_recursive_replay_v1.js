"use strict";
// Independent scenario runner; derived adapted families, not original CURRENT8 solvers.
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


function monthShift(m,n=1){let [y,k]=m.split("-").map(Number);const d=new Date(Date.UTC(y,k-1+n,1));return d.toISOString().slice(0,7);}
function gaussSeed(){
 // seeded deterministic array, no external randomness
 const rand=rnd(24092026);return ()=>{let a=Math.max(rand(),1e-9),b=rand();return Math.sqrt(-2*Math.log(a))*Math.cos(2*Math.PI*b);};
}
function ANNFit(X,Y,epochs,seed=24092026,hidden=8){
 const gen=rnd(seed),H=hidden,N=X.length;
 let W1=Array.from({length:H},()=>Array.from({length:D},()=>.15*(gen()-.5)));
 let b1=Array(H).fill(0),W2=Array.from({length:D},()=>Array.from({length:H},()=>.1*(gen()-.5))),b2=Array(D).fill(0);
 const weights=[W1.flat(),b1.slice(),W2.flat(),b2.slice()].flat();const sizes=[H*D,H,D*H,D];
 const starts=[0,H*D,H*D+H,H*D+H+D*H];const m=Array(weights.length).fill(0),v=m.slice();
 let val;
 for(let t=1;t<=epochs;t++){
  const g=new Float64Array(weights.length);let err=0;
  for(let n=0;n<N;n++){
   const x=X[n],y=Y[n],z=Array(H);
   for(let h=0;h<H;h++){let s=weights[starts[1]+h];for(let j=0;j<D;j++)s+=weights[h*D+j]*x[j];z[h]=Math.tanh(s);}
   const out=Array(D),delta=Array(D);
   for(let k=0;k<D;k++){let s=weights[starts[3]+k];for(let h=0;h<H;h++)s+=weights[starts[2]+k*H+h]*z[h];out[k]=s;delta[k]=s-y[k];err+=delta[k]*delta[k];}
   const dz=Array(H);
   for(let h=0;h<H;h++){let s=0;for(let k=0;k<D;k++)s+=delta[k]*weights[starts[2]+k*H+h];dz[h]=s*(1-z[h]*z[h]);}
   for(let k=0;k<D;k++){g[starts[3]+k]+=delta[k]/N;for(let h=0;h<H;h++)g[starts[2]+k*H+h]+=delta[k]*z[h]/N;}
   for(let h=0;h<H;h++){g[starts[1]+h]+=dz[h]/N;for(let j=0;j<D;j++)g[h*D+j]+=dz[h]*x[j]/N;}
  }
  const rate=.006,reg=.004;
  for(let i=0;i<weights.length;i++){
   const penalty=(i<starts[1]||(i>=starts[2]&&i<starts[3]))?reg*weights[i]:0;
   const gi=g[i]+penalty;m[i]=.9*m[i]+.1*gi;v[i]=.999*v[i]+.001*gi*gi;
   weights[i]-=rate*(m[i]/(1-Math.pow(.9,t)))/(Math.sqrt(v[i]/(1-Math.pow(.999,t)))+1e-8);
  }
 }
 return {weights,hidden:H,starts};
}
function ANNPredict(model,x){
 const {weights:w,hidden:H,starts:s}=model,z=Array(H);
 for(let h=0;h<H;h++){let a=w[s[1]+h];for(let j=0;j<D;j++)a+=w[h*D+j]*x[j];z[h]=Math.tanh(a);}
 return Array.from({length:D},(_,k)=>{let a=w[s[3]+k];for(let h=0;h<H;h++)a+=w[s[2]+k*H+h]*z[h];return a;});
}
function runBlind2025(source,opt={}){
 const rows=source.monthly.map(x=>({m:x.month,p:METALS.map(z=>Number(x[z]))})).sort((a,b)=>a.m.localeCompare(b.m));
 check(rows.length===180&&rows[0].m==="2010-01"&&rows.at(-1).m==="2024-12","STRICT_2024_12_ONLY");
 for(let i=1;i<rows.length;i++)check(rows[i].m===monthShift(rows[i-1].m),"MISSING_MONTH");
 const samples=[];
 for(let i=2;i<rows.length;i++){
  const a=rows[i-2],b=rows[i-1],t=rows[i],x=b.p.map((v,j)=>Math.log(v/a.p[j])),y=t.p.map((v,j)=>Math.log(v/b.p[j]));
  check(x.every(Number.isFinite)&&y.every(Number.isFinite),"NONFINITE_RETURN");
  samples.push({month:t.m,x,y,origin:b.p[0],actual:t.p[0],tainted:["2026-02","2026-03","2026-04"].includes(t.m)});
 }
 const train=samples.filter(z=>z.month<"2022-01"),validation=samples.filter(z=>z.month>="2022-01"&&z.month<"2025-01");
 const post=[]; // no future-year samples or labels inside model input
 check(train.length>140&&validation.length===36,"SPLIT");
 const xm=Array.from({length:D},(_,i)=>mean(train.map(z=>z.x[i])));
 const xs=Array.from({length:D},(_,i)=>std(train.map(z=>z.x[i]),xm[i]));
 const ym=Array.from({length:D},(_,i)=>mean(train.map(z=>z.y[i])));
 const ys=Array.from({length:D},(_,i)=>std(train.map(z=>z.y[i]),ym[i]));
 const X=a=>scale(a.map(z=>z.x),xm,xs),Y=a=>scale(a.map(z=>z.y),ym,ys);
 const xtr=X(train),ytr=Y(train),xv=X(validation),yv=Y(validation);
 const pop=opt.pop||12,gens=opt.gens||18,repeats=opt.repeats||2;
 const anchor=initAnchor(xtr);let best={val:Infinity};const iter=[];
 for(let i=0;i<repeats;i++){
  const seed=24092026+i*1009,res=hho(seed,anchor,xtr,ytr,xv,yv,pop,gens);
  iter.push({seed,validation_loss:res.val});
  if(res.val<best.val)best=res;
 }
 check(best.theta&&Number.isFinite(best.val),"CHHHO_SELECTION");
 let epbest=0,vmin=Infinity,th=best.theta.slice();
 for(let ep=0;ep<40;ep++){
  const loss=fit(th,xtr,ytr,xv,yv).mse;
  if(loss<vmin){vmin=loss;epbest=ep;}
  th=gradStep(th,xtr,ytr,.01).theta;
 }
 function fitAnfis(used){
  const x=X(used),y=Y(used);let theta=best.theta.slice();
  for(let e=0;e<epbest;e++)theta=gradStep(theta,x,y,.01).theta;
  const result=fit(theta,x,y);check(result.betas,"ANFIS_FINAL_FIT_FAILED");return {theta,betas:result.betas};
 }
 const eCandidates=[50,100,180,300,480,700];const valLoss=[];
 for(const epochs of eCandidates){
  const model=ANNFit(xtr,ytr,epochs);const p=xv.map(x=>ANNPredict(model,x));
  const loss=mean(p.map((row,i)=>mean(row.map((val,j)=>Math.abs(val-yv[i][j])))));
  valLoss.push({epochs,loss});
 }
 const bestAnn=valLoss.reduce((a,b)=>a.loss<=b.loss?a:b);
 const prior=train.concat(validation),full=prior.concat(post);
 const frozenChhho=fitAnfis(prior),frozenAnn=ANNFit(X(prior),Y(prior),bestAnn.epochs);
 const fullChhho=fitAnfis(full),fullAnn=ANNFit(X(full),Y(full),bestAnn.epochs);
 function decode(z){return z.map((a,j)=>a*ys[j]+ym[j]);}
 const predictCh=(mod,x)=>decode(forecast(mod.theta,mod.betas,x.map((v,i)=>(v-xm[i])/xs[i])));
 const predictAnn=(mod,x)=>decode(ANNPredict(mod,x.map((v,i)=>(v-xm[i])/xs[i])));
 const evaluate=items=>items.map(r=>{const out=[["ANFIS",predictCh(frozenChhho,r.x)[0]],["ANN",predictAnn(frozenAnn,r.x)[0]]];return {month:r.month,actual:r.actual,origin:r.origin,models:Object.fromEntries(out.map(([k,v])=>[k,{forecast:r.origin*Math.exp(v),direction_correct:Number(Math.sign(v)===Math.sign(r.actual-r.origin))}]))};});
 const test2025=[]; // score only in isolated post-run evaluator
 const test2026=[];
 function metrics(rows,mod){
  return {n:rows.length,mape_pct:100*mean(rows.map(x=>Math.abs(x.models[mod].forecast-x.actual)/x.actual)),
   direction:rows.reduce((v,x)=>v+x.models[mod].direction_correct,0),sum_ae:rows.reduce((v,x)=>v+Math.abs(x.models[mod].forecast-x.actual),0)};
 }
 const future=[];
 const prev=rows.at(-2).p.slice(),cur=rows.at(-1).p.slice();
 // Recursion performed independently for each model. Unobserved Oct-Dec 2026
 // and all of 2027 are simulated; never cross-feed real values or model outputs.
 for(const name of ["ANFIS","ANN"]){
  let a=prev.slice(),b=cur.slice();
  for(let i=0;i<12;i++){
   const month=monthShift("2024-12",i+1);
   const x=b.map((v,j)=>Math.log(v/a[j]));
   const y=name==="ANFIS"?predictCh(fullChhho,x):predictAnn(fullAnn,x);
   const bounded=y.map(v=>Math.max(-.15,Math.min(.15,v)));
   const p=b.map((v,j)=>v*Math.exp(bounded[j]));
   if(!future[i])future.push({month,kind:"CONDITIONAL_RECURSIVE_NO_FUTURE_OBSERVATIONS",models:{}});
   future[i].models[name]={forecast:p[0],rawGoldMonthlyLogReturn:y[0],monthlyReturnCapped:y[0]!==bounded[0]};
   a=b;b=p;
  }
 }
 return {schema:"2025_BLIND_RECURSIVE_RESEARCH_SCENARIO_V1",status:"BLIND_RESEARCH_NUMERIC_RUN_NOT_ORIGINAL_MONTHLY_MODEL",
 methodLimitations:["NO_GPR_INPUTS; ORIGINAL CHHHO-ANFIS 8D CURRENT8 AND ORIGINAL REDUCED4 ANN NOT EXECUTED","4D monthly-price-return surrogates only, 2025 forward prices recursive and conditional","All Jan-Dec 2025 forecasts recursively simulated from 2024-12 before later scoring","15 percent max absolute monthly return cap for numerical simulation; this is an assumption, not an original model parameter","NO 2025 OR 2026 data are passed to this model","StakTrakr reconstructed daily price firstprints not PIT certified","Validation 2022-2024 is known before asof 2024-12; H1 forecaster recursively rolled blind across 2025"],
 modelSpec:{chhho:"New first-order Sugeno Gaussian five-rule 4-input 4-metal monthly one-step return ANFIS, deterministic logistic chaotic HHO + 0.002 ridge and local gradient",ann:"New feedforward MLP tanh 4->8->4 with Adam and early validation epoch; not original REDUCED4 ANN"},
 runConfig:{lastObserved:"2024-12",lastObservedGold:rows.at(-1).p[0],monthlyRows:rows.length,initialTrain:[train[0].month,train.at(-1).month],validation:[validation[0].month,validation.at(-1).month],frozenFitEnds:"2024-12",fullFitEnds:"2024-12",sourceAnomalyMonthsExcluded:["2026-02","2026-03","2026-04"],trainingN:full.length,hho:{pop,gens,repeats,selection:iter,localEpochs:epbest,validationMSE:vmin},ann:{epochsChosen:bestAnn.epochs,validationOptions:valLoss}},
 heldout2025:null,heldout2026_excluding_outliers:null,monthlyForecast:future,
 heldoutExamples2025:null};
}
module.exports={runBlind2025};
