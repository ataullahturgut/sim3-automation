# S2 kayıp günlük veriye ikinci kaynak denetimi — 16 Ekim 2026
**Alan:** GOLD-ADAPTIVE-MODEL-APP-01 / MODEL / araştırma, canlı değildir.
## Bulgular (Neon salt-okunur SQL)
- `gold_research_evduka_xau15m_bidask_candidate`: **141.890** tarihsel BID/ASK M15 satırı, 2020–2025. Tek kaynak: `EVTRADINGLABS_DUKASCOPY_DERIVED_XAUUSD_M15_BIDASK_2020_2025_V1`.
- Dönem-seans yılları 2020: 259, 2021: 258, 2022: 258, 2023: 257, 2024: 259, 2025: 258. **1.500** seans ilk filtrede 80+ bar, geçerli bid/ask, kaynak tekilliği, intraday boşluk ve terminal kapanış kriterlerini karşıladı (251/251/250/249/250/249).
- Eski HistData S2 koşusunda 2023: **118** kabul / 257 aday; alternatif kaynak 2023 **249** ön-kabul / 257 aday. Bunlar **ayrı deneylerdir**; veri kümeleri sessizce birbirine eklenmez.
- Aynı timestamp üzerinde 2023–2025 döneminde 66.251 eşleşmiş M15 fiyatı için ortalama mutlak göreli altın MID farkı **%0,08019**, en yüksek fark **%2,4584**. Sürüm/quote uyuşumu kanıtlanmadığından **tek bir zaman serisi gibi splice yasaktır**.
- Arşiv `HISTORICAL_RECOVERED_2026-10-08_NOT_PIT` ve `DUKASCOPY_DERIVED_BROKER_BID_RETURN_LABEL_WITH_SEPARATE_ASK` sınıfında. Banka %0,8 her-yön işlemin gerçek banka alış/satış zaman damgası değildir.
## Kodlama
- Aynı S2 slow bileşeni `BIDASK_M15_RECONSTRUCTED_NOT_M1` sınıfını ayrıca kabul eder; native M1 kanıtı taklit edilmez, quote-only seanslar sayılır.
- Yeni SQL `S2_SLOW_EV_DUKA_SESSION_AUDIT_2020_2025.sql`: read-only seans çıkarımı; private MID rakamları GitHub'a gönderilmez.
- `replay_slow_lifecycle_s2.js` her iki veri biçimini aynı motorla işler. Salt fiyat ve olay adaylarıdır.
## Bilim
Henüz alternatif 1.500 seans S2 replay modeliyle bitiş/başarı ölçümü çalıştırılmadı. İlk filtre, kapsam ve sürekliliğin *aday kanıtıdır*. Kaynaklar arası bağımsız tutarlılık, resmî altın settlement, tick-firstprint doğrulaması ve kör OOS yoktur. **S2_SCIENCE_GATE=PENDING.**

## Aynı S2 slow CORE gerçek alternatif kaynak tekrar koşusu (16 Ekim 2026)
**2020–2025** sıralı read-only Neon BID/ASK MID araştırması: 1.549 aday seans, **1.500 kabul**, **49 red**, 35 tamamlanmış uzun epizot, 24 sansürlü, medyan 9 seans. 2023–2025 ayrı başlatılan karşılaştırmada 774 aday/748 kabul, **17 bitmiş**, 11 sansürlü, medyan 10 seans. Eski HistData 2023–2025 koşusu **609 kabul, 12 bitmiş** idi; bu kaynaklar **birleştirilmedi**.
| Ufuk | Skor | END | CONTINUE | S2 Brier | Basit baseline | Epizot-kümeli iyileşme %95 GA |
|---|---:|---:|---:|---:|---:|---|
| 1 seans | 231 | 10 | 221 | 0,043069 | **0,042541** | [-0,005497; +0,003775] |
| 3 seans | 196 | 29 | 167 | **0,116184** | 0,123571 | [-0,010241; +0,022798] |
| 5 seans | 171 | 53 | 118 | **0,183422** | 0,203705 | [-0,016597; +0,052688] |
| 10 seans | 131 | 90 | 41 | **0,193725** | 0,229801 | [-0,022712; +0,087526] |
3/5/10 seans araştırma Brier'ı daha düşük olsa da **TÜM GA sıfırı içeriyor** ve tam tarihsel arşivde yürütülen retrospektif deneydir. Ayrı 2023–2025 başlangıç koşusunda 1/3/5/10 skor 49/38/31/22, bitmiş epizot 17; ufukların hiçbirinde iki sınıfın her birinde 12 bağımsız etiket yok. **S2_SCIENCE_GATE=PENDING**, güvenilir alpha veya net ticaret kararı ilan edilmez.

Kod yürütme: doğrudan GitHub'daki aynı `adaptive_slow_lifecycle_s2.js` işlevleri ve salt okunur Neon SQL çıktı dizisi (araştırma arşivi) ile çalıştırıldı; özel fiyat ve model checkpointi GitHub'a alınmadı.
