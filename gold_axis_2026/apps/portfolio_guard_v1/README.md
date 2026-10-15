# GOLD Portfolio Guard V1 — sabit tarihsel koşu uygulaması

**Statü: RESEARCH_ONLY · READ_ONLY · LOCALHOST_ONLY · BANKAYA EMİR YOK**

Bu uygulama, Ocak 2026 altın koruma deneyinin aynı veri, aynı parametreler ve aynı motorla her seferinde **aynı sonucu vermesini** sağlar. Canlı tavsiye veya alım-satım emri üretmez.

## Başlatma — Windows PowerShell

GitHub dalı: gold-portfolio-guard-app-v1-20261015

Repo klasöründe:

    cd gold_axis_2026\apps\portfolio_guard_v1
    node --version
    npm test
    npm run verify
    npm start

Tarayıcıdan: http://127.0.0.1:8787

Kapatmak için ilgili PowerShell penceresinde Ctrl+C. Node.js 18+ gerektirir; harici NPM paketi veya internet bağlantısı gerekmez. Yerel sunucu yalnızca 127.0.0.1 adresinde çalışır.

## Sabit API
- GET /api/health — model ve veri kontrolü
- GET /api/summary — üç dondurulmuş modelin kıyaslaması ve kaynak imzaları
- GET /api/replay?mode=event15m — tam 2.976 slot karar defteri
- GET /api/replay?mode=price15m — yalnız fiyat
- GET /api/replay?mode=legacy3h — eski 3 saatlik karşılaştırma

İşlem türü yalnız GET; kullanıcı arayüzü hesaplama formülü çalıştırmaz, motordan gelen verileri görüntüler.

## Ocak 2026 başlıca referans sonuçlar

| Senaryo | 100 $ net son değer | Koruma satışı |
|---|---:|---|
| Olay benzerliği ve fiyat · 15 dk | **119,753917 $** | 29 Ocak 18.15 TSİ |
| Yalnız fiyat · 15 dk | **119,753917 $** | 29 Ocak 18.15 TSİ |
| Eski fiyat · 3 saat | **118,337853 $** | 29 Ocak 21.00 TSİ |

İlk 15 dakikalık alış 5 Ocak 2026 09.30 TSİ, 4.424,055 XAU MID; satış 29 Ocak 2026 18.15 TSİ, 5.383,775 XAU MID. Net sonuç 119,753917 dolar nakit; ay sonuna kadar nakitte.

Maliyetler %0,8 alım + %0,8 satım; **gerçek banka ASK/BID spreadi, slippage, stopaj yok**. Al-ve-tutun aynı 15 dakikalık veri sonuyla teorik tasfiye karşılığı yaklaşık 111,195133 dolar.

Ocak içinde olay öğrenme katmanı, fiyat modelinin işlem kararlarını **değiştirmedi**. Olay bazlı ek net getiri **0 $**. Yakın olaylara verilen skor **kalibre edilmiş olasılık değil**; ekonomik nedensellik ve ilk yayımlı haber verisi henüz kanıtlanmış değil. Ocak 2026 bağımsız ileri test DEĞİLDİR.

## Sürüm ve veri güvenliği
1. Veri ve kaynak vaka dosyalarının **Git blob SHA-1** kimlikleri engine.js içinde sabittir. Bir bayt değişiklikte uygulama hata vererek durur.
2. Komisyonlar ve koşullar engine.js içinde donduruldu. Yeni mantık yeni model VERSION ile ayrı kaydedilmeli.
3. Türkiye saat dilimi Europe/Istanbul. 2.976 Ocak takvim slotunun 1.804'ünde yeni, yeterli M15 veri var. Eksik zamanlarda yeni işlem verilmez.
4. Sadece tamamlanmış CME H1 geçmişi kullanıldı; XAU alım-satımı bir sonraki M15 open MID vekil fiyatından modellendi.
5. 2023–2025 arşivindeki yalnız ilk Ocak 2026'dan önce 96 saatlik ileri fiyat sonucu olgunlaşmış 92 vaka eğitim benzerliği için kullanılabildi. Arşiv, gerçek ilk haber zamanı / nedensellik doğrulaması yerine geçmez.
6. npm test, referans gelir, işlem saatleri, tam slot sayısı, kadans karşılaştırması ve kaynak kimliklerini kontrol eder.
7. Ocak sonu portföy durumu: 119,753917 $ **NAKİT**, altın 0 ons. Şubat'a nakit ve öğrenme notları birlikte devredilmeli.
8. Repo'nun var olan altın tahmin uygulamalarına müdahale edilmedi. Bu uygulama yeni dalda ve ayrı klasördedir.

## Bilerek ertelenen işlevler
- Şubat ve sonraki aylara evrilen genelleştirilmiş ay-ay motor / veri ithalatı
- Geçmişe bakmayan model güncelleme/değişiklik kaydı ve aylık run-id defteri
- Zaman doğrulanmış haberlerin ekonomik DNA P0–P5 evreleriyle gerçek entegre öğrenilmesi
- Olaysız negatif kontroller, şok kalibrasyonu ve bağımsız performans testleri
- Gerçek banka ASK/BID / likidite / işlemin verilebilme saatleri

**Bu V1 yalnız Ocak 2026 sabit arşivine göre çalışan prototiptir.** Diğer aylarda performans iddiası yoktur.

Kaynak: gold_axis_2026/adaptive_volatility_learning/months/2026-01-new-learning/JAN_2026_NEW_EVENT_MONTH_WALK_V1_SCIENTIFIC_REPORT.md
