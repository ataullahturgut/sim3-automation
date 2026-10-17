# Ocak 2023 — EKONOMİK ORG hipotezleri + S1/S2/S3 GERÇEK günlük CORE denetimi

**Proje:** GOLD-ADAPTIVE-MODEL-APP-01 | **Kod:** mevcut tek `adaptive_market_core_s1_s2.js` | **Çalışma:** 17 Ekim 2026 | **GitHub Actions:** [Başarılı tekrarlanabilir koşu](https://github.com/ataullahturgut/sim3-automation/actions/runs/39044090856)

**Sözleşme:** Ekim–Aralık 2022, **5865 gerçek M15** barı üzerinde ön-öğrenim, Ocak 2023 **1920 gerçek M15** barı üzerinden kronolojik model değerlendirmesi. Tek EV/Dukascopy-türev MID kaynağı, veri kaynağı değişmedi. Tarih NY17 uyumlu 22:00-UTC oturum etiketidir; zorunlu BANKA SAATİ YOK. Günlük S1/S2 ölçümleri **oturum sonuna aittir**; aynı satırdaki seans getirisi **o oturumun geçmişte gerçekleşmiş ilk–son fiyat hareketidir**. O seans getirisini gün sonu tahmininin isabeti gibi puanlama. Girdi veri arşivinin asıl 2023 tarihli erişim kanıtı yoktur.

**Ön eğitim S1:** 3 öğrenilmiş **piyasa** prototipi, 357 anchor, 344 olgun dört-saatlik sonuç. Bunlar ÖĞREN-03 ekonomik mekanizma kuralı olarak yorumlanamaz. Ocak ayı sonunda 5 piyasa prototipi, 443 olgun sonuç; **ekonomik mekanizma doğrulanması = 0**. Gün sonu dört saatlik UP olasılık aralığı %51.76–%54.50; dört saatlik beklenen log hareket %0,01–%0,03 civarı, AL+SAT toplam yaklaşık %1,59 maliyeti aşan güvenilir ekonomik avantaja dönüşmedi.

**S2:** Kısa S2 hareket evresi gün gün hesaplandı. Dört saatlik `hazard4h` **yalnız S2'nin dört saatlik kural ankrajında** üretildiğinden 22:00 UTC gün-sonu kıyas anlarının hepsinde `READY` değildi; bunu tüm S2 boyunca hiç öğrenme yoktu şeklinde yorumlama. Kısa S2'nin 2023 dört-saatlik olgun Brier'i 0.21293, bağımsız olmayan baz kıyası 0.21042; **üstünlük gösterilemedi**. S2 SLOW: 82 tamamlanmış kabul oturumu, 3 reddedilen, **1 tamamlanmış uzun epizot**; 1/3/5/10 seans için olgun/kalibre bitiş olasılığı **henüz yok**. 2022-10 başlanmasına rağmen günlük SLOW `WARMUP/UNREADY` sık; daha fazla seans almak evre ayırmayı otomatik doğrulamaz.

**S3:** `CONDITIONAL_ECONOMIC_RESEARCH` kipinde bütün gün sonlarında **KEEP CASH**; `action=null, tradeAllowed=false`, `shadowEnabled=false`; bunlar canlı banka işlemi veya kâr değildir. Ekonomik olay kararı desteklenmediyse "NO_SUPPORTED_CONDITIONAL_NET_ADVANTAGE"; olay yoksa "NO_SUPPORTED_MARKET_NET_ADVANTAGE". Günlük ORG hipotezleri başlık/OLAY-02 kaynaklarından araştırmacı eşleştirmesidir, S1 tarafından öğrenilmiş kanıtlı ekonomik ORG etiketi **değildir**.

## Her günün çıktısı

| Tarih (NY17) | Ekonomik hipotez (henüz öğrenilmiş AL/SAT değil) | S1 P(UP, +4h) | S1 E[log%, +4h] | S2 hızlı evre / yön | S2 trend z | S3 araştırma | Gerçek seans ilk-son MID % |
|---|---|---:|---:|---|---:|---|---:|
| 2023-01-01 | YOK | — | — | — / — | — | — | — |
| 2023-01-02 | YOK | — | — | — / — | — | — | — |
| 2023-01-03 | YOK | 52.06% | 0.016% | CONTINUE / UP | 0.01 | KEEP | 0.669% |
| 2023-01-04 | G01-mixed | 52.53% | 0.017% | NEUTRAL / — | 0.73 | KEEP | 0.868% |
| 2023-01-05 | ORG02? | 52.34% | 0.010% | NEUTRAL / — | -0.21 | KEEP | -1.204% |
| 2023-01-06 | ORG01? / ORG02? | 51.77% | 0.016% | PULLBACK / UP | 0.85 | KEEP | 1.842% |
| 2023-01-07 | YOK | — | — | — / — | — | — | — |
| 2023-01-08 | YOK | — | — | — / — | — | — | — |
| 2023-01-09 | YOK | 52.15% | 0.014% | NEUTRAL / — | -0.07 | KEEP | 0.173% |
| 2023-01-10 | YOK | 51.76% | 0.017% | CONTINUE / UP | 0.69 | KEEP | 0.331% |
| 2023-01-11 | YOK | 52.52% | 0.016% | NEUTRAL / — | 0.34 | KEEP | -0.062% |
| 2023-01-12 | ORG01? | 52.90% | 0.016% | END / — | -0.11 | KEEP | 1.052% |
| 2023-01-13 | YOK | 52.81% | 0.020% | CONTINUE / UP | 0.70 | KEEP | 1.256% |
| 2023-01-14 | YOK | — | — | — / — | — | — | — |
| 2023-01-15 | YOK | — | — | — / — | — | — | — |
| 2023-01-16 | YOK | 52.97% | 0.019% | NEUTRAL / — | 0.18 | KEEP | -0.280% |
| 2023-01-17 | YOK | 52.63% | 0.019% | NEUTRAL / — | 0.33 | KEEP | -0.398% |
| 2023-01-18 | ORG01? RIVAL | 53.10% | 0.019% | NEUTRAL / — | -0.36 | KEEP | -0.224% |
| 2023-01-19 | YOK | 52.85% | 0.023% | CONTINUE / UP | 1.49 | KEEP | 1.457% |
| 2023-01-20 | YOK | 53.32% | 0.024% | PULLBACK / UP | 0.25 | KEEP | -0.337% |
| 2023-01-21 | YOK | — | — | — / — | — | — | — |
| 2023-01-22 | YOK | — | — | — / — | — | — | — |
| 2023-01-23 | YOK | 52.90% | 0.025% | CONTINUE / UP | 1.53 | KEEP | 0.289% |
| 2023-01-24 | YOK | 53.00% | 0.025% | CONTINUE / UP | 1.38 | KEEP | 0.315% |
| 2023-01-25 | YOK | 53.21% | 0.026% | CONTINUE / UP | 1.68 | KEEP | 0.476% |
| 2023-01-26 | ORG02? | 53.35% | 0.023% | NEUTRAL / — | 0.51 | KEEP | -0.960% |
| 2023-01-27 | G01 mixed | 53.97% | 0.024% | NEUTRAL / — | -0.14 | KEEP | -0.088% |
| 2023-01-28 | YOK | — | — | — / — | — | — | — |
| 2023-01-29 | YOK | — | — | — / — | — | — | — |
| 2023-01-30 | YOK | 54.50% | 0.023% | CONTINUE / DOWN | -0.37 | KEEP | -0.227% |
| 2023-01-31 | G01 mixed | 53.86% | 0.024% | NEUTRAL / — | -0.54 | KEEP | 0.279% |

**İşlemsiz gün:** Pazar/Cumartesi veya 1–2 Ocak için o tarihle etiketlenen tam NY17 seansı yok. 16 Ocak yalnız 76 M15 bar, kısmi seans; sayısal çıktı geçmişi yansıtır, tam seans kalite sertifikası değildir.

## Ekonomik açıklama anındaki asıl algoritma gözlemi

- **2023-01-06:** Varsayılan +60 dakika ekonomik erişimden sonraki ilk kayıt 2023-01-06T14:30:00.000Z. S1 dört saatlik ekonomik koşullu tahmin **NOT READY**; S2 **NEUTRAL**, yön **—**, trend z **0.80**; S3 **KEEP**. Ekonomik girdi yalnız `POST_RELEASE_ONLY`, tarihsel firstprint/PIT doğrulanmadı.
- **2023-01-12:** Varsayılan +60 dakika ekonomik erişimden sonraki ilk kayıt 2023-01-12T14:30:00.000Z. S1 dört saatlik ekonomik koşullu tahmin **NOT READY**; S2 **REENTRY**, yön **UP**, trend z **0.62**; S3 **KEEP**. Ekonomik girdi yalnız `POST_RELEASE_ONLY`, tarihsel firstprint/PIT doğrulanmadı.

**Öğrenme sonucu:** 6 ve 12 Ocak'ta ekonomik release girişi modele `RECONSTRUCTED_RELEASE_RESEARCH` statüsünde geçirildi; buna rağmen ekonomik sürpriz özellikleri için 2022-Q4 ön eğitiminde yeterli ekonomik örnek bulunmadığından ilk ekonomik koşullu S1 dört-saat tahmini hazır değildi. **Ekonomik kurallardan büyük hareketi önceden yakalayan karar mekanizması bu deneyde doğrulanmadı**. Mevcut S1 fiyat istatistikleri, ÖĞREN-03 ORG01 nedensel kanıtı yerine kullanılamaz.

**Ayrım:** ORG01 gibi hipotezlerin başlığı sonuçların ardından açıklanabilir; yalnız gerçekten öğretilmiş ve o anda kabul edilen özelliklerle üretilen önceden kayıtlı bir tahminin ekonomik kural başarısı olarak sayılmasına izin vardır. Bu deney o kapıyı geçmedi.

**Teknik tekrar:** [Runner](replay_jan2023_integrated_s1_s2_s3_daily.js), [Gizli fiyatı yalnız salt-okunur çıkaran kod](export_private_evduka_for_conditional_replay.py), [CI sözleşmesi](../../.github/workflows/gold-jan2023-economic-s1-s2-daily-audit.yml). Lisanslı ham M15 fiyatlar GitHub'a commitlenmedi, workflow sonuçta yalnız güvenli toplanmış metrikleri yayımlar.
