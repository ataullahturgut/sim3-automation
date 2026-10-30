# Numune / Teknik Veri Denetimi — 30.10.2026

## Kapsam ve sınırlar
- Kaynak ürün tablosu: `Reaktor_Ortak_Uretim_ve_Numune_Matrisi_2026.xlsx`. 135 kaynak satırının **133'ünde pozitif yıllık üretim** vardır (iki satır 0 adet). Yıllık toplam **45.088** adet, Şönt **35.772** ve Harmonik **9.316**.
- Ana otorite kontrolü: üreticinin `https://www.gruparge.com/fl/tr` adresinden erişilen **2026/12 fiyat/teknik listesi**. Özellikle PDF sayfa 17, 29–31. Üretici ürün ölçülerinin üretim revizyonuna göre değişebileceğini belirtmektedir.
- Bu rapor **katalog değerlerinin kaynak Excel'den farklı olduğunu** doğrular; ürünün fiilî BOM'unu, sarım reçetesini veya hangi üretim revizyonunun siparişte geleceğini kanıtlamaz.

## Numune listesi kaynak karşılaştırması
Kaynakta fiziksel olarak incelenmesi önerilen **17 farklı stok kodu** bulunuyor:
- **6 ilk fiziksel numune:** GA5002, GA5106, GA5212, GA5436, GA5426, GA5412.
- **11 ayrıca fiziksel kıyas numunesi:** GA5102, GA5104, GA5108, GA5204, GA5207, GA5209, GA5636, GA5536, GA5429, GA5336, GA5415.

Aile dağılımı Şönt **9**, Harmonik **8**. Geri kalan 133 aktif ürünün 73'ü kaynakta sökmeden/doküman kıyası, 43'ü teknik kimlik/doğrulama eksikliği sınıfındadır. Fiziksel numune adaylarının ayrı ayrı sipariş edilmesi önerisi **satın alma onayı / tam ürün kapsaması garantisi değildir**. 11 fiziksel kıyas adayı uygulamada sadeleştirilmiş biçimde `Ana numune` olarak gösteriliyor: rol ayrımı ek bilgi olmadan kaybolabilir.

## Kritik katalog veri ayrışması — Şönt
2026/12 üretici listesindeki **23 standart Şönt** kodu kaynak Excel'le karşılaştırıldığında:
- **23/23 ölçü farklı**
- **16/23 ağırlık farklı**
- **6/23 bağlantı tipi farklı**
- Şöntte 2 diğer ürün GA5004, GA5006 için katalog kodu/teknik kimliği doğrulanamadı (teknik teyit gerekli).
- 17 fiziksel numune adayının **9 Şönt örneğinde ölçü farkı**, **6 Şönt örneğinde ağırlık farkı** bulundu. Diğer 8 Harmonik numune adayında kontrol edilen ölçü ve ağırlık aynıydı.

### Öne çıkan numuneler
| Stok kodu | Kaynak ölçü (mm) | Üretici 2026/12 (mm) | Kaynak kg | Üretici kg | Bağlantı uyuşmazlığı |
|---|---|---|---:|---:|---|
| GA5002 | 150×125×121 | 150×125×110 | 9 | 8 | Yok |
| GA5102 | 150×125×121 | 150×125×120 | 9 | 9,5 | Yok |
| GA5104 | 210×315×145 | 210×270×180 | 20 | 20 | Yok |
| GA5106 | 255×315×155 | 260×330×200 | 32 | 34 | Yok |
| GA5108 | 290×365×205 | 290×380×250 | 62 | 58 | **Bara M10 → Bara M8** |
| GA5204 | 215×265×144 | 240×225×100 | 17 | 17 | Yok |
| GA5207 | 380×315×155 | 370×330×190 | 48 | 48 | **Pabuç M10 → Bara M8** |
| GA5209 | 380×315×175 | 390×330×220 | 63 | 67 | Yok |
| GA5212 | 530×420×260 | 520×430×290 | 173 | 170 | Yok |

Diğer **4 bağlantı farkı**: GA5105 (Pabuç M10 → Pabuç M8), GA5107 (Bara M10 → Bara M8), GA5205 (Pabuç M8 → Klemens), GA5206 (Pabuç M8 → Klemens).

### Diğer teknik kapsam uyarıları
- SRT 20/25 kVAr (GA5210, GA5211) kaynakta GA5211 referansına bağlıdır, fakat GA5211 17 satın alma/inceleme adayında **yer almıyor**. Bu alt grubun temsil kabiliyeti doğrulanmalı; otomatik 18. numune kararı verilmemeli.
- G/GG varyantları ve siparişe özel ürünlerde üretici standart baz ürününün katalog değerleri **aynı fiziksel tasarım anlamına gelmez**; teknik reçete istenmeli.
- HRM ürünlerinin p=%5,67 / %7 / %14 sınıfları tek `HRM` üst başlığı altında görülebiliyor. Numune önerileri yalnız HRM %7 örneklerinden oluşuyor; diğer p sınıflarının yapı eşdeğerliği varsayılmamalı.
- `plan2027-detail.js` içindeki eski "5/5 teknik alan uyumlu" ifadesi **yanlıştı**, bu denetimde kaldırıldı. `plan2027-samples.js` Şönt katalog durumunda fark uyarısı gösteriyor. **Hiçbir kaynak sayısal değer otomatik değiştirilmedi.**

## Karar
17 aday **kaynak önerilerine sadık**, fakat bunların **asgari/yeterli numune seti olduğu kanıtlanmış değil**. En azından Şönt teknik ölçü, kg ve bağlantı kaynak farkları için ürün revizyonu/BOM/teknik çizim teyidi yapılmadan numune satın alma ve makine kapasitesi kilitlenmemeli. Farkların katalog revizyonu mu yoksa kayıt hatası mı olduğu üreticiden teyit edilmeli.

**Kaynaklar:** Üretici PDF `https://www.gruparge.com/fl/tr`; dahili numune matrisi `Reaktor_Ortak_Uretim_ve_Numune_Matrisi_2026.xlsx`.