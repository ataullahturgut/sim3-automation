# CLAUDE_INDEPENDENT — Öğrenen kanıt sistemi (AES v1) · ÖN KAYIT

**Tarih:** 2026-10-14 · **Statü:** `PREREG_WRITTEN_BEFORE_ANY_AES_RUN` · RESEARCH ONLY
**Neden:** Kullanıcı, kararların yalnız haber/vaka eşleştirmesine değil **veri analizine de** dayanmasını ve geçmişten **öğrenen, uyarlanan** bir sistem istedi. Önceki iki deneme (mekanik kural backtest'i ve yalnız-analog takdir) bu dalda korunur; bu sürüm onların yerine geçen birincil denemedir.
**Hindsight beyanı:** Ocak–Şubat 2023 sonuçlarını biliyorum. Bu yüzden aşağıdaki her şey 2023 koşusundan önce sabitlenir ve sonradan değiştirilmez; değişiklik gerekirse AES v2 olarak ayrı kaydedilir.

## 1. Karar anları ve icra
* Her hafta içi **06:00Z (09:00 TRT)** ve **13:45Z (16:45 TRT)**. 13:45Z, 13:30Z'deki NFP/CPI açıklamalarından sonraki ilk tamamlanmış 15dk barıdır; FOMC (18–19Z) bir sonraki 06:00Z'de değerlendirilir.
* Yalnız karar anında tamamlanmış barlar. CME saatlik barlar başlangıç etiketli: t anında kullanılabilir son bar `ts_event + 1s ≤ t`.
* İcra: 2023'te karar dakikasından sonraki M1 MID ± son M15 yarım makas; geliştirme döneminde karar anındaki M15 barının BID/ASK açılışı. %0,8 alış + %0,8 satış.

## 2. Hedef (öğrenme etiketi)
`y = sign(r_H)`, `r_H = C(S_{t}+H) / MID_t − 1`, burada C = t'den sonraki H'inci NY17 seans kapanışı. **Birincil H = 10 seans**, ikincil H = 20 (yalnız raporlanır). Etiket, o kapanış zamanı geçmeden öğrenmede kullanılmaz (sızıntı yok).

## 3. Uzman modüller (her biri −1…+1 oy veya 0 = görüş yok)
| Kod | Modül | Tanım (as-of t) |
|---|---|---|
| M1 | TREND | trend20 ve mom10 aynı işaretliyse o işaret, değilse 0 |
| M2 | KISA MOMENTUM | z3 = r(son 3 seans kapanışı→t) / (σ_günlük·√3); oy = clip(z3/2) |
| M3 | ŞOK GERİ DÖNÜŞÜ | z1 = r(son seans kapanışı→t)/σ_günlük; |z1|>1 ise oy = −clip(z1/2), değilse 0 |
| M4 | HABER/SÜRPRİZ | Son 3 seans içindeki NFP/CPI/FOMC: ilk 60dk XAU tepkisi |r60|≥%0,4 ve en az bir sürpriz bileşeni aynı yönde ise sign(r60); açıklama seansında ağırlık 1, sonraki iki seansta 0,5 |
| M5a | OLAY ANALOĞU | M4 aktifken: geçmişte sonucu belli olmuş olaylardan k=7 en yakın (olay türü, sürpriz yönü, r60, olay öncesi trend20, mom10; standartlaştırılmış uzaklık); oy = clip(ortalama kalan hareket(+4s→10 seans) / %1,5) |
| M5b | DURUM ANALOĞU | Her karar anında: geçmişte etiketi olgunlaşmış karar anlarından k=25 en yakın (trend20, mom10, mom20, 20-seans zirveden uzaklık, z1, z3); oy = clip(ortalama r_H / %1,5) |
| M6 | GÜMÜŞ TEYİDİ | 24 saatlik altın ve gümüş (SI.n.0 1dk) getirisi aynı işaretli ve |gümüş| ≥ %0,5 ise sign(altın 24s), değilse 0 |
| M7 | FAİZ KANALI | ZN.n.0 son 24 saat |Δ| ≥ %0,25 ise sign(ΔZN) (ZN↑ = getiri↓ = altın lehine), değilse 0 |
| M8 | RİSK/LİKİDİTE | NQ.n.0 24s ≤ −%1,5 iken: altın 24s ≥ 0 → +1 (güvenli liman), altın < 0 → −1 (likidite satışı); aksi 0 |
| M9 | OYNAKLIK (GVZ) | D-1 GVZ 5 günlük değişim ≥ +2 puan iken sign(altın 5 seans getirisi), aksi 0 |

Veri yoksa modül uyur (0). GVZ 2021'den, CME/gümüş 2022'den itibaren var; öncesinde M6–M9 uyur.

## 4. Öğrenme (uyarlanma) kuralı
* **Uyuyan-uzman Hedge:** her modülün kaybı `ℓ = (1 − v·y)/2` (yalnız oy verdiği ve etiketi olgunlaşmış anlarda). Ağırlık `w_i ∝ exp(−η · L_i)`, η = 0,05; `L_i` üstel unutmalı toplam kayıp, yarı ömür 250 karar anı (~125 seans) → rejim değişince ağırlıklar kayar.
* **Birleşik skor:** `s = Σ w_i v_i / Σ_{uyanık} w_i`.
* **Vaka kütüphanesi büyür:** M5a/M5b yalnız t'den önce sonucu belli olmuş örnekleri kullanır; her yeni olgunlaşan örnek kütüphaneye girer.
* **Kalibrasyon (öğrenilir):** olgunlaşmış son 500 karar anında s'nin beşte birlik dilimine göre ampirik `P_up = P(r_H > +%1,65)` ve `P_dn = P(r_H < −%1,65)`.

## 5. Karar
* NAKİT → **AL**: `P_up − P_dn ≥ 0,25` ve s > 0.
* ALTIN → **SAT**: `P_dn − P_up ≥ 0,25` ve s < 0.
* Aksi halde **KAL**. Bir işlemden sonra 2 seans boyunca ters işlem yok (testere koruması).
* %1,65 = %1,62 tur maliyeti + yaklaşık makas.

## 6. Dönemler ve değerlendirme
* Öğrenme 2020-01'den başlar (altın/makro), değerlendirme ve 100 $ portföy **2021-07-01 → 2022-12-30 (geliştirme)**; sonra kesintisiz öğrenmeye devam ederek **2023-01-03 → 2023-02-28 (vaka penceresi)**.
* Raporlanacaklar: yön isabeti (accuracy, balanced accuracy, UP/DOWN recall), modül başına isabet ve ağırlık evrimi, işlem sayısı, ücret, net 100 $, pasif altın ve nakit; A1/A2/B/C vaka sonuçları; her karar anında modül oyları ve gerekçe.
* Geliştirme döneminde AES nakit veya pasif altını geçemezse bu negatif sonuç olarak yazılır; parametre taraması yapılmaz.
* Eksik veri: DXY, 2Y/10Y getiri, ETF/COT gün içi — modül yok, rapora `MISSING`.
