# Altın büyük düşüş erken uyarı araştırması — V13 gerçek koşu

26 Ekim 2026. **Araştırma fiilen çalıştırıldı; güvenilir yeni erken uyarı modeli elde edilemedi. 2000–2009 fiyat kapsamı ve tarihsel ilk-yayın sertifikası tamamlanmadı.** Canlı uygulama, Neon ve orijinal BASE14/CFTC21 dosyaları değiştirilmedi.

## 1. Somut sonuç

- Özgün V8 arşivi indirildi ve mevcut referans birebir üretildi: 2026 BASE14 **46 kırmızı / 37 yanlış**, CFTC21 **31 kırmızı / 25 yanlış**; ertesi gün %3 düşüş **4/4 ve 4/4**, beş günlük etiket grubu **4/4 ve 2/4**.
- 2010–2022 **3.282 dört-metal ortak seansı**, Neon salt-okuma sorgusuyla kaynak arşivine karşılaştırıldı: **0 değer farkı**. Bir ek günde PT/PD eksik; doldurulmadı.
- **27 fiyat düşüş olay grubu** bulundu. -30/+10 pencereleri birleştirildiğinde **14 zaman kümesi** kalıyor: 27 bağımsız kriz iddiası yok.
- Katı aynı-yıl ve pencere çakışmama şartlarında **8 olay / 21 negatif kontrol**, **32 olay-öncesi gün +21 kontrol =53 eğitim örneği**. 18 olayda iki uygun kontrol bulunamadı; 1 olayda özellik başlangıç kapsamı eksik. Özellikle 2013 büyük düşüşleri açıklayıcı olay tablosunda var, fakat bu eşleştirme altında denetimli eğitimin temsilinde eksik: önemli sınırlılık.
- **6 model/özellik ailesi ×3 eğitim-kantili eşiği =18 meta-filtre** çalıştırıldı; 2025 seçiminde hiçbir aday 3/3 ertesi-gün yakalamayı koruyamadı. Bu nedenle yeni filtre seçilmedi. `PASSTHROUGH`, bir kazanan değil, filtre uygulamama kaydıdır.
- **12/12 test geçti**. Temiz dizindeki tekrar koşusunda 10 temel çıktı dosyası **byte-for-byte aynı SHA-256** verdi.

## 2. Yeni bulunan tarih sorunu: 2023 ION gecikmesi

CFTC'nin [resmî özel duyuru arşivi](https://www.cftc.gov/MarketReports/CommitmentsofTraders/HistoricalSpecialAnnouncements/index.htm) 2023 Ocak31–Mart14 raporlarının olağan tarihte yayımlanmadığını gösteriyor. Eski CSV normal +7 gün kullanmış. GC/SI toplam **14 kayıt** için resmî yayın +1 gün ile mevcut vekilin daha geç olanı uygulandı; orijinal CSV değiştirilmedi.

| Pozisyon tarihi | Gerçek yayın | Araştırmada en erken kullanım |
|---|---|---|
| 2023-01-31 | 2023-02-24 | 2023-02-25 |
| 2023-02-07 | 2023-03-03 | 2023-03-04 |
| 2023-02-14 | 2023-03-08 | 2023-03-09 |
| 2023-02-21 | 2023-03-10 | 2023-03-11 |
| 2023-02-28 | 2023-03-14 | 2023-03-15 |
| 2023-03-07 | 2023-03-16 | 2023-03-17 |
| 2023-03-14 | 2023-03-21 | 2023-03-22 |

21 günlük eskime kapısı nedeniyle hizalı toplam örnek **873→859**; kayıp 14 gün eğitim döneminde. 2025 **232**, 2026 **161** değerlendirme günü aynı kaldı. RobustScaler/IsolationForest yeniden fit edildiğinde eğitim eşiği değişti. Aşağıdaki yeni sayılar **model geliştirme kazancı değildir**, tarih ve eğitim-örneklemi etkisidir. İlk-yayın *sayısal vintage* hâlâ kanıtlı değildir.

## 3. Aynı günlerde model karşılaştırması

BASE14, RobustScaler + IsolationForest (200 ağaç, random_state=1701) ile denetimsiz anomali öğrenir; kırmızı eşik yalnız eğitim skorunun %95 kantilidir. 2025 için 2023–24, 2026 için 2023–25 fit edilir. İlk 6 özellik altın trend/RSI/oynaklık ve metal ayrışması, 4 özellik GVZ, 2 özellik yayımlanmış broad USD getirisi, 2 özellik 10Y nominal faizdir. CFTC21 buna GC/SI net pozisyon/OI, GC haftalık ve dört haftalık değişimleri, SI dört haftalık değişimi, GC−SI farkı ve GC short/OI olmak üzere 7 girdi ekler. Bu skor düşüş olasılığı değildir. Yeni denetimli katmanın eğitimi ise yalnız 2010–2022 olay/kontrol örnekleridir: L2 lojistik C=0.1 veya 60 ağaçlı depth2/min_leaf10 GBM; ayrıca CFTC/USD/faiz/GVZ aileleri birer birer çıkarılır. Tam 31 özellik listesi ve sabit eşikler arşivde bulunur.

Yeni meta-filtreler tarih-düzeltilmiş BASE14 veya CFTC21 kırmızısının üzerine uygulanır. Aşağıdaki Q25 adayları önceden belirlenen orta eşik örnekleridir; 2026'ya bakılarak seçilmiş kazananlar değildir. Diğer 16 aday da `outputs/paired_results.csv` ve tam çıktı arşivindedir.

| Dönem | Model | Kırmızı gün | Ertesi gün ≥%3 | 5g ≥%5 etiket kümesi | Yanlış kırmızı gün |
|---|---|---:|---:|---:|---:|
| 2025 | Tarih-düzeltilmiş BASE14 |32|2/3|3/3|27|
| 2025 | Tarih-düzeltilmiş CFTC21 |21|2/3|2/3|17|
| 2025 | Lojistik tüm özellikler Q25 |27|2/3|2/3|23|
| 2025 | Sığ GBM tüm özellikler Q25 |32|2/3|3/3|27|
| 2026 | Tarih-düzeltilmiş BASE14 |50|4/4|4/4|40|
| 2026 | Tarih-düzeltilmiş CFTC21 |32|4/4|3/4|25|
| 2026 | Lojistik tüm özellikler Q25 |12|1/4|2/4|7|
| 2026 | Sığ GBM tüm özellikler Q25 |49|4/4|4/4|39|

Lojistik yanlış alarmı azaltırken üç ertesi-gün düşüşünü kaçırıyor. GBM yalnız bir yanlış günü azaltıyor; yanlış alarm epizodu **12→13**, tüm alarm epizodu **10→11**: süreyi parçalayarak daha iyi görünme riski var. Hedeflenen **4/4 korunarak 25 yanlış günün altı** sağlanmadı. 2025'te filtre girdisi birleşiminin kendisi 2/3 olduğu için yalnız veto yapan bir katmanın 3/3'e ulaşması zaten mümkün değil; adaylar bu başarısızlık açıkça kaydedilerek reddedildi.

Özgün V8 karşılaştırması `original_V8_metrics.csv` ve `replay/` dosyalarında ayrıca korunur. 2026'nın önceden incelenmiş olması nedeniyle bu bir **geriye dönük stres testidir, kör test değildir**.

## 4. Alarm gerçekten düşüşten önce mi?

Günlük fiyatlarda olay aralığındaki zirvenin sonraki seansı “başlangıç vekili” alındı. Bu kural gün içi gerçek başlangıcı kanıtlamaz. Son 10 seans içindeki ilk kırmızı:

| Günlük başlangıç vekili | BASE14 ilk alarmı | Seans farkı | Yorum |
|---|---|---:|---|
| 2026-01-30 |2026-01-21|7|Günlük başlangıç vekilinden önce|
| 2026-06-05 |2026-06-05|0|Başlangıç günü kapanışı; erken sayılmaz|
| 2026-06-18 |2026-06-05|9|Önceki Haziran düşüşünün alarmıyla örtüşüyor; yeni bağımsız başarı sayılmaz|
| 2026-08-26 |2026-08-21|3|Günlük başlangıç vekilinden önce|

2026 Mart13 günlük olay adayı bozuk 27 Şubat fiyatının etkilenen özellik penceresine denk geliyor. Uygun karar günü yok; **kaçırılmış olay veya doğru tahmin sayılmadı**, `NOT_EVALUABLE_QUARANTINE` işaretli. Referans 161 günün dışında kalır. Bu dışlama sonuç kapsamını daraltır.

`pre_onset_all_models_1_3_5_10.csv` her aday için 1/3/5/10 seans önceden uyarıyı, `daily_alarms_with_source_dates.csv` karar günü fiyat değişimini ve son görülen CFTC tarihlerini, `alarm_episodes.csv` alarm başlangıç/bitiş/süresini verir. “İlk alarm” belirtilen geriye bakış penceresindeki ilktir, tüm tarihin ilk alarmı değildir.

## 5. Tarihsel olaylar ve ekonomik ortaklıklar

Örnek günlük zirve-dip düşüşleri: 23–25 Ağustos 2011 **-%9,01**; 19–26 Eylül 2011 **-%11,12**; 10–16 Nisan 2013 **-%12,87**; 13–28 Haziran 2013 **-%13,20**; 6–17 Mart 2020 **-%12,72**; 7–13 Ağustos 2020 **-%6,33**. Bunlar kaynak serisinin günlük referans fiyatlarıdır, intraday gerçekleşmiş işlem fiyatları değildir. Tam 27 satır `historical_event_coverage.csv` içindedir.

Eşleşmiş küçük örneklemde (32 pozitif gün,21 kontrol) medyanlar:

| Geçmiş gösterge | Düşüş öncesi | Kontrol |
|---|---:|---:|
| GVZ |19,13|17,38|
| Yayımlanma vekilli 5g broad USD log getirisi |+%0,375|-%0,148|
| GC managed-money net / açık pozisyon |%25,54|%20,77|
| SI managed-money net / açık pozisyon |%23,63|%13,44|
| GC net/OI haftalık değişimi |−1,85 yüzde puan|−0,15 yüzde puan|
| Reel 10Y son 5 gözlem değişimi |−4 baz puan|−2 baz puan|

Dolar güçlenmesi, pozisyon yoğunluğu ve GC çözülmesi bu örneklemde birlikte görülebiliyor. Ancak faiz artışı bütün olayların ortak şartı değil; reel faiz medyanı iki sınıfta da düşüyor. Dağılımlar geniş ve örtüşüyor. Bu değerler seçilmiş küçük örneklemin **betimleyici sonuçlarıdır**, nedensellik veya doğrulanmış alarm kuralı değildir. Kontrol eşleştirmesi altın trendi/oynaklık/dört-metal ayrışmasıyla yapılır; bütün makro değişkenlerde birebir ekonomik eşitlik garanti etmez. 2011 kontrol mesafeleri de yüksek; eşleştirme kalitesi dosyada açık.

Tarihsel walk-forward modelleri de güven vermiyor. <=2016 eğitim/2017–19 kontrol döneminde sert düşüş etiketi yokken çok sayıda alarm üretildi; <=2019 eğitim/2020–22 testinde yakalama artsa da yanlış alarm yüksekti. Bu test, meta skorların bağımsız risk alarmları olarak kalibre edilmediğini gösterir. Ek +3/+7 günlük kaynak gecikmesi hassasiyeti yalnız 2025'te değerlendirildi; sonucuyla aday seçimi değiştirilmedi.

## 6. Kaynaklar, eksikler ve zaman doğruluğu

- [CFTC resmî yıllık ZIP](https://www.cftc.gov/MarketReports/CommitmentsofTraders/HistoricalCompressed/index.htm): 2000–2009 legacy ve 2010–2022 disaggregated gerçekten indirildi; yalnız COMEX088691/084691 ayıklandı. Legacy noncommercial ile managed-money aynı özellik olarak birleştirilmedi. 2006'ya geri yayımlanan disaggregated veri o yıllara taşınmadı.
- [Cboe GVZ](https://cdn.cboe.com/api/global/us_indices/daily_prices/GVZ_History.csv): arşiv alındı. 2000'de GVZ varmış gibi doldurma yok; ilk baskı belirsiz.
- [Fed/FRED](https://fred.stlouisfed.org/): DGS2,DGS10,DFII10,DTWEXB,DTWEXBGS gerçek CSV'leri indirildi. Fed doğrudan H15 dosyasının SHA256 değeri önceki resmî indirmeyle aynı: `75dcc355bf51e2c45bd04d9b4cfc7fbc1edaa81abef1c0318de8a18ac44b9906`.
- 2010–2019 USD için eski DTWEXB; 2020+ için yeni DTWEXBGS. Yeni serinin 2006'ya uzanan geriye doldurulmuş değerleri eski dönemde kullanılmadı. Tarihsel H10 +10 takvim günü, H15/TIPS +1 gün, CFTC +7 gün **hipotetik araştırma gecikmeleridir**; gerçek her-vaka yayın takvimi doğrulaması değildir. 2013 Ekim ve2018 sonu–2019 ilk çeyrek CFTC belirsizliği dışlandı.
- 2000–2009 altın fiyatı: FRED GOLDAMGBD228NLBM **404**, BoE iki indirme yolu **403**, doğrudan LBMA PM JSON **403**. [FRED'in 2022 kaldırma duyurusu](https://fred.stlouisfed.org/news/2022/01/ice-benchmark-administration-ltd-iba-data-to-be-removed-from-fred) de seri eksikliğini açıklar. Bu dönemde olay/kontrol tablosu veya eğitim sonucu **üretilmedi**. Var olan CFTC/makro veri, eksik altın fiyatının yerine geçmez.
- V12 Actions [40297856605](https://github.com/ataullahturgut/sim3-automation/actions/runs/40297856605) arşivi gerçekten indirildi; SHA256 `09671971e3238ac608e37e95a7e1a0d9462a4779787829d3c4231fd63509524e`. Arşiv CFTC2010–19+GVZ içeriyor; o koşudaki Fed indirmeleri timeout olmuştu. Bu turda yeniden indirilerek alındı.
- Özgün kaynak [40013192599](https://github.com/ataullahturgut/sim3-automation/actions/runs/40013192599), arşiv SHA256 `d45cef136f673a8016a0f457599f2a55b125d14836452418b0f57808306f1856`. Bu tur yerel Python'da koştu; yeni Actions koşusu başlatıldığı iddia edilmiyor.

**SHA doğruluğu ilk-yayın doğruluğu değildir.** Mevcut dosyalar geçmiş revizyon içerebilir. `strict_gate()` bu verilerle güvenilir PIT sinyali üretimini reddeder; bütün yeni sonuçlar `strict_pit_signal=False`. Sinyal/ilk baskı sertifikasyonu TAMAMLANMADI. Resmî yayın anı kanıtlanmayan seri başarılı canlı geçmiş sinyal gibi sunulmadı.

## 7. Yeniden üretim ve teslim

Python3.12; sürümler `requirements.txt`. İnternet/veritabanı/parola gerekmeden dondurulmuş arşivden:

```bash
cd gold_axis_2026/research/case_control_v13
python -m pip install -r requirements.txt
bash reproduce.sh
```

`frozen_inputs.zip` özgün model kaynak ZIP'i,398 satırlık CFTC girdisi, gerçek Fed/GVZ CSV'leri, GC/SI arşivlerinden hash-korumalı sayısal ayıklama, Neon salt-okuma çıkarımı, SQL ve indirme denetimlerini içerir. Büyük tüm-piyasalar CFTC ZIP'leri bu kompakt pakete tekrarlanmaz; her özgün dosyanın URL/hash'i korunur, `acquire.py` yeniden indirir. Sayısal ayıklama ayrı SHA kapısıyla denetlenir.

`outputs_full.zip`: bütün 31 özellik paneli; 27 olay ve21 kontrolün -30/+10 pencereleri; bütün adayların günlük skor/alarm CSV'leri; kaynak as-of vekil defteri; 2025 seçim kilidi; 2026 stres; horizon/walk-forward/ablation/gecikme duyarlılığı; ilk alarm ve kaçırmalar; test logları. Önemli tablolar ayrıca açık CSV olarak kaydedildi.

Testler: V8 referans; gelecekteki fiyatları11 kat değiştirdiğinde tarihsel girdilerin sabitliği; yalnız2022'ye kadar eğitim; kontrol ayrıklığı; ION yayın tarihi; PIT reddi; Şubat27 karantina; aynı393 test günü; yalnız2025 seçim; kaynak-zaman defteri; Neon fiyat eşitliği; karantinadaki olayın yanlışlıkla “kaçırıldı” sayılmaması. **12 PASS; performans/kapsam kabul kapısı FAIL.**

Model protokolü sonuçlardan önce yerel commit `f9fc5fc` ile kaydedildi. İlk kodda yalnız1 kontrolü olan olay da alınmıştı; kullanıcının 2–4 şartına uymadığı için çıkarıldı ve son koşu 8 olay/21 kontrolle tekrar edildi. Bu hata düzeltmesi raporludur; 2026 sonuçları eşik/özellik seçimine sokulmadı. Bu yine de gerçek kör çalışma iddiası sağlamaz.

## Karar

Yeni modeller ana modellere eklenmeyecek. Hedef iyileşme sağlanmadı. Kullanıcı talebinin **fiilî deney ve karşılaştırma kısmı yürütüldü; 2000–2009 ve tam ilk-yayın doğruluğu kısmı açık kaldı**. Bir sonraki bilimsel çalışma eksik fiyat arşivi ve ilk-yayın kanıtı üzerinde olmalı; 2026 Mart/Ağustos alarmlarını kaldırmak için bu sonuçtan yeni eşik türetilmemeli.
