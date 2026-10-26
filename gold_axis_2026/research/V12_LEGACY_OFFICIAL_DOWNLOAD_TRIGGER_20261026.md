# V12 — Resmî geçmiş CFTC/GVZ/dolar/faiz indirme tetikleyicisi (26 Ekim 2026)

Kullanıcı talebi: 2010–2019 büyük altın düşüşü ve benzer düşüşsüz dönemlerini sadece altın fiyatına göre değil; CFTC GC/SI büyük fon pozisyonları, GVZ, dönemin gerçekten mevcut dolar endeksi, 2/10 yıllık nominal ve reel faizlerle karşılaştır.

## Tamamlanan somut araştırma
- Neon 2010–2019: AU/AG/PT/PD fiyatlarının her birinde 2.526 tekil hafta içi kaydı, 2011 ve 2013 büyük düşüş olayı doğrulandı.
- Neon 2010–2019 günlük CFTC/GVZ/Fed H.10/H.15 içermiyor. Mevcut aylık türevler günlük as-of geçmiş yerine geçirilemez.
- 2011 ve 2013 çok-metalli ortak panelin günlük kaynak soy ağacı aynı; gelecek beş günlük düşüş yalnızca hedef etiketinde kullanılmalı, model girdisi yapılamaz.
- CFTC resmi yıllık Disaggregated Futures Only arşivleri 2010–2019; sadece GC 088691 / SI 084691, Salı rapor gözlemi yayımlanma anı değildir.
- Cboe GVZ günlük arşivi, Fed H.15 DGS2/DGS10/DFII10 ve 2011/2013 döneminde mevcut eski H.10 broad USD DTWEXB kaynakları belirlendi. DTWEXBGS geçmişe geri doldurulmuş tarihi değerleri yalnız 2019 sonrası yayımlanmıştır; 2011'de biliniyormuş gibi modele giremez.
- Resmî kaynak dosyalarını indirmek ve SHA/semantik denetim için `gold_risk_legacy_macro_acquisition_v12.py` yazıldı.
- Bu dosyanın commit'i yalnızca araştırma dalında `workflow_dispatch` / `push` yoluyla GitHub Actions tetikler; sonuçlar GitHub Actions artifact'e çıkar. Neon'a yazım yok, model değişikliği yok.

## Kritik araştırma kapısı
Başarılı ZIP/CSV indirme, gerçek tarihsel ilk yayımlanma değerini kanıtlamaz. CFTC gerçek COT release takvimi / özel gecikme, GVZ ve H.10/H.15 geçmiş sürümleri doğrulanmadan **as-of model eğitimine veri girmez**. 2026 risk model ayarı için kullanılmaz. Tekrar koşu yapılmadan etkin performans iddiası kurulmaz.
