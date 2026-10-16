# V20 Audit R2 — İkinci bağımsız denetim sonrası R1 raporuna DÜZELTME
2026-10-16 | Ön kayıt: V20_R2_PREREG_20261016.md (ilk commit, R2 kodundan önce).

## R1 kabul cümlelerinin geri çekilmesi

1. R1 ve V18 ekonomik sonuçları aynı tam sayı hassasiyetiyle karşılaştırıldığında önceki 64 senaryoda farklılık yoktur: rapordaki 1 iyi / 2 kötü sadece dört ve üç ondalıkla yuvarlanmış finansal gösterim değerlerinden kaynaklanır. **64/64 ekonomik eşit** olarak okunmalı. Gerçek XAU testi yapılmadı.
2. R1 maxDrawdownPct:15 verilmesi otomatik kuralda zorunlu satışı kaldırdığı için, explicit-15 alert deneyindeki 238.623 USD ortalama sonuç limitsiz R1 ile aynı kararlardan oluşur. Bir risk limitinin başarısı veya %15 DD garantisi değildir. %15 raporlanır ama zorunlu uygulanmaz.
3. enforceEntryRiskBudget:true opsiyonel eski R1 kuralı 'current nav * exp(-tail) < peak*(1-DD)' olduğu için CASH NAV geçmiş peak'in altına girdiyse kalıcı BUY yasağı oluşturabilir. Bu işlev R2'de kullanılmaz; geçmiş NAV/peak'e göre veto yerine sinyal anında risk hedefi için koşullu ileriye dönük ve bounded skor cezası kullanılır. Bu da gerçek DD limiti garanti etmez.
4. Eski shadow uzman R1'de salt STRESS=>SELL ve RALLY=>BUY idi; hakikaten durumların büyük bölümünde V18'e kıyasla beklenen tek-adım getiri ve ücretten sonra negatif kaldı. V20 R1'de 10.813 etiket olması uzmanının alfa yarattığı anlamına gelmez. Gölge uzman karar yetkisi kazanmadı.
5. 1 ve 2 banka aralıklı karşı olgusal net getiri, ekstra pozisyonun taşıdığı gerçek tüm süreye göre işlem ücretini amortize etmeyi göstermez. Bu nedenle R2 kodu iki ayrı bağımsız, kendi işlemi ve ücreti olan tam portföy içerir. Böylece risk uzmanı bazen sadece nakitteyse bile ücret harcamamış olur; aynı portföyün getirisi, gerçekten tuttuğu süre boyunca birikir.
6. R1'in yumuşak korumayı kullanıcı limitini sonradan aşmakla aynı görmesi hatalıydı. Kullanıcı onayı olmadan 'sert maxDD garanti stop' ilan edilmeyecek. R2 ALERT/soft-penalty ayrımı PREREG'de baştan donduruldu.

## Kabul yorumu
R2 teknik testleri ile R2'nin gerçek kurgu ekonomideki performansı iki ayrı başlıkta raporlanmalıdır.
R2 soft-penalty modu, kullanıcı isteğine uygun bir risk hedefine yaklaşım önerisidir, halen istatistiksel kalibrasyon ve gerçek banka spread kontrolü gerektirir.
Eski V18, orijinal V20 ve R1 sonuçlarının hiçbiri değiştirilmedi; yalnız yeni R2 dalında bu yanlış yorumlar düzeltiliyor.