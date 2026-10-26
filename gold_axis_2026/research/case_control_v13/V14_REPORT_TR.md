# V14 — Bağımsız risk katmanı entegrasyonu (GÖLGE MOD)

Kapsam: 2010–2022 tarihsel öğrenim, 2025 doğrulama ve 2026 stres;
**orijinal BASE14/CFTC21 ve Neon değiştirilmedi**.
Bu kod, eski model kırmızı vermese de bağımsız skor üretir. Nihai alarm
yalnız 2025 kapısını geçen aday varsa gölge olarak hesaplanır.

- Tarihsel olay sayısı: 27; eğitime alınan olay: 27; birleştirilmiş bağlam: 15.
- 2013 olayları eğitime alınan: 5 olay.
- Geçerli 2025 aday: 0.
- Seçilen araştırma adayı: BASE14.
- Doğrulama yakalaması tam, ama yanlış alarm şartı başarısız bağımsız tanı modeli: V14_NO_CFTC_GBM_Q95_INDEPENDENT.

| 2026 model | Kırmızı | Ertesi gün ≥%3 | 5g risk kümesi | Yanlış alarm günü |
|---|---:|---:|---:|---:|
| BASE14 | 50 | 4/4 | 4/4 | 40 |
| CFTC21 | 32 | 4/4 | 3/4 | 25 |
| V14 gölge | 50 | 4/4 | 4/4 | 40 |
| V14 bağımsız (reddedildi) | 118 | 3/4 | 4/4 | 108 |

**Üretim kapısı kapalıdır:** ilk yayın sayısal veri vintage ve gerçek seans içi
başlangıç doğrulanmadı. 2026 geçmişte görüldüğünden kör başarı kanıtı değildir.
Gelişme bulunmadıysa gölge sonuç BASE14 referansını gösterir; yeni model başarılı sanılmamalıdır.
Tam adaylar: outputs/v14_metrics_2025_2026.csv.

