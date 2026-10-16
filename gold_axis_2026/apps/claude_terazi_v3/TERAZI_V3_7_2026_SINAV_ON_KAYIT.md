# TERAZİ v3.7 — 2026 sınavı | Ön kayıt ve dondurma

2026-10-17. **Bu dosya 2026 karar koşusundan ÖNCE commit edilmiştir.** Bu araştırma hattında
2026 fiyatlarıyla hiçbir model koşulmadı; geliştirme yükleyicisi 2026'yı reddeder
(`load_rows(dev_only=True)` assert).

## Dondurulan model (değişmez)
- Öğrenme: v3.10 yapılandırması = v3.5 (kırılma kanalında beceri güveni, COT kırılma kanalından
  hariç) + eğitimde verisi olmayan 19 değişken sabit 0. Geliştirme döneminde v3.7 karar
  katmanıyla v3.5 ile birebir aynı karar verir (225,68, 5 işlem).
- Karar: v3.7 — ALIŞ v2 kuralı (P − 0,5·U > 0,5); SATIŞ = k = 2 yapı kırılması VE
  Pe + 0,5·Ue < 0,5 VE makro onayı (rr_d5 > 0 VEYA y2_d5 > 0).
- Protokol geliştirmeyle aynı: aylık yürüyen öğrenme, etiketler yalnız olgunlaşınca. Koşu
  2023-01-03'ten kesintisiz sürer; 2026 performansı 2025-12-31 kapanış değerinden ölçülür.
- Kod: `terazi_v3.py`, `run_terazi_v3_4.py` (mod v310), `karar_v37.py`, `run_2026.py`.

## 2026 için veri tamamlama (sonuca bakmadan)
- DGS2 ve GVZ: `GOLD_EXECUTION_{DGS2,GVZ}_FREE_CANDIDATE_2020_20261007.csv`'den yalnız
  2025-12-31 sonrası günler; ortak günlerde mevcut dosyalarla birebir aynı (757/757, 1257/1257).
- FOMC 2026 takvimi federalreserve.gov'dan eklendi.
- Geliştirme dönemi bu değişikliklerden sonra birebir yeniden üretildi (günlük dosya değişmedi).
- Fiyat kaynağı değişir: 2025 EV/Dukascopy 15 dk (EVDUKA_15M), 2026 Dukascopy H1. Ayrı raporlanır.
- CPI/NFP sürprizleri 2026'da yok; bu değişkenler dondurulan modelde zaten maskeli.

## Sınav dönemi ve ölçütler
2026-01-02 → 2026-09-30 (panelin son günü), 193 işlem günü. Kıyas: aynı dönemde al-tut
(2025 sonunda altında olan yatırımcı için tut).
- **T1 (birincil):** v3.7 net getirisi ≥ al-tut net getirisi.
- **T2:** maksimum düşüş al-tut'tan düşük.
- Raporlanır: her işlem, satış → geri alım sonucu, aylık getiri, sabit-eşik v3.3 ile kıyas.
Sonuç ne olursa olsun model değiştirilmez; 2026 için ikinci koşu yapılmaz.
