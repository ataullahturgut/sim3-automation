# TERAZİ v1 — Kural tabanlı uyarlanır çıkarım ağı | Mimari ön kaydı

2026-10-16. Dal: `research-gold-claude-pusula-v1-20261016`. Bu dosya TERAZİ kodundan ve her türlü sonuçtan ÖNCE commit edilmiştir. Geliştirme dönemi: ısıtma 2020-01→2022-12, maraton 2023-01→2025-12. **2026 verisi yüklenmez.**

## Paradigma ve özgünlük beyanı
Paradigma: ANFIS/bulanık çıkarım ağları gibi, **kural tabanı taşıyan ve parametrelerini uyarlayan** bir ağ. ANFIS kopyalanmamıştır; şu noktalarda yapısal olarak farklıdır:

| | Klasik ANFIS | TERAZİ v1 |
|---|---|---|
| Kural yapısı | Girdi uzayının ızgara bölünmesi (boyutla patlar) | **Seyrek kurallar, veriden keşfedilir** (1–3 kapı) |
| Üyelik | Çan/Gauss, her girdi için sabit sayıda | **Yönlü yumuşak kapı** σ(d(z−c)/s): "koşul ne kadar gerçekleşti" |
| Sonuç (consequent) | Girdilerin doğrusal fonksiyonu (Takagi–Sugeno) | **Olasılıksal özet:** beklenen getiri μ ve belirsizlik v |
| Kural ağırlığı | Tüm veride ortak eğitilir (içsel) | **Yalnız kural doğduktan SONRAKİ günlerde kazanılır** (sahada sınanmış güven) |
| Çıkış | Ağırlıklı toplam | **Maliyet duyarlı tartı:** kurallar çelişirse güven düşer, pozisyon korunur |
| Yapı değişimi | Sabit | **Aylık doğum/ölüm:** rejim değişince kural ölür, yenisi doğar |
| Öğrenme | Hibrit geri yayılım + en küçük kareler | **İki zaman ölçeği:** sonuçlar çevrimiçi, yapı aylık |

## Girdiler
DENEYİM v1'in 35 tarihsiz, karar anında bilinen durum değişkeni (`deneyim_states.py`, standardize z, ±4 kırpma). Yürütme de aynı: karar 06:00Z, dolum aynı gün 09:00Z, AL = ASK, SAT = BID, maliyet %0,8/yön.

## Katman 1 — Yumuşak koşul kapıları
Kapı = (j, d, c): j değişken, d ∈ {+1,−1} yön, c eşik.
```
g(z) = σ( d · (z_j − c) / s ),  s = 0,5   (z birimi)
```
Değer (0,1) aralığında: 1 = koşul tam gerçekleşti. İkili değişkenler (sig_*) için eşik ızgarası yalnız {0,5}.
Eşik ızgarası: c ∈ {−1,5; −1,0; −0,5; 0; +0,5; +1,0; +1,5}.

## Katman 2 — Kurallar (yumuşak VE)
Kural R, 1–3 kapının kümesi. Tetikleme gücü:
```
w_R(z) = Π_{kapı ∈ R} g(z)
```

## Katman 3 — Sonuç belleği (çevrimiçi, olgunlaşmış)
Her kural, kendi bölgesindeki 10 karar günlük getiriyi tutar. H = 10. Olgunlaşmış bir (z_i, r_i) geldiğinde, w = w_R(z_i) ile:
```
n ← ρ·n + w ;  μ ← μ + (w/n)(r_i − μ) ;  v ← max(v_min, ρ·v + (w/n)((r_i − μ_önce)² − v))
```
ρ = 0,995, v_min = 0,25. Başlangıç: μ = 0, v = 9, n = 0.

## Katman 4 — Sahada sınanmış güven (özgün çekirdek)
Kural, **doğduğu günden sonra** olgunlaşan sonuçlarla sınanır. Yalnız bu sonuçlarla:
```
h ← ρ·h + w·1[sign(μ_o önce) = sign(r_i)] ;   k ← ρ·k + w
güven = (h − (k − h)) / (k + 10)        (küçültülmüş yönlü isabet, −1..+1)
oy ağırlığı a_R = max(0, güven)
```
Doğum sonrası kanıtı az olan kural çıraklıktadır (a_R küçük). İçsel uyum oy hakkı kazandırmaz.

## Katman 5 — Maliyet duyarlı tartı
Tam tur maliyet c_rt = −200·ln(1−0,008) ≈ %1,606.
```
W = Σ_R a_R·w_R(z)
W < W_min = 0,5  →  görüş yok, pozisyon korunur
E = Σ a_R·w_R·μ_R / W
U = sqrt( Σ a_R·w_R·(v_R + (μ_R − E)²) / W )     (belirsizlik + kurallar arası çelişki)
AL  : E − λU >  c_rt/2    (λ = 0,5)
SAT : E + λU < −c_rt/2
aksi halde pozisyon korunur
```
Eşikler maliyetten türetilir, **aranmaz**.

## Aylık yapı değişimi (ay sonu, yalnız o güne kadarki veriyle)
1. **Artıkları hesapla:** olgunlaşmış her gün için e_i = r_i − E_i (modelin o günkü tahmini).
2. **Kural doğumu:** aday havuzu = (a) tüm tek kapılar; (b) hayatta kalan kuralların bir kapı eklenmiş hâlleri (en fazla 3 kapı). Her aday için ağırlıklı artık ortalaması ve etkin destek hesaplanır. Çoklu deneme cezası: adayın küçültülmüş ortalamasının mutlak değeri `sqrt(2·ln M / n_eff)·sd` eşiğini geçmeli (M = o ay taranan aday sayısı). Destek n_eff ≥ 20 şartı. Geçenlerden en iyi **3 tanesi** eklenir.
3. **Kural ölümü:** doğum sonrası k ≥ 15 olup güveni < 0 olan kurallar; n < 5'e düşenler; başka kuralla aynı kapı kümesine sahip olanlar silinir.
4. Kural tabanı üst sınırı 60 kural; aşılırsa en düşük oy ağırlıklı kurallar düşer.

## Nedensellik ve dürüstlük
- Hiçbir sonuç olgunlaşmadan (i + H ≤ ay sonu) öğrenmeye girmez.
- Bir ayın kararları yalnız **önceki ay sonundaki** kural tabanıyla verilir.
- Kural doğumu, keşfedildiği veriyi oy hakkı için kullanamaz (katman 4).
- 2020–2022 ısıtması yalnız 2022-12-30'a kadarki veriyi kullanır.
- Testler: gelecek fiyat bozma değişmezliği, kesme eşitliği, olgunlaşma sınırı, tekrar üretilebilirlik.

## Raporlama
Her ay: tetiklenen kurallar, doğan/ölen kurallar, kural tabanının büyüklüğü, E ve U, kararlar, ideal yola göre hata. Sonunda: hayatta kalan kural tabanının tamamı insan okunur biçimde (hangi koşul, beklenen getiri, sahada sınanmış güven, kaç gün yaşadı).
Kıyaslar: pasif altın, SMA100 trend kuralı, DENEYİM v1.2, ideal yol.
Beklenti dürüstçe kaydedilir: önceki teşhis (tam kopya üst sınır testi 206 < dürüst 213,5 < pasif 230,8), bu veri kümesinde zirve zamanlaması sinyalinin zayıf olduğunu göstermiştir. TERAZİ'nin pasifi geçmesi beklenmez; amaç **kararlarını kurallarla açıklayabilen, uyum sağlayan** bir model kurmak ve ne öğrendiğini ölçmektir.

## Dondurma
Maraton sonunda kural tabanı ve tüm parametreler `TERAZI_V1_DONDURULMUS_MODEL.json` olarak dondurulur. 2026 testi bu dosyayla, kod değiştirilmeden yapılır.
