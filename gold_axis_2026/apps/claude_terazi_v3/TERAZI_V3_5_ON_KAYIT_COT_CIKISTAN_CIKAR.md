# TERAZİ v3.5: COT kırılma kanalından çıkarılır | Ön kayıt eki 6

2026-10-17. **Kod ve sonuçlardan ÖNCE commit edilmiştir.**

## Teşhis (v3.4, ölçüldü)
v3.4'ün 2023'teki yanlış satışları (6 Ocak, 10 Şubat) COT kurallarıyla tetiklendi
("COT MM 4 hafta değişim > +1,5σ", μ 0,195). 6 Ocak'ta altın yalnız −0,86σ düşmüştü.
2024'teki 5 yanlış satış "altın 1g getiri < −1σ" kurallarından geldi.

## Tek değişiklik
Kırılma (çıkış) kanalında `cot_mm` ve `cot_mm_d4` kural adayı olamaz. Gerekçe (kullanıcıyla
birlikte, sonuca bakmadan önce): COT haftalık, en az 7 gün gecikmeli ve Şubat 2023'te
haftalarca yayımlanmadı; günlük kırılma anını zamanlayamaz. Giriş kanalı COT'u kullanmaya
devam eder. v3.4'ün güven ölçüsü (beceri) korunur. Başka değişiklik yok, yeni parametre yok.

## Ölçütler
v3.4 ön kaydındaki S1–S4 aynen; ek olarak **S0: 3 Ocak – 2 Şubat 2023 arasında satış yok.**
2024'teki tek günlük düşüş kaynaklı satışlar bu değişiklikle ele alınmaz; raporlanır.
Geliştirme kaydıdır, kanıt değildir.
