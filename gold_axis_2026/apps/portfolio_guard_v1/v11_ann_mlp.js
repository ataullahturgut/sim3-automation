"use strict";
/**
 * Actual nonlinear ANN: 14 normalized as-of inputs -> 12 tanh -> 8 tanh ->
 * 2 real heads (net 4-day / 14-day XAU buy-then-sell returns in percent / 10).
 * Huber backprop + Adam + L2; deterministic seed; fit uses training-only scalers.
 * Research-only. No connection to a bank.
 */
const INPUTS=14,WIDTH1=12,WIDTH2=8,OUTPUTS=2;
function rng(seed){
 let x=seed>>>0;return ()=>{
  x+=0x6d2b79f5;let y=x;
  y=Math.imul(y^(y>>>15),y|1);
  y^=y+Math.imul(y^(y>>>7),y|61);
  return ((y^(y>>>14))>>>0)/4294967296;
 };
}
function init(seed=25){
 const r=rng(seed),random=fan=>((r()*2)-1)*Math.sqrt(6/fan);
 return {W1:Array.from({length:WIDTH1},()=>Array.from({length:INPUTS},()=>random(INPUTS+WIDTH1))),
  b1:Array(WIDTH1).fill(0),
  W2:Array.from({length:WIDTH2},()=>Array.from({length:WIDTH1},()=>random(WIDTH1+WIDTH2))),
  b2:Array(WIDTH2).fill(0),
  W3:Array.from({length:OUTPUTS},()=>Array.from({length:WIDTH2},()=>random(WIDTH2+OUTPUTS))),
  b3:Array(OUTPUTS).fill(0)};
}
function forward(m,x){
 if(x.length!==INPUTS)throw Error("ANN_FEATURE_SHAPE");
 const calc=(W,b,a,nonlinear=true)=>W.map((row,i)=>{
  const z=row.reduce((v,w,j)=>v+w*a[j],b[i]);
  return nonlinear?Math.tanh(z):z;
 });
 const h1=calc(m.W1,m.b1,x),h2=calc(m.W2,m.b2,h1),o=calc(m.W3,m.b3,h2,false);
 return {x,h1,h2,o};
}
function zerosLike(m){
 return Object.fromEntries(Object.entries(m).map(([k,v])=>[k,
   Array.isArray(v[0])?v.map(row=>row.map(()=>0)):v.map(()=>0)]));
}
function huber(error,delta=1.5){
 const a=Math.abs(error);
 return a<delta?[.5*error*error,error]:[delta*(a-.5*delta),delta*Math.sign(error)];
}
function gradient(m,cache,y){
 let g=zerosLike(m),loss=0;
 const dOut=[];
 for(let i=0;i<OUTPUTS;i++){
  const [l,d]=huber(cache.o[i]-y[i]);loss+=l/OUTPUTS;dOut[i]=d/OUTPUTS;
  for(let j=0;j<WIDTH2;j++)g.W3[i][j]+=dOut[i]*cache.h2[j];
  g.b3[i]+=dOut[i];
 }
 const dz2=Array.from({length:WIDTH2},(_,j)=>{
  const a=dOut.reduce((s,d,i)=>s+m.W3[i][j]*d,0);
  return a*(1-cache.h2[j]**2);
 });
 for(let i=0;i<WIDTH2;i++){
  for(let j=0;j<WIDTH1;j++)g.W2[i][j]+=dz2[i]*cache.h1[j];
  g.b2[i]+=dz2[i];
 }
 const dz1=Array.from({length:WIDTH1},(_,j)=>{
  const a=dz2.reduce((s,d,i)=>s+m.W2[i][j]*d,0);
  return a*(1-cache.h1[j]**2);
 });
 for(let i=0;i<WIDTH1;i++){
  for(let j=0;j<INPUTS;j++)g.W1[i][j]+=dz1[i]*cache.x[j];
  g.b1[i]+=dz1[i];
 }
 return {g,loss};
}
function normalizeFit(samples){
 if(samples.some(s=>s.features.length!==INPUTS||s.y.length!==OUTPUTS))
   throw Error("ANN_TRAIN_SHAPE");
 const mean=Array.from({length:INPUTS},(_,i)=>samples.reduce((sum,s)=>sum+s.features[i],0)/samples.length);
 const std=Array.from({length:INPUTS},(_,i)=>{
  const va=samples.reduce((sum,s)=>sum+(s.features[i]-mean[i])**2,0)/samples.length;
  return Math.max(1e-3,Math.sqrt(va));
 });
 return {mean,std};
}
const normalize=(features,scaler)=>features.map((v,i)=>{
 if(!Number.isFinite(v))throw Error("ANN_BAD_INPUT");
 return Math.max(-5,Math.min(5,(v-scaler.mean[i])/scaler.std[i]));
});
function trainEpoch(m,train,scaler,seed,epoch,opts,state){
 const random=rng(seed+epoch*1103515245),indices=train.map((_,i)=>i);
 for(let i=indices.length-1;i>0;i--){let k=Math.floor(random()*(i+1));[indices[i],indices[k]]=[indices[k],indices[i]];}
 const batch=opts.batch||32,lr=opts.lr||.006,l2=opts.l2??.0008;
 for(let start=0;start<indices.length;start+=batch){
  const ids=indices.slice(start,start+batch),grad=zerosLike(m);
  for(const idx of ids){
   const s=train[idx],x=normalize(s.features,scaler),y=s.y.map(v=>Math.max(-4,Math.min(4,v/10)));
   const res=gradient(m,forward(m,x),y).g;
   for(const [k,arr] of Object.entries(grad))
     if(Array.isArray(arr[0]))arr.forEach((row,i)=>row.forEach((_,j)=>{grad[k][i][j]+=res[k][i][j];}));
     else arr.forEach((_,i)=>{grad[k][i]+=res[k][i];});
  }
  state.step++;
  for(const [key,arr] of Object.entries(m)){
   const mat=Array.isArray(arr[0]);
   const apply=(v,i,j)=>{
    const g=(mat?grad[key][i][j]:grad[key][i])/ids.length+
       (key.startsWith("W")?l2*v:0);
    const mm=state.m[key],vv=state.v[key];
    let oldm=mat?mm[i][j]:mm[i],oldv=mat?vv[i][j]:vv[i];
    const newm=.9*oldm+.1*g,newv=.999*oldv+.001*g*g;
    const hatm=newm/(1-Math.pow(.9,state.step));
    const hatv=newv/(1-Math.pow(.999,state.step));
    if(mat){mm[i][j]=newm;vv[i][j]=newv;}
    else{mm[i]=newm;vv[i]=newv;}
    return v-lr*hatm/(Math.sqrt(hatv)+1e-8);
   };
   if(mat)arr.forEach((row,i)=>row.forEach((v,j)=>{row[j]=apply(v,i,j);}));
   else arr.forEach((v,i)=>{arr[i]=apply(v,i);});
  }
 }
}
function evalLoss(m,samples,scaler){
 let loss=0;
 for(const s of samples){
  const y=s.y.map(v=>Math.max(-4,Math.min(4,v/10)));
  const o=forward(m,normalize(s.features,scaler)).o;
  loss+=(huber(o[0]-y[0])[0]+huber(o[1]-y[1])[0])/2;
 }
 return loss/samples.length;
}
function fit(samples,options={}){
 if(samples.length<85)throw Error("ANN_NOT_ENOUGH_MATURED_TRAINING_LABELS");
 // Inputs are chronological; last 20% is prior-period internal validation,
 // NOT 2024/25/26 future test data. Purge 21d to avoid overlapping labels.
 const ordered=[...samples].sort((a,b)=>a.ts-b.ts);
 const split=Math.floor(ordered.length*.8);
 const validation=ordered.slice(split);
 const firstValidation=validation[0].ts;
 const first=ordered.slice(0,split).filter(s=>s.exit14Ts<firstValidation);
 if(first.length<55)throw Error("ANN_PURGE_TOO_SMALL");
 const scaler=normalizeFit(first);
 let model=init(options.seed||17),best=null,bestEpoch=0,bestLoss=Infinity,patience=0;
 const state={m:zerosLike(model),v:zerosLike(model),step:0};
 for(let ep=1;ep<=(options.epochs||80);ep++){
  trainEpoch(model,first,scaler,options.seed||17,ep,options,state);
  const error=evalLoss(model,validation,scaler);
  if(error<bestLoss-1e-5){
   bestLoss=error;bestEpoch=ep;
   best=JSON.parse(JSON.stringify(model));patience=0;
  }else if(++patience>=12)break;
 }
 // Freeze weights at best prior chronological validation epoch. Avoid refitting
 // hyperparameters to the evaluation period. No future labels passed to fit.
 const validationErr=[];
 for(const s of validation){
  const p=forward(best,normalize(s.features,scaler)).o;
  validationErr.push(s.y[1]-p[1]*10);
 }
 const mae14=validationErr.reduce((z,e)=>z+Math.abs(e),0)/validationErr.length;
 const rms14=Math.sqrt(validationErr.reduce((z,e)=>z+e*e,0)/validationErr.length);
 return {weights:best,scaler,trainSize:first.length,validationSize:validation.length,
  bestEpoch,validationHuber:bestLoss,validationMAE14Pct:mae14,
  validationRMSE14Pct:rms14,lastTrainOrigin:first.at(-1).at,
  lastValidationOrigin:validation.at(-1).at};
}
function predict(trained,features){
 const [net4,net14]=forward(trained.weights,normalize(features,trained.scaler)).o;
 return {net4:net4*10,net14:net14*10,validationRMSE14:trained.validationRMSE14Pct};
}
module.exports={INPUTS,WIDTH1,WIDTH2,OUTPUTS,rng,init,forward,gradient,normalizeFit,normalize,fit,predict,huber};
