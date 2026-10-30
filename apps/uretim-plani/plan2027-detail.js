/* 2027 aylık teknik detay tablosu.
   Eski uygulamanın 40 gerçek sütun tanımı birebir korunmuştur.
   Mevcut 12 aylık plandaki KAYITLI miktarlar dinamik kullanılır; yeni parti dağıtımı oluşturulmaz. */
(()=>{'use strict';
const MONTHS=['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık'];
const fmt=n=>Number(n||0).toLocaleString('tr-TR');
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
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
 official2026Page(p.kod)!==null?(p.grup==='Şönt'?'Kod eşleşti; üreticiyle ölçü farkı var, revizyon teyidi gerekli':'Stok kodu resmî listede; teknik alanlar ayrıca karşılaştırılmalı'):
 official2026BaseCode(p.kod)!==null?'Standart baz model var; varyant doğrulanmadı':'Ürün kodu resmî tabloda yok';
const official2026Note=p=>
 official2026Page(p.kod)!==null?(p.grup==='Şönt'?'2026/12 resmî üretici listesinde Şönt ürünleri için ölçü farklılıkları bulundu; ağırlık ve bağlantı da farklı olabilir. Bu kaynak kayıtları otomatik değiştirilmedi; BOM/üretim revizyonunu doğrulayın.':'Stok kodu 2026/12 üretici listesinde. Kaynak akım, L, ölçü, kg ve bağlantı değerlerinin her biri ayrıca doğrulanmalıdır.'):
 official2026BaseCode(p.kod)!==null?'Standart '+official2026BaseCode(p.kod)+' üreticinin listesinde. G/GG varyantının akım, endüktans, ölçü, ağırlık ve bağlantısı ayrıca yayımlanmamış; baz ürün değerleri kopyalanmamalı.':
 p.kod==='GA5ÖZELHARM'?'Siparişe özel ürün; 2026 listesinde aynı kodla teknik tablo yok. Üretici teknik föyü gerekli.':
 '2026 listesinde aynı stok koduyla karşılık bulunamadı; üretici teknik föyü gerekli.';

const OFFICIAL_DATASHEETS={Şönt:'https://www.gruparge.com/wp-content/uploads/2025/05/SONT-REAKTORU-DATASHEET.pdf',Harmonik:'https://www.gruparge.com/wp-content/uploads/2025/05/HARMONIK-FILTRE-DATASHEET.pdf'};


function upperGroup(p){
 const model=String(p.model||'').toUpperCase(),code=String(p.kod||''),kind=String(p.altGrup||'');
 if(p.grup==='Şönt'){if(model.startsWith('SVC-R'))return 'SVC-R';if(model.startsWith('SRM'))return 'SRM';if(model.startsWith('SRT'))return 'SRT';return 'Diğer Şönt'}
 if(code.startsWith('GAGG'))return 'HRT-GG varyant';
 if(code.startsWith('GAG'))return 'HRT-G varyant';
 if(code==='GA5ÖZELHARM'||(!model.startsWith('HRM')&&!model.startsWith('HRT')))return 'Özel Harmonik';
 if(model.startsWith('HRM'))return 'HRM';
 if(kind.includes('5,67'))return 'HRT 5,67';
 if(kind.includes('14'))return 'HRT 14';
 if(kind.includes('<%7'))return 'HRT 7/7';
 return 'HRT 7/8';
}
const upperOrder=['SVC-R','SRM','SRT','HRM','HRT 5,67','HRT 7/8','HRT 7/7','HRT 14','HRT-G varyant','HRT-GG varyant','Özel Harmonik'];
function upperRank(p){const idx=upperOrder.indexOf(upperGroup(p));return idx<0?99:idx}

const COLS=[
 {name:'Stok kodu',kind:'main',get:p=>p.kod},
 {name:'Ürün modeli / açıklama',kind:'main',get:p=>p.model},
 {name:'Ürüne özel teknik föy',kind:'main',get:p=>p.id,productCard:true},
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
COLS.splice(2,0,{name:'Üst ürün grubu',kind:'main',get:p=>upperGroup(p)});
function presentValue(value,col){
 if(value===null||value===undefined||value==='')return '<span class="missing">—</span>';
 if(col.productCard)return '<a class="product-sheet-link" href="urun.html?id='+encodeURIComponent(String(value))+'" target="_blank" rel="noopener noreferrer">Bu ürünün föyünü aç ↗</a>';
 if(col.link&&typeof value==='string'&&/^https:\/\//i.test(value))return `<a href="${esc(value)}" target="_blank" rel="noopener noreferrer" title="${col.pdf?'Ürün grubunun resmî teknik PDF dosyası; her model için özel PDF değildir':col.baseReference?'Standart baz modelin verileri; G/GG varyantı doğrulanmış değildir':col.pdfList?'Üreticinin resmî 2026/12 teknik listesi; ilgili sayfaya git':esc(value)}">${col.pdf?'2025 grup datasheet PDF ↗':col.baseReference?'Baz model PDF ↗':col.pdfList?'2026/12 resmî liste ↗':esc(value)}</a>`;
 const v=col.fraction&&typeof value==='number'?(value*100).toLocaleString('tr-TR',{maximumFractionDigits:4})+' %':typeof value==='number'?value.toLocaleString('tr-TR',{maximumFractionDigits:8}):String(value);
 return esc(v);
}

const root=document.getElementById('monthDetail');
let selectedMonth=null,rows=[],order=[],search='',family='all',mode='all',customColumns=null,sortColumn='Üst ürün grubu',sortDirection='desc',rules=[],ruleLogic='and',ready=false,ruleId=0;
const numericColumns=new Set(['Yıllık miktar (adet)','Parti sayısı','Bu ay üretim (adet)','Birim ağırlık (kg)','Parti ağırlığı (kg)','Faz','Güç (kVAr)','Akım (A / Irms)','Endüktans L (mH)','p (%)','Kaynak Excel satırı']);
const $=id=>document.getElementById(id);
const sectionList=[['main','Kimlik ve teknik föy'],['plan','Üretim / ağırlık'],['identity','Sınıflandırma'],['technical','Teknik özellikler'],['review','Kıyas / katalog / datasheet / kaynak']];
function attach(){
 if(ready)return;ready=true;
 root.innerHTML=
 '<div class="detail-bar"><div><span class="detail-eyebrow">SEÇİLEN AYIN TÜM TEKNİK BİLGİLERİ</span><h2 id="detailTitle">Üretim detayları</h2><p id="detailInfo"></p></div><button type="button" id="detailClose" class="btn">Kapat ✕</button></div>'+
 '<div class="detail-actions">'+
 '<label>Ürün / özellik ara<input id="detailSearch" type="search" placeholder="Kod, model, güç, ölçü, kaynak ara…"></label>'+
 '<label>Ürün ailesi<select id="detailFamily"><option value="all">Tüm ürünler</option><option value="Şönt">Şönt</option><option value="Harmonik">Harmonik</option></select></label>'+
 '<label>Gösterilecek alanlar<select id="detailMode"><option value="all">Tüm '+COLS.length+' sütun</option><option value="technical">Teknik özellikler</option><option value="plan">Üretim ve miktar</option><option value="review">Katalog / datasheet / kıyas</option><option value="custom">Seçtiğim sütunlar</option></select></label>'+
 '<label>Sırala<select id="detailSort">'+COLS.map(c=>'<option value="'+esc(c.name)+'">'+esc(c.name)+'</option>').join('')+'</select></label>'+
 '<label>Sıralama yönü<select id="detailSortDir"><option value="desc">Azalan</option><option value="asc">Artan</option></select></label>'+
 '<button class="btn small" type="button" id="detailExport">↓ Ay detayını CSV indir</button></div>'+
 '<div class="detail-options"><details id="detailColPicker"><summary id="detailColSummary">Sütunları göster / gizle</summary><div class="detail-picker-body"><div class="detail-picker-actions"><button type="button" id="detailAllCols">Tüm '+COLS.length+' sütun</button><button type="button" id="detailMinCols">Sadece kod ve model</button></div><div id="detailCols"></div></div></details>'+
 '<details id="detailFilterBox"><summary>Gelişmiş filtreler <span id="detailRuleCount">(0)</span></summary><div class="detail-rule-panel"><div class="detail-rule-bar"><button type="button" id="detailAddRule">+ Koşul ekle</button><button type="button" id="detailClearRules">Temizle</button><label>Birleştir <select id="detailLogic"><option value="and">VE (hepsi)</option><option value="or">VEYA (biri)</option></select></label></div><div id="detailRules"></div></div></details></div>'+
 '<p class="detail-audit" id="detailAudit"></p>'+
 '<div class="technical-scroll" role="region" aria-label="Seçilen ay için tüm ürünlerin teknik ve kaynak verileri" tabindex="0"><table class="technical-table"><thead id="detailHead"></thead><tbody id="detailBody"></tbody><tfoot id="detailFoot"></tfoot></table></div>'+
 '<div class="detail-bottom" id="detailShown"></div>'+
 '<p class="detail-source-note">Aylık detay listesi üst ürün grubuna göre bloklar halinde sıralanır. Resmî grup datasheet bağlantıları ürün ailesine aittir; her stok kodu için ayrıca yayımlanmış ürün föyü oldukları iddia edilmez. Özel ve G/GG varyantlarda katalog doğrulaması ayrıca gösterilir.</p>';
 $('detailClose').addEventListener('click',()=>{selectedMonth=null;root.hidden=true;document.querySelectorAll('.month-open').forEach(b=>b.classList.remove('is-selected'))});
 $('detailSearch').addEventListener('input',e=>{search=e.target.value;renderTable()});
 $('detailFamily').addEventListener('change',e=>{family=e.target.value;renderTable()});
 $('detailMode').addEventListener('change',e=>{mode=e.target.value;renderColumns();renderTable()});
 $('detailSort').addEventListener('change',e=>{sortColumn=e.target.value;renderTable()});
 $('detailSortDir').addEventListener('change',e=>{sortDirection=e.target.value;renderTable()});
 $('detailAllCols').addEventListener('click',()=>{mode='all';customColumns=null;$('detailMode').value=mode;renderColumns();renderTable()});
 $('detailMinCols').addEventListener('click',()=>{mode='custom';customColumns=COLS.slice(0,2).map(c=>c.name);$('detailMode').value=mode;renderColumns();renderTable()});
 $('detailCols').addEventListener('change',e=>{
  const idx=Number(e.target.dataset.col);
  if(!Number.isInteger(idx)||!COLS[idx]||idx<2)return;
  const selected=new Set(activeCols().map(c=>c.name));if(e.target.checked)selected.add(COLS[idx].name);else selected.delete(COLS[idx].name);
  customColumns=[...selected];mode='custom';$('detailMode').value=mode;renderColumns();renderTable();
 });
 $('detailAddRule').addEventListener('click',()=>{rules.push({id:++ruleId,field:'Bu ay üretim (adet)',op:'gte',value:''});renderRules();renderTable()});
 $('detailClearRules').addEventListener('click',()=>{rules=[];renderRules();renderTable()});
 $('detailLogic').addEventListener('change',e=>{ruleLogic=e.target.value;renderTable()});
 $('detailRules').addEventListener('input',onRuleChange);
 $('detailRules').addEventListener('change',onRuleChange);
 $('detailRules').addEventListener('click',e=>{const btn=e.target.closest('[data-remove-rule]');if(!btn)return;rules=rules.filter(r=>r.id!==Number(btn.dataset.removeRule));renderRules();renderTable()});
 $('detailHead').addEventListener('click',e=>{const btn=e.target.closest('[data-sort]');if(!btn)return;const col=COLS[Number(btn.dataset.sort)];if(!col)return;if(sortColumn===col.name)sortDirection=sortDirection==='asc'?'desc':'asc';else{sortColumn=col.name;sortDirection=numericColumns.has(col.name)?'desc':'asc'}$('detailSort').value=sortColumn;$('detailSortDir').value=sortDirection;renderTable()});
 $('detailExport').addEventListener('click',exportDetail);
}
function onRuleChange(e){
 const id=Number(e.target.dataset.rule),prop=e.target.dataset.prop;
 const r=rules.find(x=>x.id===id);if(!r||!['field','op','value'].includes(prop))return;
 r[prop]=e.target.value;if(e.type==='change'&&prop==='field'){renderRules()}
 renderTable();
}
function activeCols(){
 if(mode==='all')return COLS;
 if(mode==='custom')return COLS.filter((c,i)=>i<2||(customColumns||[]).includes(c.name));
 return COLS.filter((c,i)=>i<2||c.kind===mode||(mode==='technical'&&c.kind==='identity'));
}
function renderColumns(){
 const selected=new Set(activeCols().map(c=>c.name));
 $('detailColSummary').textContent='Sütunları göster / gizle ('+selected.size+'/'+COLS.length+')';
 $('detailCols').innerHTML=sectionList.map(([kind,title])=>'<fieldset><legend>'+title+'</legend>'+COLS.map((c,i)=>({c,i})).filter(x=>x.c.kind===kind).map(({c,i})=>'<label><input data-col="'+i+'" type="checkbox" '+(selected.has(c.name)?'checked ':'')+(i<2?'disabled ':'')+'>'+esc(c.name)+'</label>').join('')+'</fieldset>').join('');
}
function renderRules(){
 $('detailRuleCount').textContent='('+rules.length+')';
 const opt=COLS.map(c=>'<option value="'+esc(c.name)+'">'+esc(c.name)+'</option>').join('');
 $('detailRules').innerHTML=rules.map(r=>'<div class="detail-rule"><select data-rule="'+r.id+'" data-prop="field">'+opt+'</select><select data-rule="'+r.id+'" data-prop="op"><option value="contains">İçerir</option><option value="eq">Eşit</option><option value="gte">En az (≥)</option><option value="lte">En çok (≤)</option><option value="empty">Boş</option><option value="notEmpty">Dolu</option></select><input data-rule="'+r.id+'" data-prop="value" value="'+esc(r.value)+'" placeholder="Değer"><button type="button" data-remove-rule="'+r.id+'">×</button></div>').join('');
 for(const r of rules){const group=$('detailRules').querySelector('[data-prop="field"][data-rule="'+r.id+'"]');const op=$('detailRules').querySelector('[data-prop="op"][data-rule="'+r.id+'"]');if(group)group.value=r.field;if(op)op.value=r.op;}
}
function matchRule(p,r){
 const c=COLS.find(x=>x.name===r.field);if(!c)return true;
 const value=c.get(p),blank=value===null||value===undefined||value==='';
 if(r.op==='empty')return blank;
 if(r.op==='notEmpty')return !blank;
 if(String(r.value).trim()==='')return true;
 if(blank)return false;
 if(r.op==='contains')return String(value).toLocaleLowerCase('tr-TR').includes(String(r.value).toLocaleLowerCase('tr-TR'));
 const a=Number(value),b=Number(String(r.value).replace(',','.'));
 if(Number.isFinite(a)&&Number.isFinite(b)){
  if(r.op==='gte')return a>=b;if(r.op==='lte')return a<=b;if(r.op==='eq')return a===b;
 }
 return r.op==='eq'?String(value).toLocaleLowerCase('tr-TR')===String(r.value).toLocaleLowerCase('tr-TR'):false;
}
function valueForSort(p,c){const value=c.get(p);if(value===null||value===undefined||value==='')return null;const n=typeof value==='number'?value:Number(String(value).replace(',','.'));return numericColumns.has(c.name)&&Number.isFinite(n)?n:String(value).toLocaleLowerCase('tr-TR')}
function getShown(){
 const s=search.toLocaleLowerCase('tr-TR').trim();
 const filtered=rows.filter(p=>
  (family==='all'||p.grup===family)&&(!s||COLS.some(c=>String(c.get(p)??'').toLocaleLowerCase('tr-TR').includes(s)))&&
  (rules.length===0||(ruleLogic==='and'?rules.every(r=>matchRule(p,r)):rules.some(r=>matchRule(p,r))))
 );
 const sort=COLS.find(c=>c.name===sortColumn),orderIndex=new Map(order.map((id,i)=>[id,i]));
 filtered.sort((a,b)=>{
  if(!sort)return upperRank(a)-upperRank(b)||(orderIndex.get(a.id)||0)-(orderIndex.get(b.id)||0);
  if(sortColumn==='Üst ürün grubu')return upperRank(a)-upperRank(b)||b.partiAdedi-a.partiAdedi||(orderIndex.get(a.id)||0)-(orderIndex.get(b.id)||0);
  const aa=valueForSort(a,sort),bb=valueForSort(b,sort);
  if(aa===null&&bb!==null)return 1;if(bb===null&&aa!==null)return -1;
  let diff=0;
  if(typeof aa==='number'&&typeof bb==='number')diff=aa-bb;
  else diff=String(aa??'').localeCompare(String(bb??''),'tr',{numeric:true});
  return diff===0?(orderIndex.get(a.id)||0)-(orderIndex.get(b.id)||0):(sortDirection==='desc'?-diff:diff);
 });return filtered;
}
function renderTable(){
 if(selectedMonth===null)return;
 const shown=getShown(),cols=activeCols();
 const groupStarts=new Set(shown.map((p,i)=>i===0||upperGroup(p)!==upperGroup(shown[i-1])?i:-1));
 $('detailHead').innerHTML='<tr>'+cols.map(c=>'<th scope="col"><button type="button" data-sort="'+COLS.indexOf(c)+'" title="Bu sütuna göre sırala">'+esc(c.name)+(c.name===sortColumn?(sortDirection==='desc'?' ▼':' ▲'):' ↕')+'</button></th>').join('')+'</tr>';
 $('detailBody').innerHTML=shown.length?shown.map((p,j)=>'<tr'+(groupStarts.has(j)?' class="detail-group-start"':'')+'>'+cols.map((c,i)=>{
  const v=c.get(p),t=i===0?'<a href="urun.html?id='+encodeURIComponent(p.id)+'" target="_blank" rel="noopener" class="detail-product">'+presentValue(v,c)+'</a>':presentValue(v,c);
  return '<td class="'+(typeof v==='number'?'detail-numeric':'')+(c.long?' detail-long':'')+'">'+t+'</td>';
 }).join('')+'</tr>').join(''):'<tr><td colspan="'+cols.length+'">Seçilen filtrelerle eşleşen ürün yok.</td></tr>';
 const totalQty=shown.reduce((n,p)=>n+p.partiAdedi,0),kgKnown=shown.reduce((n,p)=>n+(pWeight(p)??0)*p.partiAdedi,0),kgUnknown=shown.filter(p=>pWeight(p)===null).length;
 $('detailFoot').innerHTML='<tr>'+cols.map(c=>'<td>'+(
  c.name==='Stok kodu'?'TOPLAM':c.name==='Ürün modeli / açıklama'?shown.length+' ürün':
  c.name==='Bu ay üretim (adet)'?fmt(totalQty):c.name==='Parti ağırlığı (kg)'?fmt(Math.round(kgKnown*100)/100)+(kgUnknown?' *':''):''
 )+'</td>').join('')+'</tr>';
 $('detailShown').textContent=shown.length+' / '+rows.length+' ürün · '+cols.length+' / '+COLS.length+' teknik ve kaynak sütunu · '+fmt(totalQty)+' adet'+(kgUnknown?' · '+kgUnknown+' üründe ağırlık eksik':'');
 const exact=shown.filter(p=>official2026Page(p.kod)!==null).length;
 const base=shown.filter(p=>official2026BaseCode(p.kod)!==null).length;
 $('detailAudit').textContent=exact+' üründe katalog kodu doğrudan eşleşiyor · '+base+' varyant yalnız baz ürün referanslı · '+(shown.length-exact-base)+' üründe doğrudan katalog kodu eşleşmesi yok.';
}
function refreshedRows(){
 if(selectedMonth===null)return;
 const byId=new Map(rows.map(p=>[p.id,p]));
 rows=sourceProducts.filter(p=>p.monthly[selectedMonth]>0).map(p=>({...p,parti:p.monthly.filter(v=>v>0).length,partiAdedi:p.monthly[selectedMonth],month:selectedMonth}));
 const sum=rows.reduce((n,p)=>n+p.partiAdedi,0);
 $('detailTitle').textContent=MONTHS[selectedMonth]+' · '+(rows[0]?.grup||'Üretim')+' teknik ürün listesi';
 $('detailInfo').textContent=rows.length+' ürün kaydı · '+fmt(sum)+' adet üretim · '+COLS.length+' teknik/kaynak sütunu · Ürün föyü ve üretici datasheet bağlantıları';
 renderTable();
}
let sourceProducts=[];
function open(month,products,sortOrder){
 if(!Number.isInteger(month)||month<0||month>11)return;
 attach();selectedMonth=month;sourceProducts=products;order=sortOrder.slice();
 root.hidden=false;refreshedRows();
 document.querySelectorAll('.month-open').forEach(btn=>btn.classList.toggle('is-selected',Number(btn.dataset.month)===month));
 root.scrollIntoView({behavior:'smooth',block:'start'});
}
function refresh(products,sortOrder){
 if(selectedMonth===null)return;
 sourceProducts=products;order=sortOrder.slice();refreshedRows();
}
function close(){selectedMonth=null;root.hidden=true}
function month(){return selectedMonth}
function exportDetail(){
 if(selectedMonth===null)return;
 const data=[['Ürün kimliği','Ay',...COLS.map(c=>c.name)]];
 for(const p of getShown())data.push([p.id,MONTHS[selectedMonth],...COLS.map(c=>c.get(p))]);
 const csv='\ufeff'+data.map(x=>x.map(v=>'"'+String(v==null?'':v).replace(/"/g,'""')+'"').join(';')).join('\r\n');
 const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));
 const a=document.createElement('a');a.href=url;a.download='2027_'+MONTHS[selectedMonth]+'_Uretim_Teknik_Ozellikler.csv';document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
window.ProductionMonthDetails={open,refresh,month,close,columns:COLS.length};
})();