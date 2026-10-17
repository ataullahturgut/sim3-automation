# GOLD MODEL — GPT ekonomik mekanizma yorumcusu / Ocak–Şubat 2023 araştırma protokolü v1.0

**İlgili proje:** GOLD-ADAPTIVE-MODEL-APP-01; yeni bağımsız model ailesi değil.  
**Sürüm:** 2026-10-17. **MODE:** RESEARCH_ONLY, BANK_TRADE=false, SCIENCE_GATE=FAIL.  
**Uygulama:** `apps/portfolio_guard_v1` → `Ocak–Şubat 2023 · AI mekanizma deneyi`.  
**Girdi:** Gerçek yalnızca tamamlanmış fiyat barı ve önceki olgun çıktılar; olay kanıtı birincil ilk-yayın değilse RETROSPECTIVE_QUARANTINE.

## Amaç ve kontrol kolları

- CORE: orijinal `adaptive_market_core_s1_s2.js`; modelin kendi `action:null/tradeAllowed:false` durumuna müdahale edilmez. Gerçek 2023 koşusunda **100 USD CASH**.
- AI: **yalnız bağımsız, gerçek GPT çıktısı varsa** araştırma shadow portföyü; hiç GPT yanıtı yoksa *başarı/başarısızlık getiri metriği YOK*, kâr üretmek veya `S3 KEEP` etiketini GPT'nin kararı olarak kopyalamak YASAK.
- HİBRİT: gerçek GPT kanıtlı araştırma adayının S1/S2 fiyat doğrulaması ve ücret sonrası kalan avantajı ile karşılaştırılması; bu geçici **heuristic araştırma filtresi** kanıtlanmış yatırım kuralı değildir. GPT eksikse aynı şekilde sonuç yok.
- Referanslar: 100 USD nakit, ilk kaynak M15 kapanış ASK'ından altın al ve değerlendirme sonunda BID ile tasfiye et; her yöne %0,8 ayrı.
- **İşlem simülasyonu:** as-of `t` kararını `t` MID/ASK/BID fiyatından uygulama; yalnız **bir SONRAKİ tamamlanmış M15 barın** kapanış kotasyonunu vekil fiyat olarak kullan. Gerçek banka makası/derinlik/tick erişimi ve fiyat anı doluluk belgelenmediği için yalnız vendor proxy.

## GPT hangi durumlarda inceler?

Her fiyat barında S1/S2 çalışır. GPT inceleme talebi ise **(i) araştırma seansı ilk barı; (ii) yeni kaynaklı ekonomik yayın; (iii) kesintisiz M15 barlar arasında en az %0,5 mutlak fiyat tepkisi; (iv) START/END/REENTRY evresine yeni geçiş** koşullarından en az birinde oluşturulur. Normal her bar yeni GPT çağrısı değildir; evre tetiklerinde en az 4s soğuma. Tetiklerin toplamı Ocak–Şubat gerçek tarihsel koşusunda **156**. Bu sayı gerçekleşmiş GPT çağrısı değil, **AI çağrı adayı** sayısıdır. Şok eşiği çalışma maliyeti için önceden seçilmiş araştırma parametresidir; ekonomiden öğrenilmiş karar eşiği sayılmaz.

## GPT değerlendirmesinin sistem talimatı (kullanılacağı zaman)

> Yalnız `prompt.at` anına kadar `availableAt` olan verileri kullan; bu andan sonraki altın, makro haber, yön ve sonuçları bilme. Tarihsel olay hakkındaki önbilgini kullanarak ileri tarihli gerçek sonuç yazma. Geçmiş ekonomik olay kütüphanesi bir hipotez/kural sözlüğüdür: mekanizmaların adını, önkoşul, aktarım, karşıt kanıt ve geçersizleşme tanımlarını kullanabilirsin, fakat vaka sonucu veya tarihi önceki performans etiketi olarak kullanamazsın. S1 4s UP, S2 hızlı fiyat evresi, slow durum, mevcut CASH/GOLD, işlem maliyeti ve veri kanıtı düzeyini birlikte yorumla. Ekonomik kanıt UNVERIFIED_ARCHIVE ise nedenselliği ve firstprint'i doğrulanmış gösterme. Her zaman ekonomik açıklama adayına karşı bir rakip hipotez oluştur. Kalan hareketin maliyet sonrası avantajı savunulamıyorsa HOLD/ABSTAIN ver, yüzde uydurma. Bir açıklamanın duyurulmamış ISM/CPI/NFP sonuçlarını veya başka zamanlı fiyatı gerekçeye sokma. Yalnızca JSON yanıtı ver.

**Araştırma cevap şeması:**

```json
{
 "asof": "2023-01-06T14:45:00.000Z",
 "action": "HOLD",
 "createdAt": "2026-10-17T19:00:00Z",
 "provenance": "GPT_ARCHIVE_RETROSPECTIVE",
 "responseId": "unique-response-id",
 "reason": "O andaki veri ve fiyat kanıtıyla ekonomik neden/karşıt kanıt ve karar gerekçesi (en az 30 karakter)",
 "mechanisms": ["ORG01", "ORG02"],
 "counterEvidence": ["Henüz doğrulanmamış faiz/dolar çapraz tepkisi"],
 "refEventIds": ["2023-01-06T13:30:00.000Z"],
 "expectedNetAdvantagePct": 0.0
}
```

**Çok önemli:** Bu örnek **GÜNÜN GERÇEK GPT ÇIKTISI değildir**; sadece veri şemasıdır. `asof` içindeki örnek timestamp belirli bir giriş fırsatını ima etmez. Ekonomik veri ilk-yayın kanıtı bulunmadığından `GPT_ARCHIVE_RETROSPECTIVE` olarak etiketlenir. GPT'ye `HOLD` sonucunu zorlamak yasaktır; ama net avantajın dürüst tahmini yoksa gelir için BUY/SELL uydurulmamalıdır. Şemanın zorunlu sayısal `expectedNetAdvantagePct` alanına kanıtlı tahmin yoksa 0 yazılır ve bu ihtiyati yetersizlik işaretidir; gelir iddiası değildir.

**2023 Ocak–Şubat kayıtları ve yazılım arayüzü:**

- `chronological_ai_portfolio_v1.js`: veri önce/sonra sınırı, ekonomik hafıza, olay ilk kullanım zamanı, karar-kayıt bütünlüğü, gelen GPT memo doğrulaması, AI/HİBRİT sanal portföyleri, bir-sonraki-bar BID/ASK + komisyon, bağımsız NAKİT/AL-TUT kıyası.
- `replay_2023_mechanism_ai_shadow_v1.js`: gerçek Neon vendor fiyatlarının 2022 Q4 üzerinde CORE eğitim, Ocak–Şubat 3.750 M15 veri sırayla CORE ve karar motoruna akışı; gerçek GPT JSON dizisi ancak **opsiyonel dördüncü komut satırı dosyası** ile verilebilir. Komut `node replay_2023_mechanism_ai_shadow_v1.js PRIVATE_M15 PRIVATE_SLOW MACRO_CSV GPT_RESPONSES.json`. Boş/eksik GPT girdisi otomatik yapay karar üretmez.
- `.github/workflows/gold-jan-feb2023-ai-mechanism-shadow.yml`: özel veritabanından ham fiyatlar sadece geçici CI çalışma dizinine çekilir; uygulamaya yalnız gün-özetleri commitlenmiştir; tam araştırma çıktısı workflow artifaktıdır.
- `apps/portfolio_guard_v1/model_2023_ai_shadow_view.js`: gerçek CORE sonuçlarını **sunucu yeniden eğitmeden** doğrulayarak salt okunur gösterir; `GET /api/model/2023/jan-feb-ai-shadow`.

## Ocak–Şubat 2023 ilk gerçek çalışma sonucunun kapsamı

Kaynak ve süre: tek EVTradingLabs/Dukascopy türevi 2022 Q4 5.865 M15 fiyat pretraining; Ocak 1.920, Şubat 1.830 M15; toplam 3.750. Modelin 2023 başında 3 fiyat rejim kuralı ve 344 olgun S1 tahmin etiketi bulunur. Matematiksel CORE ve M1 kalite kapısı tam 3.750 kere çağrıldı. İki Ocak ve iki Şubat makro dalgası = **4**, tamamı firstprint-vintage onaysız arşiv araştırması. AI inceleme tetikleri **156**; gerçek GPT yanıtı **0**. GPT arm/hybrid arm **kârlılık sonucu açıklamaya uygun değil**. Matematiksel CORE **0 BUY / 0 SELL, 100 USD CASH**. 3 Ocak ilk seans ASK'ten alıp 28 Şubat son vendor BID ile tasfiye benchmark'ı **98,26375 USD** (iki yön %0,8 varsayımı dâhil); kullanıcı bankasında gerçekleştirilmiş net bakiye değil. **AI entegrasyonu ve ekonomik ORG deneyi henüz bilimsel olarak TAMAMLANMADI**.

**Üç ayrı başarı tanımı:**

1. Mühendislik: kaynağı korunmuş tam kronolojik M15 veri akışı, 2022 Q4 öğrenim hafızası, olay tetikleme, ücretli gölge işlem motoru, ekran/REST API ve kaynağı doğrulama testleri.
2. Araştırma: gerçekten üretilmiş GPT `responseId`, sağladığı özgün gerekçe ve karşıt kanıt, as-of input hash, ayrı AI/HİBRİT geriye dönük portföy sonuçları; **henüz yok**.
3. Bilimsel kabul: P0→P5 ekonomik mekanizma ve ilk-yayın gerçek PIT, bağımsız negatif kontrol, önceden dondurulmuş politika ve ayrı out-of-sample başarısı; **FAIL**.

Bu sözleşme, ne geçmiş olayları AI'nın o gün bildiğini varsayar ne de AI cevaplamadığı hâlde sentetik AL/SAT ve kârlılık yaratır.
