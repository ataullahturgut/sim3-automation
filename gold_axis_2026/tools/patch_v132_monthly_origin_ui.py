from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "gold_axis_2026/apps/gold_control_mobile_v1.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly 1 match, got {count}")
    return text.replace(old, new, 1)


def main() -> None:
    text = APP.read_text(encoding="utf-8")

    replacements = [
        (
            "state empty title",
            'return empty_html("31 AĞUSTOS STATE REPLAY OKUNAMADI","Production Evidence Spine ve deployment replay snapshot kullanılamıyor.")',
            'return empty_html("31 AĞUSTOS ORIGIN YÖN SNAPSHOT OKUNAMADI","Production Evidence Spine ve deployment origin snapshot kullanılamıyor.")',
        ),
        (
            "state title",
            '"<div class=\'gc-card\' style=\'margin-top:.7rem\'><div class=\'gc-section-title\'>31 AĞUSTOS 2026 YÖN / RİSK STATE REPLAY</div>"',
            '"<div class=\'gc-card\' style=\'margin-top:.7rem\'><div class=\'gc-section-title\'>EYLÜL 2026 · 31 AĞUSTOS ORIGIN YÖN / RİSK SNAPSHOT</div>"',
        ),
        (
            "state provenance",
            '+f"<div class=\'gc-footnote\'><b>HISTORICAL REPLAY · PROSPECTIVE DEĞİL</b> · state boundary 31.08.2026 17:00 ET · kaynak: {esc(source)}. Bu durumlar H=1 fiyat tahmini değildir ve current yön oyu/kararı değiştirmez.</div>"',
            '+f"<div class=\'gc-footnote\'><b>31 AĞUSTOS ORIGIN · EYLÜL AY-AÇILIŞ CONTEXT</b> · information boundary 31.08.2026 17:00 ET · kaynak: {esc(source)}. <span style=\'color:var(--gc-muted)\'>Audit: 4 Eylül\'de yeniden hesaplandı · HISTORICAL_REPLAY / ORIGIN_RECONSTRUCTION.</span> Bu durumlar H=1 fiyat tahmini değildir ve current yön oyu/kararı değiştirmez.</div>"',
        ),
        (
            "state blocker title",
            '+"<div class=\'gc-track-head\'><b>REPLAY\'DE HALEN BLOCKED / ARCHIVED</b><span class=\'gc-track-pill\'>FAIL-CLOSED</span></div>"',
            '+"<div class=\'gc-track-head\'><b>31 AĞUSTOS ORIGIN\'DE HALEN BLOCKED / ARCHIVED</b><span class=\'gc-track-pill\'>FAIL-CLOSED</span></div>"',
        ),
        (
            "expansion empty title",
            'return empty_html("31 AĞUSTOS GENİŞLETİLMİŞ REPLAY OKUNAMADI","Causal Patch / Emergency / BOCPD successor immutable replay evidence kullanılamıyor.")',
            'return empty_html("31 AĞUSTOS ORIGIN MOTOR SETİ OKUNAMADI","Causal Patch / Emergency / BOCPD successor immutable origin-reconstruction evidence kullanılamıyor.")',
        ),
        (
            "expansion title",
            '+"<div class=\'gc-section-title\'>31 AĞUSTOS REPLAY · RECOVERED / SUCCESSOR CONTEXT</div>"',
            '+"<div class=\'gc-section-title\'>EYLÜL 2026 · 31 AĞUSTOS ORIGIN MOTOR SETİ</div>"',
        ),
        (
            "expansion provenance",
            '+f"<div class=\'gc-footnote\'><b>HISTORICAL_REPLAY · PROSPECTIVE ISSUED DEĞİL</b> · information boundary 31.08.2026 17:00 ET · kaynak: {esc(source)}.</div>"',
            '+f"<div class=\'gc-footnote\'><b>EYLÜL AY-AÇILIŞ REFERANSI · 31 AĞUSTOS ORIGIN</b> · information boundary 31.08.2026 17:00 ET · kaynak: {esc(source)}. <span style=\'color:var(--gc-muted)\'>Audit provenance: 4 Eylül\'de yeniden hesaplandı · HISTORICAL_REPLAY / ORIGIN_RECONSTRUCTION; 31 Ağustos\'ta issued edildi iddiası yoktur.</span></div>"',
        ),
        (
            "inventory replay label",
            '+f"<div style=\'font-size:.58rem;font-weight:900;color:#8a5b00\'>{esc(ref.get(\'label\'))} · REPLAY · PROSPECTIVE DEĞİL</div>"',
            '+f"<div style=\'font-size:.58rem;font-weight:900;color:#8a5b00\'>{esc(ref.get(\'label\'))} · EYLÜL / 31 AĞUSTOS ORIGIN</div>"',
        ),
        (
            "waiting origin note",
            'return "Uygun ay-sonu originini bekliyor. İlk meşru prospective aday: Eylül sonu → Ekim 2026 H=1; yalnız issuer/PIT gate\'leri geçerse. 31 Ağustos replay referansı ayrı HISTORICAL_REPLAY evidence katmanıdır."',
            'return "Eylül için 31 Ağustos origin referansı mevcut. İleri operasyonel durum bir sonraki aylık döngüyü bekliyor: 30 Eylül origin → Ekim 2026 H=1; yalnız issuer/PIT gate\'leri geçerse. Eylül referansının audit sınıfı ORIGIN_RECONSTRUCTION / HISTORICAL_REPLAY olarak korunur."',
        ),
        (
            "waiting emergency note",
            'return "İlk governed prospective CAUSAL_PATCH expert referansını bekliyor. İlk meşru aday: Eylül sonu → Ekim 2026 H=1. 31 Ağustos historical replay Emergency state\'i bu forward requirement\'ı karşılamaz."',
            'return "Eylül ay-açılış Emergency state\'i 31 Ağustos origin referansıyla mevcut. İleri operasyonel lane, 30 Eylül origin → Ekim için zamanında yayımlanacak governed CAUSAL_PATCH referansını bekliyor. Reconstruction forward prospective kanıt yerine geçmez."',
        ),
        (
            "gorunum emergency level",
            'html_row("Emergency · Level",f"{display_state(aug31_replay_expansion.get(\'emergency_level\'),\'—\')} · 31 AĞUSTOS REPLAY","gc-warning")',
            'html_row("Emergency · Level",f"{display_state(aug31_replay_expansion.get(\'emergency_level\'),\'—\')} · EYLÜL / 31 AĞUSTOS ORIGIN","gc-warning")',
        ),
        (
            "gorunum emergency reversal",
            'html_row("Emergency · Reversal",f"{display_state(aug31_replay_expansion.get(\'emergency_reversal\'),\'—\')} · 31 AĞUSTOS REPLAY","gc-warning")',
            'html_row("Emergency · Reversal",f"{display_state(aug31_replay_expansion.get(\'emergency_reversal\'),\'—\')} · EYLÜL / 31 AĞUSTOS ORIGIN","gc-warning")',
        ),
        (
            "page subtitle",
            'page_head("TAHMİN","Mevcut hedef ay için geçerli replay/reference ve gelecek H=1 kanonik sonuçları ayrı evidence katmanlarında gösterilir.",updated);',
            'page_head("TAHMİN","Her ayın tahmin ve ay-açılış yön referansı bir önceki tamamlanmış ay-sonu originine bağlıdır. Reconstruction provenance audit katmanında ayrıca gösterilir.",updated);',
        ),
        (
            "hero value block",
            'mom_value=fmt_num(None if not mom else mom.get("forecast_value"),2)\n        rw_value=fmt_num(None if not rw else rw.get("forecast_value"),2)\n        hero_title=f"{mom_value} / {rw_value} USD"\n        hero_sub=f"3M Momentum / Random Walk · Hedef: {replay_target} · Eylül kapanana kadar ay-içi referans · 31 Ağustos bilgi kesiti"\n        badge="REPLAY · PROSPECTIVE ISSUED DEĞİL"',
            'mom_value=fmt_num(None if not mom else mom.get("forecast_value"),2)\n        rw_value=fmt_num(None if not rw else rw.get("forecast_value"),2)\n        patch_value=fmt_num(None if not aug31_replay_expansion else aug31_replay_expansion.get("causal_patch_forecast"),2)\n        hero_title=f"{mom_value} / {rw_value} / {patch_value} USD"\n        hero_sub=f"3M Momentum / Random Walk / Causal Patch · Hedef: {replay_target} · 31 Ağustos bilgi sınırı"\n        badge="31 AĞUSTOS ORIGIN · RECONSTRUCTION"',
        ),
        (
            "hero kicker",
            'hero_kicker="EYLÜL 2026 H=1 · CURRENT-MONTH REFERENCE"',
            'hero_kicker="EYLÜL 2026 · 31 AĞUSTOS ORIGIN"',
        ),
        (
            "hero direction label",
            'direction_label="31 AĞUSTOS AY-AÇILIŞ YÖN CONTEXT"',
            'direction_label="EYLÜL AY-AÇILIŞ YÖN MOTORLARI"',
        ),
        (
            "hero origin label",
            'origin_label="REPLAY ORIGIN"',
            'origin_label="ORIGIN BOUNDARY"',
        ),
        (
            "replay empty",
            'empty_html("EYLÜL 2026 REPLAY KAYDI YOK","Production Evidence Spine üzerinde HISTORICAL_REPLAY kaydı okunamadı.")',
            'empty_html("EYLÜL 2026 · 31 AĞUSTOS ORIGIN KAYDI YOK","Production Evidence Spine üzerinde Eylül için origin-reconstruction kaydı okunamadı.")',
        ),
        (
            "replay main section",
            'st.markdown("<div class=\'gc-replay\'><div class=\'gc-replay-head\'><strong>EYLÜL 2026 HISTORICAL REPLAY</strong><span class=\'gc-replay-pill\'>REPLAY · PROSPECTIVE DEĞİL</span></div><div class=\'gc-footnote\'><b>H=1 EXPERT REPLAY</b> · Aşağıdaki USD değerleri Eylül aylık ortalama fiyat replay\'idir.</div>"+replay_db_body+aug31_state_replay_html(aug31_state_replay,aug31_replay_expansion)+aug31_replay_expansion_html(aug31_replay_expansion)+"<div class=\'gc-footnote\' style=\'margin-top:.65rem\'><b>Resmî prospective issuance durumu:</b> NOT_ISSUED_MISSED_2026_08_31_ORIGIN. H=1 replay ile 31 Ağustos EOD state replay ayrı evidence katmanlarıdır; canonical forecast, selector, ensemble veya karar otoritesi yaratmazlar. Ancak her ikisinin target context\'i 2026-09 olduğu için Eylül kapanana kadar mevcut ay için referans/context olarak görünür kalırlar. Provenance HISTORICAL_REPLAY olarak korunur.</div></div>",unsafe_allow_html=True)',
            'st.markdown("<div class=\'gc-replay\'><div class=\'gc-replay-head\'><strong>EYLÜL 2026 · 31 AĞUSTOS ORIGIN</strong><span class=\'gc-replay-pill\'>MONTH-OPEN REFERENCE</span></div><div class=\'gc-footnote\'><b>H=1 AY-AÇILIŞ EXPERT SETİ</b> · Aşağıdaki USD değerleri 31 Ağustos bilgi sınırıyla Eylül 2026 aylık ortalama fiyatı için ayrı expert referanslarıdır; winner/ortalama değildir.</div>"+replay_db_body+aug31_state_replay_html(aug31_state_replay,aug31_replay_expansion)+aug31_replay_expansion_html(aug31_replay_expansion)+"<div class=\'gc-footnote\' style=\'margin-top:.65rem\'><b>Audit provenance:</b> Bu Eylül origin seti 4 Eylül\'de 31 Ağustos bilgi sınırıyla yeniden hesaplandı; bu nedenle evidence sınıfı ORIGIN_RECONSTRUCTION / HISTORICAL_REPLAY olarak korunur. Bu, 31 Ağustos\'ta gerçekten issued edildi iddiası değildir. Bir sonraki normal aylık döngü: <b>30 Eylül origin → Ekim 2026</b>. Canonical forecast, selector, ensemble veya karar otoritesi yaratılmaz.</div></div>",unsafe_allow_html=True)',
        ),
        (
            "history caption",
            'st.caption("REPLAY · PROSPECTIVE DEĞİL · official prospective status: NOT_ISSUED_MISSED_2026_08_31_ORIGIN")',
            'st.caption("ORIGIN_RECONSTRUCTION / HISTORICAL_REPLAY · target/origin: 31 Ağustos → Eylül · gerçek hesaplama/persistence tarihi korunur")',
        ),
    ]

    for label, old, new in replacements:
        text = replace_once(text, old, new, label)

    APP.write_text(text, encoding="utf-8")
    print(f"PATCH_V132_MONTHLY_ORIGIN_UI_PASS replacements={len(replacements)}")


if __name__ == "__main__":
    main()
