# GOLD — Orta/Büyük UP–DOWN Olayları ve Aylık Kalıcı Öğrenme

**Sürüm:** 2026-10-14 · **Durum:** JAN_2023_V0_MISALIGNED_BASELINE_ARCHIVED / EVENT_STRATEGY_NOT_RUN · **Güncel amaç:** [ana manifest](../GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md) ve [olay odaklı yeniden başlangıç protokolü](EVENT_DRIVEN_MEDIUM_LARGE_MOVE_RESTART_CONTRACT_20261014.md).

## Tek saklama prensibi

**Ana manifest = hedef ve bilimsel kurallar, burada ise = çalışmanın üretilebilir kayıtları.** Chat mesajı, model hafızası veya tek aylık Markdown raporu algoritma hafızası değildir. Kalıcı öğrenme için verinin, hesaplamanın, kodun, kararın ve hataların izlenebilir dosya/kayıt olarak saklanması gerekir.

| Yeri | Saklanan | Değişim disiplini |
|---|---|---|
| `EVENT_REGISTRY.json` | Olay kimlikleri; 2023–2026 çapraz yıl benzerlik ve karşı-vakalar; kaynak referansları | Tek olayı farklı yıllarda yeniden kullan; fiyat kümeleri bağımsız ekonomik olay sayılmaz; eski etiket/yeni yorum ayrımı |
| `METHOD_REGISTRY.json` | Özellik ve algoritma kimlikleri; kod yolu, commit, girdi, parametre, deney, başarısız/başarılı sonuç, versiyon | Gerçek kod geliştirilince kayıt ekle; değişen sürümü eskisinin üzerine yazıp kanıtı silme |
| `months/YYYY-MM/STATE.json` | Aylık analiz durumu, olay ve kaynak kimlikleri, sayısal deney, yapay zekâ eleştirisi, test/istatistik, açık sorular ve **sonraki aya devredilecek** dersler | Başlangıçta boş durum; tarihsel bulgular araştırıldıktan sonra gerçek değerleri işle; her kayda evidence_id |
| `AI_REVIEW_PROTOCOL.md` | Yapay zekâya sunulacak kanıt şeması, ikinci görüşün soruları, durma/itiraz ve kalite testleri | Prompt sürümü değişince experiment run karşılaştırması sakla |

**Ham / yüksek hacimli ve lisanslı piyasa veri satırları GitHub'a aktarılmaz.** Kaynak veri zaten bağlı Neon/diğer izinli depoda; burada yalnız gizli veri içermeyen veri kümesi kimliği, şema, as-of/vintage açıklaması, SQL/ETL kod referansı, satır sayısı, içerik hash'i ve sayısal toplulaştırmalar bulunur. Repo kamuya açık olabilir. Erişim anahtarı, özel fiyat tablosu dökümü, kişisel işlem ve banka bilgisi GitHub'a veya haricî modele gönderilmez.

## Aylık geçiş

1. **Ocak 2023** V0 referansı arşiv olarak saklanır; olay temelli **orta/büyük UP/DOWN, başlamış hareket ve maliyet-sonrası BUY/SELL/HOLD/WAIT** yeniden çalışılmadan ay TAMAMLANDI sayılmaz. FULL_HISTORY_DISCOVERY kipinde 2024/2025/mevcut 2026 olayları açıklama ve karşı-vaka için kullanılabilir, tarihsel emir simülasyonunun önbilgisi sayılamaz.
2. Sayısal algoritmanın giriş/vintage, üretilmiş özellikler, yöntem sürümü ve test sonucu, **bulgu seviyesine uygun** şekilde kaydedilir. Kod varsa repoda gerçek dosya ve git commit hash'i gösterilir. Sadece sözel bulgu algoritma sürümü değildir.
3. Yapay zekâ ikinci incelemeyi **algoritmanın önceki kararını, kaynakları ve karşıt vakaları** görerek yapar; orijinal veriyi sessizce değiştiremez. Kaydedilen yorum `AI_REVIEW_PROTOCOL.md` sözleşmesine uyar.
4. Ay sonu `handoff_to_next_month`: desteklenen, reddedilen, henüz teyitsiz kurallar; kullanılan yöntem sürümleri; başarısızlıklar, eksik veri, araştırılacak soru ve yeni deneyler aktarılır. **Ocak olay-stratejisi tamamlandıktan sonra Şubat aynı snapshotı okuyarak** başlar; eski V0 ve yeni strateji ayrı deney olarak korunur.
5. **Kip A keşif:** Geçmişin tüm yılları kullanılabilir, sonuçlar `EX_POST_DISCOVERY` etiketlidir. **Kip B as-of:** Görülmüş yıllardaki mekanizmalardan kör performans iddia edilmez; ayrı donmuş yöntem ve görünmemiş dönem gerekir.

**Kalite kararı:** Tek aylık iyi oran yöntemi 'kanıtlanmış' yapmaz. Negatif ve olaysız kontrol, posthoc optimizasyon kaydı, kaynak ilk yayını, yıl/volatilite rejimi değişimi ve çoklu hipotezler saklanır. Sadece yazılmış kayıtlar otomatik eğitim verisi sayılmaz. Aylık yorum ya da yapay zekâ görüşü, doğrulanmış nicel modelin ağırlıklarını kendiliğinden güncellemez.

## Bugünkü gerçek durum

Bu dizinde **Ocak 2023'ün gerçek 31 günlük hesaplanmış V0 sayısal simülasyonu ve GPT kanıt eleştirisi kayıtlıdır**: [tam aylık sonuç](months/2023-01/JAN_2023_FULL_MONTH_GPT_ONLY_SCIENTIFIC_AUDIT.md), [gün gün 31 UTC](months/2023-01/JAN_2023_31_UTC_CALENDAR_DAYS_ACTIONS_NAV.csv), [20 tam/1 kısmi NY17 seansı](months/2023-01/JAN_2023_21_NY17_SESSIONS_VOL_AND_DECISIONS.csv), [simülasyon sonuç JSON](months/2023-01/JAN_2023_100USD_RESULTS.json), [Şubat devir durumu](months/2023-01/STATE.json). 100 USD → **101,9695 USD**; aynı maliyetle altın pasif **103,7589 USD**; vol-filtresi 20/20 seansta fark yaratmadı, çalışma model üstünlüğü veya gelecek şok olasılığı doğrulaması değildir. Yalnız **GPT yorumlama** kullanılmış, başka AI API çağrılmamıştır; otomatik sürekli çalışan uygulama hâlâ geliştirilmemiştir.


## 14 Ekim amaç düzeltmesi — korunmuş V0, henüz yapılmamış asıl deney

Eski V0 (`$101,9695`) **günlük momentumla pozisyon değiştirme deneyidir; ekonomik olarak anlamlı orta/büyük UP/DOWN olaylarının giriş/çıkışını araştıran strateji değildir**. `$103,7589` pasif altın karşılığıyla aynı satırda tutulur fakat bu farkı asıl sistemin başarısızlığı olarak yorumlamayız. `months/2023-01/STATE.json` içindeki `objective_alignment_audit` ve yeni deney sözleşmesi bağlayıcıdır. Şubat'a doğrulanmış strateji devri **beklemede**.

## Ocak 2023 ikinci deney — orta/büyük olay tarama V1

[31 gün eylem, kaynak/karşı kanıt ve sonuç raporu](months/2023-01/JAN_2023_EVENT3_FULL_31DAY_RESEARCH_REPLAY_20261014.md) · [Günlük NAV/olay CSV](months/2023-01/JAN_2023_EVENT3_31DAY_ACTIONS_NAV_20261014.csv) · [Maliyetli sonuç JSON](months/2023-01/JAN_2023_EVENT3_EXPLORATORY_RESULTS_20261014.json). +3/-3 beş seanslık fiyat olayı: 4 Ocak UP tespiti, 1 AL, 31 Ocak yalnız dönemsonu muhasebesi için SAT; 100 → **101,9914 USD**; aynı kaynaktan pasif altın **103,7589 USD**. **Sayılar tam çalıştırılmış tek-ay fiyat-only exploratory baseline'ıdır; GPT ekonomik olay yorumunun emirleri değiştirdiği veya maliyet-sonrası faydayı artırdığı kanıtlanmadı.** Aynı ayın önceki V0 kaydı korunur. Aylar arası strateji aktarımı yalnız sınırı doğru etiketlenmiş bilgiye dayanır.
