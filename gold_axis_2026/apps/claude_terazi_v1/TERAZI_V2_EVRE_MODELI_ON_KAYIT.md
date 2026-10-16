# TERAZİ v2 — Evre (faz) modeli | Ön kayıt

2026-10-16. Dal: `research-gold-claude-pusula-v1-20261016`. Bu dosya v2 kodundan ve sonuçlarından ÖNCE commit edilmiştir. Geliştirme: ısıtma 2020-01→2022-12, maraton 2023-01→2025-12. **2026 verisi yüklenmez.**

## Hedef değişikliği (asıl fark)
v1 modeli "önümüzdeki 10 günde beklenen getiri" tahmin ediyordu. Bu, kullanıcının istediği şey değildi ve iki sorun üretti: sabit 10 günlük pencere modelin gerçek davranışıyla (aylarca tutma) çelişiyordu, ve masraf tek ufka yüklendiği için model neredeyse hiç işlem yapamıyordu.

**v2'nin sorduğu soru:** *"Altın şu an yükselme evresinde mi, düşme evresinde mi?"*
- Yükselme evresinde olduğuna **yeterli kanıtla emin olursa** AL.
- Düşme evresine geçtiğine **yeterli kanıtla emin olursa** SAT.
- Emin değilse pozisyonu korur.

Sabit tutma süresi yoktur. Model evre değişene kadar pozisyonda kalır.

## Evre etiketi (yalnız öğrenme hedefi; zigzag)
Fiyat yolu (06:00Z mid) salınımlara bölünür: son uç noktadan **%5** ters yönde hareket olursa yön dönmüş sayılır (zigzag eşiği θ = %5).
- Yükselen bacaktaki günler: evre = **1 (yükselme)**
- Düşen bacaktaki günler: evre = **0 (düşme)**

**Olgunlaşma kuralı (nedensellik):** Bir günün evre etiketi, o günü içeren bacağın **dönüşü onaylandığı anda** bilinir (fiyat uçtan %5 ters hareket ettiğinde). Yalnız ay sonuna kadar onaylanmış etiketler öğrenmeye girer. Henüz onaylanmamış son bacağın günleri etiketsizdir ve öğrenilmez. v1'deki sabit 10 günlük olgunlaşma yerine bu kural geçerlidir.

Duyarlılık: θ = %3 ve %8 için sonuçlar ayrıca raporlanır (seçim için kullanılmaz; birincil θ = %5'tir).

## Kurallar ve öğrenme (v1'den devam, değişmedi)
- 35 tarihsiz, karar anında bilinen durum değişkeni (`deneyim_states.py`).
- Yumuşak yönlü kapılar `σ(d(z−c)/s)`, s = 0,5; eşik ızgarası ±1,5σ'ya kadar; kural = 1–3 kapının yumuşak VE'si.
- Aylık kural doğumu: adaylar artıklardan taranır, **dereceli doğum güveni** c₀ = kırp(tanh((z−pen)/τ), −0,4; +0,9), τ = 1,0; etkin bağımsız deneme sayısıyla ceza.
- **Sahada sınanmış güven:** kural, doğduktan SONRA onaylanan etiketlerle sınanır. `güven = (2h − k + 10·c₀)/(k + 10)`. Oy ağırlığı = max(0, güven).
- Aylık ölüm: saha kanıtı ≥ 15 olup güveni negatif olan, desteği düşen ve yinelenen kurallar silinir. Taban üst sınırı 60.

## Sonuç (consequent) — değişti
Her kural, kendi bölgesinde **yükselme evresi oranını** tutar: μ_R = P(evre = yükselme | kural tetiklendi). Çevrimiçi, indirimli (ρ = 0,995), öncül 0,5 ve 2 sözde gözlem ağırlığıyla.

## Karar — maliyet karardan çıkarıldı
```
W = Σ a_R · w_R(z)            (a_R = oy ağırlığı, w_R = tetikleme)
W < W_min = 0,5  →  görüş yok, pozisyon korunur
P = Σ a_R·w_R·μ_R / W                       (yükselme evresi olasılığı)
U = sqrt( Σ a_R·w_R·(μ_R(1−μ_R)/n_R + (μ_R − P)²) / W )   (tahmin hatası + kurallar arası çelişki)

NAKİT iken:  P − λ·U > 0,5  →  AL        (λ = 0,5)
ALTIN iken:  P + λ·U < 0,5  →  SAT
aksi halde pozisyon korunur
```
Okunuşu: *"Yükselme evresinde olduğuna, belirsizliği düştükten sonra bile emin misin?"* Histerezis bu iki koşulun doğasından gelir; ayrıca eşik aranmaz.

**Banka komisyonu kararda kullanılmaz** (kullanıcı kararı: "şimdilik boşver"). Ancak NAV muhasebesinde %0,8/yön **tam olarak uygulanır**, yoksa sonuç gerçek olmaz. Raporda hem net NAV (masraflı) hem brüt NAV (masrafsız) verilir; aradaki fark masrafın bedelini gösterir. Masrafı karara geri koymak ileride ayrı bir sürümün konusudur.

## Dürüstlük
- Evre etiketi geriye dönüktür (zigzag), ama yalnız **onaylanmış** bacaklar öğrenilir; model girdileri as-of'tur.
- Ayın kararları yalnız önceki ay sonu kural tabanıyla verilir.
- Testler: gelecek fiyat bozma değişmezliği, kesme eşitliği, etiket olgunlaşma sınırı, tekrar üretilebilirlik, 2026 yasağı.
- **Uyarı:** v1 → v1.1 → v2 zincirinde geliştirme dönemine bakılarak yapısal değişiklikler yapıldı. Bu yüzden 2023–2025 sonuçları kanıt değil, geliştirme kaydıdır. Tek gerçek sınav 2026 testidir. v1, v1.1 ve v2 sonuçları her zaman yan yana raporlanır.
- Bu, geliştirme dönemine bakılarak yapılan **son** yapısal değişikliktir. Bundan sonra model dondurulur ve 2026'ya geçilir.

## Raporlama
Aylık: evre etiketi, modelin P ve U değerleri, tetiklenen kurallar, kararlar, doğan/ölen kurallar. Sonunda: hayatta kalan kural tabanı insan okunur biçimde, kıyaslar (pasif altın, SMA100, ideal yol, v1, v1.1), net ve brüt NAV.
