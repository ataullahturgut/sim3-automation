# V31 — Ekonomik Olay ve Yeniden Fiyatlama Katmanı | Gerçek Kod, 108 Olay, Haziran 2026 Kontrolü

**27 Ekim 2026 — Gold Control — yalnızca araştırma dalı.**

## Sonuç / statü

**Kod yazıldı ve gerçek veri üzerinde çalıştırıldı.** V31 yeni, bağımsız `EVENT_PENDING` (önceden *kanıtlanmış* takvim), `PRIOR_MACRO_CONTEXT`, `POST_RELEASE_WAIT`, `EVENT_REPRICING_RESEARCH_REVIEW` ve `ABSTAIN` bilgi katmanıdır. **BASE14, CFTC21 ve V22’nin hiçbir ağırlığı, eşiği, eğitimi veya alarmı değiştirilmedi. Otomatik SAT/AL üretmez.** Kod üretime deploy edilmedi, Neon'a yazı yazılmadı.

İki gerçek uygulama dosyası:
- `risk_v31_macro_event_layer.py`: 108 resmi veri zamanı + XAU 5m event-time replay; ilk görünme as-of saati denetimi.
- `risk_v31_prior_jolts_adp_context.py`: 2 ve 3 Haziran 2026'da NFP'den önce yayımlanan JOLTS ve ADP'nin sınırlı, kaynak-damgalı bağlamı.
İki bağımsız test: `test_risk_v31_macro_event_layer.py` ve `test_risk_v31_prior_jolts_adp_context.py`.

## Bağlı veri kaynakları ve tutarlılık

Neon Gold Control'a **SELECT-only**:
- `public.observations`: 2023–2026 tarihli NFP actual firstprint reconstruction + forecast consensus, headline/core CPI actual/consensus, FOMC V3 event-score timestamp. **108 tarihi olay** = 44 NFP + 43 CPI + 21 FOMC.
- `public.xau_intraday_research_cache_5m`: gerçek fiyat barları 2020–2026; provider **Twelve Data**, XAU/USD, arşiv toplama **2026-09-08**, `evidence_class=HISTORICAL_RESEARCH_RETRIEVAL`. 108 olaydan 103'ünde pre5/post15/post30 fiyatı var; 5 eksik örnekte sonuç `ABSTAIN_MISSING_5MIN_BARS`. **2023–2026 olaylarındaki 5m fiyatların ilk yayın vintageları bu arşivden kanıtlanamaz.**
- Konsensüs serilerinde `provider_exact_pre_release_update_timestamp_proven=false`; `available_as_of` değeri yayın saatine eşit diye yayın öncesi kesin biliniyordu kabul edilemez. Bu nedenle hiçbir tarihsel olaya canlı onay verilmedi. **Kaynak kullanım şartlarına uyarak ham Investing.com konsensüs arşivi CSV olarak GitHub'da yeniden yayımlanmadı; yalnız türetilmiş işaretler ve olay dönüşümleri gösterildi.**

## Metodoloji

1. **Eğitim referansı:** yalnız **2023–2024** fiyat tepkilerinin, her olay türü için ilk 30 dakika XAU getirisinin 10. yüzdelik dilimi. Sabit çıktı:
   - NFP: **−%0,99341445**, 23 gözlenebilir referans olay.
   - CPI: **−%0,461499928**, 23 olay.
   - FOMC: **−%0,384683918**, 15 olay.
   Eşikler 2025 ve 2026 kullanılarak seçilmedi, orijinal modellerin parametresi değildir.
2. **2025** yalnız değerlendirme, **2026** keşfi önceden bilinen tarihsel stres dönemi. Ne 2025 sonuçlarına göre yeniden kalibrasyon ne de 5 Haziran 2026 için özel eşik ayarı yapıldı.
3. **Saat kontratı:** 08:30 EDT veri yayınında 15:30 TR; 5m bar timestamp konvansiyonundan dolayı 30m tepki ancak +35 dakikada (16:05 TR) temkinli biçimde erişilebilir kabul edildi. Yayın öncesi 30m fiyat ve gerçekleşen/consensus sürprizi görünmez. `EVENT_PENDING` yalnızca gerçekten yayın öncesi arşivlenmiş ve yetkili resmî BLS/Fed URL'li takvim belgesi varsa açılır; eski 2026 tarih listesiyle üretilen `PENDING_UNVERIFIED_CALENDAR` yalnız araştırma.
4. 30m XAU hareketi tarihsel eşikten daha negatif olduğunda yalnız `EVENT_REPRICING_RESEARCH_REVIEW` üretilir; piyasadaki düşüş gözlendikten sonra. DXY, 2Y UST, petrolün aynı dakikalı firstprint kaynakları verilmediği için `INTRADAY_MACRO_CONFIRMATION=NOT_FOUND`. **Faizlerin neden olduğunu canlıda kanıtlayan çok varlıklı sinyal üretilmedi.**
5. **Saat kısıtı:** Türkiye bankasında işlem saatleri esas alınır; 17:00 sonrası FOMC sinyalleri `OUTSIDE_BANK_WINDOW`. İçinde olanlar dahi burada *otomatik SAT* anlamına gelmez.
6. Gerçek yayın anı, fiyat barının gerçek ilk alınma saati ve konsensüsün yayın öncesi sürümü as-of kanıtlanmazsa **LIVE_PROMOTION_BLOCKED**.

## Gerçek Haziran 2026 sonucu

| Tarih / saati (TR) | Katman | Olay | Sonuç | Karar niteliği |
|---|---|---|---|---|
| 02.06 17:33 | JOLTS bağlam | Nisan açık iş 7,618m; beklenti 6,88m, işe alımlar −419k | İşgücü gücü ile işe alım zayıflığı karışık | **Bağlam**, SAT değil |
| 03.06 15:31 | ADP bağlam | Mayıs ADP 122k, beklenti 117k | +5k küçük olumlu sürpriz | **Bağlam**, NFP tahmini değil |
| 04.06 16:45 | Ön bağlam | Yukarıdaki iki kaynak NFP'den önce var | `PENDING_UNVERIFIED_CALENDAR` | Şokun yönü henüz bilinmiyor |
| **05.06 15:30** | NFP yayımlandı | 172k, konsensüs 85k: +87k | `AWAIT_REACTION_30M_BAR` | Henüz reaksiyon skoru yok |
| **05.06 16:05** | XAU tepki | Altın 30 dakikada **−%1,20719** | **`EVENT_REPRICING_RESEARCH_REVIEW`**, NFP eşiği −%0,99341 aşıldı | Yalnız geriye dönük test; canlı kesin alarm değil |
| 10.06 16:05 | CPI | Manşet CPI %+0,5 vs %+0,5; XAU ilk 30m **+%0,39590** | `NO_RARE_ADVERSE_REACTION` | Beklenmedik kötü CPI gibi gösterilmez |
| 17.06 21:35 | FOMC | XAU ilk 30m **−%2,17337** | `EVENT_REPRICING_RESEARCH_REVIEW` | **Bankada işlem zamanı dışında** |

JOLTS resmi: https://www.bls.gov/news.release/archives/jolts_06022026.htm  
JOLTS yayın sonrası Reuters konsensüsü: https://ca.marketscreener.com/news/us-job-openings-jump-to-near-two-year-high-in-april-ce7f5ddedd8bf621  
ADP birincil: https://mediacenter.adp.com/2026-06-03-ADP-National-Employment-Report-Private-Sector-Employment-Increased-by-122%2C000-Jobs-in-May-Annual-Pay-was-Up-4-4  
ADP piyasa konsensüsü: https://www.investing.com/news/economy-news/us-private-payrolls-increase-in-may-adp-says-4724242  
BLS NFP: https://www.bls.gov/news.release/archives/empsit_06052026.htm  
BLS CPI: https://www.bls.gov/news.release/archives/cpi_06102026.htm

**Önemli mantıksal ayrım:** 4 Haziran fiyat zirvesinden **önce satış alarmı yakalandı demiyoruz.** Bu katman 4 Haziran'da yalnız yaklaşan olay ve karışık istihdam öncülleri gösterebilir; **5 Haziran 16:05'te, şokun başlamasından sonra, ama Türkiye saati 17:00 kısıtından önce** altındaki olağan dışı aşağı hareketi teşhis eder. V30'da eski BASE14/CFTC21/V22 günlük modeller **4 Haziran NORMAL**, ancak **5 Haziran günü bittikten sonra BASE14 RED** idi. Günlük RED'i 15:30 ya da 16:05 anında mevcutmuş gibi okumak yasaktır.

## 2023–2025 kontrol sonuçları

- 2023/2024 toplam 64 kaynak olayı, 61 tam 5m tepkisi; olay türüne göre 30m alt yüzde 10 eşiği sabitlendi.
- 2025: NFP **0/11**; CPI **0/10** tarihsel 30m ağır negatif uç eşik ihlali. **2025 FOMC kayıtları bu kaynak kümesinde 0: NOT_FOUND.** Bu yüzden `2025 FOMC doğrulandı` iddiası yanlış; daha geniş FOMC geçmişi tamamlama gerekli.
- 2026: NFP 1/9, CPI 0/9, FOMC 2/5 ağır negatif 30m gözlem; bunların 2'sinde (NFP/CPI) 5m bar tam değil; bu günler **ABSTAIN** olarak korunur. Bu frekanslar **büyük gelecek düşüş yakalama/yanlış alarm başarı ölçüsü DEĞİLDİR**. Yalnız *olay sonrası 30m negatif tepki sıklığıdır*. Olay öncesi tahmin gücü kanıtlanmadı.

## Operasyonel ayrım ve sonraki entegrasyon sınırı

V31 mevcut risk modellerinin yanındaki **bağımsız olay-zaman bilgi kanalıdır**. Şu an yalnız araştırma katmanı olarak kod ve çıktıları vardır; uygulama menüsüne, canlı işlem sistemine, Neon model registry'ye veya otomatik alarmlara bağlanmamıştır.

Canlı kullanılabilir duruma geçmek için kaynak-zamanlı:
- BLS resmî NFP/CPI takvimi, Fed FOMC resmi takvimini **olay öncesi gerçek indirme zamanıyla** saklayan scheduler ve değişiklik denetimi.
- NFP/CPI ön-konsensüsünü timestamp ile yakalayan izinli provider; release firstprint logu.
- Öncesi/sonrası gerçek zamanlı altın 5m barları, ilk teslim edilen timestamp, bar-start / bar-close sözleşmesi.
- DXY / 2 yıllık tahvil / 10 yıllık reel faiz / petrol ve isteğe bağlı gümüş tepkileri eş zamanlı farklı kaynaklar; alınamayanlar `NOT_FOUND` ve sonuç çok varlıklı olarak sertifikalanamaz.
- 2023–2025 tamamlanmış haber + saat + fiyat tarihi ve yalnız gelecek olaylarda bağımsız forward/false-positive testi, izinli lisans, çok-bacaklı ekonomik düşüş aileleri.

**Güvence:** Hiçbir 2026 girdi, 2023–24 eşiklerini değiştiremez; Y gizli, pre-release fiyat reaksiyonu gizli, NaN/missing fiyat `ABSTAIN`, tarihsiz consensus live kapıdan geçemez. V31 orijinal RED’i ne değiştirebilir ne kapatabilir.

## Somut kanıt

- Başarılı GitHub Actions: https://github.com/ataullahturgut/sim3-automation/actions/runs/40498015603 — **14/14 test geçti**.
- `outputs/v31_macro_event_research_2023_2026_108_events.csv` — 108 olay kaynak-zamanı ve araştırma fiyat tepki inputu.
- `outputs/v31_june2026_nfp_cpi_fomc_outputs_COMMITTED.csv` — üç Haziran olayının gerçek çalıştırma sonucu.
- `outputs/v31_macro_events_by_year_metrics_COMMITTED.csv` — olay frekansı ve missing bars, 2023–2026.
- `outputs/v31_june_before_NFP_JOLTS_ADP_evidence.csv` — 2 ve 3 Haziran yayımlanmış ön bağlam kaynakları.
- `outputs/v31_june2026_macro_layer_event_timeline_COMMITTED.csv` — olay/tepki/operasyon zaman akışı.
- GitHub Actions artifact 90 gün: `v31_historical_macro_overlay_all_108_events.csv`, `v31_june2026_known_prior_release_context.json`, `v31_macro_event_layer_manifest.json`.

**Durum:** Research implementation + historic execution **COMPLETE**; prospective firstprint data and app deployment **BLOCKED**, not silently treated as done.
