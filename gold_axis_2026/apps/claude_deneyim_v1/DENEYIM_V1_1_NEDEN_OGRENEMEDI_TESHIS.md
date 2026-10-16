# Teşhis: model neden iyi öğrenemedi? (aylık hata analizi ve üst sınır testi)

2026-10-16. Soru: "kötü öğrendiği aylara bakıp ona göre iyileştirme yapmak daha iyi olmaz mı?"
Cevap: aylara baktım. Sonuç, aylık düzeltmenin işe yaramayacağını ve yapılırsa 2026 testini geçersiz kılacağını gösteriyor. Ölçümler aşağıda.

## 1. Hata nerede? (36 ayın tamamı)
İdeal yol ile modelin aylık log getirileri arasındaki toplam fark **163,3 puan**. Bu farkın dağılımı:

| Hata tipi | Gün | Kayıp payı |
|---|---:|---:|
| **Geç çıkış** (ideal NAKİT derken altın tutmak) | 271 | **134,9 puan (%83)** |
| Kaçırılan giriş (ideal ALTIN derken nakitte kalmak) | 46 | 28,4 puan (%17) |

En kötü aylar: 2023-03 (15,4 puan, kaçırılan giriş), 2024-11 (11,5), 2025-10 (10,9), 2025-04 (8,8), 2025-05 (8,3) — son dördü tamamen geç çıkış.
**Teşhis:** Model girişleri makul yapıyor; sorun neredeyse tamamen **zirvelerde satamamak**.

## 2. Karar katmanı mı suçlu, sinyal mi zayıf?
Modelin kendi gerçek zamanlı sinyallerini alıp, eşikleri **geriye dönük en iyi** (yani kopya çekerek) seçtim. Eğer karar katmanı sinyali boşa harcıyor olsaydı, bu çok daha yüksek bir sonuç verirdi:

| Sinyal | Geriye dönük en iyi eşikle NAV |
|---|---:|
| E[10 günlük getiri] (v1.1'in kullandığı) | 199,2 |
| −P(düşüş) | 218,1 |
| İdeal pozisyon olasılığı (v1) | 193,9 |
| **Modelin dürüst, gerçek zamanlı sonucu** | **213,5** |

Model, sinyalinde olanın neredeyse tamamını zaten çıkarmış. Eşikleri aylara göre ayarlamak kazanç getirmez.

## 3. Bilgi veride var mı? (üst sınır testi)
35 özelliğin **tamamını** ve 2023–2025'in **bütün ideal etiketlerini** görerek (tam kopya) bir model eğittim, eşikleri de geriye dönük seçtim:

| Yöntem | İdeal pozisyon doğruluğu | NAV |
|---|---:|---:|
| Tam kopya lojistik (orta düzenleme) | %74,0 | 206,0 |
| Tam kopya lojistik (çok esnek) | %73,9 | 197,7 |
| En iyi tek özellik (GVZ düzeyi), geriye dönük en iyi eşikle | — | 237,3 |
| **Dürüst gerçek zamanlı model** | — | **213,5** |
| Pasif altın | — | 230,8 |
| İdeal yol | %100 | 580,6 |

**Kritik sonuç:** Geleceği tamamen bilerek eğitilen model bile 206 yapıyor — yani dürüst modelden (213,5) ve pasif altından (230,8) **daha kötü**. Sebebi: %74 doğruluk kulağa iyi geliyor ama yanlış kalan %26, dönüş noktalarına denk geliyor ve her yanlış dönüş %1,6 maliyet yiyor.

## 4. Neden böyle?
- İdeal yol 39 bacaktan oluşuyor, ortalama net %4,73. Bu yolu yakalamak için dönüşleri **birkaç gün içinde** bilmek gerekiyor.
- 2023–2025'te altın yaklaşık %130 yükseldi. Bu dönemde nakitte geçirilen her gün sistematik kayıp.
- Elimizdeki veriler (fiyat yapısı, faiz, dolar, GVZ, COT, CPI/NFP sürprizleri, Nasdaq/petrol/gümüş) altının **zirvelerini** birkaç gün hassasiyetinde işaret etmiyor. En iyi tek özellik bile tam kopya eşikle pasifi ancak 6,5 puan geçiyor.

## 5. Aylık düzeltme neden yapılmamalı?
Bir ayın kaybına bakıp kural eklemek (örneğin "2025-04'te GVZ 4 sigmaya çıkmışken sat") o ayı düzeltir. Ama yukarıdaki üst sınır testi, bu tür kuralların bütünde kazanç üretmediğini gösteriyor: gelecek tamamen bilindiğinde bile toplam sonuç pasifin altında. Dolayısıyla aylık düzeltmelerle elde edilecek kazanç, gerçek bir örüntü değil, o aya özel gürültüye uyum olur. Üstelik 2026 testini anlamsız hale getirir, çünkü model artık "test edilecek bir hipotez" değil, "geçmişe uydurulmuş bir eğri" olur.

## 6. Meşru iyileştirme yolları (hangisi seçilirse ön kayıtla yapılır)
1. **Hedefi değiştir.** "39 bacağı yakala" ulaşılamaz bir hedef. Daha az ve daha büyük hareket hedefleyen bir ideal tanımı (örneğin yalnız %8'den büyük düşüşlerden kaçınmak) öğrenilebilir olabilir.
2. **Yeni veri ekle.** Eksik olan şey model değil, bilgi: ilk yayın zamanı doğrulanmış haber akışı, ETF akışları, merkez bankası alımları, opsiyon piyasası göstergeleri. Zirveler bu verilerde görünebilir.
3. **Modeli olduğu gibi test et.** "İyi bir anda gir ve tut" bulgusu dürüst bir sonuç; 2026'da da geçerli mi diye sınanabilir.

Önerim: 3 ile devam edip (çünkü v1.1 dondurulmuş durumda ve test bedava bilgi verir), sonra 1 veya 2'yi yeni ön kayıtla denemek.
