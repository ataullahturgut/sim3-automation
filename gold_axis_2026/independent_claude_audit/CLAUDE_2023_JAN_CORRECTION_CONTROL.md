# SINAV C — 26–31 Ocak 2023 küçük DOWN · yanlış alarm / gereksiz işlem kontrolü

**Kip:** `AS_OF_DECISION_EVALUATION` (kararlar) + tanısal ex-post. Hindsight'a açık.

## 1. Fiyat olayı (EX-POST)

M15 MID tepe 2023-01-26 06:00Z barı **1948,705** → dip 2023-01-31 12:15Z barı **1902,92**: **−%2,35**. Ocak'ta −%3'lük DOWN yok.

## 2. Kronoloji ve rejim

| Zaman (UTC) | Bilgi | XAU 15dk / 4s / 3 seans / 5 seans | Not |
|---|---|---|---|
| 01-25 kapanış | Rejim UP, trend20 +%3,31 | — | 9 ayın zirvesi civarı |
| 01-26 13:30 | GDP Q4 öncü %2,9 vs ~%2,6; GDP fiyat endeksi %3,5 vs %3,2 (Kitco 2023-01-26) | −0,23 / −0,56 / −0,77 / +0,65 | Hafif hawkish büyüme sürprizi |
| 01-27 13:30 | PCE Ara çekirdek +%0,3 a/a, yıllık %4,4 — beklentiyle aynı (Kitco 2023-01-27) | +0,02 / −0,34 / −0,22 / −1,04 | Sürpriz yok |
| 01-30 kapanış | trend20 +%1,17, mom10 +%0,47 → hâlâ UP | — | Rejim zayıflıyor |
| 01-31 13:30 | ECI Q4 | +0,06 / +0,93 / +0,02 / −2,34 | Altın dipten toparlandı |
| 02-01 19:00 | FOMC +25bp, Powell “dezenflasyon başladı” | +1,46 (4s) | Düzeltme kapandı, yeni zirve 02-02 07:00Z 1959,6 |

GC/SI/ZN/NQ saatlik tepkiler [CLAUDE_2023_KEY_RELEASES_CME_N0_H1_REACTIONS.csv](CLAUDE_2023_KEY_RELEASES_CME_N0_H1_REACTIONS.csv): 26 Ocak GDP saatinde GC −%0,18, ZN −%0,08 (yatay); 27 Ocak PCE saatinde ZN 0,00 — **faiz kanalında anlamlı şok yok.**

**Okuma:** Düşüş, yeni bir makro şoktan çok, FOMC öncesi kâr realizasyonu / konsolidasyon ve hafif güçlü büyüme verisiyle uyumlu (aile 6 + aile 1, kanıt L1–L2). Dolar/getiri seviyeleri MISSING.

## 3. Sistem ne gördü?

* 26–31 Ocak boyunca **z12 en düşük −1,14** (31 Ocak 08:15Z). Silahlı `ONSET_DOWN` (z12 ≤ −2) **hiç oluşmadı**; aşama en çok `UNCERTAIN`.
* `MACRO_DOWN` oluşmadı: GDP/PCE/ECI makro sınıfında değil (yalnız NFP/CPI/FOMC). Sınıf GDP'yi kapsasaydı bile: GDP sonrası 15dk −%0,23, 60dk −%0,06 → −%0,40 eşiği bu bar kapanışlarında aşılmadı (60dk içindeki diğer iki M15 kapanışı ayrıca kontrol edilmedi).
* Rejim UP kaldı → V-A/V-B/V-C/v2 hepsi **ALTIN TUT**.

## 4. Maliyet hesabı (26 Ocak 06:00Z'de 100 $ altına girilmiş kurulum, ASK 1947,71)

| Strateji | 31 Ocak sonu BID değeri | Net (satılsa) |
|---|---:|---:|
| Tüm varyantlar ve pasif: TUT | 98,16 | **97,37** |
| **Kâhin üst sınırı** (tepede sat, dipte geri al; ±0,16 makas) | 98,90 | 98,11 |

**Sonuç:** Kusursuz zamanlamayla bile SAT→AL döngüsünün kazancı en fazla **+0,74 $**. Gerçekçi bir sinyal tepe sonrası ve dip sonrası gecikmeyle çalışacağından beklenen değer negatif. **Doğru karar TUT'tur ve sistem TUT verdi.** `false_alarm_status = NO_ALARM (doğru)`.

## 5. Şubat düşüşünden farkı ne?

| Özellik | 26–31 Ocak | 2–3 Şubat |
|---|---|---|
| En düşük z12 | −1,14 | −2,54 (2 Şub 15:00Z), −3,67 (seans kapanışı) |
| Tetikleyici | Planlı, sürprizsiz/zayıf veriler | ECB/BoE sonrası dolar sıçraması + NFP 517k |
| Faiz kanalı (ZN 1s) | ~0 | 2 Şub +0,42 (ters!), 3 Şub −0,68 |
| Rejim | trend20 %1,2'ye indi ama pozitif kaldı | 2 Şub kapanışında SMA20'nin %0,08 altına geçti |
| Sonrası | 1 Şub'da yeni zirve | 24 Şub'a kadar −%7,15 |

Ayırt edici olan, **fiyatın SMA20'yi ne kadar geride bıraktığı** ve **şokun büyüklüğü**. Ocak sonunda rejim zayıflıyordu ama dönmedi; Şubat'ta dönüş sınırda (−%0,08) gerçekleşti. Bu sınırın kırılganlığı [CLAUDE_UNCERTAINTIES_AND_FALSIFICATION.md](CLAUDE_UNCERTAINTIES_AND_FALSIFICATION.md) içinde ayrıca işlendi.
