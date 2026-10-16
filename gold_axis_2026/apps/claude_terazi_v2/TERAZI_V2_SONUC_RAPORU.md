# TERAZİ v2 — Evre (faz) modeli: maraton sonucu

2026-10-16. Sıra: ön kayıt `212e876` → kod ve 7 nedensellik testi → bu sonuç. Isıtma 2020-01→2022-12, işlem 2023-01-03→2025-12-31. **2026 verisi yüklenmedi.**

## Model artık istenen şeyi yapıyor
Soru değişti: "10 günde beklenen getiri" değil, **"altın şu an yükselme evresinde mi?"** Sabit tutma süresi yok; model evre değişene kadar pozisyonda kalıyor. Banka komisyonu karardan çıkarıldı (NAV'da tam uygulanıyor).

## Sonuç (100 USD, 774 işlem günü)

| | Son değer | Maks. düşüş | İşlem |
|---|---:|---:|---:|
| **TERAZİ v2 (net, masraflı)** | **202,82** | %11,67 | 7 |
| TERAZİ v2 (brüt, masrafsız) | 215,31 | — | 7 |
| Pasif altın | 230,82 | %10,79 | 1 |
| DENEYİM v1.2 | 220,07 | %10,79 | 1 |
| SMA100 trend | 215,36 | %11,42 | — |
| TERAZİ v1.1 (bulanık, getiri hedefi) | 153,92 | %10,36 | 1 |
| TERAZİ v1 (sert sınır) | 131,10 | %10,36 | 1 |
| İdeal yol (geriye dönük) | 2.289,69 | — | 39 bacak |

Masrafın bedeli: 215,31 − 202,82 = **12,5 puan** (7 işlem).

**Modelin pozisyonu gerçek evreyle 540/774 günde (%70) uyuştu.**

## İşlem defteri

| Tarih | Karar | Fiyat | P(yükselme) |
|---|---|---:|---:|
| 2023-01-03 | AL | 1836,33 | 0,546 |
| 2023-02-23 | SAT | 1826,56 | 0,427 |
| 2023-03-06 | AL | 1853,65 | 0,619 |
| 2023-10-02 | SAT | 1839,47 | 0,381 |
| 2023-10-12 | AL | 1880,56 | 0,598 |
| 2023-12-12 | SAT | 1983,70 | 0,442 |
| 2024-01-02 | AL | 2073,53 | 0,615 |

**Model Ocak 2023'ün ilk günü aldı** — v1'de kaçırdığı giriş. 2023'te evreleri takip edip üç kez girip çıktı, Ocak 2024'ten sonra yükseliş evresinde kalıp hiç satmadı.

## Model ne öğrendi?

En güçlü kurallar (P = yükselme evresi olasılığı):

| Kural | P | Güven | Saha |
|---|---:|---:|---:|
| altın 20g getiri < +1σ **VE** 60g zirveye uzaklık < +0,5σ **VE** son NFP sürprizi... | 0,83 | +0,85 | 51,8 |
| altın 20g getiri < +1,5σ **VE** zirveye uzaklık < +0,5σ **VE** COT < +1,5σ | 0,78 | +0,94 | 6,0 |
| zirveye uzaklık < +1σ **VE** COT < +1,5σ | 0,77 | +0,90 | 0,0 |

Ortak örüntü: **"altın aşırı ısınmamış, zirveye yapışmamış ve spekülatif pozisyon aşırı kalabalık değil"** → yükselme evresi devam ediyor. Yani model, trendin sağlıklı olup olmadığına bakıyor; yükselişi değil, yükselişin **sürdürülebilirliğini** öğrendi.

Kural tabanı: 198 kural doğdu, 51'i öldü, 60'ı hayatta (üst sınır). Her gün görüş üretildi (görüşsüz gün: 0).

## Zigzag eşiği duyarlılığı (seçim için kullanılmadı)

| Evre eşiği | Son NAV | İşlem |
|---|---:|---:|
| %3 | 182,96 | 23 |
| **%5 (birincil)** | **202,82** | 7 |
| %8 | 176,29 | 5 |

Birincil eşik önceden seçilmişti; %3 ve %5 arası fark modelin eşiğe duyarlı olduğunu gösteriyor. Bu bir zayıflık ve 2026 testinde akılda tutulmalı.

## Bulunan ve düzeltilen hata
İlk v2 koşusunda model hiç işlem yapmadı ve tüm kurallar P ≈ 0,47 veriyordu. Nedeni, indirimli oran güncellemesinde cebirsel bir hataydı: eski kanıt iki kez indirime uğruyor ve payda ile pay uyuşmuyordu, bu yüzden oran sistematik olarak sıfıra çekiliyordu. Ölçüm: aynı kural için ampirik oran 0,770 iken formül 0,469 üretiyordu. İndirimli toplam ayrı tutulacak şekilde düzeltildi (artık 0,894; son dönem ağırlıklı ampirik 0,946). Bu bir kodlama hatasıdır, ön kayıttaki belirtimin doğru uygulanmasıdır; parametre ayarı değildir.

## Dürüst değerlendirme

**İyi olan:**
- Model senin tanımladığın mantıkla çalışıyor: evre takip ediyor, emin olunca giriyor, evre dönünce çıkıyor, her kararını kuralla açıklıyor.
- Ocak 2023'ün ilk günü girdi; önceki sürümlerin kaçırdığı giriş yakalandı.
- Pozisyonu gerçek evreyle %70 uyuştu. Kurallar ekonomik olarak anlamlı ve okunabilir.
- 51 kural sahada başarısız olduğu için öldü; içsel uyumla oy hakkı kazanan olmadı.

**Eksik olan:**
- Pasif altını (230,82) hâlâ geçmiyor: 202,82. Fark 28 puan; bunun 12,5'i masraf, kalanı 2023'teki üç gidiş-gelişin zamanlama kaybı.
- Zigzag eşiğine duyarlı (%3 → 183, %5 → 203).
- 2024-01'den sonra hiç satmadı; yani büyük düşüşlerden kaçınma yeteneği yine sınanmadı.
- **En önemlisi:** v1 → v1.1 → v2 zinciri geliştirme dönemine bakılarak değişti. Bu sayılar kanıt değil, geliştirme kaydıdır.

## Dondurma
`TERAZI_V2_DONDURULMUS_MODEL.json`: 60 kural, standartlaştırma durumu, tüm sabitler. Bu, geliştirme dönemine bakılarak yapılan **son** yapısal değişikliktir. 2026 testi bu dosyayla, kod değiştirilmeden yapılacaktır.
