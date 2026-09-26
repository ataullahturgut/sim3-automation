# GPR ara sonuçlar — 26 Eylül 2026

Durum: Stage0–2 tamamlandı; Stage3A çalışıyor. Bu dosya nihai dondurma değildir.

| DEV modeli | Toplam mutlak hata | Yön |
|---|---:|---:|
| MULTISWARM–GPR |1606.7414|23/33|
| FA–FPA–GPR |1724.6532|25/33|
| Adaptive PSO–GPR |1794.2201|20/33|
| DE–ABC–RBFNN referansı |1415.8371|25/33|

GPR şu ana kadar DEV üzerinde RBFNN referansını geçemedi. Model seçimi yalnızca DEV2022-04–2024-12. Dört baseline,32 optimizer ve ilk geliştirme denetlendi. Adaptive TLBO işi108470702038 çalışıyor; koşu36266015124 kalan dört zorunlu geliştirmeyi sırayla başlatacak. Sonrasında MPA–SCA, literatür adayı LMC2 ve ensemble/final karşılaştırma bekliyor.

## 2026 verideki gerçekler ve tahminler

USD/ons aylık ortalama; mevcut Ocak–Temmuz dönemi. Dış dönem sonuçları model seçimine dahil değildir. Bu RBFNN düzeltilmiş sürümü ve GPR, 2024-12 sonrası hiperparametre öğrenmeme kuralına uyar. Dış dönem model seçmez ve istatistiksel üstünlük kanıtlamaz. Daha eski ailelere genişletilen toplu karşılaştırmada protokol uyumsuzlukları ayrıca geçerlidir.

| Ay | Gerçek | DE–ABC–RBFNN | MULTISWARM–GPR |
|---|---:|---:|---:|
|2026-01|4753.00|4276.86|4322.90|
|2026-02|5020.00|4573.79|4769.43|
|2026-03|4856.00|5247.98|5040.68|
|2026-04|4721.00|4802.18|4840.47|
|2026-05|4587.00|4666.83|4655.56|
|2026-06|4228.00|4552.23|4685.68|
|2026-07|4073.00|4206.14|4238.95|
|Toplam mutlak hata|—|1932.70|1677.00|
|Doğru yön|—|4/7|4/7|

## Kontrol ve Uyum Özeti

DEV-only seçim; kronolojik iç ayrım; dış dönem hiperparametre dondurması; veritabanı salt okunur; invariant eşitliği; teknik tekrar sayısal eşdeğerliği PASS. Ayrıntılı yöntem authority dosyasında, tüm32 model Stage1 raporunda, köken kimlikleri evidence/provenance ve ana ledger içinde. Sonraki aşamalar tamamlanmış gösterilmedi.
