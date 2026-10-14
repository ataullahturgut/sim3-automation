# ALTIN — COT resmî rapor yayımlanma saati denetimi ve 154 haftalık analizin tekrar eşleştirilmesi
**Tarih: 14 Ekim 2026 | Kapsam: 2023–2025 | Araştırma otoritesi; tahmin stratejisi veya nedensel ispat değildir.**

## 1. CFTC gerçek rapor sözleşmesi
- **`report_date` = pozisyonun ölçüm günü** (normalde ilgili haftanın SALI günü kapanışı). Ölçüm günü kamuya yayımlanma anı DEĞİLDİR.
- **`published_at` = CFTC'nin kamuya duyurduğu tarih ve 15:30 ABD Eastern yayın saati** (normalde CUMA). ABD yaz saati sırasında **19:30 UTC = Türkiye 22:30**, kış saati sırasında **20:30 UTC = Türkiye 23:30**. Saat Amerika/New_York DST ile hesaplanmalıdır.
- **Tatil/olağanüstü durum:** federal tatil, 2023 ION siber aksaması ve 2025 federal kapanma olayında alışılmış 3 günlük gecikme geçersizdir. 2023 ION raporlarına ve 2025 revize kapanma takvimine CFTC resmi duyuruları üstün otoritedir.
- **Veri semantiği:** COT'un *Disaggregated Futures Only* ve *Futures & Options Combined* ölçümleri ayrı seridir. Ham depodaki `opt_mm_net`/`d_opt_mm_net` alanı tek başına 'yalnız opsiyon alım satımı' sayılmaz; kaynak alanı futures+options combined sınıflaması çerçevesinde raporlanmalıdır.

## 2. Eski depo tablosunda saptanan yanlış zamanlama
Kaynak: [eski 1060 satırlık ham COT PIT durumu](GOLD_COT_GOLD_PIT_STATE_RAW_REBUILT_2026-10-06.csv). **2023–2025 157 gözlem** içinde `DEFAULT_7D_CONSERVATIVE` baskındı: normal salı ölçümünü **sonraki salı 15:30 ET** tarihinde erişilebilir kabul ediyor; gerçek normal erişilebilirlik cuma 15:30 ET'dir. Konservatif olması geçmişten bilgi sızdırmıyor, ama yayımlanmış veriyi dört gün gereksiz saklayıp altın olay analizi ve korelasyonları değiştiriyor.
- [157 satır yayımlanma saati karşılaştırması](GOLD_COT_2023_2025_OFFICIAL_PUBLISH_VS_LEGACY_CLOCK_AUDIT_20261014.csv): **128/157** eski/yeninin erişilebilir zaman damgası değişiyor, **29 aynı**. Bunların **125'i kural bazlı normal cuma 15:30 ET, 7'si CFTC 2023 ION özel duyurusu, 13'ü CFTC 9 Aralık 2025 revize resmî arka-log takvimi, 1'i CFTC 2025 Ocak ulusal yas, 1'i CFTC 2026 Ocak 5 tatil takvimi** ve **10'u tarihsel gün bazında ayrıca teyit edilemeyen tatil haftası** (önceki geç muhafazakâr tarih saklandı). **125 normal gün tarihi kamuya açık tarihsel tekil yayım kaydıyla bağımsız ispatlanmış değildir: CFTC'nin resmî genel cuma kuralından türetilmiştir.**
- **Örnek:** 16 Eylül 2025 salı tarihli pozisyon verisi 19 Eylül cuma saat 15:30 New York'ta normal yayımlanmış olmalı; eski kaynak ise 23 Eylül Salı erişimi kabul ediyordu. Bu, retrospektif nokta-zaman eşleşmesinde yanlış gecikmeye yol açar.

## 3. CFTC istisnaları, resmî takvim
### 2023 ION siber olayı (farklı tarihlerde yayımlanma)
| Pozisyon ölçüm tarihi | Resmî geç yayın tarihi |
|---|---|
| 31 Ocak 2023 | 24 Şubat 2023 |
| 7 Şubat 2023 | 3 Mart 2023 |
| 14 Şubat 2023 | 8 Mart 2023 |
| 21 Şubat 2023 | 10 Mart 2023 |
| 28 Şubat 2023 | 14 Mart 2023 |
| 7 Mart 2023 | 16 Mart 2023 |
| 14 Mart 2023 | 21 Mart 2023 |

Resmî CFTC tarihçesi: https://www.cftc.gov/MarketReports/CommitmentsofTraders/HistoricalSpecialAnnouncements/index.htm ; ilk gecikme açıklaması: https://www.cftc.gov/PressRoom/PressReleases/8662-23 .

### 2025 federal hükümet kapanması ve revize yayımlar
| Pozisyon tarihi | Resmî güncellenmiş yayın tarihi |
|---|---|
| 30 Eylül 2025 | 19 Kasım 2025 |
| 7 Ekim 2025 | 21 Kasım 2025 |
| 14 Ekim 2025 | 25 Kasım 2025 |
| 21 Ekim 2025 | 2 Aralık 2025 |
| 28 Ekim 2025 | 5 Aralık 2025 |
| 4 Kasım 2025 | 9 Aralık 2025 |
| 10 Kasım 2025 | 10 Aralık 2025 |
| 18 Kasım 2025 | 12 Aralık 2025 |
| 25 Kasım 2025 | 15 Aralık 2025 |
| 2 Aralık 2025 | 17 Aralık 2025 |
| 9 Aralık 2025 | 19 Aralık 2025 |
| 16 Aralık 2025 | 23 Aralık 2025 |
| 23 Aralık 2025 | 29 Aralık 2025 |

Arka-log yayın tablosunun **9 Aralık revizyonu**, 18 Kasım ilk duyurusunun sonraki 2025 Aralık tarihlerine üstün gelir. Ayrıca **7 Ocak 2025 ölçümü** Carter ulusal yas günü nedeniyle **13 Ocak Pazartesi** yayımlandı; **30 Aralık 2025 ölçümü** CFTC 2026 takviminde **5 Ocak 2026 Pazartesi** yayınlı görünüyor. Kaynaklar: https://www.cftc.gov/PressRoom/PressReleases/9147-25 ; https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm .

## 4. 154 haftalık COT–altın olay eşleştirmesi, düzeltilmiş kaynak günü
Yeni 157 takvim revizyonu, önceki [154 haftalık altın/metaller paneline](GOLD_COT_METAL_WEEKLY_ORIGIN_2023_2025_NY17_PIT_RESEARCH_20261014.csv) uygulandı. Her origin için **günün 20:00 UTC'sine kadar gerçekten yayımlanmış** en son COT pozisyonunu seçtik (NY17 kapanışından da önce). Şok etiketi, gümüş/platin/paladyum değerleri ve NY17 altın fiyatı **değiştirilmedi**. **154 origin'den 123'ünde hangi COT raporunun seçildiği değişti**: 2023 39/50; 2024 48/53; 2025 36/51. 2022 Aralık önceki verisi ayrıca resmî saatle denetlenmedi ve etiketlendi.

### Düzeltilmiş değerlerle ilk örnek karşılaştırma (sabit eski 2023–24 Q75 pozisyon eşiği = 0.3065900336)
| İlişki | Geliştirme 2023–2024 | Test 2025 |
|---|---:|---:|
| Yüksek futures managed money → yeni DOWN V2 ilk bayrağı | 6/28 = %21,4 | 2/21 = %9,5 |
| Diğer futures managed money → yeni DOWN V2 ilk bayrağı | 7/75 = %9,3 | 6/30 = %20,0 |
| Futures+Options combined MM değişimi pozitif → DOWN V2 | 7/46 = %15,2 | 5/15 = %33,3 |
| Diğer MM değişimi → DOWN V2 | 6/57 = %10,5 | 3/36 = %8,3 |
| Pozitif futures+options combined MM değişimi → UP veya DOWN herhangi yeni V2 başlangıcı | 15/46 = %32,6 | 12/15 = %80,0 |
| Diğer MM değişimi → herhangi yeni V2 başlangıcı | 12/57 = %21,1 | 11/36 = %30,6 |

**İstatistiksel kapı:** 2025 herhangi yeni V2 olayı × pozitif combined-MM değişimi Fisher iki taraflı p≈0.001833; DOWN için p≈0.038998. Ancak bunlar COT takvimi düzeltmesinden **sonra elde edilen keşifsel ve çoklu tarama sonrası** değerlerdir. 2023–2024'te aynı gözlem belirgin değildir (herhangi şok için p≈0.259789); zaman zaman çakışan olaylar, 2025 rejimi, kısmi resmî teyidi olmayan tatil haftaları ve tekrar test/hipotez seçimi nedeniyle **kanıtlanmış mekanizma, güvenilir tahmin yeteneği veya canlı sinyal değildir**. Tüm 36 hipotezin corrected-clock istatistikleri henüz yeniden çalıştırılmadı, yalnız sabit ana COT adayları tekrar karşılaştırıldı.

**COT veri yaşlanması:** 2025 51 origin'in 10'unda en güncel COT raporunun pozisyon yaşı >14 gün; 14 günlük filtrede 41 origin kalıyor. Pozitif combined-MM değişimi ve sonraki herhangi V2 başlangıcı burada **12/14** vs **6/27**; Ekim–Aralık kapanma dönemini tamamen çıkartınca **11/13** vs **6/26**. Bu sonuçlar örneklem/mekanizma onayı değildir, ayrıca bağımsız tam faktör kontrolleri ve olayların yayın ilk baskı vektörü gereklidir.

### Kanıt artefaktları
- [157 satır CFTC yayın günü + kaynak seviyesi](GOLD_COT_2023_2025_OFFICIAL_PUBLISH_VS_LEGACY_CLOCK_AUDIT_20261014.csv)
- [154 corrected-first-PIT hafta](GOLD_COT_154_WEEKLY_NY17_CORRECTED_PUBLISH_CLOCK_RETEST_20261014.csv)
- [Düzeltilmiş haftalar sabit COT hipotez sayımları](GOLD_COT_FRIDAY_CLOCK_CORRECTED_HYPOTHESES_20261014.csv)
- [14 günlük staleness ve shutdown çıkarması](GOLD_COT_FRIDAY_CLOCK_AGE_SHUTDOWN_SENSITIVITY_20261014.csv)

## 5. Araştırma hükmü / authority
`COT_REPORT_DATE_IS_TUESDAY_POSITION_ASOF_NOT_PUBLICATION_DATE` — `DEFAULT_PLUS7D_TUESDAY_CLOCK_UNDERSTATES_KNOWN_FRIDAY_PUBLICATION` — `OFFICIAL_2023_ION_AND_2025_SHUTDOWN_MAP_SUPERSEDES_GENERIC_FRIDAY` — `OLD_COT_154_WEEKLY_ASSOCIATIONS_SUPERSEDED_FOR_COT_TIMING` — `125_NORMAL_WEEKS_RULE_BASED_PROVISIONAL_AND_10_HOLIDAY_WEEKS_UNVERIFIED` — `NO_PROVEN_CAUSALITY_OR_TRADING_SIGNAL`.

**Yüksek öncelikli kalan doğrulama:** 2023–25 tüm resmî tatil istisnalarını CFTC tarihsel takvim arşivinden tek tek tamamlama; yalnızca yayımlanan anın doğrulandığı COT kesitleriyle yeni negatif kontroller; CFTC `fut_mm_*` vs `opt_mm_*` kaynak kalemi/normalize payda sözleşmesini sabitleme; 2025 mekanizmalarını haber ve metal ilk fiyat tepki zamanı üzerinden test etme.
