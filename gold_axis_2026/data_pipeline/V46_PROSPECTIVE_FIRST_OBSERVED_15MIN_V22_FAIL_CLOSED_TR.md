# V46 — GELECEĞE DÖNÜK 15 DAKİKALIK VERİ GÜNLÜĞÜ: İLK GÖRÜLME ZAMANI, V22 HAZIRLIK KİLİDİ

## Hedef

2024–2026 retrospektif V22/V43 araştırması, yalnız *arşiv* fiyatlarıyla canlı performans sertifikalandıramaz. Bu V46 mekanizması **kaynak fiyatın GitHub Actions araştırma toplayıcısı tarafından ilk görüldüğü zamanı** ayrı Neon tablosuna yazar. Bu zaman **fiyat sağlayıcının gerçek ilk yayımlanma zamanı demek değildir**.

## Kesin sınırlar

- Dört metal (AU/AG/PT/PD) StakTrakr kamuya açık 15m JSON kaynaklarından alınır, her metalde tarih/saat/spot/providing label/ham snapshot SHA256 ve kaynak satırı SHA256 saklanır.
- Kaynak gözlem zamanı, kolektör saati ve ilk veritabanı yazılma zamanı ayrı tutulur. `collected_at` ya da yayımlanma zamanı ASLA eski tarihe geri alınmaz.
- New York 17:00 piyasa açılış/kapanış takviminde hafta sonu `marketOpen=false`. Eski snapshot için >45 dakika `source_recent=false` ve sinyal hazır sayılmaz.
- Çakışan kaynak gözlemleri birden çok kez kaydetme: `UNIQUE(metal,window_start_utc,source_row_sha256)`, `ON CONFLICT DO NOTHING`. Fiyat revizyonu farklı kaynak hash ile **korunur**, var olan tarihsel araştırma tablolarına dokunulmaz.
- V22 kaynak tarafında yalnız `gold_weekly_live.staktrakr_v22_risk_shadow_v1` kaydı var; bu kayıtlar **`is_production_signal=false`**. Dolayısıyla kaydın tüm fiyatları güncel olsa bile **V22 uygun değil = riskten çıkış sinyali ÜRETME**.
- Bu çalışma **otomatik AL/ÇIK/NAKİT**, gerçek emir ya da uygulama üretim sinyali sağlamaz. Sadece bir sonraki 15m fiyatın araştırma projesi tarafından *görülmesi* için güçlü denetim izi oluşturur. V22 canlı as-of 09:00 gibi orijinal eşzamanlı tasdik beklenir.
- Teknik yetki: araştırma tablosu `gold_weekly_live.staktrakr_firstseen_15m_collector_shadow_v1`, hiçbir V22/ANN/BASE14/CFTC21 üretim tablosu değişmez.

## Takvim ve ilk başarılı koşu

GitHub Actions `gold-v46-prospective-firstseen-15m-shadow.yml` iş akışı, ana dala birleştirildiğinde **UTC saatte 07, 22, 37, 52. dakikalarda** kaynak gözlemeyi dener; 15 dakikalık data gerçek yayın gecikmesi için 5 geçmiş pencereden ilki kullanılır. GitHub Actions scheduler gecikebilir, kaynak yayını gecikebilir, durum raporları mutlak anlık eşzamanlılığı **garanti etmez**.

İlk gerçek GitHub Actions araştırma çalışma kanıtı:
https://github.com/ataullahturgut/sim3-automation/actions/runs/41182210245
- 10/10 birim test PASS ve gerçek API kaynağından 31 Ekim 07:30 UTC dört metal birer fiyat gözlemi başarıyla alındı.
- Dört metal kayıt da araştırma tablosuna eklendi; hafta sonu piyasa kapalı (`marketReady=false`) ve V22 uygun canlı kaynak yok (`BLOCKED_NO_PRODUCTION_QUALIFIED_V22`).
- **Dört fiyat kaydedilmiş olması ÇIK sinyalinin canlı çalıştığı anlamına GELMEZ.**

## Güvenilir canlı V43 için ön koşullar

1. Kaynak fiyatın gerçek broker/banka zaman damgası, spread ve piyasa açık durumu doğrulanmalı.
2. **V22'nin gerçek zamanlı hesaplandığı ilk-yayın veri kaynakları** ile model sürüm SHA ve max-input-available UTC kayıtları as-of olarak saklanmalı.
3. Hazır olduğunda ancak ayrı bir `PROSPECTIVE_V22_RISK` girdisi teyit edildikten sonra V44'ün tek yönlü `WATCH→EXIT` algoritması ilgili fiyat akışına bağlanmalı. Eski 2026 retrospektif sinyalleri güncel uyarı gibi yeniden oynatılamaz.
4. Güncel fiyat sağlayıcısının spot fiyat tanımı HistData araştırma serisinden farklı olabilir; geçmiş eşikler yeni kaynağa birebir aktarılıp canlı yatırım kararı üretilemez.
5. Kullanıcı para/pozisyon yönetimi istemediği için bu altyapı AL/REENTRY/portföy kurgusu yapmaz.

## Kaynak kod

- `gold_axis_2026/data_pipeline/staktrakr_first_observed_15m_shadow_v46.py`
- `gold_axis_2026/data_pipeline/test_staktrakr_first_observed_15m_shadow_v46.py`
- `.github/workflows/gold-v46-prospective-firstseen-15m-shadow.yml`

**Statü: araştırma verisi ilk-görülme zaman damgası, veri yayıncısı firstprint veya canlı V22 değil.**
