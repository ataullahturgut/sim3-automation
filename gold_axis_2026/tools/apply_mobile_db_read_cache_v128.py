from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
APP=ROOT/'apps'/'gold_control_mobile_v1.py'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    n=text.count(old)
    if n!=1:
        raise SystemExit(f'EXPECTED_EXACTLY_ONE_MATCH:{label}:{n}')
    return text.replace(old,new,1)

text=APP.read_text(encoding='utf-8')
anchor='''@st.cache_data(ttl=1800, show_spinner=False)\ndef get_gvz(): return fetch_gvz_latest()\n'''
cache_block='''@st.cache_data(ttl=1800, show_spinner=False)\ndef get_gvz(): return fetch_gvz_latest()\n\n# Navigation reruns must not reopen the same read-only Neon queries. The cache\n# contains display/evidence rows only, expires quickly, and never performs writes.\n@st.cache_data(ttl=30, show_spinner=False)\ndef get_decision_cached(database_url: str): return fetch_current_decision_state(database_url)\n@st.cache_data(ttl=30, show_spinner=False)\ndef get_decision_history_cached(database_url: str): return fetch_decision_history(database_url)\n@st.cache_data(ttl=30, show_spinner=False)\ndef get_runtime_cached(database_url: str): return fetch_runtime_observability(database_url)\n@st.cache_data(ttl=30, show_spinner=False)\ndef get_current_forecast_cached(database_url: str): return fetch_current_forecast(database_url)\n@st.cache_data(ttl=30, show_spinner=False)\ndef get_forecast_history_cached(database_url: str): return fetch_forecast_history(database_url)\n@st.cache_data(ttl=30, show_spinner=False)\ndef get_latest_experts_cached(database_url: str, forecast_track: str): return fetch_latest_expert_forecasts(database_url,forecast_track)\n@st.cache_data(ttl=30, show_spinner=False)\ndef get_expert_history_cached(database_url: str, forecast_track: str): return fetch_expert_forecast_history(database_url,forecast_track)\n'''
text=replace_once(text,anchor,cache_block,'cache wrappers')
old='''url=db_url()\ndecision=safe_call(lambda:fetch_current_decision_state(url),None)\ndecision_rows=safe_call(lambda:fetch_decision_history(url),[]) if url else []\nruntime_obs=safe_call(lambda:fetch_runtime_observability(url),None)\nforecast=safe_call(lambda:fetch_current_forecast(url),None) if url else None\nforecast_rows=safe_call(lambda:fetch_forecast_history(url),[]) if url else []\nmonth_end_experts=safe_call(lambda:fetch_latest_expert_forecasts(url,TRACK_MONTH_END),[]) if url else []\nearly_experts=safe_call(lambda:fetch_latest_expert_forecasts(url,TRACK_EARLY_INDICATIVE),[]) if url else []\nmonth_end_history=safe_call(lambda:fetch_expert_forecast_history(url,TRACK_MONTH_END),[]) if url else []\nearly_history=safe_call(lambda:fetch_expert_forecast_history(url,TRACK_EARLY_INDICATIVE),[]) if url else []\n'''
new='''url=db_url()\ndecision=safe_call(lambda:get_decision_cached(url),None)\ndecision_rows=safe_call(lambda:get_decision_history_cached(url),[]) if url else []\nruntime_obs=safe_call(lambda:get_runtime_cached(url),None)\nforecast=safe_call(lambda:get_current_forecast_cached(url),None) if url else None\nforecast_rows=safe_call(lambda:get_forecast_history_cached(url),[]) if url else []\nmonth_end_experts=safe_call(lambda:get_latest_experts_cached(url,TRACK_MONTH_END),[]) if url else []\nearly_experts=safe_call(lambda:get_latest_experts_cached(url,TRACK_EARLY_INDICATIVE),[]) if url else []\nmonth_end_history=safe_call(lambda:get_expert_history_cached(url,TRACK_MONTH_END),[]) if url else []\nearly_history=safe_call(lambda:get_expert_history_cached(url,TRACK_EARLY_INDICATIVE),[]) if url else []\n'''
text=replace_once(text,old,new,'shared DB reads')
text=replace_once(text,
"historical_replay_experts=safe_call(lambda:fetch_latest_expert_forecasts(url,TRACK_HISTORICAL_REPLAY),[]) if url else []",
"historical_replay_experts=safe_call(lambda:get_latest_experts_cached(url,TRACK_HISTORICAL_REPLAY),[]) if url else []",
'replay latest cached')
text=replace_once(text,
"historical_replay_history=safe_call(lambda:fetch_expert_forecast_history(url,TRACK_HISTORICAL_REPLAY),[]) if url else []",
"historical_replay_history=safe_call(lambda:get_expert_history_cached(url,TRACK_HISTORICAL_REPLAY),[]) if url else []",
'replay history cached')
APP.write_text(text,encoding='utf-8')
print('MOBILE_DB_READ_CACHE_V128_PATCH_PASS')
