/* Numune ve Teknik Kapsam — Şönt ve Harmonik sarım/emprenye teknik veri girişi.
   Onaylanan düzen: 1 Ürün(5) → 4 Mevcut teknik(10) → 2 Sarım(9) → 3 Emprenye(4).
   İki ailenin teknik girişleri birbirinden ayrı tarayıcı kayıtlarında tutulur;
   Şöntün eski v1 kayıtları ve ürünlerin kaynak/üretim planı verileri korunur.
   Fiziksel ölçüm olmadan varsayımsal makine bilgisi doldurulmaz. */
(()=>{'use strict';
const $=id=>document.getElementById(id);
const esc=v=>String(v==null?'':v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const qty=n=>Number(n||0).toLocaleString('tr-TR');
const pct=(v,n)=>n?(100*v/n).toLocaleString('tr-TR',{minimumFractionDigits:2,maximumFractionDigits:2})+'%':'—';
const val=v=>v===null||v===undefined||v===''||/^(?:unresolved|unknown|bilinmiyor|belirsiz)$/i.test(String(v))?'—':typeof v==='number'?v.toLocaleString('tr-TR'):String(v);
const raw=(p,k)=>p.tamKayit&&Object.prototype.hasOwnProperty.call(p.tamKayit,k)?p.tamKayit[k]:null;
const byFamily=(p,shunt,harmonic)=>raw(p,p.grup==='Şönt'?shunt:harmonic);
const VERSION=1;
const SHUNT_STORAGE='simulation3.shunt.machine-inputs.v1';
const HARMONIC_STORAGE='simulation3.harmonic.machine-inputs.v1';
const SHUNT_FORMAT='simulation3-shunt-machine-inputs';
const HARMONIC_FORMAT='simulation3-harmonic-machine-inputs';
const BACKUP_FORMAT='simulation3-reactor-machine-inputs';
const STORAGE_SPECS={
 'Şönt':{key:SHUNT_STORAGE,format:SHUNT_FORMAT},
 'Harmonik':{key:HARMONIC_STORAGE,format:HARMONIC_FORMAT}
};
const GROUPS={
 'Şönt':['SVC-R','SRM','SRT','Diğer Şönt'],
 'Harmonik':['HRM 5,67','HRM 7','HRM 14','HRT 5,67','HRT 7/8','HRT 7/7','HRT 14','HRT-G varyant','HRT-GG varyant','Özel Harmonik']
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
const INPUTS=['coilCount','conductor','conductorOther','conductorSize','coilDimensions','coilWeightKg','turns','windingMinutes','core','coreOther','insulations','insulationOther','impPart','resinMode','resinCode','impMethod','impMethodOther','impCycle','reviewStatus'];
const NUMERIC=new Set(['coilCount','coilWeightKg','turns','windingMinutes','impCycle']);
const INTEGER=new Set(['coilCount','turns']);
const TEXT_LIMITS={conductorOther:90,conductorSize:90,coilDimensions:140,coreOther:90,insulationOther:90,resinCode:90,impMethodOther:90};
const HEADERS=[
 ['Ürün kodu','code'],['Model / açıklama','model'],['Yıllık üretim adedi','count'],
 ['Ailedeki payı (%)','percent'],['İnceleme önceliği','sample'],
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
let products=[],search='',family='Tümü',ready=false,entries={},storageEnabled=true,duplicateHarmonicCodes=new Set();
// Aynı stok kodundaki özel/ayrı sipariş satırları fiziksel olarak farklı olabilir.
// Tekil ürünlerde eski kod bazlı kayıt uyumluluğu korunur; yinelenenlerde id kullanılır.
function recordKey(p){
 return p.grup==='Harmonik'&&duplicateHarmonicCodes.has(p.kod)?String(p.id):p.kod;
}
function legacyAmbiguous(){
 return [...duplicateHarmonicCodes].filter(code=>Object.prototype.hasOwnProperty.call(entries,code));
}
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
 if(/^GA531\d/.test(code))return 'HRM 5,67';
 if(/^GA541\d/.test(code))return 'HRM 7';
 if(/^GA551\d/.test(code))return 'HRM 14';
 if(model.startsWith('HRM')){
  if(/\/5[.,]67/.test(model))return 'HRM 5,67';
  if(/\/14/.test(model))return 'HRM 14';
  return 'HRM 7';
 }
 if(/^GA53[23]\d/.test(code))return 'HRT 5,67';
 if(/^GA56[23]\d/.test(code))return 'HRT 7/7';
 if(/^GA54[23]\d/.test(code))return 'HRT 7/8';
 if(/^GA55[23]\d/.test(code))return 'HRT 14';
 if(kind.includes('5,67')||/\/5[.,]67/.test(model))return 'HRT 5,67';
 if(kind.includes('14')||/\/14/.test(model))return 'HRT 14';
 if(kind.includes('<%7')||/\/7-7/.test(model))return 'HRT 7/7';
 return 'HRT 7/8';
}
const HARMONIC_ADDITIONAL_SAMPLES={
 'GA5313':'HRM %5,67 sınıfını fiziksel olarak temsil etmek; GA5412 ile bobin/sarım yapısı aynı kabul edilmez.',
 'GA5514':'HRM %14 sınıfını incelemek; farklı p oranında bobin ve iletken ölçümü.',
 'GA5339':'HRT 100 kVAr, 44 kg, 355×310×190 mm; ağır ve büyük gövde sınırı.',
 'GA5639':'HRT 100 kVAr, 44 kg, THDv<%7; farklı p/THDv sınıfında büyük gövde.',
 'GA5438':'HRT 75 kVAr, 40 kg, 295×255×205 mm; derinlik ve dış ölçü sınırı.'
};
function basePriority(p){
 if(p.grup==='Şönt'){
  const m=window.ShuntMachineInvestment?.get(p.kod);
  if(!m)throw Error('Şönt inceleme kaydı bulunamadı: '+p.kod);
  const labels={A:'Ana Numune',B:'Karşılaştırma Numunesi',C:'Dış Kontrol'};
  return {label:labels[m.priority],rank:'ABC'.indexOf(m.priority),className:'shunt-'+m.priority,
   hint:m.reason+' · Ölçüm: '+m.focus+' · Henüz kapasite onayı yok.'};
 }
 const code=String(p.kod||'').toUpperCase();
 const status=String(raw(p,'Numune / kontrol')||'');
 const first=['GA5436','GA5426','GA5412'],compare=['GA5636','GA5536','GA5429','GA5336','GA5415'];
 // Her iki ailenin görüntülenen etiketleri aynı: öncelikli, hedefli, sökmeden.
 // Harmonik 3 ilk numune öncelikli; diğer 5 eski + 5 yeni fiziksel numune hedefli.
 if(status.startsWith('1 ·')||first.includes(code))
  return {label:'Ana Numune',rank:0,className:'main',hint:'Fiziksel numune. Kaynak ilk numune; tüm ürünlerin temsili henüz kanıtlanmadı.'};
 if(status.startsWith('2 ·')||compare.includes(code))
  return {label:'Karşılaştırma Numunesi',rank:1,className:'compare',hint:'Fiziksel numune. Kaynak kıyas adayı; bobin ve proses ortaklığı henüz kanıtlanmadı.'};
 if(Object.prototype.hasOwnProperty.call(HARMONIC_ADDITIONAL_SAMPLES,code))
  return {label:'Karşılaştırma Numunesi',rank:1,className:'compare',hint:'Fiziksel numune. '+HARMONIC_ADDITIONAL_SAMPLES[code]+' Sargı/proses ölçümleri doğrulanacak.'};
 if(status.startsWith('3 ·'))
  return {label:'Dış Kontrol',rank:2,className:'external',hint:'Katalog/görsel ve dış ölçü kontrolü; ürün sökülmez.'};
 if(status.includes('Kimlik')||/^(GAG|GAGG)/.test(code)||code==='GA5ÖZELHARM')return {label:'Teknik Bilgi Eksik',rank:3,className:'unknown',fixed:true,hint:'Ürüne özgü teknik çizim ve imalat reçetesi gerekli'};
 const m=code.match(/^GA(\d{4})$/),n=m?Number(m[1]):0;
 const ranges=[[5311,5317],[5411,5417],[5511,5517],[5321,5339],[5629,5639],[5521,5539],[5421,5439]];
 return ranges.some(([lo,hi])=>n>=lo&&n<=hi)?
  {label:'Dış Kontrol',rank:2,className:'external',hint:'Ürün açılmadan dış ölçü, ağırlık, bağlantı ve katalog kontrolü'}:
  {label:'Teknik Bilgi Eksik',rank:3,className:'unknown',fixed:true,hint:'Önce ürün kimliği ve üretim reçetesi doğrulanmalı'};
}
const REVIEW_STATUSES={main:{label:'Ana Numune',rank:0,className:'main'},
 compare:{label:'Karşılaştırma Numunesi',rank:1,className:'compare'},
 external:{label:'Dış Kontrol',rank:2,className:'external'}};
function priority(p){
 const base=basePriority(p);
 if(base.fixed)return base; // Teknik bilgi eksik ürünleri serbestçe sınıflandırma.
 const selection=entries[recordKey(p)]?.reviewStatus;
 return selection&&REVIEW_STATUSES[selection]?{
  ...base,...REVIEW_STATUSES[selection],hint:base.hint+' · İnceleme sınıfı kullanıcı tarafından değiştirildi.'
 }:base;
}
function specialHarmonic(p){
 return p.grup==='Harmonik'&&(/^(?:GAG|GAGG)/.test(p.kod)||p.kod==='GA5ÖZELHARM');
}
function technicalDisplay(p,field){
 const source=raw(p,field);
 if(p.grup!=='Harmonik')return val(source);
 if(specialHarmonic(p)){
  if(source===null||source===undefined||source==='')return 'Doğrulanmadı';
  return val(source)+' (sipariş kaydı; teyitsiz)';
 }
 if(field==='THDv tasarım sınıfı'&&(group(p)==='HRT 7/7'||group(p)==='HRT 7/8')){
  return group(p)==='HRT 7/7'?'<%7':'<%8';
 }
 return val(source);
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
 if(field==='reviewStatus')return ['main','compare','external'].includes(v)?v:null;
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
 if(!['other','mixed'].includes(result.conductor))delete result.conductorOther;
 if(result.core!=='other')delete result.coreOther;
 if(result.impMethod!=='other')delete result.impMethodOther;
 if(!(result.insulations||[]).includes('Diğer'))delete result.insulationOther;
 if(result.impPart==='none'){result.impMethod='none';delete result.impMethodOther;}
 return result;
}
function productFamily(key){
 const p=products.find(p=>recordKey(p)===key);
 return p&&(p.grup==='Şönt'||p.grup==='Harmonik')?p.grup:null;
}
function familyRecords(grup){
 const keys=new Set(products.filter(p=>p.grup===grup).map(recordKey));
 // Belirsiz eski birleşik kayıtlar aynen korunur, herhangi satıra aktarılmaz.
 if(grup==='Harmonik')for(const code of duplicateHarmonicCodes)keys.add(code);
 return Object.fromEntries(Object.entries(entries).filter(([key])=>keys.has(key)));
}
function saveToStorage(grup){
 const spec=STORAGE_SPECS[grup];
 if(!spec)throw Error('Geçersiz ürün ailesi: '+grup);
 localStorage.setItem(spec.key,JSON.stringify({format:spec.format,version:VERSION,records:familyRecords(grup)}));
}
function saveRecord(code,field,value){
 const grup=productFamily(code);
 if(!grup)return;
 const rec={...(entries[code]||{})};
 if(value===''||(Array.isArray(value)&&!value.length))delete rec[field];else rec[field]=value;
 const next=cleanRecord(rec);
 if(Object.keys(next).length)entries[code]=next;else delete entries[code];
 try{
  saveToStorage(grup);
  storageEnabled=true;notice(grup+' teknik girişleri bu tarayıcıya kaydedildi. Başka cihaz için JSON yedeği al.');
 }catch(e){storageEnabled=false;notice(grup+' teknik girişleri tarayıcıya kaydedilemedi. JSON yedeği indir.','error');}
}
function cleanAll(records,grup){
 if(!records||typeof records!=='object'||Array.isArray(records))throw Error('Kayıt içeriği geçersiz');
 const result={},known=new Set(products.filter(p=>p.grup===grup).map(recordKey));
 if(grup==='Harmonik')for(const code of duplicateHarmonicCodes)known.add(code);
 for(const [code,record] of Object.entries(records)){
  if(!known.has(code))throw Error('Bilinmeyen '+grup+' ürün kodu: '+code);
  const item=cleanRecord(record);
  if(Object.keys(item).length)result[code]=item;
 }
 return result;
}
function loadSaved(){
 const failures=[];
 for(const grup of ['Şönt','Harmonik']){
  const spec=STORAGE_SPECS[grup];
  try{
   const data=localStorage.getItem(spec.key);
   if(!data)continue;
   const parsed=JSON.parse(data);
   if(parsed?.format!==spec.format||parsed.version!==VERSION)throw Error('Geçersiz teknik kayıt sürümü');
   Object.assign(entries,cleanAll(parsed.records,grup));
  }catch(e){failures.push(grup);}
 }
 if(failures.length){storageEnabled=false;notice(failures.join(', ')+' teknik kaydı okunamadı. JSON yedeğinizi kontrol edin.','error');}
 else if(legacyAmbiguous().length)notice('Uyarı: '+legacyAmbiguous().length+' yinelenen Harmonik stok koduna ait eski ortak giriş satıra eşleştirilemiyor. JSON yedeğini koruyun; yeni girişler satır bazında ayrılır.','error');
}
function notice(message,kind='ok'){
 const el=$('sampleEditNotice');
 if(el){el.textContent=message;el.className='sample-edit-notice'+(kind==='error'?' error':'');}
}
function get(p,key){return entries[recordKey(p)]?.[key]??'';}
function optionList(list,value){return list.map(([k,l])=>'<option value="'+esc(k)+'"'+(String(value)===k?' selected':'')+'>'+esc(l)+'</option>').join('');}
function select(p,key,options){
 const label={conductor:'İletken türü ve malzemesi',core:'Nüve tipi',impPart:'Emprenye edilen parça',impMethod:'Emprenye yöntemi'}[key]||key;
 const value=get(p,key),otherField={conductor:'conductorOther',core:'coreOther',impMethod:'impMethodOther'}[key];
 const otherActive=otherField&&(value==='other'||(key==='conductor'&&value==='mixed'));
 return '<div class="sample-edit-stack"><select class="sample-edit" data-code="'+esc(recordKey(p))+'" data-field="'+key+'" aria-label="'+esc(p.kod+' · '+label)+'">'+optionList(options,value)+'</select>'+
 (otherActive?textInput(p,otherField,'Diğer / karma açıklaması'):'')+'</div>';
}
function numberInput(p,key,placeholder,integer=false){
 const v=get(p,key);
 return '<input class="sample-edit sample-edit-number" type="number" min="'+(integer?'1':'0.001')+'" step="'+(integer?'1':'any')+'" inputmode="decimal" placeholder="'+esc(placeholder)+'" data-code="'+esc(recordKey(p))+'" data-field="'+key+'" value="'+esc(v)+'" aria-label="'+esc(p.kod+' '+key)+'">';
}
function textInput(p,key,placeholder){
 const v=get(p,key),max=TEXT_LIMITS[key]||100;
 return '<input class="sample-edit sample-edit-text" type="text" maxlength="'+max+'" placeholder="'+esc(placeholder)+'" data-code="'+esc(recordKey(p))+'" data-field="'+key+'" value="'+esc(v)+'" aria-label="'+esc(p.kod+' '+key)+'">';
}
function resinCell(p){
 const mode=get(p,'resinMode'),code=get(p,'resinCode');
 const datalist=p.grup==='Şönt'?'sampleResinCodeListShunt':'sampleResinCodeListHarmonic';
 return '<div class="sample-resin-editor"><select class="sample-edit" data-code="'+esc(recordKey(p))+'" data-field="resinMode" aria-label="Vernik veya reçine seçimi">'+
 optionList([['','Belirlenmedi'],['code','Malzeme kodu gir / seç'],['none','Kullanılmıyor']],mode)+'</select>'+
 (mode==='code'?'<input class="sample-edit sample-edit-text" type="text" list="'+datalist+'" maxlength="90" placeholder="Üretici malzeme kodu" data-code="'+esc(recordKey(p))+'" data-field="resinCode" value="'+esc(code)+'" aria-label="Üretici vernik reçine kodu">':'')+'</div>';
}
function resinCodes(grup){
 return [...new Set(Object.entries(familyRecords(grup)).map(([,x])=>x).filter(x=>x.resinMode==='code'&&x.resinCode).map(x=>x.resinCode))].sort((a,b)=>a.localeCompare(b,'tr'));
}
function insulationCell(p){
 const values=get(p,'insulations')||[],summary=values.length?values.join(', '):'Belirlenmedi';
 return '<div class="sample-edit-stack"><details class="sample-multi"><summary>'+esc(summary)+'</summary><div class="sample-multi-content">'+INSULATIONS.map(item=>
 '<label><input type="checkbox" data-code="'+esc(recordKey(p))+'" data-field="insulations" value="'+esc(item)+'"'+(values.includes(item)?' checked':'')+'> '+esc(item)+'</label>').join('')+'</div></details>'+
 (values.includes('Diğer')?textInput(p,'insulationOther','Diğer izolasyon açıklaması'):'')+'</div>';
}
function technicalCell(p,key){
 const v=get(p,key);
 if(v===''||v===undefined||v===null||Array.isArray(v)&&!v.length)return '<span class="sample-original">—</span>';
 const list={conductor:CONDUCTOR,core:CORES,impPart:PARTS,impMethod:METHODS}[key];
 let value;
 if(key==='insulations')value=v.map(x=>x==='Diğer'&&get(p,'insulationOther')?'Diğer: '+get(p,'insulationOther'):x).join(', ');
 else if(key==='resinMode')value=v==='none'?'Kullanılmıyor':v==='code'?(get(p,'resinCode')||'Malzeme kodu bekliyor'):'Belirlenmedi';
 else if(list){
  value=list.find(([x])=>x===v)?.[1]||v;
  const extra={conductor:'conductorOther',core:'coreOther',impMethod:'impMethodOther'}[key];
  if(extra&&get(p,extra))value+=' · '+get(p,extra);
 }else value=String(v);
 return '<span class="sample-original">'+esc(value)+'</span>';
}
function editable(p,key){
 if(p.grup!=='Şönt'&&p.grup!=='Harmonik')return '—';
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
  raw(p,'L (mH)')??p.L,
  p.grup==='Harmonik'?technicalDisplay(p,'p (%)'):raw(p,'p (%)')??p.p,
  p.grup==='Harmonik'?technicalDisplay(p,'THDv tasarım sınıfı'):raw(p,'THDv tasarım sınıfı')??p.thdv,
  DATASHEETS[p.grup],
  ...['coilCount','conductor','conductorSize','coilDimensions','coilWeightKg','turns','windingMinutes','core','insulations','impPart','resinMode','impMethod','impCycle'].map(k=>get(p,k))
 ];
}
function rowCells(p,totals){
 const priorityData=priority(p);
 const fields=[
  '<div class="sample-row-identity"><a class="sample-product-link" href="urun.html?id='+encodeURIComponent(p.id)+'" target="_blank" rel="noopener">'+esc(p.kod)+'</a>'+
  '<button type="button" class="sample-row-edit" data-edit-id="'+esc(p.id)+'">Düzenle</button></div>',
  esc(p.model),
  '<strong class="sample-amount">'+qty(p.annual)+'</strong>',
  pct(p.annual,totals[p.grup]),
  '<span class="sample-status '+esc(priorityData.className)+'" title="'+esc(priorityData.hint)+'">'+esc(priorityData.label)+'</span>',
  esc(val(byFamily(p,'Ölçü G×Y×D (mm)','Dış ölçüler (mm)'))),
  esc(val(typeof p.kg==='number'&&p.kg>0?p.kg:null)),
  esc(val(byFamily(p,'Bağlantı tipi','Bağlantı'))),
  esc(val(raw(p,'Faz')??p.faz)),esc(val(raw(p,'Güç (kVAr)')??p.guc)),
  esc(val(byFamily(p,'Akım (A)','Akım (Irms, A)')??p.akim)),
  esc(val(raw(p,'L (mH)')??p.L)),
  esc(p.grup==='Harmonik'?technicalDisplay(p,'p (%)'):val(raw(p,'p (%)')??p.p)),
  esc(p.grup==='Harmonik'?technicalDisplay(p,'THDv tasarım sınıfı'):val(raw(p,'THDv tasarım sınıfı')??p.thdv)),
  '<a href="'+esc(DATASHEETS[p.grup])+'" target="_blank" rel="noopener">PDF</a>',
  ...['coilCount','conductor','conductorSize','coilDimensions','coilWeightKg','turns','windingMinutes','core','insulations','impPart','resinMode','impMethod','impCycle'].map(k=>technicalCell(p,k))
 ];
 if(fields.length!==HEADERS.length)throw Error('28 teknik sütun eşleşmedi: '+p.kod+' '+fields.length);
 return '<tr class="sample-product-row">'+fields.map((x,i)=>'<td class="sample-cell-'+HEADERS[i][1]+'">'+x+'</td>').join('')+'</tr>';
}
function searchVisible(p){
 const info=p.grup==='Şönt'?window.ShuntMachineInvestment?.get(p.kod):null;
 const hay=p.kod+' '+p.model+' '+group(p)+' '+(info?.reason||'')+' '+Object.values(entries[recordKey(p)]||{}).join(' ')+' '+val(raw(p,'Numune / kontrol'));
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
 for(const grup of ['Şönt','Harmonik']){
  const dl=$(grup==='Şönt'?'sampleResinCodeListShunt':'sampleResinCodeListHarmonic');
  if(dl)dl.innerHTML=resinCodes(grup).map(code=>'<option value="'+esc(code)+'"></option>').join('');
 }
 const guide=$('shuntProcurementGuide');if(guide)guide.hidden=family==='Harmonik';
 const ambiguous=legacyAmbiguous().length;
 if(ambiguous)notice(ambiguous+' yinelenen Harmonik kodunun eski ortak teknik girdisi satıra güvenle bağlanamadı; JSON yedeğini koruyun. Yeni girişler ayrıdır.','error');
 const shunt=products.filter(p=>p.grup==='Şönt');
 const harmonic=products.filter(p=>p.grup==='Harmonik');
 if(shunt.length!==25||harmonic.length!==108||totals['Şönt']!==35772||totals['Harmonik']!==9316)
  throw Error('Kaynak ürün miktarları ve adetleri tutarsız');
 const classifications=[{grup:'Şönt',arr:shunt},{grup:'Harmonik',arr:harmonic}].map(x=>{
  const counts={main:0,compare:0,external:0,missing:0,annual:0};
  for(const p of x.arr){
   const status=priority(p);
   if(status.label==='Ana Numune'){counts.main++;counts.annual+=p.annual;}
   else if(status.label==='Karşılaştırma Numunesi'){counts.compare++;counts.annual+=p.annual;}
   else if(status.label==='Dış Kontrol')counts.external++;
   else if(status.label==='Teknik Bilgi Eksik')counts.missing++;
   else throw Error('Bilinmeyen inceleme sınıfı '+status.label);
  }
  if(counts.main+counts.compare+counts.external+counts.missing!==x.arr.length)throw Error('Sınıflandırma eksik');
  return {...counts,grup:x.grup,total:x.arr.length};
 });
 const sc=classifications[0],hc=classifications[1];
 const chosen=products.filter(searchVisible);
 $('sampleMetrics').innerHTML='<span><b>Yıllık toplam</b> '+qty(annual)+' adet</span><span><b>Şönt</b> '+qty(totals['Şönt'])+' adet</span>'+
 '<span><b>Harmonik</b> '+qty(totals['Harmonik'])+' adet</span>'+
 '<span><b>Şönt numunesi</b> '+(sc.main+sc.compare)+'</span>'+
 '<span><b>Harmonik numunesi</b> '+(hc.main+hc.compare)+'</span>'+
 '<span><b>Toplam numune</b> '+(sc.main+sc.compare+hc.main+hc.compare)+'</span>'+
 '<span class="sample-count">'+chosen.length+' / '+products.length+' ürün</span>';
 const shuntNote='<b>Şönt:</b> '+sc.main+' Ana Numune, '+sc.compare+' Karşılaştırma Numunesi, '+sc.external+' Dış Kontrol.';
 const harmonicNote='<b>Harmonik:</b> '+hc.main+' Ana Numune, '+hc.compare+' Karşılaştırma Numunesi, '+hc.external+' Dış Kontrol, '+hc.missing+' Teknik Bilgi Eksik. '+qty(hc.annual)+' adet/yıl seçili numunelerin doğrudan üretim miktarı.';
 const note=family==='Şönt'?shuntNote:family==='Harmonik'?harmonicNote:shuntNote+' '+harmonicNote;
 $('shuntSampleReview').innerHTML=note+' <b>İnceleme türünü ve teknik bilgileri değiştirmek için Ürün Seç / Düzenle ekranını kullanın.</b>';

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
   if(p.grup==='Şönt'||p.grup==='Harmonik'){
    const index={conductor:16,core:22,insulations:23,impPart:24,impMethod:26};
    for(const [key,i]of Object.entries(index)){
     const opts={conductor:CONDUCTOR,core:CORES,impPart:PARTS,impMethod:METHODS};
     if(key==='insulations'){
      const selected=get(p,key)||[];
      fields[i]=selected.map(x=>x==='Diğer'&&get(p,'insulationOther')?'Diğer: '+get(p,'insulationOther'):x).join(', ');
     }else{
      const label=opts[key].find(x=>x[0]===get(p,key))?.[1]||'Belirlenmedi';
      const extra={conductor:'conductorOther',core:'coreOther',impMethod:'impMethodOther'}[key];
      fields[i]=label+(extra&&get(p,extra)?' · '+get(p,extra):'');
     }
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
 const records={'Şönt':familyRecords('Şönt'),'Harmonik':familyRecords('Harmonik')};
 download('sont-harmonik-makine-teknik-girisler.json',JSON.stringify({format:BACKUP_FORMAT,version:VERSION,exportedAt:new Date().toISOString(),records},null,2),'application/json;charset=utf-8');
}
async function uploadBackup(){
 const el=$('sampleImportFile'),file=el?.files?.[0];
 if(!file)return;
 try{
  if(file.size>1000000)throw Error('Yedek dosyası çok büyük');
  const json=JSON.parse(await file.text());
  if(json?.version!==VERSION)throw Error('Yedek sürümü uyuşmuyor');
  let groups=[];
  let imported={};
  if(json.format===BACKUP_FORMAT){
   if(!json.records||typeof json.records!=='object'||Array.isArray(json.records)||
      !Object.prototype.hasOwnProperty.call(json.records,'Şönt')||
      !Object.prototype.hasOwnProperty.call(json.records,'Harmonik'))throw Error('Yedekte aile kayıtları eksik');
   groups=['Şönt','Harmonik'];
   for(const grup of groups)imported[grup]=cleanAll(json.records[grup],grup);
  }else if(json.format===SHUNT_FORMAT||json.format===HARMONIC_FORMAT){
   // Daha önce indirilmiş Şönt v1 yedekleri geçerli kalır.
   const grup=json.format===SHUNT_FORMAT?'Şönt':'Harmonik';
   groups=[grup];imported[grup]=cleanAll(json.records,grup);
  }else throw Error('Yedek dosyasının türü tanınmadı');
  const previous=entries,next={...entries};
  for(const grup of groups){
   const known=new Set(products.filter(p=>p.grup===grup).map(recordKey));
   if(grup==='Harmonik')for(const code of duplicateHarmonicCodes)known.add(code);
   for(const code of Object.keys(next))if(known.has(code))delete next[code];
   Object.assign(next,imported[grup]);
  }
  const storedBefore=Object.fromEntries(groups.map(grup=>[grup,localStorage.getItem(STORAGE_SPECS[grup].key)]));
  entries=next;
  try{
   for(const grup of groups)saveToStorage(grup);
  }catch(e){
   entries=previous;
   for(const grup of groups){
    try{
     const old=storedBefore[grup],key=STORAGE_SPECS[grup].key;
     if(old===null)localStorage.removeItem(key);else localStorage.setItem(key,old);
    }catch(rollbackError){/* geri yükleme başarısızsa kullanıcı bilgilendirilir */}
   }
   throw Error('Tarayıcıya yazılamadı. Önce JSON yedeğinizi koruyun');
  }
  storageEnabled=true;
  render();notice('Teknik yedek yüklendi: '+groups.join(' + ')+'. Kayıtlar ayrı saklandı.');
 }catch(e){notice('Yedek yüklenemedi: '+e.message,'error');}
 finally{el.value='';}
}
/* Ayrı ürün düzenleme ekranı: seçim ve düzenleme süresince hiçbir kayıt otomatik değişmez. */
let editorProduct=null,editorDraft=null,editorDirty=false,pickerId='';
const EDIT_FIELDS=[
 ['coilCount','Bobin adedi / ürün','number','1'],
 ['conductor','İletken türü ve malzemesi','select',CONDUCTOR],
 ['conductorOther','Diğer / karma iletken açıklaması','text','Diğer iletken biçimi'],
 ['conductorSize','İletken kesiti (mm)','text','Ø çap veya en × kalınlık'],
 ['coilDimensions','Bobin ölçüleri (mm)','text','İç / dış / sarım eni'],
 ['coilWeightKg','Bobin ağırlığı (kg)','number','0.001'],
 ['turns','Tur sayısı','number','1'],
 ['windingMinutes','Sarım süresi (dk / bobin)','number','0.001'],
 ['core','Nüve tipi','select',CORES],
 ['coreOther','Diğer nüve açıklaması','text','Diğer nüve tipi'],
 ['insulations','İzolasyon tipi','multi',INSULATIONS],
 ['insulationOther','Diğer izolasyon açıklaması','text','Diğer izolasyon malzemesi'],
 ['impPart','Emprenye edilen parça','select',PARTS],
 ['resinMode','Vernik / reçine seçimi','select',[['','Belirlenmedi'],['code','Malzeme kodu gir / seç'],['none','Kullanılmıyor']]],
 ['resinCode','Vernik / reçine malzeme kodu','text','Üretici ürün kodu'],
 ['impMethod','Emprenye yöntemi','select',METHODS],
 ['impMethodOther','Diğer emprenye yöntemi açıklaması','text','Diğer yöntem'],
 ['impCycle','Emprenye çevrimi (dk / parti)','number','0.001']
];
function promptDiscard(){
 return !editorDirty||typeof window.confirm!=='function'||window.confirm('Bu üründe henüz kaydedilmemiş değişiklikler var. Değişiklikleri iptal edip çıkmak istiyor musunuz?');
}
function openPicker(){
 if(!promptDiscard())return;
 editorProduct=null;editorDraft=null;editorDirty=false;
 $('sampleEditor').hidden=false;
 $('samplePickerArea').hidden=false;$('sampleEditArea').hidden=true;
 $('sampleEditorTitle').textContent='Ürün seç';
 $('samplePickSearch').value='';$('samplePickFamily').value=family;
 pickerId='';renderPicker();
 if(typeof $('samplePickSearch').focus==='function')$('samplePickSearch').focus();
}
function renderPicker(){
 const q=String($('samplePickSearch').value||'').toLocaleLowerCase('tr-TR').trim();
 const fam=$('samplePickFamily').value;
 const matches=products.filter(p=>(fam==='Tümü'||p.grup===fam)&&
  (p.kod+' '+p.model+' '+group(p)+' '+p.annual+' '+recordKey(p)).toLocaleLowerCase('tr-TR').includes(q));
 const list=$('samplePickList');
 list.innerHTML=matches.map(p=>'<option value="'+esc(p.id)+'"'+(String(p.id)===pickerId?' selected':'')+'>'+
 esc(p.grup+' · '+p.kod+' · '+p.model+' · '+qty(p.annual)+' adet/yıl'+
 (duplicateHarmonicCodes.has(p.kod)?' · Satır '+p.id:''))+'</option>').join('');
 if(!matches.some(p=>String(p.id)===pickerId))pickerId='';
 list.value=pickerId;
 $('samplePickerConfirm').disabled=!pickerId;
 $('samplePickCount').textContent=matches.length+' ürün bulundu. Aynı kodlu ürünlerde model ve satır kimliğini kontrol edin.';
}
function selectPickerItem(id){
 pickerId=products.some(p=>String(p.id)===String(id))?String(id):'';
 $('samplePickerConfirm').disabled=!pickerId;
}
function editProductById(id){
 const p=products.find(x=>String(x.id)===String(id));
 if(!p){notice('Ürün satırı bulunamadı.','error');return;}
 if(!promptDiscard())return;
 editorProduct=p;editorDraft={...(entries[recordKey(p)]||{})};
 if(Array.isArray(editorDraft.insulations))editorDraft.insulations=[...editorDraft.insulations];
 editorDirty=false;
 $('sampleEditor').hidden=false;
 $('samplePickerArea').hidden=true;$('sampleEditArea').hidden=false;
 $('sampleEditorTitle').textContent='Ürün teknik bilgilerini düzenle';
 $('sampleEditorIdentity').innerHTML='<strong>'+esc(p.kod)+' · '+esc(p.model)+'</strong>'+
 '<span>'+esc(p.grup)+' / '+esc(group(p))+' · '+qty(p.annual)+' adet/yıl</span>'+
 '<span>Ürün kayıt kimliği: '+esc(p.id)+(duplicateHarmonicCodes.has(p.kod)?' · Bu stok kodu farklı ürünlerde tekrar kullanılıyor.':'')+'</span>';
 renderEditorForm();
}
function editField(field,caption,type,opts){
 const value=editorDraft[field]??'';
 const key=esc(field),label=esc(caption);
 if(type==='select')return '<label class="sample-editor-field">'+label+
  '<select data-field="'+key+'">'+optionList(opts,value)+'</select></label>';
 if(type==='multi'){
  const values=Array.isArray(value)?value:[];
  return '<fieldset class="sample-editor-field sample-editor-multi"><legend>'+label+'</legend>'+
  opts.map(item=>'<label><input type="checkbox" data-field="'+key+'" value="'+esc(item)+'"'+(values.includes(item)?' checked':'')+'> '+esc(item)+'</label>').join('')+'</fieldset>';
 }
 if(type==='number')return '<label class="sample-editor-field">'+label+
  '<input data-field="'+key+'" type="number" inputmode="decimal" min="'+opts+'" step="'+(opts==='1'?'1':'any')+
  '" value="'+esc(value)+'" placeholder="Ölçüm bekliyor"></label>';
 const datalist=field==='resinCode'?(editorProduct.grup==='Şönt'?'sampleResinCodeListShunt':'sampleResinCodeListHarmonic'):'';
 return '<label class="sample-editor-field">'+label+
 '<input data-field="'+key+'" type="text" maxlength="'+(TEXT_LIMITS[field]||90)+'"'+(datalist?' list="'+datalist+'"':'')+
 ' value="'+esc(value)+'" placeholder="'+esc(opts)+'"></label>';
}
function renderEditorForm(){
 if(!editorProduct||!editorDraft)return;
 const p=editorProduct,base=basePriority(p);
 const selectValue=editorDraft.reviewStatus||({ 'Ana Numune':'main','Karşılaştırma Numunesi':'compare','Dış Kontrol':'external'}[base.label]||'external');
 const statusHtml=base.fixed?
  '<div class="sample-editor-fixed"><b>İnceleme türü: Teknik Bilgi Eksik</b><p>Bu statü, ürünün kimliği ve reçetesi doğrulanmadan değiştirilemez. Teknik veriler yine de girilebilir.</p></div>':
  '<label class="sample-editor-field">İnceleme türü'+
  '<select data-field="reviewStatus">'+optionList([['main','Ana Numune'],['compare','Karşılaştırma Numunesi'],['external','Dış Kontrol']],selectValue)+'</select></label>';
 const visible=(f)=>{
  if(f==='conductorOther')return ['mixed','other'].includes(editorDraft.conductor);
  if(f==='coreOther')return editorDraft.core==='other';
  if(f==='insulationOther')return (editorDraft.insulations||[]).includes('Diğer');
  if(f==='impMethodOther')return editorDraft.impMethod==='other';
  if(f==='resinCode')return editorDraft.resinMode==='code';
  return true;
 };
 const fields=(names)=>EDIT_FIELDS.filter(([id])=>names.includes(id)&&visible(id)).map(a=>editField(...a)).join('');
 $('sampleEditorForm').innerHTML='<fieldset class="sample-editor-section"><legend>1 · İnceleme türü</legend>'+statusHtml+'</fieldset>'+
 '<fieldset class="sample-editor-section"><legend>2 · Sarım makinesi bilgileri</legend><div class="sample-editor-grid">'+
 fields(['coilCount','conductor','conductorOther','conductorSize','coilDimensions','coilWeightKg','turns','windingMinutes','core','coreOther','insulations','insulationOther'])+'</div></fieldset>'+
 '<fieldset class="sample-editor-section"><legend>3 · Emprenye bilgileri</legend><div class="sample-editor-grid">'+
 fields(['impPart','resinMode','resinCode','impMethod','impMethodOther','impCycle'])+'</div></fieldset>';
 $('sampleEditorMessage').textContent=editorDirty?'Kaydedilmemiş değişiklikler var.':'';
 $('sampleEditorSave').disabled=false;
}
function updateEditorDraft(e){
 if(!editorProduct||!editorDraft)return;
 const el=e.target,field=el?.dataset?.field;
 if(!field||!INPUTS.includes(field)||basePriority(editorProduct).fixed&&field==='reviewStatus')return;
 if(field==='insulations'){
  const list=Array.isArray(editorDraft.insulations)?editorDraft.insulations:[];
  editorDraft.insulations=el.checked?[...new Set([...list,el.value])]:list.filter(x=>x!==el.value);
 }else editorDraft[field]=el.value;
 editorDirty=true;
 const rerender=['conductor','core','impMethod','resinMode','insulations'].includes(field);
 if(rerender)renderEditorForm();
 else $('sampleEditorMessage').textContent='Kaydedilmemiş değişiklikler var.';
}
function saveEditor(){
 const p=editorProduct;
 if(!p||!editorDraft){notice('Önce ürün seçin.','error');return;}
 const key=recordKey(p),current=products.find(x=>String(x.id)===String(p.id));
 if(!current||recordKey(current)!==key){$('sampleEditorMessage').textContent='Ürün kimliği uyuşmadı. Kayıt yapılmadı.';return;}
 if(basePriority(p).fixed)delete editorDraft.reviewStatus;
 // Geçersiz sayısal giriş sessizce silinemez: kayıt öncesi doğrulanır.
 for(const [field,value]of Object.entries(editorDraft)){
  if(!INPUTS.includes(field))continue;
  if(value===''||value===null||value===undefined)continue;
  const valid=validInput(field,value);
  if(valid===null){
   $('sampleEditorMessage').textContent='Geçersiz değer: '+(EDIT_FIELDS.find(x=>x[0]===field)?.[1]||field)+'. Kayıt yapılmadı.';
   return;
  }
 }
 const next=cleanRecord(editorDraft),previous=entries[key];
 if(Object.keys(next).length)entries[key]=next;else delete entries[key];
 try{saveToStorage(p.grup);}
 catch(error){
  if(previous)entries[key]=previous;else delete entries[key];
  $('sampleEditorMessage').textContent='Kaydedilemedi: tarayıcı depolama hatası. Değişiklikler taslakta duruyor.';
  return;
 }
 editorDirty=false;
 editorDraft={...next};
 if(Array.isArray(next.insulations))editorDraft.insulations=[...next.insulations];
 render();
 renderEditorForm();
 $('sampleEditorMessage').textContent='Kaydedildi: '+p.kod+' / '+p.model+' · Yalnız bu ürün güncellendi.';
 notice(p.kod+' · '+p.model+' teknik bilgileri kaydedildi.','ok');
}
function closeEditor(){
 if(!promptDiscard())return;
 $('sampleEditor').hidden=true;
 editorProduct=null;editorDraft=null;editorDirty=false;
}
function editorBack(){
 if(!promptDiscard())return;
 editorProduct=null;editorDraft=null;editorDirty=false;
 $('sampleEditArea').hidden=true;$('samplePickerArea').hidden=false;
 $('sampleEditorTitle').textContent='Ürün seç';
 renderPicker();
}
function editorCancel(){
 if(!editorProduct)return;
 editorDraft={...(entries[recordKey(editorProduct)]||{})};
 if(Array.isArray(editorDraft.insulations))editorDraft.insulations=[...editorDraft.insulations];
 editorDirty=false;renderEditorForm();
 $('sampleEditorMessage').textContent='Kaydedilmeyen değişiklikler iptal edildi.';
}

function init(list){
 if(!Array.isArray(list)||!list.length)throw Error('Numune sayfası ürün listesi eksik');
 products=list;
 if(products.some(p=>!p.id||!p.kod||!p.grup||!Number.isFinite(p.annual)||p.annual<=0))throw Error('Numune sayfası ürün kaydı geçersiz');
 const counts=new Map();
 for(const p of products.filter(p=>p.grup==='Harmonik'))counts.set(p.kod,(counts.get(p.kod)||0)+1);
 duplicateHarmonicCodes=new Set([...counts].filter(([,n])=>n>1).map(([code])=>code));
 if(new Set(products.map(p=>p.grup+'|'+recordKey(p))).size!==products.length)throw Error('Teknik kayıt anahtarı çakışması');
 loadSaved();
 $('tabProduction').addEventListener('click',()=>showPage('production'));
 $('tabSamples').addEventListener('click',()=>showPage('samples'));
 $('sampleSearch').addEventListener('input',e=>{search=e.target.value||'';render();});
 $('sampleFamily').addEventListener('change',e=>{family=e.target.value;render();});
 $('sampleClear').addEventListener('click',()=>{
  search='';family='Tümü';$('sampleSearch').value='';$('sampleFamily').value='Tümü';render();
 });
 $('sampleBody').addEventListener('click',e=>{
  const button=e.target?.closest?.('[data-edit-id]');
  const id=button?.dataset?.editId||e.target?.dataset?.editId;
  if(id)editProductById(id);
 });
 $('sampleOpenPicker').addEventListener('click',openPicker);
 $('samplePickSearch').addEventListener('input',renderPicker);
 $('samplePickFamily').addEventListener('change',renderPicker);
 $('samplePickList').addEventListener('change',e=>selectPickerItem(e.target.value));
 $('samplePickList').addEventListener('dblclick',()=>{if(pickerId)editProductById(pickerId)});
 $('samplePickerConfirm').addEventListener('click',()=>{if(pickerId)editProductById(pickerId)});
 $('sampleEditorClose').addEventListener('click',closeEditor);
 $('sampleEditorBack').addEventListener('click',editorBack);
 $('sampleEditorCancel').addEventListener('click',editorCancel);
 $('sampleEditorSave').addEventListener('click',saveEditor);
 $('sampleEditorForm').addEventListener('submit',e=>e.preventDefault());
 $('sampleEditorForm').addEventListener('input',e=>{
  if(e.target?.type==='text'||e.target?.type==='number')updateEditorDraft(e);
 });
 $('sampleEditorForm').addEventListener('change',e=>{
  if(e.target?.type!=='text'&&e.target?.type!=='number')updateEditorDraft(e);
 });
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