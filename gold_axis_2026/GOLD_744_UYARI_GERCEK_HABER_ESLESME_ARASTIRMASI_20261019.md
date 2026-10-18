# 2023–2025: 744 gerçek fiyat alarmı hangi haberlerle ilişkili?

**19 Ekim 2026 — OLAY-02 × ÖĞREN-03 × ETKİ-05 × GOLD downside-native-model**

## Çalışma yapıldı mı?

**Evet.** [70.915 gerçek altın M15 BID/ASK kapanışında](adaptive_trading_core/GOLD_DOWN_FALL_ONSET_REAL_2023_2025_REPLAY_V1_20261019.json) tekrar üretilen **744 fiyat-zayıflama alarmı**, [OLAY-02 arşivindeki 85 saatli CPI/NFP/FOMC ekonomik yayını](OLAY_02_85_MAKRO_YENI_DNA_TEPKI_PLASEBO_20261014.csv) ile **saat düzeyinde** birleştirildi. Ayrıca [17 büyük düşüş için belgelenen olay adaylarının tarihlerini](ETKI_05_17_DUSUS_HABER_VE_M15_GERI_CEKILME_SAAT_KARSILASTIRMA_V2_20261018.json) saatleri gerçekten bilinmedikleri sürece **gün düzeyinde**, ana analizin dışında tuttuk.

**Bu 744 haber değildir, 744 fiyat uyarısıdır.** Kayıtlı makro takvimi tüm dünya haberlerini kapsamaz. 85 makronun "release UTC" alanı tarihsel araştırma takviminden gelir: ilk baskı, arşiv veri konsensüs vintage'ı ve haberin 2023–25'te gerçekten hangi milisaniyede görülebildiği henüz bağımsız olarak **firstprint-certify edilmiş değildir**. BLS'nin resmî CPI arşivi https://www.bls.gov/bls/news-release/cpi.htm ve duyuru takvimi https://www.bls.gov/schedule/news_release/cpi.htm referans olarak mevcuttur; bunlardan 85 ayrı orijinal belge taranıp UTC-firstprint sertifikası üretilmiş değildir.

## 1) 744 uyarı ve zaman sırası

| Bir fiyat uyarısının kayıtlı CPI/NFP/FOMC açıklamasına göre zamanı | Uyarı | Yaklaşık sonraki 5×96 M15 bar içinde en az %4 yeni düşüş |
|---|---:|---:|
| **Açıklama önce:** 0–4 saat önce açıklama yayımlanmış | **54** | **0/54 = %0,00** |
| **Açıklama önce:** 4–24 saat önce açıklama yayımlanmış | **41** | **5/41 = %12,20** |
| **Alarm önce:** 0–4 saat sonra açıklama yayımlanacak | **13** | **1/13 = %7,69** |
| **Alarm önce:** 4–24 saat sonra açıklama yayımlanacak | **50** | **5/50 = %10,00** |
| **Takvimde eşleşme yok:** ±24 saat içinde bu üç tür açıklama yok | **586** | **46/579 = %7,94** |
| **TOPLAM** | **744** | **57/737 = %7,73** |

**Önemli:** Bir uyarının hem öncesinde hem sonrasında yayın bulunursa tabloya yalnız **önceki en yakın** habere göre tek kategoriyle girer. Ham eşleşme sayısı: **95 uyarı** gerideki 24 saatte makro yayına yakın; **68 uyarı** ilerideki 24 saatte makro yayına yakın; çift eşleşmeler giderildiğinde **158 benzersiz alarm** en az bir makroyla ±24 saat yakın, **586 benzersiz alarm** bu dar takvimde hiç eşleşmedi.

**Gelecek sonuç etiketi:** Uyarı anından sonraki **480 kaydedilmiş 15dk barı** içinde görülen **en kötü ilave fiyat getirisi ≤−%4**. Bu yaklaşık beş normal işlem seansı kadar *fiyat gözlemi*, gerçek 5 takvim günü veya sürekli açık bir piyasa değildir; seans/hafta sonu boşlukları bu ufku uzatabilir. 7 alarmın gelecekte 480 bar verisi tamamlanmadığından sonuç **bilinmiyor**, başarısız kabul edilmedi. Alarm geçmiş verilerden; sonuç yalnız daha sonraki bilimsel değerlendirmeden elde edildi, işlem anı girdisi değildir.

**Net yorum:** Makro açıklamadan sonraki ilk dört saatte **54 fiyat zayıflama** gözlendi. **Hiçbirinin ardından** bu ölçüm ufkunda yeni bir %4'ten büyük fiyat düşüşü görülmedi. İstatistiksel neden-sonuç veya evrensel sonuç çıkarılmaz; türlere, katılım oranlarına ve 2025 veri eksiklerine göre uygun örnekleme yapılmadı. **Makroya yakın fiyat alarmı, otomatik çok günlük büyük düşüş alarmı değildir.**

## 2) Haber türü: hangi sınıf fiyat uyarısı ile daha çok eşleşiyor?

| Arşivdeki zamanlı haber türü | Yayın | Yayın sonrası 4 saatte en az bir fiyat-zayıflama uyarısı | Yayın sonrası 24 saatte en az bir fiyat uyarısı |
|---|---:|---:|---:|
| CPI enflasyon | **34** | **21** | **26** |
| NFP istihdam | **35** | **21** | **22** |
| FOMC faiz kararı | **16** | **6** | **15** |
| **Toplam** | **85** | **48** | **63** |

Bu sayı, CPI/NFP haberlerinin ilk birkaç saatlik **fiyat dalgalanmasıyla zaman yakınlığının yüksek** olduğunu gösterir. Ancak M15 zayıflama −%0,5 alarmı **şokun yönünü veya sonraki büyüklüğünü tahmin etmez**. Yayınların hiçbirinin ilk PRICE-DOWN neden olduğu bu sayıdan kanıtlanmaz.

## 3) Yıllara göre alarm–haber kapsama

| Yıl | Fiyat alarmı | Öncesindeki 24 saatte CPI/NFP/FOMC | Sonrasındaki 24 saatte CPI/NFP/FOMC |
|---|---:|---:|---:|
| 2023 | **219** | **33** | **19** |
| 2024 | **237** | **44** | **22** |
| 2025 | **288** | **18** | **27** |

**Veri evreni farkı:** 2023 ve 2024 için takvimde **32'şer** makro yayın; 2025 için ise **yalnız 21** yayın vardı. Dolayısıyla 2025'te daha çok “makroya bağlanamayan alarm” görmemiz, diğer ekonomik haberlerin etkisiz olduğunu **göstermez**; takvim yetersizdir.

## 4) 17 büyük düşüş ile kesişim

Ayrı [17 büyük düşüş ve 744 alarm denetimi](adaptive_trading_core/GOLD_744_UYARI_17_BUYUK_DUSUS_MAKRO_TUR_ESLESMESI_20261019.json) üretildi.

- Fiyat etiketlerinden sonuç-sonrası seçilmiş **17/17** büyük düşüşün pivot gününün **−1/+2 gün çevresinde** en az bir fiyat alarmı var. **Bu fiyat zaten bozulurken alarm olduğu için %100 erken öngörü değildir.**
- Yalnız **3/17** başlangıç çevresinde (−1/+2 gün) yukarıdaki **85 makro açıklamanın biri** var: **1 Şubat 2023 FOMC**, **3–5 Mayıs 2023 FOMC/NFP**, **11 Aralık 2024 CPI**. Bu üçü bile kesin ilk düşüş nedeni değil.
- **13/17** büyük düşüşün pivot çevresindeki en az bir alarmı ile **önceden seçilmiş 17 tarihli belgesel haberden birinin** günü ±3 takvim günü içindeki yakınlığı var. Bu örnekler önceden **özellikle büyük düşüşleri açıklamak için** derlendiği için "13/17 haberle başlatıldı" demek **seçim yanlılığı** olur; bu belgelerin çoğu haberi değil gerçekleşmiş düşüşü anlatır.
- **2023 3 Şubat NFP** 13:30Z → takip eden erken fiyat alarmı **13:45Z**; fakat büyük fiyat bacağı **1 Şubat'ta** başlamıştı. Yeni aşağı dalgayı başlatma veya güçlendirme adaylığı var; bacağın ilk nedeni değil.
- **2023 4 Mayıs 02:15Z** fiyat alarmı, **3 Mayıs 18:00Z FOMC'den 8s15dk sonra**; fiyatın ilkin yukarı tepki verebildiği karşı örneği dikkate alınmalı.
- **2024 11 Aralık 04:45Z** fiyat alarmı, o günkü **CPI 13:30Z'den 8s45dk önce**. Sonraki CPI açıklaması ilk uyarıya geriye doğru neden olamaz.
- **2025 26 Aralık 17:30Z** ilk fiyat alarmı ve tarihli **CME teminat kararı** aynı takvim günü. CME raporunun **ilk yayın saati** bulunmadığından bu olay kesin olarak "haber ilk" sınıfına yükseltilemez; 29 Aralık büyük satıştan önce var olan resmî belge adayı olarak kalır.
- 2 Nisan 2025 tarifeleri ve 13 Haziran 2025 saldırıları gibi vakalarda haberin **ilk XAU yanıtı yukarı** olabileceği için K koşulu tek başına "DOWN başlatır" olarak kodlanmamalı.

## 5) ÖĞREN-03 ve ETKİ-05'e ne ekledik, ne henüz ekleyemedik?

**Eklenen ve çalıştırılan:** [downside_alert_news_join_v1.js](adaptive_trading_core/downside_alert_news_join_v1.js) ile **her fiyat alarmının** ilk erişilebilir ekonomi makro saatine göre konumu, önceden gelen release mi, gelecekteki release mi, tarihinden başka zamanı bilinmeyen ilgili haber mi, ileri ufuktaki ≥%4 düşüş etiketi mi, tümü 744 kayıt için işlendi. İlk haber **sonra** geldiyse ilk tetikleyici kabul edilemez. Sonradan yazılmış haber **ilk-baskı olarak gösterilemez**.

**Bu aşamada asla yapılmayanlar:** Bu dosyadaki **macro-event timestamps** geriye dönük yayımlanma saatlerine dayanır; gerçek 2023'te ilk erişim ve konsensüs-vintage güveni sertifikalı olmadığından hiçbir macro K/ORG açıklaması kesin fiyat tetikleyici sayılmadı. 85 yayından yeni bir yön/profit kuralı eğitilmedi. 744 alarm S3 satış emirlerine çevrilmedi. Alış/satış maliyeti araştırma sınırı tek yön %0,8 / round-trip %1,6 olarak korunur.

## 6) Sonuç — kullanıcının sorusuna cevap

**744 fiyat alarmını olay/öğren/etki ile ilk kez sistematik olarak birleştirdik.** Buna rağmen 586 alarmın yakınında **mevcut CPI/NFP/FOMC takviminde** haber yok. Bu, ekonomik haberin etkisini yoklamayı değil, **haber evreninin dar olduğunu** gösterir; tarife/jeopolitik/likidite/rezerv/ETF/şirket finansman ve pozisyon açıklamaları günlük ve saatli olarak tamamlanmadıkça tüm alarm evreni için genel nedensellik hükmü verilemez.

Büyük düşüşlerin ne kadarını ilk haberin yakaladığını öğrenmek için önce **gerçek haber başlangıç saati** ile **gerçek zayıflama saati** birlikte kanıtlanacak; sonradan gelen haberler ayrı hızlandırıcı rolünde kalacak. **Fiyat zayıflama alarmı = ekonomik satış sinyali değil.**

### Tam hesap verileri, tekrar çalıştırma ve testler

- [744 alarmın tamamı — kolay denetlenebilir CSV](adaptive_trading_core/GOLD_744_FIYAT_UYARISI_HABER_ZAMANI_YAN_YANA_20261019.csv)
- [744 alarm + 85 makro yayın + 17 tarihli haber — makine JSON](adaptive_trading_core/GOLD_2023_2025_744_FIYAT_UYARISI_85_MAKRO_HABER_ESLESME_20261019.json)
- [Makro ve 17 büyük düşüş kırılımları](adaptive_trading_core/GOLD_744_UYARI_17_BUYUK_DUSUS_MAKRO_TUR_ESLESMESI_20261019.json)
- [Reprodüksiyon kodu](adaptive_trading_core/downside_alert_news_join_v1.js)
- [9/9 zaman-vintage ve lookahead koruma testi](adaptive_trading_core/test_downside_alert_news_join_v1.js)

**Durum:** \`744_ALERTS_MATCHED=YES\`; \`AVAILABLE_CALENDAR_85_RELEASES=YES\`; \`DATE_ONLY_CASE_CONTEXT_17=YES\`; \`MARKET_DATA_BARS_70915=YES\`; \`FIRSTPRINT_CERTIFIED=0\`; \`ALL_WORLD_NEWS_CAPTURED=NO\`; \`ECONOMIC_CAUSAL_ALPHA=NOT_PROVEN\`; \`S3_BANK_TRADES=0\`.
