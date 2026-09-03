from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
APP=ROOT/'apps'/'gold_control_mobile_v1.py'
QA=ROOT/'apps'/'mobile_viewport_qa.py'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    n=text.count(old)
    if n!=1:
        raise SystemExit(f'EXPECTED_EXACTLY_ONE_MATCH:{label}:{n}')
    return text.replace(old,new,1)

app=APP.read_text(encoding='utf-8')
app=replace_once(app,
"    TRACK_EARLY_INDICATIVE,\n    TRACK_MONTH_END,\n",
"    TRACK_EARLY_INDICATIVE,\n    TRACK_HISTORICAL_REPLAY,\n    TRACK_MONTH_END,\n",
'import replay track')
app=replace_once(app,
"early_history=safe_call(lambda:fetch_expert_forecast_history(url,TRACK_EARLY_INDICATIVE),[]) if url else []\n",
"early_history=safe_call(lambda:fetch_expert_forecast_history(url,TRACK_EARLY_INDICATIVE),[]) if url else []\nhistorical_replay_experts=[]\nhistorical_replay_history=[]\n",
'initialize replay ledgers without eager DB read')
app=replace_once(app,
"elif nav==\"↗ Tahmin\":\n    expert_update=",
"elif nav==\"↗ Tahmin\":\n    historical_replay_experts=safe_call(lambda:fetch_latest_expert_forecasts(url,TRACK_HISTORICAL_REPLAY),[]) if url else []\n    expert_update=",
'lazy load replay experts on Tahmin')
app=replace_once(app,
"else:\n    latest=month_end_history[0].get(\"as_of\") if month_end_history else (early_history[0].get(\"as_of\") if early_history else None); page_head(\"GEÇMİŞ\"",
"else:\n    historical_replay_history=safe_call(lambda:fetch_expert_forecast_history(url,TRACK_HISTORICAL_REPLAY),[]) if url else []\n    latest=month_end_history[0].get(\"as_of\") if month_end_history else (early_history[0].get(\"as_of\") if early_history else None); page_head(\"GEÇMİŞ\"",
'lazy load replay history on Gecmis')
replay_card="""    replay_db_body=(expert_cards(historical_replay_experts) if historical_replay_experts else empty_html(\"EYLÜL 2026 REPLAY KAYDI YOK\",\"Production Evidence Spine üzerinde HISTORICAL_REPLAY kaydı okunamadı.\"))
    st.markdown(\"<div class='gc-replay'><div class='gc-replay-head'><strong>EYLÜL 2026 HISTORICAL REPLAY</strong><span class='gc-replay-pill'>REPLAY · PROSPECTIVE DEĞİL</span></div>\"+replay_db_body+\"<div class='gc-footnote' style='margin-top:.65rem'><b>Resmî prospective durum:</b> NOT_ISSUED_MISSED_2026_08_31_ORIGIN. Bu satırlar 31 Ağustos bilgi kesitiyle sonradan yeniden hesaplanmıştır; canonical forecast, selector, ensemble veya yön oyu değildir.</div></div>\",unsafe_allow_html=True)
"""
app=replace_once(app,
"    st.markdown(\"<div class='gc-card'><div class='gc-section-title'>SENARYOLAR</div>\"+empty_html(\"SENARYOLAR HENÜZ YAYIMLANMADI\",SCENARIO_STATUS)+\"<div class='gc-footnote'>Kanonik senaryo kontratı açılmadan baz/iyimser/kötümser sayı üretilmez.</div></div>\",unsafe_allow_html=True)\n",
replay_card+"    st.markdown(\"<div class='gc-card'><div class='gc-section-title'>SENARYOLAR</div>\"+empty_html(\"SENARYOLAR HENÜZ YAYIMLANMADI\",SCENARIO_STATUS)+\"<div class='gc-footnote'>Kanonik senaryo kontratı açılmadan baz/iyimser/kötümser sayı üretilmez.</div></div>\",unsafe_allow_html=True)\n",
'insert replay Tahmin card')
history_block="""    rdf=expert_history_frame(historical_replay_history)
    with st.container(border=True):
        st.markdown(\"<div class='gc-section-title'>PRODUCTION HISTORICAL_REPLAY · EYLÜL 2026</div>\",unsafe_allow_html=True)
        if not rdf.empty:
            pivot=rdf.pivot_table(index=\"target_month\",columns=\"expert_id\",values=\"forecast_value\",aggfunc=\"last\").reset_index(); plot_lines(pivot,\"target_month\",[c for c in EXPERT_DISPLAY_ORDER if c in pivot.columns],250)
            cols=[c for c in [\"target_month\",\"expert_id\",\"model_version\",\"forecast_value\",\"evidence_class\",\"forecast_origin\",\"as_of\"] if c in rdf.columns]; table=rdf[cols].copy(); table[\"target_month\"]=table[\"target_month\"].dt.strftime(\"%Y-%m\"); st.dataframe(table,width=\"stretch\",hide_index=True)
            st.caption(\"REPLAY · PROSPECTIVE DEĞİL · official prospective status: NOT_ISSUED_MISSED_2026_08_31_ORIGIN\")
        else: st.markdown(empty_html(\"PRODUCTION HISTORICAL_REPLAY KAYDI YOK\",\"Replay ledger yalnız HISTORICAL_REPLAY evidence ile okunur.\"),unsafe_allow_html=True)
"""
app=replace_once(app,
"    if not replay.empty and {\"actual\",\"patch_r1\",\"vw\",\"mom\",\"rw\"}.issubset(replay.columns):\n",
history_block+"    if not replay.empty and {\"actual\",\"patch_r1\",\"vw\",\"mom\",\"rw\"}.issubset(replay.columns):\n",
'insert replay history DB block')
app=replace_once(app,
"st.write(\"EARLY_INDICATIVE rows:\",len(early_history)); st.write(\"Auto selector:\",AUTO_SELECTOR_STATUS)",
"st.write(\"EARLY_INDICATIVE rows:\",len(early_history)); st.write(\"HISTORICAL_REPLAY rows (active view):\",len(historical_replay_history)); st.write(\"Auto selector:\",AUTO_SELECTOR_STATUS)",
'audit replay count')
APP.write_text(app,encoding='utf-8')

qa=QA.read_text(encoding='utf-8')
qa=replace_once(qa,
'"HISTORICAL_REPLAY","WAITING_ELIGIBLE_MONTH_END_ORIGIN"]',
'"HISTORICAL_REPLAY","REPLAY · PROSPECTIVE DEĞİL","EYLÜL 2026 HISTORICAL REPLAY","NOT_ISSUED_MISSED_2026_08_31_ORIGIN","WAITING_ELIGIBLE_MONTH_END_ORIGIN"]',
'qa Tahmin replay markers')
QA.write_text(qa,encoding='utf-8')
print('SEPTEMBER_REPLAY_UI_V128_PATCH_PASS')
