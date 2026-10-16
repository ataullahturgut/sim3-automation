# TERAZİ v4 — Kullanıcı seçimli hedef | Ön kayıt

2026-10-16. Dal: `research-gold-claude-pusula-v1-20261016`.
**Bu dosya v4 kodundan ve sonuçlarından ÖNCE commit edilmiştir.**
Isıtma 2020-01→2022-12, geliştirme koşusu 2023-01-03→2025-12-31. **2026 verisi yüklenmez.**

## 0. Neden v4 — v1/v2/v3'ten ders

| sürüm | hedef | neden tıkandı |
|---|---|---|
| v1 | 10 günde beklenen getiri | sabit ufuk gerçek davranışla çelişti; masraf tek ufka yüklendi |
| v2 | zigzag %5 evre etiketi | evre dönüşü %5 geriden onaylanıyor; çıkış hep geç |
| v3 | tepe kırılma anı (ilk m gün) | taban oran %6,6 → oransal belirsizlik patlaması; üç bağlama biçimi de başarısız |
| **v4** | **kullanıcının seçtiği hareketler** | — |

v3 raporunun kalıcı bulgusu: *"üç patolojinin üçünde de eksik olan şey, kararın masrafı
hesaba katamamasıydı."* v4 bunu hedefin **içine** koyuyor.

## 1. Hedef — kullanıcının kendi seçimi, kural olarak

Kullanıcı interaktif defterde (artifact `QekwUgDpRkKW8LfPkbGKre`) 39 ideal hareketten **24'ünü**
seçti ve 15'ini çıkardı. Seçim keskin bir eşik gösteriyor:

- tuttuklarının en küçüğü **net +%2,51**
- çıkardıklarının en büyüğü **net +%2,32**

Bu yüzden seçim bir tarih listesi değil, **bir kural** olarak tanımlanır:

> **Hedef:** maliyetli ideal yolun (DP, %0,8/yön) **net getirisi ≥ %2,4** olan bacaklarında
> ALTINDA ol; diğer her gün NAKİTTE ol.

Doğrulama: `net ≥ %2,4` eşiği 2023–2025'te **tam olarak kullanıcının 24 seçimini** üretir
(birebir eşitlik kodla doğrulanmıştır). Eşik taranmamıştır; kullanıcının kendi kararından
(2,51 ile 2,32 arasındaki boşluktan) okunmuştur.

Tanımın dönemden bağımsız olması zorunlu, yoksa model 2026'da ne arayacağını bilemez:
- 2020–2022 ısıtma: 42 bacağın 19'u eşiği geçiyor, taban oran **%37,7**, yılda ~6,3 gidiş-dönüş
- 2023–2025: 24 bacak, taban oran **%50,8**, yılda 8 gidiş-dönüş

**Taban oranın ~%40–50 olması v4'ün can alıcı avantajı:** 0,5 artık doğal karar sınırıdır.
v3'ü batıran nadir-olay patolojileri (ulaşılamaz eşik, `U_Q ≈ 0,85·Q`, oransal belirsizlik
baskınlığı) burada yapısal olarak oluşamaz.

### 1.1 Etiket olgunlaşması (nedensellik) — v4'ün en hassas noktası
İdeal yol geleceğe bakar. Bu yüzden **yuvarlanan ideal** kullanılır:

- Her ay sonunda, **yalnız o ay sonuna kadarki fiyatlarla** DP yeniden koşulur.
- O koşuda **kapanmış** (çıkışı gerçekleşmiş) ve net ≥ %2,4 olan bacakların günleri
  etiketlenir ve öğrenmeye girer.
- Hâlâ açık olan son bacağın günleri **etiketsizdir** ve öğrenilmez.
- Bir gün bir kez öğrenildikten sonra, sonraki ayların DP'si o günü farklı etiketlese bile
  **yeniden etiketlenmez** (ilk olgunlaşma kesindir); bu kural testle doğrulanır.

Bu, v2'nin zigzag onay mantığının birebir karşılığıdır ve testlerle sınanır:
ay sonunda seri kesilse etiket aynı kalmalıdır.

## 2. Mimari — çalışan makine korunur

Kural makinesi v2'den **değiştirilmeden** alınır (v3'te bunu bozmanın bedelini gördük):

- 35 tarihsiz, karar anında bilinen durum değişkeni (`deneyim_states.py`), **yeni özellik eklenmez**.
- Yumuşak yönlü kapılar `σ(d(z−c)/s)`, s = 0,5; eşik ızgarası ±1,5σ; kural = 1–3 kapının yumuşak VE'si.
- Aylık kural doğumu: adaylar artıklardan taranır, dereceli doğum güveni
  c₀ = kırp(tanh((z−pen)/τ), −0,4; +0,9), etkin bağımsız deneme sayısıyla ceza.
- Sahada sınanmış güven: `güven = (2h − k + 10·c₀)/(k + 10)`, oy ağırlığı = max(0, güven).
  Saha testinin referansı **0,5**'tir (taban oran ~%40–50 olduğu için v3'teki p₀ uyarlaması gereksiz).
- Aylık ölüm: saha ≥ 15 ve güveni negatif olanlar, desteği düşenler, yinelenenler silinir. Taban sınırı 60.
- Sonuç: her kural kendi bölgesinde **μ_R = P(altında ol | kural tetiklendi)** tutar,
  çevrimiçi indirimli (ρ = 0,995), öncül 0,5 ve 2 sözde gözlem.

## 3. Karar — v2'nin kuralı, tek sayı, tek eşik

```
W = Σ a_R · w_R(z);      W < 0,5  →  görüş yok, pozisyon korunur
P = Σ a_R·w_R·μ_R / W                      (altında olma olasılığı)
U = sqrt( Σ a_R·w_R·(μ_R(1−μ_R)/n_R + (μ_R − P)²) / W )

NAKİT iken:  P − λ·U > 0,5  →  AL        (λ = 0,5)
ALTIN iken:  P + λ·U < 0,5  →  SAT
aksi halde pozisyon korunur
```

- Alış ve satış **aynı sayıyı** kullanır; v3.1'in iki kanal çelişkisi imkânsızdır.
- Giriş ve çıkış **simetriktir** ve bu v4'te doğrudur: hedefin kendisi iki tarafı da içeriyor.
  (v3.2'de simetri hataydı, çünkü orada hedef yalnız çıkışı tanımlıyordu.)
- `2λU` genişliğindeki tutma bandı korunur: savrulmayı önleyen şey bu, ve hedef artık
  zaten %2,4 altındaki hareketleri içermiyor.
- **Masraf karara girmez** ama **hedefin tanımına girmiştir** (DP %0,8/yön ile koşuluyor ve
  eşik net getiridir). NAV muhasebesinde %0,8/yön tam uygulanır; net ve brüt NAV ayrı raporlanır.

## 4. Geçme ölçütleri — sonuçlara bakmadan sabitlenir

| | ölçüt | gerekçe |
|---|---|---|
| **G1** | net NAV ≥ **230,82** | pasif altın. v2/v3'ün 202,82'si değil; gerçek baraj bu. |
| **G2** | işlem sayısı 20–60 arası | hedef 48. Altı "yakalamıyor", üstü "zırt pırt". |
| **G3** | pozisyonun hedef etiketiyle uyuşması ≥ **%65** gün | yön tutuyor mu |
| **G4** | nedensellik testlerinin tamamı geçer | **mutlak.** Geçmezse v4 reddedilir. |
| **G5** | ilk bacağın çıkışı **2023-02-02'den önce** | hedef 2023-01-26; bütün çalışmanın çıkış noktası |
| **G6** | maksimum düşüş ≤ %11,67 | v2'nin düşüşünden kötü olmasın |

G1, G2, G3, G5 veya G6 sağlanmazsa v4 **başarısız** raporlanır.

## 5. Dürüstlük — bu sürümün özel riski

- **Eşik (%2,4) kullanıcının 2023–2025 sonuçlarına bakarak yaptığı seçimden türetildi.**
  Dolayısıyla 2023–2025, hedef tanımı bakımından **örneklem içidir**. Bu dönemde elde edilecek
  her sayı geliştirme kaydıdır, kanıt değildir. Rapor bunu her yerde belirtir.
- Tek gerçek sınav **2026**'dır: eşik, mimari ve kod dondurulmuş hâlde, 2026 verisi
  hiç görülmeden koşulur.
- Eşik 2023–2025 NAV'ını iyileştirmek için **değiştirilmeyecektir.** Duyarlılık
  (%2,0 / %2,4 / %3,0) raporlanır, seçim için kullanılmaz.
- Yeni özellik eklenmez; `deneyim_states.py` ve panel değiştirilmez.
- v1, v1.1, v2, v3.3 ve v4 sonuçları her zaman yan yana raporlanır.
- **Beşinci mimari fikir denenmeyecektir.** v4 de G1–G3/G5/G6'yı geçmezse bulgu şudur:
  *"kullanıcının seçtiği hareketler bu 35 değişkenden gerçek zamanlı kestirilemiyor."*

## 6. Raporlama

Aylık: hedef etiketi, P ve U, tetiklenen kurallar, kararlar, doğan/ölen kurallar, hedefle uyum.
Sonunda: kural tabanı insan okunur biçimde, G1–G6 tablosu, Ocak–Şubat 2023 dökümü,
eşik duyarlılığı, v1/v1.1/v2/v3.3/v4 ve pasif altın / ideal yol / kullanıcı seçimi (498,43)
karşılaştırması, net ve brüt NAV.
