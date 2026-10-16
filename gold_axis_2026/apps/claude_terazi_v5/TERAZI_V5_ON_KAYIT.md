# TERAZİ v5 — Gecikmeye dayanıklı hedef | Ön kayıt

2026-10-16. Dal: `research-gold-claude-pusula-v1-20261016`.
**Bu dosya v5 modelinin kodundan ve sonuçlarından ÖNCE commit edilmiştir.** Yalnız hedef
fonksiyonu (`hedef_v5.py`) yazılıp hangi hareketleri seçtiği kontrol edilmiştir; model koşulmadı.
Isıtma 2020-01→2022-12, geliştirme koşusu 2023-01-03→2025-12-31. **2026 verisi yüklenmez.**

## 0. Neden v5

v4'ün hedefi (kullanıcının 24 hareketi, net ≥ %2,4) ideal yolun **tam** dönüş noktalarıydı.
Ölçüm (kullanıcıyla birlikte, 2023): gerçek zamanlı bir algoritma dönüşü ancak 2–3 gün geç
fark edebilir ve bu gecikmeyle 2–5 günlük hareketlerin hepsi zarara döner; kullanıcının
7 hareketlik 2023 planı 139,05'ten 2 gün gecikmeyle 114,08'e iner. Yani v4'ün hedefi, hiçbir
gerçek zamanlı modelin ulaşamayacağı şeyleri de içeriyordu.

v5 hedefi, **gecikmeyle bile kârlı kalan** hareketlerdir. Kullanıcı bu yönü onayladı
("kur bakalım model başarabilecek mi").

Ayrıca v4'te tespit edilen kodlama hatası düzeltilir (bkz. §2).

## 1. Hedef — otomatik kural, elle seçim yok

1. Maliyetli ideal yol (DP, %0,8/yön) dönüş noktalarını verir: dipler (bacak başları) ve
   tepeler (bacak sonları).
2. Bir aday hareket = (dip_i → tepe_j), j ≥ i. Değeri, **K işlem günü geç** uygulanarak
   hesaplanır: giriş `ask[dip_i + K]`, çıkış `bid[tepe_j + K]`, iki yön %0,8.
3. Örtüşmeyen hareketlerden, gecikmeli NAV'ı en büyük yapan dizi DP ile seçilir; yalnız
   gecikmeli net getirisi > 0 olan hareketler seçilebilir. Bu, kısa hareketleri eler ya da
   komşu uzun harekete birleştirir.
4. Etiket: seçilen hareketlerin `[dip, tepe)` günleri = **ALTINDA ol (1)**, diğerleri 0.

**K = 2** (birincil). Duyarlılık: K = 3 (seçim için kullanılmaz).

Kural kontrolü (yalnız hedef, model yok): 2023'te 4 hareket seçiyor —
3 Oca → 26 Oca, 8 Mar → 5 May, 21 Ağu → 31 Ağu, 5 Eki → 4 Ara — gecikmeli NAV 120,40.
2023–2025: 10 hareket, gecikmeli NAV **310,15** (= gerçekçi tavan), taban oran %71.
2020–2022 ısıtma: 12 hareket, taban oran %46.

### Olgunlaşma (nedensellik)
v4'teki gibi yuvarlanan hesap: her öğrenme anında hedef yalnız o ana kadarki fiyatlarla
yeniden hesaplanır; yalnız `tepe + K` günü gözlenmiş, kapanmış bölge etiketlenir; bir gün
ilk olgunlaştığı değerle öğrenilir ve yeniden etiketlenmez.

## 2. Model — v4 makinesi + güven hatası düzeltmesi

- Kural makinesi, kapılar, doğum/ölüm, 35 değişken: v4/v2 ile **aynı**. Yeni özellik yok.
- Karar: v4.1'deki gibi `z = (P − p₀)/U`; `z > λ` AL, `z < −λ` SAT, λ = 0,5. p₀ öğrenilmiş
  etiketlerin taban oranı.
- **Düzeltme (v4 düzeltme notunda tespit edildi, `f243ea7`):** kuralların saha güveni de
  taban orana göre ölçülür: `agree = (μ_önce ≥ p₀) == (y ≥ 0,5)`. v4'te referans 0,5 idi ve
  "hep nakit" diyen kurallar bedava güven kazanıyordu.

### Öğrenme sıklığı
- **Birincil: aylık** (v4 ile aynı; hedef + güven düzeltmesinin etkisini ayrı görmek için).
- Beyan edilmiş ikincil varyant: **haftalık** öğrenme ve yeniden yapılanma. Raporlanır;
  geç/kal kararını birincil verir.

## 3. Geçme ölçütleri (sonuçlara bakmadan)

| | ölçüt |
|---|---|
| G1 | 2023–2025 net NAV ≥ **230,82** (al-tut) |
| G2 | işlem sayısı 10–60 |
| G3 | pozisyonun (tam dönem) hedefle uyumu ≥ %65 gün |
| G4 | nedensellik testlerinin tamamı geçer — **mutlak** |
| G5 | Ocak 2023 hareketinin (3–26 Oca) günlerinin ≥ %50'sinde altında |
| G6 | maksimum düşüş ≤ %11,67 |

Referans tavan: hedefin gecikmeli NAV'ı 310,15. Model buna ne kadar yaklaştığıyla da raporlanır.

## 4. Dürüstlük

- K = 2, 2023 üzerinde kullanıcıyla birlikte yapılan gecikme analizinden sonra seçildi.
  Dolayısıyla 2023–2025 sonuçları **geliştirme kaydıdır**, kanıt değildir. Tek sınav 2026.
- Bu, v4 ön kaydında "beşinci mimari denenmeyecek" maddesine rağmen yapılıyor: mimari aynı,
  değişen hedef ve bir kodlama hatasının düzeltmesi; kullanıcının açık talebiyle.
- Hedef kuralı ve K, 2023–2025 sonucunu iyileştirmek için değiştirilmeyecek.
