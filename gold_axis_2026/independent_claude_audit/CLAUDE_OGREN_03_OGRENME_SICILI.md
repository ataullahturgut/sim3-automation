# CLAUDE ÖĞREN — Ortak öğrenme ve karar hipotezleri sicili (Claude'un bağımsız sicili)

**Temel belgeler (yalnız okunur):** [ANA-01](../GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md) amaç ve kurallar · [OLAY-02](../OLAY_02_ENTEGRE_OLAY_VAKA_KUTUPHANESI.md) olay kimlikleri. Claude olay kayıtları: [CLAUDE_OLAY_KAYITLARI_2023_01_02.md](CLAUDE_OLAY_KAYITLARI_2023_01_02.md).
**ChatGPT'nin ÖĞREN-03 sicili** ([dosya](../adaptive_volatility_learning/EVENT_CAUSAL_ACTION_HYPOTHESIS_REGISTER_20261014.md)) **değiştirilmez**; karşılık gelen hipotezler aşağıda yalnız referans olarak gösterilir.
**Makine-okunur sürüm:** [CLAUDE_OGREN_03_OGRENME_SICILI.json](CLAUDE_OGREN_03_OGRENME_SICILI.json).
**Statü:** `RESEARCH_ONLY / HINDSIGHT_EXPOSED / NO_PROMOTION`. Hiçbir hipotez otomatik banka emri değildir.

## Kanıt seviyeleri (ANA-01 ile aynı)
L0 fiyat olayı · L1 tarihli haberle uyumlu açıklama · L2 resmî saat + eşsaatli fiyat tepkisi · L3 benzer/karşıt kontrol vakaları ve alternatif mekanizmalarla karşılaştırma · L4 bağımsız ileri test ve maliyetli karar performansı.

---

## A. Karar hipotezleri

| ID | Hipotez (koşul → aksiyon) | Destekleyen olaylar | Karşıt kanıt | Seviye | Durum |
|---|---|---|---|---|---|
| **C-H01** | Yükseliş rejiminde **tek seferlik / ikincil** hawkish veriyle altın düşer → altındaysan **KAL** (satıp geri almak maliyeti karşılamaz) | `MACRO_2023_01_05_ADP`; Kip B: 2020–22'de n=8, ek düşüş ort. −%0,85, 1/8 maliyeti aştı | Faiz kanalı aynı saatte teyitliydi (ZN −0,52) yine de tersine döndü → teyit tek başına satış gerekçesi değil | L2–L3 | Tek 2023 vakası + 2020–22 taban oranı. ChatGPT H-HOLD01 ile aynı yön |
| **C-H02** | Yükseliş rejiminde **dovish sürpriz** + altın ilk 15dk ≥ +%0,4 + gümüş aynı yönde → nakitteysen **AL**, altındaysan **KAL** | `MACRO_2023_01_06_NFP`, `US_CPI_2023_01_12`; Kip B: 2022-11-10, 2022-12-13 CPI | Sınıfta 3/11 maliyeti aşan ters dönüş; 10 seans ort. yalnız +%0,33 | L2 | ChatGPT H-UP01 ile aynı dakika AL |
| **C-H03** *(yeni)* | **Duraklama** (yükselişten sonra ≥5 seans yatay; mom10 belirgin düşer, trend20 erir) **+ şok + günlük rejim dönüşü + gümüş teyidi + düşüş faizle açıklanmıyor** → altındaysan **SAT** (haberi beklemeden) | `REGIME_FLIP_2023_02_02` (3 Şub 09:00 TRT SAT) | Koşulsuz rejim dönüşü taban oranı ~0 (2020–22, n=56); dönüş marjı yalnız −%0,08; tek uygulama | L1–L2 | **Kontrol:** aynı kural 5, 19, 27, 31 Ocak düşüşlerinde SAT demedi (rejim dönmedi). Koşullu sürüm hiç bağımsız test edilmedi |
| **C-H04** | **Fed yolunu değiştiren** büyük sürpriz (konsensüsün çok üstü, önceki anlatıyı yalanlayan) + altın sert düşüş → altındaysan **SAT**, nakitteysen **KAL** | `MACRO_2023_02_03_NFP`; Kip B: 2022-09-13 CPI, 2021-06-16 FOMC | DOWN rejiminde hawkish düşüşler ort. yatay/geri alındı (n=7); Kip A: 2024-06-07 NFP sonrası +%7,7 | L2–L3 | ChatGPT H-DN01 ile aynı yön; C-H03 ile birlikte daha erken çıkış |
| **C-H05** | **Sürprizsiz veri** günlerinde, rejim dönmeden gelen düzeltme → **KAL** | `EPISODE_2023_01_26_31_CORRECTION`: kâhin bile en fazla +0,74 $ | — | L2 | Maliyet tarafı güçlü; yön tarafı hipotez |
| **C-H06** | Rejim DOWN iken **ardışık hawkish veri dizisi** → nakitteysen **geri girme**; giriş için dovish katalizör + rejim düzelmesi birlikte gerekir | `EPISODE_2023_02_06_28_HAWKISH_SEQUENCE` | Şubat sonunda tepkiler küçüldü (PCE 3 seansta +%0,56) — dipte geç kalma riski | L1–L2 | Geri giriş kuralı test edilmedi |
| **C-H07** | Büyük planlı açıklamadan (NFP/CPI/FOMC) **önce** maliyetli pozisyon açma; sonucu bekle | 3–5 Oca BEKLE; 31 Oca–1 Şub KAL | 2022'de UP rejimdeki hawkish NFP'ler düşürdü; Ocak 2023'te bekleme sonucu değiştirmedi | L1 | Davranış kuralı; getiri katkısı ölçülmedi |

## B. Olumsuz bulgular (yanlışlanan / zayıflayan fikirler)

| ID | Bulgu | Kanıt |
|---|---|---|
| **C-N01** | Tek veri sinyalleri (trend, momentum, gümüş, faiz, analog, GVZ) **tek başına** 10 seans yönünü bilmiyor | AES 2021–22: modül isabetleri %45–57; [sonuç](CLAUDE_ADAPTIVE_EVIDENCE_SYSTEM_RESULTS.md) |
| **C-N02** | Mekanik rejim/şok kuralları %0,8+%0,8 maliyetle kaybettirir | 2020–22: 100 $ → 59–73 $; [protokol](CLAUDE_RESEARCH_PROTOCOL.md) |
| **C-N03** | “Faiz piyasası teyit ediyorsa şok kalıcıdır” | 5 Oca: teyitli, 24 saatte döndü |
| **C-N04** | “Altın düşüşü faiz kanalından gelir” | 2 Şub: altın −%1,46 (4s) iken ZN +0,42, NQ +1,74 |
| **C-N05** | “Güçlü NFP ⇒ altın düşer” (deterministik) | 6 Oca güçlü NFP'de altın yükseldi; 2023-03-10 karşı vaka |
| **C-N06** | “1dk kovalamama kapısı her sinyalde yararlı” | Yavaş günlük sinyali 4 denemede reddetti, satış düştü |
| **C-N07** | Kalibre edilmiş olasılık farkı ≥0,25 eşiği bu veriyle neredeyse hiç geçilmiyor; 2023'ün en güçlü AL işareti 2 Şub düşüşünden hemen önceydi | AES ledger_2023 |

## C. Açık sorular / sonraki testler
1. **C-H03'ün bağımsız testi:** Koşullar (duraklama tanımı, rejim dönüşü, gümüş teyidi, faiz ayrışması) **şimdi** sabitlenip Mart 2023 – Aralık 2024'te tek seferlik ve gün gün sınanmalı. Ölçüt: tetiklenen satışlar sonrası 10 seans kalan düşüş > %1,62 oranı; yanlış satış ve geri alım maliyeti.
2. **Dolar verisi:** C-H03 ve C-N04 dolar kanalına dayanıyor; gün içi DXY/EURUSD olmadan L2'nin üstüne çıkamaz.
3. **Olay kütüphanesi genişletme:** ISM, PCE, PPI, perakende, ADP ilk yayın + konsensüs arşivi (şu an yalnız NFP/CPI/FOMC sayısal).
4. **Geri giriş kuralı (C-H06):** Hiç test edilmedi.

## D. Güncelleme fişi (ANA-01 / Belge haritası şablonu)
- **Okunan:** ANA-01, OLAY-02, ChatGPT ÖĞREN-03 sicili ve Ocak STATE.json (değiştirilmedi).
- **Değiştirilen:** yalnız `gold_axis_2026/independent_claude_audit/` altındaki Claude dosyaları.
- **Çıkarım:** C-H01…C-H07, C-N01…C-N07.
- **Değiştirilmeyen:** tarihsel arşiv, ChatGPT dosyaları, OLAY-02, ÖĞREN-03.
- **GitHub:** dal `research-gold-claude-independent-audit-20261014`.
