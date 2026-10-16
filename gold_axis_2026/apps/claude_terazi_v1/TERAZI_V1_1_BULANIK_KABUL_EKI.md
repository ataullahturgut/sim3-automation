# TERAZİ v1.1 — Bulanık kural kabulü | Ön kayıt eki

2026-10-16. TERAZİ v1 mimarisi (`93d733a`) + düzeltme eki (`TERAZI_V1_MIMARI_DUZELTME_EKI.md`) üzerine. Bu ek, v1.1 kodundan ve sonuçlarından ÖNCE commit edilmiştir.

## Tespit: sert sınır, bulanık mimariye aykırı
Ocak 2023'ün gün gün kaydı, modelin o ay hiç görüş üretmemesinin **bilgi eksikliğinden değil, ikili bir kabul eşiğinden** kaynaklandığını gösterdi:

| 2022-12-30 (Ocak'a girerken) | |
|---|---:|
| En iyi aday: "10Y reel faiz 20g değişim < +1,0σ" beklenen getiri | +%0,433 |
| Kabul eşiği | %0,450 |
| **Fark** | **−%0,017 → REDDEDİLDİ** |

Bir ay sonra (2023-01-31) aynı aday %0,506 ile eşiği geçti ve kabul edildi. Yani kural zaten 2022'de bulunmuştu; ikili eşik onu yüzde binde 17 farkla elemiştir.

Mimarinin geri kalanı bulanıktır (yumuşak kapılar, dereceli tetikleme, dereceli güven). Yalnız kural kabulü sert eşiktir. Bu, hem mimari olarak tutarsız hem de gerçek dünyaya uygun değildir: kanıt derecelidir, kanıtın %1 altında kalması "bilgi yok" demek değildir.

## Değişiklik 1 — kabul yerine dereceli kanıt güveni
Kanıt oranı: `z = |m_küçültülmüş| · √n_eff / sd`. Ceza eşiği `pen` (aşağıda).
- **Kabul:** `z > pen − 1,5·τ` (τ = 1,0 kanıt birimi). Daha zayıf adaylar hiç alınmaz.
- Kural **doğum güveniyle** gelir: `c₀ = kırp( tanh((z − pen)/τ), −0,4, +0,9 )`.
  - Eşiğin tam üstünde: c₀ ≈ 0 → kural sessiz, kendini kanıtlamak zorunda.
  - Eşiğin belirgin üstünde: c₀ → +0,9 → kural baştan konuşabilir.
  - Eşiğin hemen altında: c₀ < 0 → kabul edilir ama sessizdir; sahada kanıt toplayana kadar oy kullanmaz.
- Güven formülü, doğum güvenini **öncül** olarak alır:
  `güven = (2h − k + TRUST_SHRINK·c₀) / (k + TRUST_SHRINK)`
  k = 0'da güven = c₀; saha kanıtı (k) büyüdükçe saha performansı öncülü bastırır. Bu, öncülden sonsala geçişin standart biçimidir ve "oy hakkı sahada kazanılır" ilkesini bozmaz: zayıf kanıtla doğan kural yine sessizdir.

## Değişiklik 2 — etkin bağımsız deneme sayısı
Eski ceza, taranan **ham** aday sayısını (442) bağımsız deneme saydı. Oysa aynı değişkenin komşu eşikleri (örneğin `< +0,5σ` ve `< +1,0σ`) birbirinin neredeyse kopyasıdır; bunlar bağımsız deneme değildir. Tek kapılı adaylarda bağımsız deneme sayısı (değişken × yön) = 35 × 2 = 70'tir; eşik ızgarası tek bir monoton aile taramasıdır.
**Düzeltme:** `M_etkin` = (değişken × yön) + (iki ve üç kapılı ailelerin sayısı), eşik ızgarası ailede tek deneme sayılır. `pen = sqrt(2·ln M_etkin)`.
Bu bir ayar değil, çoklu deneme düzeltmesinin doğru uygulanmasıdır (korelasyonlu testler).

## Değişmeyenler
35 durum değişkeni, yumuşak kapı tanımı ve ızgarası, kural ölüm kuralları, destek eşiği (n_eff ≥ 20), ρ, λ = 0,5, W_min = 0,5, maliyet eşikleri (AL > +%0,803 / SAT < −%0,803), H = 10, aylık doğum/ölüm döngüsü, 2020–2022 ısıtması, 2026 yasağı.

## Dürüstlük uyarısı
Bu iki değişiklik, Ocak 2023'ün sonucu görüldükten SONRA yapılmıştır. İkisi de ilkesel gerekçeye dayanır (ikili eşik keyfidir; korelasyonlu testler bağımsız sayılmaz), performansa göre ayarlanmış sayı yoktur. Buna rağmen geliştirme dönemi (2023–2025) sonucu artık temiz bir okuma değildir ve öyle sunulmayacaktır. **Asıl kanıt 2026 testidir.**
v1 (sert sınır) ve v1.1 (bulanık) sonuçları her zaman yan yana raporlanır. Bundan sonra performansa bakarak başka değişiklik yapılmayacak; gerekirse yeni ön kayıtla TERAZİ v2 yazılır.
