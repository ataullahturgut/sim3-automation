# GOLD — haftalık ANN + düşüş sinyalleri için veri hattının kontrollü yeniden açılması

**30 Ekim 2026. Kullanıcı onayı:** Güncel tahmin altyapısını devreye alma. **Aylık kalibrasyon:** ASKIDA, değişiklik yok.

## Hangi işler yeniden açıldı?

`main` üzerindeki `.github/workflows/gold-control-production-scheduler-v142.yml` 24 Ekim 2026'da açık kullanıcı talebiyle duraklatılmıştı. 30 Ekim'deki yeni onay üzerine aşağıdaki **veri toplama** zamanlamaları yeniden tanımlandı:

- Saatlik kanonik XAU durum alma: `17 * * * *`.
- Günde iki kez ana XAU/CBOE/Fed/GPR kaynakları: `45 23 * * *` ve `25 6 * * *`.
- FRED endeksleri: `15 1 * * 2-6`, `30 12 * * 2-6`.
- Twelve market endeksleri: `35 1 * * 2-6`, `45 12 * * 2-6`.
- NY17 kanonik XAU kapanışı: `10 22 * * 1-5`.
- `push` sadece zamanlayıcı dosyası ana dala birleştirildiğinde **tek seferlik `core-daily` veri telafisi** yapar. Standart manuel `workflow_dispatch` korunur.
- **SAATLİK `snapshot-refresh` OTOMATİK AÇILMADI.** Mevcut üretim motor durumları eski iken sahte güncellik yaratmamak için bu işlem yalnız manuel tetiklenebilir.
- Diğer duraklatılmış model/araştırma otomasyonları, özellikle `gold-h3-aurora-prospective-scheduler.yml`, değiştirilmedi.

## Gerçek Neon kontrolü (yeni veri akışı öncesi)

| Seri | 30 Ekim denetiminde son gözlem |
|---|---|
| `XAU_EOD_TWELVE_NY17` | 2026-10-20 21:00 UTC |
| `XAU_SPOT_XAUS` | 2026-10-21 07:37 UTC (endikatif) |
| `GVZ_CBOE`, `VIX_CBOE` | 2026-10-20 |
| `DGS10_FRB_H15`, `EFFR_NYFED` | 2026-10-19 |
| `decision_runs` | 0 kayıt |
| `decision_signal_snapshots` | 0 kayıt |

Bu nedenle kullanıcıya **30 Ekim için yeni ANN/V22/BASE14 tahmini üretildi** denilemez.

## Canlılık koruması

Yeni `gold_axis_2026/data_pipeline/gold_weekly_live_readiness_v1.py`:

1. Yalnız kaynak onaylı `canonical_latest` XAU-NY17, GVZ, VIX, DGS10 ve EFFR değerlerini inceler.
2. Her seri için **iş gününe göre** eskime penceresi kontrol eder; eski, eksik, kötü kalite ve gelecek zaman damgalı kayıtlar `BLOCKED`.
3. Veri yeni gelse bile `decision_runs` ile `decision_signal_snapshots` mevcut olmadığında veya run içeriği model kaynağı/ilk erişim sözleşmesi doğrulanmadığında `BLOCKED_NOT_LIVE` döner.
4. API Gold spot fiyatı gösterim amaçlıdır, model girdisinin yerini **tutamaz**.
5. Test ve durum raporuna veri tabanını yazma, model üretme veya alım/satım kararı verme izni **verilmedi**.
6. `gold-weekly-live-readiness-v1.yml` GitHub Actions haftada beş gün iki defa denetim JSON çıktısı üretir; ayrıca workflow değişince `push` ile kendi testini ve okumayı yapar.

## Henüz model tarafında açık kalanlar

1. **V34 haftalık ANN:** Tarihsel 2026 simülasyonu mevcut; yeni haftayı as-of veriyle tahmin eden dondurulmuş/versiyonlu üretim çalıştırıcısının ağırlıkları, preprocessing girdileri ve bağımsız yeniden üretim kontrolü ayrıca kanıtlanmalı. Orijinal ağırlık yerine V3 kalibratörü yeniden eğitilmiş V34 gibi sunulamaz.
2. **V22 ve BASE14:** 2026 güncel sinyal motoru öncesi tam as-of XAU/volatilite/makro kaynak ve eşik sürümü doğrulaması gerekli. Mevcut simülasyon sonucu günlük yeni sinyal değildir.
3. **Prospektif iz:** Her haftalık/sinyal forecast için `model_version`, `forecast_origin`, son erişilebilir gözlem zamanı, kaynağın hash'i, tarih ve ilk kayıt zamanı ile ayrı, değişmez karar raporu; ardından yayınlama kapısı.
4. **Gerçek GitHub Actions sonucu:** Dosyanın `main` dalına alınması cron'un tanımlanmasıdır; cron'un gerçekten çalıştığı, hesap yetkileri/secretlar, ilk veri telafi koşusu ve yeni Neon gözlemleri ayrıca **gerçek kayıtlarla** doğrulanır. Bu teyit alınmadan `LIVE_READY` ilan edilmez.

**Güvenlik:** Kullanıcının altın nakit/AL/ÇIK kararı ve portföy tarihi değiştirilmedi. Gerçek banka emri veya canlı alım-satım yok. Aylık kalibrasyon askıda.
