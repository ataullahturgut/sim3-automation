# Şubat 2023 — mevcut S1 + S2 + S3 CORE gerçek günlük araştırma sonuçları

**GOLD-ADAPTIVE-MODEL-APP-01 — 17 Ekim 2026.** [Başarılı GitHub Actions koşusu](https://github.com/ataullahturgut/sim3-automation/actions/runs/39044531815). Aynı kaynaklı ve şeffaf **reconstructed read-only Neon EV/Dukascopy MID** araştırma fiyatları. **Banka gerçek kotasyonu / gerçekleşmiş emir / gerçek firstprint PIT değildir.**

## Zaman ve aktarım sözleşmesi
- Mevcut matematiksel CORE tek oturum boyunca sıfırlanmadı: **2022 Ekim–Aralık + Ocak 2023** ön-öğrenim: 7785 M15 fiyat barı. Şubat 2023: **1830** M15 bar.
- Şubat başlangıcında S1 **5 piyasa prototipi**, **443 olgun 4s etiket**; Şubat bitiminde **6 piyasa prototipi**, **553 olgun 4s etiket**. Bu prototipler tarih bağımsız ÖĞREN-03 ORG kuralının öğrenildiği veya doğrulandığı anlamına GELMEZ.
- Şubat bütün günlerinde S3 `CONDITIONAL_ECONOMIC_RESEARCH` politika teklifi **KEEP**, portföy başlangıç ve sonuç durumu **CASH**. **`shadowEnabled=false`**; net servet hesaplaması ve gerçek işlem gerçekleştirilmiş gibi raporlanamaz. Gölge işlem yetkisi/gerçek emir yok.
- Ekonomi ile ilişkili kayda alınmış release: **3 Şubat NFP/AHE/UNEMP**, **14 Şubat TÜFE**. İkisi için yalnız tarihsel belgeye dayalı `POST_RELEASE_ONLY_NOT_PIT` koşullu özellikler varsayılan 60 dakika geciktirildi. **S1 ekonomik koşullu 4s tahmin bu iki olayın araştırma anında hazır değildi.** Diğer olaylar tabloya manuel eşleşen kural hipotezi olarak girilmiştir; gerçek ekonomik özellikler gibi modele S1'e enjekte edilmedi.
- Günlük S1/S2/S3 sayıları NY17 uyumlu 22:00 UTC araştırma-seansının **son tamamlanmış 15 dakikalık barı itibarıyla** hesaplandı. Aynı satırdaki gerçekleşen fiyat değişimi **o seansın ilk–son MID hareketidir, modelin sonraki 4 saatlik tahmin sonucu DEĞİLDİR**. Şubat 20 seans dâhil, 20 Şubat 82 M15 bar ile kısmi. 4–5, 11–12, 18–19, 25–26 Şubat'ta tam seans yok; ne sıfır getiri ne de BUY/HOLD tarihsel banka kararı iddiası yapılır.
- ÖĞREN-03 tarihsiz kural hipotezleri **yeni üretilmedi/değiştirilmedi**. ORG01/02/10 işaretleri olay-ön durumun **araştırmacı teşhisidir**, algoritmanın kanıtlı ekonomiden türetilmiş kararı değildir.

## 28 günün tamamı

| Tarih | Ekonomik kural *adayı* | S1 UP (+4s) | S1 beklenen log% (+4s) | S1 etkin N | S2 hızlı evre / yön | S2 trend z | S2 uzun evre | S3 | O seans altın (%) |
|---|---|---:|---:|---:|---|---:|---|---|---:|
| 2023-02-01 | ORG01? / ORG02? RIVAL | 53.28% | 0.0219% | 165.7 | CONTINUE / UP | 1.47 | NEUTRAL | KEEP | 1.196% |
| 2023-02-02 | ORG10? / ORG02? RIVAL | 53.94% | 0.0131% | 152.6 | CONTINUE / DOWN | 0.06 | NEUTRAL | KEEP | -2.222% |
| 2023-02-03 | ORG02? | 52.95% | 0.0086% | 158.2 | NEUTRAL / — | 0.49 | NEUTRAL | KEEP | -2.469% |
| 2023-02-04 | — | — | — | — | — / — | — | — | — | — |
| 2023-02-05 | — | — | — | — | — / — | — | — | — | — |
| 2023-02-06 | — | 53.11% | 0.0102% | 157.0 | NEUTRAL / — | 0.32 | NEUTRAL | KEEP | 0.009% |
| 2023-02-07 | ORG02? RIVAL | 53.26% | 0.0098% | 153.3 | NEUTRAL / — | -0.82 | NEUTRAL | KEEP | 0.290% |
| 2023-02-08 | — | 53.31% | 0.0114% | 158.6 | NEUTRAL / — | -0.06 | NEUTRAL | KEEP | 0.170% |
| 2023-02-09 | ORG02? RIVAL | 54.12% | 0.0072% | 150.1 | CONTINUE / DOWN | -1.33 | NEUTRAL | KEEP | -0.746% |
| 2023-02-10 | — | 52.41% | 0.0099% | 170.3 | CONTINUE / UP | 1.04 | NEUTRAL | KEEP | 0.172% |
| 2023-02-11 | — | — | — | — | — / — | — | — | — | — |
| 2023-02-12 | — | — | — | — | — / — | — | — | — | — |
| 2023-02-13 | — | 52.30% | 0.0073% | 166.6 | NEUTRAL / — | 0.45 | NEUTRAL | KEEP | -0.593% |
| 2023-02-14 | ORG01 / ORG02 RIVAL | 52.25% | 0.0087% | 169.7 | NEUTRAL / — | 0.80 | NEUTRAL | KEEP | 0.028% |
| 2023-02-15 | ORG02? | 51.99% | 0.0060% | 169.1 | NEUTRAL / — | 0.28 | NEUTRAL | KEEP | -0.981% |
| 2023-02-16 | ORG02? | 52.04% | 0.0054% | 163.5 | NEUTRAL / — | -1.14 | START | KEEP | -0.051% |
| 2023-02-17 | — | 51.66% | 0.0062% | 173.5 | CONTINUE / UP | 0.49 | CONTINUE | KEEP | 0.386% |
| 2023-02-18 | — | — | — | — | — / — | — | — | — | — |
| 2023-02-19 | — | — | — | — | — / — | — | — | — | — |
| 2023-02-20 | — | 52.36% | 0.0034% | 165.8 | CONTINUE / DOWN | -0.91 | CONTINUE | KEEP | 0.029% |
| 2023-02-21 | — | 51.79% | 0.0052% | 176.5 | NEUTRAL / — | -0.46 | UNREADY | KEEP | -0.390% |
| 2023-02-22 | ORG02? | 53.10% | -0.0013% | 156.5 | CONTINUE / DOWN | -2.01 | WARMUP | KEEP | -0.536% |
| 2023-02-23 | — | 51.02% | 0.0048% | 186.2 | NEUTRAL / — | 0.24 | WARMUP | KEEP | -0.206% |
| 2023-02-24 | ORG02? | 50.32% | 0.0026% | 188.8 | NEUTRAL / — | 0.38 | WARMUP | KEEP | -0.633% |
| 2023-02-25 | — | — | — | — | — / — | — | — | — | — |
| 2023-02-26 | — | — | — | — | — / — | — | — | — | — |
| 2023-02-27 | — | 50.84% | 0.0011% | 181.7 | NEUTRAL / — | -0.61 | WARMUP | KEEP | 0.234% |
| 2023-02-28 | — | 50.71% | 0.0026% | 182.4 | NEUTRAL / — | -0.71 | WARMUP | KEEP | 0.525% |

## Olayın ilk araştırma gözlemi — gün sonuna bakarak tahmin uydurmama

- **2023-02-03 / 2023-02-03T14:30:00.000Z:** ekonomik haberin araştırma amaçlı +60 dakika sonrası ilk tam fiyat kayıt zamanı. S1 ekonomi koşullu 4s tahmin **hazır değil**; S2 **NEUTRAL/—**; S2 trend z **-1.10**; S2 uzun **NEUTRAL/—**; S3 **KEEP**, neden **NO_SUPPORTED_CONDITIONAL_NET_ADVANTAGE**. Ekonomik veri `POST_RELEASE_ONLY_NOT_PIT`.
- **2023-02-14 / 2023-02-14T14:30:00.000Z:** ekonomik haberin araştırma amaçlı +60 dakika sonrası ilk tam fiyat kayıt zamanı. S1 ekonomi koşullu 4s tahmin **hazır değil**; S2 **NEUTRAL/—**; S2 trend z **-0.97**; S2 uzun **NEUTRAL/—**; S3 **KEEP**, neden **NO_SUPPORTED_CONDITIONAL_NET_ADVANTAGE**. Ekonomik veri `POST_RELEASE_ONLY_NOT_PIT`.

## Niceliksel karar eleştirisi

- S1 gün sonu dört saatlik UP olasılığı **%50.32–%54.12** aralığında; bu sınırlı fiyat-temelli destek tek başına `BUY` / `SELL` değildir. S1 beklenen +4 saat log artışı, 2 × %0,8 ~ %1,59 tam tur maliyeti karşısında çok küçük.
- S2 FAST 4s araştırma skoru: **Brier 0.23974**, kendi temel karşılaştırması **0.23054**; daha düşük Brier daha iyi olduğundan, mevcut S2 4s risk modeli **üstünlük göstermemiştir**. Çakışan ankrajlar nedeniyle bağımsız başarı diye puanlanmaz.
- S2 SLOW: **101** kabul edilmiş tamamlanan seans, **1** bitmiş uzun epizot, **4** ret. 1/3/5/10 seans bitiş/kalım olasılıkları için hazır etiket sayısı **sıfır**; uzun risk tahmini bilinmiyor.
- S3 tüm 1830 Şubat barında ekonomi/maliyet destekli pozisyon değişikliğini önermedi. Bu, büyük Şubat düşüşünü başarılı şekilde öngörmek değil, **eksik ekonomik ayrıştırma nedeniyle hiçbir yeni aksiyon üretememektir**.
- NFP ilk ekonomi varsayım anında S2 **NEUTRAL**, trend z **−1,10**; TÜFE varsayım anında S2 **NEUTRAL**, trend z **−0,97**. Fakat dört saatlik S1 ekonomik tahmin **UNREADY** ve S3 **KEEP CASH**.
- Bu çalışma saat filtresine sahip DEĞİLDİR. Öğrenme hafızası Şubat başında sıfırlanmadı; ekonomik ORG kuralı bir takvim yılından ibaret değildir.

**Bilim kapısı:** `SCIENCE_GATE=FAIL`, `ECONOMIC_CAUSAL_CHAIN_NOT_VALIDATED`, `FIRSTPRINT_PIT_NOT_CERTIFIED`, `TRADE_ALLOWED=false`. Sahte/otomatik ekonomik kural gücü veya olmayan canlı emir başarısı yazma.

**Tekrar:** [Şubat mevcut CORE runner](replay_feb2023_integrated_s1_s2_s3_daily.js); [Jan araştırması](JAN_2023_INTEGRATED_S1_S2_S3_REAL_DAILY_RESULTS_20261017.md); [İş akışı](https://github.com/ataullahturgut/sim3-automation/actions/runs/39044531815). Günlük toplanmış araştırma çıktılarını workflow artifact olarak indirilebilir; lisanslı ham fiyat GitHub'a commitlenmedi.
