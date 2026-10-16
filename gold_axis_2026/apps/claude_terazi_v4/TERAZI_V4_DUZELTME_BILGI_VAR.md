# TERAZİ v4 — Düzeltme: "bilgi yok" sonucu yanlıştı

2026-10-16. `TERAZI_V4_SONUC_RAPORU.md` §6 "eksik olan bilginin kendisi" diyordu. Bu iddia
kanıtlanmadan yazıldı ve aşağıdaki ölçümle **yanlışlandı**. Rapordaki NAV ve ölçüt sonuçları
geçerlidir; yalnız başarısızlığın **nedeni** düzeltilir.

## Ölçüm: ham değişkenler yıl içinde hedefi ayırt ediyor

Karar anında bilinen, nedensel standartlaştırılmış tek bir değişken, hiçbir öğrenme olmadan
(yıl içi AUC, hedef = net ≥ %2,4 bacakları):

| değişken | 2023 | 2024 | 2025 |
|---|---:|---:|---:|
| altın 5g getiri | **0,799** | **0,679** | **0,637** |
| altın 1g getiri | 0,683 | 0,626 | 0,677 |
| 60g zirveye uzaklık | 0,672 | 0,647 | 0,633 |
| **model P (karar anı)** | **0,501** | **0,611** | **0,455** |

(Değişkenler 35 içinden en iyi 10 olarak seçildi — seçim örneklem içi. Ama 5g getiri üç yılın
üçünde de ilk sıralarda, yani tesadüf değil.)

**Tek bir ham değişken bütün kural tabanını yeniyor. Bilgi var; algoritma onu kaybediyor.**

## Algoritmik nedenler

1. **Güven testi referansı hatası (kodlama hatası, benim).** Ek-1'de karar referansını taban
   orana taşıdım ama kuralların saha güveni hâlâ `(μ ≥ 0,5) == (y ≥ 0,5)` ile ölçülüyor.
   Taban oran 0,40 iken "hep nakit" diyen bir kural günlerin ~%60'ında bedava doğru sayılır:
   100 gün sonra güveni ≈ +0,18, yani oy hakkı kazanır. Son tabanda 60 kuralın **46'sı** μ < 0,5
   diyor, ortalama güvenleri +0,31. Bu kurallar P'yi günden bağımsız olarak "nakit"e çekiyor.
   v3 ek-1'de aynı hatayı tespit edip düzeltmiştim; v4'te tekrarladım.

2. **Öğrenme gecikmesi.** Son kural tabanı geriye dönük uygulanınca P yıl içinde iyi ayırıyor
   (0,806 / 0,698 / 0,665) — ama karar anındaki taban ayıramıyordu. *Bu sayılar geriye bakış
   içerir, kanıt değildir;* yalnız şunu gösterir: kurallar doğruyu öğreniyor ama geç. Olası
   nedenler: etiket ancak bacak kapanınca olgunlaşıyor, öğrenme aylık, ayda en fazla 3 kural
   doğuyor, ısıtmadan (2020–2022, farklı rejim) gelen kurallar 2023 başında baskın.

3. Ortalama alma (v3'te ölçülen seyrelme) v4'te ana neden **değil**: son tabanda ortalama P
   (0,806) en güçlü tek karakterden (0,750) daha iyi ayırıyor.

## Sonuç

v4'ün başarısızlığı "veri eksik" değil, **algoritmik**: bir kodlama hatası ve öğrenme
gecikmesi. Rapordaki "yeni veri bul" önerisi bu ölçümle zayıflıyor; önce bu iki neden
düzeltilip sınanmalı.
