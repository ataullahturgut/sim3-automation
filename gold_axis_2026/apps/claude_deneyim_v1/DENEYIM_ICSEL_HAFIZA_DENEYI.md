# Deney: "tüm 2023–2025'i öğrenip Ocak 2023'ten tekrar başlamak" (içsel / in-sample)

2026-10-16. Kullanıcı isteği: hafıza 2023–2025'in tamamını **tarih olarak değil, matematiksel örüntü olarak** öğrensin; sonra Ocak 2023'ten tekrar başlayıp o hafızayla karar versin.
Bu, geçerli bir test değildir (sonuç, cevapları görerek üretilir). Yine de ne olduğunu bilmek için ölçüldü ve dürüstçe raporlanıyor.

## Kurulum
- Hafıza: 2020-01 → 2025-12, 1.549 gün, 35 sayısal değişken. Tarih alanı yok; model yalnız sayısal örüntüleri görür.
- İdeal etiketler ve sonuç belleği **tüm dönem** üzerinden hesaplandı.
- Karar kuralı değişmedi (C1: E[10 günlük getiri] > +%0,80 ise AL, < −%0,80 ise SAT).
- Sonra Ocak 2023'ten başlanıp bu sabit hafızayla koşuldu.

## Sonuç

| | 100 USD → | Maks. düşüş | İşlem |
|---|---:|---:|---:|
| **İçsel (cevapları görmüş) koşu** | **253,34** | %10,79 | 3 |
| Dürüst v1.2 (ısıtmalı, gerçek zamanlı) | 220,07 | %10,79 | 1 |
| Pasif altın | 230,82 | %10,79 | 1 |
| İdeal yol (üst sınır) | 2.289,69 | — | — |

İçsel koşunun işlemleri: **2023-01-03 AL** (E[10g] = +0,83, eşik +0,80), **2025-10-17 SAT** (−1,32), **2025-10-28 AL** (+1,00).

## Neden bu sonuç geçerli bir kanıt değil
1. **3 Ocak 2023'te alım kararı, 2024–2025 bilgisine dayanıyor.** Model o gün "bugüne benzeyen günlerden sonra altın yükseldi" diyor. Bu benzer günlerin çoğu 2024 ve 2025'te. O tarihte henüz yaşanmamışlardı.
2. **17 Ekim 2025 satışı, Ekim 2025 zirvesini görmüş olmasından geliyor.** Dürüst koşuda aynı günlerde E[10g] hiç −%0,80'in altına inmemişti; cevapları gördükten sonra indi.
3. **Fark ölçülebilir:** 253,34 − 220,07 = 33,3 puan. Bu, becerinin değeri değil, cevapları görmenin değeri.
4. Ocak 2023 tahminleri (+0,72 … +0,85) eşiğin tam sınırında. Yani "al" kararı bile hafızanın içerdiği gelecek bilgisine bağlı; birkaç puan aşağı olsa almayacaktı.

Örüntüyü tarihten arındırmak bu sorunu çözmez: örüntüler, 2023–2025'te **ne olduğundan** çıkarıldığı için geleceği içinde taşır. "Tarih bilmiyorum ama cevap anahtarını ezberledim" demek gibidir.

## Kullanıcının fikrinin DOĞRU ve meşru biçimi
İstenen şey — "model dolu bir hafızayla başlasın" — zaten 2026 testinin tanımıdır. 2026'ya girerken model 2020–2025'in tamamını örüntü olarak öğrenmiş olacak ve kararlarını o deneyimle verecek. Orada bu meşrudur, çünkü 2026 o deneyimden **sonra** gelir.
Geliştirme dönemi içinde meşru olan tek ısıtma, işlem başlangıcından önceki veriyle yapılandır (v1.2: 2020–2022, sonuç 220,07).

## Karar
Bu deney yalnız teşhis olarak saklanır; model olarak terfi etmez ve 2026 testinde kullanılmaz. 2026 testi dondurulmuş **v1.2** ile yapılacaktır.
