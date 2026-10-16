# DENEYİM v1.2 — Hafıza ısıtması | Ön kayıt eki

2026-10-16. Bu ek, v1.2 kodu ve sonuçlarından ÖNCE commit edilmiştir. Geliştirme dönemi; 2026 verisi yüklenmez.

## Düzeltilen kurulum hatası
v1/v1.1 maratonu 2023-01-03'te **boş hafızayla** başlıyordu. Ocak 2023 günlük dökümü, modelin o ay hiçbir tahmin üretemediğini gösterdi (benzer durum tahmini için geçmiş örnek yok). Ocak 2023'teki %0 getiri bir yanlış karar değil, modelin henüz hiçbir şey öğrenmemiş olmasının sonucudur. Aynı körlük 2023'ün ilk aylarını da etkiliyor.

PUSULA v1 protokolünde 2020–2022 zaten "yalnız öğrenme, işlem yok" dönemi olarak tanımlıydı; DENEYİM maratonunda bu ısıtma sehven uygulanmamıştı.

## v1.2'de değişen TEK şey
Deneyim hafızası ve sonuç belleği **2020-01-02'den** itibaren oluşturulur. İşlem yine 2023-01-03'te 100 USD nakitle başlar. Ocak 2023'e girerken model, yalnız 2022-12-30'a kadarki veriyle öğrenilmiş parametrelere sahiptir.

## Değişmeyenler
- Karar kuralı C1 (ön kayıtlı, seçilmiş): NAKİT iken E[r_H] > c_rt/2 ise AL; ALTIN iken E[r_H] < −c_rt/2 ise SAT. Eşikler yine maliyetten türetilir, ayarlanmaz.
- 35 durum değişkeni, ayırt edici metrik, bant genişliği, düzenleme katsayısı, H = 10, aylık öğrenme döngüsü.
- İdeal etiketler aynı dinamik programlamayla, yalnız o ay sonuna kadarki veriyle hesaplanır (ısıtma dönemi dahil, 2020-01-02'den itibaren).
- Nedensellik: ısıtma yalnız geçmiş veriyi kullanır; hiçbir 2023+ bilgisi ısıtmaya sızmaz. Aylık kararlar yalnız önceki ay sonu parametreleriyle verilir. Mevcut testler (kesme eşitliği, gelecek bozma) ısıtmalı sürümde de geçmelidir.

## Raporlama
v1.1 (ısıtmasız) ve v1.2 (ısıtmalı) sonuçları yan yana verilir. Hangisi daha iyi olursa olsun ikisi de raporlanır; v1.2 yalnız kurulum hatası düzeltildiği için tercih edilir, performansına göre seçilmez.
