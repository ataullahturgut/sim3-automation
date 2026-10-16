# TERAZİ v3 — İki kanallı karar (giriş yavaş, çıkış hızlı) | Ön kayıt

2026-10-16. Dal: `research-gold-claude-pusula-v1-20261016`. **Bu dosya v3 kodundan ve sonuçlarından ÖNCE commit edilmiştir.**
Isıtma 2020-01→2022-12, geliştirme maratonu 2023-01→2025-12. **2026 verisi yüklenmez.**

## 0. Dondurmanın bozulması — açık kayıt

v2 ön kaydı şunu yazmıştı: *"Bu, geliştirme dönemine bakılarak yapılan son yapısal değişikliktir."*
Bu taahhüt **bilerek ve kullanıcının açık onayıyla** bozulmaktadır. Kullanıcı, Şubat 2023 teşhisini gördükten
sonra v3'ün 2023–2025'e bakılarak serbestçe ayarlanmasını seçti.

Bunun bilimsel bedeli burada peşinen kabul edilir:

- **v3'ün 2023–2025 sayıları kanıt değildir, geliştirme kaydıdır.** Rapor hiçbir yerde bunları
  "test başarısı" olarak sunmayacaktır.
- **Tek gerçek sınav 2026'dır.** v2 ve v3, 2026 verisi hiç görülmeden dondurulur ve 2026'ya
  **tek seferde birlikte** girer. Sıra böyle kurulmuştur ki v3, v2'nin 2026 sonucunu bilerek
  tasarlanmış olmasın; aksi halde 2026 v3 için de yanardı.
- v1, v1.1, v2 ve v3 sonuçları her zaman yan yana raporlanır.

## 1. Teşhis — P&L'e değil, algoritmanın yapısına dayanır

Bu iki kusur, getiri veya NAV'a bakılmadan, yalnız dondurulmuş v2 kural tabanı ve panel
üzerinden ölçüldü. Dolayısıyla "Şubat 2023'te para kaybettik" gözlemine değil, belirtim
kusuruna dayanıyorlar.

### Kusur 1 — Tek etiket, tek hız
Kural doğumu adayları **yalnız** %5 zigzag evre etiketini açıklama başarısıyla puanlıyor
(`restructure`, artıklara karşı z kanıtı). Bir günlük getiri, %5 ile yumuşatılmış yavaş bir
etiketi açıklayamaz; doğum süreci onu haklı olarak gürültü sayıp eledi.

Ölçüm — dondurulmuş v2 tabanında (60 kural, **167 kapı**) değişken başına kapı sayısı:

| kapı | pay | değişken |
|---:|---:|---|
| 53 | %31,74 | 60g zirveye uzaklık |
| 41 | %24,55 | altın 20g getiri |
| 26 | %15,57 | altın 5g getiri |
| 21 | %12,57 | COT managed money net |
| **1** | **%0,60** | **altın 1g getiri** |

Kırılma anında (2023-02-03 ve 02-06) **−2,0σ** ile hareket eden tek değişken günlük getiriydi
ve tabanda 167 kapının 1'ini alıyor.

### Kusur 2 — Düzey standartlaştırması işareti tersine çeviriyor
"60g zirveye uzaklık" bir **düzey** değişkeni ve kendi genişleyen tarihçesine göre
standartlaştırılıyor. Tipik durum zaten düşüşte olmak olduğu için, gerçek bir çöküş
"normalden iyi" diye okunuyor.

Ölçüm (2023-02-06, o güne kadarki tarihçeyle):
tarihçe ortalaması %−4,78, std %3,40; o günün değeri %−3,89 → **z = +0,26σ**.
İki seansta %3,8 düşen altın, modelin en çok kapı kurduğu değişkende artı işaretle göründü.

### Ortak kök
Giriş ve çıkış aynı soruya iki yönden bakıyor (`P−λU>0,5` ve `P+λU<0,5`). Oysa giriş yavaş bir
soru ve model onu doğru yapıyor; çıkış hızlı bir sorudur ve kendi kanalı yoktur. Gecikme tek bir
yerde değil: yavaş etiketten aşağı, doğan her kapıya miras kalıyor. θ'yı %3'e çekmek bu yüzden
işe yaramadı (202,82 → 182,96): mekanizmayı değiştirmedi, yalnız yavaş etiketi gürültülü yaptı.

## 2. v3 mimarisi — yeni veri yok, yeni soru var

**Önemli kısıt: v3 hiçbir yeni özellik (feature) eklemez.** Aynı 35 tarihsiz durum değişkeni
kullanılır. Değişen tek şey çıkışın öğrenme hedefidir. Teşhis doğruysa, hedefi hızlandırmak
elimizdeki günlük getiri değişkeninin kural doğumunda **kendiliğinden** kazanmasına yol açmalıdır.
Bu, aşağıda H1 olarak sınanabilir biçimde yazılmıştır.

### 2.1 Giriş kanalı — v2'den aynen, değiştirilmez
Evre etiketi (zigzag θ=%5, onaya dayalı olgunlaşma), aynı kural makinesi, aynı güven formülü:

```
NAKİT iken:  P − λ·U > 0,5  →  AL        (λ = 0,5)
```

Gerekçe: giriş zaten kusursuz çalışıyor (2023-01-03 girişi ayın geriye dönük en iyi alış günüydü,
%0,00 fark). Çalışan şey ellenmez.

### 2.2 Çıkış kanalı — yeni: "kırılma" etiketi

Zigzag bacakları zaten tanımlı. Bacak **tepesi**, yönün +1 → −1 döndüğü pivot noktasıdır.

```
brk[i] = 1   eğer  0 < i − tepe_indeksi ≤ m        (düşen bacağın ilk m günü)
brk[i] = 0   aksi halde
m = 5 işlem günü
```

Hedef artık "bu gün düşen bacağın bir günü mü" değil, **"bu gün tepe kırılma anı mı"**.
Fark kritik: düşen bacağın çoğu günü tepeden uzaktır ve orada günlük getiri bilgi taşımaz;
ilk m gün ise tam olarak günlük getirinin −2σ gittiği penceredir.

**Olgunlaşma (nedensellik) — v2 ile aynı:** `brk[i]` ancak o bacağın dönüşü onaylandığında
(fiyat uçtan %5 ters hareket ettiğinde) bilinir. Öğrenmeye yalnız ay sonuna kadar onaylanmış
etiketler girer. `conf[i]` v2'deki zigzag onay zamanıdır, değişmez.

m = 5 önceden seçilmiştir (bir işlem haftası). Duyarlılık m ∈ {3, 5, 10} için ayrıca raporlanır;
seçim için kullanılmaz.

### 2.3 Çıkış kararı — ölçekten bağımsız eşik

Kırılma etiketinin taban oranı 0,5 değildir (bacak başına m gün). Bu yüzden 0,5 eşiği anlamsızdır.
Taban oran **yalnız ısıtma döneminden (2020-01→2022-12)** hesaplanır ve dondurulur:

```
p0 = (ısıtma döneminde onaylanmış brk etiketlerinin ortalaması)
Q  = Σ a_R·w_R·μ_R / W          (kırılma olasılığı, çıkış tabanından)
U_Q= v2'deki ile aynı belirsizlik formülü
```

Karar:
```
ALTIN iken:  ( Q − λ·U_Q > 2·p0 )  VE  ( makro onayı )   →  SAT      (λ = 0,5)
             veya v2'nin kendi çıkış koşulu  P + λ·U < 0,5  →  SAT
```

"2·p0" = kırılma olasılığı, belirsizliği düştükten sonra bile koşulsuz orandan **en az iki kat**
yüksek. Bu bir taranmış eşik değil, önceden beyan edilmiş bir konvansiyondur.
Duyarlılık 1,5× ve 3× için ayrıca raporlanır; seçim için kullanılmaz.

v2'nin eski çıkış koşulu **kaldırılmaz**, yanında durur: yavaş kanal hâlâ uzun ve derin
evre dönüşlerini yakalayabilir.

### 2.4 Makro onayı — yanlış alarm freni (kullanıcı kararı)

Hızlı kanal tek başına işlem sayısını artırır; kullanıcı "zırt pırt girip çıkma" istemiyor.
Fren olarak **fiyat kırılması tek başına yetmez**, faiz tarafının da altına karşı dönmesi gerekir:

```
makro onayı  ≡  ( rr_d5 > 0 )  VEYA  ( y2_d5 > 0 )
```
(10Y reel faizin 5 günlük değişimi pozitif, veya 2Y faizin 5 günlük değişimi pozitif.)

Ekonomik gerekçe önceden beyan edilir: altının evre kırılmaları reel/kısa faiz kanalından gelir;
faizler altına karşı dönmemişken gelen fiyat kırılması daha büyük olasılıkla gürültüdür.
Değişkenlerden biri eksikse (None) o koşul yanlış sayılır; ikisi de eksikse makro onayı yoktur.

### 2.5 Değişmeyenler
Kapı biçimi σ(d(z−c)/s), s=0,5; ızgara ±1,5σ; 1–3 kapı; ρ=0,995; aylık doğum 3, ölüm kuralları,
taban üst sınırı 60; dereceli doğum güveni c₀ ve `güven=(2h−k+10c₀)/(k+10)`; standartlaştırma
(genişleyen pencere, ±4 kırpma, MIN_HIST=60). Çıkış tabanı bunların **ayrı bir kopyasını** tutar;
iki taban birbirine karışmaz. Banka komisyonu **karara girmez**, NAV'a %0,8/yön **tam** uygulanır.

## 3. H1 — teşhisin sınanabilir yapısal tahmini

Bu, sonuçlara bakmadan yazılmış ve yanlışlanabilir bir tahmindir. Hedefi hızlandırmak elimizdeki
hızlı değişkenlerin kural doğumunu kazanmasına yol açmıyorsa, teşhis yanlıştır.

**Taban (dondurulmuş v2, 167 kapı):** g_r1 = %0,60; g_r1 + g_r5 = %16,17.

**Tahmin (v3 çıkış tabanı için):**
- H1a: `g_r1` kapı payı **≥ %5** (v2'nin ~8 katı)
- H1b: `g_r1 + g_r5` kapı payı **≥ %30** (v2'nin ~2 katı)

Tutmazsa rapora "H1 yanlışlandı, teşhis hatalıydı" diye yazılır ve v3 performansı ne olursa olsun
mekanizma iddiası geri çekilir.

## 4. Geçme ölçütleri (geliştirme dönemi; kanıt değil)

Önceden beyan edilir ki sonradan hangi sayının "iyi" olduğu uydurulmasın:

- **G1:** v3 net NAV ≥ v2 net NAV (202,82).
- **G2:** işlem sayısı ≤ 15 (v2: 7). Üstü "zırt pırt" sayılır ve fren yetersiz demektir.
- **G3:** Şubat 2023'te çıkış 10 Şubat'tan önce gerçekleşir (kârlı pencere 1–10 Şubat'tı).
- **G4:** 7 nedensellik testinin tamamı geçer. **Bu koşul mutlaktır**; diğerleri sağlansa bile
  G4 geçmezse v3 reddedilir.
- **G5:** maksimum düşüş v2'den (%11,67) kötü değil.

G1–G3 ve G5 sağlanmazsa v3 **başarısız olarak** raporlanır ve v2 dondurulmuş haliyle 2026'ya
tek başına girer. Negatif sonuç da sonuçtur.

## 5. Yapılmayacaklar

- 2023–2025 üzerinde m, eşik çarpanı (2×), λ veya makro onay koşulu için **en iyi değeri arayan
  tarama yapılmaz.** Kullanıcı serbest ayara izin verdi; yine de taramayla seçmek bu dosyadaki
  her sayıyı anlamsız kılar. Duyarlılıklar raporlanır, seçim için kullanılmaz.
- Yeni özellik (feature) eklenmez; panel ve `deneyim_states.py` değiştirilmez.
- v2 kodu ve `TERAZI_V2_DONDURULMUS_MODEL.json` **ellenmez**; v3 ayrı klasörde durur.
- 2026 verisi yüklenmez; `load_rows(dev_only=True)` sınırı testle doğrulanır.

## 6. Raporlama

Aylık: evre ve kırılma etiketleri, P/U ve Q/U_Q, tetiklenen kurallar, kararlar, doğan/ölen kurallar.
Sonunda: iki kural tabanı insan okunur biçimde, H1 kapı sayımı, G1–G5 tablosu, Şubat 2023 dökümü,
m ve eşik duyarlılığı, v1 / v1.1 / v2 / v3 ve pasif altın / SMA100 / ideal yol karşılaştırması,
net ve brüt NAV.
