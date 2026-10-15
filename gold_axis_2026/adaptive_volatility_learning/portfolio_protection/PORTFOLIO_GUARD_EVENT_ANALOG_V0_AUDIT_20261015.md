# MARJİNAL HAREKET PORTFÖY KORUMASI — OLAY-ÖĞRENME ANALOG V0
**Durum:** `RESEARCH_ONLY_NOT_VALIDATED` · **Tarih:** 2026-10-15
**Kaynak otoritesi:** ANA-01 / OLAY-02 / ÖĞREN-03; bu belge eskilerinin yerine geçmez.
**Kapsam:** Yalnız büyük DOWN/UP hareketlerinde pozisyon koruması; günlük yön ticareti hedef değildir.

## 1. Kullanıcının hedefi ve temel tercih
Normal koşulda aylık ana görünüm GOLD ise altın taşınır. Sırf ufak düşüş için banka ücreti ödenmez.
Bir DOWN olayı beklenen **kalan** hareket itibarıyla satış + tekrar alış maliyetini aşabilecekse koruma düşünülebilir.
CASH konumunda iken büyük UP fırsatları ayrıca ele alınır. Bu V0 testinin deney başlangıç durumu GOLD'dur;
dolayısıyla CASH başlangıcının tam kapsamlı sınavı yapılmamıştır.
AL ve SAT tarafı ayrı ayrı %0,8; ek banka makası/slippage **eksik**.

## 2. Gerçek olay öğrenimi ne kadar tamamlandı?
Kaynak: `OLAY_02_96_TUM_VAKA_EVRENSEL_ORUNTU_MATRIKS_20261015.csv`.
- 96 arşiv vakası (2023–2025), 93 tanesinde yeterli as-of XAU özellikleri.
- Bunların yalnız 17'sinde ORG01–ORG12 aday sınıf eşleştirmesi; kalan 76'sı doğrudan ORG eşleştirilmemiş.
- **96/96 olayın ilk haber yayın saati doğrulanmamış; 96/96'nın ekonomik nedenselliği doğrulanmamış.**
- Olay başlangıcı **kanıtlanmış** kabul edilmedi. `candidate_DNA`, `org_plot_candidate` yalnız tarihsel vaka metadatasıdır.
- Arşivden ekonomik olay nedeni değil, **fiyat-morfoloji ve çapraz piyasa benzerliği** öğrenilebilir.
- 93 olayın karar kesitini izleyen 96 takvim saatindeki gerçek fiyat alt/üstü ham Neon M15'ten tekrar ölçüldü:
  - en az %3 aşağı uzama: 18 / 93;
  - en az %5 aşağı uzama: 2 / 93.
  Bu 93 vaka **ex-post seçilmiş** olduğu için oranlar evrensel olay olasılığı DEĞİLDİR.
- Öğren-03 grupları G01 makro, G02 politika, G03 jeopolitik, G04 akış, G05 finansal stres, G06 pozisyon ve G07 belirsizlik ayrımı korunur. ORG08/ORG12 dahil ekonomik aileye fiyat hareketinden nedensel isim *atanmaz*.

## 3. As-of karar soruları
1. `MARKET_PHASE`: Son 4 saatlik altın hareketi, düşüşün başlangıcı/devamı veya toparlanma adayı mı?
2. `CROSS_MARKET`: XAU'da son 16 tam M15 getirisi <= -%1, NQ'da geçmiş 6 tamamlanmış H1 fiyat barı getirisi <= -%1 mi? 
3. `ARCHIVED_CASE_ANALOG`: 2023–2025 arşivinin as-of fiyat profillerinden en yakın dokuz vaka hangileri; onların **ayrı ölçülen** 96 saatlik gerçek aşağı uzaması <= -%3 mü?
4. `NOVELTY`: Gözlenen şok geçmiş benzerlerden çok uzaksa model düşük öğrenilmiş risk puanına güvenmemeli mi?
5. `NEWS_CLOCK`: Güncel kanıtlı firstprint ve rakip ekonomik kanal doğrulanmış mı? (V0: HAYIR/UNRESOLVED.)
6. `COST_AND_POSITION`: Kaçınılabilir gelecek düşüşün, banka satış/alış bedelini ve olası yeniden giriş fırsat kaybını aşması mantıklı mı?
7. `REENTRY`: Bekleme sonrası 92 bar getirisi >= +%2 ve 276 bar getirisi >= +%0,5 ile toparlanma var mı?

`ARCHIVED_CASE_ANALOG`: 8 boyutlu ağırlıklı normalize uzaklık (4h log getiri, RV4h,
aşağı yönlü varyans payı, yol verimliliği, kapanışın aralıktaki konumu,
4h tepe farkı, NQ H1, ZN H1), k=9 ve ters kare mesafe ağırlığı.
Skor kalibre edilmiş bir risk olasılığı DEĞİLDİR.

### V0 alarm kapısı
```
COSELL := XAU 16-bar return <= -1% AND NQ 6-completed-H1 return <= -1%
ANALOG_RISK := weighted proportion of 9 analogs with next-96h low <= -3%
NOVELTY := nearest standardized distance >= 1.0 AND realized-vol4h >= 0.8%
PROTECT := COSELL AND (ANALOG_RISK >= 0.20 OR NOVELTY)
REENTER := >= 72h after exit AND XAU 92-bar return >= 2% AND XAU 276-bar return >= 0.5%
```
Exit/reentry share=100% only to *compare* with the previous price-only research, **not** a live recommendation.
Thresholds are post-hoc research candidates; calendar-locked blind validation has NOT occurred.
OHLC 15m used for features; fills modeled using next 15m opening price.
No future-derived attributes enter a decision. Future 96h low is used only to label fully historical archive.

## 4. Aynı kaynak ve checkpoint evreninde sonuç
2025 değerlendirmesi için yalnız 2023–2024 prototipleri (53 tarihli arşiv kesiti).
2026 değerlendirmesi için yalnız 2023–2025 prototipleri (93 kesit).
Hesaplama evreni sırasıyla **2000** ve **1511** uygun M15-temelli 3 saatlik checkpoint;
kaynak zamanı ve kalite kapısı değişince daha önceki başka örneklemli sayılarla bire bir kıyaslanmaz.

| Metot | 2025 net | 2025 azami DD | 2026 Ocak–Eyl net | 2026 azami DD | 2026 savunma satışı |
|---|---:|---:|---:|---:|---:|
| Altını sürekli taşımak | +%61,102 | %10,98 | -%5,943 | %28,64 | 0 |
| XAU + NQ basit ortak satış alarmı | +%49,511 | %10,98 | +%3,055 | %24,91 | 9 |
| **Olay analog + bilinmeyen aşırı şok** | **+%51,447** | **%10,98** | **-%5,473** | **%28,45** | **3** |

- 2026 hibrit V0 büyük şok olan **29 Ocak 2026 21:00 TSİ**'de savunmaya geçebildi. 
- Buna karşın sonraki aylardaki bazı büyük düşüşleri kaçırdı; risk puanı fazlasıyla düşük kaldı.
- 2025 analog filtresi iki koruma satışına izin verdi, baz fiyat+NQ alarmı üç satış yaptı.
- Yüksek güvenle `G05` ya da `ORG12` ekonomik şok nedeni atamak **yanlış** olur.
- Modelin azami DD iyileşmesi 2026'da pasif altına göre yalnızca **0,19 yüzde puan**; kabul için yetersiz.
- Masraf %0,8 alış ve %0,8 satış varsayıldı; ilave gerçek banka BID/ASK makası yok.
- Daha önce araştırmacı tarafından görülmüş 2026 örnekleri burada tam kör OOS değildir.

## 5. Neden bilimsel olarak kabul edilmedi?
1. **Event-base enrichment bias:** Tüm arşiv ex-post olay seçilmiş. Sakin/ters/olaysız karşı vakalarla gerçek risk tabanı henüz kalibre edilmedi.
2. **OOD / rejim:** 2026 sert kırılmaları arşivden çok uzak, kNN puanı sahte güven üretebiliyor. 
3. **Attribution gap:** İlgili ORG/DNA mekanizmasının as-of makro firstprint + US 2Y/USD/SI ile teyidi yok.
4. **Censoring:** Son Eylül sinyallerinde tam ileri 96 saat gözlem ufku gerekebilir; eğitimde kullanılamaz.
5. **Maliyet:** Gerçek Türkiye banka makası, emir saati, slippage ve geri giriş uygulaması sınanmadı.
6. **Multiple comparisons:** Fiyat/NQ eşiği ve analog/novelty kombinasyonları tarihsel sonuç görüldükten sonra önerildi; kilitli ileri test yok.

## 6. Sonraki deneyin bağlayıcı araştırma sırası
A) OLAY-02'nin 96 tarihi vakasında source-firstprint, consensus vintage, tamamlanmış zaman damgalı USD/2Y/SI/ZN/NQ ve karşıt haber teyidini çıkar; `VERIFIED/UNRESOLVED` ayrımı zorunlu.
B) Her vaka yanında zaman açısından eşleştirilmiş **olaysız karşı kontrol** oluştur, olay kütüphanesi seçilim yanlılığını ölç.
C) Öğrenilmiş öncül risk dağılımını event vs no-event olasılığıyla kalibre et (episod bazlı purged/embargo zaman splits).
D) 3%/5% ve 24/48/96 saat bariyerleri için olay bazlı precision/recall, yanlış alarm, gecikme, kaçırılan düşüşün büyüklüğü, gerçekte önlenebilir kayıp ve kaçan yükseliş ölç.
E) Hareket OOD ise sebep bildiğini iddia etme: `UNKNOWN_SHOCK` ayrı işleme adaydır; ilk gerçek veriyle sınıflandırmayı güncelle.
F) Banka maliyeti ve mevcut GOLD/CASH durumuna göre TUT öncelikli karar eşiği hesapla. Dondurulmamış 2026 üzerinden skorla model seçme.
G) Ancak üstteki kanıtlar tamamlandığında 15 dakikalık gerçek karar döngüsüne geç; şu anki 3h V0 modeli otomatik karar için yasak.

## 7. Çalıştırılabilir araştırma kodu
`portfolio_protection/event_analog_portfolio_guard_v0.py` çalışma motorunu içerir.
Girdiler üç CSV: orijinal OLAY-02 vaka matrisi, aynı 96 vaka için M15'ten türetilmiş
`case_id,low96,high96,ct` sonuç tablosu, tamamlanmış M15 ve H1'den
üretilmiş `tt,p,c,r4,r1,r3,rv,ds,eff,loc,dd,nq1,nq6,zn1` checkpoint paneli.
Bu iki türetilmiş CSV, aşağıdaki değişmez as-of veri hazırlama sözleşmesine göre üretilmelidir:
- Archive case anchor `checkpoint_utc`'den **önceki** tamamlanmış XAU M15 close fiyatı.
- Anchor'dan sonraki `[anchor, anchor+96h)` M15 low/high; sonuç tablosu yalnız tarihsel hedef üretir.
- Checkpoint at origin time, en son tamamlanmış fiyatı ve bir sonraki M15 OPEN'u kullanır;
  16/92/276 bar geriye bakış; en son tamamlanmış CME H1 ve yalnız geçmiş 6 H1 NQ.
- Henüz kapanmamış veriyi, gerçek ilk yayımı belirsiz haberi veya `expost_price_label`'ı predictor yapma.
- Örnekleme değişirse sonuçlar eski raporun devamı sayılmaz, yeni sürüm gerekir.
```sh
python event_analog_portfolio_guard_v0.py \
  --library OLAY_02_96_TUM_VAKA_EVRENSEL_ORUNTU_MATRIKS_20261015.csv \
  --outcomes historical_96h_case_outcomes.csv \
  --checkpoints verified_3h_asof_features.csv \
  --year 2026 --mode hybrid --output replay_2026.json
```
**Repo güvenliği:** Bu dosya eski Ocak 2026 strateji deneyi değildir;
hiçbir arşiv, eski manifest veya silinen Ocak dosyası geri yüklenmez.
