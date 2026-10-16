# TERAZİ v5.2 — Ön kayıt eki 2: koşulu sağlanan kurallar oy verir + istikrar testi

2026-10-16. Ek-1 `257b6d8`, v5.1 sonucu `fe2c4ef`. **Bu ek v5.2 koşulmadan önce commit edilmiştir.**

## Teşhis (v5.1 üzerinde, karar anında)
1. **Oy seyrelmesi:** toplam oyun ~%30'u, kapı çarpımı w < 0,5 olan (koşulu yarıdan az sağlanan)
   kurallardan geliyor.
2. **Rejim tersine dönmesi:** bazı değişkenlerin hedefle ilişkisi yıldan yıla işaret değiştiriyor
   (ör. GVZ düzeyi yıl içi AUC 2023 0,81 → 2025 0,08); geçmiş yıldan öğrenilen ilişki yeni yılda
   ters uygulanıyor. Bu ölçüm 2023–2025'e bakıyor, bu yüzden **elle değişken seçilmez**;
   düzeltme yalnız geçmiş veriyle çalışan bir doğum testidir.
3. (Reddedildi) Tekrar eden kurallar: 57 kural / 35 aile; "aile başına bir oy" ayırt etmeyi
   değiştirmedi. Düzeltme yapılmaz.

## Değişiklikler
**D1 — Güçlü oy:** `decide` yalnız w ≥ 0,5 olan kuralları kullanır (P ve U bunlar üzerinden).
W < W_min ise görüş yok. 0,5, yumuşak kapının "koşul doğru" sınırıdır.

**D2 — İstikrar testi (kural doğumu):** kabul eşiğini geçen her aday için, öğrenilmiş günler
takvim yılına bölünür; destek ≥ MIN_SUPPORT (20) olan her yılda ağırlıklı ortalama artık,
toplam artıkla **aynı işaretli** olmalıdır ve böyle en az **2 yıl** bulunmalıdır. Aksi halde aday
doğmaz. Yalnız öğrenme anına kadarki veri kullanılır.

## Varyantlar (önceden beyan)
- A: D1 · B: D2 · **C: D1 + D2 (birincil)**. Hepsi v5.1 üzerine (yeniden etiketleme, aylık, K=2).
- Birincil C, sonuçlardan önce seçilmiştir. A ve B yalnız etkileri ayırmak için raporlanır;
  hangisi daha iyi çıkarsa çıksın 2026'ya C girer.
- Geçme ölçütleri G1–G6 değişmez. Nedensellik testleri C üzerinde koşulur.
