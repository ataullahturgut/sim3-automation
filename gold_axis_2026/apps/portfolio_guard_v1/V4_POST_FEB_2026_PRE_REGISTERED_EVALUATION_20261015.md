# V4 Şubat sonrası sıralı bağımsız döneme uzatma — önceden kayıtlı deney

**Algoritma sürümü önceden sabitlendi:** V4_ADAPTIVE_CARRY_GUARD_SHADOW_20261015; kod: recovery_v4.js; sabit ana kod commit `0bb484ce80f18544242489c997a16d23b2914e86` ve 2020–2025 girdi SHA'ları. Bu protokol Mart–Eylül 2026 performansı hesaplanmadan yazıldı. 2026 zaman serisi daha geniş altın araştırmasında önceden görüldüğünden sıkı anlamda kör ileri test DEĞİLDİR.

## Araştırma sorusu
2026 Ocak V1 119,75391720039644 USD nakit portföyü ile Şubat başında başlayan, **değiştirilmemiş V4 politikasının** Mart–Eylül 2026 boyunca hiç sıfırlanmadan altın/para birimi/devam eden evreleri tutması hangi net sonuçları üretir? 2025 yükselişini kaçırma sorunu daha sonraki farklı piyasa dönemlerinde devam eder mi?

## Veri + değerlendirme sözleşmesi
1. Mart–Eylül 2026 HistData XAUUSD 15m birincil fiyat tablosundan UTC 00,03,06,09,12,15,18,21 saatli as-of özellik satırları türetilecek; ilk karar anında yalnız tamamlanmış M15 ve o anki bir sonraki açılış fiyatı proxy'si kullanılır. Gelecek fiyat etiketleri karar girdisi olmayacak.
2. Şubat 2026 mevcut dondurulmuş panelden 3h adayları alınır; 1 Şubat 00:00 Türkiye günü piyasa kapalı olduğu için sahte veri/sahte işlem yok. Portföy Mart'a Şubat sonu GOLD + USD portföy durumu ile **kesintisiz devredilecek**, yeni ay her seferinde 100 dolardan sıfırlanmayacak.
3. Eğitim eşikleri sadece 2020–2025 olgunlaşmış verisinden 2026 başlangıcında hesaplanıp aynı kalacak. 2026 Mart–Eylül sonuçlarına bakıp alım/satım eşiklerini yeniden ayarlamak YASAK; validasyon dosyası sonuçları gördükten sonra parametre değişikliği kabul edilmeyecek.
4. İşlemler sadece Türkiye saatinde 09:00 / 12:00 / 15:00; alış ve satış yönü ayrı %0,8; gerçek banka ask/bid farkı ve slip eksik olduğu özellikle belirtilecek. Açık GOLD pozisyonu ay sonunda son geçerli gözlem kapanışından, **varsayımsal çıkış ücretinden sonra** raporlanacak (gerçekten satıldı iddiası yok).
5. Ayrı kıyaslar: sabit nakitte bekleme; Şubat'ın ilk Türkiye 09:00 kesitinde AL/TUT; sabit V3/V4 Şubat sonu; nakit+GOLD taşınan V4 Mart–Eylül yürüyüşü. Aynı veri saatine ve komisyon varsayımına uy.
6. Ay bazında son net değer ve önceki aya göre kazanç, AL/SAT adetleri, açık GOLD oranı, toplam kaçınma/kaçırma, max drawdown, ilk 09:00 giriş değeri, portföy hissesi, kaynak kapsamı, market-day gap sayısı, karar gerekçeleri ve olay nedensellik kanıtsız durumunun açık yazımı.
7. Geçmişteki 2023–25 yıllık geriye dönük karşılaştırma (2023 eksik) sonuçları ayrıca gösterilecek. Tek bir ay kârı, olay nedenini veya kalibre edilmiş UP/DOWN olasılığını kanıtlamaz.

## Başarısızlık ve karar
Eğer V4 Mart–Eylül'de nakit veya AL/TUT altına karşı kalıcı ve risk-ağırlıklı net üstünlük göstermiyorsa, **V4'ü canlı AL/SAT'a yükseltme**. Tespit edilen kör noktalar yeni hipotez/ayrı V5 adayı yapılabilir; Mart–Eylül üzerinde yeniden ayarlayıp aynı örneklemde üstünlük raporlamak yasak. Karşılaştırmaya sonuçlar iyi diye yeni fiyat kaynakları eklenemez; veri kaynakları Git SHA ile sabitlenir.

**Risk uyarısı:** G05-C/G06-B ekonomik nedensellik ilk haber/veri yayımı doğrulanmadığından UNRESOLVED kalır. Veriler MID/proxy, gerçek bankacılık kotasyonu değil. Bu yalnız geçmiş fiyat araştırmasıdır.
