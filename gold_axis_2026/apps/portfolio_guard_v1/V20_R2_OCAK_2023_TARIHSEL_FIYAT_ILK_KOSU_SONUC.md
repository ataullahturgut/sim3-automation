# V20 KAVİS–ATLAS R2 | 3–31 Ocak 2023 ilk tarihsel fiyat yürüyüşü

**Durum:** Gerçek piyasa tarihinden türetilmiş MID fiyat vekili kullanılarak koşulmuş kronolojik araştırma pilotu. Gerçek banka BID/ASK fiyatı, otomatik emir veya işlem yok. **Gerçek bankayla birebir uygulanabilir getiri değildir.**

## Donmuş sözleşme
- Başlangıç 2023-01-03 saat 09:00 Türkiye (UTC 06), 100.00 USD nakit.
- Her uygun Türkiye saati 09:00 veya 12:00'de sadece **geçmiş** fiyatlar için 3 saatlik özellikler hesaplanır. Yalnız önceki sinyalin ardından gelen bankaya uygun saat 12:00/15:00 fiyatından MID-proxy fill. 15:00'den sonra işlem yok.
- V20 R2 modelinin **riskMode: alert** varsayılan sürümü kullanıldı; kullanıcının seçmediği %15 gibi bir maxDD limitini uygulamadık. Bu modun fiilî alım satım politikası dondurulmuş V18 Double Q ile aynıdır.
- Banka fiyatı yerine 2020–2022 ve 2023–2025 için daha önce dondurulmuş CME'den elde edilen XAU MID proxy CSV kaynakları kullanıldı. SHA pinleri pilot runner'da doğrulandı.
- Gerçek ilk-yayın zamanlı OLAY-02/ÖĞREN-03 haber olayları, NQ/metaller vb. PIT kanıtları bu pilotta **0**. Bu nedenle yalnız fiyat tabanlı as-of özellikler ve banka maliyeti varsayımı bulunuyor.
- Önceki yıllar araştırmada görüldüğü için 2023 tarihleri yeni kör strateji doğrulaması DEĞİL.

## İlk ay sonuçları
| Ölçüt | Sonuç |
|---|---:|
| 3 Ocak başlangıç nakit | **100.000000 USD** |
| 31 Ocak terminal altın VARSAYIMSAL tasfiye değeri | **98.64003551915013 USD** |
| Yaklaşık aylık net getiri | **-%1.35996448** |
| Pasif ilk uygun fiyattan AL ve ay sonunda SAT | **102.05476381005809 USD** |
| Sürekli nakit | 100.000000 USD |
| En yüksek ölçülen portföy gerilemesi | **%1.94159358** |
| Üretilen sinyal | **41** |
| Gerçekleşmiş sanal banka fiyatı kontrol dolumu | **41** |
| Q için olgunlaşmış fiyat aralığı | **40** |
| Sanal AL | 1 |
| Sanal SAT | 0 |
| İspatlanmış risk uzmanı override | 0 (alert modu zaten müdahaleye kapalı) |
| Onaylanmış haber/ekonomik ilk yayın girişi | 0 |

## Kesin işlem defteri
- **3 Ocak 2023, 09:00 Türkiye**: başlama, 100 USD CASH. İlk karar WAIT. Kullanılan en son geçmiş fiyat 30 Aralık 2022 21:00Z; giriş sinyalinden 81 saat önce, 2023 gelecek fiyatı kullanılmadı.
- **13 Ocak 2023, 12:00 Türkiye** (2023-01-13 09:00Z): öğrenilmiş V18 Double Q ilk BUY sinyalini oluşturdu. Bu sinyalin borsadaki fiyatı aynı anda kullanılarak alış yapılmadı.
- **13 Ocak 2023, 15:00 Türkiye** (2023-01-13 12:00Z): ilk uygun sonraki kontrol noktasında 1899.595 USD/ons MID fiyat vekilinden 100 USD nakit ile BUY simüle edildi, alış yönlü %0.8 maliyet düşüldü. Terminal mark-to-liquidation NAV burada **98.4064 USD** idi (varsayımsal nihai çıkış bacağı da dahil).
- **31 Ocak 2023, 15:00 Türkiye** (2023-01-31 12:00Z): terminal MID vekil fiyatı 1904.105 USD/ons. SAT sinyali oluşmadı, altın sanal portföyde tutuldu. Tüm değer satılsa terminal **98.64003551915013 USD** olurdu; satış aslında yapılmadı.
- **Pasif kıyas:** ilk uygun alım 3 Ocak 2023 12:00 Türkiye (2023-01-03 09:00Z), fiyat 1836.035 MID proxy; Jan31 1904.105. İki yön %0.8 masraflı teorik altın getiri **102.05476381005809 USD**. Bu tek aylık koşuda algoritma pasif al-tutun **3.41472829 USD** gerisinde.

## Teknik test ve veri kanıtları
- CI run https://github.com/ataullahturgut/sim3-automation/actions/runs/38890285818 başarılı.
- Yalnız bu pilot için **7/7** geçmiş fiyat, as-of, veri değişmezliği, gelecek fiyat bozma, borsa saati/sonraki nokta ve tekrar üretim testi geçti; hiçbir başarısız test yok.
- Kaynak 2020–2022 blob: e19d69fbbf4a825420a07d7e5f678899d1e0f805 (5725 gözlem). Kaynak 2023–2025 blob: a588b6745f893fcafc935fa486328a6349caa658 (5125 gözlem).
- Karar günlüğü, 41 sinyal, 41 dolum ve modelin as-of kapanış checkpoint'i GitHub Actions artefaktında kayıtlıdır: https://github.com/ataullahturgut/sim3-automation/actions/runs/38890285818/artifacts/12040929761

## Bilimsel sonuç
**Model Ocak 2023'ün erken yükselişine geç katıldı, maliyetlerin ardından zarar etti.** Bu sonucun gerçek fiyat vekiliyle kronolojik deneyde gözlenmesi, V20 R2'nin güçlü performans sertifikası olmadığını gösteriyor. Güncel tüm olay/haber katmanları ve gerçek banka spreadleri doğrulanmadan canlı işlem tavsiyesine dönüştürülmez.

**Devamlılık:** Ocak sonu portföy ve iki gölge uzman/model Q durumları tam snapshot olarak CI JSON artefaktına kaydedildi. Şubat'a sıfırdan başlayıp sonuçları yapay biçimde parlatmak yerine bu durumun kesintisiz devam ettirilmesi gerekiyor. Bu rapor yalnız Ocak pilotudur.