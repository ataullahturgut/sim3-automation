# ALTIN PORTFÖY KORUMA: V6 EKONOMİK VERİ + OLAY-02 SONUÇ DENETİMİ

**15 Ekim 2026 · Çalışan deneme tamamlandı · Otomatik alım-satım için RED.** Bu rapor yalnızca başarısız veya olumlu sonuçları değil, sonuçların hangi bilimsel ölçüte dayanmadığını da gösterir. Sonuçları yeniden üretilebilir dosyalara bağlar.

## Veri ve zaman disiplini
- OLAY-02, 96 kaydın tamamı Git blob `4b6c8fd84ea291ae22ddc9b0d5d545ce2d8fa527`: **96/96 haberin ilk yayımlanması doğrulanmamış; 96/96 mekanizma nedeni kanıtlanmamış; 0 as-of onaylı işlem**. ORG01–ORG... ve G05-C/G06-B otomatik AL/SAT nedeni OLAMAZ.
- Mevcut ayrı `event_evidence_gate_v6.js` somut tarihsel karşı-örnek: 1 Şubat 2023 saat 06.15 UTC fiyat kontrolünün nedeni aynı gün ABD saat 14.00/19.00 UTC yayımlanan FOMC açıklaması OLAMAZ. Haber ve karar saatlerinin doğru ayrılması zorunlu.
- Model `macro_v6_portfolio.js`, CME Databento NQ (Nasdaq futures), ZN (ABD 10 yıllık tahvil fiyatı vadeli), SI (gümüş futures) tamamlanmış H1 verilerinden hesaplanan 6 saat/24 saat getiriyle beslendi. **Her 3h karar kesitinde yalnız geçmişte kapanmış H1 barı kullanıldı**; haber nedeni çıkarılmadı.
- 2023–2026 7.682 saat kesiti; tamamlanmış eş NQ+ZN altı saat gözlemleri: 2023 1.615/2.045, 2024 1.624/2.059, 2025 1.609/2.046, 2026 1.224/1.532. SI aynı saat yeterince dolu değil; eksik gözlem 0 diye alınmaz.
- CME sabit kaynaklar `data/CME_3H_ASOF_2023_2024_V6.csv` Git blob `e8787df9823b412e31546c784f1e95a762126697` ve `data/CME_3H_ASOF_2025_2026_V6.csv` Git blob `2a2b42d0140fac3aea197013c443cd268db92b6d`.
- Mevcut risk kategorileri `EQUITY_BOND_SELL_OFF`, `SAFE_HAVEN_ROTATION`, `YIELD_HEADWIND`, `CROSS_RISK_ON`, `NO_CONSENSUS_OR_STALE`. Bunlar fiyat korelasyonu tanımıdır, bir olayın gerçek nedeni, Fed tutumu ya da doğrulanmış haber etkisi DEĞİLDİR.
- Banka işlem zamanları Türkiye 09/12/15. Komisyon alım +%0,8 ve satım +%0,8, fakat bankanın gerçek ASK/BID makası ve slippage bulunmamaktadır. Dolayısıyla gerçek banka karı gösterilemez.

## Önceden tanımlanmış V6 karar etkileri
Alımda Nasdaq+tahvil birlikte sert satış ve altın orta vade düşüş varsa giriş ertelenir. Nasdaq yükselirken tahvil fiyatı düşüyorsa ve altın uzun vadede zayıfsa giriş payı yarılanır. Ekonomik panik eşleşmesinde altının kendi orta/yavaş düşüşü ile birlikte koruyucu SAT öne alınabilir. Nasdaq düşüp tahvil yükselirken altın kendi fiyatı güçleniyorsa gereksiz normal SAT ertelenebilir. Belirsiz/eksik veri eski V5 fiyat kararını aynen bırakır. Kurallar [V6 deney protokolü](V6_CROSS_ASSET_EVIDENCE_PROTOCOL_20261015.md) sonuçlar okunmadan kaydedilmiştir.

## Tarihsel portföy karşılaştırması — her eski yıl ayrı 100 dolar nakit

| Yıl | V5 sadece fiyat/trend | V6 makro ekli | İlk işlemi AL sonra altını TUT | Karar |
|---|---:|---:|---:|---|
| 2023* | 107,68 | **107,68** | 110,32 | Makro ek getiri yok |
| 2024 | 111,23 | **111,23** | **124,43** | Makro ek getiri yok |
| 2025 | 135,04 | **135,04** | **161,15** | Makro ek getiri yok |

*2023 XAU kaynak kapsamı eksiktir, yıllık kıyas sağlam değildir. 2024–25 de araştırma sürecinde daha önceden görülmüş dönemler olduğundan yüksek güvenli kör OOS sayılmaz.

## 2026 Şubat–Eylül: tek portföy ve ay devri

- Başlangıç **119,753917 USD NAKİT**, Ocak 2026 dondurulmuş V1 sonu. V6 ve V5 her ay sıfırlanmadan Şubat–Eylül aynı portföyü taşır.
- Eylül sonu V5 **107,832861 USD**; V6 **107,740399 USD**. V6, ekonomik kontrol eklediği halde yaklaşık **0,09246 USD daha az** sonuç aldı. Başlangıçtan V6 zararı yaklaşık **%10,03**.
- Hiç işlem yapmadan NAKİT **119,753917 USD** kalacaktı. 2 Şubat ilk 09:00 banka zamanı teorik AL ve Eylül sonunda çıkış ise **107,741250 USD**. V6 ne nakdi geçebildi ne de pasif altına anlamlı üstünlük kurdu.
- Kaynak: `macro_v6_portfolio.js`, `recovery_v5.js`, `v4_forward_review.js`; saat ve maliyet karar defteri `npm run verify-macro-v6-portfolio`; Windows/Linux otomatize regresyon testi.

## Bağımsız tahmin metriği: ek ekonomik değişkenler faydalı mı?
Önceden mevcut ayrı `macro_v6.js` logistic denetimi, fiyat 5 özellik ile fiyat+NQ/ZN/CL (petrol) 11 özellik karşılaştırdı; bu **AL/SAT simülasyonu değil**, gelecek 24 saatte bir 3h altın kapanışında en az %2 düşüş alarm araştırmasıdır.

| Test yılı | Gerçek alarm vakası | Yalnız XAU Brier | XAU+makro Brier |
|---|---:|---:|---:|
| 2024 | 5 / 148 | 0,03316 | **0,03155** |
| 2025 | 8 / 155 | **0,04795** | 0,05014 |

2024'te ek gösterge kısmi iyileşti, 2025'te kötüleşti. Vaka sayıları çok azdır, güvenilir olasılık ya da ekonomik nedensellik çıkarma mümkün değil. Macro modellenen XAU olayında 2024/25 kalıcı ek değer gösterilmedi.

## Bilimsel kabul/red
**V6 kabul edilmedi (`REJECT_AUTOMATIC_PROMOTION`).** 2024 ve 2025'te V5'i geçemedi. 2026 portföyünde V5'ten kötü; 96 ekonomik olayın nedenselliği doğrulanmadı, gerçek banka kotasyonu ve bağımsız prospektif test yok. Sayısal iyileşme istendiği için eşikleri aynı 2026 örneğinde yeniden değiştirip başarı elde edilmiş gibi gösterilmeyecek.

## Gerçek sonraki hamle ve kaynak gereksinimi
1. OLAY-02'deki 96 olayın hepsi haber saatinin doğrulanmasıyla başlamalı. Her olayda başlatıcı kanıt, yayın zamanı, beklenen/gerçekleşen veri, diğer varlıkların aynı as-of tepki sırası ve rakip açıklama toplanmalı. Nedensellik bulunmayanlar `UNRESOLVED` olarak bırakılmalı.
2. Dolar endeksi/yönü, ABD 2Y/10Y gerçek tahvil **getirileri**, gümüş gün içi devamlı veri ve gerçek banka işlem alış/satış kotasyonları yeni kaynak sözleşmesiyle eklenmeli. Futures ZN fiyatını gerçek tahvil getiri oranı sanma.
3. Öğrenme örneği olay bazında olmalı, aynı şokun 100'lerce 15m barı bağımsız olay sayılmamalı; 24/48/96h başarısız/başarılı toparlanma etiketleri ve 5/10 seans riski olgunlaştığında eğitim setine aktarılmalı.
4. Gelecekte henüz görülmemiş dönem için kod, girdiler ve karar maliyeti sabitlenmeli; ancak o zaman kalıcı net üstünlük için geçerli bağımsız OOS ölçülebilir.

**Sistem durumu:** Çalışan, yeniden üretilebilen tarihsel ekonomik risk kontrolleri vardır; olumlu getirisi bilimsel olarak kanıtlanmış otomatik AL/SAT **yoktur**. V1–V5 sonuçları ve OLAY-02/ÖĞREN-03 dosyaları korunmuştur.
