# GOLD MONTHLY — Origin fiyat seviyesi / ChHHO-ANFIS tam optimizasyon yeniden koşusu

**23 Ekim 2026 | Tamamlandı: frozen DEV 33/33, teknik testler PASS | Yalnız araştırma dalı**

## Karar

**İki ayrı kod işi yapıldı:**
1. Hedef ay için `X` girdileri gerçekleşmiş hedef fiyatına başvurmadan oluşturuluyor; geçmiş etiketler `Y` yalnız eğitim aylarına ait. Gerçek CHHHO bu koşullarda tahmin yapabiliyor.
2. Önceki ayın **retrospektif nihai CORE5 ortalamasını** fiyat çıpası olarak kullanmak yerine, dondurulmuş dört-metal günlük veri arşivinin aynı ayına ait altın fiyatlarından **katı tarih kesitli geçici ortalama** ayrı araştırma kolu olarak tanımlandı. Son takvim günündeki fiyat kaydı katı kolda alınmaz.

Orijinal 8-girdi/5-kural/4-çıktı ChHHO-ANFIS yapısı ve optimizer bütçesi **değiştirilmedi**. Dondurulmuş `GOLD_MONTHLY_DEV_SNAPSHOT_V1_2026-09-28` payload SHA `2111e394f60d131995273789fc014dc339db4e1b7672095c89117c133879a3eb`, salt okunur, 2025 ve 2026 kaynak satırları yok.

**Resmî veri yayın-zamanı PIT sertifikası yoktur:** StakTrakr günlük serisi 2010'dan beri tarihli fiyatlar barındırıyor ama arşiv olarak 2026'da çekildi, günlük gözlemlerin o gün ve saat ilk yayımlandığı doğrulanamadı. Dolayısıyla `STAK_PREFIX_STRICT_DATE` *tarih-kesitli tarihsel stres deneyi*, bir **canlı PIT veri düzeltmesi tamamlandı** iddiası değildir. CORE5 eski sonuç ayrı tutulur, üretim girişi otomatik değiştirilmez.

## Deney: 33 hedef ay, her ayda gerçek tam ChHHO

- 2022-04..2024-12, **33** hedef ay, 2010-03'ten başlayan uygun geçmiş aylık etiketler (ilk DEV ayında 145, son DEV ayında 177 train satırı).
- Her ay **24 aday × 45 nesil × 3 deterministik tekrar**, kronolojik inner holdout, ayrı yerel ANFIS epoch seçimi, daha sonra tam pre-target history refit.
- `outer_target` satırı yalnız `(X,None)`; hedef ay altın/gümüş/platin/paladyum gerçekleşmiş fiyatları train/validation özelliklerine dahil edilmez.
- `STAK_PREFIX_STRICT_DATE`: ön ayın 1'inden **son takvim gününden bir önceki güne kadar** tarihli, yalnız hafta içi altın değerlerinin basit ortalaması. En az 15 fiyat kaydı, tekil/sıralı tarih, fiyat >0 şartı, hafta sonu reddi. 33 aylık SQL bağımsız veri denetiminde **18–22** business day, 0 hafta sonu satırı.
- `STAK_FULL_ORIGIN_MONTH`: aynı günlük seride son takvim günü de dahil, kontrol kolu. Kaynak tarihi kontrolü dışında yayın saati kanıtı yok; daha fazla veri kullanır.
- `CORE5_FINAL_HISTORICAL`: eski nihai aylık araştırma çıpası, tahmin ayı sonunda *yayımlanmış* olduğuna dair kanıt **yok**.
- Üç kolda ChHHO'nun tahmin ettiği aynı `log_return` **değişmedi**; yalnız `origin_anchor × exp(pred_log_return)` farklı. Orijinal optimizasyon 33 ayın tümünde **gerçekten yeniden çalıştırıldı**; aşağıdaki fiyat-çıpası varyantları için gereksiz ayrı HHO eğitimleri yapılmadı (özellikler aynı).

## Doğrulanmış çıktı — hedef: CORE5 / Dünya Bankası ile uyumlu nihai aylık ortalama

| Çıpa | DEV 33 ay toplam mutlak hata (USD/ons toplam) | MAE USD/ons | MAPE | Yön |
|---|---:|---:|---:|---:|
| CORE5_FINAL_HISTORICAL (eski) | **1413.0297794085** | 42.819084 | 2.107678% | 23/33 |
| STAK_PREFIX_STRICT_DATE (ana araştırma düzeltmesi) | **1409.4360335973** | 42.710183 | 2.101522% | **24/33** |
| STAK_FULL_ORIGIN_MONTH (kontrol) | **1400.5227226816** | 42.440083 | 2.087634% | **24/33** |

Ana katı-tarih kesitli geçici çıpa eskiye göre **3.5937458112 USD / 33 ay** daha az toplam hata (≈%0.2543); MAE farkı ≈0.1089 USD/ons. Çok **küçük**; modelin istatistiksel ya da canlı başarısı yönünde kanıt değil. FULL control daha düşük ama doğrudan üstün yöntem ilan edilmez.

### Yıllık DEV toplam mutlak hata (CORE5 hedefi)

| Yıl | CORE5 eski | STAK strict date | STAK full |
|---|---:|---:|---:|
| 2022 (9 ay) | 397.879386 | 398.201208 | 394.782920 |
| 2023 (12 ay) | 395.713992 | 399.656062 | 395.382427 |
| 2024 (12 ay) | 619.436402 | 611.578763 | 610.357376 |

**Dikkat:** Strict kaynak 2022 ve 2023'te eski çıpadan **daha kötü**, toplam kazanç 2024 ağırlıklı. “Her yıl üstün” diyemeyiz.

## Modelin gerçek öğrenme hedefiyle kaynak eşleştirme kontrolü

Modelin eğitim label'ları dört metalin `StakTrakr` günlük ortalamalarından hesaplanan aylık log-return'dür, `CORE5` doğrudan altın hedefi değil. Bu nedenle aynı hesapları **STAK_MONTHLY_MATCHED** günlük-fiyat-aylık ortalaması hedefiyle ayrıca yaptık:

| Çıpa | 33 ay ΣAE, Stak-uyumlu aylık ortalama | Yön |
|---|---:|---:|
| CORE5 nihai | 1377.510941 | 24/33 |
| STAK strict date | 1373.917195 | 24/33 |
| STAK full | 1365.003884 | 24/33 |

Bu da orijinal (STAK eğitilmiş return × CORE5 origin) ile (STAK target) arasında **birim değil metodolojik fixing/source uyuşmazlığı** olduğunu gösterir. **Gerçek nihai aylık tahmin hedefimiz** hâlâ CORE5/WB olduğu için ana rapor CORE5 hedefiyle verilmiştir.

## Kesin orijinal parity ve teknik doğrulama

[GitHub Actions **run 39910607818 (SUCCESS)**](https://github.com/ataullahturgut/sim3-automation/actions/runs/39910607818)

- **33/33 `ANCHOR_REPLAY_PROGRESS`** kaydı; 2024-12 son noktada 33/33 tamamlandı.
- Orijinal DEV referansı `1413.0297794085`, yeniden üretim `1413.0297794084559` (floating-point hassasiyetinde aynı), yön **23/33**.
- Araştırma yeni source proxy testleri **7/7 PASS**, önceki unlabeled-target regression **10/10 PASS**, toplam **17/17** özel test (genel repo CI değil).
- Frozen sonuç artifact ID **12482925939**, artifact `monthly-chhho-origin-anchor-replay-bc26ce04b2110e418f979e06c0160bce7afca913`; tam model diagnostics, per-origin satırlar, her çıpa ve her hedef çıktısı içerir.
- CI koşusu DB'ye erişmiyor (env `NEON_DATABASE_URL:''`), immutable snapshot kullanıyor; canlı üretim modeline, tahmin kayıtlarına, Neon verilerine write yok.
- Ayrı ve eski `Gold Control V1.49 research governance` test grubu ana dalın mevcut eksik artefaktları dolayısıyla bu araştırma branch'inde başarısız; **bütün repo yeşil değildir**. Bu özel deneyin ayrı CI run'ı PASS.

## Hangi riskler kapanmadı?

1. **Gerçek first-publication kaynak:** 2010–2024 Stak günlük fiyatlarının tarih-saatli özgün yayın/vintage delilleri yok. Tarih kesiti yalnız gözlem tarihini sınırlar; piyasaya bilgi ne zaman ulaştı sorusunu bütünüyle kanıtlamaz.
2. **WB aylık nihai yayın gecikmesi:** Origin ayındaki CORE5 final ortalaması origin sonu itibarıyla erişilebilir sayılmamalı; gerçek üretimde açıkça belirtilmiş yayın/vintage kurallı first-print daily feed kullanılmalı.
3. **GPR origin-vintage:** 2022–24 resmî Git arşiv snapshot yeniden kuruldu; o gün sistemin çektiğine dair canlı capture kanıtı yok.
4. **2025/2026 farklı dönemler:** Bu **tam full-optimizer ayrı run yalnız 33 DEV ayını** kapsar; 2025 ve 2026 örnekleri bu immutable snapshot'ta bulunmaz. Daha önce salt okunur fiyat çıpası duyarlılığı ölçülmüş olsa da onu bu yeni tam optimizasyon sonucu diye sunmamak gerekir.
5. **İleri tahmin performansı:** Seçim yanlılığı, yaşanmış 2025/2026 sonuçları, yeni untouched/future paper trading olmadan giderilemez.

## Sonuç / sonraki bilimsel karar

**Kod düzeltmesi ve 33 aylık tam optimizer karşılaştırması başarıyla tamamlandı.** Eski referans özdeş yeniden hesaplandı; katı günlük tarih kesitli geçici ortalama teknik olarak çalışıyor ve 33 ayda daha iyi görünen, ancak ekonomik/statistiksel olarak küçük fark üretiyor. Ana modelin doğruluğu bugünkü kanıttan daha güçlü ilan edilmez. Bundan sonra **gerçek as-of yayımlanma zamanlı günlük veri kaynağı** edinilmeli ve onunla 2025/2026'yı da içeren *kronolojik, değiştirilmeyen optimizer* transport testi yapılmalı; production izin/yükseltme ayrıca kararlaştırılmalıdır.

## Sonraki tam 8-girdi zaman-kesiti koşusu — kritik tamamlayıcı sonuç

Bu sayfadaki price-origin çalışmasında **8 model girdisi değiştirilmemişti**. Sonradan tüm dört metalin MR ve VW X özellikleri de son takvim günü dışlanarak **33 ayın her birinde yeniden tam orijinal ChHHO-ANFIS optimizasyonu** çalıştırıldı:

- [Ayrıntılı rapor: GOLD_MONTHLY_CHHHO_STRICT_8_FEATURE_ASOF_STRESS_RESULT_20261023.md](GOLD_MONTHLY_CHHHO_STRICT_8_FEATURE_ASOF_STRESS_RESULT_20261023.md)
- Full strict X+origin CORE5 DEV ΣAE **1855.692973 USD**, direction **21/33**, eski **1413.029779 USD**, **23/33**. **%31.33 daha yüksek toplam hata**.
- [CI 39911429995](https://github.com/ataullahturgut/sim3-automation/actions/runs/39911429995) = SUCCESS, 33/33 optimizer. Son günün veri yayınlanma saati kanıtlı olmadığından bunu otomatik "geleceği görme" teşhisi diye değil, **tahmin anı bilgi-kesiti duyarlılığı** olarak yorumla.

