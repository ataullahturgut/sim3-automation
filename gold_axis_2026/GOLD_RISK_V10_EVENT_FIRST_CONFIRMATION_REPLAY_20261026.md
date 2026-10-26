# GOLD RISK V10 — İki ayrı araştırma: doğrulayıcı model ve geçmiş düşüş vakaları

26 Ekim 2026 · **Araştırma, canlı model değil.** BASE14/CFTC21, Neon ve otomasyonlara dokunulmadı.

## Deneyin hedefi

BASE14 Risk = -IsolationForest(RobustScaler(14 özellik)), eğitim skorundan 95. yüzdelik kırmızı eşik.
METAL+GVZ Risk = aynı algoritma 14 girdinin ilk 10'u, eğitim skorundan 95. yüzdelik kırmızı eşik.

**V10 çift doğrulama kuralı:** 

`V10_RED(t) = BASE14_RED(t) AND METAL_GVZ10_RED(t)`.

Bu **yeni bir tahmin modeli değildir**; iki bağımsız fit edilmiş anomali göstergesinin kırmızı alarmları arasındaki bir doğrulama kuralıdır. Yeni veri grubunun ilk-baskı sertifikası gerektirmez, V8 zaman-korumalı aynı 2023–2026 piyasa özelliklerinden yararlanır. Bu her zaman BASE14'ün bir altkümesidir, uyarı kaybı olabileceği için geçmişi kör olarak görmek gerekir.

11 hipotez/kural denendi; 2025 tanı döneminde birincil iki hedefi koruyarak seçim yapılsa **CFTC21** seçiliyor. V10 burada **2026 verileri geçmişte görüldüğü için keşifsel adaydır, önceden kilitlenmiş bağımsız bir galip değildir.** Seçim 2026 verisi kullanılarak yapılmadı; 2026 raporundaki aday geriye dönük araştırmadır.

## V8 orijinal 873 hizalı kök tarihte eşit karşılaştırma

| Dönem | Model | Ertesi gün >=%3 kayıp kırmızı günü | 5g >=%5 pozitif başlangıç günü | 5g ileri etiket kümesinde en az bir kırmızı | 5g hedefine göre yanlış kırmızı gün | Kırmızı gün toplam |
| --- | --- | --- | --- | --- | --- | --- |
| 2025 | BASE14 | 2/3 | 4/5 | 2/3 | 27 | 31 |
| 2025 | CFTC21 | 3/3 | 5/5 | 3/3 | 25 | 30 |
| 2025 | V10 çift doğrulama | 2/3 | 4/5 | 2/3 | **26** | **30** |
| 2026 | BASE14 | 4/4 | 9/13 | 4/4 | 37 | 46 |
| 2026 | CFTC21 | 4/4 | 6/13 | 2/4 | **25** | **31** |
| 2026 | V10 çift doğrulama | **4/4** | **9/13** | **4/4** | **32** | **41** |

**2026 çıkarılan beş yanlış kırmızı karar günü:** 20 Mayıs, 3 Eylül, 11 Eylül, 14 Eylül, 15 Eylül. Mart 30–Nisan 3 false-alarm bloğu **halen çözülmedi**. Daha iyi model sayılabilmesi için V10'un *hem* 2025'te CFTC21'in 3/3'ünü karşılaması, *hem* bağımsız sonraki dönemlerde BASE14'ün yakalama üstünlüğünü koruması gerekir; V10 henüz bu şartı karşılamıyor.

2026 beş günlük etiket gruplarından üçünün öncesinde, ilk pozitif başlangıç gününden önceki beş günlük dilimde en az bir kırmızı uyarı vardı. Bu **fiziksel düşüş başlamadan önce 3/4 kesin uyarı** anlamına gelmez. Gerçek fiyat zirvesi/düşüş başlangıcı ayrı etiketlenmelidir.

## Tarihsel düşüş olay örnekleri (2010–2019)

Mevcut Neon StakTrakr araştırma kaynağından **9 tek-gün %3+ düşüş başlangıç günü** ve **45 beş-gün %5+ pozitif başlangıç günü**. Ardışık pozitif başlangıçları gruplayınca **17 etiketsel küme** var; bunlar 17 fiziksel bağımsız çöküş değil. 2011 sonbahar ve 2013 ilkbahar-yaz dönemleri gerçek çalışma için zengin örneklerdir. Aynı tarihli fiyat satırlarının **ilk yayın vintage/PIT doğrulaması yoktur**. Bu yüzden yeni olaylar **bu V10 modelinin eğitimine sokulmadı**; yalnız tarihsel olay adayları listesine eklendi. 2020–2022 bu deneye dahil edilmedi.

## Bilimsel sıradaki deney protokolü

1. 2010–2019 vaka kümelerinde yerel zirve, fiziksel düşüşün ilk işlem günü, dip ve toparlanma etiketlerini tutarlı bir kuralla yeniden belirle; 5g pencerelerini bağımsız çöküş gibi sayma.
2. Her vakayı büyüklük (>= %3 / >= %5), yön (başlangıç-sonrası), zaman (ilk risk alarmı, başlangıç öncesi marj) ve karşı örnek (aynı rejim ama çöküş olmamış) bakımından eşleştir.
3. 2010–2019 için metal, CFTC, USD, GVZ ve faiz verilerinin dönemsel kapsamasını, tarihi yayın anını ve orijinal veri vintage'ını çıkar; yalnız yayın kanıtı olanlar giriş olarak kullanılabilir. Gerekiyorsa eski dönem için daha az özellikle **ayrı model**; yeni modele sorgusuz veri yığma yok.
4. 2023–2025 dönemiyle ayar, sonuç pencereleri çakışmasın diye en az 5 işlem günü **purge/embargo**; 2026 zaten geçmişte incelendiği için gerçek yeni kör test gelecekteki verilerde yapılır.
5. Yanlış alarm günleri + yanlış alarm epizodu + bağımsız fiziksel düşüş başlangıcından önceki uyarı zamanı + büyük düşüş kaçırma sayısını bir arada değerlendir.

## Kullanım

`python -m pip install numpy scikit-learn`
`python independent_confirmation_research.py`
`python -m unittest test_candidate.py -v`

Girdi: `inputs/gold-risk-overlay-2023-2026-source-artifact.zip` ve `inputs/CFTC_GC_SI_2023_2026_QUALITY_GATED.csv` (V8 orijinaller, hash kontrolü). Çıktı: `outputs/v10_candidate_results.json`, `outputs/v10_daily_signals.csv`. `historical_cases_2010_2019.csv` raporun içinde verilen SQL ile Neon read-only sorgusundan türetildi, model eğitiminden ayrı.

## Literatür

- Precious metals bubble risk (2026): https://doi.org/10.1002/ijfe.70267
- Early Warning Systems for Financial Instability (2023): https://doi.org/10.1016/j.ijforecast.2022.08.004
- BIS early warning indicators: https://www.bis.org/publications/qr-201803/early-warning-indicators-banking-crises-expanding-family
- scikit-learn Isolation Forest: https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html