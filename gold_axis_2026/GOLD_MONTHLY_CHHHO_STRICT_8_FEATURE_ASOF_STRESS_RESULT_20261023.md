# GOLD MONTHLY — Katı tarih kesitli dört-metal 8-feature ChHHO-ANFIS tam yeniden optimizasyonu

**Tarih: 23 Ekim 2026**  
**Karar: RESEARCH_COMPLETE / 33-DEV FULL OPTIMIZER / NOT PROMOTED / FIRSTPRINT NOT VERIFIED**

## Neden bu ikinci deney?

[GOLD_MONTHLY_CHHHO_ORIGIN_ANCHOR_FULL_REPLAY_RESULT_20261023.md](GOLD_MONTHLY_CHHHO_ORIGIN_ANCHOR_FULL_REPLAY_RESULT_20261023.md) raporunda aylık getiri tahminlerinin orijinal **8 özellikli X** girdileri değişmeden yalnız `forecast_usd=origin_anchor*exp(pred_return)` fiyat çıpası değiştirilmişti. Bu 33 ayda `1413.03 → 1409.44` USD küçük hata azalması gösterdi. **Ancak X özellikleri origin ayının son takvim günündeki fiyatı içeriyor olabilir.** Sadece çıpayı kesmek, tüm model için aynı as-of cutoff kontratını ispatlamaz.

Bu ikinci deney tüm **Gold, Silver, Platinum, Palladium** günlük serilerini her ay **ay sonunun bir önceki takvim günü** ile sınırlandırıyor; sonra bunlardan **MR ve GPR-weighted VW** özelliklerini sıfırdan çıkarıyor. 2010–2024 geçmiş eğitim `Y` etiketleri hâlâ ilgili tamamlanmış ayın tam günlük ortalama getirileri; target `Y` outer prediction içinde `None`. Ortak HHO optimizasyon bütçesi, 5-rule Sugeno ANFIS, GPR vintage, kronolojik inner holdout ve seed kuralı **değişmiyor**.

**Önemli epistemik sınır:** Son takvim gününü atlamak **fazla muhafazakâr** olabilir; o günün fiyatları karar verilirken gerçekten açıklanmış olabilir. Ayrıca StakTrakr 2026'da alınan geriye dönük fiyat arşividir; kalan günlerin bile **ilk yayın saatleri kanıtlı değildir**. Bu deney yalnız bir *time-cutoff robustness check*, canlı PIT sertifikası değildir.

## Tamamlanan gerçek koşular

| Çalışma | 33 ay gerçek optimizer (24 aday ×45 nesil ×3 repeat) | Eğitim özellikleri | Fiyat çıpası | Başarılı GitHub CI |
|---|---|---|---|---|
| Orijinal ChHHO | EVET | Orijinal CURRENT8 (origin complete) | Retrospektif CORE5 final | [39910607818](https://github.com/ataullahturgut/sim3-automation/actions/runs/39910607818) |
| Yalnız price-origin prefix | Aynı koşunun tahminleri (ayrı yeniden eğitim gerektirmez) | Orijinal CURRENT8 | StakTrakr prefix | aynı |
| Tüm X ve fiyat çıpası prefix | **EVET, baştan 33/33 tam optimizer** | Gold/Ag/Pt/Pd 8 özellik prefix | StakTrakr prefix | [39911429995](https://github.com/ataullahturgut/sim3-automation/actions/runs/39911429995) |

Her iki CI'da DB bağlantısı kapalı, aynı immutable `GOLD_MONTHLY_DEV_SNAPSHOT_V1_2026-09-28` SHA `2111e394f60d131995273789fc014dc339db4e1b7672095c89117c133879a3eb`. 2025–2026 satırları *yok*. İkinci CI'da 33/33 `STRICT_FEATURE_FULL_OPTIMIZER_PROGRESS` geçti; `STRICT_FEATURE_FULL_REPLAY_GATE=PASS` verdi. İş çıktısı Actions artifact **12483176426** `monthly-chhho-strict-feature-replay-374ef3a37df52303ff4739007d461f728ad21fda`, her hedef için model optimizasyon diagnostics ve tahmini içerir.

## Sayısal sonuçlar — aynı CORE5 nihai aylık altın fiyatı hedefi

| Yöntem | ΣAE USD (33 ay) | MAE USD/oz | MAPE | Yön |
|---|---:|---:|---:|---:|
| Orijinal X, CORE5 final origin | **1413.029779** | 42.819084 | 2.107678% | 23/33 |
| Orijinal X, **strict prefix** origin | **1409.436034** | 42.710183 | 2.101522% | 24/33 |
| **STRICT PREFIX 8 X**, **strict prefix** origin | **1855.692973** | 56.233120 | 2.778204% | 21/33 |

Tamamen strict-X yeniden öğrenim orijinal modele karşı ΣAE **+442.663193 USD**, yani **yaklaşık %31.33 daha fazla toplam hata**. Doğru yön **23/33 → 21/33**. Son günlük gözlemin girdiye girmesi modelde anlamlı değişim yaratıyor; ancak bu farkı tek başına `lookahead leak` diye ilan etmek bilimsel olarak doğru değil. Kaynağın yayın saatine ve tahmin karar saatine bakılmadan yasak veri mi, meşru en son fiyat mı olduğu ayırt edilemez.

### Yıllık toplam mutlak hata CORE5 nihai hedefe karşı

| Yıl | Orijinal X/orijin | Orijinal X/strict origin | Full strict X+origin |
|---|---:|---:|---:|
| 2022 (9 ay) | 397.879386 | 398.201208 | 678.537034 |
| 2023 (12 ay) | 395.713992 | 399.656062 | 475.269383 |
| 2024 (12 ay) | 619.436402 | 611.578763 | 701.886556 |
| **TOPLAM** | **1413.029779** | **1409.436034** | **1855.692973** |

Özellikle 2022'deki fark yüksek; tekil ay aşırı uçları için ayrıca artifact per-month hata ve condition-number analizi gerekecek. Bu koşu yeni mimarinin 'üstün' olduğu seçimi yapmaz.

### Daha aynı kaynaktan eğitim hedefine göre kontrol

Y label'ları STAK spot metal aylık ortalamalarıyla üretildiğinden, STAK spot aylık hedefiyle ayrıca:

| Yöntem | 33-ay ΣAE STAK spot monthly label'a göre | Yön |
|---|---:|---:|
| Orijinal | 1377.510941 | 24/33 |
| Sadece anchor strict | 1373.917195 | 24/33 |
| X+anchor strict | **1829.472480** | 21/33 |

Kaynak-hedef eşleştirme değiştirilse de sıkı X varyantı açıkça geride kalıyor.

## Bilimsel statü / değişiklik kapsamı

1. **KAPATILDI (kod):** Tahmin ayının gerçekleşmiş fiyatı gerekmeden `X,None` ileri tahmin kontratı kuruldu; 10 hedef-label test PASS.
2. **KAPATILDI (araştırma):** Önceki aya ait geçici fiyat ortalaması (strict son gün hariç) ayrı bir hesaplama, tatil/hafta sonu testleri ve ilk bağımsız 33 ay optimizer karşılaştırmasıyla doğrulandı (7 kaynak test PASS; eski optimizer 33/33 parity).
3. **KAPATILDI (hassasiyet):** Tüm 8 özelliğin de aynı tarih kesitine zorlanmasıyla 33-ay ayrı *gerçek* optimizer testi tamamlandı ve performans belirgin bozuldu.
4. **AÇIK (as-of gerçeği):** Stak/XAU ve diğer metallerin tarih-saatli orijinal piyasa **firstprint**, aylık nihai WB/CORE5 **yayın-vintage** ve GPR PIT uluslararası kaynakların gerçek yayın timestamp'i, ayrıca tahminin kesin saat dilimi kararlaştırılmalı. Son takvim gününü çıkaran test **kanıtlı doğru üretim kontratı değildir**.
5. **AÇIK (dış doğrulama):** Gerçek kaynaklarla kronolojik dönemin yeniden tam eğitimi, 2025 ve 2026 transport, gerekirse yeni bağımsız tarihler. 2025/2026 daha önce analiz edildiği için bunları yeni kör örnek olarak kabul etmek doğru değil. Production/model promotion yok; DB write yok. Eski tüm tahminler frozen tutuldu.

## Hüküm

**Mevcut yıllık DEV başarısı aritmetik olarak tekrar üretilebilir; fakat as-of kaynak-zamanı güvenilirliği hâlâ kesin kanıtlanmış değil.** Modelin son origin günü fiyatlarına ciddi duyarlılığı bulundu; elimizdeki arşiv kaynakların gerçek zamanlı yayımlanma saati olmadığından gün sonu gözlemini kullanmayı otomatik olarak sızıntı, dışlamayı da otomatik olarak bilimsel doğruluk ilan etmiyoruz. Bir sonraki kapı **decision_clock + firstprint-aware data ingest** kontratını kaynak bazında kilitlemektir.
