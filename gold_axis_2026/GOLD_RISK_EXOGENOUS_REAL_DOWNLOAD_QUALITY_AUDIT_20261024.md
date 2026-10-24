# 2026-10-24 Resmî risk göstergeleri — GERÇEK İNDİRME + KALİTE SONUCU

## Doğrulanmış çalışma
GitHub kaynak toplama run: https://github.com/ataullahturgut/sim3-automation/actions/runs/40128963283 (success: araştırma envanteri oluşturuldu; **her veri kaynağı başarılı değil**).
Bir kez çalıştırıldı ve launch push tetikleyicisi derhal silindi; `.github/workflows/gold-exogenous-official-source-audit-manual-v1.yml` hem main hem dalda otomatik zamanlama içermiyor.
Neon'a yazılmadı, model değiştirilmedi, tahmin üretilmedi.

## İndirilen resmî ham dosyalar

**CFTC Disaggregated Futures Only 2023–2026** — DÖRT ZIP fiziksel olarak indirildi:
- 2023: GOLD COMEX GC=088691 52 hafta; SILVER COMEX SI=084691 52 hafta.
- 2024: GC 53; SI 53.
- 2025: GC 52; SI 52.
- 2026 (20 Ekim'e kadar): GC 42; SI 42.
- TOPLAM **398 doğru tip sözleşme haftalık satırı**. Mikro altın dahil edilmedi. İlk ayrıştırıcıda bu alt sözleşmelerden kaynaklanan duplicate hatası görüldü; kontrat kodu tam eşleme kuralıyla düzeltildi. Teknik arşiv indeksleyici de düzeltildi.
- Alanlar: managed-money long, short, net, open-interest ve net/OI.
- CFTC rapor günü != yayın günü. Normal dönemde **7 takvim günlük konservatif gecikme araştırma vekili**; anlık yayın bilgisi kesin olarak sertifikalı değil. 2025 federal hükümet kapanmasında 13 rapor için duyurulan **gerçek gecikmiş yeni yayın günleri** kullanılıyor (yayımlandığı günün ERTESİ günü modelde erişilebilir olacak). Resmî duyuru: https://www.cftc.gov/PressRoom/PressReleases/9147-25 ; CFTC ZIP: https://www.cftc.gov/MarketReports/CommitmentsofTraders/HistoricalCompressed/index.htm
- 29 Ocak 2026 araştırma orijininde kullanılabilecek son CFTC GC ve SI posizyon raporu: **20 Ocak 2026**, konservatif 27 Ocak kullanım başlangıcı. 27 Ocak raporunu 29 Ocak'a taşımak yasak.
- Sonuç: kaynak, kontrat kimliği ve hafta kapsamı doğrulandı; **geçmişteki normal yayınların tarih/saat tam birincil teyidi olmadığı için tutucu/research-only**.

**SPDR GLD (resmî XLSX, 2004–2026)** — indirildi ve artifact_tool ile okundu; toplam 5.721 satırlık iki sayfalı workbook. 2023–2026 yerel kapsama:
- 2023: 250 günlük sayısal kayıt + 10 tatil/boş.
- 2024: 252 sayısal + 10 tatil/boş.
- 2025: 250 sayısal + 11 tatil/boş.
- 2026 (22 Ekim'e kadar): 203 sayısal + 8 tatil/boş.
- Toplam 955 sayısal + 39 tatil/boş = **994 tarih satırı**. 2023–2025: **752 sayısal kayıt**.
- Sütunlar: total ounces / tonnes in trust, ounces gold per GLD share, share trading volume, closing GLD share price. Tonaj değişimi para girişi değildir; üründe işlem/teslimat zaman farkı olabilir.
- SPDR ilk yayın zamanı ve vintage tek tek kanıtlı değil; nedenle **katı PIT modele şu an dahil edilmeyecek**.
- Publisher link: https://api.spdrgoldshares.com/api/v1/historical-archive?exchange=NYSE&lang=en&product=gld
- Issuer copyright/license restrictions preserved: full proprietary XLSX or row-by-row reconstruction is **not committed into the public GitHub repository**. Only metadata, hash and audit are preserved.

## Denenen ancak tam indirilemeyen yeni kaynaklar

- **CME GC/SI tarihsel teminat PDF**, resmî site üzerinden 403 Forbidden GitHub runner; resmî PDF sayfasının açık olması raw GET iznini garanti etmiyor. **INDIRILMEDI**. https://www.cmegroup.com/solutions/risk-management/margin-services/historical-margins.html
- **FRED yeni CSV** DFII10, DGS2, DGS10, DTWEXBGS: her biri 90s okuma zaman aşımı; yeni CSV **INDIRILMEDI**. Bununla beraber Neon `public.observations` içinde `DFII10_ALFRED_ASOF_DAILY_RESEARCH_V1` 749 ve `DFII10_FRB_H15` 749 **2023–2025** kaydı zaten var. ALFRED bazlı seri `first_access_minute_not_verified` bayrağı içeriyor; FRED latest vintaj araştırma amaçlı.
- **SLV** BlackRock Data Download için indirilen yanıt geçerli XLS/XLSX imzasını taşımadığından **REJECT**; tarihsel 2023–2025 kapsamı kesinleşmedi. https://www.ishares.com/us/products/239855/ishares-silver-trust-fund

## Kalite maskeleri: modelin hiçbir alanı kendiliğinden doğru kabul etmesi yasak

| Aile | Dosya/seri durumu | Araştırma sınıfı | Üretim/katı PIT kullanımı |
|---|---|---|---|
| CFTC GC/SI | 398 satır + kaynağı/kontrat kodu doğrulanmış | Aday (gecikmeli asof) | Önce tüm yayın istisnalarını denetle; sonra seç |
| GLD | 752 sağlam sayısal 2023–25, 31 holidays/no-data | Retrospektif çalışma adayı | İLK YAYIN vintajı doğrulanana kadar uzak tut |
| DFII10 (Neon mevcut) | 749 satır 2023–25 | ALFRED araştırma bayraklı | availability/vintaj kontrollü |
| SLV | indirme türü geçersiz | Karantina | DAHİL ETME |
| CME GC/SI | 403 | Kaynak engelli | DAHİL ETME |
| FRED yeni ham | ağ timeout | Mevcut Neon verisini denetle | Yeni kaynakmış gibi işaretleme |

Eksik değerler sıfır veya ileriye dönük taşıma ile uydurulamaz. Bir değerin güvenilir olması *indekste bulunması* ile *zamanında öğrenilmiş olması* açısından iki ayrı şarttır.

**Tahmin modelleri HÂLÂ DEĞİŞMEDİ.** Bu koşu veri indirme, sözleşme ayırımı ve kalite tabanlı maskeleme aşamasıdır. Retrospektif skorda riskli durumlar yanlış-alarm ve bağımsız olay kümeleri ile ölçülecek; gerçek ANN hata uyarısı için 2023–2025 eğitim dışı hatalarına bağlanması gerekiyor.
