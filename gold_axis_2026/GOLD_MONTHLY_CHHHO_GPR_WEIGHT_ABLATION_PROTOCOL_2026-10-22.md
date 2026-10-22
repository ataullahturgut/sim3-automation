# GOLD MONTHLY — ChHHO-ANFIS GPR Ağırlıklarının Bağımsız Katkı Deneyi

**Tarih:** 2026-10-22  
**Durum:** SOURCE/WORKFLOW CREATED; MODEL RUN STARTED; FINAL NUMERIC RESULT PENDING IN WORKFLOW
**Bilimsel rol:** Yeni modelin otomatik terfisi değil, GPR ağırlıklandırma mekanizmasının kontrollü ablasyonu.

## Asıl soru

CURRENT8'in MR+VW bütünlüğünün iyi çalışması GPR'nin tek başına faydalı olduğunu **kanıtlamaz**. Bu deney dört metalin aylık MR girdilerini, origin ve hedef fiyatlarını, modelin 8→5 kural→4 ANFIS mimarisini, Chaotic HHO optimizasyonunu, başlangıç seed'lerini, aynı kronolojik iç kontrolü, eğitim satır kümesini ve metrik sözleşmesini korur. Yalnız **VW günlük log getiri ağırlığı** değişir.

## Üç önceden sabitlenmiş yöntem

| Deney kolu | Günlük getiri özelliği | GPR kullanımı |
|---|---|---|
| `GPR_PIT_CURRENT8` (otorite kontrolü) | `sum(exp(-λ(z)*age)*r) / sum(exp(-λ(z)*age))`, `λ(z)=0.1*exp(-10*z)` | Tahmin ayı origin `p` için `p-1` GPR gözlemi, o origin'in resmî PIT vintage'ından |
| `NO_GPR_EQUAL` | `mean(r)` | Yok |
| `NO_GPR_FIXED_RECENCY` | `sum(exp(-0.05*age)*r)/sum(exp(-0.05*age))` | Yok; `0.05` sabit katsayısı bu deney başlamadan seçildi, sonuçtan öğrenilmez |

- `r`: tamamlanmış origin ayındaki dört metalin ayrı ayrı günlük log getirileri.
- `MR1`: dört metalin önceki iki tamamlanmış aylık ortalamasının log oranı; bütün kollarda aynıdır.
- Tüm kollarda **8 giriş** ve **4 hedef log getirisi** vardır, hiçbiri 4 girdili MR-only/VW-only sonuçlarıyla karıştırılmaz.

## Başarının gerçek ölçümü

1. Yetkili DEV: **2022-04…2024-12, 33 hedef ay**.
2. Kullanılan veri: `GOLD_MONTHLY_DEV_SNAPSHOT_V1_2026-09-28`, payload SHA-256 `2111e394f60d131995273789fc014dc339db4e1b7672095c89117c133879a3eb`. Neon bağlantısı **kapalı**.
3. Her ay `t` için bütün eğitim hedefleri `<t`; rastgele train/test bölünmesi yok. İç kontrol kronolojik.
4. Önce CURRENT8 kodunun özgün özelliklerle **bit-bit `np.array_equal`** eşleşmesi, sonra DEV `ΣAE=1413.0297794085` ve direction `23/33` paritesi zorunlu. Aksi halde işlem başarısız.
5. Üç tam fiyat tahmin serisinden aynı ay bazında `Σ|forecast-actual|`, `MAE`, doğru yön, ay-ay GPR avantajı, 2022/2023/2024 yıllık istikrar, kazandırdığı/kaybettirdiği aylar, medyan eşli AE farkı raporlanır.
6. “GPR tek başına katkılı” sonucu için sadece düşük toplam hata yetmez; GPR'li kolun hata kazanımı, yönü kötüleştirmemesi, en az 2/3 DEV yılında iyileşme, ay bazında kazanımların en az kayıplar kadar olması ve pozitif medyan fayda birlikte denetlenir. İstatistiksel anlamlılık veya ileri doğrulama iddiası **otomatik değil**.
7. **2025 ve 2026 ayları DEV seçiminde kesinlikle kullanılmaz**. Bağımsız dış dönem araştırması, bu üç yöntem DEV sonunda dondurulduktan sonra ve kaynak/protokol paritesi ayrıca sağlandıktan sonra yapılabilir.

## Kod, workflow ve sonuçun kanıt yolu

- Model koşusu: `tools/gold_monthly_chhho_gpr_weight_ablation_v1.py`
- Eşli rapor: `tools/gold_monthly_chhho_gpr_weight_summarize_v1.py`
- GitHub Actions: `.github/workflows/gold-monthly-chhho-gpr-weight-ablation-v1.yml`
- İlk gerçek çalıştırma: [run 39766658131](https://github.com/ataullahturgut/sim3-automation/actions/runs/39766658131)
- Her kol çıktısı: `gpr_weight_<ARM>.json`; birleşik `GOLD_MONTHLY_CHHHO_GPR_WEIGHT_PAIRED_V1.json`.
- İşlem çıkışı dönene kadar **NO_RESULT / NO_CLAIM**.

## Model/uygulama izolasyonu

CURRENT8 canlı ana fiyat modelinin parametreleri, `gold-adaptive-model` uygulama görünümleri ve geçmiş raporları **değiştirilmez**. Bu çalışma yalnız bilimsel deneydir. DEV kazananının 2025–2026'da yeniden seçilmesi veya otomatik yönlendirme yapılması yasaktır.
