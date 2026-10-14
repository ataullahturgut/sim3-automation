# GOLD — Aylık Olay Öğrenme ve Adaptif Volatilite Araştırması

**Sürüm:** 2026-10-14 · **Durum:** RECORDING_FRAMEWORK_READY / RESEARCH_NOT_STARTED · **Güncel amaç:** [ana manifest](../GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md).

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

1. **Ocak 2023** `2023-01/STATE.json` başlangıç kaydı ile açılır. FULL_HISTORY_DISCOVERY kipinde 2024/2025/mevcut 2026 olayları da benzer veya karşıt vaka olarak incelenebilir.
2. Sayısal algoritmanın giriş/vintage, üretilmiş özellikler, yöntem sürümü ve test sonucu, **bulgu seviyesine uygun** şekilde kaydedilir. Kod varsa repoda gerçek dosya ve git commit hash'i gösterilir. Sadece sözel bulgu algoritma sürümü değildir.
3. Yapay zekâ ikinci incelemeyi **algoritmanın önceki kararını, kaynakları ve karşıt vakaları** görerek yapar; orijinal veriyi sessizce değiştiremez. Kaydedilen yorum `AI_REVIEW_PROTOCOL.md` sözleşmesine uyar.
4. Ay sonu `handoff_to_next_month`: desteklenen, reddedilen, henüz teyitsiz kurallar; kullanılan yöntem sürümleri; başarısızlıklar, eksik veri, araştırılacak soru ve yeni deneyler aktarılır. **Şubat aynı snapshotı okuyarak** başlar; sonuçlara göre sürüm artırılır, eski kayıt korunur.
5. **Kip A keşif:** Geçmişin tüm yılları kullanılabilir, sonuçlar `EX_POST_DISCOVERY` etiketlidir. **Kip B as-of:** Görülmüş yıllardaki mekanizmalardan kör performans iddia edilmez; ayrı donmuş yöntem ve görünmemiş dönem gerekir.

**Kalite kararı:** Tek aylık iyi oran yöntemi 'kanıtlanmış' yapmaz. Negatif ve olaysız kontrol, posthoc optimizasyon kaydı, kaynak ilk yayını, yıl/volatilite rejimi değişimi ve çoklu hipotezler saklanır. Sadece yazılmış kayıtlar otomatik eğitim verisi sayılmaz. Aylık yorum ya da yapay zekâ görüşü, doğrulanmış nicel modelin ağırlıklarını kendiliğinden güncellemez.

## Bugünkü gerçek durum

Bu dizin **boş sözleşme / kayıt altyapısıdır**. Ocak 2023 için henüz veri toplama, olay karşılaştırması, eğitim, çıkarım, AI değerlendirmesi veya başarılı model testi gerçekleştirilmiş değildir. Mevcut eski araştırmalar ana manifestten izlenebilir; ancak bu dizine onaysız/otomatik yeni test sonucu diye kopyalanmaz.
