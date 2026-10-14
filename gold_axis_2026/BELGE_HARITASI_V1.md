# ALTIN PROJESİ — SABİT BELGE İSİMLERİ
**Tek araştırma bütünlüğü: olay = haber akışı + veri akışı + ekonomi bağlantısı + karar + maliyetli sonuç.**

| Kod | Adı | GitHub asıl dosyası | İşlev |
|---|---|---|---|
| **ANA-01** | **Proje Ana Manifesti** | [Aktif ana manifest](GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md) | Araştırma hedefleri, protokol, kaynak ve belge yetkisi. |
| **OLAY-02** | **Entegre Olay ve Vaka Kütüphanesi** | [Tek olay dizini](OLAY_02_ENTEGRE_OLAY_VAKA_KUTUPHANESI.md) | Her olayın **haber + fiyat + piyasa + 15m/1m analiz + AL/SAT/TUT + sonuç** bütünlüğü. Daha önce 'VAKA-03' dediğimiz dosyalar bu kaydın ALT bileşenleridir. |
| **ÖĞREN-03** | **Ortak Öğrenme ve Karar Mekanizmaları** | [Tek mekanizma sicili](adaptive_volatility_learning/EVENT_CAUSAL_ACTION_HYPOTHESIS_REGISTER_20261014.md) | Birden çok olaydan çıkarılan doğrulanmış/hipotez mekanizma kayıtları ve yanlışlamalar. |
| **DURUM-04** | **Aylık Çalışma Durumu** | [Ocak 2023](adaptive_volatility_learning/months/2023-01/STATE.json) | Ay ilerlemesi ve en son durum. Diğer aylar kendi STATE.json dosyasında. |

### Arşiv ayrı, araştırma olayı tek
Dünkü 5.190 satırlık [olay araştırması dondurulmuş arşivi](GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST_FULL_HISTORY_SNAPSHOT_20261014.md), **OLAY-02'nin geçmiş kaynak kanıtıdır**; ayrı, rakip bir olay-katalog otoritesi değildir. Dondurulmuş arşivi değiştirmiyoruz. Yeni incelemeler OLAY-02 dizininde aynı `EVENT_ID` ile birleştirilir ve orijinal tarihsel kanıta bağlanır.

**VAKA-03 kodu artık KULLANILMAYACAK.** Vaka raporları fiziksel olarak eskiden kalan dosya adlarında olabilir ama içerik ve kimlik olarak OLAY-02 altında bulunur; eski linkler kırılmaz.

### Asgari güncelleme fişi
- **Okunan:** ANA-01 / OLAY-02 / ÖĞREN-03 kaynakları.
- **Değiştirilen:** kod + tam dosya yolu; OLAY-02 olay-ID ve iç kanıt yolu.
- **Çıkarım:** ÖĞREN-03 hipotez-ID ve kanıt/doğrulama durumu.
- **Değiştirilmeyen:** tarihsel arşiv ve ayrı araştırma dallarındaki diğer modeller.
- **GitHub:** doğrulanmış commit ve araştırma dalı.
