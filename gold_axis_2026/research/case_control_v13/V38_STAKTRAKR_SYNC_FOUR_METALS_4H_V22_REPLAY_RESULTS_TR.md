# V38 — StakTrakr dört değerli metalin eşzamanlı 4 saat hareketleri: V22 karşılaştırması

**30 Ekim 2026 UTC — gerçek Neon verileri ve GitHub Actions üzerinde ÇALIŞTIRILDI.** 
**Ayrı araştırma; canlı alarm/finansal işlem yok; ilk yayın (firstprint) sertifikası yok.**

## Gerçek veriler ve tekrar üretim

- Altın, gümüş, platin ve paladyumun *aynı UTC saatte sonlanan* dört saatlik getiri değerleri kullanıldı; **4 adet kesintisiz saatlik kapanış** şartı var. Düşüş anında gelecekte oluşacak barlara bakılmadı.
- Kaynak: `gold_weekly_live.staktrakr_fourmetal_hourly_ohlca_research_v1`. 20.712 gerçek saatlik kayıt, dört metal için **5.178 ortak saat**, 2026-03-25–2026-10-29. İlk yayın saatleri tarihsel kaynaklarda kesinleşmiş değil. Veri StakTrakr'ın yayımladığı v2 günlük saatlik OHLCA arşividir.
- V22: orijinal V33 takvim ve model kararları, `outputs/v33_2026_jan_oct27_DAILY_all_models_and_outcomes.csv`. V22 kodu ve ağırlıkları **değiştirilmedi**.
- Ayrı değerlendirme 1: **orijinal V33 günlük altın fiyatının** ilerideki 5 tamamlanmış işlem günü boyunca ≥%4 düşüş etiketi: **146 olgunlaşmış fiyat günü**, bunların **18'i etiketli**.
- Ayrı değerlendirme 2: **aynı StakTrakr kaynağının** gün sonu son saatlik altın kapanışının ilerideki 5 tamamlanmış hafta içi fiyat günü boyunca ≥%4 düşüş etiketi: **148 olgunlaşmış fiyat günü**, bunların **21'i etiketli**.
- İki etiketin farklı çıkması **fiyat tanımları/takvim ve fiyatların aynı olmaması** nedeniyle mümkündür. Sonuçları birbirine karıştırmak yasaktır. Uyarılar tüm geçmiş günün tamamlanmış saatlik barlarından çıkarıldı; fiyatın **saatlik yayına gerçekten erişilebilir zamanı** doğrulanmadı.

## 4-saatlik koşullar

1. **Orijinal V22**: V22'nin zaten verdiği öncelikli uyarı.
2. **V22 VEYA XAU -%1,7952 / 4s**: 2024–2025 HistData XAU 4 saat günlük-aşırı-değer eşiği; ancak 2026 StakTrakr spot saatliği ile birebir aynı upstream kaynak **değil**. Sadece eşik transferini test etmek için korunmuştur; **Haziran'ı bu testte yakalamaz**.
3. **V22 VEYA dört metalin de ≤-%1 / 4s eşzamanlı hareketi**: Altın, gümüş, platin, paladyumun aynı 4 saat sonunda hepsinin -%1 veya altında olması. **2024–2025 StakTrakr saatlik verisi olmadığı için bunun -%1 eşiği eğitimden öğrenilmiş değildir; 2026 sonuçlarını inceledikten sonra araştırılan ad hoc koşuldur**. Kesin model seçimi olarak kullanılamaz.
4. **V22 VEYA XAU ≤-%1 ve kalan üç metalden en az 2'si ≤-%1,5**: alternatif koşul, yine keşif amaçlı.

## 2026 tarihsel skor — V33 fiyat etiketi (146 gün, 18 pozitif gün)

| Araştırma kuralı | Uyarı günü | 5g içinde ≥%4 ile eşleşen | Eşleşmeyen uyarı günü |
|---|---:|---:|---:|
| V22 | 23 | 7 | **16** |
| V22 veya eski XAU 4s eşiği | 28 | 8 | **20** |
| V22 veya 4 metal aynı 4s ≤-%1 | **42** | **9** | **33** |
| V22 veya XAU ≤-%1, başka 2 metal ≤-%1,5 | 43 | 9 | 34 |

**Aynı metal veri kaynağının fiyat etiketiyle skor (148 gün, 21 pozitif gün):**

| Araştırma kuralı | Uyarı günü | 5g içinde ≥%4 ile eşleşen | Eşleşmeyen uyarı günü |
|---|---:|---:|---:|
| V22 | 23 | 6 | **17** |
| V22 veya eski XAU 4s eşiği | 28 | 6 | **22** |
| V22 veya 4 metal aynı 4s ≤-%1 | **42** | **7** | **35** |
| V22 veya XAU ≤-%1, başka 2 metal ≤-%1,5 | 43 | 7 | 36 |

**Özet:** Dört metal -%1 koşuluyla, V22'ye göre **19 ek uyarı günü** ve **17–18 ek sonuçsuz uyarı günü** üretiliyor; gerçekleşmiş gelecek-5-gün ≥%4 düşüş etiketi yalnızca **1–2 ek uyarı günü** kazanıyor. Tek başına tercih edilecek kadar seçici değil. Sayılanlar bağımsız yanlış alarm epizotları değil, *gün* sayılarıdır.

## Beş büyük düşüş dönemi — önceki 10 işlem gününde ilk tarih

| Düşüş dönemi | Orijinal V22 | Eski XAU 4s eşiğiyle birleşim | Dört metal ≤-%1 birleşimi |
|---|---|---|---|
| Mayıs (başlangıç 13 Mayıs) | YOK | YOK | **7 Mayıs**, yaklaşık 4 işlem günü önce |
| Haziran ilk (başlangıç 4 Haziran) | YOK | YOK | **28 Mayıs**, 5 işlem günü önce |
| Haziran ikinci (başlangıç 17 Haziran) | 5 Haziran | 5 Haziran | 5 Haziran |
| Ağustos–Eylül (başlangıç 25 Ağustos) | 11 Ağustos | 11 Ağustos | 11 Ağustos |
| Eylül sonu (başlangıç 21 Eylül) | YOK | 16 Eylül | **10 Eylül**, 7 işlem günü önce |

**Önceden uyarılan büyük düşüş dönemi:** V22 **2/5**, V22+eski XAU4 **3/5**, V22+dört-metal -%1 **5/5**. **Bu yalnız arşivi olan Mart–Ekim dönemindeki beş olayın geçmişe dönük taramasıdır.** 2026'nın Ocak ve Mart büyük düşüşleri için aynı dört metal saatlik veri arşivi mevcut değil. Haziran ikinci ve Ağustos dönemi bağımsız büyük düşüş olay aileleri olmayabilir. Son 10 günün içindeki sinyal, ilerideki yalnızca 5 günde kesin %4 bekleyen uyarıyla **aynı ölçüt değildir**; dolayısıyla 5/5 olay kapsaması ile düşük 5g gün isabeti birbirini dışlamaz.

## Kritik kaynak duyarlılığı ve gerçek yeni bulgular

- **28 Mayıs** StakTrakr en sert 4s hareketi: XAU **-%1,757**, XAG **-%3,434**, XPT **-%2,881**, XPD **-%2,346**. Altın, eski `-%1,7952` HistData eşiğini *geçmedi*; eski XAU-only Haziran sinyali **yeni aynı kaynakta tekrar üretilemedi**. Buna karşılık **dört metal eşzamanlı düşüş** gerçek bir araştırma gözlemidir.
- **16 Eylül** StakTrakr en sert 4s hareketi: XAU **-%1,998**, XAG **-%2,604**, XPT **-%2,413**, XPD **-%2,836**. Dört metal anomalisi güçlü. Eylül yeni birleşiminde **10 Eylül** daha erken işaret var; bu, geçmiş fiyat gerçekleşmesini önceden bildiğimiz bir açıklama değildir.
- **7 Mayıs** altın 4s -%1,205, gümüş -%2,724, platin -%2,013, paladyum -%2,038: dört metal aday koşulu Mayıs ilk düşüşü öncesinde tetiklendi. Başka dönemlerde de tetiklenmesi **yanlış alarm sayısını artırıyor**.

## Karar ve sınırlar

- **Üretim V22'ye eklenmeyecek.** -%1 dört-metal koşulu 2026 sonuçları görülmüşken değerlendirilmiş olduğu için seçici başarı varsayımı/overfitting riski vardır. 2024–2025 dört-metal aynı kaynak saatliği yok; bu arşiv **25 Mart 2026'dan** başlar. Resmî makro DXY/GVZ/faiz saatlik kıyasını bu metal arşivi sağlamaz.
- Kaynakta ilk yayımlanma saatleri, orijinal V22'nin gerçekten canlı uyarı verdiği an ve farklı fiyat serilerinin kesin senkronizasyonu kanıtlanmadı. Kaynak dosyaları geriye dönük arşiv olarak elde edildi.
- Günlük gelecek-5-gün etiketi kullanıldığında dört metal koşulu %4 düşüşlerle çok zayıf eşleşir ve çok fazla sonuçsuz uyarı üretir. Olay kapsamı fazla görünse bile modelin **canlı tahmin gücü kanıtlanmış değildir**.
- Devam için: fiyat kaynaklarında zaman doğrulaması ve veri sağlayıcı geçişi; alarm günlerini alarm *epizotları* halinde birleştirip yanlış alarm maliyeti; 2024–2025 karşılaştırılabilir intraday dört metal bulma veya ileri tarihli prospektif gölge denemesi; yalnız belirlenen araştırma parametrelerini değiştirmeden ileri test.
- Bu script sadece Neon read-only sorgular çalıştırır, orijinal sinyalleri veya ANN modelini yeniden yazmaz.

**Çalıştırma:** `risk_v38_staktrakr_synchronous_fourmetal_shadow_v1.py`; `test_risk_v38_staktrakr_synchronous_fourmetal_shadow_v1.py`; Actions <https://github.com/ataullahturgut/sim3-automation/actions/runs/41111057653>, **6/6 regresyon testi PASS ve Neon replay success**.
