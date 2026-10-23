# 23 Ekim 2026 — KAYNAĞI YENİDEN BULDUK: 2026 AĞUSTOS–EYLÜL DÖRT METAL GÜNLÜK FİYAT ARŞİVİ

**Durum: Aynı orijinal StakTrakr GitHub kaynak ailesinden pinlenmiş güncel arşiv bulundu; veri araştırma dalında ayrı R2 araştırma kaynağı adayı olarak doğrulandı. R1/CORE5/model/Neon değiştirilmedi.**

## Önceki “yok” sonucunun nedeni

Neon'daki `XAU/XAG/XPT/XPD_STAKTRAKR_RESEARCH_DAILY_R1` serileri **2026-07-31** tarihinde duruyor. Bu, kaynağın kendisinin de orada durduğu anlamına gelmiyor. Eski R1 kaynak `lbruton/StakTrakr/data/spot-history-2026.json` pinned commit `ed2e549f82ba0d1cd3ca32842b82d3888d301e01`, dosya 2026-08-19'a kadar gözlemler zaten içeriyor; Neon eski 2026-07 araştırma kapsamıyla aktarılmış.

Daha önce projede `StakTrakr` repo ve ayrıca `StakTrakrApi` (`api` branch) kullanılmıştı. **Aynı dört-metal `spot-history-YYYY.json` dosya sözleşmesi** güncel commit'lerde mevcuttur. API repo `README.md` bu dosyaları *daily noon UTC seed entries (not live data)* olarak açıkça tanımlar; API'nın saatlik spot pollerları ile günlük tarihsel seed'in “aynı fixing” olduğu varsayılamaz.

## Gerçek GitHub dosyası incelendi

| Source pin | Dosya | Ağustos 2026 | Eylül 2026 | Kaynak etkisi |
|---|---|---|---|---|
| [R1 `ed2e549f`](https://github.com/lbruton/StakTrakr/blob/ed2e549f82ba0d1cd3ca32842b82d3888d301e01/data/spot-history-2026.json) | `spot-history-2026.json` | 1–19 Ağustos **19 tarih** (Neon R1'e yüklenmemiş) | **0** | Eski araştırma kapsamı |
| [Pin `54fdf1c8`](https://github.com/lbruton/StakTrakr/blob/54fdf1c8d39b7b6c7b874d0f30f784296e886044/data/spot-history-2026.json), commit 30 Eyl | aynı | **31 takvim tarihi** | **29 takvim tarihi**, 30 Eyl yok | 30 Eyl itibarıyla snapshot |
| [Pin `709f3111`](https://github.com/lbruton/StakTrakr/blob/709f31117ec0b748a6d0478bb652e086cd44e609/data/spot-history-2026.json), commit 17 Eki | aynı | **31 takvim tarihi** | **30 takvim tarihi** | Dönem tamam; 2026-10-16'ya kadar mevcut |

Her tarihte **Gold, Silver, Platinum, Palladium** var; 17 Eki sürümünde Ağustos **21** ve Eylül **22** iş günü (hafta içi) dört metal açısından eksiksiz. Ancak yine hafta sonu ve `sqld` sağlayıcı metaverisi belirsiz kayıtları bulunuyor. **29 Eylül'de elde edilen bir snapshot 30 Eylül'ü içeremez**; Eylül ayının nihai değerini 17 Ekim snapshot'ından almak, 30 Eylül tarihli gerçek tahminde varmış gibi kullanılamaz.

## Eski kaynakla yeni kaynak aynı fiyatları mı veriyor?

**Tam değil!** R1 eski commit dosyasındaki dört metalin 2026 gözlemlerini 30 Eylül commit'i ile doğrudan eşleştirdim:

- Eşleşen **832 metal-gün** kaydından **611'i birebir aynı**, **221 fiyatı revize** edilmiş.
- Ağustos ve Eylül kaynak dosyası tamamlansa bile **eski fiyatların sessizce üzerine yazılması yasak**. Değişen haftalar özellikle 2026-04..2026-08 döneminde; bazı tekil mutlak farklar 50–80 USD/ons'a kadar ulaşıyor.
- **30 Eylül → 17 Ekim** kaynak pinleri arasındaki mevcut 2026 ortak **1036 metal-gün fiyatı birebir aynı**; sonradan **68** yeni metal-gün kaydı eklenmiş, değiştirilmiş eski ortak fiyat 0.
- Bu tarihsel revizyon denetimi, **veriler var** ile **eski seri devamına doğrudan eklenebilir** iddialarını ayırıyor.

## Kod, otomasyon ve kanıt

- `gold_axis_2026/tools/gold_monthly_staktrakr_r2_source_bridge_v1.py`: Tam commit SHA + beklenen Git blob SHA1 kontrolü; bir tarihte dört metal tam mı; Aug/Sep 20+ iş günü; kıyaslanan eski fiyatlarda revizyon, eklenen veri, çıkarılan veri; girdi provider; kaynak firstprint iddiası.
- `gold_axis_2026/tools/tests/test_monthly_staktrakr_r2_source_bridge_v1.py`: eksik metal günü, 20 gün kapsama, revizyon görünürlüğü, silinen eski gözlem güvenliği testleri.
- `.github/workflows/gold-monthly-staktrakr-r2-bridge-v1.yml`: GitHub Actions orijinal ve 17 Ekim immutable GitHub `spot-history-2026.json` dosyalarını tekrar indirir ve kaynak hash'lerini doğrular; 2026 Ağustos–Eylül dört metal denetim raporunu artifact olarak kaydeder. **Veritabanına erişimi kapalıdır.**

## Bilimsel hüküm

**Önceki cevapta “2026 Ağustos–Eylül dört metal verisini temin edemiyorum” demek yanlıştı.** Veri aynı kaynaktan mevcut ve kaynak kontrollü araştırma R2 serisi olarak getirilebilir. Ancak bu dosya **günlük *noon UTC research seed*** ile API saatlik canlı fiyatlarını ve WB/CORE5 aylık hedefini kanıtlı aynı fixing saymaz. Modelin 2025/2026 gerçek zamanlı hata rakamları R2'yi sırf mevcut olduğu için otomatik eğitim/test verisi olarak kullanıp düzeltilemez. Yeni R2 kaynak ID ve per-origin vintage etiketleri, 2026-02..2026-09 revizyon/fixing bridge testi gerekir.

**Bu rapor yeni veri keşfi ve immutable kaynak denetimidir; Neon'da veri yenilenmedi, original R1 fiyatı değiştirilmedi, tahmin modeli yeniden koşturulmadı, yayın saati PIT sertifikası verilmedi.**
