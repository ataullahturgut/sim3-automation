# TERAZİ v3.3 — Ön kayıt eki 4: v3.2 ön kaydı ihlal etti, uyum düzeltmesi

2026-10-16. Ana ön kayıt `1fcdcaf`, ek-1 `278066b`, ek-2 `aa5ab2c`, ek-3 + etiket düzeltmesi `41fc0c6`,
v3 sonuç raporu `84490a3`.

## İhlal

Ana ön kayıt §2.1 şunu yazıyor:

> **### 2.1 Giriş kanalı — v2'den aynen, değiştirilmez**
> Gerekçe: giriş zaten kusursuz çalışıyor (2023-01-03 girişi ayın geriye dönük en iyi alış günüydü,
> %0,00 fark). **Çalışan şey ellenmez.**

v3.2 bu maddeyi **ihlal etti.** Birleşik sonsal tek bir sayı (`P_etkin`) ürettiği ve bu sayı hem
alış hem satış testinde kullanıldığı için giriş davranışı değişti: 2023-01-03 → 2023-01-27
(24 gün geç, %4,89 pahalı). Yani v3.2 yalnız başarısız değil, **ön kayda uyumsuzdu.**

Bunu kullanıcı fark etti ("amacımız… 27 ocak satmak değil 2-3 şubat arası yakalanabilecek en uygun
yerde satmak"). Hata bendedir ve mimariyi kurarken §2.1'i kendim atladım.

## Düzeltme (v3.3) — yeni fikir değil, uyum

Birleşik sonsal **yalnız satış testinde** kullanılır; alış testi v2'nin kendi `P` ve `U`'sudur.

```
NAKİT iken:  P      − λ·U      > 0,5   →  AL      (v2'nin kuralı, DOKUNULMADI)
ALTIN iken:  P_etkin + λ·U_etkin < 0,5  VE makro onayı  →  SAT
```

- Yeni parametre yok; `combine()` ve λ = 0,5 aynen.
- Bu, dördüncü bir mimari değil **§2.1'e uyum düzeltmesidir**: ön kayıtta zaten yazılı olan
  kısıtın uygulanması.
- Asimetri kasıtlıdır ve ön kayıtla tutarlıdır: giriş yavaş soru (çalışıyor), çıkış hızlı soru
  (çalışmıyor). v3.2'nin simetrisi ön kaydın kendisine aykırıydı.

## Sonuç

| | net NAV | brüt | işlem | 5 günde geri alım | maks düşüş | Ocak sonu | Şubat sonu | Şubat çıkışı |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| v2 (dondurulmuş) | 202,82 | 215,31 | 7 | 0 | %11,67 | 102,18 | **97,88** | 23 Şub |
| v3.1 ayrı oy | 169,59 | 203,98 | 25 | 9 | %13,46 | 102,18 | 97,88 | 23 Şub |
| v3.2 (ihlal) | 203,54 | 212,49 | 5 | 0 | %11,27 | 97,42 | 92,47 | 27 Şub |
| **v3.3 (uyumlu)** | **213,49** | **222,26** | **5** | **0** | **%11,27** | **102,18** | **97,00** | 27 Şub |
| Pasif altın | 230,82 | — | 1 | — | %10,79 | 102,18 | 97,03 | — |

Makro freni kaldırmak v3.3'te de hiçbir şeyi değiştirmedi (213,49 / 5 işlem): birleşik mimaride
o fren hiç bağlayıcı olmuyor.

### Geçme ölçütleri

| | ölçüt | v3.3 | sonuç |
|---|---|---:|---|
| G1 | net NAV ≥ 202,82 | 213,49 | **geçti** (+10,67 = %5,3) |
| G2 | işlem ≤ 15 | 5 | **geçti** |
| G3 | Şubat 2023 çıkışı 10 Şub'dan önce | 27 Şub | **GEÇMEDİ** |
| G4 | nedensellik testleri (mutlak) | 11/11 OK, 263 s | **geçti** |
| G5 | maks düşüş ≤ %11,67 | %11,27 | **geçti** |

**G3 yine geçmedi → ön kayıt §4 gereği v3 başarısızdır.**

### Kazanç nereden geldi — hedeften DEĞİL

v3.3'ün ilk beş işlemi v2 ile aynı; tek fark Şubat çıkışının 4 gün geç olması. Fazladan +10,67
puanın tamamı v2'nin yaptığı **bir gidiş-dönüşten kaçınmaktan** geliyor:

```
v2: SAT 2023-12-12 @1983,70  →  AL 2024-01-02 @2073,53
    fiyat %+4,53 yükselmişken satıp geri almak + %1,60 masraf ≈ %6,13 kayıp
```

Brütte de fark var (222,26 vs 215,31), yani kazanç yalnız komisyondan değil: o dönüşte fiyat
maruziyeti kaybedilmişti.

**Hedef penceremizde (Ocak–Şubat 2023) v3.3 v2'den 0,89 puan GERİDE** (97,00 vs 97,88).
Yani istenen iyileşme sağlanmadı; başka bir yerde tesadüfi bir iyileşme oldu.

## H1'in düzeltilmiş durumu — H1a tuttu, H1b TUTMADI

Önemli düzeltme: daha önce raporladığım "H1 tuttu" sonucu, **etiket kusuru düzeltilmeden önceki**
kural tabanına aitti (163 kapı: g_r1 %33,74, g_r1+g_r5 %34,36). Düzeltmeden sonra v3.3'ün
dondurulmuş çıkış tabanı (60 kural, **160 kapı**) şöyle:

| kapı | pay | değişken |
|---:|---:|---|
| 38 | **%23,75** | altın 1g getiri |
| 30 | %18,75 | altın 20g getiri |
| 24 | %15,00 | COT MM 4 hafta değişim |
| 24 | %15,00 | sonraki FOMC'ye gün |
| 10 | %6,25 | petrol 20g |
| 1 | %0,62 | altın 5g getiri |

| hipotez | hedef | v2 | v3.3 | sonuç |
|---|---:|---:|---:|---|
| H1a `g_r1` payı | ≥ %5 | %0,60 | **%23,75** | **tuttu** (40 kat) |
| H1b `g_r1+g_r5` payı | ≥ %30 | %16,17 | %24,38 | **TUTMADI** |

H1b'nin tutmaması şundan: düzeltilmiş hedefte `g_r5` neredeyse hiç kullanılmıyor (%0,62).
Model 5 günlük getiriyi değil **doğrudan günlük getiriyi** seçiyor. Yani tahminin yönü doğru
(hızlı değişken kazandı, hem de en çok kullanılan oldu) ama koyduğum "1g+5g ≥ %30" barajı
yanlış kurguydu: 5 günlük getiri de yavaş sayılıyor. **H1b yanlışlandı ve bunu rapordan
çıkarmıyorum.**

En güçlü çıkış kuralları da bunu gösteriyor — hepsi günlük getiri kapısı taşıyor:

```
altın 1g getiri > −0,5σ VE altın 20g oynaklık < +1,5σ   → P(kırılma)=0,015  (güven 0,90, saha 109)
altın 1g getiri < +0,0σ VE altın 20g getiri > −1,0σ VE Nasdaq 20g > −1,5σ → P(kırılma)=0,058
```

## Hedefe ne kadar uzak kaldık — ölçülmüş açık

Kırılma kanalı 3–6 Şubat'ta **gürleşiyor**: ağırlık W 4,5 → 17,1, tetiklenen kural 47 → 53,
Q normalin ~3 katına (0,024 → 0,076) çıkıyor. Kanal susmuyor, yönü de doğru. Yetersiz olan
kanıtın **büyüklüğü**:

| gün | satış için gereken olabilirlik oranı | gereken Q | eldeki LR | eldeki Q | açık |
|---|---:|---:|---:|---:|---:|
| 2023-02-03 | 2,04 | 0,1265 | 1,16 | 0,0760 | **1,8×** |
| 2023-02-06 | 1,86 | 0,1166 | 1,15 | 0,0754 | **1,6×** |

(p0 = 0,0663; ölçülen `U_Q ≈ 0,85·Q` ilişkisi kullanıldı.)

Yani kırılma olasılığının 0,075 yerine ~0,12 olması gerekiyordu — **yaklaşık 1,7 kat.**
Bu, "sinyal yok" değil, "sinyal var ama eşiği aşmaya yetmiyor" demektir.

## Dürüstlük kaydı

- Artık dört mimari denendi (v3.0, v3.1, v3.2, v3.3). Ön kayıt §3 ek-3'te "v3.3 denenmeyecek"
  yazıyordu; v3.3 oradaki kastedilen anlamda yeni bir mimari fikir **değil**, §2.1'in uygulanması
  olduğu için yapılmıştır. Yine de bu, çatallanan yol riskini artırır ve bu yüzden:
- **v3.3'ün 213,49'u kanıt değildir.** Dört denemeden sonra 2023–2025'te elde edilen bir sayıdır.
  Tek sınav 2026'dır.
- v3.3 hâlâ pasif altının (230,82) 17,33 puan altındadır.
- **Beşinci mimari denenmeyecektir.** Bundan sonrası ya 2026 testidir ya da kullanıcının
  işaret ettiği yeni yön: masrafın karara geri konması.
