# ALTIN OLAY ARAŞTIRMASI — TEK VE SABİT BELGE HARİTASI
**2026-10-14 • Belge rolleri netleştirildi. Bu dosya yol tabelasıdır, ek bir manifest değildir. ÖĞREN-03 aynı dosyada çıkarım manifestine yükseltildi.**

| Kod | Tam adı | Mevcut gerçek dosyası | Tek rol |
|---|---|---|---|
| **ANA-01** | **Proje Ana Manifesti** | [ANA-01](GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md) | Proje hedefi, as-of/saat/maliyet protokolü, araştırma ve onay yönetimi |
| **OLAY-02** | **Olay, Haber, Veri ve Vaka Araştırma Manifesti** | [OLAY-02 — ASIL ARAŞTIRMA KAYNAĞI](OLAY_02_ENTEGRE_OLAY_VAKA_KUTUPHANESI.md) | **96 fiyat kaydı, 96 kaynaklı haber/veri fişi, 9 karşıt vaka, 3 sayısal karar denemesi** tek olay kimlik zincirinde |
| **ÖĞREN-03** | **Çıkarım ve Olay Karakteri Manifesti** | [ÖĞREN-03 — çıkarım manifesti](adaptive_volatility_learning/EVENT_CAUSAL_ACTION_HYPOTHESIS_REGISTER_20261014.md) | 7 aday ekonomik grup, 5 ölçülebilir uzun fiyat karakteri, başlangıç–gelişim–bitiş, 96 olayla bağlantılar ve üç mevcut karar hipotezi |
| **DURUM-04** | **Aylık Çalışma Durumu** | [Ocak 2023 STATE.json](adaptive_volatility_learning/months/2023-01/STATE.json) | Her ayın ilerlemesi, eksikleri, son test ve sonraki aya devir |

**NET SAYIM:** **3 aktif manifest (ANA-01, OLAY-02, ÖĞREN-03/ÇIKARIM) + 1 yardımcı aylık DURUM-04 kaydı.** Olayın kanıtı yalnız OLAY-02'de, ekonomik genellemesi yalnız ÖĞREN-03'tedir; yeni müstakil fiziksel manifest açılmadı. Eski [5.190 satırlık tarihsel araştırma arşivi](GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST_FULL_HISTORY_SNAPSHOT_20261014.md) **salt okunur**, bu dörde rakip değil. [96 ayrıntılı fiş](OLAY_02_96_KAYIT_TEK_TEK_DOSYALAR_20261014.md), [96 CSV](OLAY_02_96_KAYIT_DENETIMLI_KATALOG_20261014.csv), diğer sonuç raporları **OLAY-02 alt kanıtıdır, manifest değildir**. Geçmişte kullanılan **VAKA-03**, **ÖĞREN-04** ve **DURUM-05** isimleri **kullanımdan kaldırıldı**; asıl eski dosya adları ve deliller kırılmasın diye fiziksel olarak korundu.

**Kapsamın gerçek sınırı:** 96 olay fişi var ama 96 fiyat dalgasının ilk haberiyle nedensel eşleşme **henüz doğrulanmadı**; 3 işlem senaryosu geriye dönük banka fiyat vekili, gerçek AL/SAT veya doğrulanmış OOS değil.

**Her işlemden sonra rapor fişi:** `ÇALIŞILAN EVENT_ID → OKUNAN OLAY-02 KAYNAĞI → GÜNCELLENEN TAM DOSYA YOLU VE BELGE KODU → ÖĞREN-03 hipotez ID → testin sayısal sonucu ve sınırı → değişmeyen dünkü arşiv → git dalı + doğrulanmış commit`. Başka araştırma dalındaki Claude sonuçlarını GPT kanıtlarının üstüne yazma; önce bağımsız analizi sonra çapraz denetimi kaydet.
