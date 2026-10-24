# GOLD RISK CFTC V2 — bağımsız 2023–2025 öğrenme / 2026 araştırma replay

**Durum 24 Ekim 2026:** 21 özellikli bağımsız piyasa anomalisi/risk katmanı gerçek tarihsel verilerle kuruldu, yerelde test edildi. Ana ANN aylık/haftalık/günlük fiyat tahminlerine veya Neon'a yazım YOK. Üretime alınmadı.

**Kod:** `gold_axis_2026/tools/gold_risk_cftc_independent_overlay_v2.py`.
**Yerel doğrulama:** 873 tarihsel ortak veri satırı; 2025 skor 232 gün; 2026 skor 161 gün; CFTC çift kontrat kimliği; 2025 gecikmiş yayın; 2026 Ocak29 fiyat etkisi; kaynak SHA ve sızıntı kapıları: PASS.

## Kaynaklar ve zayıflıkları

- CFTC resmî dört haftalık ZIP (2023–2026), 398 satır = GC 199, SI 199; **COMEX GOLD 088691**, **COMEX SILVER 084691**. Gold Micro farklı kontrat, dışarıda.
- Normal CFTC raporları için **rapor günü +7 gün** tutucu vekil kabul edildi, tüm haftaların gerçek kamu yayın anı ayrı sertifikalı değil. 2025 shutdown 13 olağandışı rapor için CFTC 9147-25 takviminden **gerçek yayım günü +1** uygulandı.
- CFTC raporunun kullanılabildiği tarihten itibaren 21 takvim gününü aşarsa sinyal için veriyi kullanmıyoruz (2025 shutdown bu nedenle bazı günler tamamen dışarıda). Eksik günler doldurulmuyor.
- 14 eski özellik: 6 metal trend/oynaklık/RSI, 4 GVZ, 2 Fed H10 Broad USD, 2 ABD nominal 10y faiz. H10 resmî izleyen pazartesi 16:15 New York sonrasında, H15 en az ertesi gün; piyasa fiyatlarının günlük **ilk baskı vintajı ispatlı değil**. Dolar/Faiz arşivi 2023–2026; yeni geçmiş yayımlanma istisnaları ayrıca denetlenmeli.
- 7 yeni CFTC özelliği: GC ve SI managed-money net/OI; GC 1-hafta ve 4-hafta değişim; SI 4-hafta değişim; GC−SI crowding spread; GC managed money short/OI.
- SPDR GLD 2023–2025 752 sayısal günlük kayıt indirilmiş **ama ilk yayın anı/point-in-time teyidi eksik**; bu V2 ana risk skorunda YOK. CME GC/SI resmî marj PDF indirme engeli, SLV doğrulanmamış: ikisi de YOK. Eksikleri sıfırla doldurma YOK.
- 2026-02-27 araştırma kaynağında bilinen sahte günlük spot fiyatı ve 20 işlem günü geçmiş/5 işlem günü gelecek hedef pencereleri karantinada. Resmî günlük işlem kapanış fiyatı ile gerçek zamanlı işlem/tahmin saati aynı kabul edilmez.

## Makine öğrenimi sözleşmesi

**RobustScaler + IsolationForest(200, seed=1701)**; yalnız EĞİTİM verisi ile 90. yüzdelik (sarı) ve 95. yüzdelik (kırmızı) skor eşiği. Etiketler eğitime **girmiyor** (denetimsiz anomali). 2023–2024 eğitim, 2025 teşhis (475 eğitim orijini). Daha sonra 2023–2025 eğitim, 2026 Ocak–21 Eylül stres testi (707 eğitim orijini). 2026 model eşiğini seçmekte asla kullanılmıyor.

**Önemli:** 2023 ve 2024 günlük araştırma fiyat kaynağında ertesi gün >=%3 düşüş yok; bu nedenle mevcut eğitimden gözetimli nadir çöküş olasılığı öğrenme iddiasında bulunulmuyor. Önceden 2025 ve 2026 olayı görülerek araştırma hipotezi kurulmuş olduğundan bu stres sınaması *model fikri açısından gerçekten kör* değildir. ANN tahmin hata olasılığı ayrıca ölçülmedi.

## Aynı orijin günlerinde kıyas — KIRMIZI uyarı ve ertesi gün altın >=%3 düşüş

| Dönem | incelenen gün | risk modeli | KIRMIZI alarm günü | Ertesi gün sert düşüş kapsaması | Kırmızı yanlış alarm günü |
|---|---:|---|---:|---:|---:|
| 2025 | 232 | İlk 14 özellik | 31 | 2 / 3 | 29 |
| **2025** | **232** | **14 + 7 CFTC** | **31** | **3 / 3** | **28** |
| 2026 | 161 | İlk 14 özellik | 51 | 4 / 4 | 47 |
| **2026** | **161** | **14 + 7 CFTC** | **29** | **4 / 4** | **25** |

Tam 2025 yılı 253 piyasa günü olsa da CFTC'ye ait bazı hafta/süre blokları kamu yayın gecikmesi ve stale-data kapısından elendi; yalnız ortak 232 gün kıyaslandı. 2026 161 analiz günü kaynak sorunlu Şubat 27 ve 5g hedef olgunluğu sonrası dışlamalar ile sınırlı.

**Beş günlük %5 drawdown hedefinde CFTC eklemek maliyetli:** 2025 ilk 14 skor 4/5, yeni 5/5; 2026 ilk 14 skor **9/13**, yeni **6/13**. 13 pozitif tarih, 13 ayrı çöküş anlamına gelmez, çakışan beş günlük origin etiketleridir.

Risk olay kümelerinin temsilî 4-gün aralık kuralı: 2025 31 KIRMIZI gün = 6 uyarı kümesi, 3 kümede ertesi gün >=%3 düşüş gözlendi; 2026 29 KIRMIZI gün = 6 uyarı kümesi, 2 kümede ertesi gün >=%3 düşüş gözlendi. Küme sayıları hassas episode-labelling çalışması değil, sunum amacıyla kümelenmiş uyarılardır.

## Gerçek 2026 Ocak kontrolü (geçmişe dönük)

- İlk uzun kırmızı uyarı kümesi **23 Ocak 2026**, 30 Ocak sert düşüşü ve 2 Şubat devamı öncesinden başlıyor. 22 Ocak yeni karma model SARI, CFTC'siz GVZ modeli KIRMIZI.
- **26, 27, 28, 29, 30 Ocak** yeni karma model KIRMIZI.
- **29 Ocak** risk skoru .6487; raporda kullanılan son GC ve SI CFTC pozisyon günü **20 Ocak**, **27 Ocak** tarihinden itibaren kullanılabilir kabul ediliyor. 27 Ocak *pozisyon raporunu* 29 Ocak'ta model görmüş gibi kullanılmadı.
- 29 Ocak kapanışı sonrası 30 Ocak referans fiyat düşüşü yaklaşık **-%7.9657**, sonraki 5 gün minimum referans fiyatı yaklaşık **-%14.84**. 29 Ocak kendi içinde sert zirve-dip gerilemesi de yaşandığından, "ilk çöküşten önce kusursuz tahmin" iddiası yasak.
- 2026 diğer >=%3 günlük düşüşler için uyarılı orijinler: **30 Ocak → 2 Şubat, 4 Şubat → 5 Şubat, 9 Haziran → 10 Haziran**.
- Yalnız CFTC yedi özelliğinden oluşan model 2025 ve 2026'da hiç KIRMIZI alarm üretemedi: CFTC tek başına kırılma tespit etti diyemeyiz.

## Nihai karar

1. V2 **araştırma prototipi** başarılı çalıştı; verisi/gecikmesi zayıf aileleri otomatik karantinada tuttu.
2. CFTC kompozitinde tek-gün <% -3 kapsamı yükseldi, ve 2026 yanlış alarm gün sayısı düştü. **5g ciddi düşüş kapsaması geriledi**. Dolayısıyla tek eşikli "nihai en iyi model" seçimi henüz haklı değil.
3. Risk çıktılarını gerçek ANN tahmin kalıntılarıyla bağımsız dönemde eşleştirene kadar **'bu tahmin hatalı olacak' kalibre uyarısı** yoktur.
4. Sonraki deney yalnız eğitim/teşhis 2023–2025 verisiyle, epizod-tabanlı ve duyarlık/yanlış alarm dengeli; 2026 dönemine bakarak eşik uydurmayacağız.
5. **Otomatik GitHub scheduler'lar kapalı**, ana tahmin modelleri, Neon ve uygulama değiştirilmedi.
