# TERAZİ v3.2 — Ön kayıt eki 3: iki kanal yerine tek tutarlı sonsal

2026-10-16. Ana ön kayıt `1fcdcaf`, ek-1 `278066b`, ek-2 `aa5ab2c`.
**Bu ek, v3.2 koşulmadan önce commit edilmiştir.** v3.1 sonucu aşağıda olduğu gibi kaydedilmiştir.

## v3.1 sonucu — BAŞARISIZ (4/4 ölçüt)

| | v3.1 | v2 | G |
|---|---:|---:|---|
| net NAV | **181,66** | 202,82 | G1 geçmedi |
| brüt NAV | 212,11 | 215,31 | |
| işlem | **19** | 7 | G2 geçmedi |
| Şubat 2023 çıkışı | yok (23 Şub) | — | G3 geçmedi |
| maks düşüş | **%12,31** | %11,67 | G5 geçmedi |
| hızlı kanal satışı | 6 | — | |

H1 yine tuttu (`g_r1` kapı payı %33,74; `g_r1+g_r5` %34,36) ve kırılma dedektörünün ayırt etme
gücü gerçek: **AUC = 0,710** (29 kırılma günü, 712 diğer gün; Q ortalaması 0,0760'a karşı 0,0555).

## Başarısızlığın ölçülmüş nedeni: iki kanal mantıksal olarak çelişiyor

Hızlı kanalın 6 satışının **6'sında da**, satış gününde yavaş kanalın AL koşulu `P − λU > 0,5`
sağlanıyordu:

| satış günü | hızlı z | yavaş `P − λU` | yavaş kanal AL der mi? |
|---|---:|---:|---|
| 2024-03-22 | 0,513 | 0,598 | evet |
| 2024-04-23 | 0,806 | 0,536 | evet |
| 2024-05-23 | 0,661 | 0,537 | evet |
| 2024-07-25 | 0,611 | 0,618 | evet |
| 2024-11-07 | 0,956 | 0,567 | evet |
| 2024-11-12 | 0,765 | 0,536 | evet |

Sonuç yapısal olarak kaçınılmazdı: model satar, ertesi işlem günü geri alır. Altı gidiş-dönüşte
fiyat farkı −%0,64 … +%1,19 (fiyat hiçbir yere gitmedi), ama her birinde 2×%0,8 komisyon ödendi.
Brüt 212,11 − net 181,66 = **30,4 puan**, tamamı bu boşa dönüşlerin bedeli.

Bu bir eşik sorunu değil **mimari sorundur**: iki kanal paralel ve birbirinden habersiz oy veriyor.

## Mantıksal kusur

İki etiket bağımsız değil. Tanım gereği:

```
brk[i] = 1  ⟹  lab[i] = 0        (kırılma günü her zaman düşme bacağındadır)
```

(Bu, `test_break_only_inside_falling_legs` ile doğrulanmıştır.) Yani kırılma kanıtı, mantıken
**yükselme evresi aleyhine kanıttır**. v3.0/v3.1 mimarisi bunu kullanmıyor; kırılma kanıtını
yalnız satış tarafına bağlayıp alış tarafını ondan habersiz bırakıyor. Bu yüzden model aynı gün
hem "kırıldı, sat" hem "yükselme evresi, al" diyebiliyor.

## Düzeltme: tek sonsal, tek karar kuralı (v3.2)

İki kanal **oy vermeyi bırakır**, kanıt olarak birleşir. Kırılma kanıtı olabilirlik oranına
çevrilir ve yükselme olasılığının bahis oranını böler:

```
odds_yavaş = P / (1 − P)
LR         = [ Q / (1 − Q) ]  /  [ p₀ / (1 − p₀) ]
odds_etkin = odds_yavaş / LR
P_etkin    = odds_etkin / (1 + odds_etkin)
```

Okunuşu: kırılma, koşulsuz oranından LR kat daha olası görünüyorsa, yükselme evresinin bahis
oranı tam o kat kadar bölünür. LR = 1'de hiçbir şey değişmez; LR < 1'de yükselme lehine artar.

Belirsizlik, logit ölçeğinde delta yöntemiyle toplanır (varyanslar toplanır):

```
s_P   = U   / ( P (1−P) )
s_Q   = U_Q / ( Q (1−Q) )
s_etkin = sqrt( s_P² + s_Q² )
U_etkin = s_etkin · P_etkin (1 − P_etkin)
```

Karar artık **tek kuraldır — v2'nin kendi kuralı, değiştirilmeden**:

```
NAKİT iken:  P_etkin − λ·U_etkin > 0,5  →  AL
ALTIN iken:  P_etkin + λ·U_etkin < 0,5  VE  makro onayı  →  SAT      (λ = 0,5)
```

Makro onayı kullanıcının seçtiği frendir ve satış tarafında korunur; makro onaysız varyant
duyarlılık olarak ayrıca raporlanır (seçim için kullanılmaz).

### Neden bu bir ayar değil
- **Yeni parametre yok.** κ = 1 (bağımsız kanıt birleşimi); LR'nin üssü serbest bırakılmaz.
  λ = 0,5 v2'den gelir. p₀ yine yalnız 2020–2022 ısıtmasından (0,0677).
- **Serbestlik derecesi azalır:** ikinci karar kuralı ve `EXIT_LAM` ortadan kalkar; geriye
  v2'nin tek kuralı kalır.
- **Çelişki artık imkânsız:** alış ve satış aynı sayıyı (`P_etkin`) kullanır. Kırılma kanıtı
  yükseldiğinde satış kolaylaşırken alış da aynı anda zorlaşır; ertesi gün geri alım
  yapısal olarak engellenir.
- Mantıksal kısıt `brk ⟹ düşme` zaten testle doğrulanmış bir tanım sonucudur, veriden
  seçilmiş bir ilişki değildir.

### Neden olasılık ölçeğinde basit sınır işe yaramaz
`brk ⟹ düşme` olduğu için `P(yükselme) ≤ 1 − Q` sınırı da geçerlidir. Ama ölçülen en yüksek Q
0,157; yani sınır 0,843 ve `P ≈ 0,6` için asla bağlayıcı olmuyor. Kırılma etiketi tanımı gereği
seyrek (bacak başına m = 5 gün), bu yüzden mutlak düzeyi değil **oransal kaldırmayı** kullanmak
gerekiyor. Olabilirlik oranı tam olarak bunu yapar.

## Dürüstlük kaydı

- Bu düzeltme, v3.1'in ölçülen başarısızlığına bakılarak yapılmıştır. Gerekçesi "daha iyi sonuç"
  değil, yukarıdaki mantıksal çelişkidir; ama keşif yolu saklanmıyor.
- v3.2'nin Şubat 2023'ü yakalayacağının **garantisi yok.** Elle hesapladığım örnekler:
  2024-11-07'de `P_etkin ≈ 0,395` ve satış koşulu kıl payı sağlanıyor; 2023-02-06'da
  `P_etkin ≈ 0,392` ama `U_etkin ≈ 0,248` olduğu için satış koşulu 0,516 ile kıl payı
  **sağlanmıyor**. Yani G3'ün yine geçmemesi kuvvetle muhtemeldir. Bu ek sonucu bilerek değil,
  mantıksal tutarlılığı sağlamak için yazıldı.
- Geçme ölçütleri G1–G5 değişmez. v3.2 de geçmezse v3 bütünüyle başarısız raporlanır, v2
  dondurulmuş haliyle 2026'ya tek başına girer ve bulgu şu olarak kayda geçer:
  *"kırılma anı bu 35 değişkenden, işlem masrafını karşılayacak isabetle kestirilemiyor."*
- **Bundan sonra v3.3 denenmeyecektir.** Üç denemede (v3.0, v3.1, v3.2) ön kayıttaki mimari
  fikir sınanmış sayılır; dördüncü deneme çatallanan yol problemi yaratır.
