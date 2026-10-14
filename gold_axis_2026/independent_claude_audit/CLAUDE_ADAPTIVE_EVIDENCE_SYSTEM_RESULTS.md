# Öğrenen kanıt sistemi (AES v1) — sonuçlar

**Tarih:** 2026-10-14 · **Ön kayıt:** [CLAUDE_ADAPTIVE_EVIDENCE_SYSTEM_PREREG.md](CLAUDE_ADAPTIVE_EVIDENCE_SYSTEM_PREREG.md) (commit `e7be8d6`, koşudan önce) · **Kod:** [aes/aes_engine.py](aes/aes_engine.py) · **Sonuç dosyaları:** [AES_v1_0_RESULTS.json](aes/AES_v1_0_RESULTS.json), [AES_v1_1_RESULTS.json](aes/AES_v1_1_RESULTS.json) (2023'teki her karar anı için modül oyları, ağırlıklar ve olasılıklar `ledger_2023` alanında)
**Hüküm:** `NEGATIVE — NO EDGE IN DEV, NO TRADES IN JAN–FEB 2023`

## 1. Ne kuruldu?

Her hafta içi 09:00 ve 16:45 TRT'de on “uzman” ayrı ayrı görüş bildirdi:

| Modül | Neye bakıyor |
|---|---|
| Trend | 20 seans ortalamasına göre konum + 10 seans yönü |
| Kısa momentum | Son 3 seansın oynaklığa göre büyüklüğü |
| Şok geri dönüşü | Son günün aşırı hareketi geri döner mi |
| Haber/sürpriz | NFP, CPI, FOMC sürprizi + altının ilk 60 dk tepkisi |
| Olay analoğu | Şu anki habere en çok benzeyen 7 geçmiş açıklamada sonra ne oldu |
| Durum analoğu | Şu anki piyasa durumuna en çok benzeyen 25 geçmiş anda sonra ne oldu |
| Gümüş teyidi | Gümüş aynı yönde mi |
| Faiz kanalı | 10 yıllık tahvil vadelisi |
| Risk/likidite | Nasdaq sert düşerken altın ne yapıyor |
| Oynaklık | Altın oynaklık endeksi (GVZ) yükseliyor mu |

**Öğrenme:** Bir modülün tahmininin sonucu belli olunca (10 seans sonra) haklı ya da haksız sayıldı ve ağırlığı buna göre güncellendi. Vaka kütüphaneleri her yeni sonuçla büyüdü. Sistem hiçbir zaman sonucu henüz belli olmayan bilgiyi kullanmadı.

**Karar:** Geçmişte benzer skorlardan sonra “maliyeti aşan yükseliş” olasılığı, “maliyeti aşan düşüş” olasılığından en az 25 puan fazlaysa AL; tersiyse SAT; değilse KAL.

## 2. Sonuçlar

| Dönem | v1.0 (ilk kod) | v1.1 (düzeltilmiş) | Pasif altın | Nakit |
|---|---:|---:|---:|---:|
| Geliştirme Tem 2021 – Ara 2022 (100 $) | 99,15 $ · 1 işlem | 92,77 $ · 1 işlem | 100,86 $ | 100,00 $ |
| A1 3–16 Oca 2023 (nakitle başlayan) | 100,00 $ · işlem yok | 100,00 $ · işlem yok | 102,49 $ | 100,00 $ |
| A2 (ChatGPT pozisyonu, 16 Oca) | net 101,73 · tuttu | net 101,73 · tuttu | — | — |
| C 26–31 Oca (altında) | net 96,66 · tuttu | net 96,66 · tuttu | — | — |
| B 30 Oca – 28 Şub (altında) | net 92,15 · tuttu | net 92,15 · tuttu | — | — |
| Sürekli 3 Oca – 28 Şub (nakit) | 100,00 $ | 100,00 $ | 97,55 $ | 100,00 $ |

(A2/C/B rakamları sistemin kendi 15 dk fiyat vekiliyle hesaplandı; önceki raporlardaki dakikalık fill rakamlarından birkaç sent farklıdır.)

**Yön isabeti (10 seans sonrası yönü bilme):**

| Dönem | v1.0 | v1.1 |
|---|---:|---:|
| 2021 2. yarı | %37 | %39 |
| 2022 | %52 | %50 |
| Oca–Şub 2023 | %67 | %65 |

**Modüllerin tek tek isabeti (geliştirme dönemi):** trend %50, momentum %51, şok geri dönüşü %48, haber %51, olay analoğu %46, durum analoğu %45, gümüş %50, faiz %52, risk %56 (106 karar), GVZ %57 (68 karar). **Hiçbiri yazı-turadan anlamlı biçimde iyi değil.**

## 3. Neden işe yaramadı?

1. **Modüllerde tek başına öngörü gücü yok.** Bu basit biçimleriyle, 10 seanslık yönü %50 civarında biliyorlar. Birleştirmek bunu düzeltmiyor.
2. **Kalibrasyon maliyeti aşmayı nadiren gösterdi, gösterdiğinde de yanıldı.** Ocak–Şubat 2023'teki 84 karar anında “büyük yükseliş” ile “büyük düşüş” olasılıkları arasındaki fark en fazla 0,17 (yükseliş) ve 0,10 (düşüş) oldu; işlem eşiği 0,25. 2023'ün en güçlü “AL” işareti (0,17, v1.0) **2 Şubat 16:45 TRT'de, büyük düşüşün hemen öncesinde** geldi. Geliştirme döneminde eşik en az bir kez geçildi; açılan tek pozisyon (v1.0: Tem 2021, v1.1: Nis 2022 zirveye yakın) satış sinyali gelmeden dönem sonuna taşındı ve kaybettirdi.
3. **Dönüş anlarında veri yanıldı.** 2 Şubat 09:00 TRT, büyük düşüşün hemen öncesi: trend, gümüş, faiz ve durum analoğu hep **yükseliş** diyordu (skor +0,65). 3 Şubat 16:45'te NFP düşüşünden sonra “şok geri döner” modülü **AL** yönüne itti (skor +0,55). Ocak'taki 2023 isabeti (%65–67) ise trendin sürdüğü haftalardan geliyor.
4. **Uygulama hatası (v1.0):** Oy vermeyen modüller ceza almadığı için seyrek oy verenler ağırlık topladı, sık oy verenler sıfırlandı. v1.1'de ön kayıttaki “uyuyan-uzman” yöntemine uygun düzeltildi; sonuç değişmedi, geliştirme dönemi daha da kötüleşti.
5. **Zamanlama tutarsızlığı (ön kayıtta):** 16:45 TRT karar anı NFP/CPI'den 15 dk sonra; haber modülü 60 dk tepki istediği için aynı günkü açıklamayı ancak ertesi sabah görebildi. 3 Şubat NFP'si haber modülüne 6 Şubat sabahı girdi.

## 4. Önceki iki denemeyle karşılaştırma

| Yöntem | Sürekli Oca–Şub 2023 | Not |
|---|---:|---|
| Mekanik rejim kuralı (V-A) | 102,35 $ | 2020–22'de kaybettirdi (59 $) |
| Vaka eşleştirmesiyle takdir kararları | 100,45 $ | Sonucu bilen biri tarafından verildi — kör test değil |
| **Öğrenen kanıt sistemi (AES)** | **100,00 $** | Hiç işlem yapmadı; geliştirmede de üstünlük yok |
| Pasif altın | 97,55 $ | |

**Dürüst okuma:** Ocak–Şubat 2023'te para kazandıran iki yaklaşımın da önceden doğrulanmış bir üstünlüğü yok. Veriye dayalı, kendi kendine öğrenen sistem ise sakin kaldı. Bu, “bu veri setiyle %1,6 maliyeti aşan öngörü yok” demek. Sistem hata yapmadı ama değer de üretmedi.

## 5. Sonraki sürüm için öneriler (henüz koşulmadı, ayrı ön kayıt gerekir)

1. **Bağlama göre öğrenme:** Modüllerin tek bir global ağırlığı yerine rejime göre ayrı ağırlıklar. Örneğin trend modülü güçlü trendde, geri dönüş modülü yatay piyasada değerlendirilsin. Şu an iki rejimin sonuçları birbirini götürüyor.
2. **Olaya göre ufuk:** Haber sonrası kararlarda 10 seans yerine 1–3 seanslık hedef. 2023'te NFP'den sonraki hareketin çoğu ilk 4 saatte bitti.
3. **Eksik veri:** Gün içi dolar endeksi ve 2/10 yıllık getiriler. 2 Şubat dönüşü dolar kaynaklıydı ve sistemde bunu görecek modül yoktu.
4. **Test tasarımı:** Kuralları 2020–2022'de geliştirip **Mart 2023 – Aralık 2024'te** bir kez sınamak. Bu dönem AES'e hiç gösterilmedi.
