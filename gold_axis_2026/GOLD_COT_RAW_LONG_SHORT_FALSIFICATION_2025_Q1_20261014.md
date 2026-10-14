# GOLD COT — Orijinal CFTC net long/short ve payda yanlışlama denetimi
**14 Ekim 2026 · Geriye dönük ekonomik neden–sonuç araştırması · RESEARCH ONLY / NO TRADING**

## Yönetici hükmü

Önceki 2025 "managed-money reconstructed option-equivalent residual yükseldiği hafta sonra büyük hareket" ilişkisinin **en az üç mekanizması birbirinden ayrıştırıldı**: gerçek futures-only net pozisyon değişimi, combined net pozisyon değişimi ve combined open interest paydasındaki değişim. Orijinal CFTC GOLD COMEX (contract code **088691**) haftalık **Disaggregated Futures Only** ve **Disaggregated Futures & Options Combined** raporlarından 25 Şubat, 4 Mart, 18 Mart, 25 Mart, 1 Nisan, 8 Nisan 2025 altı tarihli veri çıkarıldı ve arşivdeki `opt_mm_net`, `d_opt_mm_net` düzeyiyle **dört ardışık rapor geçişi için 0 mutlak yuvarlamasız farkla** yeniden üretildi. 25 Şubat futures-only LONG/SHORT değeri 4 Mart raporunun haftalık değişim satırından geriye çözüldü; diğer 5 tarih doğrudan orijinal rapor satırından.

**Önemli yanlışlama:** Pozitif `d_opt_mm_net` **futures+options toplam managed-money net long pozisyonunun arttığı anlamına gelmez**. Örneğin 25 Mart–1 Nisan 2025: futures-only net long **−32.733 kontrat**, combined net long **−16.134 kontrat**, combined-minus-futures **opsiyon eşdeğeri net fark +16.599 kontrat**; futures-only short pozisyonu **+24.061 kontrat**. Yani yüksek `d_opt_mm_net`, fiyat yönüne yönelik "spekülatörler daha fazla altın satın aldı" iddiasına **karşı örnektir**. 1 Nisan futures-only + combined rakamları CFTC birincil kaynaktan doğrulandı.

## Kaynak ham raporları (CFTC GOLD COMEX 088691)

Tarih | Futures-only OI | Futures MM long | Futures MM short | Futures net | Combined OI | Combined MM long | Combined MM short | Combined net | Residual net `N_t` | Residual/`OI_comb`
---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:
25 Şubat 2025 | (bağımsız okunmadı) | 212.694* | 32.882* | 179.812* | 773.047 | 223.455 | 29.098 | 194.357 | 14.545 | 0,01881516
4 Mart 2025 | 489.270 | 204.965 | 38.307 | 166.658 | 756.299 | 217.056 | 34.492 | 182.564 | 15.906 | 0,02103136
18 Mart 2025 | 533.566 | 220.879 | 37.045 | 183.834 | 870.033 | 235.409 | 35.252 | 200.157 | 16.323 | 0,01876136
25 Mart 2025 | 511.482 | 213.505 | 38.773 | 174.732 | 826.602 | 226.705 | 34.018 | 192.687 | 17.955 | 0,02172146
1 Nisan 2025 | 498.746 | 204.833 | 62.834 | 141.999 | 851.437 | 216.348 | 39.795 | 176.553 | 34.554 | 0,04058316
8 Nisan 2025 | 445.468 | 175.393 | 44.407 | 130.986 | 775.736 | 181.033 | 42.568 | 138.465 | 7.479 | 0,00964117

*25 Şubat futures ONLY değerleri 4 Mart `Changes from Feb 25` resmi satırından geriye hesaplandı; 25 Şubat combined rakamları o haftanın orijinal CFTC sayfasından doğrudan okundu. 11 Mart haftası araştırmaya dahil edilmedi, dolayısıyla **4 Mart–18 Mart farkı tek haftalık veri veya `d_opt` olarak okunamaz**.

Resmî futures-only: https://www.cftc.gov/sites/default/files/files/dea/cotarchives/2025/futures/other_sf030425.htm ; https://www.cftc.gov/sites/default/files/files/dea/cotarchives/2025/futures/other_sf031825.htm ; https://www.cftc.gov/sites/default/files/files/dea/cotarchives/2025/futures/other_sf032525.htm ; https://www.cftc.gov/sites/default/files/files/dea/cotarchives/2025/futures/other_sf040125.htm ; https://www.cftc.gov/sites/default/files/files/dea/cotarchives/2025/futures/other_sf040825.htm

Resmî futures+options combined: https://www.cftc.gov/sites/default/files/files/dea/cotarchives/2025/options/other_sof022525.htm ; https://www.cftc.gov/sites/default/files/files/dea/cotarchives/2025/options/other_sof030425.htm ; https://www.cftc.gov/sites/default/files/files/dea/cotarchives/2025/options/other_sof031825.htm ; https://www.cftc.gov/sites/default/files/files/dea/cotarchives/2025/options/other_sof032525.htm ; https://www.cftc.gov/sites/default/files/files/dea/cotarchives/2025/options/other_sof040125.htm ; https://www.cftc.gov/sites/default/files/files/dea/cotarchives/2025/options/other_sof040825.htm

## 1. Normalizasyonun analitik ayrıştırması

\[
 F_t=MM\,Long^{Futures}_t-MM\,Short^{Futures}_t,\quad C_t=MM\,Long^{Combined}_t-MM\,Short^{Combined}_t
\]
\[
 N_t=C_t-F_t,\qquad O_t=N_t/OI^{Combined}_t,\qquad \Delta O_t=O_t-O_{t-1}
\]
Tam özdeşlik:
\[
 \Delta O_t = \frac{N_t-N_{t-1}}{OI^{Combined}_{t-1}} + N_t \left(\frac{1}{OI^{Combined}_t}-\frac{1}{OI^{Combined}_{t-1}}\right).
\]

| Geçiş | Ham residual net değişimi | \(\Delta O_t\) | Numeratör katkısı | Payda/OI katkısı | Doğrulama |
|---|---:|---:|---:|---:|---|
| 25 Şub → 4 Mar | +1.361 | +0,00221621 | +0,00176057 | +0,00045564 | Depo birebir |
| 18 Mar → 25 Mar | +1.632 | +0,00296010 | +0,00187579 | +0,00108431 | Depo birebir |
| 25 Mar → 1 Nis | **+16.599** | **+0,01886170** | **+0,02008101** | −0,00121931 | Depo birebir |
| 1 Nis → 8 Nis | **−27.075** | **−0,03094199** | −0,03179918 | +0,00085719 | Depo birebir |

**Yanlışlama sonucu:** Yalnız OI paydasının değişimi 4 Mart / 25 Mart küçük pozitif farkın sırasıyla ~%20,6 / ~%36,6'sını oluşturuyor; fakat 1 Nisan büyük pozitif değişimde payda **ters işaretli** olduğundan arttırıcı mekanizma *gerçek, ham N net eşdeğer fark değişimi*. Ancak bu ham `N` seçeneklerin alım hacmi veya pozisyon transferi değildir. Birleşik tablodaki opsiyon pozisyonları delta futures-equivalent ile ölçülür; fiyatın değişmesi delta yüzünden raporu etkileyebilir. **CFTC yalnız bu agregalardan kim, ne zaman, neden pozisyon aldı göstermez.**

## 2. Zamanlama / nedensellik kontrolü

1 Nisan 2025 pozisyon değişimi **salı rapor ölçüm tarihinde** mevcuttur fakat kamuya normalde **4 Nisan Cuma 15:30 New York** tarihinde açıklanmıştır. **2 Nisan tarife ilanı sonrasında çıkan** rapor, 2 Nisan sonrası ilk dalganın kamuca okunmuş öncül sinyali olamaz; pozisyonlanan kurumlar ölçüm gününde kendi pozisyonlarını bilir. 7 Nisan NY17 araştırma kökeni açısından 4 Nisan yayını biliniyor olabilir, dolayısıyla **sonraki toparlanmayla eş-hareket** ileri-zaman sızıntısı değildir. Bu kronolojik uygunluk, raporun fiyatı başlattığının nedensel ispatı değildir.

## 3. Aynı fikrin farklı dönem / negatif kontrollerde performansı

Veri: 154 hafta, 103 DEV (2023–24), 51 2025, corrected CFTC Friday/as-of, 774 valid NY17 XAU seansı. `ΔO>0` sabit işaret. Aşağıdaki geçmiş ve gelecek fiyat yolları NY17 gün sonu ekseninde, her kökenden beş uygun seans. Geçmiş bariyer, origin'den geriye doğru kümülatif pozitif/negatif hareketin %3 sınırını aşması; gelecekteki bariyer ayrı ileri fiyat yolu.

| Ölçüm | DEV: residual artış (+ / n) | DEV: diğer | 2025: residual artış (+ / n) | 2025: diğer |
|---|---:|---:|---:|---:|
| **Önceki beş seansta %3 fiyat bariyeri** | 7/46 (%15,2) | 8/57 (%14,0) | 7/15 (%46,7) | 11/36 (%30,6) |
| **İzleyen beş seansta %3 fiyat bariyeri** | 8/46 (%17,4) | 8/57 (%14,0) | **9/15 (%60,0)** | **9/36 (%25,0)** |
| **Gelecek beşinci seans mutlak %3 kapanış** | 5/46 (%10,9) | 7/57 (%12,3) | 7/15 (%46,7) | 7/36 (%19,4) |
| **Yeni V2 ilk küme bayrağı** | 15/46 (%32,6) | 12/57 (%21,1) | 12/15 (%80,0) | 11/36 (%30,6) |

**Negatif kontrol yorumu:** `ΔO>0` 2025'te sadece gelecek şoklarla değil, geçmişteki yüksek volatiliteyle de birlikte. Bu durum pozisyonların fiyat şokuna tepki olarak değişmesi veya rejim etkisiyle uyumludur; gelecek ilişkisini tek başına iptal etmez, ama nedensel atıf için güçlü karşıt hipotez sağlar. DEV'de gelecek fiyat bariyeri ayrımı neredeyse sıfırdır. 2025 Q1 hariç tutulunca gelecek fiyat bariyeri **5/11 vs 8/27** (Fisher iki taraflı p≈0,457). Sinyali yalnızca **2025 özellikle Q1** için geçici aday tut; 2026 doğrulama yapılmadan genel özellik dememeliyiz.

2025'te `ΔO>0, ΔF<=0` **7/7 V2 yeni bayrak**; 2023–24 **6/16**. Bu fiyat yönü veya %3 fiyat bariyeri için 7/7 değil; yalnızca cluster başlangıç etiketidir. Ayrıca 14 Nisan 2025 hafta başlangıcında V2 bayrağı yokken sonraki 5 NY17 seans kapanış getirisi **+%5,291**. Fiyat yolunu V2 küme yöntemiyle karıştırma.

İlgili dosyalar:
- [Orijinal CFTC GOLD uzun/kısa ve combined OI yeniden üretimi](GOLD_CFTC_2025_6_ORIGINAL_WEEKLY_MM_FUTURES_OPTIONS_RESIDUAL_DECOMPOSITION_20261014.csv)
- [Geçmiş ve gelecek 5 NY17 seans negatif kontrol (154 satır)](GOLD_COT_PAST_VS_FUTURE_5SESS_PRICEMOVE_NEGATIVE_CONTROL_20261014.csv)
- [COT, options-futures, CPI/NFP/FOMC, altın fiyat ve V2 karşılaştırmaları](GOLD_COT_OPTIONS_RESIDUAL_FUTURES_CROSSCHANNEL_154_WEEKLY_WITH_MACRO_CONTROLS_20261014.csv)
- [Resmî COT yayın saati otoritesi](GOLD_COT_PUBLICATION_CLOCK_OFFICIAL_AUDIT_AND_RETROSPECTIVE_154_ORIGIN_RETEST_20261014.md)

## 4. İstatistiksel ve epistemik sonuç

**Desteklenen:** (i) `opt_mm_net` depo formülü ve delta COT raporları 4 geçişte ham kaynaktan yeniden üretildi; (ii) bazı risk rejimlerinde managed-money Futures Only vs Combined hareketi sert biçimde farklılaşır; (iii) büyük farkın yalnız payda değişiminden ibaret olmadığı pozisyon örneği doğrulandı; (iv) 2025 geçmiş-yüksek hareket ilişkisi endojen fiyat/pozisyon tepkisi ihtimalini gösterdi.

**Desteklenmeyen:** Genel 2023–25'te güvenilir artan şok kuralı, yalnız futures long/short'a bakıp opsiyon piyasasına kesin alım/satım nedeni atfı, 2 Nisan ilk fiyat düşüşünü **4 Nisan yayımlanan COT raporuna** bağlama, COT açıklama saatinde bağımsız fiyat tepkisi doğrulanmadan raporun şoku tetiklediği iddiası. Çoklu test/hindsight seçimi, Δ'nın fiyatla beraber endojen oluşması, arşivlenen 2026 metal fiyatlarının PIT olmaması sınırlamaları devam ediyor.

**Sonraki gerçek doğrulama:** CFTC 2023–2025 tüm 156 hafta için futures-only/combined OI ve long/short'u tekil haftalık HTML veya resmî toplu yıllık arşivden eksiksiz getir; `N_t` ham sayıda ve `OI` payda etkisini her hafta ayır; baştan sabit negatif kontrollerle tüm üç yılda fiyat yolu / makro açıklamalarla eşleştir. Tarih ve yön performansı değil **mekanizma kanıtı** öncelik. Resmî yıllık arşiv: https://www.cftc.gov/MarketReports/CommitmentsofTraders/HistoricalCompressed/index.htm . Bu çalışmada 6 ham rapor tarihi alınabildi; yıllık ZIP dosyaları bağlı yürütme ortamına indirilemedi, 156 haftanın tümünün ham doğrulandığı iddia edilmez.

**STATUS: RAW_CFTC_ANCHORS_REPRODUCED / DENOMINATOR_NOT_SUFFICIENT / FUTURES_SHORT_BUILD_2025_APR01 / PRIOR_PRICE_PLACEBO_NONZERO / CROSS_YEAR_NO_REPLICATION / NO_CAUSAL_PROMOTION.**
