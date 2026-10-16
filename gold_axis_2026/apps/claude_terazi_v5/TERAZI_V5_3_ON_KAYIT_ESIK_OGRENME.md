# TERAZİ v5.3 — Öğrenen karar eşikleri (yürüyen pencere) | Ön kayıt eki 3

2026-10-16. Kullanıcı önerisi: "satış eşiklerini öğrenen bir yapı, yıla / 3 aya / 6 aya göre revize".
**Bu ek koşudan önce commit edilmiştir.**

## Sinyal
v5.1'in z serisi (`(P − p₀)/U`), değiştirilmeden. Model öğrenmesi pozisyondan bağımsız olduğu için
z serisi kesindir; kayıt 2021-01-04'ten başlatılır (öğrenme aynı, yalnız kayıt erken başlar).

## Karar
Nakitteyken z > θ_al → AL; altındayken z < θ_sat → SAT; θ_sat < θ_al.
Izgara: θ_al ∈ {−0,5, −0,25, 0, 0,25, 0,5, 0,75, 1,0}; θ_sat ∈ {−∞ (hiç satma), −1,5, −1,0, −0,75,
−0,5, −0,25, 0, 0,25}.

## Öğrenme (yürüyen pencere, nedensel)
- Her R ayda bir (dönem başında), **son 12 ayın** z serisi ve fiyatlarıyla her (θ_al, θ_sat) çifti için
  o pencerede %0,8/yön komisyonla net getiri simüle edilir (pencere başında nakitten başlanır).
- En yüksek net getiriyi veren çift seçilir; eşitlikte daha az işlem yapan.
- Seçilen eşikler yalnız **sonraki R ay** için kullanılır; pozisyon dönem sınırında korunur.
- Hiçbir seçimde dönem başından sonraki veri kullanılmaz.

## Varyantlar
R = 3, 6, 12 ay. **Birincil: R = 6.** Üçü de raporlanır.

## Ölçütler (2023-01-03 → 2025-12-31)
G1 net NAV ≥ 230,82 (al-tut) · G2 işlem 10–60 · G6 maks düşüş ≤ %11,67. Kıyas: v5.1 sabit eşik 189,94.
Geliştirme kaydı; tek sınav 2026.
