# V4 ve V5 bilimsel sonuç denetimi — Şubat–Eylül 2026

**Tarih:** 2026-10-15. **Durum:** Historical shadow only / V5 bilimsel kabul REDDEDİLDİ. Kod önceden görülmüş döneme sonradan geliştirilmiştir, sonuç bağımsız kör OOS değildir.

## Zaman disiplini ve veri
- V4 politika: `V4_ADAPTIVE_CARRY_GUARD_SHADOW_20261015`; 2026 Mart–Eylül verileri görülmeden [deney protokolü](V4_POST_FEB_2026_PRE_REGISTERED_EVALUATION_20261015.md) GitHub'da donduruldu. V4 Mart–Eylül sonucuna göre değiştirilmedi.
- V5 politika: `V5_SLOW_TREND_PROTECTION_SHADOW_20261015`; 2026 Mart–Eylül sonucunun ardından [hipotez ve eşikler](V5_SLOW_TREND_PROTECTION_PRE_REGISTER_20261015.md) ayrı kaydedildi. 2026 üzerinde başarısı kör test değildir.
- Geçmiş eğitim: 2020–2025 gerçek XAU M15'ten türetilmiş toplam 10.850 tamamlanmış 3h satır; stres epizodu 65, bunlar **65 bağımsız kanıtlı ekonomik olay değildir**. 2023 kaynakta bar kapsamı eksiktir. As-of haber ilk yayımı ve makro beklenti yok; G05-C/G06-B bilinmeyen ekonomik mekanizma.
- 2026 Mart–Eylül: HistData kaynak XAUUSD 15m'den tamamlanmış 3h kesit, 1.123 satır (Mart 153, Nisan 160, Mayıs 156, Haziran 164, Temmuz 174, Ağustos 158, Eylül 158 UTC). Pinned Git blob `860917258c84a86a210d8c7f44655d46d878470e`. Sep30 21UTC (TR Ekim1 00:00) Eylül sonuçlarının dışında tutulur.
- Şubat başlangıcı Ocak 2026 V1 sonundan **119,75391720039644 USD nakit**. Şubat'tan Eylül'e **tek portföy**: her ay yeni 100 USD, sıfırlanan altın veya yeni verilerle öğrenme yok. Eğitim RV eşikleri 2026-01-01'de kilitli.
- İşlemler Türkiye saati 09:00, 12:00, 15:00; altın MID/next-open işlem vekili. Alış ve satış yönünün her birinde %0,8 komisyon; son açık altın pozisyonu için teorik çıkış ücreti. Gerçek banka bid/ask, slip ve spread yok; bu gerçek kullanıcı nakdi veya emir sonucu değildir.

## Eylül sonu sonuç, Şubat 119,75 USD başlangıcına göre

| Model / strateji | Son net USD | Başlangıçtan getiri | Maksimum portföy gerilemesi |
|---|---:|---:|---:|
| V4 dondurulmuş model | **96,706968** | **-%19,25** | **%26,68** |
| V5 ayrı aday | **107,832861** | **-%9,95** | **%17,28** |
| Hiç altın almadan nakit | 119,753917 | %0 | 0 (faiz/kur farkı hariç) |
| Şubat 2 TR 09:00 ilk bankacılık fiyatında al ve Eylül sonuna kadar tut | 107,741250 | -%10,03 | Bu raporda bağımsız risk dizisi hesaplanmadı |

V5, V4'e karşı yaklaşık **11,13 USD** kaybı azaltmıştır. Fakat nakitte kalmanın **11,92 USD altında** ve pasif altının yalnız **0,09 USD üzerinde** kalmıştır. Şubat'ın tek aylık 122,87 USD kârı sekiz aylık strateji başarısı değildir.

## Zaman içinde net değerin ilerlemesi (her ay sonu, aynı portföy)

| Türkiye takvim ayı | V4 | V5 | Nakit | İlk TR09 AL/TUT |
|---|---:|---:|---:|---:|
| 2026-02 | 122,87 | 122,87 | 119,75 | 136,39 |
| 2026-03 | 107,89 | 116,65 | 119,75 | 120,20 |
| 2026-04 | 107,18 | 112,65 | 119,75 | 119,40 |
| 2026-05 | 105,70 | 110,76 | 119,75 | 117,76 |
| 2026-06 | 93,65 | 107,39 | 119,75 | 104,33 |
| 2026-07 | 94,05 | 104,63 | 119,75 | 104,78 |
| 2026-08 | 103,12 | 112,03 | 119,75 | 114,89 |
| 2026-09 | 96,71 | 107,83 | 119,75 | 107,74 |

V4 31 Mart 2026 09:00 TR'de yeniden GOLD'a geçip Eylül sonuna kadar altını tuttu; Mart öncesi 2 satış ve Mart içinde tekrar alışlarla maliyet ödemiş oldu. 31 Mart sonrası yavaş düşüşü yakalayamaması V5'in **tespit edilmiş** düzeltme hedefidir.

## Yıllık V4 vs V5 bilimsel çapraz kontrol

| Takvim yılı | V4 USD | V5 USD | Aynı ilk fiyattan AL/TUT | V4 işlemi | V5 işlemi |
|---|---:|---:|---:|---:|---:|
| 2023* | 110,57 | 107,68 | 110,32 | 1 | 6 |
| 2024 | **125,52** | 111,23 | 124,43 | 1 | 10 |
| 2025 | **141,13** | 135,04 | 161,15 | 5 | 10 |

*2023 veri kapsamı eksik. Her yıl bağımsız 100 USD başlangıç; fiyat verisi/kapanış temelinde geriye dönük rapor. 2024 ve 2025'in performansı daha önce araştırıldığı için bunlar da güçlü kör OOS değildir.

**V5 sonuç:** Trend filtrelemesi 2026 risk düşüşünü sınırlarken 2024/25 yükselişlerinde fazladan komisyon ve fırsat kaybı yarattı. Risk-ödül ihtiyacı tek eşikli rejim kuralıyla çözülmemiştir.

## Otomatik bilimsel kabul kapısı
`scientific_promotion_gate.js` 2024/2025 eksiksiz yıllarında V5'in V4 ve AL/TUT ile performans, maksimum gerileme ve işlem sayısını denetler. V5, iki yılda da V4'ten daha az getirmiş, AL/TUT'tan daha az getirmiş ve **daha çok işlem yapmıştır**. Ayrıca gerçek banka bid/ask yok, ekonomik haber firstprint yok ve bağımsız ileri doğrulama yok. Sonuç **REJECT_PROMOTION**, `authorized=false`. Program model yükseltmez.

## Sonraki bilimsel adımlar
1. 2023 eksik veri kapsamını gerçek kaynaktan tamamlamadan ve 2020–2025 olay düzeyi ekonomik ilk yayın kaynaklarıyla G05/G06 doğrulamadan probabilistik karar iddiasına geçme.
2. Reel bankadaki BID/ASK + işlem saatine göre makas ölçülmeden komisyon sonrası kesin kâr iddiası yok.
3. Her bağımsız epizotta iki fonksiyonlu değerlendirme: erken toparlanma/UP katılımı ile büyük -%3 altı düşüş maruziyeti; sadece ay sonu net USD ile optimize etmek başarısız.
4. Yeni araştırmada tek yıllık veya Şubat–Eylül dönemine aşırı uydurma yerine henüz model yazarının görmediği yeni zaman diliminde sürüm kilitli prospektif test. Başarısız adaylar aynı dosyada tutulmalı; başarı seçmeciliği yasak.
5. Aylık sisteme geçişi yalnız başarısı kanıtlanan karar motoruyla yap; teknik replay, ekonomik DNA'nın gerçekten fiyatı açıkladığı anlamına gelmez.

**Önemli:** Bu çalışma finansal tavsiye veya bankaya emir verici sistem değildir; 2026 fiyatlarının kayıttaki örnek anları ve kısıtlı işlem fiyatı vekili kullanılmıştır.
