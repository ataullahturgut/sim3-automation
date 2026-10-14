# GPT bağımsız B vakası — Şubat 2023 DOWN (1–24 Şubat 2304×15 dakika)
**2026-10-14**. GPT bağımsız Claude karşılaştırması, Claude çıktıları okunmadı. Eski V1 NY17 tarihsel ZigZag yaklaşık **-%7.15**, burada TRT günleri ve **$100 ayrı GOLD başlangıç portföyü**. `NOT_BLIND / NOT_BANK_EXECUTED`.

**Başlangıç benchmark:** 1 Şubat saat **09:15 TRT** tamamlanmış M15 vendor ASK **1926.90**, $100 üzerinde %0.8 BUY → **0.0514816545 ons**. Bu altın taşıma başlangıcı şartlıdır; Jan13 testindeki altın 1Feb'e atlatılmadı, eksik aradaki dönem icat edilmedi. 1 Şubat Fed açıklaması 19:00Z/22:00TRT başlangıçta bilinemez.

**3 Şubat 13:30 UTC/16:30 TRT NFP:** BLS resmi **517 bin istihdam**, işsizlik **%3.4**, [ilk tarihli BLS belgesi](https://www.bls.gov/news.release/archives/empsit_02032023.htm). Daha sonra revize edilmiş istihdam sayısı karara giremez. Güçlü işgücü + Fed faiz/USD baskısı = altın DOWN ekonomik adayı (tüm transfer kanalları aynı dakika sayısal ispatlanmadı). NFP ön M15 MID **1913.810**, ilk tamamlanan 15m MID **1888.175**, düşüş **-1.339%**.

**Aynı fiyat teyit kuralı:** NFP sürprizinin yönü DOWN, ilk M15 DOWN; fiyat açıklama öncesi MID'in **-%0.6 altında üç ardışık tamamlanmış M1** kapanışıyla korunacak. İlk teyit **13:45 UTC/16:45 TRT**: M1 değerleri 1888.05005, 1889.31995, 1887.95996, eşik 1902.32714. **Karar 16:45 TRT, sonraki 13:45–13:46 UTC 1m kapanış vekiliyle 16:46 TRT SAT**. Tarihsel son bilinen M15 makas **0.41**; o sonraki M1 MID 1887.51001, satılabilir banka değil **proxy BID 1887.30501**. %0.8 SAT ücreti sonrası **$96.3843 CASH**.

**As-of kuralları:** NFP firstprint t13:30Z, M15 13:30–13:45Z tamamlanmadan kullanılamaz; M1 13:44Z son barı 13:45Z itibarıyla tamam. 13:45Z kararında **ZN H1 13:00–14:00Z barı henüz yok**; o faizi teyit sayma. 2023 15m DXY, gerçek banka altın kotasyonu yok. 16:46 TRT geç banka kapanış saati riski vardır.

**Satıştan sonraki makro ekonomi:** 14 Şubat [BLS CPI](https://www.bls.gov/news.release/archives/cpi_02142023.htm), 16 Şubat [BLS PPI +%0.7](https://www.bls.gov/news.release/archives/ppi_02162023.htm), 24 Şubat [BEA PCE +%0.6 genel/çekirdek](https://www.bea.gov/news/2023/personal-income-and-outlays-january-2023). Bunlar 3 Şubat SAT kararının nedeni olarak geriye taşınmadı. Sonraki dönemde nakit tutma, **re-entry kuralı bulunmayan dar SELL-koruma modülünün varsayımıdır**, en iyi tam sistem olduğunu söyleme.

**Günlük 96×15 dk tarama:** [2304 zamanlı CSV](GPT_INDEPENDENT_FEB01_24_2304X15M_STATE_LEDGER_20261014.csv), 1646 adet M15 fiyat gözlemi, kalan tatil/hafta sonu boşluklar açık. Her kontrol yeni/tamamlanmış M15, varsa tam 1/4/12 saat getiri, o an bilinen haber kimliği, CASH/GOLD portföyü, bid-mark ve varsayımsal likidasyonu ayrı. Her 15 dakika yeni emir verilmez.

| TRT günü | M15 fiyat başlangıcı | Pozisyon sonu | Nakit/net SAT varsayımı |
|---|---:|---|---:|
| 2023-02-01 | 92 | GOLD | 99.69 |
| 2023-02-03 | 92 | CASH | 96.38 |
| 2023-02-06 | 88 | CASH | 96.38 |
| 2023-02-14 | 92 | CASH | 96.38 |
| 2023-02-16 | 92 | CASH | 96.38 |
| 2023-02-24 | 92 | CASH | 96.38 |

**24 Şubat 23:45 TRT kıyası**: NFP sonrası Şubat3 SAT → **$96.3843 CASH**; satmadan GOLD taşıyıp Feb24 BID 1811.86 ile o anda SAT yapılsa → **$92.5313**. SAT bileşeni bu seçilmiş vakada **$3.8530** daha fazla sermaye koruyor. Her iki politikanın 100 dolar başlangıca göre net getirisi negatiftir. Bu, büyük DOWN ortamında her zaman altın tutmayı önleyebilme bakımından ilk stres örneğidir, ileri başarı ispatı değildir. Sinyal tahmini Fed-vintage ve banka icra doğrulaması yetersiz.

**Claude kıyas alanları**: [JSON](GPT_INDEPENDENT_FEB01_24_NFP_DOWN_RESULTS_20261014.json) `decision_utc=2023-02-03T13:45:00Z, fill_utc=13:46Z, fee, bid_proxy, saved_vs_hold`. Örnek ve eşik geriye dönük açık, doğru bilimsel seviyede `L2 gold-price reaction, not L3-4 causal forecast`.
