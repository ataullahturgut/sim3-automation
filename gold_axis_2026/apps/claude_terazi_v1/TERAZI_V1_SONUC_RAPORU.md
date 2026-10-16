# TERAZİ v1 — Kural tabanlı uyarlanır çıkarım ağı: maraton sonucu

2026-10-16. Sıra: mimari ön kaydı `93d733a` → ilk koşu → düzeltme eki (`TERAZI_V1_MIMARI_DUZELTME_EKI.md`) → bu sonuç. Geliştirme dönemi: ısıtma 2020-01→2022-12, işlem 2023-01-03→2025-12-31. **2026 verisi yüklenmedi.**

## Mimari çalıştı mı? Evet.
Model kuralları **kendisi keşfetti**, ben vermedim. 36 ay boyunca:
- **76 kural doğdu, 36'sı öldü, 40'ı hayatta kaldı.** Kural tabanı yaşayan bir yapı oldu.
- Her karar, tetiklenen kurallarla gerekçelendirildi.
- Kurallar oy hakkını yalnız **doğduktan sonraki** günlerde kazandı; keşfedildikleri veride oy kullanamadılar.

Hayatta kalan en güçlü kurallardan birkaçı (güven = sahada sınanmış yönlü isabet):

| Kural | Beklenen 10g getiri | Güven | Saha kanıtı |
|---|---:|---:|---:|
| son NFP sürprizi < +1,0σ **VE** Nasdaq 20g > −0,5σ | +%1,48 | +0,43 | 57,9 |
| COT spekülatif pozisyon > +1,0σ | +%1,74 | +0,39 | 59,2 |
| Nasdaq 20g > −1,0σ | +%1,52 | +0,37 | 96,5 |
| altın 60g getiri < +1,0σ **VE** COT > +1,0σ | +%2,06 | +0,36 | 23,8 |
| GVZ < 0σ **VE** COT > +1,0σ | +%2,19 | +0,35 | 12,9 |
| 10Y reel faiz 20g değişim < +1,0σ **VE** COT < 0σ | +%1,63 | +0,35 | 21,2 |

Okunuşu: *"Hisse piyasası çökmemişse ve son istihdam verisi aşırı güçlü gelmemişse, önümüzdeki 10 günde altından ortalama %1,5 beklerim; bu kural doğduğundan beri 58 günlük kanıtla sınandı."*

## Ekonomik sonuç: zayıf

| | 100 USD → | Maks. düşüş | İşlem |
|---|---:|---:|---:|
| **TERAZİ v1** | **131,10** | %10,36 | 1 |
| DENEYİM v1.2 | 220,07 | %10,79 | 1 |
| SMA100 trend kuralı | 215,36 | %11,42 | — |
| Pasif altın | 230,82 | %10,79 | 1 |
| İdeal yol (geriye dönük) | 2.289,69 | — | 39 bacak |

**Nedeni mimarinin kendi dürüstlük mekanizması:** Bir kural oy hakkı kazanmak için doğduktan sonra sahada sınanmak zorunda. Güven formülündeki küçültme (k + 10) ve görüş eşiği (W ≥ 0,5) birlikte, modelin konuşmaya başlaması için birkaç kuralın yeterli saha kanıtı toplamasını gerektirdi.

Sonuç: **model 36 ayın 30'unda hiç görüş üretmedi.** İlk görüşünü **2025-05**'te verdi.

## Konuştuğu dönemde ne yaptı?

| 2025-05-14 → 2025-12-31 | Sonuç |
|---|---:|
| TERAZİ v1 | +%33,3 |
| Altın (aynı dönem, maliyetli) | +%31,1 |

Yani kuralları olgunlaştıktan sonra modelin kararları altını hafifçe geçti. Ama bu yalnız 8 ay ve tek bir giriş; istatistiksel bir kanıt değil.

## İlk koşu (düzeltme öncesi) — kayıt için
Ön kayıttaki belirsizlik formülü, ortalamanın standart hatası yerine sonuç dağılımının genişliğini kullanıyordu. Bu hâliyle model **hiçbir işlem yapmadı** (NAV 100,00; 753 günün 662'sinde görüş yok). Düzeltme ve gerekçesi `TERAZI_V1_MIMARI_DUZELTME_EKI.md`'de; bundan sonra performansa bakarak hiçbir parametre değiştirilmedi.

## Dürüst değerlendirme

**Kazanımlar:**
- İstenen paradigma kuruldu: kuralları veriden keşfeden, kuralları doğup ölen, her kararını kuralla açıklayan özgün bir mimari. ANFIS kopyası değil (karşılaştırma tablosu ön kayıtta).
- Keşfedilen kurallar ekonomik olarak anlamlı: COT spekülatif pozisyon, reel faiz yönü, hisse piyasası durumu ve altın oynaklığı etrafında toplandı. Bu, DENEYİM v1'in ağırlık analiziyle de uyumlu.
- Dürüstlük mekanizması gerçekten çalıştı: 36 kural, sahada sınanınca başarısız olduğu için **öldü**. İçsel uyumla oy hakkı kazanan kural olmadı.

**Eksikler:**
- Çok temkinli: 2,5 yıl boyunca sessiz kaldı. Bu dönemde altın yaklaşık iki katına çıktı, model nakitte bekledi.
- Tek işlem yaptı; zirve zamanlaması yine öğrenilemedi. Bu, önceki teşhisle tutarlı: bu veri kümesinde zirve sinyali zayıf (tam kopya üst sınır testi 206 < dürüst 213,5 < pasif 230,8).
- 8 aylık görüş dönemi, becerinin kanıtı değil.

## Dondurma ve sonraki adım
Kural tabanı ve tüm sabitler `TERAZI_V1_DONDURULMUS_MODEL.json` olarak donduruldu. 2026 testi bu dosyayla, kod değiştirilmeden yapılacak. 2026'ya girerken modelin 40 kuralı ve 6 yıllık saha kanıtı olacak — yani ilk kez "deneyimli" bir model test edilecek.

Parametre ayarı yapılmayacak. Mimariyi değiştirmek gerekirse yeni ön kayıtla TERAZİ v2 yazılır ve yalnız 2026-10 sonrası ileri dönemde değerlendirilir.
