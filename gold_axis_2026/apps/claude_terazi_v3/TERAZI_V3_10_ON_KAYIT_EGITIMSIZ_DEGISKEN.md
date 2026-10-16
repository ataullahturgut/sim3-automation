# TERAZİ v3.10: eğitimde verisi olmayan değişkenler çıkarılır | Ön kayıt eki 11

2026-10-17. **Kod ve koşudan ÖNCE commit edilmiştir.**

## Bulgu (ölçüldü, `deneyim_states.build_states` ham değerleri)
35 değişkenin 16'sı 2020–2022 ısıtma/eğitim döneminde **%100 eksik**; `Standardizer.z` eksik
değeri 0 (= ortalama) yapıyor. Kurallar bu değişkenleri 3 yıl boyunca sabit 0 olarak görüp
öğreniyor; 2023'te veri başlayınca (ilk aylarda kısmen) aynı kurallar hiç eğitilmedikleri
değerlerle tetikleniyor. Bu bir dağılım kaymasıdır ve 2023–2025'teki karar davranışını,
eğitimde hiç sınanmamış bir şekilde değiştirir.

Eksik olanlar: y2_d5, y2_d20, cpi_surp, cpi_days, nfp_surp, nfp_days, fomc_since, last_react,
nq_r5, nq_r20, zn_r5, cl_r5, cl_r20, si_r5, si_r20, gs_ratio_d20; bunlardan türeyen ikili
izler sig_equity_shock, sig_flight, sig_oil_shock.

## Kural (sonuca bakmadan, tarih seçimi yok)
Ham değeri 2020–2022 günlerinin **%50'sinden fazlasında eksik** olan değişken ve ondan türeyen
ikili izler, tüm dönem boyunca sabit 0 tutulur (kural ayırt edici bilgi alamaz). Yukarıdaki
19 değişken bu kurala göre çıkar; kalan 16 değişken + fomc_to + sig_vol_jump kullanılır.
Makro onay kapısı (rr_d5 VEYA y2_d5 > 0) değişmez — öğrenilen bir parça değildir.

## Koşu
v3.5 öğrenme yapılandırması (beceri güveni, COT kırılma kanalından hariç) + bu maske;
karar katmanı **v3.7 aynen** (k = 2 yapı + sonsal + makro). Ek bir ayar yapılmaz.

## Ölçütler
v3.7 ölçütleri (S0–S4) ve kullanıcının 2023 yolu (satış 3–10 Şub ve 8–31 May; alışlar Mart
ve Ekim) raporlanır; ayrıca yıllık getiri 2023/2024/2025 ve v3.7 ile karşılaştırma.
Geliştirme kaydıdır, kanıt değildir.
