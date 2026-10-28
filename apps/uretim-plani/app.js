(()=>{'use strict';
const MONTHS=['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık'];
const SHORT=['Oca','Şub','Mar','Nis','May','Haz','Tem','Ağu','Eyl','Eki','Kas','Ara'];
const fmt=n=>Number(n||0).toLocaleString('tr-TR');
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const kClass=q=>q<=0?0:q<=200?1:q<=500?2:q<=1000?3:4;
const partLabel={1:'1 parti',2:'2 parti',3:'3 parti',4:'4 parti'};
const list=document.getElementById('selection'), grid=document.getElementById('calendar');
const state={products:[],scenario:'balanced',oneMonth:5,twoMonth:2,group:1,month:5,product:null,query:'',groupFilter:'all',columnFilter:'all',assignments:[],months:Array.from({length:12},()=>[])};
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
 grid.querySelectorAll('button[data-g]').forEach(b=>b.addEventListener('click',()=>{state.group=+b.dataset.g;state.month=+b.dataset.m;state.product=null;state.query='';state.groupFilter='all';state.columnFilter='all';renderCalendar();renderSelection()}));
 const top=Math.max(...Array.from({length:12},(_,m)=>sumMonth(m)))||1;
 document.getElementById('monthly').innerHTML=SHORT.map((m,i)=>`<div class="m"><label>${m}</label><div class="barbox"><div class="bar" style="height:${Math.max(0,100*sumMonth(i)/top)}%"></div></div><div class="qty">${fmt(sumMonth(i))}</div></div>`).join('');
}
// Kaynak Excel'deki 19 şönt + 22 harmonik alanının tamamı korunur.
// Birbirinin eşdeğeri sütunlar birleştirilir, kaynakta olmayan bilgiler tahmin edilmez.
const raw=(p,name)=>p.tamKayit&&Object.prototype.hasOwnProperty.call(p.tamKayit,name)?p.tamKayit[name]:null;
const groupRaw=(p,s,h)=>p.grup==='Şönt'?raw(p,s):raw(p,h);
const pWeight=p=>typeof p.kg==='number'&&p.kg>0?p.kg:null;
const COLS=[
 {name:'Stok kodu',kind:'main',get:p=>p.kod},
 {name:'Ürün modeli / açıklama',kind:'main',get:p=>p.model},
 {name:'Grup',kind:'plan',get:p=>p.grup},
 {name:'Yıllık miktar (adet)',kind:'plan',get:p=>p.adet},
 {name:'Parti sayısı',kind:'plan',get:p=>p.parti},
 {name:'Bu ay üretim (adet)',kind:'plan',get:p=>p.partiAdedi},
 {name:'Miktar payı / toplam pay',kind:'plan',get:p=>groupRaw(p,'Miktar payı','Toplam pay'),fraction:true},
 {name:'Birim ağırlık (kg)',kind:'plan',get:p=>pWeight(p)},
 {name:'Parti ağırlığı (kg)',kind:'plan',get:p=>pWeight(p)==null?null:Math.round(pWeight(p)*p.partiAdedi*100)/100},
 {name:'Ön inceleme grubu (geçici)',kind:'identity',get:p=>raw(p,'Ön inceleme grubu (geçici)'),long:true},
 {name:'Ürün ailesi',kind:'identity',get:p=>raw(p,'Ürün ailesi')},
 {name:'Teknik inceleme grubu',kind:'identity',get:p=>raw(p,'Teknik inceleme grubu'),long:true},
 {name:'Standart / varyant',kind:'identity',get:p=>raw(p,'Standart / varyant')},
 {name:'Faz',kind:'technical',get:p=>raw(p,'Faz')},
 {name:'Güç (kVAr)',kind:'technical',get:p=>raw(p,'Güç (kVAr)')},
 {name:'Akım (A / Irms)',kind:'technical',get:p=>groupRaw(p,'Akım (A)','Akım (Irms, A)')},
 {name:'Endüktans L (mH)',kind:'technical',get:p=>raw(p,'L (mH)')},
 {name:'p (%)',kind:'technical',get:p=>raw(p,'p (%)')},
 {name:'THDv tasarım sınıfı',kind:'technical',get:p=>raw(p,'THDv tasarım sınıfı'),long:true},
 {name:'Ölçüler (mm)',kind:'technical',get:p=>groupRaw(p,'Ölçü G×Y×D (mm)','Dış ölçüler (mm)')},
 {name:'Bağlantı',kind:'technical',get:p=>groupRaw(p,'Bağlantı tipi','Bağlantı')},
 {name:'Sarım tipi / iletken biçimi',kind:'technical',get:p=>groupRaw(p,'Sarım tipi (tel/folyo)','Sarım iletken biçimi'),long:true},
 {name:'Yapı referansı (2025 çizimi)',kind:'technical',get:p=>raw(p,'Yapı referansı (2025 çizimi)'),long:true},
 {name:'Kıyas kodu / önerisi',kind:'review',get:p=>groupRaw(p,'Kıyas kodu','Kıyas önerisi')},
 {name:'Numune / kontrol',kind:'review',get:p=>raw(p,'Numune / kontrol'),long:true},
 {name:'Seçilme veya kıyas nedeni',kind:'review',get:p=>raw(p,'Seçilme veya kıyas nedeni'),long:true},
 {name:'Katalog / teknik veri durumu',kind:'review',get:p=>groupRaw(p,'2026/12 katalog durumu','Teknik veri durumu'),long:true},
 {name:'İnceleme / eksik bilgi',kind:'review',get:p=>raw(p,'İnceleme / eksik bilgi'),long:true},
 {name:'Kaynak URL / bağlantısı',kind:'review',get:p=>groupRaw(p,'Kaynak URL','Kaynak bağlantısı'),long:true,link:true},
 {name:'Kaynak kayıt',kind:'review',get:p=>raw(p,'Kaynak kayıt'),long:true},
 {name:'Kaynak dosya',kind:'review',get:p=>p.kaynakDosya},
 {name:'Kaynak Excel satırı',kind:'review',get:p=>p.kaynakSatir}
];
function presentValue(value,col){
 if(value===null||value===undefined||value==='')return '<span class="missing">—</span>';
 if(col.link&&typeof value==='string'&&/^https:\/\//i.test(value))return `<a href="${esc(value)}" target="_blank" rel="noopener noreferrer">${esc(value)}</a>`;
 const v=col.fraction&&typeof value==='number'?(value*100).toLocaleString('tr-TR',{maximumFractionDigits:4})+' %':typeof value==='number'?value.toLocaleString('tr-TR',{maximumFractionDigits:8}):String(value);
 return esc(v);
}
function renderSelection(){
 const rows=monthlyOf(state.group,state.month).sort((a,b)=>b.partiAdedi-a.partiAdedi),total=rows.reduce((x,p)=>x+p.partiAdedi,0);
 if(!total){list.innerHTML='<div class="empty-state">Bu sınıfta seçilen ay için üretim yok.</div>';return}
 list.innerHTML=`<div class="selected-head"><div><h2>${MONTHS[state.month]} · ${partLabel[state.group]}</h2><p>${rows.length} ürün satırı · Ürün matrislerinin bütün mevcut alanları aynı tabloda</p></div><div class="quantity">${fmt(total)}<small>adet üretim</small></div></div>
 <div class="detail-table-toolbar"><label class="table-search">Ürün ara<input id="searchProduct" placeholder="Stok kodu, model veya teknik özellik ara…" aria-label="Ürün ara" value="${esc(state.query)}"></label><label class="table-filter">Ürün grubu<select id="groupFilter" aria-label="Ürün grubu"><option value="all">Tüm ürünler</option><option value="Şönt">Şönt</option><option value="Harmonik">Harmonik</option></select></label><label class="table-filter">Sütun grubu<select id="columnFilter" aria-label="Sütun grubu"><option value="all">Tüm özellikler</option><option value="plan">Üretim ve miktar</option><option value="technical">Teknik özellikler</option><option value="review">Kıyas, numune ve kaynaklar</option></select></label><span class="table-hint">Sağa kaydırarak bütün sütunları inceleyin →</span></div>
 <div class="product-table-wrap" role="region" aria-label="Üretim ürünleri ve tüm teknik özellikleri" tabindex="0"><table class="product-table"><thead id="productTableHead"></thead><tbody id="productTableBody"></tbody><tfoot id="productTableFoot"></tfoot></table></div>
 <div class="stack-note"><span id="shownCount"></span> · 32 sütunda üretim, teknik, kıyas, numune ve kaynak bilgileri. <b>—</b> kaynak matriste değerin olmadığı anlamına gelir; doğrulanmamış alanlar kaynakta yazdığı gibi korunur. Aynı stok kodunun farklı açıklamalı kayıtları ayrı satırlardadır.</div>`;
 document.getElementById('searchProduct').addEventListener('input',e=>{state.query=e.target.value;renderProductTable(rows)});
 const filter=document.getElementById('groupFilter');filter.value=state.groupFilter;filter.addEventListener('change',e=>{state.groupFilter=e.target.value;renderProductTable(rows)});
 const columns=document.getElementById('columnFilter');columns.value=state.columnFilter;columns.addEventListener('change',e=>{state.columnFilter=e.target.value;renderProductTable(rows)});
 renderProductTable(rows);
}
function activeColumns(){return COLS.filter((c,i)=>i<2||state.columnFilter==='all'||c.kind===state.columnFilter||(state.columnFilter==='technical'&&c.kind==='identity'))}
function renderProductTable(rows){
 const term=state.query.toLocaleLowerCase('tr-TR').trim();
 const shown=rows.filter(p=>{
  if(state.groupFilter!=='all'&&p.grup!==state.groupFilter)return false;
  return COLS.some(c=>String(c.get(p)??'').toLocaleLowerCase('tr-TR').includes(term));
 });
 const cols=activeColumns();
 document.getElementById('productTableHead').innerHTML='<tr>'+cols.map(c=>`<th scope="col">${esc(c.name)}</th>`).join('')+'</tr>';
 const body=document.getElementById('productTableBody');
 body.innerHTML=shown.length?shown.map(p=>'<tr>'+cols.map((c,i)=>{
   const value=c.get(p);
   const attr=c.long?' class="long-text"':(typeof value==='number'?' class="numeric"':'');
   return `<td${attr}>${i===0?`<strong>${presentValue(value,c)}</strong>`:presentValue(value,c)}</td>`;
 }).join('')+'</tr>').join(''):`<tr><td colspan="${cols.length}" class="table-no-result">Aramaya uygun ürün yok.</td></tr>`;
 const sumQty=shown.reduce((n,p)=>n+p.partiAdedi,0),unknownKg=shown.filter(p=>pWeight(p)===null).length;
 const sumKg=Math.round(shown.reduce((n,p)=>n+(pWeight(p)===null?0:pWeight(p)*p.partiAdedi),0)*100)/100;
 const totalByName={'Stok kodu':'TOPLAM','Ürün modeli / açıklama':`${shown.length} ürün satırı`,'Bu ay üretim (adet)':fmt(sumQty),'Parti ağırlığı (kg)':unknownKg?fmt(sumKg)+' *':fmt(sumKg)};
 document.getElementById('productTableFoot').innerHTML='<tr>'+cols.map(c=>`<td>${totalByName[c.name]||''}</td>`).join('')+'</tr>';
 document.getElementById('shownCount').textContent=`${shown.length} / ${rows.length} ürün gösteriliyor · ${cols.length} sütun${unknownKg?` · ${unknownKg} üründe ağırlık eksik, toplam kg eksik olabilir`:''}`;
}
function downloadCSV(){
 const header=['Ürün ID','Ay',...COLS.map(c=>c.name)];
 const lines=[header,...state.assignments.map(p=>[p.id,MONTHS[p.month],...COLS.map(c=>c.get(p))])];
 const csv='\ufeff'+lines.map(row=>row.map(x=>'"'+String(x==null?'':x).replace(/"/g,'""')+'"').join(';')).join('\r\n');
 const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));a.download='sont_harmonik_tum_ozellikler_uretim_plani.csv';a.click();URL.revokeObjectURL(a.href);
}
function setup(){for(const id of ['oneMonth','twoMonth']){const select=document.getElementById(id);const candidates=id==='twoMonth'?MONTHS.slice(0,6):MONTHS;select.innerHTML=candidates.map((m,i)=>`<option value="${i}">${m}</option>`).join('');select.value=state[id];select.addEventListener('change',e=>{state[id]=+e.target.value;rerender()})}
 document.getElementById('scenario').addEventListener('change',e=>{state.scenario=e.target.value;rerender()});document.getElementById('downloadBtn').addEventListener('click',downloadCSV)}
function rerender(){buildPlan();renderStats();renderCalendar();renderSelection()}
async function load(){try{const b64=window.PRODUCTS_GZIP_B64;if(!b64)throw Error('Ürün verisi bulunamadı');const raw=Uint8Array.from(atob(b64),c=>c.charCodeAt(0));const ds=new DecompressionStream('gzip');const decompressed=await new Response(new Blob([raw]).stream().pipeThrough(ds)).text();state.products=JSON.parse(decompressed);if(state.products.length!==135||state.products.reduce((s,p)=>s+p.adet,0)!==45088)throw Error('Veri toplamı beklenenden farklı');setup();rerender();document.getElementById('sourceBadge').textContent=`${state.products.length} ürün · Veri doğrulandı`;}catch(e){document.getElementById('sourceBadge').textContent='Veri hatası';list.innerHTML=`<div class="empty-state"><strong>Veri yüklenemedi</strong><p>${esc(e.message)}</p></div>`;console.error(e)}}
load();
})();
