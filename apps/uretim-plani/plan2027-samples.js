/* Numune ve Teknik Kapsam — 2027 ürün portföyü.
   Üretim planından bağımsız görünüm. Yıllık miktarlar ürün verisinden,
   numune statüsü yalnız kaynak inceleme önerisinden türetilir.
   Fiziksel ortak üretim / numune kapsama onayı varsayılmaz. */
(()=>{'use strict';
const $=id=>document.getElementById(id);
const esc=v=>String(v==null?'':v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const val=(v,missing='—')=>(v===null||v===undefined||v===''||v==='Bilinmiyor')?missing:(typeof v==='number'?v.toLocaleString('tr-TR'):String(v));
const qty=n=>Number(n||0).toLocaleString('tr-TR');
const pct=(n,total)=>total?(100*n/total).toLocaleString('tr-TR',{minimumFractionDigits:2,maximumFractionDigits:2})+'%':'—';
const raw=(p,name)=>p.tamKayit&&Object.prototype.hasOwnProperty.call(p.tamKayit,name)?p.tamKayit[name]:null;
const byFamily=(p,shunt,harmonic)=>raw(p,p.grup==='Şönt'?shunt:harmonic);
const GROUPS={
 'Şönt':['SVC-R','SRM','SRT','Diğer Şönt'],
 'Harmonik':['HRM','HRT 5,67','HRT 7/8','HRT 7/7','HRT 14','HRT-G varyant','HRT-GG varyant','Özel Harmonik']
};
const OFFICIAL_RANGES=[[5001,5003],[5101,5108],[5201,5212],[5311,5317],[5411,5417],[5511,5517],[5321,5339],[5629,5639],[5521,5539],[5421,5439]];
const datasheets={
 'Şönt':'https://www.gruparge.com/wp-content/uploads/2025/05/SONT-REAKTORU-DATASHEET.pdf',
 'Harmonik':'https://www.gruparge.com/wp-content/uploads/2025/05/HARMONIK-FILTRE-DATASHEET.pdf'
};
function group(p){
 const model=String(p.model||'').toUpperCase(),code=String(p.kod||''),kind=String(p.altGrup||'');
 if(p.grup==='Şönt'){
  if(model.startsWith('SVC-R'))return 'SVC-R';
  if(model.startsWith('SRM'))return 'SRM';
  if(model.startsWith('SRT'))return 'SRT';
  return 'Diğer Şönt';
 }
 if(code.startsWith('GAGG'))return 'HRT-GG varyant';
 if(code.startsWith('GAG'))return 'HRT-G varyant';
 if(code==='GA5ÖZELHARM'||(!model.startsWith('HRM')&&!model.startsWith('HRT')))return 'Özel Harmonik';
 if(model.startsWith('HRM'))return 'HRM';
 if(kind.includes('5,67'))return 'HRT 5,67';
 if(kind.includes('14'))return 'HRT 14';
 if(kind.includes('<%7'))return 'HRT 7/7';
 return 'HRT 7/8';
}
function official(p){
 const m=String(p.kod||'').match(/^GA(\d{4})$/);
 return !!m&&OFFICIAL_RANGES.some(([lo,hi])=>Number(m[1])>=lo&&Number(m[1])<=hi);
}
/* 2026 ortak numune matrisi: kaynak dosyadaki fiziksel inceleme adayları.
   Paketlenmiş ürün teknik kaydının "Numune / kontrol" alanı bazı ürünlerde
   boş olduğundan tek başına o alana güvenilmez (GA5002/GA5106 vb.).
   Yalnızca 17 kaynakta açıkça işaretlenmiş ürün burada adaydır.
   6 "İlk fiziksel numune", 11 "Kıyas numunesi". */
const PRIMARY_SAMPLE_CODES=new Set(['GA5002','GA5106','GA5212','GA5436','GA5426','GA5412']);
const PHYSICAL_COMPARISON_CODES=new Set(['GA5102','GA5104','GA5108','GA5204','GA5207','GA5209','GA5636','GA5536','GA5429','GA5336','GA5415']);
function sampleStatus(p){
 const code=String(p.kod||'').trim().toUpperCase();
 if(PRIMARY_SAMPLE_CODES.has(code))return {label:'Ana numune',type:'main',hint:'Kaynak inceleme matrisi: ilk fiziksel numune adayı. Satın alma kararı değildir.',physical:true,priority:'ilk'};
 if(PHYSICAL_COMPARISON_CODES.has(code))return {label:'Ana numune',type:'main',hint:'Kaynak inceleme matrisi: ayrı alınması önerilen fiziksel kıyas numunesi. Satın alma kararı değildir.',physical:true,priority:'kıyas'};
 if(official(p))return {label:'Kıyas',type:'compare',hint:'2026 katalog karşılığı mevcut; kaynak numune matrisi doküman/sökmeden kıyas öneriyor. Fiziksel yapısal kapsam onayı değildir.',physical:false};
 return {label:'Bilgiler doğrulanmadı',type:'unknown',hint:'2026/12 katalogda teknik eşleşme veya özel ürün reçetesi doğrulanmadı. Bobin farkı saptanmış değildir.',physical:false};
}
function reviewText(p){
 const note=raw(p,'Seçilme veya kıyas nedeni')||raw(p,'İnceleme / eksik bilgi');
 return val(note);
}
function provisionalCoil(p){
 if(p.coil===1||p.coil===3)return p.coil+'*';
 return '—';
}
function sourceLink(p){
 const url=byFamily(p,'Kaynak URL','Kaynak bağlantısı');
 return typeof url==='string'&&/^https?:\/\//i.test(url)?url:null;
}
function verifiedField(p,name){
 const v=raw(p,name);
 return v===null||v===undefined||String(v).trim()===''||/bilinmiyor|doğrulanmadı|belirsiz/i.test(String(v))?'Doğrulanmadı':v;
}
// Kaynak numune matrisinde doğrulanmış temel ürün sınıfı. Paket kayıttaki
// Faz alanı boşsa yalnız aile kodundan kesin ayırt edilebilen tipler doldurulur.
// G/GG ve özel modeller için faz tahmini yapılmaz.
function technicalPhase(p){
 const recorded=raw(p,'Faz');
 if(recorded!==null&&recorded!==undefined&&recorded!=='')return recorded;
 const code=String(p.kod||'').trim().toUpperCase(),model=String(p.model||'').trim().toUpperCase();
 if(code.startsWith('GAG')||code==='GA5ÖZELHARM')return null;
 if(model.startsWith('SVC-R')||model.startsWith('SRM')||model.startsWith('HRM'))return 1;
 if(model.startsWith('SRT')||model.startsWith('HRT'))return 3;
 return null;
}
function technicalFields(p){
 return [
  p.kod,p.model,sampleStatus(p).label,p.annual,
  technicalPhase(p),raw(p,'Güç (kVAr)'),
  byFamily(p,'Akım (A)','Akım (Irms, A)'),raw(p,'L (mH)'),
  raw(p,'p (%)'),raw(p,'THDv tasarım sınıfı'),
  byFamily(p,'Ölçü G×Y×D (mm)','Dış ölçüler (mm)'),
  typeof p.kg==='number'&&p.kg>0?p.kg:null,
  byFamily(p,'Bağlantı tipi','Bağlantı'),provisionalCoil(p),
  verifiedField(p,'Nüve tipi'),verifiedField(p,'Tel / levha'),verifiedField(p,'İzolasyon'),verifiedField(p,'Vernik / emprenye'),
  byFamily(p,'Sarım tipi (tel/folyo)','Sarım iletken biçimi'),
  raw(p,'Yapı referansı (2025 çizimi)'),
  raw(p,'Teknik inceleme grubu'),
  reviewText(p),
  byFamily(p,'2026/12 katalog durumu','Teknik veri durumu'),
  raw(p,'İnceleme / eksik bilgi'),
  p.kaynakDosya,p.kaynakSatir
 ];
}
const HEADERS=[
 ['Ürün kodu','code'],['Model / açıklama','model'],['Numune / inceleme','sample'],
 ['Yıllık adet','count'],['Toplamdaki pay (%)','percent'],
 ['Faz','small'],['Güç (kVAr)','small'],['Akım (A)','small'],['L (mH)','small'],
 ['p (%)','small'],['THDv','value'],['Ölçüler (mm)','dimension'],['Ağırlık (kg)','small'],
 ['Bağlantı','value'],['Bobin*','small'],['Nüve','value'],['Tel / levha','value'],['İzolasyon','value'],['Vernik / emprenye','value'],['Sarım / iletken','value'],
 ['Yapı / çizim referansı','value'],['Teknik inceleme sınıfı','text'],
 ['Seçilme / kıyas nedeni','long'],['Katalog durumu','long'],
 ['Eksik teknik bilgiler','long'],['Kaynak dosya','text'],['Kaynak satırı','small'],
 ['Ürün föyü','link'],['Aile datasheet','link'],['Kaynak bağlantısı','link']
];
let products=[],search='',family='Tümü',catalog=HEADERS,initComplete=false;
function summarize(){
 const groups=new Map(),familyTotals={'Şönt':0,'Harmonik':0};
 for(const p of products){
  const annual=Number(p.annual)||0;familyTotals[p.grup]=(familyTotals[p.grup]||0)+annual;
  const key=p.grup+'|'+group(p);
  if(!groups.has(key))groups.set(key,{family:p.grup,group:group(p),annual:0,all:[],shown:[]});
  const g=groups.get(key);g.annual+=annual;g.all.push(p);
 }
 return {groups,familyTotals,annual:products.reduce((t,p)=>t+(Number(p.annual)||0),0)};
}
function visible(p){
 return (family==='Tümü'||p.grup===family)&&(p.kod+' '+p.model+' '+group(p)+' '+val(raw(p,'Numune / kontrol'),'')).toLocaleLowerCase('tr-TR').includes(search.toLocaleLowerCase('tr-TR'));
}
function rowCells(p,g,totals){
 const t=technicalFields(p),status=sampleStatus(p);
 const fields=[
  '<a class="sample-product-link" href="urun.html?id='+encodeURIComponent(p.id)+'" target="_blank" rel="noopener">'+esc(p.kod)+'</a>',
  esc(val(t[1])),
  '<span class="sample-status '+status.type+'" title="'+esc(status.hint)+'">'+esc(status.label)+'</span>',
  '<strong class="sample-amount">'+qty(p.annual)+'</strong>',
  pct(p.annual,totals.annual),
  ...t.slice(4).map(v=>esc(val(v))),
  '<a href="urun.html?id='+encodeURIComponent(p.id)+'" target="_blank" rel="noopener">Teknik föy</a>',
  '<a href="'+esc(datasheets[p.grup]||'#')+'" target="_blank" rel="noopener">PDF</a>',
  (sourceLink(p)?'<a href="'+esc(sourceLink(p))+'" target="_blank" rel="noopener">Kaynak</a>':'—')
 ];
 if(fields.length!==HEADERS.length)throw Error('Numune tablosu sütun eşleşme hatası: '+fields.length+' ≠ '+HEADERS.length);
 return '<tr class="sample-product-row">'+fields.map((x,i)=>'<td class="sample-cell-'+HEADERS[i][1]+'">'+x+'</td>').join('')+'</tr>';
}
function render(){
 if(!initComplete)return;
 const totals=summarize(),familyList=['Şönt','Harmonik'];
 const shown=products.filter(visible),body=[];
 const head='<tr>'+HEADERS.map(([label,type])=>'<th scope="col" class="sample-head-'+type+'">'+esc(label)+'</th>').join('')+'</tr>';
 $('sampleHead').innerHTML=head;
 for(const fam of familyList){
  if(family!=='Tümü'&&family!==fam)continue;
  const groupRows=[];
  for(const gn of GROUPS[fam]){
   const g=totals.groups.get(fam+'|'+gn);
   if(!g)continue;
   const found=g.all.filter(visible);
   if(!found.length)continue;
   const groupPosition=GROUPS[fam].indexOf(gn);
   const sorted=found.slice().sort((a,b)=>{
    const weight=sampleStatus(a).type==='main'?0:sampleStatus(a).type==='compare'?1:2;
    const weightB=sampleStatus(b).type==='main'?0:sampleStatus(b).type==='compare'?1:2;
    return weight-weightB||b.annual-a.annual||a.kod.localeCompare(b.kod,'tr');
   });
   groupRows.push('<tr class="sample-group-row"><td colspan="'+HEADERS.length+'"><span class="sample-group-name">'+esc(gn)+'</span><span>'+qty(g.annual)+' adet</span><span>Yıllık üretimin '+pct(g.annual,totals.annual)+'’si</span><span class="sample-muted">'+g.all.length+' ürün'+(found.length!==g.all.length?' · '+found.length+' gösteriliyor':'')+'</span></td></tr>');
   for(const p of sorted)groupRows.push(rowCells(p,g,totals));
  }
  if(!groupRows.length)continue;
  body.push('<tr class="sample-family-row"><td colspan="'+HEADERS.length+'"><span>'+esc(fam.toLocaleUpperCase('tr-TR'))+'</span><strong>'+qty(totals.familyTotals[fam])+' adet/yıl</strong><span>Yıllık üretimin '+pct(totals.familyTotals[fam],totals.annual)+'’si</span></td></tr>');
  body.push(...groupRows);
 }
 $('sampleBody').innerHTML=body.join('')||'<tr><td colspan="'+HEADERS.length+'" class="sample-empty">Arama kriterlerine uygun ürün yok.</td></tr>';
 $('sampleMetrics').innerHTML='<span><b>Yıllık toplam</b> '+qty(totals.annual)+' adet</span><span><b>Şönt</b> '+qty(totals.familyTotals['Şönt'])+' · '+pct(totals.familyTotals['Şönt'],totals.annual)+'</span><span><b>Harmonik</b> '+qty(totals.familyTotals['Harmonik'])+' · '+pct(totals.familyTotals['Harmonik'],totals.annual)+'</span><span><b>Fiziksel numune adayları</b> '+products.filter(p=>sampleStatus(p).physical).length+' ürün (6 ilk + 11 kıyas)</span><span class="sample-count">'+shown.length+' / '+products.length+' ürün</span>';
}
function exportCSV(){
 const t=summarize();
 const rows=[['Aile','Üst ürün grubu',...HEADERS.map(h=>h[0])]];
 for(const fam of ['Şönt','Harmonik'])for(const gn of GROUPS[fam]){
  const g=t.groups.get(fam+'|'+gn);if(!g)continue;
  for(const p of g.all.filter(visible)){
   const values=technicalFields(p);
   const add=[p.kod,p.model,sampleStatus(p).label,p.annual,pct(p.annual,t.annual),...values.slice(4),
    'urun.html?id='+p.id,datasheets[fam],sourceLink(p)||''];
   if(add.length!==HEADERS.length)throw Error('CSV alan eşleşmesi başarısız.');
   rows.push([fam,gn,...add]);
  }
 }
 const encode=s=>'"'+String(s==null?'':s).replace(/"/g,'""')+'"';
 const blob=new Blob(['\ufeff'+rows.map(row=>row.map(encode).join(';')).join('\r\n')],{type:'text/csv;charset=utf-8'});
 const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='2027-numune-teknik-kapsam.csv';document.body.appendChild(a);a.click();a.remove();URL.revokeObjectURL(url);
}
function showPage(name){
 const sample=name==='samples';
 $('productionView').hidden=sample;
 $('sampleView').hidden=!sample;
 $('tabProduction').classList.toggle('is-active',!sample);
 $('tabSamples').classList.toggle('is-active',sample);
 $('tabProduction').setAttribute('aria-selected',String(!sample));
 $('tabSamples').setAttribute('aria-selected',String(sample));
 document.title=(sample?'Numune ve Teknik Kapsam':'Üretim Planlama')+' | Şönt ve Harmonik';
 if(sample)render();
}
function init(list){
 if(!Array.isArray(list)||!list.length)throw Error('Ürün verileri yüklenmeden numune görünümü açılamaz.');
 products=list;
 if(products.some(p=>!p.id||!p.kod||!p.grup||!Number.isFinite(p.annual)||p.annual<=0))throw Error('Numune sayfası ürün verileri geçersiz.');
 $('tabProduction').addEventListener('click',()=>showPage('production'));
 $('tabSamples').addEventListener('click',()=>showPage('samples'));
 $('sampleSearch').addEventListener('input',e=>{search=e.target.value||'';render()});
 $('sampleFamily').addEventListener('change',e=>{family=e.target.value;render()});
 $('sampleClear').addEventListener('click',()=>{family='Tümü';search='';$('sampleSearch').value='';$('sampleFamily').value='Tümü';render()});
 $('sampleExport').addEventListener('click',exportCSV);
 initComplete=true;render();
 showPage(location.hash==='#numune'?'samples':'production');
}
window.SampleCoverageMatrix={init,render,group,status:sampleStatus,columns:HEADERS.length};
})();