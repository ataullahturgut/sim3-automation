# TERAZİ v4 — Sonuç: hedef kullanıcının seçimi, model onu kestiremiyor

2026-10-16. Sıra: ön kayıt `f3811ff` → kod → v4.0 koşusu → ek-1 (referans düzeltmesi) →
v4.1 koşusu → nedensellik testleri → bu rapor.
Isıtma 2020-01→2022-12, koşu 2023-01-03→2025-12-31. **2026 verisi yüklenmedi** (testle doğrulandı).

> **2023–2025 sayıları kanıt değildir.** Hedefin eşiği (%2,4) kullanıcının bu döneme bakarak
> yaptığı seçimden türetildi, yani dönem hedef tanımı bakımından örneklem içidir.

## 1. Hedef doğru kuruldu

Kullanıcı interaktif defterde 39 ideal hareketten 24'ünü seçti. Seçim keskin bir eşikteydi
(tuttuğu en küçük net +%2,51; çıkardığı en büyük +%2,32), bu yüzden tarih listesi değil
**kural** olarak tanımlandı: *ideal yolun net ≥ %2,4 olan bacaklarında altında ol.*

Doğrulandı (test `test_threshold_reproduces_user_selection`): eşik 2023–2025'te **tam olarak
kullanıcının 24 seçimini** üretiyor. Hedefin NAV'ı 498,43.

Dönemden bağımsız: ısıtmada (2020–2022) 19 bacak, taban oran %37,9; 2023–2025'te 24 bacak, %50,8.

## 2. Sonuç — BAŞARISIZ

| | v4.0 (ön kayıttaki hâli) | **v4.1 (ek-1 düzeltmeli)** | ölçüt |
|---|---:|---:|---|
| net NAV | 83,26 | **129,08** | G1 ≥ 230,82 → **geçmedi** |
| brüt NAV | — | 163,07 | |
| işlem | 28 | 29 | G2 20–60 → geçti |
| hedefle uyum | %53,6 | **%49,4** | G3 ≥ %65 → **geçmedi** |
| ilk çıkış | 2024-11-04 | 2023-02-17 | G5 < 2023-02-02 → **geçmedi** |
| maks düşüş | %22,79 | %18,87 | G6 ≤ %11,67 → **geçmedi** |
| nedensellik testleri | — | **11/11 OK (201 s)** | G4 (mutlak) → **geçti** |
| pozisyonda geçen gün | %15,0 | %79,2 | hedef %50,8 |
| karar referansı p₀ | 0,5 (hatalı) | 0,4023 (veriden) | |

Kıyaslar: hedef 498,43 · pasif altın 230,82 · v3.3 213,49 · v2 202,82 · v4.1 **129,08**.

**v4 başarısızdır** (G1, G3, G5, G6).

## 3. Yol boyunca bulunan iki hata

### 3.1 Karar referansı (ek-1, kodda düzeltildi)
Ana ön kayıt §1'de "taban oran ~%40–50 olduğu için 0,5 doğal karar sınırıdır" yazmıştım.
Ölçüm bunu yanlışladı: karar anında geçerli taban oran **%37,9–40,0**. v2'nin kuralı
cebirsel olarak `(P − 0,5)/U > λ` bir z-testidir; ortalama P ≈ 0,38 iken alım için
P > 0,55 gerekiyordu ve model **22 ay hiç almadı** (ilk işlem 2024-10-22, NAV 83,26).

Düzeltme: referans öğrenilmiş etiketlerin taban oranına taşındı, `(P − p₀)/U > λ`.
Yeni parametre eklenmedi; p₀ veriden okunuyor ve yalnız öğrenilmiş etiketlerden
hesaplanıyor (test `test_base_rate_uses_learned_labels_only`). Bu, v3 ek-2'de (`aa5ab2c`)
zaten türetilmiş ilkenin uygulanmasıdır — v4.0'da kendi ön kaydımda atladım.

### 3.2 Hatalı test (testte düzeltildi, kodda değil)
`test_label_learned_once_never_changes` yanlış şeyi iddia ediyordu. Yuvarlanan ideal
**ufka duyarlıdır**: aynı gün, ufuk uzadıkça farklı etiketlenebilir. Ölçüldü:

| | |
|---|---:|
| ortak gün | 1.546 |
| ilk olgunlaşma ≠ nihai etiket | **74 gün (%4,8)**, hepsi 0→1 |
| ilk etiketlerin taban oranı | %40,2 |
| nihai etiketlerin taban oranı | %45,0 |

Ön kayıt §1.1 ilk olgunlaşmayı kesin sayıyor (geriye dönük düzeltme yok) ve kod bunu
uyguluyor; test ters yönü iddia ettiği için düzeltildi.

**Önemli:** bu kararsızlık başarısızlığın açıklaması DEĞİL. Tavan hesabı: nihai hedefi
kusursuz öğrenmiş bir model, gerçek zamanda yalnız ilk etiketleri görebildiği için en fazla
**%95,2** uyum sağlayabilirdi. Model %49,4 sağlıyor.

## 4. Başarısızlığın gerçek nedeni — ölçülmüş

Modelin hedefi ayırt etme gücü (karar anındaki P ile, 2023–2025):

| | |
|---|---:|
| hedef = ALTINDA günler, ortalama P | 0,4298 |
| hedef = NAKİT günler, ortalama P | 0,3951 |
| **toplam AUC** | **0,618** |

Ama yıl bazında kırılım toplamın aldatıcı olduğunu gösteriyor:

| yıl | AUC | altında / nakit gün |
|---|---:|---|
| 2023 | **0,501** | 94 / 163 |
| 2024 | 0,611 | 122 / 137 |
| 2025 | **0,455** | 177 / 81 |

0,618'lik toplam, yıllar arası seviye kaymasından (P zamanla yukarı sürükleniyor, hedefin
taban oranı da yükseliyor) geliyor; **yıl içinde ayırt etme gücü yazı-tura.** 2025'te
yazı-turanın altında.

Eşik duyarlılığı (önceden beyan edildi, seçim için kullanılmadı) bunun tek bir eşik sorunu
olmadığını gösteriyor:

| eşik | hedef bacak | hedef NAV | model net | işlem | uyum | düşüş |
|---|---:|---:|---:|---:|---:|---:|
| net ≥ %2,0 | 26 | 521 | 116,85 | 38 | %49,9 | %24,88 |
| **net ≥ %2,4** | **24** | **498** | **129,08** | **29** | **%49,4** | **%18,87** |
| net ≥ %3,0 | 20 | 448 | 129,11 | 23 | %44,4 | %16,72 |
| net ≥ %5,0 | 15 | 370 | 148,17 | 15 | %42,8 | %18,28 |

Hiçbir eşikte uyum yazı-turayı geçmiyor; hepsinde NAV pasif altının (230,82) çok altında.
Eşik yükseldikçe NAV artıyor ama bu isabetten değil, daha az işlemden geliyor.

## 5. Üç sürümün birlikte söylediği şey

| sürüm | hedef | hedefi ayırt etme | sonuç |
|---|---|---:|---|
| v2 | zigzag %5 evre | pozisyon-evre uyumu %70 | NAV 202,82 |
| v3.3 | tepe kırılma anı (ilk 5 gün) | AUC **0,710** | NAV 213,49 |
| **v4.1** | **net ≥ %2,4 bacakları** | **yıl içi AUC ~0,52** | **NAV 129,08** |

Örüntü net: **soru "rejim" sorusuna yaklaştıkça model bir şeyler görüyor (AUC 0,65–0,71),
"bu hareket masrafı karşılayacak mı" sorusuna yaklaştıkça görmüyor (AUC ~0,52).**

Hedef ne kadar ekonomik olarak değerliyse o kadar az kestirilebilir çıkıyor. Bu, daha önce
ölçülmüş bulguyla da uyumlu: tepe zamanlaması sinyali bu özellik kümesinde büyük ölçüde yok
(geriye dönük en iyi eşikler 199–218, tam geçmiş-bilgili lojistik 206; hepsi dürüst gerçek
zamanlı 213,5'in altında).

## 6. Kalıcı bulgu

> **Kullanıcının seçtiği 24 hareket, elimizdeki 35 tarihsiz değişkenden gerçek zamanlı
> kestirilemiyor.** Hedefin kendisi iyi tanımlı (tavan %95,2), kural makinesi çalışıyor
> (195 kural doğdu, görüşsüz gün 0), nedensellik sağlam — eksik olan **bilginin kendisi.**

Bu, ön kayıt §5'te yazılan sonuçtur ve **beşinci mimari fikir denenmeyecektir.**

Ne denendi ve tükendi:
- v1: 10 günlük beklenen getiri → sabit ufuk / masraf çelişkisi
- v2: zigzag evre etiketi → çıkış %5 geriden onaylanıyor
- v3.0/3.1/3.2/3.3: tepe kırılma anı → ulaşılamaz eşik / kanal çelişkisi / belirsizlik baskınlığı
- v4.0/4.1: kullanıcı seçimli hedef → sinyal yok

## 7. Buradan sonra ne yapılabilir (öneri, taahhüt değil)

1. **Dondurulmuş v2'yi ve v3.3'ü 2026'da test et.** Elimizdeki tek temiz kanıt bu olur.
   v4 başarısız olduğu için 2026'ya girmemesi önerilir.
2. **Özellik kümesini genişlet.** Bulgu "model kötü" değil, "bilgi yok". Eksik olabilecekler:
   gün içi veri (bu araştırma günlük 06:00Z tek nokta kullanıyor), opsiyon zımni oynaklık
   yüzeyi, ETF akımları, merkez bankası alımları, reel zamanlı haber akışı.
   Bu, yeni bir veri toplama araştırmasıdır, yeni bir model mimarisi değil.
3. **Hedefi kolaylaştır.** AUC 0,710 ile en kestirilebilir hedef v3'ün kırılma anıydı.
   Masrafı karara koyarak (v3 raporunun işaret ettiği adım) o sinyalden faydalanmak,
   kestirilemeyen bir hedefi zorlamaktan daha umutlu görünüyor.

## 8. Dosyalar

`TERAZI_V4_DONDURULMUS_MODEL.json` (v4.1), `TERAZI_V4_0_ONKAYIT_HALI_SONUC.json`,
`TERAZI_V4_DUYARLILIK.json`, `TERAZI_V4_GUNLUK.json`, `reports/` (aylık kayıtlar),
`test_terazi_v4.py` (11 nedensellik testi).
