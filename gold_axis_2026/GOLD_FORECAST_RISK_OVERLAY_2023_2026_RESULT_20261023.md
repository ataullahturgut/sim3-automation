# Gold Forecast Risk Overlay V1 — 2023–2025 öğrenimi, 2026 salt-okunur uyarı katmanı

**Tarih:** 23 Ekim 2026  
**Durum:** TEST TAMAMLANDI / BAĞIMSIZ ARAŞTIRMA KATMANI / CANLI UYGULAMAYA EKLENMEDİ / GERÇEK ANN HATA OLASILIĞI HENÜZ DOĞRULANMADI  
**GitHub Actions:** https://github.com/ataullahturgut/sim3-automation/actions/runs/40013192599 (2/2 PASS)  
**Dal:** gold-forecast-risk-overlay-v1-20261023
**Kod:** tools/gold_forecast_risk_overlay_2023_2026_v1.py; tools/gold_forecast_risk_warning_adapter_v1.py
**Tam kayıt:** gold-risk-overlay-2025-2026-daily-flags-and-metrics, ayrıca uyarı adaptörü senaryo JSON'u

## İhtiyaç

Aylık, haftalık ve günlük mevcut ANN tahminlerini yeniden eğitmeden; mevcut farklı başlangıç/veri tamlıkları olan gösterge aileleriyle, tahmin dönemi içindeki beklenmedik piyasa koşullarına uyarı ekle. Aylık veya haftalık tahmin fiyatını geriye dönük DEĞİŞTİRME. Ana modelin ölçülmüş hatasıyla eşleşme henüz yapılmadığından "hata olasılığı %X" deme; "piyasa rejimi sıra dışı ve tahmin belirsizliği artmış olabilir" de.

## Gerçek kurulum

- GVZ: resmi CBOE günlük kapanış; kaynak sonradan indirilmiş tarihsel snapshot, ilk gün yayınına ait değiştirilemez tarihsel vintaj doğrulaması yok
- Altın, gümüş, platin, paladyum: 2010–2026 araştırma kaynakları, daily common-date; 2026-02-27 sahte fiyat anomalisi ve en az 20 işlem günlük özellik penceresi/5 günlük hedef penceresiyle temas eden dönemler karantinada; diğer kaynak hataları ayrıca kanıtlanmış değil
- Dolar: Fed DTWEXBGS_FRB_H10, **önceki haftanın gözlemleri izleyen pazartesi saat 16:15 ET açıklandıktan sonra** modelde kullanılabilir
- Faiz: Fed DGS10_FRB_H15, ilk baskı/PIT kanıtı olmadığı için en az **önceki gün gözlemi** kullanıldı
- 14 risk özelliği: metal trend/RSI/oynaklık/ayrışma (6), GVZ endeksi (4), H.10 broad USD değişimleri (2), 10 yıllık faiz değişimi/seviyesi (2)
- Dört bağımsız ablasyon: METAL_ONLY; METAL_GVZ; METAL_GVZ_USD_RATES; USD_RATES_ONLY
- Dışsal hata etiketi kullanılmadan, IsolationForest 200 n_estimators + RobustScaler. **Anomali puanı = sıra dışı koşul**. DOWN tahmini, gerçek olay olasılığı, ANN tahmin hatası olasılığı değildir.
- Eşikler yalnız eğitim dönemi risk skorlarının 90. ve 95. yüzdelikleri. Uyarılar bunlara göre YELLOW ve RED.
- 2025 teşhis: **486 adet 2023–2024 eğitim satırı**, 2025'te 253 kontrol günü.
- 2026 stres: **739 adet 2023–2025 eğitim satırı**, 2026 Ocak–Eylül arası kaynağı temiz olan ve ileri hedefi olgunlaşan 161 kontrol günü.
- Tarihsel araştırma, 30 Ocak olayı görüldükten sonra hipotez oluşturulduğu için **2026 bütünüyle hipotez-kör bilimsel test değildir**.

## Öne çıkan test (GERÇEK GÜNLÜK VERİ)

Sadece RED (eğitimdeki üst %5 anomali eşiği) için:

| Aile | 2025 RED uyarı günü | 2025 ertesi gün gerçek >=%3 düşüş | Öncesinde RED bulunan | RED yanlış uyarı günü | 2026 RED uyarı günü | 2026 ertesi gün gerçek >=%3 düşüş | Öncesinde RED bulunan | RED yanlış uyarı günü |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| METAL_GVZ | 61/253 | 3 | 3 | 58 | 54/161 | 4 | 4 | 50 |
| **METAL_GVZ_USD_RATES** | **42/253** | **3** | **3** | **39** | **43/161** | **4** | **4** | **39** |
| USD_RATES_ONLY | 14/253 | 3 | 0 | 14 | 1/161 | 4 | 0 | 1 |

- 2025 RED combo: 3/3 o günün kapanışına kadar verilen uyarıların bir sonraki günlük fiyatında gerçekleşen >=%3 düşüşler vardı; **42 uyarı günü / 253 gün** demek çoğu uyarı yanlış.
- 2026 RED combo: 4/4 sonraki günlük büyük düşüş görülen günler uyarı kapsamında; **43 uyarı günü / 161 gün**, 39 yanlış alarm.
- 2025 next5d -5%: combo RED **6/6 örtüşen riskli çıkış günü**, fakat RED 36 yanlış alarm gününe sahip. 2026 next5d -5%: combo RED **9/13 riskli çıkış günü**, 34 yanlış alarm günü. Tek olay birçok örtüşen riskli çıkış günü üretebilir.
- Sadece dolar/faiz sınıfı 2025'te 0/3, 2026'da 0/4; **Ocak çöküşünün öncü riskini dolar/faiz değil metal ve GVZ ailesi sağladı**. Dolar/faizin beraber eklenmesi kompozit modelde 2025 RED alarm sayısını 61'den 42'ye indirdi, ama gerçek yönün % kaçı tamamen buna nedensel bağlı bilinmiyor.
- YELLOW dahil 2025 combo **58/253** uyarı günü, 2026 combo **81/161** uyarı günü. RED alarm yoğunluğu 2026'da bile aşırı yüksek, dolayısıyla canlı otomatik SAT/AL kararı verilemez.

### Ocak 2026 detay (2023–2025 eğitimi tamamlanmış, 2026'ya dokunulmamış modelin *retrospektif* uyarısı)

| Risk gözlem/uyarı tarihi | Kompozit METAL_GVZ_USD_RATES | USD_RATES_ONLY | Olay |
|---|---|---|---|
| 21 Ocak | RED | NORMAL | erken kırılganlık; bu günün 5g ufkunda Jan30 doğrudan kapsanmıyor |
| 22 Ocak | YELLOW | NORMAL | uyarı ama sonraki 5g büyük düşüş yok (yanlış alarm) |
| 23 Ocak | RED | NORMAL | erken risk; next5 window Jan30'la kesişebilir |
| 26 Ocak | RED | NORMAL | 30 Ocak/2 Şubat öncesinde |
| 27 Ocak | RED | NORMAL | 30 Ocak/2 Şubat öncesinde |
| 28 Ocak | RED | NORMAL | 30 Ocak/2 Şubat öncesinde |
| **29 Ocak** | **RED** | **NORMAL** | 30 Ocak ertesi gün sert düşüşün hemen önünde |
| 30 Ocak | RED | NORMAL | 2 Şubat'ta sert satış devam etti |

2026 diğer aday uyarı kümeleri: 5–19 Haziran, 21–25 Ağustos, 11–15 Eylül; birçok doğru/yanlış uyarı birlikte. 27 Şubat ve veri anomalisiyle kirlenen sonraki özellik/hedef günleri değerlendirme dışında bırakıldı.

### Alarm günleri yerine alarm olayları — gösterim sadeleştirme

METAL_GVZ_USD_RATES RED uyarılarının art arda gelen dönemler halinde toplamı: 2025'te **8**, 2026 Ocak–Eylül kayıtlı 161 gün içinde **9** dönem. Bunların hepsi çöküş değildir; örneğin 21 Ocak tekil, 23 Ocak–10 Şubat uzun çok günlük uyarı kümesidir. Kullanıcıya her gün aynı uyarı tekrar gösterilmemeli; alarm dönemi altında başlangıç, devam, sona erme gösterilmelidir.

## Gerçek uyarı adaptörü

tools/gold_forecast_risk_warning_adapter_v1.py (GitHub Actions 5/5 TEST PASS):
- Ana model tahmin çıktıları değişmez; risk seviyesi ve orijinler eklenir.
- Jan30 günlük tahmini Jan29 kapanışı itibarıyla RED; gerçek model günlük fiyat tahmini 5478.903740930488 aynen korunur.
- 2 Şubat haftalık tahmini 30 Ocak kapanışı itibarıyla RED; orijinal hafta tahmini 5037.21 değişmez.
- Şubat aylık örnek 30 Ocak sonrasında 4892.34 değişmeden RED açıklama alır.
- Ocak aylık tahmininin 31 Aralık başlangıcına 28 Ocak sinyali önceden varmış gibi yazılmaz. 28 Ocak'ta ayrı **takip güncellemesi** gelir. 31 Aralık'ta eski 2025 uyarıları ilk Ocak günlerini 5g ufukla kapsıyorsa, onlar ayrıca o tarihte bilinen risk olarak korunur; 30 Ocak olayını 31 Aralık'ta bilindi sanmak yasak.
- Eski/bitmiş tarihli tahminler için işlem tavsiyesi üretmez.

## Önemli eksikler ve geçme koşulu

1. **GERÇEK ANN tahmin hata eşleşmesi yok**: 2023–2025 günlük/haftalık/aylık aynı zamanlı orijinal ANN walk-forward tahmin ve gerçekleşen hatalarıyla layer sinyalinin doğruluk payını karşılaştırmadan "ANN şu kadar hata yapacak" iddiası KESİNLİKLE YAPILMAZ.
2. CFTC COT, GLD/SLV ETF akımları, CME teminat tam tarihsel aileleri bu V1'de hala veri denetimi nedeniyle eklenmedi. Dolayısıyla tamamlanmış tüm çok-kaynaklı risk sistemi değil.
3. 2026 test seti veri karantinası nedeniyle eksik ve hipotez 2026 çöküşü görüldükten sonra seçildi.
4. Büyük düşüşler nadir, aynı çöküşten gelen birçok 5g etiket birbirine bağımlı. Günlük false-alarm/alert rate çok yüksek. Üretime onay **VERİLMEDİ**.
5. Daha az gereksiz uyarı için sadece **2023–2025** olay bazlı eğitim/kalibrasyon, bağımsız daha ileri dönem, yeterli nadir olay sayısı gereklidir; 2026 Ocak'a göre eşik düzeltmesi yapılmaz.
