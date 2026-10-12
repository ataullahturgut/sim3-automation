# Claude Code — Gold araştırma oturumları için çalışma kuralları

Bu dosya yalnızca Claude Code oturumlarının **nasıl çalışacağını** tanımlar. Bilimsel otorite değildir.
Araştırma sözleşmesi, hedefler ve geçmiş sonuçlar şu belgelerde kalır ve buradan değiştirilmez:

- Kısa vade / Türkiye işlem saatleri (09:00→16:45, 16:45→ertesi takvim günü 09:00, H3): `gold_axis_2026/GOLD_INTRAMONTH_OPPORTUNITY_PROJECT_MANIFEST.md`
- Yön motoru: `gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md`
- Aylık fiyat: `gold_axis_2026/GOLD_MONTHLY_PROJECT_MANIFEST.md`

Bu dosya ile bir manifest çelişirse manifest geçerlidir.

## Kaynaklar

- GitHub: `ataullahturgut/sim3-automation`; ana çalışma dalı `gold-execution-channel-audit-20261006`.
- Neon projesi: `Gold Control` (`winter-art-94880101`), Neon MCP üzerinden.
- Python: önce mevcut numpy/pandas; gerekirse küçük paketler `pip` ile kurulabilir.

## Bağımsız çalışma — önceden verilmiş yetkiler

Kullanıcı aşağıdakileri önceden yetkilendirmiştir. Bunlar için sohbette yeniden izin istenmez, plan anlatıp beklenmez.
Deney sonuna kadar yürütülür ve ölçülmüş sonuçlarla dönülür.

- GitHub'daki araştırmaları, manifestleri, kodları ve sonuç dosyalarını incelemek.
- Neon'da araştırma verilerini sorgulamak (SELECT).
- Gerektiği ölçüde Python paketi kurmak.
- Model eğitmek, deney çalıştırmak, testleri tekrarlamak, sonuçları değerlendirmek.
- Neon'da mevcut tablolara dokunmadan **yeni**, açıkça isimlendirilmiş araştırma tabloları/görünümleri oluşturmak ve deney sonuçlarını yazmak.
  - İsim kalıbı: `gold_research_rNN_<konu>_v1`.
- GitHub'da **yalnızca kendi araştırma dallarında** kod, rapor ve sonuçları commit/push etmek; ana çalışma dalına yönelik PR açmak.
- Başarısız ve negatif deneyleri de araştırma kayıtlarına eklemek.

## Açık onay gerektiren durumlar

Yalnızca şunlar için önce kullanıcıdan açık onay istenir:

1. Mevcut Neon tablolarını veya kayıtlarını değiştirmek ya da silmek (UPDATE, DELETE, DROP, TRUNCATE, ALTER).
2. Ana GitHub dalına (`gold-execution-channel-audit-20261006`, `main` vb.) doğrudan yazmak, herhangi bir force push yapmak veya PR birleştirmek.
3. Şifreleri, API anahtarlarını, bağlantı dizelerini veya özel verileri dışarı aktarmak.
4. Yeni ücretli hizmet veya API kullanımı başlatmak.
5. Araştırmanın nihai hedefini ya da dondurulmuş bilimsel sözleşmeyi değiştirmek.

Platformun kendi güvenlik onayı veya izin istemi çıkarsa atlatılmaya çalışılmaz.

## Git kuralları

- Çalışmaya başlamadan önce ana çalışma dalının **güncel remote HEAD'i** fetch edilir. Yeni dal bu HEAD'den açılır, böylece başkalarının yeni commitleri ezilmez.
- Her araştırma için ayrı dal açılır, örn. `rNN-<kısa-konu>`. Normal push yapılır, force push yapılmaz.
- PR'ın hedefi ana çalışma dalıdır. PR birleştirmek kullanıcıya aittir.
- Erişim anahtarları, bağlantı şifreleri ve gereksiz ham piyasa verileri commit edilmez.
  - Yeniden üretilebilirlik için türetilmiş, küçük, tarih eşleşmiş paneller (ör. log-getiriler) ve bunları üreten SQL commit edilebilir.

## Bilimsel dürüstlük (manifestteki kuralların özeti; asıl metin manifesttedir)

- Önce manifestte aynı veya matematiksel olarak eşdeğer bir deney aranır. Varsa açıkça bildirilir; yalnızca gerçekten yeni kısım sınanır. Başarısız yöntem yeni isimle tekrarlanmaz.
- Hipotez, kurallar, pencereler, parametreler ve geçme ölçütleri **sonuçlara bakmadan** bir `..._PREREG.md` dosyasına yazılır ve commit edilir.
- Sabit hipotez başarısız olursa geriye dönük eşik, saat veya model taraması yapılmaz.
- Rastgele bölme yapılmaz. Eğitim ve ön işleme yalnızca karar anında mevcut bilgiyle sınırlıdır. Karar saatinden sonra tamamlanan hiçbir çubuk kullanılmaz.
  - CME saatlik `ts_event` çubuk **başlangıcıdır**.
  - `Europe/Istanbul` = UTC+3.
- Geliştirme dönemi 2023–2024'tür. 2025 ve 2026 sonuçları daha önce görülmüştür; **dokunulmamış test başarısı olarak sunulmaz**.
- Veri kaynakları (EV/Dukascopy 2020–2025, doğrudan Dukascopy 2026, HistData vb.) farkları kaydedilmeden birleştirilmez. Yıl ve kaynak bazında ayrı raporlanır.
- Her yıl için şunlar raporlanır:
  - N, kapsama, accuracy, balanced accuracy, UP/DOWN recall;
  - aynı tarihlerde taban çizgileri ve mevcut modelle eşleşmiş karşılaştırma;
  - düzeltilen/bozulan karar sayıları, belirsizlik ve anlamlılık.
- Banka alış/satış kotasyonu olmadan kârlılık iddiası yapılmaz.
- Erişilemeyen veri veya çalıştırılmayan test için sonuç uydurulmaz. Sayılar, commit edilmiş kod ve sonuç dosyalarıyla birebir tutarlı olmalıdır.
- Negatif sonuç da sonuçtur: rapora, sonuç dosyalarına ve kendi dalındaki manifest kaydına eklenir.
