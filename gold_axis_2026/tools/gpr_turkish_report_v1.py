"""Human-readable Turkish method/result dossier generated only after final audit."""
import json
from pathlib import Path
from gpr_stage2_v1 import load

def run(root):
 final=json.loads((root/'GOLD_MONTHLY_GPR_FINAL_FREEZE_2026-09-26.json').read_text())
 verification=json.loads((root/'GOLD_MONTHLY_GPR_FINAL_VERIFICATION_2026-09-26.json').read_text());assert final['status']=='COMPLETE' and verification['status']=='PASS'
 models=load(root);ens=json.loads((root/'GOLD_MONTHLY_GPR_STAGE4_RESULT_2026-09-26.json').read_text())
 candidates={**models,**{pool+'_'+n:d for pool,z in ens['pools'].items() for n,d in z['variants'].items()}}
 primary=final['primary'];d=candidates[primary];m=d['dev']['metrics']
 lines=['# GPR: yöntem, deneyler ve sonuç dosyası','',
 f"**Aşamalar 0–5 tamamlandı.** Dört çıktılı GPR ailesinin seçilen modeli **{primary}**. DEV toplam mutlak hata **{m['sum_abs_error']:.4f}**, doğru yön **{m['direction_correct']}/33**. Model seçimi yalnızca 2022-04–2024-12 DEV dönemine dayanır. 2025 ve 2026 sonuçları seçim amacıyla kullanılmadı.",'',
 '## Araştırmaya dayalı yöntem','',
 'Amaç, önceki tamamlanmış ayın sonunda sonraki takvim ayının ortalama XAU/USD fiyatını tahmin etmektir. Önceki ailelerle aynı sekiz VW-MIDAS girdisi ve aynı gerçekleşen değerler kullanıldı. Her metal için iki girdi vardır: son tamamlanmış ayın log getirisi ve o ayın günlük log getirilerinin ağırlıklı ortalaması. Ağırlıklar, gecikmeli ve tahmin tarihinde yayımlanmış jeopolitik risk endeksiyle belirlenir. Buradaki jeopolitik risk endeksi ile GPR modelinin Gaussian Process Regression adı ayrı kavramlardır. Ana GPR modelleri dört metalin logaritmik getirilerini birlikte öğrenir. SO_RBF yalnızca altın öğrenen yardımcı karşılaştırmadır; ortak öğrenen ana modele dönüştürülmedi.','',
 'Temel ortak kovaryans **B ⊗ K + D ⊗ I** biçimindedir. B=LLᵀ ile dört çıktı arasındaki ilişki pozitif yarı tanımlı tutulur; D her çıktının ayrı gözlem gürültüsünü içerir. Girdi çekirdeği birim genliklidir, böylece B ile tekrar eden bir genlik parametresi bulunmaz. Ana modelde ARD-RBF, alternatif başlangıç modelinde Matérn-3/2 kullanıldı. Gürültü beyazlatmasıyla yapılan çözüm, tam ortak kovaryans hesabına cebirsel olarak eşdeğerdir; seyrek GP yaklaşımı değildir.','',
 'Ana modelin 22 parametresi: sekiz uzunluk ölçeği, Cholesky matrisinin dört pozitif köşegen ve altı serbest alt üçgen elemanı, dört gürültü standart sapması. Doğal ölçekte sınırlar sırasıyla [0.05,20], [0.1,3], [-2,2], [0.01,2]; sayısal jitter 1e-8. Sınırlar proje tercihleridir, kaynakların zorunlu sabitleri değildir.','',
 'Eğitim amacı ortak negatif log marjinal olabilirliktir. Düzenlenmiş sürümlerde dönüştürülmüş parametreler üzerinde önceden sabitlenmiş Gaussian önsel cezası eklendi. Doğrulama kaybı standartlaştırılmış ölçekte %70 altın MAE ve %30 dört çıktı MAE bileşimidir. Stage1 ve koşullu hibritte her neslin eğitim kaybına göre en iyi çeyreğinden geçmiş doğrulamayla aday tutulur; optimizerın evrimini eğitim kaybı yönlendirir. Stage3A ise her son eğitim kazananını doğrular ve üç tekrar arasından seçer; iç q araması ayrıca geçmiş doğrulama kullanır. Doğrulama değerlendirme sayıları yöntemler arasında eşit değildir. Fiyat tahmini önceki gerçek fiyat × exp(tahmini log getiri) biçimindedir; bu, lognormal dağılımın medyanıdır.','',
 'Her tahmin tarihinde yalnızca daha eski veriler kullanılır. Geçmişin son %20’si, en az altı gözlem, iç doğrulamadır; iç eğitim en az 30 gözlemdir. Ölçekleyiciler yalnızca iç eğitimde öğrenilir. Son posterior tüm erişilebilir geçmişle koşullandırılırken hiperparametreler ve ölçekleyici sabit kalır. Rastgele eğitim/test ayrımı yapılmaz.','',
 '2025–2026 raporlamasında hiperparametreler, çekirdek ve ölçekleyici 2024-12 itibarıyla donduruldu. Sonraki aylarda yalnızca artık gözlenmiş geçmiş değerler posteriora eklenir; yeni hiperparametre, optimizer, havuz veya ensemble ağırlığı seçilmez.','',
 'Birincil kaynaklar: [Rasmussen–Williams, GPML bölüm2](https://gaussianprocess.org/gpml/chapters/RW2.pdf), [bölüm4](https://gaussianprocess.org/gpml/chapters/RW4.pdf), [bölüm5](https://gaussianprocess.org/gpml/chapters/RW5.pdf); [Bonilla–Chai–Williams, çok görevli GP](https://proceedings.neurips.cc/paper/2007/file/66368270ffd51418ec58bd793f2d9b1b-Paper.pdf); [Álvarez–Rosasco–Lawrence, vektör değerli çekirdekler](https://arxiv.org/abs/1106.6251). Kaynaklar GP mekanizmasını destekler; bu veri üzerinde üstünlük garantisi vermez. Optimizer mekanizmaları önceki ailelerin kaynak kodlarından aktarıldı; 32 optimizerın her biri için makale düzeyinde bağımsız eşdeğerlik kanıtlanmış değildir.','',
 '## Aşamalar ve uygulama','',
 '| Aşama | Yapılan işlem |','|---|---|',
 '| 0 | Altın-only RBF, ortak ICM-RBF, ortak ICM-Matérn-3/2 ve önselli ICM-RBF: dört başlangıç modeli. |',
 '| 1 | Dokuz sırayla yürütülen grupta 32 optimizer; ortak 22 parametre, popülasyon24, nesil45, tekrar3. Gerçek amaç fonksiyonu çağrıları ayrıca kaydedildi. Eşit nesil, eşit hesaplama maliyeti demek değildir. |',
 '| 2 | Yalnızca DEV ile fiyat, yön, kararlılık, mimari referans ve koşullu hibrit rolleri; çiftli hata korelasyonu, yön kurtarma ve aylık fiyat kazancı incelemesi. Seçimler Stage3 öncesinde kaydedildi. |',
 '| 3A | Adaptive PSO, Adaptive TLBO, TLBO-tuned PSO, DE-tuned PSO, Adaptive CROW ve PSO–TLBO. Dış optimizer parametreleri yalnızca tarihsel iç doğrulamayla öğrenildi. |',
 '| 3B | Önceden sabitlenmiş korelasyon/yön kurtarma/fiyat kazancı koşullarını sağlayan MPA–SCA. Diğer çiftler sonuca bakarak açılmadı. |',
 '| 3C | Ayrı çekirdekler ve ayrı çıktı kovaryansları içeren iki bileşenli LMC. Yöntem ve bütçe üretim sonucu görülmeden sabitlendi. |',
 '| 4 | FULL ve REDUCED havuzları değerlendirmeden önce donduruldu; ortalama, medyan, geçmiş MAE tersi ve simplex/shrinkage karşılaştırıldı. |',
 '| 5 | Önceki ailelerin aynı aylardaki fiyatlarıyla yeniden hesaplanan karşılaştırma, Pareto incelemesi ve nihai dondurma. |','',
 'LMC genişletmesi B₁⊗K_RBF + B₂⊗K_M32 + D⊗I kullanır; 40 parametre ve tam yoğun Cholesky çözümü vardır. Bu, tek ortak çekirdeğin optimizerını değiştirmekten yapısal olarak farklıdır. Tam analitik olabilirlik türeviyle üç deterministik L-BFGS-B başlangıcı, maxiter60/maxfun1600 ve λ=1 önsel kullanıldı. Tüm40 türev, merkezi sonlu farklarla teknik olarak doğrulandı. Bütçe sınırında kalan sonlu çözümler kaydedilir; tümünün yakınsadığı veya küresel optimum olduğu ileri sürülmez.','',
 'Ensemble ilk altı DEV ayında eşit ağırlık kullanır. Sonraki ayın ağırlığı yalnızca önceki DEV hatalarıyla öğrenilir. Simplex ağırlıkları negatif olamaz ve toplamı birdir. Shrinkage α∈{0,0.1,0.25,0.5,0.75,1}; α yalnızca DEV ile seçilir. Tüm DEV’e uydurulmuş ağırlıkların sonucu yalnızca tanısaldır. Havuz DEV ile seçildiğinden geçmişe dayalı ağırlık sonuçları bağımsız iç içe test tahmini değildir.','',
 '## Bütün tek model deneyleri','',
 '| Model | Çıktı | DEV ΣAE | Yön | 2025 ΣAE / yön | 2026 Ocak–Temmuz ΣAE / yön |','|---|---:|---:|---:|---|---|']
 for n,z in sorted(models.items(),key=lambda kv:kv[1]['dev']['metrics']['sum_abs_error'] if kv[1]['dev']['metrics'] else float('inf')):
  v=[]
  for p,nn in [('dev',33),('transport_2025',12),('stress_2026',7)]:
   mm=z[p]['metrics'];v.append((f"{mm['sum_abs_error']:.4f}",f"{mm['direction_correct']}/{nn}") if mm else ('Bilimsel kapı başarısız','—'))
  lines.append(f"| {n} | {z['spec']['outputs']} | {v[0][0]} | {v[0][1]} | {' / '.join(v[1])} | {' / '.join(v[2])} |")
 lines+=['','## Geliştirmelerin hesaplama kayıtları','','| Model | Toplam koşu süresi (s) | DEV eğitim amacı çağrısı |','|---|---:|---:|']
 for n,z in models.items():
  if z.get('stage') not in ['3A','3B','3C']:continue
  calls=sum(row['diag'].get('training_calls',sum(q.get('evaluations',0) for q in row['diag']['repeat_records'])) for row in z['dev']['rows'])
  lines.append(f"| {n} | {z['seconds']:.2f} | {calls} |")
 lines+=['','Süreler gerçek koşu kayıtlarıdır, donanımdan bağımsız hız karşılaştırması değildir. LMC çağrıları tam yoğun kovaryans ve analitik türev içerir; diğerlerinin bir çağrısıyla aynı hesaplama maliyetine sahip değildir. DEV çağrı sayısı yalnızca33 tahmin tarihindeki eğitim amaçlarını toplar.']
 lines+=['','## Ensemble ve nihai roller','',f"Birincil: **{primary}**. Yön uzmanı: **{final['direction_specialist']}**. Dengeli karşılaştırma: **{final['balanced_challenger']}**. En iyi ensemble: **{final['ensemble_leader']}**, karar: **{final['ensemble_decision']}**.",'','| Havuz / yöntem | DEV ΣAE | Doğru yön |','|---|---:|---:|']
 for n,mm in sorted(final['ensemble_metrics'].items(),key=lambda kv:kv[1]['sum_abs_error']):lines.append(f"| {n} | {mm['sum_abs_error']:.4f} | {mm['direction_correct']}/33 |")
 lines+=['','## Önceki ailelerle DEV karşılaştırması','','| Model | ΣAE | Yön | MAE | RMSE |','|---|---:|---:|---:|---:|']
 for n,z in sorted(final['cross_family_metrics'].items(),key=lambda kv:kv[1]['dev']['sum_abs_error']):
  mm=z['dev'];lines.append(f"| {n} | {mm['sum_abs_error']:.4f} | {mm['direction_correct']}/33 | {mm['mae']:.4f} | {mm['rmse']:.4f} |")
 lines+=['','İki amaçlı DEV Pareto kümesi: '+', '.join(final['cross_family_frontier'])+'. Farklar nokta tahminleridir; 33 aylık ve çok sayıda model denenmiş bir DEV üzerinde istatistiksel üstünlük kanıtı değildir. Düzeltilmiş RBFNN ve GPR, 2024-12 sonrası hiperparametre öğrenmeme kuralına uyar. Daha eski ailelerin dış dönem protokolleri eşitlenmiş değildir; bütün ailelerin dış dönem tablosu kontrollü bir üstünlük sıralaması olarak yorumlanmaz.','',
 '## Seçilen GPR modelinin 2026 gerçek ve tahminleri','',
 'Birim USD/troy ons; aylık ortalama XAU/USD. Yalnızca mevcut Ocak–Temmuz dönemi gösterilir. Gerçekleşmesi/verisi bulunmayan aylar doldurulmadı. Model 2026 sonuçlarıyla seçilmedi.','',
 '| Ay | Gerçek | Tahmin | Mutlak hata | Gerçek yön | Tahmin yön |','|---|---:|---:|---:|---|---|']
 direction=lambda x:'↑' if x>0 else '↓' if x<0 else '→'
 for r in d['stress_2026']['rows']:lines.append(f"| {r['target']} | {r['actual']:.4f} | {r['forecast']:.4f} | {abs(r['actual']-r['forecast']):.4f} | {direction(r['actual']-r['rw'])} | {direction(r['forecast']-r['rw'])} |")
 import gzip
 rb=json.loads(gzip.decompress((root/'evidence/rbfnn_stage1/strict_results.json.gz').read_bytes()))['DE_ABC']
 lines+=['','## Önceki RBFNN liderinin 2026 gerçek ve tahminleri','','DEV ile seçilmiş DE–ABC–RBFNN. Aynı gerçekleşen değerler üzerinde, 2024-12 sonrası nonlinear ayar öğrenmeyen düzeltilmiş sürüm referans alınmıştır.','','| Ay | Gerçek | Tahmin | Mutlak hata |','|---|---:|---:|---:|']
 for r in rb['stress_2026']['rows']:lines.append(f"| {r['target']} | {r['actual']:.4f} | {r['forecast']:.4f} | {abs(r['forecast']-r['actual']):.4f} |")
 lines+=['','## Kontrol ve Uyum Özeti','',
 f"Bağımsız son aritmetik denetim **PASS**: {verification['model_specifications']} model, {verification['model_period_checks']} model-dönem ve {verification['ensemble_period_checks']} ensemble-dönem kontrolü. Her modelin hedef/gerçek/RW değerleri RBFNN referansıyla eşleşti. Model özetleri ham aylık tahminlerden yeniden hesaplandı.",'',
 'Yoğun kovaryans oraklıyla posterior ortalama/varyans/olabilirlik, gerçek çıktılar arası etkileşim, bağımsız çıktı limiti, hedef/gelecek etiketlerine değişmezlik ve ensemble geçmişe bağlılığı sınandı. Bilimsel kapılar: sonlu getiri ve varyans, |log getiri|<1, pozitif gözlem varyansı, Cholesky başarısı ve koşul sayısı üst sınırı≤1e12. Başarısız aylar gizlenerek alt küme sıralaması yapılmaz. Veritabanı salt okunur tutuldu, önce/sonra değişmezleri eşleşti.','',
 'ABC/ALO/DE–ABC’nin 1/(1+loss) dönüşümü için tüm teknik tekrar eğitim çağrılarında pozitif kayıp doğrulandı. ALO’da makine hassasiyeti düzeyindeki farklar nedeniyle bit düzeyinde özet eşitliği yerine tüm sayısal alanlarda 1e-10 bağıl/mutlak tolerans, ayrık kararlarda tam eşitlik kontrolü yapıldı. Orijinal ve tekrar özetleri ayrı saklandı; sonuçlar veya optimizer değiştirilmedi.','',
 'GPR %95 gözlem aralıkları ve NLPD raporlandı; aralıklar dış veride kalibre edilmedi ve hiperparametre belirsizliğini içermez. Tekrarların iç doğrulama dağılımı kayıtlıdır; tam tahmin sürecinin bağımsız tekrarlarla sağlamlığı **kanıtlanmış değildir**.','',
 '## Yeniden üretim ve kayıtlar','',
 '- Yöntem ve önceden sabitlenmiş protokol: `GOLD_MONTHLY_GPR_AUTHORITY_AND_STAGE_PLAN_2026-09-26.md`.',
 '- Deney koşuları, iş/çıktı kimlikleri, kaynak commitleri ve kararlar: ana aylık ledger ve `evidence/gpr_stage0`, `gpr_stage1`, `gpr_stage3` altındaki provenance dosyaları.',
 '- Ham sonuçlar: her aşamanın `results.json.gz` arşivi; aylık tahminler, hiperparametreler, seedler ve bilimsel tanılar korunur.',
 '- Stage2 rol dondurması, Stage3 kapanışları, Stage4 havuz dondurması ve final doğrulama ayrı dosyalardır.',
 '- Devam durumu: `GOLD_MONTHLY_GPR_EXECUTION_CHECKPOINT_2026-09-26.json`. Bu dosya çalışma hafızasıdır; hesap belleğinin değiştirildiği anlamına gelmez.',
 '', 'Sıradaki yol haritası ailesi: **N3 Multi-task RFF-BLR**. GPR çalışmasının tamamlanması N3 deneylerinin otomatik başlatıldığı anlamına gelmez.']
 (root/'GOLD_MONTHLY_GPR_YONTEM_VE_SONUCLAR_2026-09-26.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':run(Path('gold_axis_2026'))
