# PUSULA v1 — Sonuç raporu (2023-01 → 2026-09, ay ay kesintisiz)

2026-10-16. Dal: `research-gold-claude-pusula-v1-20261016`.
Sıra: PREREG `c2c3aba` → veri paneli `e9de447` → kod ve testler dondu `505a80b` → bu sonuçlar. Koşudan sonra hiçbir parametre değiştirilmedi.

**Karar: PUSULA v1 BAŞARISIZ (4 ölçütten 1'i geçti).** 2023–2026 daha önce görülmüş dönemdir; kör test değildir. Fiyatlar Dukascopy BID/ASK + varsayımsal %0,8/yön banka maliyetidir; Türk bankası kotasyonu değildir. Haber verisi kullanılmadı.

## Kabul ölçütleri (PREREG §10, örtüşmeyen örnek N = 96)

| Ölçüt | Sonuç | Eşik | Durum |
|---|---|---|---|
| K1 Kalibrasyon (%80 aralık kapsaması) | 0,844 | 0,72–0,88 | GEÇTİ |
| K2 Tahmin becerisi (Spearman μ–y) | −0,162; %95 GA [−0,380; 0,109] | > 0 ve GA 0'ı içermesin | KALDI |
| K3 Sürüklenmenin ötesinde öğrenme (ort. log-skor) | topluluk −2,673; S0 −2,653 | topluluk > S0 | KALDI |
| K4 Ekonomik | NAV 124,13 < trend 185,88; maks. düşüş %22,84 ≤ pasif %27,87 | ikisi birden | KALDI |

## Sermaye (100 USD, 2023-01-03 → 2026-09-30, 967 işlem günü)

| | Son değer | Maks. düşüş | İşlem |
|---|---:|---:|---:|
| PUSULA v1 | **124,13 USD** | %22,84 | 4 |
| Trend kuralı (SMA100 ±%1) | 185,88 USD | %32,52 | 10 |
| Pasif altın | 224,62 USD | %27,87 | 1 |
| Nakit | 100,00 USD | 0 | 0 |

Bağımsız yeniden hesaplama: işlem defteri, pasif ve trend kıyası paneldeki BID/ASK ile modelden ayrı kodla yeniden oynatıldı; dört işlem NAV'ı, son NAV, pasif ve trend değerleri birebir aynı.

İşlemler: 2025-07-22 AL (3.389,30) → 2025-11-11 SAT (4.135,43) → 2025-12-17 AL (4.319,56) → 2026-03-30 SAT (4.537,94); sonra nakit.

## Yıl ve kaynak bazında (örtüşmeyen örnek)

| Yıl | Kaynak | N | Kapsama | Yön doğr. | Dengeli doğr. | UP / DOWN duyarlılığı | "Hep UP" doğr. | S0 doğr. | Trende göre düzeltilen / bozulan | Strateji / pasif / trend getiri |
|---|---|---:|---:|---:|---:|---|---:|---:|---|---|
| 2023 | EV/Dukascopy 15 dk | 26 | 0,92 | 0,42 | 0,45 | 0,83 / 0,07 | 0,46 | 0,42 | 4 / 7 | %0,0 / %12,7 / %3,4 |
| 2024 | EV/Dukascopy 15 dk | 26 | 0,88 | 0,62 | 0,42 | 0,84 / 0,00 | 0,73 | 0,73 | 0 / 3 | %0,0 / %26,5 / %26,5 |
| 2025 | EV/Dukascopy 15 dk | 26 | 0,73 | 0,65 | 0,51 | 0,89 / 0,13 | 0,69 | 0,69 | 1 / 2 | %17,8 / %64,6 / %64,6 |
| 2026 Oca–Eyl | Dukascopy H1 | 18 | 0,83 | 0,39 | 0,44 | 0,88 / 0,00 | 0,44 | 0,44 | 5 / 4 | %5,4 / −%2,7 / −%13,7 |

## Ne oldu?

1. **Hatalardan öğrenme mekanizması tasarlandığı gibi çalıştı ama yön bilgisi bulamadı.** Aylık kalibrasyon katsayısı c² 0,5–2,0 arasında hataya göre ayarlandı ve kapsama %84 ile hedef aralıkta kaldı: model ne kadar emin olmadığını doğru ölçtü. Ancak tahminlerin gerçekleşen 10 günlük getiriyle sıra korelasyonu negatif ve anlamsız; piyasalar arası değişkenler ve altın kendi geçmişi, sürüklenmenin ötesinde bilgi taşımadı (K3). Bu, manifestteki `DYNAMIC_LOGIT_D99` başarısızlığıyla ve "bilgi kümesi sorunu" yorumuyla uyumludur.
2. **Ekonomik kayıp, belirsizlik altında nakitte beklemekten geldi.** Karar kuralı AL için "μ − s > eşik" güveni istiyor. Parametre belirsizliği ve adaylar arası ayrışma büyük olduğu için model 2023-01'den 2025-07'ye kadar 2,5 yıl nakitte kaldı; bu dönemde altın yaklaşık iki katına çıktı.
3. **Olumlu taraf sınırlı:** maks. düşüş pasif altından düşük (%22,8 vs %27,9) ve 2026'da (Oca–Eyl) strateji +%5,4 iken pasif −%2,7, trend −%13,7. Ancak 2026 Mart satışından sonra belirsizlik o kadar büyüdü ki model yeniden girmedi; bu da tasarımın aynı zaafının sonucudur, kanıtlanmış bir koruma becerisi değildir.

## Sonraki adım kuralı
PREREG §10 gereği eşik, parametre veya özellik taraması yapılmayacak. Değişiklik gerekirse PUSULA v2 yeni ön kayıtla yazılır ve yalnız 2026-10 sonrası ileri (kâğıt üzerinde) dönemde değerlendirilir. v2 için öğrenilenler (sonuçlara bakılarak edinildiği için v2'nin 2023–2026 performansı kanıt sayılmaz): (a) yön tahmini bu bilgi kümesinde yok; asıl hedef yön değil risk/maruziyet yönetimi olmalı, (b) "emin olunca gir" kuralı güçlü sürüklenmeli piyasada sistematik olarak geç kalır; varsayılan maruziyet ve risk bazlı azaltma ayrı ayrı sınanmalı.

## Dosyalar
- `results/PUSULA_V1_RESULTS.json` — kabul ölçütleri, işlemler, yıllık tablo
- `results/PUSULA_V1_MONTHLY.csv` — 45 ayın aylık raporu (getiri, pozisyon, isabet, kapsama, c², aday ağırlıkları)
- `results/PUSULA_V1_DAILY_LOG.csv` — günlük karar defteri
