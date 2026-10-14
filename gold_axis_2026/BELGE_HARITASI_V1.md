# ALTIN OLAY ARAŞTIRMASI — TEK VE SABİT BELGE HARİTASI
**2026-10-14 • Bu dosya yol tabelasıdır, ek bir manifest değildir. İsimler ve görevler sabittir.**

| Kod | Tam adı | Mevcut gerçek dosyası | Tek rol |
|---|---|---|---|
| **ANA-01** | **Proje Ana Manifesti** | [ANA-01](GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md) | Proje hedefi, as-of/saat/maliyet protokolü, araştırma ve onay yönetimi |
| **OLAY-02** | **Olay, Haber, Veri ve Vaka Araştırma Manifesti** | [OLAY-02 — ASIL ARAŞTIRMA KAYNAĞI](OLAY_02_ENTEGRE_OLAY_VAKA_KUTUPHANESI.md) | **96 fiyat kaydı, 96 kaynaklı haber/veri fişi, 9 karşıt vaka, 3 sayısal karar denemesi** tek olay kimlik zincirinde |
| **ÖĞREN-03** | **Ortak Öğrenme ve Karar Mekanizmaları Sicili** | [ÖĞREN-03](adaptive_volatility_learning/EVENT_CAUSAL_ACTION_HYPOTHESIS_REGISTER_20261014.md) | OLAY-02'den türetilen, yanlışlanacak veya doğrulanacak ortak mekanizmalar |
| **DURUM-04** | **Aylık Çalışma Durumu** | [Ocak 2023 STATE.json](adaptive_volatility_learning/months/2023-01/STATE.json) | Her ayın ilerlemesi, eksikleri, son test ve sonraki aya devir |

**NET SAYIM:** **2 aktif manifest + 2 yardımcı kayıt.** Başka bir aktif olay manifesti yok. Eski [5.190 satırlık tarihsel araştırma arşivi](GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST_FULL_HISTORY_SNAPSHOT_20261014.md) **salt okunur**, bu dörde rakip değil. [96 ayrıntılı fiş](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md), [96 CSV](OLAY_02_96_KAYIT_DENETIMLI_KATALOG_20261014.csv), diğer sonuç raporları **OLAY-02 alt kanıtıdır, manifest değildir**. Geçmişte kullanılan **VAKA-03**, **ÖĞREN-04** ve **DURUM-05** isimleri **kullanımdan kaldırıldı**; asıl eski dosya adları ve deliller kırılmasın diye fiziksel olarak korundu.

**Kapsamın gerçek sınırı:** 96 olay fişi var ama 96 fiyat dalgasının ilk haberiyle nedensel eşleşme **henüz doğrulanmadı**; 3 işlem senaryosu geriye dönük banka fiyat vekili, gerçek AL/SAT veya doğrulanmış OOS değil.

**Her işlemden sonra rapor fişi:** `ÇALIŞILAN EVENT_ID → OKUNAN OLAY-02 KAYNAĞI → GÜNCELLENEN TAM DOSYA YOLU VE BELGE KODU → ÖĞREN-03 hipotez ID → testin sayısal sonucu ve sınırı → değişmeyen dünkü arşiv → git dalı + doğrulanmış commit`. Başka araştırma dalındaki Claude sonuçlarını GPT kanıtlarının üstüne yazma; önce bağımsız analizi sonra çapraz denetimi kaydet.
