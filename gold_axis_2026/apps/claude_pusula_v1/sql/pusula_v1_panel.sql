-- PUSULA v1 günlük as-of paneli (Neon Gold Control, salt SELECT).
-- Fiyat zamanı t: EV/Dukascopy 15 dk için bar_start+15 dk; Dukascopy H1 için utc+1 saat (çubuk kapanışı).
-- 2025 çakışmasında iki kaynak ortalama %0,0001 farkla eşleşir; birleşim 2026-01-01 00:00Z'de yapılır.

-- (1) ALTIN: her UTC iş günü için 06:00Z karar fiyatı ve 09:00Z dolum BID/ASK.
-- :y yıl parametresi; çıktı tek satırda kompakt metin: tarih,p06,p06_saat,bid09,ask09;
with marks as (
  select bar_start_utc + interval '15 minutes' as t, bid_close as bid, ask_close as ask
  from gold_research_evduka_xau15m_bidask_candidate
  where bar_start_utc < '2026-01-01'
  union all
  select utc + interval '1 hour', bid_close, ask_close
  from gold_research_dukascopy_xau_h1_monthly_source_candidate_v1
  where utc >= '2026-01-01'
),
days as (
  select d::date as d from generate_series(make_date(:y,1,1), make_date(:y,12,31), interval '1 day') d
  where extract(isodow from d) <= 5 and d <= '2026-09-30'
),
dec as (
  select distinct on (days.d) days.d, (m.bid+m.ask)/2 as p06, m.t as t06
  from days join marks m on m.t > days.d::timestamptz and m.t <= days.d::timestamptz + interval '6 hours'
  order by days.d, m.t desc
),
fil as (
  select days.d, m.bid, m.ask from days join marks m on m.t = days.d::timestamptz + interval '9 hours'
)
select count(*) as n, round(sum(dec.p06)::numeric,3) as sum_p06, round(sum(fil.bid)::numeric,3) as sum_bid,
  string_agg(to_char(days.d,'YYYY-MM-DD')||','||coalesce(round(dec.p06::numeric,3)::text,'')||','||
    coalesce(to_char(dec.t06 at time zone 'UTC','HH24MI'),'')||','||coalesce(round(fil.bid::numeric,3)::text,'')||','||
    coalesce(round(fil.ask::numeric,3)::text,''), ';' order by days.d) as rows
from days left join dec using (d) left join fil using (d);

-- (2) CME: her karar günü için 06:00Z'den önce kapanmış son saatlik çubuğun kapanışı (yaş <= 72 saat) ve sözleşme kodu.
-- ts_event çubuk BAŞLANGICI; kapanış zamanı ts_event+1 saat.
with days as (
  select d::date as d from generate_series(make_date(:y,1,1), make_date(:y,12,31), interval '1 day') d
  where extract(isodow from d) <= 5 and d <= '2026-09-30'
),
c as (
  select symbol, ts_event + interval '1 hour' as t, close, instrument_id
  from gold_research_cme_glbx_futures_2023_2026_h1_5roots_continuous_c
  where symbol in ('NQ.c.0','ZN.c.0','CL.c.0','SI.c.0')
),
a as (
  select distinct on (s.symbol, days.d) s.symbol, days.d, c.close, c.instrument_id
  from days cross join (values ('NQ.c.0'),('ZN.c.0'),('CL.c.0'),('SI.c.0')) s(symbol)
  join c on c.symbol = s.symbol and c.t <= days.d::timestamptz + interval '6 hours'
        and c.t > days.d::timestamptz + interval '6 hours' - interval '72 hours'
  order by s.symbol, days.d, c.t desc
)
select symbol, count(*) as n, round(sum(close)::numeric,4) as sum_close,
  string_agg(to_char(d,'YYMMDD')||','||close::text||','||instrument_id::text, ';' order by d) as rows
from a group by symbol order by symbol;
