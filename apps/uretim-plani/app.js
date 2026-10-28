(()=>{'use strict';
const MONTHS=['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık'];
const SHORT=['Oca','Şub','Mar','Nis','May','Haz','Tem','Ağu','Eyl','Eki','Kas','Ara'];
const fmt=n=>Number(n||0).toLocaleString('tr-TR');
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const kClass=q=>q<=0?0:q<=200?1:q<=500?2:q<=1000?3:4;
const partLabel={1:'1 parti',2:'2 parti',3:'3 parti',4:'4 parti'};
const list=document.getElementById('selection'), grid=document.getElementById('calendar');
const state={products:[],scenario:'balanced',oneMonth:5,twoMonth:2,group:1,month:5,product:null,query:'',groupFilter:'all',columnFilter:'all',customColumns:null,grouping:'type',sortBy:'batch',sortDirection:'desc',sortedColumn:'Bu ay üretim (adet)',filters:[],filterLogic:'and',filterId:0,assignments:[],months:Array.from({length:12},()=>[])};
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
 grid.querySelectorAll('button[data-g]').forEach(b=>b.addEventListener('click',()=>{state.group=+b.dataset.g;state.month=+b.dataset.m;state.product=null;state.query='';state.groupFilter='all';renderCalendar();renderSelection()}));
 const top=Math.max(...Array.from({length:12},(_,m)=>sumMonth(m)))||1;
 document.getElementById('monthly').innerHTML=SHORT.map((m,i)=>`<div class="m"><label>${m}</label><div class="barbox"><div class="bar" style="height:${Math.max(0,100*sumMonth(i)/top)}%"></div></div><div class="qty">${fmt(sumMonth(i))}</div></div>`).join('');
}
// Kaynak Excel'deki 19 şönt + 22 harmonik alanının tamamı korunur.
// Birbirinin eşdeğeri sütunlar birleştirilir, kaynakta olmayan bilgiler tahmin edilmez.
const raw=(p,name)=>p.tamKayit&&Object.prototype.hasOwnProperty.call(p.tamKayit,name)?p.tamKayit[name]:null;
const groupRaw=(p,s,h)=>p.grup==='Şönt'?raw(p,s):raw(p,h);
const pWeight=p=>typeof p.kg==='number'&&p.kg>0?p.kg:null;
// Üreticinin resmî aile datasheetleri: stok kodu başına özel PDF olduğu iddia edilmez.

/* 28.10.2026 tarihinde üreticinin 2026/12 resmî teknik fiyat listesi (https://www.gruparge.com/fl/tr)
   PDF'nin 17, 30, 31 ve 32. sayfalarındaki 112 farklı stok kodu esas alınmıştır.
   Kullanıcı matrisindeki 135 satırın 92'si bu listede bulunmuş ve akım, L, ölçü,
   ağırlık, bağlantı alanları 5/5 eşleşmiştir. Diğer 43 satır (29 G/GG,
   12 özel üretim, 2 SVC) katalog dışıdır. Resmî listede olmamak ürün yokluğu değildir.
   Bu eşleşmelerin satır bazında CSV raporu ayrıca hazırlanmıştır.
*/
const OFFICIAL_2026_LIST='https://www.gruparge.com/fl/tr';
const OFFICIAL_2026_RANGES=[
 [5001,5003,17],[5101,5108,17],[5201,5212,17],
 [5311,5317,30],[5411,5417,30],[5511,5517,30],
 [5321,5339,31],[5629,5639,31],
 [5521,5539,32],[5421,5439,32]
];
const official2026Page=code=>{
 if(typeof code!=='string'||!/^GA\d{4}$/.test(code))return null;
 const value=Number(code.slice(2));
 const range=OFFICIAL_2026_RANGES.find(([a,b])=>value>=a&&value<=b);
 return range?range[2]:null;
};
// G/GG kodu için yalnızca standart baz kodu gösterilir; varyantın teknik verisi türetilmez.
const official2026BaseCode=code=>{
 const m=typeof code==='string'?code.match(/^GAGG?(\d{4})$/):null;
 const base=m?'GA'+m[1]:null;
 return base&&official2026Page(base)!==null?base:null;
};
const official2026Status=p=>
 official2026Page(p.kod)!==null?'5/5 teknik alan uyumlu':
 official2026BaseCode(p.kod)!==null?'Standart baz model var; varyant doğrulanmadı':'Ürün kodu resmî tabloda yok';
const official2026Note=p=>
 official2026Page(p.kod)!==null?'2026/12 resmî tablo: akım, L, ölçü, kg ve bağlantı değerleri eşleşti.':
 official2026BaseCode(p.kod)!==null?'Standart '+official2026BaseCode(p.kod)+' üreticinin listesinde. G/GG varyantının akım, endüktans, ölçü, ağırlık ve bağlantısı ayrıca yayımlanmamış; baz ürün değerleri kopyalanmamalı.':
 p.kod==='GA5ÖZELHARM'?'Siparişe özel ürün; 2026 listesinde aynı kodla teknik tablo yok. Üretici teknik föyü gerekli.':
 '2026 listesinde aynı stok koduyla karşılık bulunamadı; üretici teknik föyü gerekli.';

const OFFICIAL_DATASHEETS={Şönt:'https://www.gruparge.com/wp-content/uploads/2025/05/SONT-REAKTORU-DATASHEET.pdf',Harmonik:'https://www.gruparge.com/wp-content/uploads/2025/05/HARMONIK-FILTRE-DATASHEET.pdf'};

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
 {name:'2026/12 teknik doğrulama',kind:'review',get:official2026Status},
 {name:'2026/12 kontrol notu',kind:'review',get:official2026Note,long:true},
 {name:'Standart baz ürün kodu (referans)',kind:'review',get:p=>official2026BaseCode(p.kod)},
 {name:'Baz ürün teknik liste bağlantısı',kind:'review',get:p=>official2026BaseCode(p.kod)?OFFICIAL_2026_LIST+'#page='+official2026Page(official2026BaseCode(p.kod)):null,link:true,baseReference:true},
 {name:'2026/12 kaynak PDF sayfası',kind:'review',get:p=>official2026Page(p.kod)},
 {name:'Resmî 2026/12 teknik liste',kind:'review',get:p=>official2026Page(p.kod)?OFFICIAL_2026_LIST+'#page='+official2026Page(p.kod):null,link:true,pdfList:true},
 {name:'Resmî datasheet (grup PDF)',kind:'review',get:p=>OFFICIAL_DATASHEETS[p.grup]||null,link:true,pdf:true},
 {name:'Kaynak kayıt',kind:'review',get:p=>raw(p,'Kaynak kayıt'),long:true},
 {name:'Kaynak dosya',kind:'review',get:p=>p.kaynakDosya},
 {name:'Kaynak Excel satırı',kind:'review',get:p=>p.kaynakSatir}
];
function presentValue(value,col){
 if(value===null||value===undefined||value==='')return '<span class="missing">—</span>';
 if(col.link&&typeof value==='string'&&/^https:\/\//i.test(value))return `<a href="${esc(value)}" target="_blank" rel="noopener noreferrer" title="${col.pdf?'Ürün grubunun resmî teknik PDF dosyası; her model için özel PDF değildir':col.baseReference?'Standart baz modelin verileri; G/GG varyantı doğrulanmış değildir':col.pdfList?'Üreticinin resmî 2026/12 teknik listesi; ilgili sayfaya git':esc(value)}">${col.pdf?'2025 grup datasheet PDF ↗':col.baseReference?'Baz model PDF ↗':col.pdfList?'2026/12 resmî liste ↗':esc(value)}</a>`;
 const v=col.fraction&&typeof value==='number'?(value*100).toLocaleString('tr-TR',{maximumFractionDigits:4})+' %':typeof value==='number'?value.toLocaleString('tr-TR',{maximumFractionDigits:8}):String(value);
 return esc(v);
}
function renderSelection(){
 const rows=monthlyOf(state.group,state.month).sort((a,b)=>b.partiAdedi-a.partiAdedi),total=rows.reduce((x,p)=>x+p.partiAdedi,0);
 if(!total){list.innerHTML='<div class="empty-state">Bu sınıfta seçilen ay için üretim yok.</div>';return}
 list.innerHTML=`<div class="selected-head"><div><h2>${MONTHS[state.month]} · ${partLabel[state.group]}</h2><p>${rows.length} ürün satırı · Ürün matrislerinin bütün mevcut alanları aynı tabloda</p></div><div class="quantity">${fmt(total)}<small>adet üretim</small></div></div>
 <div class="detail-table-toolbar"><label class="table-search">Ürün ara<input id="searchProduct" placeholder="Stok kodu, model veya teknik özellik ara…" aria-label="Ürün ara" value="${esc(state.query)}"></label><label class="table-filter">Ürün grubu<select id="groupFilter" aria-label="Ürün grubu"><option value="all">Tüm ürünler</option><option value="Şönt">Şönt</option><option value="Harmonik">Harmonik</option></select></label><label class="table-filter">Sütun grubu<select id="columnFilter" aria-label="Sütun grubu"><option value="all">Tüm özellikler</option><option value="plan">Üretim ve miktar</option><option value="technical">Teknik özellikler</option><option value="review">Kıyas, numune ve kaynaklar</option><option value="custom">Özel sütun seçimi</option></select></label><details class="column-picker" id="columnPicker"><summary id="columnPickerSummary">Sütun ekle / çıkar</summary><div class="column-picker-panel" id="columnPickerPanel"></div></details><label class="table-filter">Grupla<select id="groupBy" aria-label="Gruplama"><option value="type">Şönt / Harmonik</option><option value="family">Ürün ailesi</option><option value="quantity">Üretim adedi aralığı</option><option value="weight">Birim ağırlık aralığı</option><option value="dimensions">Dış ölçü aralığı</option><option value="none">Gruplama yok</option></select></label><label class="table-filter">Sırala<select id="sortBy" aria-label="Sıralama ölçütü"><option value="batch">Bu ay üretim adedi</option><option value="annual">Yıllık adet</option><option value="unitWeight">Birim ağırlık</option><option value="batchWeight">Parti ağırlığı</option><option value="largestEdge">En büyük dış ölçü</option><option value="outerVolume">Yaklaşık dış hacim</option><option value="power">Güç (kVAr)</option><option value="code">Stok kodu</option><option value="column" id="columnSortLabel">Sütun başlığına göre</option></select></label><label class="table-filter narrow-filter">Sıralama yönü<select id="sortDirection" aria-label="Sıralama yönü"><option value="desc">Büyükten küçüğe</option><option value="asc">Küçükten büyüğe</option></select></label><details class="multi-filter" id="multiFilter"><summary id="multiFilterSummary">Ek filtreler (0)</summary><div class="multi-filter-panel"><div class="filter-actions"><b>Birden fazla koşul ekleyin</b><button type="button" id="addFilter">+ Filtre ekle</button><button type="button" id="clearFilters">Temizle</button></div><label class="filter-logic">Koşulları birleştir<select id="filterLogic"><option value="and">Hepsi sağlansın (VE)</option><option value="or">Herhangi biri sağlansın (VEYA)</option></select></label><div id="filterRows"></div><small>Ürün grubu ve arama filtreleriyle birlikte uygulanır. Eksik değerler ayrı filtrelenebilir.</small></div></details><span class="table-hint">Sütun başlığına basarak sıralayın (▲ / ▼). Birden çok filtreyi birlikte kullanabilirsiniz. Grupların içindeki ürünler sıralanır.</span></div>
 <div class="product-table-wrap" role="region" aria-label="Üretim ürünleri ve tüm teknik özellikleri" tabindex="0"><table class="product-table"><thead id="productTableHead"></thead><tbody id="productTableBody"></tbody><tfoot id="productTableFoot"></tfoot></table></div>
 <div class="audit-banner"><strong>2026/12 resmî katalog denetimi:</strong> 135 satır: 92 ürün (5 teknik alan uyumlu), 29 G/GG varyantında standart baz model referansı var fakat varyant doğrulanmadı, 14 ürün kodu listede yok. <a href="https://www.gruparge.com/fl/tr" target="_blank" rel="noopener noreferrer">Resmî listeyi aç ↗</a> · <span id="auditCurrentSelection"></span></div><div class="stack-note"><span id="shownCount"></span> · ${COLS.length} sütunda üretim, teknik, kıyas, numune ve kaynak bilgileri. Resmî datasheet bağlantısı ürün grubuna aittir, tekil ürün datasheeti değildir. <b>—</b> kaynak matriste değerin olmadığı anlamına gelir; doğrulanmamış alanlar kaynakta yazdığı gibi korunur. Aynı stok kodunun farklı açıklamalı kayıtları ayrı satırlardadır.</div>`;
 document.getElementById('searchProduct').addEventListener('input',e=>{state.query=e.target.value;renderProductTable(rows)});
 const filter=document.getElementById('groupFilter');filter.value=state.groupFilter;filter.addEventListener('change',e=>{state.groupFilter=e.target.value;renderProductTable(rows)});
 const columns=document.getElementById('columnFilter');columns.value=state.columnFilter;columns.addEventListener('change',e=>{if(e.target.value==='custom'&&state.customColumns===null)state.customColumns=activeColumns().map(c=>c.name);else if(e.target.value!=='custom')state.customColumns=null;state.columnFilter=e.target.value;renderProductTable(rows);renderColumnPicker(rows)});
 for(const [id,key] of [['groupBy','grouping'],['sortBy','sortBy'],['sortDirection','sortDirection']]){
  const control=document.getElementById(id);control.value=state[key];control.addEventListener('change',e=>{state[key]=e.target.value;renderProductTable(rows)});
 }
 document.getElementById('addFilter').addEventListener('click',()=>{state.filters.push({id:++state.filterId,field:'Bu ay üretim (adet)',op:'gte',value:''});renderFilterPanel(rows)});
 document.getElementById('clearFilters').addEventListener('click',()=>{state.filters=[];renderFilterPanel(rows);renderProductTable(rows)});
 const filterLogic=document.getElementById('filterLogic');filterLogic.value=state.filterLogic;filterLogic.addEventListener('change',e=>{state.filterLogic=e.target.value;renderProductTable(rows)});
 renderProductTable(rows);renderColumnPicker(rows);renderFilterPanel(rows);
}
function activeColumns(){return COLS.filter((c,i)=>i<2||(state.customColumns!==null?state.customColumns.includes(c.name):state.columnFilter==='all'||c.kind===state.columnFilter||(state.columnFilter==='technical'&&c.kind==='identity')))}

// Ürün özelliklerinden hesaplanan aralıklar yalnızca sıralama içindir; makine yük kapasitesi değildir.

function renderColumnPicker(rows){
 const panel=document.getElementById('columnPickerPanel'), summary=document.getElementById('columnPickerSummary');
 if(!panel||!summary)return;
 const selected=new Set(activeColumns().map(c=>c.name));
 summary.textContent='Sütun ekle / çıkar ('+selected.size+'/'+COLS.length+')';
 const groups=[['main','Kimlik (sabit)'],['plan','Üretim ve miktar'],['identity','Ürün sınıflandırması'],['technical','Teknik özellikler'],['review','Kıyas, numune ve kaynaklar']];
 panel.innerHTML='<div class="picker-title">Gösterilecek sütunları işaretleyin</div>'+
 '<div class="picker-actions"><button type="button" data-picker-action="all">'+COLS.length+' sütunun tamamı</button><button type="button" data-picker-action="minimal">Yalnızca kod ve model</button></div>'+
 '<input type="search" id="columnPickerSearch" placeholder="Sütun adı ara..." aria-label="Sütun adı ara">'+
 '<div class="picker-options">'+groups.map(([kind,title])=>'<fieldset class="picker-fieldset"><legend>'+title+'</legend>'+
 COLS.map((c,i)=>({c,i})).filter(x=>x.c.kind===kind).map(({c,i})=>
 '<label class="column-option"><input type="checkbox" data-column-index="'+i+'" '+(selected.has(c.name)?'checked ':'')+(i<2?'disabled ':'')+'><span>'+esc(c.name)+'</span></label>'
 ).join('')+'</fieldset>').join('')+'</div>'+
 '<div class="picker-foot">Stok kodu ve model sütunları sabit kalır. Diğer '+(COLS.length-2)+' sütunu isteğe göre açıp kapatabilirsiniz.</div>';
 function applySelection(names){
  state.customColumns=COLS.filter((c,i)=>i<2||names.includes(c.name)).map(c=>c.name);
  state.columnFilter='custom';
  document.getElementById('columnFilter').value='custom';
  renderProductTable(rows);
  renderColumnPicker(rows);
 }
 panel.querySelectorAll('input[data-column-index]').forEach(input=>input.addEventListener('change',()=>{
  const selectedNow=new Set(activeColumns().map(c=>c.name));
  const name=COLS[Number(input.dataset.columnIndex)].name;
  if(input.checked)selectedNow.add(name);else selectedNow.delete(name);
  applySelection([...selectedNow]);
 }));
 panel.querySelectorAll('[data-picker-action]').forEach(button=>button.addEventListener('click',()=>{
  if(button.dataset.pickerAction==='all'){
   state.customColumns=null;state.columnFilter='all';
   document.getElementById('columnFilter').value='all';
   renderProductTable(rows);renderColumnPicker(rows);
  }else applySelection(COLS.slice(0,2).map(c=>c.name));
 }));
 panel.querySelector('#columnPickerSearch').addEventListener('input',e=>{
  const q=e.target.value.toLocaleLowerCase('tr-TR');
  panel.querySelectorAll('.column-option').forEach(label=>{label.hidden=!label.textContent.toLocaleLowerCase('tr-TR').includes(q)});
  panel.querySelectorAll('.picker-fieldset').forEach(field=>{field.hidden=!Array.from(field.querySelectorAll('.column-option')).some(label=>!label.hidden)});
 });
}

function dimensionsOf(p){
 const value=groupRaw(p,'Ölçü G×Y×D (mm)','Dış ölçüler (mm)');
 if(value===null||value===undefined)return null;
 const parts=String(value).replace(/mm/gi,'').replace(/,/g,'.').split(/[×xX*]/).map(x=>Number(x.trim()));
 return parts.length===3 && parts.every(x=>Number.isFinite(x)&&x>0)?parts:null;
}
function bucket(value, edges, labels){
 if(value===null||value===undefined||!Number.isFinite(value))return {key:'unknown',title:'Bilgisi olmayanlar',order:edges.length+1};
 for(let i=0;i<edges.length;i++)if(value<=edges[i])return {key:String(i),title:labels[i],order:i};
 return {key:String(edges.length),title:labels[edges.length],order:edges.length};
}
function productionGroup(p){
 const kg=pWeight(p),dims=dimensionsOf(p),maxEdge=dims?Math.max(...dims):null;
 if(state.grouping==='type')return {key:p.grup,title:p.grup,order:p.grup==='Şönt'?0:1};
 if(state.grouping==='family'){
  const family=raw(p,'Ürün ailesi')||p.aile||'Aile bilgisi yok';
  const title=p.grup+' · '+String(family);
  return {key:title,title,order:p.grup==='Şönt'?0:1};
 }
 if(state.grouping==='quantity')return bucket(p.partiAdedi,[50,200,500],['1–50 adet','51–200 adet','201–500 adet','501+ adet']);
 if(state.grouping==='weight')return bucket(kg,[5,15,35,75],['0–5 kg','5–15 kg','15–35 kg','35–75 kg','75 kg üzeri']);
 if(state.grouping==='dimensions')return bucket(maxEdge,[150,250,400],['En büyük kenar ≤150 mm','151–250 mm','251–400 mm','400 mm üzeri']);
 return {key:'all',title:'Tüm ürünler',order:0};
}
function sortMetric(p){
 const dims=dimensionsOf(p);
 switch(state.sortBy){
  case 'column':return normalizeColumnSortValue(COLS.find(c=>c.name===state.sortedColumn),p);
  case 'annual':return p.adet;
  case 'unitWeight':return pWeight(p);
  case 'batchWeight':return pWeight(p)===null?null:pWeight(p)*p.partiAdedi;
  case 'largestEdge':return dims?Math.max(...dims):null;
  case 'outerVolume':return dims?dims.reduce((a,b)=>a*b,1)/1000000:null; // dış kutu geometrisi, litre
  case 'power':{const value=raw(p,'Güç (kVAr)');const n=typeof value==='number'?value:Number(String(value).replace(',','.'));return value!==null&&value!==undefined&&value!==''&&Number.isFinite(n)?n:null;}
  case 'code':return p.kod;
  default:return p.partiAdedi;
 }
}
function productComparator(a,b){
 const av=sortMetric(a),bv=sortMetric(b);
 const aMissing=av===null||av===undefined||av==='',bMissing=bv===null||bv===undefined||bv==='';
 if(aMissing!==bMissing)return aMissing?1:-1; // bilinmeyenler iki yönde de son sırada
 const direction=state.sortDirection==='asc'?1:-1;
 let cmp=0;
 if(!aMissing)cmp=typeof av==='number'&&typeof bv==='number'?av-bv:String(av).localeCompare(String(bv),'tr');
 if(cmp)return cmp*direction;
 return String(a.kod).localeCompare(String(b.kod),'tr')||String(a.id).localeCompare(String(b.id),'tr');
}
function displayGroupedRows(rows,cols){
 const groups=new Map();
 for(const p of rows){
  const category=productionGroup(p);
  if(!groups.has(category.key))groups.set(category.key,{...category,items:[]});
  groups.get(category.key).items.push(p);
 }
 const allGroups=[...groups.values()].sort((a,b)=>a.order-b.order||a.title.localeCompare(b.title,'tr'));
 let html='';
 for(const group of allGroups){
  const items=group.items.sort(productComparator);
  if(state.grouping!=='none'){
   const qty=items.reduce((sum,p)=>sum+p.partiAdedi,0);
   const unknown=items.filter(p=>pWeight(p)===null).length;
   const knownKg=items.reduce((sum,p)=>sum+(pWeight(p)===null?0:pWeight(p)*p.partiAdedi),0);
   const weightLabel=(unknown===items.length?'Ağırlık verisi yok':fmt(Math.round(knownKg*100)/100)+' kg (bilinen)')+(unknown?' · '+unknown+' üründe kg eksik':'');
   html+='<tr class="product-group-row"><th scope="rowgroup" colspan="'+cols.length+'"><span class="group-label">'+esc(group.title)+'</span><span class="group-aggregate">'+items.length+' ürün · '+fmt(qty)+' adet · '+esc(weightLabel)+'</span></th></tr>';
  }
  for(const p of items){
   html+='<tr>'+cols.map((c,i)=>{
    const value=c.get(p),attr=c.long?' class="long-text"':typeof value==='number'?' class="numeric"':'';
    return '<td'+attr+'>'+(i===0?'<strong>'+presentValue(value,c)+'</strong>':presentValue(value,c))+'</td>';
   }).join('')+'</tr>';
  }
 }
 return {html,groupCount:allGroups.length};
}


// 32 gerçek sütunun tamamı filtrelenebilir; boyut verileri ek bir sayısal arama alanına da dönüşebilir.
const NUMERIC_FIELDS=new Set(['Yıllık miktar (adet)','Parti sayısı','Bu ay üretim (adet)',
 'Miktar payı / toplam pay','Birim ağırlık (kg)','Parti ağırlığı (kg)',
 'Faz','Güç (kVAr)','Akım (A / Irms)','Endüktans L (mH)','p (%)','Kaynak Excel satırı',
 'En büyük dış ölçü (mm)','Yaklaşık dış hacim (L)']);
const FILTER_FIELDS=[...COLS.map(c=>({name:c.name,get:c.get,numeric:NUMERIC_FIELDS.has(c.name)})),
 {name:'En büyük dış ölçü (mm)',numeric:true,get:p=>{const dims=dimensionsOf(p);return dims?Math.max(...dims):null}},
 {name:'Yaklaşık dış hacim (L)',numeric:true,get:p=>{const dims=dimensionsOf(p);return dims?dims.reduce((a,b)=>a*b,1)/1000000:null}}];
function filterNumber(value){
 if(typeof value==='number')return Number.isFinite(value)?value:null;
 if(value===null||value===undefined)return null;
 let rawValue=String(value).trim().replace(/\s/g,'').replace(/%$/,'');
 if(!rawValue)return null;
 if(rawValue.includes(',')&&rawValue.includes('.'))rawValue=rawValue.replace(/\./g,'').replace(',','.');
 else rawValue=rawValue.replace(',','.');
 return /^[-+]?\d+(?:\.\d+)?$/.test(rawValue)?Number(rawValue):null;
}
function normalizeColumnSortValue(c,p){
 if(!c)return null;
 const value=c.get(p);
 if(value===null||value===undefined||value==='')return null;
 if(c.name==='Ölçüler (mm)'){const dims=dimensionsOf(p);return dims?Math.max(...dims):null}
 if(NUMERIC_FIELDS.has(c.name))return filterNumber(value);
 return value;
}
function matchFilter(p,rule){
 const field=FILTER_FIELDS.find(x=>x.name===rule.field);
 if(!field)return true;
 const value=field.get(p),missing=value===null||value===undefined||value==='';
 if(rule.op==='empty')return missing;
 if(rule.op==='notEmpty')return !missing;
 if(missing)return false;
 if(field.numeric){
  const v=filterNumber(value),target=filterNumber(rule.value);
  if(v===null||target===null)return false;
  switch(rule.op){
   case 'eq':return v===target;case 'neq':return v!==target;
   case 'gt':return v>target;case 'gte':return v>=target;
   case 'lt':return v<target;case 'lte':return v<=target;
   default:return false;
  }
 }
 const v=String(value).toLocaleLowerCase('tr-TR'),target=String(rule.value).toLocaleLowerCase('tr-TR').trim();
 switch(rule.op){
  case 'contains':return v.includes(target);case 'notContains':return !v.includes(target);
  case 'eq':return v===target;case 'neq':return v!==target;
  case 'starts':return v.startsWith(target);
  default:return false;
 }
}
function filterOperators(field){
 const numeric=field?.numeric;
 return numeric?[['gte','Büyük veya eşit'],['gt','Büyük'],['lte','Küçük veya eşit'],['lt','Küçük'],['eq','Eşittir'],['neq','Eşit değil'],['empty','Boş'],['notEmpty','Dolu']]:
 [['contains','İçerir'],['notContains','İçermez'],['eq','Eşittir'],['neq','Eşit değil'],['starts','İle başlar'],['empty','Boş'],['notEmpty','Dolu']];
}
function renderFilterPanel(rows){
 const target=document.getElementById('filterRows'),summary=document.getElementById('multiFilterSummary');
 if(!target||!summary)return;
 const active=state.filters.filter(r=>r.op==='empty'||r.op==='notEmpty'||String(r.value).trim()!=='').length;
 summary.textContent='Ek filtreler ('+active+')';
 document.getElementById('filterLogic').value=state.filterLogic;
 target.innerHTML=state.filters.length?state.filters.map(rule=>{
  const field=FILTER_FIELDS.find(x=>x.name===rule.field)||FILTER_FIELDS[0];
  const options=filterOperators(field);
  const noValue=rule.op==='empty'||rule.op==='notEmpty';
  return '<div class="filter-rule" data-rule-id="'+rule.id+'">'+
   '<select class="rule-field" aria-label="Filtrelenecek sütun">'+FILTER_FIELDS.map(f=>'<option value="'+esc(f.name)+'"'+(f.name===rule.field?' selected':'')+'>'+esc(f.name)+'</option>').join('')+'</select>'+
   '<select class="rule-op" aria-label="Filtre koşulu">'+options.map(([v,label])=>'<option value="'+v+'"'+(v===rule.op?' selected':'')+'>'+label+'</option>').join('')+'</select>'+
   '<input class="rule-value" type="text" inputmode="'+(field.numeric?'decimal':'text')+'" placeholder="'+(field.numeric?'Örn. 15':'Aranacak değer')+'" value="'+esc(rule.value)+'" aria-label="Filtre değeri"'+(noValue?' disabled':'')+'>'+
   '<button class="rule-remove" type="button" aria-label="Filtreyi kaldır" title="Filtreyi kaldır">×</button></div>';
 }).join(''):'<p class="filters-empty">Ek koşul yok. “+ Filtre ekle” ile başlayabilirsiniz.</p>';
 target.querySelectorAll('.filter-rule').forEach(el=>{
  const id=Number(el.dataset.ruleId);
  function getRule(){return state.filters.find(r=>r.id===id)}
  const column=el.querySelector('.rule-field'),op=el.querySelector('.rule-op'),value=el.querySelector('.rule-value');
  column.addEventListener('change',e=>{
   const rule=getRule();if(!rule)return;
   rule.field=e.target.value;
   const field=FILTER_FIELDS.find(f=>f.name===rule.field);
   rule.op=field?.numeric?'gte':'contains';
   rule.value='';
   renderFilterPanel(rows);renderProductTable(rows);
  });
  op.addEventListener('change',e=>{
   const rule=getRule();if(!rule)return;
   rule.op=e.target.value;
   value.disabled=rule.op==='empty'||rule.op==='notEmpty';
   renderProductTable(rows);renderFilterPanel(rows);
  });
  value.addEventListener('input',e=>{
   const rule=getRule();if(!rule)return;
   rule.value=e.target.value;
   summary.textContent='Ek filtreler ('+state.filters.filter(r=>r.op==='empty'||r.op==='notEmpty'||String(r.value).trim()!=='').length+')';
   renderProductTable(rows);
  });
  el.querySelector('.rule-remove').addEventListener('click',()=>{
   state.filters=state.filters.filter(r=>r.id!==id);
   renderFilterPanel(rows);renderProductTable(rows);
  });
 });
}

function renderProductTable(rows){
 const term=state.query.toLocaleLowerCase('tr-TR').trim();
 const shown=rows.filter(p=>{
  if(state.groupFilter!=='all'&&p.grup!==state.groupFilter)return false;
  if(!COLS.some(c=>String(c.get(p)??'').toLocaleLowerCase('tr-TR').includes(term)))return false;
  const rules=state.filters.filter(r=>r.op==='empty'||r.op==='notEmpty'||String(r.value).trim()!=='');
  return rules.length===0||(state.filterLogic==='and'?rules.every(r=>matchFilter(p,r)):rules.some(r=>matchFilter(p,r)));
 });
 const officialMatched=shown.filter(p=>official2026Page(p.kod)!==null).length;
 const baseReferenced=shown.filter(p=>official2026BaseCode(p.kod)!==null).length;
 const unmatched=shown.length-officialMatched-baseReferenced;
 const auditStat=document.getElementById('auditCurrentSelection');
 if(auditStat)auditStat.textContent='Görünen listede '+officialMatched+' doğrulanan, '+baseReferenced+' baz referanslı (varyant teyitsiz), '+unmatched+' resmî kod eşleşmesi olmayan kayıt.';
 const cols=activeColumns();
 const colSort=state.sortBy==='column';
 document.getElementById('productTableHead').innerHTML='<tr>'+cols.map((c,i)=>{
  const active=colSort&&state.sortedColumn===c.name;
  const arrow=active?(state.sortDirection==='asc'?' ▲':' ▼'):' ↕';
  const ariaSort=active?(state.sortDirection==='asc'?'ascending':'descending'):'none';
  return `<th scope="col" aria-sort="${ariaSort}"><button type="button" class="head-sort ${active?'is-sorted':''}" data-sort-index="${i}" title="${esc(c.name)} sütununa göre sırala" aria-label="${esc(c.name)} sütununa göre sırala">${esc(c.name)}<span class="sort-arrow" aria-hidden="true">${arrow}</span></button></th>`;
 }).join('')+'</tr>';
 document.getElementById('productTableHead').querySelectorAll('button[data-sort-index]').forEach(button=>button.addEventListener('click',()=>{
  const col=cols[Number(button.dataset.sortIndex)],same=state.sortBy==='column'&&state.sortedColumn===col.name;
  state.sortDirection=same?(state.sortDirection==='asc'?'desc':'asc'):(NUMERIC_FIELDS.has(col.name)?'desc':'asc');
  state.sortedColumn=col.name;state.sortBy='column';
  document.getElementById('sortBy').value='column';
  document.getElementById('sortDirection').value=state.sortDirection;
  document.getElementById('columnSortLabel').textContent='Sütun: '+col.name;
  renderProductTable(rows);
 }));
 const body=document.getElementById('productTableBody');
 const grouped=displayGroupedRows(shown,cols);
 body.innerHTML=shown.length?grouped.html:'<tr><td colspan="'+cols.length+'" class="table-no-result">Aramaya uygun ürün yok.</td></tr>';
 const sumQty=shown.reduce((n,p)=>n+p.partiAdedi,0),unknownKg=shown.filter(p=>pWeight(p)===null).length;
 const sumKg=Math.round(shown.reduce((n,p)=>n+(pWeight(p)===null?0:pWeight(p)*p.partiAdedi),0)*100)/100;
 const totalByName={'Stok kodu':'TOPLAM','Ürün modeli / açıklama':`${shown.length} ürün satırı`,'Bu ay üretim (adet)':fmt(sumQty),'Parti ağırlığı (kg)':unknownKg?fmt(sumKg)+' *':fmt(sumKg)};
 document.getElementById('productTableFoot').innerHTML='<tr>'+cols.map(c=>`<td>${totalByName[c.name]||''}</td>`).join('')+'</tr>';
 document.getElementById('shownCount').textContent=`${shown.length} / ${rows.length} ürün gösteriliyor · ${grouped.groupCount} grup · ${cols.length} sütun${unknownKg?` · ${unknownKg} üründe ağırlık eksik, toplam kg eksik olabilir`:''}`;
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
