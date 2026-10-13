# GOLD INTRAMONTH — Kurumsal Manifest Denetimi ve Otorite Yönetimi
**Denetim tarihi:** 2026-10-13 · **Durum:** Araştırma dalı / değişiklik incelemesinde · **Kapsam:** Gold intramonth ana manifest, yaklaşık 4.9 bin satır. **Otorite:** Bu belge mevcut bilimsel sonuçları değiştirmez; proje belgelerinin okunma ve onay iş akışını yönetir. **Üretim/lisans:** Hiçbir otomatik banka emri veya canlı model geçişi yapılmadı.

## 1. Yönetici karar özeti
- Mevcut manifestte güçlü bir **deney izi ve kanıt saklama** düzeni var: numaralı R çalışmaları, GitHub PR'ları, tarihli metodoloji/sonuç kayıtları, kaynak ve leakage uyarıları. Fakat tek bir **güncel yönetici özeti, rol bazlı otorite haritası ve değişiklik hiyerarşisi** yoktu. Yaklaşık 4.9 bin satır ve farklı tarihlerde yazılmış "current/next/binding" emirleri, operasyonel otorite çakışması doğurabiliyordu.
- Düzeltme: ANA BELGE BAŞINDA **governance index** ve her araştırma hattı için kapsam/otorite/kanıt-düzeyi ayrımı; 2026-10-07 tarihli session görev notlarını artık bugünkü görev gibi göstermeme; tarihsel #10 hiyerarşiden sonra gelen bölümleri açıkça **11. ekler/kısmi bağlayıcı veri düzeltmeleri** diye sınıflandırma. Tarihsel sayısal kayıtlar korunur.
- Araştırma dalı ve ana depo karıştırılamaz. V4 `PR #128` **OPEN/UNMERGED** ve önceki #127/#126/#125 üzerine yığılmıştır; ilk Ocak günlük defteri `#123` ayrı açık PR'dır. Bu belge **yalnız araştırma önerisidir**; ana üretim/strateji otoritesi değişmez. PR'ların merge sırası ve çatışmaları ayrıca gözden geçirilmeden otomatik birleştime YOK.

## 2. Tek otorite yerine alan-bazlı otorite matrisi
| Hat / hedef | Yetkili veri / karar temeli | As-of durum | Üretim onayı |
|---|---|---|---|
| **Aylık** H=1 altın ay ortalaması | Ayrı `GOLD_MONTHLY_PROJECT_MANIFEST.md`; aylık tahminin bilgi sınırı önceki ay sonu | Ayrı proje, bu manifest ona üst otorite değil | Değişmedi |
| **K100/MFE/MAE intramonth** 5 BIST gözlem yolu | Orijinal Stage0–5 sözleşmeleri ve sonuç dosyaları, bu manifestin tarihsel #1–#8 temeli | Korunan **paralel** geçmiş araştırma | Bu belge canlı sinyal vermez |
| **DAILY/CIG ve H3 D0→D3** | Orijinal günlük-etiket ve H3 kaynak/issue saat yetkileri, R60 kaynak tarih QC | Günlük %74.40 eski karma-vintage tanı, daha yeni kaynakta 88/125=%70.40; H3 orijinal hedefi üç gelecekteki kaynak günü günlük ortalaması. Bu doğrulukların hiçbiri banka getirisi değil | Eski sinyaller doğrudan işlem yetkisi değil |
| **WGC/Sobti SESSION V5** | 2026-10-07 source/clock/target repair ve model kimlikleri; #0.0/#0.1 geçmiş snapshot | Ayrı session fiyat aralığı araştırması; final Türkiye banka-window etiketi değildir | No new router/consensus approval |
| **Türkiye banka-hour DAY/OVN** | R65–R70 09:00/15:00/16:45, 09→16:45 & 16:45→sonraki uygun09; gerçek quote yok | Güncel yürütme-uyumlu **araştırma**. Aynı saatli P&L'ler hipotetiktir; R70 2026 olumlu tek varyant yıllar boyunca taşınmadı | **NOT PROMOTED** |
| **Ocak2026 risk S4→V4** | PR#123, #125, #126, #127, #128; V4 test protokolü, JSON ve bilimsel hüküm | 2026 Ocak önceki bilgiye maruz retrospektif; 2024 olay kapsaması 0/12 | **REJECTED / REVIEW ONLY** |
| **2023–25 fiyat-olay atlası** | 13 Ekim V2/V3/V4 tarihli olay raporları ve kontroller | Fiyat gözlem/kısmi haber bağlamı; kesin ekonomik nedensellik veya gelecek alarmı değil | **NO MODEL** |

**Doküman önceliği:** (1) kaynak/etiket/available-as-of/clock QA sözleşmesi, (2) ilgili deneyin önce imzalanmış frozen protokolü, (3) kanıtlanmış çıktı JSON+aynı kohort skor defteri, (4) bilimsel sonuç/hüküm, (5) ana manifestin özeti. Eski dosyalar silinmez. Yeni rapor, önceki sonucu **yalnız belirtilen kapsam ve kaynağa göre** supersede edebilir. "BINDING" sözcüğü tarihsiz global emir değil, **sadece o veri/target/metot sözleşmesi** için bağlayıcıdır.

## 3. Denetim bulguları ve düzeltme statüsü
| Kod | Tespit | Düzeltme | Statü |
|---|---|---|---|
| GOV-01 | 236 başlık / çok sayıda tarihli üst not ile yönetici girişinin olmaması | Ön sayfa otorite özeti, hat navigasyonu ve bu denetim dosyası | **DÜZELTİLDİ** |
| GOV-02 | #0.0, #0.1, #1.3, #9 ve Model-02 bölümünde 2026-10-07 "current next action" ifadeleri, R65–R70 sonrası **eski** | Açık "tarihi snapshot, bugünkü görev değildir" çerçevesi | **DÜZELTİLDİ** |
| GOV-03 | #1 5-BIST-gün K100 orijinal amacı, bugünkü DAY/OVN al-sat hedefiyle karışabilir | #1 yalnız tarihsel K100 hattı; banka-DAY/OVN başka karar/etiket | **DÜZELTİLDİ** |
| GOV-04 | #10 Document Hierarchy'den sonra yeni BINDING veri düzeltmelerinin eklenmesi belgenin yanlış bittiği izlenimini veriyor | #10 "historical baseline", arkasına #11 "dated evidence and scoped corrections" sınırı | **DÜZELTİLDİ** |
| GOV-05 | V1–V4 sonuçları farklı fiyat saati/uygulama ve maliyetlerden geldiği halde yalın yüzdeler karşılaştırılabilir görülebilir | Aynı kohort, saat, kaynak, masraf ve giriş/çıkış bazında karşılaştırma mecburiyeti | **KURAL SABİTLENDİ** |
| GOV-06 | #128 branch "canonical" başlıklı dosya taşıyor fakat henüz main/aktif yürütme sistemine merge edilmedi | Üst yazıda açık OPEN PR, NO PRODUCTION, PR bağımlılık zinciri | **DÜZELTİLDİ — merge bekler** |
| GOV-07 | V4 Jan29+%23.99 kesiti başarı gibi genellenebilir | 2024 0/12 eksik kapsama ve 2025 n=2; test gate başarısız, selection/ex-post uyarısı | **MODEL REJECTED** |
| GOV-08 | EV2023–25 / HIST Jan2026 araştırma spot fiyatları ve gerçek Türk bankası kotasyonu ayrı | Banka BID/ASK, işlem anı, spread, masraf, fill eksikleri açık; net banka kârı iddiası yok | **VERİ KAPISI AÇIK/UNVERIFIED** |
| GOV-09 | V4 kendi çift-alarm/half-recovery kodu farklı bağımsız uygulama ile birebir yeniden koşulmadı | Önceki S4 12/12 parity var; **yeni strateji tam bağımsız hesap testi henüz yok** | **OPEN** |
| GOV-10 | **Farklı maliyet sözleşmesi:** R70 25 baz puan varsayımsal **toplam tur** maliyeti; V4 her yönde **%0.8** ücret + ayrıca her yönde **%0.15** aleyhte spot–kotasyon farkı; ayrıca hedef ve test pencereleri farklı | Bankada gerçek kullanıcının %0.8 alış / %0.8 satış kuralını ayrı varsayımsal stresle uygula; R70 ve V4 skorlarını aynı-maliyetli gibi karşılaştırma | **BLOK / yeni eş-maliyetli test gerekir** |
| GOV-11 | GitHub deposunun erişim seviyesi sorguda **public** göründü | Özel Neon erişimi/kimlik bilgileri, API anahtarları, lisanslı veya gizli ham fiyatlar ve hesap verileri bu açık kayıt deposuna asla eklenmemeli; repo gizliliği hakkında ayrı yetkili karar gerekli | **GİZLİLİK KONTROLÜ AÇIK** |

## 4. İş akışı: durum makinesi ve go/no-go
1. **INVENTORY:** Her model için tek `study_id`, `target_id`, `origin_clock`, `horizon`, `feature_vintage`, `source_snapshot`, `cohort`, `code_commit`, `protocol_path`, `results_path`, `run_id`, `status`, `owner_review` kayıt alanları gereklidir. Verilmeyen alanı tahmin etme, UNKNOWN yaz.
2. **DATA_GATE:** Veri sağlayıcı adı ve quote tipi (BID/ASK/MID/spot), zaman damgası dönüşümü, DST, market takvimi, ilk erişilebilir kaynak tarihi ve gün içi OHLC sıra güvenilirliği. Eksikse hedef sonucu yalnız RETROSPECTIVE RESEARCH.
3. **FREEZE:** Yöntem, eşik, karar anı, ilk işlem fiyatı, masraf formülü, re-entry politikası, negatif kontrol, **yanlış-alarm / kaçan-olay** kapısı sonuç görülmeden önce commit edilir. Önceden görülen dönem başka kohort olarak kıymetlendirilemez.
4. **EXECUTE/REPRODUCE:** Aynı kod/yıl/dönemle kaynak tablosundan deterministik yeniden üretim; yalnız S4 baseline parity yetmez, V4 FULL/HALF da bağımsız yazılım/çıktı kontrolüne ihtiyaç duyar. Gerçek işlemi temsil etmeyen market spot ölçümü banka icrası olarak etiketlenemez.
5. **SCORE:** Direction accuracy, recall ve precision; sert hareket alarmında event recall/FNR ve false-SAT, zaman gecikmesi, max DD, maliyet-dahil NAV, opportunity cost, eş tarihli passive GOLD/CASH kıyası, yeterli örnek sayısı, kohort kayması ayrı alanlar.
6. **REVIEW:** Araştırma başlığı `IDEA→FROZEN→RAN→REVIEW→REJECTED/RESEARCH-ONLY`. Sadece bağımsız kaynak/OOS/PIT/quote uygun olduğunda ve ilan edilmiş eşikler geçildiğinde `CANDIDATE_APPROVED` tartışılır; otomatik `LIVE` geçişi yok.
7. **CHANGE CONTROL:** Mevcut sonuçlar immutable; düzeltme ayrı addendum ve hangi satırı niçin supersede ettiğini yaz. PR üzerine yeni bağımlı PR açılmışsa önceki zincirin sırasını incele, baz SHA drift / merge çatışmasını denetle. Kullanıcı onayı olmadan main'e/production'a merge veya gerçek bankada emir YOK.

## 5. 29–30 Ocak V4 için kontrollü neden–sonuç tanısı
- **Gözlem:** 29 Ocak 16:30TR strict bar ordering intraday drawdown **−2.2292%**; A **6.83729** >2022/23 eşiği **5.676818**; T **4.59664** > **2.980590**; S4 r60 **+38.55%**, yani S4 TUT iken V4 SAT. 16:45 tarihi spot quote + %0.8 komisyon/yön + %0.15 adverse quote/yön ile Ocak net S4 **+13.035%**, FULL **+23.988%**; koşullu fark **+10.953 pp**.
- **Mekanik hata kökü:** eski NY17 close-only örnekleme, 29 Ocak gün içi yolu dikkate almıyordu ve emir zamanı banka saatine uymuyordu. V3'ün tekil risk değişkenleri 2024/25'te false exits yarattı. V4 AND kuralı bunları seyrekleştirdi, fakat 2024'te **12** büyük ertesi-bank-gün low düşüşünün **0**'ı yakalandı.
- **Kanıt olmayan anlatı:** 30 Ocak hareketini FED, Warsh, jeopolitik gelişme, fon akışı veya diğer metal ilişkilerinin *nedensel olarak oluşturduğunu* bu iki fiyat skoru ispat etmez; A ve T birbirinden bağımsız piyasa gözlemleri değil. V4 AND fikri Jan29 gözlenmiş olduktan sonra seçilmiş, Ocak blind OOS değildir.
- **Karar:** V4 tam/yarım SAT, ilan edilmiş 2024+2025 geçiş koşullarını karşılamıyor; ayrı bağımsız yeni dönem, eksik 2024 yakalama gücü, gerçek banka BID/ASK ve alternatif veri mekanizması çözülmeden işlem modeli olmaz.

## 6. Bakım ve inceleme kuralları
- Bir çalışma bittiğinde **üst yönetici özeti + alan kayıt tablosu** güncellenir. Binlerce satırlık tarihli bulgu eklemek yerine her deney ayrı rapora bağlanır; manifestte tek paragraf/sonuç/karar ve kanıt linki bulunur.
- Öncelik kaynak ve kronoloji, sonra model, sonra karar/işlem; açıklanacak getiri aynı yıl/saat/kaynak/bilet/maliyet olmadan farklı satırdaki yüzdelerle kıyaslanmaz.
- Hiçbir açık PR dahi, tek başına kanıt seviyesini veya ana üretim sistemi kararını değiştiremez. Tarihsel negatif sonuçları korumak zorunludur.
- Sonraki meşru bilimsel hedef, **2024 kaçırılmış olaylar** ve **2025 yanlış-çıkış maliyetleri** için başlangıç-bitiş zaman damgalı, origin-safe piyasa sinyali araştırmasıdır; önce test planı, sonra hiç görülmemiş dış dönem/ileri-kayıt.

**Kanıt yolları:** `GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md`, `GOLD_JAN2026_V4_DUAL_FACTOR_31DAY_SCIENTIFIC_VERDICT_20261013.md`, `GOLD_JAN2026_V4_DUAL_FACTOR_FROZEN_PROTOCOL_20261013.md`, `GOLD_JAN2026_V4_DUAL_FACTOR_RETEST_RESULTS_20261013.json` ve ilgili PR#123/#125/#126/#127/#128.


## 7. Kalıcı belge sırası — GENEL ARAŞTIRMA ÖNCE, OCAK ÖZEL VAKASI EN SON (2026-10-13)

**Kullanıcı talimatı:** Genel tarihsel ve bilimsel araştırmalar **önce**; daha sonra veri/clock, model ve bankacılık uygulanabilirlik denetimleri; **Ocak 2026 B0/S4/V2/V3/V4 çalışması manifestin fiziksel son bölümünde** yer alacak. En son yapılan deney, en yüksek yetki veya en temsilî çalışma anlamına gelmez.

- **Ana manifest `0`**: tek güncel durum ve kaynak/alan yetki sınırları (aylık ayrı, H3 ayrı, banka icrası ayrı).
- **Ana manifest `0.1`**: tarihsel/genel araştırmanın okunabilir sentezi: tarihsel rejim, 42 ZigZag, 174 gün/53 küme, 24 normalize küme, 13 başlangıç/9 vaka, ETF/CFTC/opsiyon/likidite, makro sürpriz zamanları, H3 dönüş hata kök nedenleri, veri QA ve banka maliyetleri.
- **Ana manifest `0.2`**: 291 kayıt/39 alanı içeren bağımsız `GOLD_HISTORICAL_EVENT_MASTER_CROSSWALK_V1_20261013.csv` ve `...AUTHORITY_20261013.md` giriş otoritesi. Kayıt adetleri ekonomik olay sayısı değildir; timestamp/firstprint/öncü özellik ve farklı hedef/clock eşleştirme kalite kapısı zorunludur.
- **Sonraki genel arşiv**: olay atlası V2 → V3 → V4 sırayla, sonra R70→R serisi, eski K100, SESSION ve 2020–2025 veri/ücret/horizon araştırma evrimi. Eski sayısal çıktılar yazıldıkları tarih/sürüm bağlamında tutulur; negatif raporlar silinmez.
- **Ana manifest son `# 12`**: Ocak 2026 kilitli günlük defter B0, Stage A/B/C, V2/V3/V4 ve bağımsız olmayan eski döneme ait tüm nedensellik/karşıolgusal bulgular. Ocak araştırması ayrı PR zincirindedir, 2024 kapsamı başarısız ve genel model seçimi otoritesi değildir.
- **Değişiklik kontrolü:** Yeni genel olay veya yeni veri kalitesi araştırmasını `# 12` içine yazma. Yeni Ocak ayrıntısını yalnız `# 12` içine ve kanıt raporuna koy; herhangi bir yeni genel araştırma `# 12`'nin **öncesine** eklenmeli. Diğer dönemler `# 12` içindeki araştırma sonrası başka konu eklenecek şekilde yazılmaz. Fiziksel yerleşim ile veri kronolojisi farklıdır; 2026 Ocak asla geleceği görmeyen holdout sayılmaz.
- **Kontrol listesi:** İlk 0.1 ve 0.2, 2023–25 tarihli olay V2/V3/V4'ten önce; bu bloklar Ocak son ekinden önce; `# 12` en son üst-seviye başlık; kapanış `END GOLD_JAN2026_EXPOST_FAILURE_AND_SCIENTIFIC_RESEARCH_GATE_20261013` işareti dosya sonu. Bu kontrol otomatik doğrulanmalı; ayırıcı yazılarının değiştirilmesi ayrıca bakım denetimi ister.

**As-of durum:** Ana manifest bu yapıya taşındı; yalnız biçim, dizin ve anlatım/sıra değişti, önceki deneylerin model/sonuç/CSV/JSON kanıt değerleri değiştirilmedi. Kurumsal sıralama araştırma modelini veya geriye dönük Ocak skorlarını onaylamaz.
