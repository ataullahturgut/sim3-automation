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
