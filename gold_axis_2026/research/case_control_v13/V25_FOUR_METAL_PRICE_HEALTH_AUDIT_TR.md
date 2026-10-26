# V25 — 2010–2026 DÖRT METAL FİYAT VERİSİ SAĞLIK DENETİMİ

**Tarih:** 26 Ekim 2026 · **Neon:** Gold Control (salt SELECT) · **Statü:** KONTROLLÜ ARAŞTIRMA / TAM SERTİFİKASYON BEKLEMEDE.

**Önemli:** Ham fiyatlar, mevcut aylık tahminler, BASE14/CFTC21/V22 kararları ve üretim uygulaması değişmedi. Model eğitimi çalıştırılmadı; tüm fiyatlar önce doğrulanmalı.

## Hızlı sonuç

- **2010–2025**: Altın **4.041**, gümüş **4.041**, platin **4.040**, paladyum **4.040**. Toplam **16.162** fiyat kaydı, dört metal için çoğu gün ortak; 2021-12-24 sadece AU/AG var (metal tatil takvimi farkı, otomatik hata sayılmadı).
- Kaynak, 2010–25 için **tek sabit StakTrakr Git commit** + LBMA etiketli eski veriler; 2026 için **ayrı bir sabit Git snapshot**. Kaynak tutarlılığı, resmî tarihsel ilk yayın/PIT tutarlılığının kanıtı değildir.
- 2010–25 altında tek günlük **%10'un üzerinde fiyat değişimi yok**; dört metalde 27 Şubat 2026 seviyesinde toplu düşüş-ertesi gün geri sıçrama yok. 10% üzeri bazı gümüş/paladyum/platin hareketleri gerçek piyasa dönemi olabilir; otomatik silinmemiştir.
- Bağımsız günlük fiyat setiyle (ayrı spot/kapanış tanımı; altın, gümüş, platin; **2010–2024** mevcut kısmı) **11.068 tarih-metal karşılaştırması** yapıldı. **49 eşleşmede mutlak fark >%5** (AU=3, AG=39, PT=7). Bunlar tek başına **49 yanlış veritabanı kaydı** demek değildir. Genel medyan mutlak fark: AU %0,414, AG %0,736, PT %0,717. Dış seri 2025'i kapsamıyor ve palladyumu kapsamıyor.
- Daha eşdeğer Gold London Fixing referansı olan Westmetall ile **2024 253, 2025 252, 2026 200** ortak altın günü karşılaştırıldı. 2024'te 252/253 ve 2025'te 252/252 **tam eşleşiyor**. 2024'teki tek büyük farkın Westmetall'deki yazım hatası olduğu bağımsız kaynaklarla doğrulandı. 2026'da 27 Şubat'taki **Neon hatası** ve 2 Ocak'taki **Westmetall yazım hatası** büyük fark oluşturuyor; ayrıca daha küçük fiyat tanımı farkları var.
- **27 Şubat 2026 DÖRT METAL TOPLU HATA**: Altın 3.516,02, gümüş 62,15, platin 1.585,39, paladyum 1.201,26. Önceki/sonraki seanslarda hepsi yaklaşık %28–32 düşüş ve %48–52 geri sıçrama gösteriyor. Aynı tarihte bağımsız piyasa referansları sırasıyla yaklaşık altın AM **5.174,10**, gümüş London fix **89,975**, platin AM **2.365**, paladyum AM **1.818** gösteriyor. Dış kaynak fiyat tanımları aynı seriye körlemesine aktarılmaz; asıl veri **karantinada**.

## Üç uyuşmazlığın kesin ayrımı

| Tarih | Neon altın | Westmetall | Bağımsız doğrulama | Hüküm |
|---|---:|---:|---:|---|
| 17.05.2024 | **2.381,75** | 2.831,75 | 321gold ve BullionWorld: 2.381,75 | Dış sitede rakam hatası |
| 02.01.2026 | **4.386,85** | 1.386,85 | GoldPriceOz ve Agosi: 4.386,85 | Dış sitede rakam hatası |
| 27.02.2026 | 3.516,02 | **5.174,10** | Diğer Londra fixing kaynaklarında 5.174,10 | Neon araştırma fiyatı hatalı |

Dış kaynaktaki iki hata **veritabanına kopyalanmadı**. 2026-02-27 hatası da otomatik AM/PM fiyat değişikliğiyle düzeltilmedi; tekil 27 Şubat AM değeri ile bütün StakTrakr serisinin aynı saat/tanım olup olmadığı ayrıca kanıtlanmalı.

## Aylık H=1 tahmin üzerindeki etkisi

Şubat 2026 ham StakTrakr ortalaması (her metalde 20 hafta içi gözlem) ve **yalnızca kontrol amacıyla** şüpheli tek gün çıkarıldığında:

| Metal | Ham Şubat ort. | 27 Şubat hariç ort. | Fark |
|---|---:|---:|---:|
| AU | 4.934,0445 | 5.008,6774 | +74,6329 USD/ons |
| AG | 81,1008 | 82,0982 | +0,9974 |
| PT | 2.099,5890 | 2.126,6521 | +27,0631 |
| PD | 1.706,3385 | 1.732,9216 | +26,5831 |

**Şüpheli günü hariç tutan ortalama doğrulanmış nihai Şubat değeri DEĞİLDİR.** Sadece hatalı günün etkisini ölçen bir senaryodur. Şubat 2026 **gerçekleşen hedefi** ve Mart 2026 kökenli VW/MR türü fiyat girdileri kirlenmiş olabilir. Önceki veriyle öğrenilmiş modellerin eski tahmin kayıtları değiştirilmedi; fiyat serisinin 2010–2025 PIT uygunluğu hâlâ ayrı sorundur. Aylık modelde tam tekrar eğitim / hata kıyaslaması temiz fiyat tanımı oturmadan **yapılmadı**.

## Raporlanan sınıflar

- `KNOWN_CORRUPT`: 2026-02-27 dört metal. Hiçbir model girişinde kesin/sağlıklı fiyat olarak kabul edilmemeli.
- `EXTERNAL_REFERENCE_TYPO`: Westmetall 2024-05-17, 2026-01-02. İç fiyat bağımsız kaynaklarla destekleniyor.
- `EXTERNAL_DEFINITION_REVIEW`: 2010–24 farklı kapanış/spot kaynağıyla uyuşmayan 49 fiyat. Resmî aynı seans fixing kanıtı olmadan hatalı diye etiketlenmez.
- `COVERAGE_NOT_YET_CERTIFIED`: 2010–25 Pd günlük dış karşılaştırma, 2025 AG/PT/PD ve tüm 2026 4-metal günlük bağımsız standartlaştırma.
- `PIT_NOT_CERTIFIED`: Bir araştırma Git snapshot'ının geçmişteki ilk yayın sürümü olduğunu doğrulayan kanıt yok; tarihsel alarm ve tahmin başarılarını canlı kanıt olarak sunma.

## Teknik kanıt / tekrar üretim

Aşağıdaki kaynak denetimi dosyaları bu dalda yer alır:

- `outputs/v25_independent_price_yearly_comparison.csv` — 2010–25 AU/AG/PT için her yıl kaç fiyatın dış kaynağa eşleştiği ve fark dağılımları.
- `outputs/v25_independent_price_large_discrepancies.csv` — 49 fiyat seviyesi farkı, tarihli inceleme listesi.
- `outputs/v25_gold_discrepancy_adjudication.csv` — iki dış referans hatası ile bir gerçek araştırma veri hatasının kanıtları.
- `outputs/v25_2026_fourmetal_confirmed_outlier.csv` — 2026-02-27 dört metal karantinası.
- `outputs/v25_february_monthly_target_sensitivity.csv` — kirli Şubat değerlerinin aylık hedefe etkisi.
- `outputs/v25_historical_partial_holiday.csv` — 2021-12-24 Pt/Pd eksikliği; altın ve gümüş o gün mevcut.
- `risk_v25_gold_westmetall_crosscheck.py` — 2024/2025/2026 gold fixing taraması ve özet metrik üretimi. Dış veri yıl tablosunun bütünü depoya kopyalanmaz.
- `risk_v25_price_health_gate.py` — kirli fiyatların sağlıklı / üretime hazır diye sertifikalandırılmasını **araştırma akışında engeller**. Eski uygulamanın tamamına otomatik bağlanmış değildir.
- `.github/workflows/gold-v25-price-health.yml` — otomatik kontrol ve test. Dış bağımsız karşılaştırma raporları GitHub Actions artifact bölümünde.

```bash
cd gold_axis_2026/research/case_control_v13
python risk_v25_price_health_gate.py --mode report
python risk_v25_gold_westmetall_crosscheck.py
python -m unittest -v test_risk_v25_price_health_gate.py test_risk_v23_calendar_safe_audit.py
# Bilerek hata üretir: şüpheli veriyle "tam temiz" sertifikası verilemez
python risk_v25_price_health_gate.py --mode certify
```

**Sonuç:** **2010–2025 için iç veri taraması ve 11.068 fiyatlı dış örnek karşılaştırması yapıldı**, 2024–26 altın büyük ölçüde aynı London fixing veri tanımıyla karşılaştırıldı, **2026-02-27 dört metal sorunu kanıtlandı**. Ancak **tüm 2010–2026 dört metal fiyatlarının temiz/PIT-sertifikalı olduğu henüz söylenemez**. Kaynak birliği ve eksik palladyum/2025–2026 farklı metal referans doğrulaması tamamlanmadan orijinal aylık tahmin hataları nihai başarı olarak raporlanmamalıdır.

Resmî LBMA/LPPM tarihsel ticari benchmark tabloları ilgili lisans ve erişim koşullarına tabidir (https://www.lbma.org.uk/prices-and-data/lbma-precious-metal-prices ve https://www.lppm.com/data). Bu yüzden fiyatlar üçüncü taraf geçmiş serilerle **araştırma amaçlı** kontrol edilmiş; tarihsel tam resmî benchmark sertifikası uydurulmamıştır.
