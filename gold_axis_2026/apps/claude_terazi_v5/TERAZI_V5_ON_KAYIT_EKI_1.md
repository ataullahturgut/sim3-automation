# TERAZİ v5.1 — Ön kayıt eki 1: geçmiş günler güncel hedefle yeniden etiketlenir

2026-10-16. Ana ön kayıt `14c7e3b`, v5 sonucu `3f36a24`. **Bu ek v5.1 koşulmadan önce commit edilmiştir.**

## Neden
v5'te etiket ilk olgunlaştığı değerle kesinleşiyordu. v5 hedefi uzun hareketleri sonradan
birleştirdiği için 2023–2025'te günlerin %35,9'u ilk olgunlaşmada 0, sonunda 1 çıktı (hepsi 0→1);
model %35 taban oranlı yanlış bir hedefle eğitildi (nihai %70,9).

## Değişiklik
Her öğrenme anında (ay sonu):
1. Hedef, yalnız o ana kadarki fiyatlarla yeniden hesaplanır (değişmedi).
2. **Bütün** etiketli geçmiş günler bu güncel hedefin etiketini alır (ilk olgunlaşma kesin sayılmaz).
3. Mevcut her kuralın sonucu (μ: indirimli toplam s, sayı n) ve saha güveni (h, k) bu güncel
   etiketlerle, kronolojik sırayla, aynı güncelleme formülüyle **baştan yeniden hesaplanır**.
   Saha güveninin referansı bu yeniden hesapta o anki taban orandır (sabit).
4. Kural doğumu/ölümü ve karar kuralı değişmez.

Nedensellik korunur: hiçbir adımda öğrenme anından sonraki fiyat kullanılmaz. Testlerle doğrulanır
(gelecek fiyat bozma, kesme eşitliği, tekrar üretilebilirlik, 2026 yasağı).

Yeni parametre yok. Birincil: aylık, K=2. Varyant: haftalık. Geçme ölçütleri G1–G6 değişmez.
2023–2025 sayıları geliştirme kaydıdır; tek sınav 2026.
