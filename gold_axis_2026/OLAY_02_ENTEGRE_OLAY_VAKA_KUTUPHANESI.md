# OLAY-02 — ENTEGRE OLAY VE VAKA KÜTÜPHANESİ
**2026-10-14 · Tek olay kimliği, tek bütün kayıt.** VAKA-03 isimlendirmesi kaldırılmıştır: vaka, OLAY-02'nin ayrı bir ana belgesi değil, aynı olayın kanıt ve işlem değerlendirme katmanıdır.

## Olayın tek kayıt kontratı
Her `EVENT_ID` altında olayın **(1) takvimi ve haber akışı**, **(2) sürpriz ve mevcut piyasa rejimi**, **(3) XAU/USD 15m ve olay-tetikli 1m fiyat akışı**, **(4) USD/faiz/değerli metaller/risk çapraz verileri ve eksikleri**, **(5) geçmiş benzer/karşıt olaylar**, **(6) neden-sonuç hipotezleri ve kanıt seviyesi**, **(7) NAKİT/GOLD pozisyonuna göre AL/SAT/TUT/BEKLE kararı**, **(8) banka ASK/BID %0,8 alış+%0,8 satış maliyetli sonuç ve kıyas**, **(9) sonradan gözlenen olay sonucu ile karar anında bilinebilir bilginin ayrımı**, **(10) ÖĞREN-03 hipotez kayıtlarına ID bağlantısı** görünmelidir.

Büyük çok-günlü epizot `EPISODE_ID` altındaki NFP, CPI, ISM vb. haberlerin her biri kendi `EVENT_ID` ile bağlıdır. Bir haberin birden çok gün süren altın hareketinin tamamını açıkladığı otomatik varsayılmaz. Güncel olmayan gelecekteki veri geçmiş AL/SAT gerekçesine taşınamaz.

Ham M15/M1 fiyatları özel Neon veritabanında kalabilir; rapor/CSV/JSON kaynakları olay kaydının içinde doğrudan linklenir. Böylece haber, fiyat ve karar ayrı dosyalarda teknik olarak saklansa da **kullanıcı tek olay sayfasından hepsine ulaşır**. Aynı fiyat/haber iki yerde birbirinden farklı doğrulukla tekrar yazılmaz.

## Entegre vaka ve olay dizini (ilk indeks)
| Olay kimliği | Olay/epizot | Haber ve piyasa mekanizması | Zaman damgalı veri + karar + maliyetli sonuç | Öğrenme bağlantısı |
|---|---|---|---|---|
| `MACRO_2023_01_06_NFP` | [5–13 Ocak büyük UP epizodu](independent_gpt_audit/2023-01-05_to_13/GPT_INDEPENDENT_JAN05_13_MACRO_EVENT_COSTED_REPLAY_20261014.md) | ABD NFP, ücret artışı beklentisi, Fed yeniden fiyatlama; ISM 6 Ocak **daha sonra** | [864×15m denetim](independent_gpt_audit/2023-01-05_to_13/GPT_INDEPENDENT_JAN05_13_864X15M_DECISION_LEDGER_20261014.csv) · [M1](independent_gpt_audit/2023-01-05_to_13/GPT_INDEPENDENT_EVENT_M1_GATES_20261014.csv) · [USD100 sonuç](independent_gpt_audit/2023-01-05_to_13/GPT_INDEPENDENT_JAN05_13_REPLAY_RESULTS_20261014.json) | `MECH_FED_DOVISH_REPRICING_UP_V1` |
| `MACRO_2023_02_03_NFP` | [1–24 Şubat büyük DOWN](independent_gpt_audit/2023-02-01_to_24/GPT_INDEPENDENT_FEB01_24_NFP_DOWN_EVENT_CASE_20261014.md) | ABD güçlü NFP, olası Fed şahin beklentisi | [2304×15m](independent_gpt_audit/2023-02-01_to_24/GPT_INDEPENDENT_FEB01_24_2304X15M_STATE_LEDGER_20261014.csv) · [USD100 sonuç](independent_gpt_audit/2023-02-01_to_24/GPT_INDEPENDENT_FEB01_24_NFP_DOWN_RESULTS_20261014.json) | `MECH_FED_HAWKISH_REPRICING_DOWN_V1` |
| `MACRO_2023_01_05_ADP` | [5 Ocak DOWN / 6 Ocak UP](adaptive_volatility_learning/stress_cases/2023-01/JAN_2023_TOP_VOLATILITY_DIRECTIONAL_STRESS_AUDIT_20261014.md) | ADP+claims düşüşü ve ertesi gün başka katalizörlerle geri dönüş | [192×15m](adaptive_volatility_learning/stress_cases/2023-01/JAN05_JAN06_2023_192X15M_ASOF_EVENT_DECISION_LEDGER_20261014.csv) · [karşı-olgular](adaptive_volatility_learning/stress_cases/2023-01/JAN05_JAN06_2023_STRESS_RESULTS_AND_COUNTERFACTUAL_20261014.json) | `MECH_SHORT_DOWN_WHIPSAW_HOLD_V1` |

**Eski kapsamlı olay araştırmasının değiştirilmeyen orijinali:** [TARİHSEL OLAY ARŞİVİ (OLAY-02 kaynak arşivi)](GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST_FULL_HISTORY_SNAPSHOT_20261014.md). Orijinal 0.1A–0.1G çalışması eksiksiz korunur; tüm tarihsel olayların yeni indekse bir seferde geçirildiği iddia edilmez. Diğer vakalar çalışıldıkça veya aktarım doğrulanınca aynı `EVENT_ID` dizinine bağlanır.

**Ana yönetim:** [ANA-01](GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md). **Ortak hipotezler:** [ÖĞREN-03 (eski dosya adı korunur)](adaptive_volatility_learning/EVENT_CAUSAL_ACTION_HYPOTHESIS_REGISTER_20261014.md). **Aylık ilerleme:** ilgili `months/YYYY-MM/STATE.json`.

**Güven sınırı:** Üç olayın karar kuralları ve %0,6/3M1 örnek teyidi geçmiş görüldükten sonra seçildi; gerçek banka kotasyonu ve bağımsız ileri performansı yok. Buradaki bağlantılar araştırma vakasıdır, otomatik banka emri değildir.
