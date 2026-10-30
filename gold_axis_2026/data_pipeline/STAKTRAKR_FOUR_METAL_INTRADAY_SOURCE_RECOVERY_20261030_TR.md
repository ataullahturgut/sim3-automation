# StakTrakr dört metal intraday veri kurtarma — doğrulanmış uygulama kaydı

**Doğrulama tarihi:** 30 Ekim 2026, UTC. **Neon:** Gold Control, `winter-art-94880101`.

## Kaynak kimliği ve kritik ayrım

Kaynak StakTrakr; günlük veriden **farklı** iki gerçek intraday fiyat ürünü bulundu:

1. `lbruton/StakTrakrApi`, `api` dalı, `data/v2/spot/{xau,xag,xpt,xpd}/YYYY/MM/DD.json`: StakTrakr'ın 15 dakikalık fiyat örneklerinden derlediği *saatlik OHLC(A)* dosyaları. Arşiv doğrulanmış başlangıcı **2026-03-25**. Kaynağın kendi 2026-08-16 release notları önceki günlerde saatlik verinin başlamadığını teyit eder; n=1 günlük sahte örnekler atılır.
2. `lbruton/StakTrakrApi`, `api` dalı, `data/15min/YYYY/MM/DD/HHMM.json`: her dört metalin aynı UTC çeyrek saatinde kaydedilmiş tarihsel fiyat anlık görüntüsü. Kaynak etiketi `seed`: StakTrakr'ın `devops/pollers/shared/api-export.js` kodunda mevcut Turso `spot_prices` kayıtları `formatSpotRow(row, "seed")` ile dışa aktarılır. *Bu etiket kendi başına ilk yayın/firstprint sertifikası değildir.* Arşiv yalnız **2026-08-01** sonrasında mevcut.

Her iki ürünün upstream veri sağlayıcısı zaman içinde değişebilir; API kimliğinin sabitliği tek bir kesintisiz birincil piyasa fiyat sağlayıcısı demek değildir. USD/ons spot referansı; işlemlerin gerçekleştiği NY17 kapanış fiyatı değildir.

## Gerçekten yazılan Neon tabloları

| Tablo | Dönem | Dört metal toplam | Ortak saat/tarih |
|---|---|---:|---|
| `gold_weekly_live.staktrakr_fourmetal_hourly_ohlca_research_v1` | 25 Mart–29 Ekim 2026 | **20.712** (5.178 × 4) | 5.178 saat, 216 farklı gün |
| `gold_weekly_live.staktrakr_fourmetal_15m_snapshot_research_v1` | 1 Ağustos–29 Ekim 2026 | **34.348** (8.587 × 4) | 8.587 çeyrek saat, 90 farklı gün |
| **Bu kurtarmada toplam** | | **55.060** | |

**Saatlik kaynak dosyası olmayan günler:** 2026-04-10, 2026-07-19 ve 2026-07-22. Kaynakta mevcut olmayan günler saatlik olarak doldurulmadı.

**15 dakikalık kaynak boşlukları:** 90 gün × 96 = 8.640 çeyrek saat beklenirken 8.587 bulunabildi; **53 eşzamanlı çeyrek saat** eksik/geçersiz. Eksiklerin 17'si 23 Ağustos'ta, 17'si 26 Eylül'de; kalanları farklı günlerde. Dört metalin birinin eksik olduğu çeyrek saatler komple reddedildi.

Saatlik gerçek veri oranı: 20.326 satır 4 örnekli, 118 satır 3 örnekli ve 268 satır 2 örnekli; **tek örnekli günlük sahte saatlik satırları** kabul edilmedi. 15m ve 1h kaynakları aynı 2.158 saatlik pencerede karşılaştırıldı. Her dört metalde kapanış fiyatı yüzde farkı p95 **%0,00000**, en yüksek yüzde fark sırasıyla AU %0,1683, AG %0,3635, PT %0,3126, PD %0,3229.

**Veri güncelliği:** 30 Ekim UTC günü tamamlanmadan o tarihe ait gün sonu ve tam kaynak arşivini tamamlandı saymayın. Saatlik kaynak yayını önceki UTC günün kapanışını izler.

## Gerçek çoklu metal dört saatlik gözlemler

Aynı upstream StakTrakr saatlik kapanışlarında, *o günün en olumsuz ardışık 4 saatlik hareketi*:

| Gün | Altın | Gümüş | Platin | Paladyum |
|---|---:|---:|---:|---:|
| 2026-05-28 | -%1,757 | -%3,434 | -%2,881 | -%2,346 |
| 2026-09-16 | -%1,998 | -%2,604 | -%2,413 | -%2,836 |

28 Mayıs'ta dört metalin en sert 4-saat penceresi 04:00 UTC; Eylül'de 19:00–20:00 UTC civarında. Bu **retrospektif ortak piyasa hareketi**dir; otomatik erken sinyal veya kesin gelecek düşüş kanıtı değildir.

## GitHub otomasyon ve test

- Saatlik gerçek arşiv aktarıcısı: `gold_axis_2026/data_pipeline/staktrakr_fourmetal_hourly_research_backfill_v1.py`; 10 test. İlk doğrulanmış Actions çalışması: https://github.com/ataullahturgut/sim3-automation/actions/runs/41106884375. Ana dal tekrar çalışması: https://github.com/ataullahturgut/sim3-automation/actions/runs/41107205854 (başarılı). PR #171 ana dala birleştirildi.
- 15m snapshot aktarıcısı: `gold_axis_2026/data_pipeline/staktrakr_fourmetal_15min_research_ingest_v1.py`; 10 test. İlk doğrulanmış Actions çalışması: https://github.com/ataullahturgut/sim3-automation/actions/runs/41107859115 (başarılı). PR #172 ana dala birleştirildi. Yeniden çalışma sonucunu ayrıca doğrulayın.
- Zamanlayıcılar: saatlik arşiv için her gün **02:20 UTC**, 15m tarihsel arşiv için **02:35 UTC**. Sırasıyla son 15 ve 7 gün tekrar okunur; satır hash çatışmaları tekrar yazılmaz. Bu **önceki günün tarihsel arşiv toplanmasıdır**, 15 dakikada bir çalışan *canlı V22 sinyali değildir*.
- Her iki tablo ayrı ve append-only'dir; kaynak dosya/alan SHA256, fiyat saati ve ingestion zamanı tutulur. `original_firstprint_certified=false` kalır. Günlük otorite fiyatları, V22/BASE14, haftalık ANN, aylık model ve al-sat algoritması **değiştirilmedi**.

## Kalan kesin eksikler

1. **2024–2025 StakTrakr dört-metal saatlik/15m geçmişi** bu yayımlı arşivde mevcut değil. Dört metalin 4 saatlik özelliklerini 2024–2025'te bu tek kaynaktan eğitmiş gibi göstermek yasaktır. Bunun için bağımsız arşiv/piyasa veri sağlayıcısı aranmalı ve kaynak farkı açık yazılmalıdır.
2. StakTrakr **DXY, ABD H.15 tahvil faizi, GVZ/VIX veya CFTC** üretmez. Bu kaynaklar StakTrakr spot metaliymiş gibi çekilemez; DGS10 için Fed H.15, GVZ için Cboe, CFTC için resmî CFTC ve DXY için ayrı lisanslı/verifiye kaynak gerekir.
3. Tarihsel snapshotlar sonradan alınmıştır; geriye dönük 2026 isabetini *o gün gerçekten canlı sinyal çıktı* diye göstermeyin.
4. Çoklu metal 4-saat sinyalinin 2026 %4+ düşüşlerini yakalama/yanlış alarm karşılaştırması **yeni kaynakla baştan hesaplanmalıdır**. V37'nin 7/8 ve 36 sonuçsuz uyarı günü, yeni StakTrakr **dört metalin aynı saatlik ölçümünden değil**, altın HistData 4s + diğer metaller günlük fiyatlarından oluşuyordu. Bu iki deneyi aynı şeymiş gibi sunmayın.

**Kaynak belge:** https://github.com/lbruton/StakTrakr/blob/main/devops/pollers/shared/api-export-v2.js ve https://github.com/lbruton/StakTrakr/blob/main/devops/pollers/shared/api-export.js.
