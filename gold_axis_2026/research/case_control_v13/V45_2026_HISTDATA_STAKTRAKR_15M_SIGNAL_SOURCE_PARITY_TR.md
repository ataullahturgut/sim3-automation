# 31 Ekim 2026 — HISTDATA VE STAKTRAKR 15m ÇIKIŞ SİNYALİ KAYNAK PARİTESİ

**Kaynak: Neon Gold Control gerçek, kaynak kaydı iki ayrı araştırma tablosundan SQL JOIN ile doğrulandı.** İki kaynak 2026 Ağustos–Eylül ortak aralığında farklı ilk-yayın/providing standardı taşıyor. İkisi de gerçek banka fiyatı veya prospektif ilk-yayın olarak onaylanmadı.

## Doğrudan eşit UTC 15-dk pencerelerin karşılaştırması

- Tablo A: `public.gold_research_histdata_xau15m_candidate` XAU/USD 15 dakikalık **non-canonical** araştırma fiyatı.
- Tablo B: `gold_weekly_live.staktrakr_fourmetal_15m_snapshot_research_v1` `metal='AU'` kamuya açık StakTrakr spot quote.
- Sadece **tam UTC 15m başlangıç zamanı eşleşen** fiyatlar: **3.858** nokta, 2026-08-02 23:00–2026-09-30 23:45 UTC.
- Ortalama yönlü kaynak fiyat farkı: **+%0,007** (StakTrakr/HISTDATA − 1).
- Fiyat *mutlak* farkı ortanca: **%0,112**, p95: **%0,422**, maksimum: **%2,024**. Mutlak fark >%1: **15** nokta, >%5: **0**.
- Yalnızca **tam 4 saat önceye ait 16 adet ardışık ortak fiyat** mevcutken 4s getiri karşılaştırılabilir; önceki 96 bar destek fiyatı da var olmalı: **3.085** ortak 4s nokta.
- HistData 4s≤−%1 işareti: **98** nokta; StakTrakr 4s≤−%1 işareti: **100** nokta; sinyal durumu **72 noktada farklı**. Bu sayı `98 vs 100` net farkından çok daha büyük çünkü kaynakların açılıp kapandığı zaman pencereleri farklıdır.
- HistData (4s≤−%1 VE önceki 96 bar fiyat dibinin altı): **35** nokta; StakTrakr aynı ön-koşullar: **32** nokta; **49 noktada kırılma durumu farklı**.
- Dört saatlik getirilerin mutlak farkı p95 **0,623 yüzde puan**.

Bu hesap **V22 WATCH uygulanmış gerçek çıkış performansı değil**, fiyat/kaynak uyuşma ve altyapı denetimidir. WATCH tepe şartı da dahil edilmedi. Fiyat tanımları birbirinden farklı olduğundan `V43` 2026 HistData etkinliğini **StakTrakr güncel feed üzerinde hazır-live algılama gücü** kabul etmek yanlıştır. İlk kaynakta çalışan fiyat eşiği aynı anda diğerinde farklı koşullar tetikleyebilir.

## Kesin karar

1. 2024–2025 saatlik StakTrakr dört metal verisi bulunmadığından kaynak-paritesi aynı biçimde 2024/25 çapraz doğrulanamaz.
2. V44/V45 2024–26 historical end-of-episode iyileşmesi, StakTrakr canlı spot verisine **doğrudan taşınamaz**. Yeni kaynağın basamak/oynaklık/fiyat feed tanımını prospektif olarak ayrı kalibre etmek gerekir.
3. V46'nın 15 dakikalık yeni fiyat ilk-görülme günlüğü **asla orijinal provider-firstprint ile aynı** sayılmamalı.
4. Canlı V22 firstprint kaynak yeterlilik kontrolü hâlen **KAPALI**; otomatik ALTIN AL/SAT/ÇIK emri veya sinyal üretmek için onay yok.

### Yeniden üretim SQL (salt-okunur, SQL console)
```sql
WITH sr AS (
 SELECT DISTINCT ON(window_start_utc) window_start_utc ts,spot_usd_oz::float8 spot
 FROM gold_weekly_live.staktrakr_fourmetal_15m_snapshot_research_v1
 WHERE metal='AU' AND window_start_utc>='2026-08-01' AND window_start_utc<'2026-10-01'
 ORDER BY window_start_utc,collected_at_utc DESC
), joined AS (
 SELECT s.ts,s.spot,h.close_price::float8 hist,
 100*(s.spot/h.close_price::float8-1) diff
 FROM sr s JOIN public.gold_research_histdata_xau15m_candidate h ON h.bar_start_utc=s.ts
)
SELECT count(*) pairs,
 round(avg(diff)::numeric,3) mean_diff_pct,
 round(percentile_cont(.5) within group(order by abs(diff))::numeric,3) median_abs_pct,
 round(percentile_cont(.95) within group(order by abs(diff))::numeric,3) p95_abs_pct,
 round(max(abs(diff))::numeric,3) worst_abs_pct
FROM joined;
```

**Bu belge başarı promosyonu değil: kaynak farkı sebebiyle canlı sinyalin bloke edilmesi gerektiğini doğrulayan denetimdir.**
