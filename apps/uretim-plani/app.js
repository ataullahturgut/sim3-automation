(()=>{'use strict';
const MONTHS=['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık'];
const SHORT=['Oca','Şub','Mar','Nis','May','Haz','Tem','Ağu','Eyl','Eki','Kas','Ara'];
const fmt=n=>Number(n||0).toLocaleString('tr-TR');
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const kClass=q=>q<=0?0:q<=200?1:q<=500?2:q<=1000?3:4;
const partLabel={1:'1 parti',2:'2 parti',3:'3 parti',4:'4 parti'};
const list=document.getElementById('selection'), grid=document.getElementById('calendar');
const state={products:[],scenario:'balanced',oneMonth:5,twoMonth:2,group:1,month:5,product:null,query:'',assignments:[],months:Array.from({length:12},()=>[])};
const quantity=(n,p,k)=>Math.floor(n/p)+(k<n%p?1:0);
function buildPlan(){
 const months=Array.from({length:12},()=>[]),load=Array(12).fill(0),plans=[];
 const all=state.products.filter(p=>p.adet>0).map(p=>({...p,parti:kClass(p.adet)}));
 function assign(p,start){const period=12/p.parti;for(let i=0;i<p.parti;i++){const m=(start+i*period)%12;const item={...p,month:m,partiAdedi:quantity(p.adet,p.parti,i)};months[m].push(item);plans.push(item);load[m]+=item.partiAdedi}}
 const a=all.filter(p=>p.parti===1),b=all.filter(p=>p.parti===2),high=all.filter(p=>p.parti>2).sort((x,y)=>y.adet-x.adet);
 for(const p of a)assign(p,state.oneMonth);
 for(const p of b)assign(p,state.twoMonth);
 for(const p of high){
  let start=0;
  if(state.scenario==='fixed')start=p.parti===3?2:0;
  else if(p.kod==='GA5002'&&p.parti===4)start=0;
  else if(p.kod==='GA5102'&&p.parti===3)start=2;
  else {let best=Infinity;for(let s=0;s<12/p.parti;s++){
    const next=load.slice();for(let i=0;i<p.parti;i++)next[s+i*(12/p.parti)]+=quantity(p.adet,p.parti,i);
    const peak=Math.max(...next),avg=next.reduce((x,y)=>x+y,0)/12;
    const score=peak*100000+next.reduce((sum,x)=>sum+(x-avg)**2,0);
    if(score<best){best=score;start=s}
  }}
  assign(p,start);
 }
 state.months=months;state.assignments=plans;
}
function monthlyOf(group,month){return state.months[month].filter(x=>x.parti===group)}
function monthQty(group,month){return monthlyOf(group,month).reduce((n,x)=>n+x.partiAdedi,0)}
function sumMonth(m){return state.months[m].reduce((n,x)=>n+x.partiAdedi,0)}
function renderStats(){const products=state.products.filter(x=>x.adet>0),sum=products.reduce((a,b)=>a+b.adet,0),count=[1,2,3,4].map(k=>products.filter(p=>kClass(p.adet)===k).length),max=Math.max(...Array.from({length:12},(_,m)=>sumMonth(m)));const cards=[['Yıllık toplam',fmt(sum),'Şönt + harmonik'],['Ürün satırı',fmt(products.length),`${state.products.length-products.length} üretimsiz ürün`],['Yıllık üretim partisi',fmt(count.reduce((s,n,i)=>s+n*(i+1),0)),'1 / 2 / 3 / 4 parti kuralları'],['En yüksek aylık adet',fmt(max),'Makine yükü için başlangıç verisi']];document.getElementById('stats').innerHTML=cards.map(x=>`<div class="stat"><label>${x[0]}</label><strong>${x[1]}</strong><small>${x[2]}</small></div>`).join('')}
function renderCalendar(){let html='<thead><tr><th class="rowname">Üretim sınıfı</th>'+SHORT.map(m=>`<th>${m}</th>`).join('')+'</tr></thead><tbody>';
 for(let g=1;g<=4;g++){
  const count=state.products.filter(p=>kClass(p.adet)===g).length;
  html+=`<tr><th scope="row" class="rowname">${g} parti<small>${count} ürün</small></th>`;
  for(let m=0;m<12;m++){const qty=monthQty(g,m);html+=`<td>${qty?`<button class="g${g} ${state.group===g&&state.month===m?'active':''}" data-g="${g}" data-m="${m}" title="${MONTHS[m]} ${g} parti · ${fmt(qty)} adet">${fmt(qty)}</button>`:''}</td>`}
  html+='</tr>';
 }
 html+='</tbody><tfoot><tr><td class="rowname">Aylık toplam</td>'+SHORT.map((_,m)=>`<td>${fmt(sumMonth(m))}</td>`).join('')+'</tr></tfoot>';
 grid.innerHTML=html;
 grid.querySelectorAll('button[data-g]').forEach(b=>b.addEventListener('click',()=>{state.group=+b.dataset.g;state.month=+b.dataset.m;state.product=null;state.query='';renderCalendar();renderSelection()}));
 const top=Math.max(...Array.from({length:12},(_,m)=>sumMonth(m)))||1;
 document.getElementById('monthly').innerHTML=SHORT.map((m,i)=>`<div class="m"><label>${m}</label><div class="barbox"><div class="bar" style="height:${Math.max(0,100*sumMonth(i)/top)}%"></div></div><div class="qty">${fmt(sumMonth(i))}</div></div>`).join('');
}
const spec=(k,v)=>`<div><dt>${esc(k)}</dt><dd>${v==null||v===''?'Doğrulanmadı':esc(v)}</dd></div>`;
function renderSelection(){
 const rows=monthlyOf(state.group,state.month).sort((a,b)=>b.partiAdedi-a.partiAdedi),total=rows.reduce((x,p)=>x+p.partiAdedi,0);
 if(!total){list.innerHTML='<div class="empty-state">Bu sınıfta seçilen ay için üretim yok.</div>';return}
 if(!state.product||!rows.some(p=>p.id===state.product))state.product=rows[0].id;
 const selected=rows.find(p=>p.id===state.product)||rows[0];
 list.innerHTML=`<div class="selected-head"><div><h2>${MONTHS[state.month]} · ${partLabel[state.group]}</h2><p>${rows.length} ürün satırı · Üretim yapılacak ürünlerin detayları</p></div><div class="quantity">${fmt(total)}<small>adet üretim</small></div></div>
 <div class="detail-layout"><div class="listcard"><div class="card-head"><b>Üretilecek ürünler</b><span>${rows.length} satır</span></div><div class="search-row"><input id="searchProduct" placeholder="Stok kodu, model veya aile ara…" aria-label="Ürün ara" value="${esc(state.query)}"></div><div class="productlist" id="productList"></div></div>
 <div class="techcard"><div class="card-head"><b>Ürün teknik kartı</b><span>Matris verisi</span></div><div class="tech-body" id="techBody"></div></div></div>
 <div class="stack-note">Aynı stok kodu farklı açıklamayla tekrar ediyorsa ayrı ürün satırı olarak korunur. Üretim olmayan aylarda boş hücre gösterilir.</div>`;
 document.getElementById('searchProduct').addEventListener('input',e=>{state.query=e.target.value;renderProductList(rows)});
 renderProductList(rows);renderTech(selected);
}
function renderProductList(rows){
 const term=state.query.toLocaleLowerCase('tr-TR').trim();const filtered=rows.filter(x=>([x.kod,x.model,x.aile,x.grup].join(' ')).toLocaleLowerCase('tr-TR').includes(term));
 const el=document.getElementById('productList');
 el.innerHTML=filtered.length?filtered.map(x=>`<div class="product-item ${state.product===x.id?'selected':''}"><div class="ident"><b>${esc(x.kod)}</b><small title="${esc(x.model)}">${esc(x.model)}</small></div><div class="amount">${fmt(x.partiAdedi)}</div><button class="btn-detail" data-id="${esc(x.id)}" aria-label="${esc(x.kod)} teknik özellikleri">İncele</button></div>`).join(''):'<div class="no-result">Aramaya uygun ürün yok.</div>';
 el.querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>{state.product=b.dataset.id;renderProductList(rows);renderTech(rows.find(x=>x.id===state.product))}));
}
function renderTech(p){const el=document.getElementById('techBody');if(!p)return;
 const kg=typeof p.kg==='number'&&p.kg>0?p.kg:null;
 const verifiedSource=typeof p.kaynak==='string'&&p.kaynak.startsWith('https://')?`<a class="source-link" href="${esc(p.kaynak)}" target="_blank" rel="noopener noreferrer">Kaynak bağlantısını aç ↗</a>`:`<span class="source-link">${esc(p.kaynak||'Belirtilmemiş')}</span>`;
 el.innerHTML=`<h3 class="code-model">${esc(p.kod)}</h3><div class="tech-sub">${esc(p.model)} · ${esc(p.grup)}</div><dl class="spec-grid">${[
 ['Bu ay üretim',fmt(p.partiAdedi)+' adet'],['Yıllık miktar',fmt(p.adet)+' adet'],['Ürün ailesi',p.aile],['Teknik grup',p.altGrup],['Faz',p.faz],['Güç (kVAr)',p.guc],['Akım (A)',p.akim],['Endüktans (mH)',p.L],['p (%)',p.p],['THDv sınıfı',p.thdv],['Dış ölçüler (mm)',p.olcu],['Birim ağırlık (kg)',kg],['Bu parti ağırlığı (kg)',kg!==null?fmt(Math.round(kg*p.partiAdedi*100)/100):null],['Bağlantı',p.baglanti],['Sarım tipi',p.sarim]
 ].map(x=>spec(...x)).join('')}</dl><div class="notice"><b>Teknik veri durumu:</b> ${esc(p.durum||'Doğrulanmadı')}<br>${esc(p.aciklama||'İşlem reçetesi henüz doğrulanmadı.')}</div><div class="stack-note">${verifiedSource}</div>`
}
function downloadCSV(){const header=['Ürün ID','Grup','Stok kodu','Model','Yıllık adet','Parti sayısı','Ay','Parti adedi','Güç kVAr','Akım A','Endüktans mH','Birim kg','Kaynak'];const lines=[header,...state.assignments.map(p=>[p.id,p.grup,p.kod,p.model,p.adet,p.parti,MONTHS[p.month],p.partiAdedi,p.guc,p.akim,p.L,p.kg,p.kaynak])];const text='\ufeff'+lines.map(row=>row.map(x=>'"'+String(x==null?'':x).replace(/"/g,'""')+'"').join(';')).join('\r\n');const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([text],{type:'text/csv;charset=utf-8'}));a.download='sont_harmonik_12_ay_uretim_plani.csv';a.click();URL.revokeObjectURL(a.href)}
function setup(){for(const id of ['oneMonth','twoMonth']){const select=document.getElementById(id);const candidates=id==='twoMonth'?MONTHS.slice(0,6):MONTHS;select.innerHTML=candidates.map((m,i)=>`<option value="${i}">${m}</option>`).join('');select.value=state[id];select.addEventListener('change',e=>{state[id]=+e.target.value;rerender()})}
 document.getElementById('scenario').addEventListener('change',e=>{state.scenario=e.target.value;rerender()});document.getElementById('downloadBtn').addEventListener('click',downloadCSV)}
function rerender(){buildPlan();renderStats();renderCalendar();renderSelection()}
async function load(){try{const b64=window.PRODUCTS_GZIP_B64;if(!b64)throw Error('Ürün verisi bulunamadı');const raw=Uint8Array.from(atob(b64),c=>c.charCodeAt(0));const ds=new DecompressionStream('gzip');const decompressed=await new Response(new Blob([raw]).stream().pipeThrough(ds)).text();state.products=JSON.parse(decompressed);if(state.products.length!==135||state.products.reduce((s,p)=>s+p.adet,0)!==45088)throw Error('Veri toplamı beklenenden farklı');setup();rerender();document.getElementById('sourceBadge').textContent=`${state.products.length} ürün · Veri doğrulandı`;}catch(e){document.getElementById('sourceBadge').textContent='Veri hatası';list.innerHTML=`<div class="empty-state"><strong>Veri yüklenemedi</strong><p>${esc(e.message)}</p></div>`;console.error(e)}}
load();
})();