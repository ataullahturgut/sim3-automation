# PUSULA v1 — Claude özgün öğrenen altın modeli | ÖN KAYIT (PREREG)

2026-10-16. Dal: `research-gold-claude-pusula-v1-20261016` (ana çalışma dalı `gold-execution-channel-audit-20261006` HEAD 45aed57'den açıldı).
Bu dosya; veri paneli, model kodu ve herhangi bir sonuç üretilmeden ÖNCE commit edilmiştir. Bu klasörde başka dosya yoktur.

## 0. Amaç ve dürüstlük beyanı
- PUSULA v1, mevcut V1–V20 / KAVİS / ATLAS kodlarını kullanmayan, kopyalamayan, bağımsız tasarlanmış bir öğrenen modeldir.
- Model 2023-01-03'te 100 USD nakitle işlem koşusuna başlar ve 2026-09-30'a kadar **ay ay kesintisiz** ilerler. Her ay sonunda yalnız o güne kadar bilinen veriyle, bu dosyada önceden yazılmış kurallarla kendini günceller. Koşu sırasında insan veya Claude koda/parametreye dokunmaz.
- **2023–2026 daha önce görülmüş dönemdir; kör test değildir.** Claude'un bilgisi 2026 ortasına kadar uzanır ve bu dönemde altının güçlü yükseldiğini bilir. Bu yanlılık tasarımın genel ve önceden dondurulmuş olmasıyla sınırlandırılmaya çalışılmıştır, tamamen dışlanamaz. Gerçek kanıt ancak 2026-10'dan itibaren dondurulmuş v1'in ileri (kâğıt üzerinde) koşusuyla elde edilir.
- **Haber verisi yoktur.** Neon'da ilk yayın zamanı doğrulanmış haber/olay tablosu bulunmadı; v1 haber kullanmaz. ETF ve tek hisse verisi de yoktur; hisse piyasası yalnız CME Nasdaq vadeli (NQ) ile temsil edilir.
- Fiyatlar Dukascopy aracı kurum BID/ASK verisidir; Türk bankası kotasyonu değildir. Banka maliyeti varsayımsal %0,8 / yön olarak eklenir.

## 0b. Önceki eşdeğer deney araması
`GOLD_CONTROL_PROJECT_MANIFEST.md` tarandı. En yakın deney `DYNAMIC_LOGIT_D99` (R25, DOWNSIDE_CROSSDOMAIN_DIRECTION_V1): 5 dk altın paneli, 4 volatilite özelliği, indirim 0,99 olan dinamik lojistik, **ertesi gün yön** sınıflaması; 2022–2024 BA ≈ 0,499 → FAIL. Manifest bunu "sınıflayıcı değil bilgi kümesi sorunu" olarak yorumlar.
PUSULA v1 matematiksel olarak eşdeğer değildir; yeni olan kısımlar: (i) 10 günlük ufukta getiri regresyonu (yön değil), (ii) piyasalar arası değişkenler (NQ, ZN, CL, SI), (iii) farklı unutma hızlı Bayesçi model topluluğu ve log-skor ağırlıklandırma, (iv) maliyete duyarlı uzun/nakit karar kuralı. Önceki başarısızlık nedeniyle K2'nin geçememesi makul bir önceliktir; bu önceden kabul edilir.

## 1. Veri (Neon `Gold Control`, salt SELECT)
- Altın 2020–2025: `gold_research_evduka_xau15m_bidask_candidate` (15 dk; fiyat zamanı = bar_start+15 dk).
- Altın 2026: `gold_research_dukascopy_xau_h1_monthly_source_candidate_v1` (1 saat; fiyat zamanı = utc+1 saat).
  Ön kontrol (sonuç değil, kaynak uyumu): 2025'te çakışan 1.971 saatte ortalama mutlak fark %0,0001; 2026'da doğrudan Dukascopy M15 ile 4.176 saatte birebir aynı.
- Piyasalar arası: `gold_research_cme_glbx_futures_2023_2026_h1_5roots_continuous_c`, semboller NQ.c.0, ZN.c.0, CL.c.0, SI.c.0. `ts_event` çubuk BAŞLANGICIDIR; kapanış ts_event+1 saatte bilinir.
- mid = (bid+ask)/2. Panel üretim SQL'i commit edilir; ham piyasa verisi commit edilmez, yalnız türetilmiş günlük panel.

## 2. Zaman ve yürütme
- Karar günleri: Pazartesi–Cuma UTC. Karar 06:00Z (09:00 TSİ). Dolum aynı gün 09:00Z (12:00 TSİ).
- Karar fiyatı P_t: aynı UTC gününde (00:00Z, 06:00Z] aralığındaki en son mid. Yoksa o gün karar yok.
- Dolum: tam 09:00Z noktasındaki BID/ASK. AL = ASK'tan, SAT = BID'den; ek banka maliyeti %0,8 / yön:
  AL: units = cash·(1−0,008)/ask. SAT: cash = units·bid·(1−0,008). 09:00Z fiyatı yoksa emir iptal, ertesi gün yeniden karar.
- Günlük değerleme (NAV): 09:00Z'de units·bid·(1−0,008) + cash (tasfiye değeri).

## 3. Hedef (etiket)
- y_t = 100·ln(mid09_{t+H} / mid09_t), H = 10 karar günü. y_t ancak t+H günü 09:00Z'de olgunlaşır ve en erken t+H+1 günü 06:00Z kararında öğrenmeye girer.

## 4. Özellikler (yalnız karar anında bilinen)
Altın (karar günleri dizisi P üzerinden):
f1 = 100 ln(P_t/P_{t−1}); f2 = 100 ln(P_t/P_{t−5}); f3 = 100 ln(P_t/P_{t−20}); f4 = 100 ln(P_t/P_{t−60});
f5 = ln(son 20 günlük f1 standart sapması); f6 = 100 ln(P_t / max(P_{t−59..t})).
Piyasalar arası: x_nq, x_zn, x_cl, x_si = 100 ln(C_t / C_{t−5}). C = 06:00Z'den önce kapanmış son saatlik çubuğun kapanışı (yaş ≤ 72 saat). Her iki uçta instrument_id aynı değilse (vade değişimi) veya bayatsa değer 0.
Standardizasyon: z = (f − ortalama)/s.sapma; istatistikler yalnız önceki karar günlerinden (genişleyen pencere), ±4'te kırpılır. Bir özellik için 60'tan az geçmiş gözlem varsa z = 0.

## 5. Model: Bayesçi indirimli doğrusal modeller topluluğu
K = 9 aday = 3 özellik kümesi × 3 indirim faktörü.
- S0 = {sabit} (yalnız sürüklenme öğrenir); S1 = {sabit, f1..f6}; S2 = {sabit, f1..f6, x_nq, x_zn, x_cl, x_si}.
- δ ∈ {0,990; 0,997; 0,999} (küçük δ = daha hızlı unutma).
Her aday bir dinamik doğrusal modeldir (öncül m0 = 0; C0 = diag(1,0² sabit, 0,5² eğimler); birim: 10 günlük % getiri).
Olgunlaşan her (x_t, y_t) için:
R = C/δ; q = xᵀRx + H·S; A = Rx/q; m ← m + A(y − xᵀm); C ← R − AAᵀq.
(H·S: 10 günlük etiketler günlük örtüştüğü için bilgi miktarını H kat azaltan örtüşme düzeltmesi.)
Gürültü varyansı S: başlangıç 9,0; her olgun etikette S ← 0,99·S + 0,01·e², e = y − xᵀm(önce); alt sınır 0,25.
Tahmin: μ_k = xᵀm, parametre belirsizliği s_k² = xᵀ(C/δ)x, öngörü varyansı v_k = s_k² + S.

## 6. Hatalardan öğrenme (matematiksel ve otomatik)
(a) Her olgun etikette (sürekli): aday ağırlıkları, karar anında saklanan tahminlerin gerçekleşen değere göre log-olabilirliğiyle güncellenir:
L_k ← 0,995·L_k + (1/H)·log N(y; μ_k, c²·v_k); w_k ∝ exp(L_k). Başlangıç eşit ağırlık.
Topluluk: μ = Σ w_k μ_k; s² = Σ w_k (s_k² + (μ_k − μ)²); v = Σ w_k (v_k + (μ_k − μ)²).
(b) Her takvim ayının son karar gününde (ay sonu öğrenme adımı): kalibrasyon katsayısı
c² = kırp(ortalama(z²), 0,5, 2,0), z = (y − μ)/√v, son 120 olgun etiket üzerinden (120'den azsa c² = 1). Yeni c² bir sonraki ay boyunca kullanılır.
(c) Ay sonu hata raporu (otomatik): yön isabeti, ortalama mutlak hata, %80 aralık kapsaması, aday ağırlıkları, ay getirisi, işlem sayısı ve kıyaslar.
Karar eşiği ve diğer tüm sabitler performansa göre AYARLANMAZ.

## 7. Karar kuralı (maliyete duyarlı, histerezisli)
Tam tur maliyet c_rt = −200·ln(1−0,008) ≈ %1,606. Beklenen tutma süresi 6 ufuk (60 karar günü) varsayımıyla ufuk başına eşik b = c_rt/6 ≈ %0,268.
- NAKİT iken: μ − s > b ise AL.
- ALTIN iken: μ < −b ise SAT.
- Diğer durumlarda pozisyon korunur.

## 8. Ön eğitim ve koşu
- 2020-01-02 → 2022-12-30: yalnız öğrenme (etiketler olgunlaştıkça), işlem yok.
- 2023-01-03 → 2026-09-30: 100 USD nakitle işlem; öğrenme kesintisiz devam eder.

## 9. Kıyaslar (aynı yürütme ve maliyetle)
1. Nakit: 100 USD.
2. Pasif altın: 2023-01-03 09:00Z ASK'tan AL, sonda BID'den tasfiye değeri.
3. Basit trend kuralı: P_t > 1,01·SMA100(P) ise AL, P_t < 0,99·SMA100(P) ise SAT.

## 10. Kabul ölçütleri (önceden donmuş; değerlendirme 2023-01-03 → 2026-09-30)
Örtüşmeyen örnek: işlem döneminin her 10. karar günü.
- K1 Kalibrasyon: o anda geçerli c ile %80 öngörü aralığının (μ ± 1,2816·c·√v) kapsaması [0,72; 0,88] içinde.
- K2 Tahmin becerisi: μ_t ile y_t arasındaki Spearman sıra korelasyonu > 0 ve 6'lık bloklarla, 2000 tekrarlı, tohum 20261016 blok bootstrap %95 güven aralığı 0'ı içermiyor.
- K3 Sürüklenmenin ötesinde öğrenme: topluluğun ortalama log-skoru, S0 (δ=0,997) adayının ortalama log-skorundan yüksek.
- K4 Ekonomik: son NAV ≥ trend kuralı son NAV'ı VE strateji maksimum düşüşü ≤ pasif altın maksimum düşüşü.
- Pasif altına göre sonuç ayrıca raporlanır (kabul ölçütü değil).
Yıl bazında (2023, 2024, 2025, 2026 Oca–Eyl) ve kaynak bazında (EV/Dukascopy 15 dk 2020–2025; Dukascopy H1 2026) ayrıca raporlanır: örtüşmeyen örnekte N, kapsama, yön doğruluğu (sign μ vs sign y), dengeli doğruluk, UP/DOWN duyarlılığı; aynı tarihlerde "her zaman UP" ve S0 sürüklenme taban çizgileri; trend kuralına göre düzeltilen/bozulan yön kararları; yıllık strateji, pasif ve trend getirileri.
Her ölçüt ayrı ayrı GEÇTİ/KALDI raporlanır. Kalan ölçüt için eşik, parametre veya özellik taraması YAPILMAZ. Değişiklik gerekirse PUSULA v2 yeni ön kayıtla yazılır ve yalnız 2026-10 sonrası ileri dönemde değerlendirilir.

## 11. Teknik zorunluluklar ve testler
- Gelecek bilgisi testi: t anındaki özellik ve kararlar, t'den sonraki tüm fiyatlar rastgele bozulduğunda değişmemeli.
- Olgunlaşmamış etiket hiçbir zaman öğrenmeye girmemeli.
- Aynı girdiyle koşu bit düzeyinde tekrar üretilebilir olmalı.
- Canlı emir yok.
