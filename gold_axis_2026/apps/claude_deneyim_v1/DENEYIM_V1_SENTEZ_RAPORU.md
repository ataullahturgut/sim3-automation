# DENEYİM v1 — 36 aylık deneyim maratonu sentezi (2023-01 → 2025-12)

2026-10-16. Dal: `research-gold-claude-pusula-v1-20261016`. Sıra: protokol `5533e39` → kod ve testler `5a76b54` → bu maraton.
**Statü:** Geliştirme (deneyim) dönemi. Test değildir. 2026 verisi yüklenmedi. Nihai algoritma `DENEYIM_V1_DONDURULMUS_MODEL.json` olarak donduruldu.

## Ne yapıldı?
Her ay sonunda: (1) o güne kadarki veriyle maliyetli en uygun al/sat yolu dinamik programlamayla hesaplandı, (2) modelin o ay **önceki ay sonu bilgisiyle gerçek zamanlı** verdiği kararlar kaydedildi, (3) ideal yükseliş bacakları ve ideal nakit dönemleri öncesindeki 35 tarihsiz durum değişkeni ölçüldü, (4) deneyim hafızası ve model yeniden öğrendi, (5) `reports/AYLIK_YYYY_MM.md/.json` yazıldı (36 ay).

Mühendislik düzeltmeleri (performansa bakmadan, veri doğruluğu için): olay dosyasında 2025'in 8 FOMC toplantısı eksik olduğu için resmi FOMC takvimi kullanıldı; CME vadeli getirileri vade geçişlerini atlayan zincirleme getiriye çevrildi (önce 20 günlük petrol/gümüş getirileri günlerin yalnız %7'sinde hesaplanabiliyordu).

## Sonuç (100 USD, 2023-01-03 → 2025-12-31, 753 işlem günü)

| | Son değer | Maks. düşüş | İşlem |
|---|---:|---:|---:|
| Maliyetli ideal yol (geriye dönük üst sınır) | 580,57 | — | 39 bacak |
| Pasif altın | 230,82 | %10,79 | 1 |
| Trend kuralı (SMA100 ±%1) | 215,36 | %11,42 | — |
| **DENEYİM v1 (gerçek zamanlı)** | **195,05** | **%10,36** | 5 |

Model 2023'te 5 işlem yaptı ve −%6,3 ile yılı kapattı. 2023-12-04'te altın aldı ve ondan sonra hiç satmadı; 2024 (+%26,5) ve 2025 (+%64,6) getirileri altını tutmaktan geldi.

## Model ne öğrendi?

**1. Skorlar deneyimle iyileşti ama zayıf kaldı.** Modelin her gün gerçek zamanlı ürettiği skorun ideal ALTIN/NAKİT günlerini ayırma gücü (AUC): 2023 **0,53**, 2024 **0,61**, 2025 **0,63**. 0,5 şans düzeyidir; öğrenme var ama ideal yolun 39 bacağını zamanlayacak kadar güçlü değil.

**2. Karar katmanı "tut" kuralına yakınsadı.** Eşikler her ay modelin kendi gerçek zamanlı geçmişiyle seçildi; çıkış eşiği 0,10'a indi. Yani model kendi deneyiminden, bu maliyetle (tam tur ~%1,6) çıkış sinyallerinin çoğunun para kaybettirdiğini öğrendi ve neredeyse hiç satmayan bir yapıya geçti. Bu, "zırt pırt girip çıkma" sorununu çözdü ama ideal yoldaki gerçek düşüşlerden kaçınmayı da engelledi.

**3. Ölçülen mekanizmalar (36 ay birleşik, standart sapma birimi):**
- **İdeal girişlerden önce tipik durum:** altın 200 günlük ortalamanın üstünde (+1,06) ama son 1–5 günde geri çekilmiş (−1,03 / −0,86); COT spekülatif pozisyon yüksek (+0,87); gümüş de son 5 günde geri çekilmiş (−0,70); girişler sıklıkla bir FOMC toplantısından birkaç gün önce (−1,75). Yani "yükselen trendde kısa geri çekilme" örüntüsü.
- **İdeal çıkışlardan önce tipik durum:** altın 200 günlük ortalamadan çok uzaklaşmış (+1,88), 60 günde güçlü yükselmiş (+1,32), son 1–20 günde hızlı tırmanmış (+1,09…+1,14) ve 60 günlük zirvede (+0,96). Yani "aşırı ısınma" örüntüsü.
- **Doğrusal skorda altın lehine:** kısa vadeli altın momentumu, yüksek COT spekülatif pozisyon, gümüşün güçlenmesi, pozitif NFP sürprizi, yüksek GVZ. **Aleyhine:** 200 günlük ortalamadan aşırı uzaklık, petrol ve Nasdaq'ın 20 günlük yükselişi, altın/gümüş oranının artması, oynaklık sıçraması.
- **Son değişken grubu önemleri:** altın fiyat yapısı 0,40; hisse/tahvil/petrol/gümüş 0,27; altın oynaklığı 0,07; makro sürpriz/takvim 0,07; olay izi (şok) 0,07; COT 0,05; faiz 0,04; dolar 0,04. Faiz ve doların düşük kalması dikkat çekici: 2023–2025'te altın reel faizle klasik ilişkisinden büyük ölçüde kopmuştu (merkez bankası alımları, tarife ve jeopolitik risk dönemi).

## Dürüst değerlendirme
- Model pasif altını ve trend kuralını geçemedi; maks. düşüşü pasifle hemen hemen aynı. Geliştirme döneminde bile ideal yolun yalnız küçük bir bölümünü yakaladı.
- Olumlu taraf: öğrenme gerçek ve ölçülebilir (AUC 0,53 → 0,63), aşırı işlem yok, mekanizma raporları yorumlanabilir.
- Sınırlar: haber metni yok (olaylar piyasa izi ve planlı makro yayınlarla temsil edildi), 39 ideal bacak küçük bir örnek, ideal etiketler geriye dönüktür, Claude 2023–2025'i biliyordu (yalnız etiket ve analizde), fiyatlar Dukascopy BID/ASK + varsayımsal %0,8/yön.

## Dondurulan algoritma
`DENEYIM_V1_DONDURULMUS_MODEL.json`: 35 değişken, 2025-12-31 standartlaştırma durumu, 753 günlük deneyim hafızası ve ideal etiketleri, ayırt edici metrik ağırlıkları, bant genişliği, düzenlemeli doğrusal katsayılar, birleşim ağırlığı α = 0,561, eşikler giriş 0,70 / çıkış 0,10.

## Sonraki adım
2026 testi için önce 2026 olay/makro verisi (CPI, NFP sürprizleri, COT, GVZ, faiz, dolar) aynı formatta toplanacak; sonra test ön kaydı yazılıp dondurulmuş algoritma kod değiştirilmeden 2026'ya uygulanacak. 2026 kısmen görülmüş olduğu için "yarı-kör" etiketlenecek; gerçek kanıt 2026-10 sonrası ileri kâğıt testidir.
