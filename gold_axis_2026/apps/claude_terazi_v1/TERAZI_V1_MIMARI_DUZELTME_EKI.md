# TERAZİ v1 — mimari ön kayda düzeltme eki

2026-10-16. Ön kayıt `93d733a` ile dondurulan mimari ilk kez koşuldu. İki **belirtim hatası** (spec bug) ortaya çıktı. Bunlar performans ayarı değil, mimarinin kendi mantığına aykırı iki nokta. İlk koşunun sonucu da aşağıda korunmuştur.

## İlk koşunun sonucu (düzeltmeden önce)
Kural tabanı çalıştı: 56 kural doğdu, 16'sı öldü, 40'ı hayatta kaldı; okunabilir kurallar üretildi. Ama model **hiç işlem yapmadı**: 753 işlem gününün 662'sinde görüş üretemedi, kalan günlerde eşiği aşamadı. NAV 100,00 (nakitte kaldı).

## Hata 1 — belirsizlik yanlış şey ölçüyordu
Ön kayıtta U, kural başına **sonuç varyansı** v_R ile tanımlanmıştı:
`U = sqrt( Σ a·w·(v_R + (μ_R − E)²) / W )`
Bu, 10 günlük getirinin **dağılım genişliği**dir (altında tipik olarak σ ≈ %2–3). Oysa karar şu soruyu sorar: *"beklenen getiri maliyeti aşıyor mu?"* Bu sorunun belirsizliği, **ortalamanın standart hatası**dır (sqrt(v/n)), tek bir sonucun saçılması değil.

Sonuç: model, "tipik bir kötü sonuç bile maliyeti aşsın" şartını arıyordu. Ölçülen etki:

| Kural | Eski U | Gereken E | Doğru U | Gereken E |
|---|---:|---:|---:|---:|
| v=9, n=50 | 3,00 | %2,30 | 0,42 | %1,02 |
| v=6, n=80 | 2,45 | %2,03 | 0,27 | %0,94 |
| v=4, n=100 | 2,00 | %1,80 | 0,20 | %0,90 |

En güçlü kuralların beklenen getirisi %1,5–2,2 olduğundan eski tanımla eşik yapısal olarak aşılamıyordu. Bu bir eşik tercihi değil, formül hatasıdır.

**Düzeltme:** `U = sqrt( Σ a·w·(v_R/max(n_R,1) + (μ_R − E)²) / W )`. Kurallar arası çelişki terimi (μ_R − E)² aynen kalır; o zaten ortalamalar arası uyuşmazlığı ölçüyor. λ = 0,5 ve maliyet eşikleri **değişmedi**.

## Hata 2 — ısıtma kuralların saha kanıtı kazanmasına izin vermiyordu
Ön kayıt, oy hakkının yalnız **doğum sonrası** günlerden kazanılmasını şart koşuyor (katman 4). İlk uygulamada ısıtmadaki 6 yapı turunun tamamı aynı ana (2022-12-30) yazılmıştı. Bu yüzden 2020–2022 boyunca hiçbir kural saha kanıtı toplayamadı ve model 2023'e **oy hakkı sıfır** bir tabanla girdi; ilk ayların körlüğü yine oluştu.

**Düzeltme:** Isıtma, maratonun aynı aylık döngüsüyle 2020-01'den itibaren yürütülür; işlem yalnız 2023-01-03'ten sonra açılır. Böylece 2020'de doğan bir kural 2021–2022'de sahada sınanır ve 2023'e kanıtıyla girer. Kullanılan veri değişmez (yalnız geçmiş), yalnız kronoloji düzelir.

## Değişmeyenler
35 durum değişkeni, kapı tanımı ve ızgarası, kural keşif/ölüm kuralları, çoklu deneme cezası, destek eşiği, ρ, λ, W_min, maliyet eşikleri, H = 10, 2026 yasağı.

## Raporlama kuralı
Düzeltilmiş koşum sonucu ne olursa olsun, bu dosyadaki ilk koşum sonucu (NAV 100, işlem yok) birlikte raporlanır. Bundan sonra performansa bakarak başka parametre değiştirilmeyecektir; gerekirse yeni ön kayıtla TERAZİ v2 yazılır.
