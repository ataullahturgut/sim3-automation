/* Numune ve Teknik Kapsam — Şönt makine yatırımı teknik veri girişi.
   Onaylanan düzen: 1 Ürün(5) → 4 Mevcut teknik(10) → 2 Sarım(9) → 3 Emprenye(4).
   Şönt alanları fiziksel ölçüm olmadan varsayımla doldurulmaz.
   Harmonik kayıtları okunur; Şönt taslak girişleri ayrı yerel depoda saklanır. */
(()=>{'use strict';
const $=id=>document.getElementById(id);
const esc=v=>String(v==null?'':v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const qty=n=>Number(n||0).toLocaleString('tr-TR');
const pct=(v,n)=>n?(100*v/n).toLocaleString('tr-TR',{minimumFractionDigits:2,maximumFractionDigits:2})+'%':'—';
const val=v=>v===null||v===undefined||v===''||/^(?:unresolved|unknown|bilinmiyor|belirsiz)$/i.test(String(v))?'—':typeof v==='number'?v.toLocaleString('tr-TR'):String(v);
const raw=(p,k)=>p.tamKayit&&Object.prototype.hasOwnProperty.call(p.tamKayit,k)?p.tamKayit[k]:null;
const byFamily=(p,shunt,harmonic)=>raw(p,p.grup==='Şönt'?shunt:harmonic);
const STORAGE='simulation3.shunt.machine-inputs.v1';
const FORMAT='simulation3-shunt-machine-inputs';
const VERSION=1;
const GROUPS={
 'Şönt':['SVC-R','SRM','SRT','Diğer Şönt'],
 'Harmonik':['HRM','HRT 5,67','HRT 7/8','HRT 7/7','HRT 14','HRT-G varyant','HRT-GG varyant','Özel Harmonik']
};
const DATASHEETS={
 'Şönt':'https://www.gruparge.com/wp-content/uploads/2025/05/SONT-REAKTORU-DATASHEET.pdf',
 'Harmonik':'https://www.gruparge.com/wp-content/uploads/2025/05/HARMONIK-FILTRE-DATASHEET.pdf'
};
const CONDUCTOR=[
 ['','Belirlenmedi'],
 ['cu-round','Bakır · Yuvarlak tel'],['cu-rect','Bakır · Dikdörtgen tel'],['cu-foil','Bakır · Folyo/levha'],
 ['al-round','Alüminyum · Yuvarlak tel'],['al-rect','Alüminyum · Dikdörtgen tel'],['al-foil','Alüminyum · Folyo/levha'],
 ['mixed','Birden fazla iletken türü'],['other','Diğer']
];
const CORES=[
 ['','Belirlenmedi'],['ei','Lamine sac · E/I'],['ui','Lamine sac · U/I'],
 ['cut','Kesilmiş C nüve'],['toroid','Toroidal nüve'],['other','Diğer']
];
const PARTS=[
 ['','Belirlenmedi'],['coil','Yalnız bobin'],['coilcore','Bobin ve nüve montajı'],
 ['full','Komple reaktör'],['multi','Birden fazla aşama'],['none','Emprenye yapılmıyor']
];
const METHODS=[
 ['','Belirlenmedi'],['dip','Atmosferik daldırma'],
 ['vacuum','Vakumlu emprenye'],['vpi','Vakum-basınç (VPI)'],
 ['trickle','Damlatma (trickle)'],['other','Diğer'],['none','Uygulanmıyor']
];
const INSULATIONS=[
 'Emaye kaplama','DMD','NMN','Elektriksel izolasyon kâğıdı',
 'Presbant','Polyester (PET) film','Poliimid film','Cam elyaf','Diğer'
];
const INPUTS=['coilCount','conductor','conductorSize','coilDimensions','coilWeightKg','turns','windingMinutes','core','insulations','impPart','resinMode','resinCode','impMethod','impCycle'];
const NUMERIC=new Set(['coilCount','coilWeightKg','turns','windingMinutes','impCycle']);
const INTEGER=new Set(['coilCount','turns']);
const TEXT_LIMITS={conductorSize:90,coilDimensions:140,resinCode:90};
const HEADERS=[
 ['Ürün kodu','code'],['Model / açıklama','model'],['Yıllık üretim adedi','count'],
 ['Şönt / aile payı (%)','percent'],['İnceleme önceliği','sample'],
 ['Ürün dış ölçüleri (mm)','dimension'],['Ürün toplam ağırlığı (kg)','weight'],
 ['Bağlantı','value'],['Faz','small'],['Güç (kVAr)','small'],['Akım (A)','small'],
 ['L (mH)','small'],['p (%)','small'],['THDv','value'],['Aile datasheet','link'],
 ['Bobin adedi / ürün','edit'],['İletken türü / malzemesi','edit'],['İletken kesiti (mm)','edit'],
 ['Bobin ölçüleri (mm)','edit'],['Bobin ağırlığı (kg)','edit'],['Tur sayısı','edit'],
 ['Sarım süresi (dk/bobin)','edit'],['Nüve tipi','edit'],['İzolasyon tipi','edit'],
 ['Emprenye edilen parça','edit'],['Vernik / reçine kodu','edit'],
 ['Emprenye yöntemi','edit'],['Emprenye çevrimi (dk/parti)','edit']
];
if(HEADERS.length!==28)throw Error('28 sütun şeması geçersiz');
let products=[],search='',family='Tümü',ready=false,entries={},storageEnabled=true;
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
function priority(p){
 if(p.grup==='Şönt'){
  const m=window.ShuntMachineInvestment?.get(p.kod);
  if(!m)throw Error('Şönt inceleme kaydı bulunamadı: '+p.kod);
  const labels={A:'1 · Öncelikli inceleme',B:'2 · Hedefli kontrol',C:'3 · Sökmeden kontrol'};
  return {label:labels[m.priority],rank:'ABC'.indexOf(m.priority),className:'shunt-'+m.priority,
   hint:m.reason+' · Ölçüm: '+m.focus+' · Henüz kapasite onayı yok.'};
 }
 const code=String(p.kod||'').toUpperCase();
 const first=['GA5436','GA5426','GA5412'],compare=['GA5636','GA5536','GA5429','GA5336','GA5415'];
 if(first.includes(code))return {label:'İlk numune',rank:0,className:'main',hint:'Kaynak inceleme matrisi'};
 if(compare.includes(code))return {label:'Fiziksel kıyas',rank:0,className:'main',hint:'Kaynak inceleme matrisi'};
 const m=code.match(/^GA(\d{4})$/),n=m?Number(m[1]):0;
 const ranges=[[5311,5317],[5411,5417],[5511,5517],[5321,5339],[5629,5639],[5521,5539],[5421,5439]];
 return ranges.some(([lo,hi])=>n>=lo&&n<=hi)?
  {label:'Kıyas',rank:1,className:'compare',hint:'Kaynak katalog kıyası'}:
  {label:'Bilgiler doğrulanmadı',rank:2,className:'unknown',hint:'Kaynak inceleme matrisi'};
}
function summary(){
 const groups=new Map(),totals={'Şönt':0,'Harmonik':0};
 for(const p of products){
  totals[p.grup]=(totals[p.grup]||0)+p.annual;
  const key=p.grup+'|'+group(p);
  if(!groups.has(key))groups.set(key,{all:[],annual:0});
  groups.get(key).all.push(p);groups.get(key).annual+=p.annual;
 }
 return {groups,totals,annual:products.reduce((s,p)=>s+p.annual,0)};
}
function validInput(field,v){
 if(!INPUTS.includes(field))return null;
 if(field==='insulations')return Array.isArray(v)&&v.length<=INSULATIONS.length&&v.every(x=>INSULATIONS.includes(x))?[...new Set(v)]:null;
 if(NUMERIC.has(field)){
  if(v===''||v===null||v===undefined)return '';
  const n=Number(v);
  return Number.isFinite(n)&&n>0&&n<10000000&&(!INTEGER.has(field)||Number.isSafeInteger(n))?n:null;
 }
 if(typeof v!=='string')return null;
 if(field==='conductor')return CONDUCTOR.some(x=>x[0]===v)?v:null;
 if(field==='core')return CORES.some(x=>x[0]===v)?v:null;
 if(field==='impPart')return PARTS.some(x=>x[0]===v)?v:null;
 if(field==='impMethod')return METHODS.some(x=>x[0]===v)?v:null;
 if(field==='resinMode')return ['','code','none'].includes(v)?v:null;
 if(Object.prototype.hasOwnProperty.call(TEXT_LIMITS,field))return v.trim().slice(0,TEXT_LIMITS[field]);
 return null;
}
function cleanRecord(record){
 if(!record||typeof record!=='object'||Array.isArray(record))return {};
 const result={};
 for(const field of INPUTS){
  if(!Object.prototype.hasOwnProperty.call(record,field))continue;
  const v=validInput(field,record[field]);
  if(v!==null&&v!==''&&!(Array.isArray(v)&&!v.length))result[field]=v;
 }
 if(result.resinMode!=='code')delete result.resinCode;
 if(result.impPart==='none')result.impMethod='none';
 return result;
}
function saveRecord(code,field,value){
 if(!products.some(p=>p.grup==='Şönt'&&p.kod===code))return;
 const rec={...(entries[code]||{})};
 if(value===''||(Array.isArray(value)&&!value.length))delete rec[field];else rec[field]=value;
 const next=cleanRecord(rec);
 if(Object.keys(next).length)entries[code]=next;else delete entries[code];
 try{
  localStorage.setItem(STORAGE,JSON.stringify({format:FORMAT,version:VERSION,records:entries}));
  storageEnabled=true;notice('Teknik girişler bu tarayıcıya otomatik kaydedildi. Başka cihaz için JSON yedeği al.');
 }catch(e){storageEnabled=false;notice('Tarayıcıya kaydedilemedi. Veriler kaybolmadan JSON yedeği indir.','error');}
}
function loadSaved(){
 try{
  const data=localStorage.getItem(STORAGE);
  if(!data)return;
  const parsed=JSON.parse(data);
  if(parsed?.format!==FORMAT||parsed.version!==VERSION||!parsed.records||typeof parsed.records!=='object')throw Error('Geçersiz teknik kayıt');
  entries=cleanAll(parsed.records);
 }catch(e){storageEnabled=false;notice('Önceki kayıt okunamadı. Teknik veri yedeğinizi kontrol edin.','error');}
}
function cleanAll(records){
 if(!records||typeof records!=='object'||Array.isArray(records))throw Error('Kayıt içeriği geçersiz');
 const result={},known=new Set(products.filter(p=>p.grup==='Şönt').map(p=>p.kod));
 for(const [code,record] of Object.entries(records)){
  if(!known.has(code))throw Error('Bilinmeyen Şönt ürün kodu: '+code);
  const item=cleanRecord(record);
  if(Object.keys(item).length)result[code]=item;
 }
 return result;
}
function notice(message,kind='ok'){
 const el=$('sampleEditNotice');
 if(el){el.textContent=message;el.className='sample-edit-notice'+(kind==='error'?' error':'');}
}
function get(p,key){return entries[p.kod]?.[key]??'';}
function optionList(list,value){return list.map(([k,l])=>'<option value="'+esc(k)+'"'+(String(value)===k?' selected':'')+'>'+esc(l)+'</option>').join('');}
function select(p,key,options){
 return '<select class="sample-edit" data-code="'+esc(p.kod)+'" data-field="'+key+'" aria-label="'+esc(p.kod+' · '+HEADERS.find(x=>x[0])?.[0])+'">'+optionList(options,get(p,key))+'</select>';
}
function numberInput(p,key,placeholder,integer=false){
 const v=get(p,key);
 return '<input class="sample-edit sample-edit-number" type="number" min="'+(integer?'1':'0.001')+'" step="'+(integer?'1':'any')+'" inputmode="decimal" placeholder="'+esc(placeholder)+'" data-code="'+esc(p.kod)+'" data-field="'+key+'" value="'+esc(v)+'" aria-label="'+esc(p.kod+' '+key)+'">';
}
function textInput(p,key,placeholder){
 const v=get(p,key),max=TEXT_LIMITS[key]||100;
 return '<input class="sample-edit sample-edit-text" type="text" maxlength="'+max+'" placeholder="'+esc(placeholder)+'" data-code="'+esc(p.kod)+'" data-field="'+key+'" value="'+esc(v)+'" aria-label="'+esc(p.kod+' '+key)+'">';
}
function resinCell(p){
 const mode=get(p,'resinMode'),code=get(p,'resinCode');
 return '<div class="sample-resin-editor"><select class="sample-edit" data-code="'+esc(p.kod)+'" data-field="resinMode" aria-label="Vernik veya reçine seçimi">'+
 optionList([['','Belirlenmedi'],['code','Malzeme kodu gir / seç'],['none','Kullanılmıyor']],mode)+'</select>'+
 (mode==='code'?'<input class="sample-edit sample-edit-text" type="text" list="sampleResinCodeList" maxlength="90" placeholder="Üretici malzeme kodu" data-code="'+esc(p.kod)+'" data-field="resinCode" value="'+esc(code)+'" aria-label="Üretici vernik reçine kodu">':'')+'</div>';
}
function resinCodes(){
 return [...new Set(Object.values(entries).filter(x=>x.resinMode==='code'&&x.resinCode).map(x=>x.resinCode))].sort((a,b)=>a.localeCompare(b,'tr'));
}
function insulationCell(p){
 const values=get(p,'insulations')||[],summary=values.length?values.join(', '):'Belirlenmedi';
 return '<details class="sample-multi"><summary>'+esc(summary)+'</summary><div class="sample-multi-content">'+INSULATIONS.map(item=>
 '<label><input type="checkbox" data-code="'+esc(p.kod)+'" data-field="insulations" value="'+esc(item)+'"'+(values.includes(item)?' checked':'')+'> '+esc(item)+'</label>').join('')+'</div></details>';
}
function harmonicOriginal(p,key){
 const map={
  conductor:raw(p,'Tel / levha')||raw(p,'Sarım iletken biçimi'),
  core:raw(p,'Nüve tipi'),
  insulations:raw(p,'İzolasyon'),
  resinMode:raw(p,'Vernik / emprenye'),
  coilCount:p.coil===1||p.coil===3?p.coil+'*':null
 };
 return Object.prototype.hasOwnProperty.call(map,key)?val(map[key]):'—';
}
function editable(p,key){
 if(p.grup!=='Şönt')return '<span class="sample-original" title="Harmonik kaynağındaki mevcut bilgi; Şönt veri giriş ekranından değiştirilemez">'+esc(harmonicOriginal(p,key))+'</span>';
 if(key==='coilCount'||key==='turns')return numberInput(p,key,'—',true);
 if(['coilWeightKg','windingMinutes','impCycle'].includes(key))return numberInput(p,key,'—');
 if(key==='conductor')return select(p,key,CONDUCTOR);
 if(key==='core')return select(p,key,CORES);
 if(key==='impPart')return select(p,key,PARTS);
 if(key==='impMethod')return select(p,key,METHODS);
 if(key==='insulations')return insulationCell(p);
 if(key==='resinMode')return resinCell(p);
 if(key==='conductorSize')return textInput(p,key,'Ø veya en×kalınlık');
 if(key==='coilDimensions')return textInput(p,key,'İç / dış / sarım eni');
 return '—';
}
function originalFields(p){
 return [
  p.kod,p.model,p.annual,'',priority(p).label,
  byFamily(p,'Ölçü G×Y×D (mm)','Dış ölçüler (mm)'),
  typeof p.kg==='number'&&p.kg>0?p.kg:null,
  byFamily(p,'Bağlantı tipi','Bağlantı'),
  raw(p,'Faz')??p.faz,raw(p,'Güç (kVAr)')??p.guc,
  byFamily(p,'Akım (A)','Akım (Irms, A)')??p.akim,
  raw(p,'L (mH)')??p.L,raw(p,'p (%)')??p.p,raw(p,'THDv tasarım sınıfı')??p.thdv,DATASHEETS[p.grup],
  ...['coilCount','conductor','conductorSize','coilDimensions','coilWeightKg','turns','windingMinutes','core','insulations','impPart','resinMode','impMethod','impCycle'].map(k=>p.grup==='Şönt'?get(p,k):harmonicOriginal(p,k))
 ];
}
function rowCells(p,totals){
 const priorityData=priority(p);
 const fields=[
  '<a class="sample-product-link" href="urun.html?id='+encodeURIComponent(p.id)+'" target="_blank" rel="noopener">'+esc(p.kod)+'</a>',
  esc(p.model),
  '<strong class="sample-amount">'+qty(p.annual)+'</strong>',
  pct(p.annual,totals[p.grup]),
  '<span class="sample-status '+esc(priorityData.className)+'" title="'+esc(priorityData.hint)+'">'+esc(priorityData.label)+'</span>',
  esc(val(byFamily(p,'Ölçü G×Y×D (mm)','Dış ölçüler (mm)'))),
  esc(val(typeof p.kg==='number'&&p.kg>0?p.kg:null)),
  esc(val(byFamily(p,'Bağlantı tipi','Bağlantı'))),
  esc(val(raw(p,'Faz')??p.faz)),esc(val(raw(p,'Güç (kVAr)')??p.guc)),
  esc(val(byFamily(p,'Akım (A)','Akım (Irms, A)')??p.akim)),
  esc(val(raw(p,'L (mH)')??p.L)),esc(val(raw(p,'p (%)')??p.p)),
  esc(val(raw(p,'THDv tasarım sınıfı')??p.thdv)),
  '<a href="'+esc(DATASHEETS[p.grup])+'" target="_blank" rel="noopener">PDF</a>',
  ...['coilCount','conductor','conductorSize','coilDimensions','coilWeightKg','turns','windingMinutes','core','insulations','impPart','resinMode','impMethod','impCycle'].map(k=>editable(p,k))
 ];
 if(fields.length!==HEADERS.length)throw Error('28 teknik sütun eşleşmedi: '+p.kod+' '+fields.length);
 return '<tr class="sample-product-row">'+fields.map((x,i)=>'<td class="sample-cell-'+HEADERS[i][1]+'">'+x+'</td>').join('')+'</tr>';
}
function searchVisible(p){
 const info=window.ShuntMachineInvestment?.get(p.kod);
 const hay=p.kod+' '+p.model+' '+group(p)+' '+(info?.reason||'')+' '+Object.values(entries[p.kod]||{}).join(' ')+' '+val(raw(p,'Numune / kontrol'));
 return (family==='Tümü'||p.grup===family)&&hay.toLocaleLowerCase('tr-TR').includes(search.toLocaleLowerCase('tr-TR'));
}
function render(){
 if(!ready)return;
 const {groups,totals,annual}=summary(),body=[];
 $('sampleHead').innerHTML='<tr class="sample-head-groups">'+
  '<th colspan="5">1 · Ürün / üretim</th><th colspan="10">4 · Mevcut teknik bilgiler</th>'+
  '<th colspan="9">2 · Sarım makinesi</th><th colspan="4">3 · Emprenye</th></tr>'+
  '<tr class="sample-head-fields">'+HEADERS.map(([label,type])=>'<th scope="col" class="sample-head-'+type+'">'+esc(label)+'</th>').join('')+'</tr>';
 for(const fam of ['Şönt','Harmonik']){
  if(family!=='Tümü'&&family!==fam)continue;
  const result=[];
  for(const gn of GROUPS[fam]){
   const g=groups.get(fam+'|'+gn);if(!g)continue;
   const found=g.all.filter(searchVisible).sort((a,b)=>priority(a).rank-priority(b).rank||b.annual-a.annual||a.kod.localeCompare(b.kod,'tr'));
   if(!found.length)continue;
   result.push('<tr class="sample-group-row"><td colspan="'+HEADERS.length+'"><span class="sample-group-name">'+esc(gn)+'</span><span>'+qty(g.annual)+' adet</span><span>'+esc(fam)+' içindeki pay '+pct(g.annual,totals[fam])+'</span><span class="sample-muted">'+found.length+' / '+g.all.length+' ürün</span></td></tr>');
   for(const p of found)result.push(rowCells(p,totals));
  }
  if(result.length){
   body.push('<tr class="sample-family-row"><td colspan="'+HEADERS.length+'"><strong>'+esc(fam.toLocaleUpperCase('tr-TR'))+'</strong> <span>'+qty(totals[fam])+' adet/yıl</span></td></tr>');
   body.push(...result);
  }
 }
 $('sampleBody').innerHTML=body.join('')||'<tr><td colspan="'+HEADERS.length+'" class="sample-empty">Arama kriterlerine uygun ürün bulunamadı.</td></tr>';
 const dl=$('sampleResinCodeList');if(dl)dl.innerHTML=resinCodes().map(code=>'<option value="'+esc(code)+'"></option>').join('');
 const guide=$('shuntProcurementGuide');if(guide)guide.hidden=family==='Harmonik';
 const shunt=products.filter(p=>p.grup==='Şönt'),stats=Object.fromEntries(['A','B','C'].map(k=>{
  const group=shunt.filter(p=>window.ShuntMachineInvestment?.get(p.kod)?.priority===k);
  return [k,{count:group.length,annual:group.reduce((s,p)=>s+p.annual,0)}];
 }));
 if(shunt.length!==25||totals['Şönt']!==35772||stats.A.count!==11||stats.B.count!==8||stats.C.count!==6||
    stats.A.annual!==32654||stats.B.annual!==2512||stats.C.annual!==606)throw Error('Şönt 11/8/6 ve miktar tutarlılık denetimi başarısız');
 const chosen=products.filter(searchVisible);
 $('sampleMetrics').innerHTML='<span><b>Yıllık toplam</b> '+qty(annual)+' adet</span><span><b>Şönt</b> '+qty(totals['Şönt'])+' adet</span>'+
 '<span><b>Harmonik</b> '+qty(totals['Harmonik'])+' adet</span><span><b>Şönt öncelikli inceleme</b> 11 ürün · '+pct(stats.A.annual,totals['Şönt'])+'</span>'+
 '<span class="sample-count">'+chosen.length+' / '+products.length+' ürün</span>';
 $('shuntSampleReview').innerHTML='<b>Şönt makine incelemesi:</b> 11 öncelikli ('+qty(stats.A.annual)+' adet), 8 hedefli ('+qty(stats.B.annual)+' adet), 6 ön kontrol ('+qty(stats.C.annual)+' adet). '+
 '<b>Sarım ve emprenye girişleri yalnız Şönt için düzenlenir.</b> Veriler doğrulanmadan makine kapasitesi kesinleştirilmez.';
}
function onCellChange(e){
 const el=e.target;
 if(!el?.dataset?.code||!el.dataset.field)return;
 const code=el.dataset.code,key=el.dataset.field;
 if(key==='insulations'){
  const existing=entries[code]?.insulations||[];
  const next=el.checked?[...new Set([...existing,el.value])]:existing.filter(v=>v!==el.value);
  saveRecord(code,key,next);
  const d=el.closest('details');if(d){const summary=d.querySelector('summary');if(summary)summary.textContent=next.length?next.join(', '):'Belirlenmedi';}
  return;
 }
 const v=validInput(key,el.value);
 if(v===null){notice('Geçersiz değer. Sayısal alanlara pozitif değer girilmeli.','error');el.focus();return;}
 saveRecord(code,key,v);
 if(key==='resinMode'){
  if(v!=='code')saveRecord(code,'resinCode','');
  render();
 }else if(key==='resinCode')render();
}
function download(name,content,type){
 const url=URL.createObjectURL(new Blob([content],{type})),a=document.createElement('a');
 a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();URL.revokeObjectURL(url);
}
function exportCsv(){
 const {groups,totals}=summary(),rows=[['Aile','Üst grup',...HEADERS.map(x=>x[0])]];
 for(const fam of ['Şönt','Harmonik'])for(const gn of GROUPS[fam]){
  const g=groups.get(fam+'|'+gn);if(!g)continue;
  for(const p of g.all.filter(searchVisible)){
   const fields=originalFields(p);fields[3]=pct(p.annual,totals[fam]);
   // Doğrudan teknik giriş verisi ayrı, insan okunur değerler CSV'de.
   if(p.grup==='Şönt'){
    const index={conductor:16,core:22,insulations:23,impPart:24,impMethod:26};
    for(const [key,i]of Object.entries(index)){
     const opts={conductor:CONDUCTOR,core:CORES,impPart:PARTS,impMethod:METHODS};
     fields[i]=key==='insulations'?(get(p,key)||[]).join(', '):(opts[key].find(x=>x[0]===get(p,key))?.[1]||'Belirlenmedi');
    }
    fields[25]=get(p,'resinMode')==='none'?'Kullanılmıyor':get(p,'resinMode')==='code'?(get(p,'resinCode')||'Kod girilecek'):'Belirlenmedi';
   }
   rows.push([fam,gn,...fields]);
  }
 }
 const encode=v=>'"'+String(v??'').replace(/"/g,'""')+'"';
 download('2027-numune-teknik-kapsam.csv','\ufeff'+rows.map(r=>r.map(encode).join(';')).join('\r\n'),'text/csv;charset=utf-8');
}
function downloadBackup(){
 download('sont-makine-teknik-girisler.json',JSON.stringify({format:FORMAT,version:VERSION,exportedAt:new Date().toISOString(),records:entries},null,2),'application/json;charset=utf-8');
}
async function uploadBackup(){
 const el=$('sampleImportFile'),file=el?.files?.[0];
 if(!file)return;
 try{
  if(file.size>1000000)throw Error('Yedek dosyası çok büyük');
  const json=JSON.parse(await file.text());
  if(json?.format!==FORMAT||json.version!==VERSION)throw Error('Yedek türü veya sürümü uyuşmuyor');
  const imported=cleanAll(json.records);
  const previous=entries;entries=imported;
  try{localStorage.setItem(STORAGE,JSON.stringify({format:FORMAT,version:VERSION,records:entries}));storageEnabled=true;}
  catch(e){entries=previous;throw Error('Tarayıcıya yazılamadı; önce verinin JSON yedeğini indirin')}
  render();notice('Teknik kayıt yedeği yüklendi. Veriler bu tarayıcıya kaydedildi.');
 }catch(e){notice('Yedek yüklenemedi: '+e.message,'error');}
 finally{el.value='';}
}
function init(list){
 if(!Array.isArray(list)||!list.length)throw Error('Numune sayfası ürün listesi eksik');
 products=list;
 if(products.some(p=>!p.id||!p.kod||!p.grup||!Number.isFinite(p.annual)||p.annual<=0))throw Error('Numune sayfası ürün kaydı geçersiz');
 loadSaved();
 $('tabProduction').addEventListener('click',()=>showPage('production'));
 $('tabSamples').addEventListener('click',()=>showPage('samples'));
 $('sampleSearch').addEventListener('input',e=>{search=e.target.value||'';render();});
 $('sampleFamily').addEventListener('change',e=>{family=e.target.value;render();});
 $('sampleClear').addEventListener('click',()=>{
  search='';family='Tümü';$('sampleSearch').value='';$('sampleFamily').value='Tümü';render();
 });
 $('sampleBody').addEventListener('change',onCellChange);
 $('sampleExport').addEventListener('click',exportCsv);
 $('sampleBackup').addEventListener('click',downloadBackup);
 $('sampleImport').addEventListener('click',()=>$('sampleImportFile').click());
 $('sampleImportFile').addEventListener('change',uploadBackup);
 ready=true;render();
 showPage(location.hash==='#numune'||location.hash==='#sont-makine'?'samples':'production');
}
function showPage(name){
 const sample=name==='samples';
 $('productionView').hidden=sample;$('sampleView').hidden=!sample;
 $('tabProduction').classList.toggle('is-active',!sample);
 $('tabSamples').classList.toggle('is-active',sample);
 $('tabProduction').setAttribute('aria-selected',String(!sample));
 $('tabSamples').setAttribute('aria-selected',String(sample));
 document.title=(sample?'Numune ve Teknik Kapsam':'Üretim Planlama')+' | Şönt ve Harmonik';
 if(sample)render();
}
window.SampleCoverageMatrix={init,render,group,status:priority,columns:HEADERS.length,headers:HEADERS.map(x=>x[0])};
})();