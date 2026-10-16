# TERAZİ v3 — Sonuç: teşhis doğrulandı, hedef tutulamadı

> **GÜNCELLEME (ek-4, `TERAZI_V3_ON_KAYIT_EKI_UYUM_DUZELTMESI.md`):** v3.2'nin ön kayıt §2.1'i
> ("giriş değiştirilmez") ihlal ettiği tespit edildi ve **v3.3** ile uyum sağlandı: birleşik sonsal
> yalnız satış testinde kullanılır, alış testi v2'nin kuralıdır. v3.3 net NAV **213,49**
> (v2: 202,82), 5 işlem, sıfır savrulma, maks düşüş %11,27, 11/11 nedensellik testi OK.
> **G3 yine geçmedi** (çıkış 27 Şubat) ve hedef penceremizde v3.3 v2'den 0,89 puan geride.
> Kazancın tamamı v2'nin Aralık 2023 gidiş-dönüşünden kaçınmaktan geliyor, hedeften değil.
> Ayrıntı ve ölçülmüş "kanıt açığı" (1,6–1,8 kat) ek-4'tedir. Aşağıdaki bölümler v3.0–v3.2'yi anlatır.

2026-10-16. Sıra: ön kayıt `1fcdcaf` → kod + ek-1 `278066b` → v3.0 koşusu → ek-2 `aa5ab2c` →
v3.1 koşusu → ek-3 + etiket düzeltmesi `41fc0c6` → v3.2 koşusu → bu rapor → ek-4 + v3.3.
Isıtma 2020-01→2022-12, koşu 2023-01-03→2025-12-31. **2026 verisi yüklenmedi** (testle doğrulandı).

> **Bu rapordaki 2023–2025 sayıları kanıt değildir, geliştirme kaydıdır.** v3, kullanıcının açık
> onayıyla bu döneme bakılarak ayarlandı. Tek gerçek sınav 2026'dır.

## 1. Üç denemenin sonucu

| | net NAV | brüt | işlem | 5 günde geri alım | maks düşüş | Şubat 2023 çıkışı |
|---|---:|---:|---:|---:|---:|---|
| **v2 (dondurulmuş)** | **202,82** | 215,31 | 7 | 0 | %11,67 | 23 Şub |
| v3.0 ön kayıttaki hali | 202,82 | 215,31 | 7 | 0 | %11,67 | 23 Şub |
| v3.1 iki ayrı kanal | 169,59 | 203,98 | 25 | **9** | %13,46 | 23 Şub |
| **v3.2 tek sonsal** | **203,54** | 212,49 | 5 | **0** | **%11,27** | 27 Şub |
| v3.2 makro freni yok | 203,54 | 212,49 | 5 | 0 | %11,27 | 27 Şub |
| Pasif altın | 230,82 | — | 1 | — | %10,79 | — |
| İdeal yol (geriye dönük) | 2.289,69 | — | 39 bacak | — | — | — |

Makro freni kaldırmak v3.2'de hiçbir şeyi değiştirmedi: **birleşik mimaride o fren hiç bağlayıcı
olmadı.** (v3.1'de bağlayıcıydı.)

## 2. Geçme ölçütleri

| | ölçüt | v3.2 | sonuç |
|---|---|---:|---|
| G1 | net NAV ≥ 202,82 | 203,54 | **geçti** (+0,72 = %0,35) |
| G2 | işlem ≤ 15 | 5 | **geçti** |
| G3 | Şubat 2023 çıkışı 10 Şub'dan önce | 27 Şub | **GEÇMEDİ** |
| G4 | 11 nedensellik testi (mutlak) | 11/11 OK, 274 s | **geçti** |
| G5 | maks düşüş ≤ %11,67 | %11,27 | **geçti** |

Ön kayıt §4: *"G1–G3 ve G5 sağlanmazsa v3 başarısız olarak raporlanır."* **G3 sağlanmadı → v3
başarısızdır.** 4/5 geçmiş olması bunu değiştirmez; G3, bütün çalışmanın sebebiydi.

## 3. Doğrulanan şey: H1 (teşhisin mekanizma iddiası)

Hedefi hızlandırmak, **yeni veri eklemeden**, hızlı değişkenlerin kural doğumunu kazanmasına yetti:

| | v2 evre tabanı (167 kapı) | v3 kırılma tabanı (163 kapı) | hedef |
|---|---:|---:|---:|
| `altın 1g getiri` | %0,60 | **%33,74** (en çok kullanılan) | ≥ %5 |
| `1g + 5g` | %16,17 | **%34,36** | ≥ %30 |

Kırılma dedektörünün ayırt etme gücü de gerçek: **AUC = 0,710** (29 kırılma günü, 712 diğer gün;
Q ortalaması 0,0760'a karşı 0,0555). Yani "yavaş etiket hızlı değişkenleri aç bırakıyor" teşhisi
doğruydu ve düzeltilebilirdi. **Sorun sinyalde değil, sinyali karara bağlamakta.**

## 4. Üç denemenin üç ayrı başarısızlık biçimi

### v3.0 — test ulaşılamazdı (ölçek hatası)
Ön kayıttaki `Q − λU_Q > 2·p₀` testi nadir olayda matematiksel olarak ulaşılamaz:
ölçülen `U_Q ≈ 0,85·Q`, yani sol taraf ≈ `0,57·Q` ve eşiğe varmak için Q > 0,237 gerekiyor;
koşudaki en yüksek Q 0,157. Kanal 774 günün tamamında görüş üretti, hiç ateşlemedi.
Düzeltme (ek-2): v2'nin kuralı cebirsel olarak bir z-testidir, `(P−0,5)/U > λ`; referansı p₀'ya
taşıyınca `(Q−p₀)/U_Q > λ` olur. Parametre eklemedi, `EXIT_MULT`'ı kaldırdı.

### v3.1 — iki kanal birbiriyle çelişti
Hızlı kanalın her satış gününde yavaş kanalın AL koşulu aynı anda sağlanıyordu, yani satış ertesi
işlem günü geri alınıyordu. Düzeltmeden önceki koşuda 6/6, etiket düzeltmesinden sonra 9 hızlı
gidiş-dönüş. Fiyat bu dönüşlerde −%0,64…+%1,19 arasında kaldı (hiçbir yere gitmedi) ama her
dönüşte 2×%0,8 komisyon ödendi: brüt 203,98 − net 169,59 = **34,4 puan boşa masraf.**

Duyarlılık (önceden beyan edildi, seçim için kullanılmadı) bunun tek bir eşik sorunu olmadığını
gösterdi:

| ayar | net | işlem | Şubat 2023 |
|---|---:|---:|---|
| m=3 | 128,65 | 49 | 23 Şub |
| **m=5 (birincil)** | 181,66¹ | 19 | 23 Şub |
| m=10 | 174,55 | 25 | **6 Şub ✓** |
| λ=1,0 | 202,82 | 7 (hiç ateşlemedi) | 23 Şub |
| λ=2,0 | 202,82 | 7 (hiç ateşlemedi) | 23 Şub |

¹ etiket düzeltmesinden önceki değer; düzeltmeden sonra 169,59.

**Şubat 2023'ü yakalayan tek ayar (m=10) aynı zamanda 25 işlemle savrulup 28 puan kaybediyor;
savrulmayan ayarlar hiç ateşlemiyor.** Aralığın hiçbir yerinde ikisi birlikte olmuyor.

### v3.2 — çelişki çözüldü, ama nadir olay kanalı kararı felç etti
Birleşik sonsal çelişkiyi tamamen bitirdi: **5 günde geri alım 9 → 0**, maksimum düşüş %13,46 → %11,27,
işlem 25 → 5. Mimari düzeltme kendi hedefini tuttu.

Bedeli ise v2'nin en iyi özelliğiydi: **kusursuz 3 Ocak 2023 girişi kayboldu.**

| 2023-01-03 | değer |
|---|---|
| evre kanalı `P − λU` | 0,5080 → **AL** |
| birleşik `P_etkin − λU_etkin` | 0,4330 → **alamadı** |

Sebep sonsalın yeri değil, **belirsizliğin patlaması**. Logit ölçeğinde o gün:

```
evre kanalı     s_P = 0,076 / (0,546 × 0,454) = 0,307
kırılma kanalı  s_Q = 0,055 / (0,0650 × 0,9350) = 0,905     ← 3,0 KAT daha büyük
birleşik        s   = √(0,307² + 0,905²) = 0,956
U: 0,076 → 0,2367   (3,1 kat)
```

Nadir olay kanalının **oransal** belirsizliği, olasılık küçük olduğu için yapısal olarak büyük
(Q(1−Q) payda küçülüyor). İki kanalı eşit ağırlıklı bağımsız kanıt olarak birleştirmek, gürültülü
kanalın kararı ele geçirmesine yol açıyor. Tüm koşu boyunca ortalama belirsizlik 0,1037 → 0,1607
(1,5 kat) ve günlerin **%17'si** kararsızlık bandının içinde kaldı.

Sonuç: v3.2'nin +0,72 puanı daha iyi zamanlamadan değil, **eylemsizlikten** geliyor — v2'nin
2023-12-12 satış / 2024-01-02 geri alım dönüşünü (fiyat %+4,53 + %1,6 masraf) yapmadı.
Düzeltmek istediğimiz işlemde ise **daha kötü** oldu:

| ilk gidiş-dönüş | NAV |
|---|---:|
| v2: AL 01-03 @1836,33 → SAT 02-23 @1826,56 | 97,88 |
| v3.2: AL 01-27 @1926,13 → SAT 02-27 @1810,02 | **92,47** |

Girişi %+4,89 pahalı, çıkışı %−0,91 kötü. **Hedef işlemde 5,4 puan kayıp.**

(Not: "v3.2 yalnız kanal sessizken işlem yapıyor" diye bir hipotez kurdum, **yanlış çıktı**:
5 işlemin yalnız 1'i kanalın sessiz olduğu güne denk geldi ve sessiz gün sayısı 5/774.)

## 5. Bulunan ve düzeltilen kusurlar

1. **Ölçek hatası** (ek-2): nadir olay kuyruğunda `Q − λU > k·p₀` testi ulaşılamaz. Düzeltildi.
2. **Etiket kusuru** (nedensellik testi yakaladı): kırılma penceresi onay gününe kadar uzadığı
   için bacağın **dibini** de kırılma sayıyordu — 2020-08-12, aynı anda düşüş bacağının onay günü
   ve yükseliş bacağının ilk günü. Satış sinyaline tam tersini öğretiyordu. Pencere artık yalnız
   evre etiketi "düşme" olan günleri kapsıyor; böylece v3.2'nin matematiğinin dayandığı
   `brk ⟹ düşme` çıkarımı zorunlu kılınmış oldu.
3. **Yama hatası** (kendi kodumda): `Pe` anahtarı iki kez eklendi, sözdizimi hatası. Düzeltildi.

## 6. Ne öğrendik — kalıcı bulgu

1. **Teşhis doğruydu ve mekanizma düzeltilebilir.** Öğrenme hedefinin hızı, hangi değişkenlerin
   kural doğumunu kazandığını belirliyor. Yavaş bir etiket hızlı değişkenleri gürültü sayıp eliyor;
   hedefi hızlandırmak, veri eklemeden bunu tersine çeviriyor (%0,60 → %33,74).
2. **Ama nadir olay kanalı karar katmanına eşit kanıt olarak bağlanamıyor.** Üç farklı bağlama
   biçimi üç farklı patolojiye düştü: ayrı eşik → ulaşılamaz; ayrı oy → çelişki ve savrulma;
   birleşik sonsal → oransal belirsizlik baskınlığı ve felç. Ortak kök, Q ≈ 0,07 düzeyinde
   `U_Q/(Q(1−Q))` oranının evre kanalının 3 katı olması.
3. **Yapısal sonuç:** kırılma anı, bu 35 değişkenden **ayırt edilebiliyor** (AUC 0,710) ama
   **işlem masrafını karşılayacak isabetle değil**. Hedefi yakalayan her ayar, aynı zamanda
   savrulma masrafını doğuruyor.
4. Bu, daha önce ölçülen bulguyla uyumlu: tepe zamanlaması sinyali bu özellik kümesinde büyük
   ölçüde yok (geriye dönük en iyi eşikler 199–218, tam geçmiş-bilgili lojistik 206 — hepsi
   dürüst gerçek zamanlı 213,5'in altında).
5. **Kullanıcının seçtiği fren (makro onayı) v3.2'de hiç bağlayıcı olmadı.** v3.1'de bağlayıcıydı
   ama yanlış yerdeydi: kaçak satış tarafında değil **geri giriş** tarafındaydı.

## 7. Karar

Ön kayıt §4 gereği **v3 başarısızdır** (G3 hiçbir sürümde geçmedi — v3.3 dâhil).

**v2 dondurulmuş haliyle, kodu değiştirilmeden 2026'ya girer.** v3.3'ün de yanında girip girmeyeceği
ayrı bir kullanıcı kararıdır; girerse "G3'ü geçmemiş, 4 denemeden sonra elde edilmiş aday"
etiketiyle ve v2 ile yan yana raporlanır. Beşinci mimari denenmeyecektir.

Dondurulmuş dosyalar: `TERAZI_V3_DONDURULMUS_MODEL.json` (v3.3, birincil mod `unified_sell`),
`TERAZI_V3_3_SONUC.json`, `TERAZI_V3_2_SONUC.json`, `TERAZI_V3_0_ONKAYIT_HALI_SONUC.json`,
`TERAZI_V3_DUYARLILIK.json`, `reports/`, `reports_v3_0/`.

Masrafı karara geri koymak (kullanıcının "banka komisyonu şimdi boşver, sonra ayarlarız" dediği
madde) bu çalışmanın işaret ettiği bir sonraki adımdır: v3'ün üç patolojisinin hepsinde eksik olan
şey, kararın "bu hareket 2×%0,8'i karşılar mı?" sorusunu soramamasıydı.
