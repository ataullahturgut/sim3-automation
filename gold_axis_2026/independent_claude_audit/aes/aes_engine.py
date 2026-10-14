"""CLAUDE_INDEPENDENT — Adaptive Evidence System (AES v1), as preregistered in
CLAUDE_ADAPTIVE_EVIDENCE_SYSTEM_PREREG.md (commit e7be8d6).

Inputs (data dir, NOT committed: derived from private Neon prices):
  sessions.txt  YYMMDD,DDHHMM,close_cents;...         NY17 session closes (MID)
  dec1.txt dec2.txt YYMMDD[A|B],mid_cents,mid-mid24h_cents,spread_cents;...  A=06:00Z, B=13:45Z
  macro.txt     YYMMDDHHMM,type,s_nfp,s_ahe,s_un,s_cpi,s_ccpi,s_fomc,r15bp,r60bp,r240bp,f10bp;...
Repo inputs: Databento .n.0 hourly (ZN/NQ), SI.n.0 1m, GVZ daily.
Usage: python3 -I aes_engine.py DATA_DIR REPO_GOLD_AXIS_DIR OUT_JSON
"""
import sys, json, math, bisect, datetime as dt
import numpy as np, pandas as pd

DATA, REPO, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
# v1.0 = as first coded (bug: asleep experts charged nothing); v1.1 = sleeping-experts Hedge as named in PREREG
SLEEPING_FIX = len(sys.argv) > 4 and sys.argv[4] == 'v1.1'
UTC = dt.timezone.utc
H, ETA, HALF, K_EVT, K_STATE, COST, EDGE = 10, 0.05, 250, 7, 25, 0.0165, 0.25
FEE = 0.008

def d6(s):
    return dt.date(2000 + int(s[:2]), int(s[2:4]), int(s[4:6]))

# ---------- sessions ----------
S = []
for x in open(f'{DATA}/sessions.txt').read().strip().split(';'):
    a, b, c = x.split(',')
    d = d6(a)
    S.append((d, dt.datetime(d.year, d.month, d.day, int(b[2:4]), int(b[4:6]), tzinfo=UTC), int(c) / 100))
S_close_ts = [s[1] for s in S]
C = np.array([s[2] for s in S])
LR = np.r_[np.nan, np.diff(np.log(C))]

def sess_idx(t):  # last session with close_ts <= t
    return bisect.bisect_right(S_close_ts, t) - 1

# ---------- decisions ----------
D = []
for f in ('dec1.txt', 'dec2.txt'):
    for x in open(f'{DATA}/{f}').read().strip().split(';'):
        a, m, dl, sp = x.split(',')
        d = d6(a)
        hh, mm = (6, 0) if a[6] == 'A' else (13, 45)
        mid = int(m) / 100
        D.append(dict(t=dt.datetime(d.year, d.month, d.day, hh, mm, tzinfo=UTC), mid=mid, mid24=mid - int(dl) / 100, spr=int(sp) / 100))
D.sort(key=lambda r: r['t'])

# ---------- macro events ----------
E = []
for x in open(f'{DATA}/macro.txt').read().strip().split(';'):
    p = x.split(',')
    ts = dt.datetime(2000 + int(p[0][:2]), int(p[0][2:4]), int(p[0][4:6]), int(p[0][6:8]), int(p[0][8:10]), tzinfo=UTC)
    f = lambda v: float(v) if v != '' else None
    comps = dict(nfp=f(p[2]), ahe=f(p[3]), un=f(p[4]), cpi=f(p[5]), ccpi=f(p[6]), fomc=f(p[7]))
    hawk = sum(1 for k, v in comps.items() if v is not None and ((v > 0 and k != 'un') or (v < 0 and k == 'un')))
    dove = sum(1 for k, v in comps.items() if v is not None and ((v < 0 and k != 'un') or (v > 0 and k == 'un')))
    r240, f10 = int(p[10]) / 1e4, (int(p[11]) / 1e4 if p[11] != '' else None)
    si = bisect.bisect_right(S_close_ts, ts)  # first session closing after ts
    mat = S_close_ts[si + 9] if si + 9 < len(S_close_ts) else None
    E.append(dict(ts=ts, type=p[1], hawk=hawk, dove=dove, r15=int(p[8]) / 1e4, r60=int(p[9]) / 1e4, r240=r240,
                  rem10=((1 + f10) / (1 + r240) - 1) if f10 is not None else None, mature=mat))

# ---------- cross-market (repo) ----------
hr = pd.read_csv(f'{REPO}/GOLD_DATABENTO_GLBX_OHLCV1H_N_RAW_2022_2024.csv.gz')
hr['ts'] = pd.to_datetime(hr.ts_event, utc=True) + pd.Timedelta('1h')  # availability time = bar end
HRS = {r: g.set_index('ts').close.sort_index() for r, g in hr.groupby(hr.symbol.str[:2])}
si1 = pd.read_csv(f'{REPO}/GOLD_DATABENTO_SI_PL_OHLCV1M_N0_RAW_2022_2024.csv.gz', usecols=['ts_event', 'symbol', 'close'])
si1 = si1[si1.symbol == 'SI.n.0']
SI = pd.Series(si1.close.values, index=pd.to_datetime(si1.ts_event, utc=True) + pd.Timedelta('1min')).sort_index()
gvz = pd.read_csv(f'{REPO}/GOLD_GVZCLS_RAW_2021_2025.csv')
gvz['date'] = pd.to_datetime(gvz.date).dt.date
GVZ_D, GVZ_V = list(gvz.date), list(gvz.value)

def asof(series, t, maxlag):
    i = series.index.searchsorted(pd.Timestamp(t), side='right') - 1
    if i < 0 or pd.Timestamp(t) - series.index[i] > maxlag:
        return None
    return float(series.iloc[i])

def ret24(series, t, maxlag=pd.Timedelta('3h')):
    a, b = asof(series, t, maxlag), asof(series, t - dt.timedelta(hours=24), pd.Timedelta('72h'))
    return None if a is None or b is None else a / b - 1

# ---------- features ----------
for r in D:
    t = r['t']; i = sess_idx(t); r['si'] = i
    if i < 60:
        r['ok'] = False; continue
    r['ok'] = True
    c = C[i]
    r['trend20'] = c / C[i - 19:i + 1].mean() - 1
    r['mom10'] = c / C[i - 10] - 1
    r['mom20'] = c / C[i - 20] - 1
    r['dd20'] = c / C[i - 19:i + 1].max() - 1
    sd = np.nanstd(LR[i - 59:i + 1], ddof=1)
    r['z1'] = (r['mid'] / c - 1) / sd
    r['z3'] = (r['mid'] / C[i - 3] - 1) / (sd * math.sqrt(3))
    r['g5'] = r['mid'] / C[i - 5] - 1
    r['g24'] = r['mid'] / r['mid24'] - 1
    r['si24'] = ret24(SI, t, pd.Timedelta('30min'))
    r['zn24'] = ret24(HRS['ZN'], t)
    r['nq24'] = ret24(HRS['NQ'], t)
    k = bisect.bisect_left(GVZ_D, t.date()) - 1
    r['gvz5'] = (GVZ_V[k] - GVZ_V[k - 5]) if k >= 5 else None
    j10, j20 = i + H, i + 20  # H-th session close AFTER t: sessions i+1..i+H
    r['r10'] = C[j10] / r['mid'] - 1 if j10 < len(C) else None
    r['m10'] = S_close_ts[j10] if j10 < len(C) else None
    r['r20'] = C[j20] / r['mid'] - 1 if j20 < len(C) else None

MOD = ['M1_TREND', 'M2_MOM', 'M3_REV', 'M4_NEWS', 'M5a_EVT_ANALOG', 'M5b_STATE_ANALOG', 'M6_SILVER', 'M7_RATES', 'M8_RISK', 'M9_GVZ']
clip = lambda x: max(-1.0, min(1.0, x))

def recent_event(r):
    t, i = r['t'], r['si']
    lo = S_close_ts[i - 2]  # within current + previous two sessions
    cand = [e for e in E if lo < e['ts'] <= t - dt.timedelta(minutes=60)]
    if not cand:
        return None, 0
    e = cand[-1]
    w = 1.0 if e['ts'] > S_close_ts[i] else 0.5
    return e, w

def event_analog(e, r, t):
    lib = [x for x in E if x['mature'] is not None and x['mature'] <= t and x['rem10'] is not None and x is not e]
    if len(lib) < K_EVT:
        return 0.0, []
    def feat(x, pre):
        return np.array([1.0 if x['type'] == e['type'] else 0.0, np.sign(x['hawk'] - x['dove']), x['r60'] / 0.01, pre[0] / 0.02, pre[1] / 0.02])
    def pre_of(x):
        j = bisect.bisect_right(S_close_ts, x['ts']) - 1
        return (C[j] / C[j - 19:j + 1].mean() - 1, C[j] / C[j - 10] - 1) if j >= 20 else (0.0, 0.0)
    q = feat(e, (r['trend20'], r['mom10']))
    dist = sorted(((float(np.sum((feat(x, pre_of(x)) - q) ** 2)), x) for x in lib), key=lambda z: z[0])[:K_EVT]
    m = float(np.mean([x['rem10'] for _, x in dist]))
    return clip(m / 0.015), [(x['ts'].strftime('%Y-%m-%d %H:%M'), x['type'], round(100 * x['r60'], 2), round(100 * x['rem10'], 2)) for _, x in dist]

STATE_F = ['trend20', 'mom10', 'mom20', 'dd20', 'z1', 'z3']

def votes(r, t, lib_state):
    v = {m: 0.0 for m in MOD}; info = {}
    if np.sign(r['trend20']) == np.sign(r['mom10']):
        v['M1_TREND'] = float(np.sign(r['trend20']))
    v['M2_MOM'] = clip(r['z3'] / 2)
    if abs(r['z1']) > 1:
        v['M3_REV'] = -clip(r['z1'] / 2)
    e, w = recent_event(r)
    if e is not None and abs(e['r60']) >= 0.004:
        ok = (e['r60'] > 0 and e['dove'] > 0) or (e['r60'] < 0 and e['hawk'] > 0)
        if ok:
            v['M4_NEWS'] = float(np.sign(e['r60'])) * w
            v['M5a_EVT_ANALOG'], info['event_analogs'] = event_analog(e, r, t)
            info['event'] = (e['ts'].strftime('%Y-%m-%d %H:%M'), e['type'], round(100 * e['r60'], 2))
    if len(lib_state) >= 100:
        X = np.array([[x[f] for f in STATE_F] for x in lib_state]); mu, sd = X.mean(0), X.std(0) + 1e-12
        q = (np.array([r[f] for f in STATE_F]) - mu) / sd
        d = np.sum(((X - mu) / sd - q) ** 2, axis=1)
        nn = np.argsort(d)[:K_STATE]
        v['M5b_STATE_ANALOG'] = clip(float(np.mean([lib_state[k]['r10'] for k in nn])) / 0.015)
    if r['si24'] is not None and np.sign(r['si24']) == np.sign(r['g24']) and abs(r['si24']) >= 0.005:
        v['M6_SILVER'] = float(np.sign(r['g24']))
    if r['zn24'] is not None and abs(r['zn24']) >= 0.0025:
        v['M7_RATES'] = float(np.sign(r['zn24']))
    if r['nq24'] is not None and r['nq24'] <= -0.015:
        v['M8_RISK'] = 1.0 if r['g24'] >= 0 else -1.0
    if r['gvz5'] is not None and r['gvz5'] >= 2:
        v['M9_GVZ'] = float(np.sign(r['g5']))
    return v, info

# ---------- online run ----------
L = {m: 0.0 for m in MOD}
decay = 2 ** (-1 / HALF)
pending = []   # decision rows with votes awaiting maturity
lib_state, matured_scored = [], []
hits = {m: [0, 0] for m in MOD}
rows = [r for r in D if r['ok']]
for r in rows:
    t = r['t']
    # 1) absorb matured labels
    still = []
    for p in pending:
        if p['m10'] is not None and p['m10'] <= t:
            y = np.sign(p['r10'])
            if y != 0:
                mix_loss = (1 - p['s'] * y) / 2  # loss of the combined forecast at that time
                for m in MOD:
                    L[m] *= decay
                    if p['votes'][m] != 0:
                        L[m] += (1 - np.sign(p['votes'][m]) * y) / 2 * abs(p['votes'][m])
                        if p['t'] >= dt.datetime(2021, 7, 1, tzinfo=UTC):
                            hits[m][0] += int(np.sign(p['votes'][m]) == y); hits[m][1] += 1
                    elif SLEEPING_FIX:
                        L[m] += mix_loss  # sleeping-experts Hedge: asleep expert is charged the mixture's loss
            lib_state.append(p); matured_scored.append(p)
        else:
            still.append(p)
    pending = still
    # 2) votes, weights, score
    v, info = votes(r, t, lib_state)
    w = {m: math.exp(-ETA * L[m]) for m in MOD}
    awake = [m for m in MOD if v[m] != 0]
    s = sum(w[m] * v[m] for m in awake) / sum(w[m] for m in awake) if awake else 0.0
    # 3) calibration
    hist = matured_scored[-500:]
    pu = pdn = None
    if len(hist) >= 100:
        sc = np.array([h['s'] for h in hist]); rr = np.array([h['r10'] for h in hist])
        edges = np.quantile(sc, [0.2, 0.4, 0.6, 0.8])
        b = np.searchsorted(edges, s); bk = np.searchsorted(edges, sc) == b
        pu, pdn = float(np.mean(rr[bk] > COST)), float(np.mean(rr[bk] < -COST))
    r.update(votes=v, info=info, w={m: round(w[m] / sum(w.values()), 4) for m in MOD}, s=s, pu=pu, pdn=pdn,
             awake=awake)
    pending.append(r)

# ---------- evaluation helpers ----------
def run_portfolio(t0, t1, cash, units, entry_note=''):
    pos_gold = units > 0; last_trade_si = -99; trades = []
    for r in rows:
        if not (t0 <= r['t'] < t1) or r['pu'] is None:
            continue
        bid, ask = r['mid'] - r['spr'] / 2, r['mid'] + r['spr'] / 2
        can = r['si'] - last_trade_si >= 2
        if not pos_gold and can and r['s'] > 0 and r['pu'] - r['pdn'] >= EDGE:
            units = cash * (1 - FEE) / ask; trades.append(dict(t=r['t'].isoformat(), act='BUY', px=round(ask, 2), fee=round(cash * FEE, 4), s=round(r['s'], 3), pu=r['pu'], pdn=r['pdn']))
            cash = 0; pos_gold = True; last_trade_si = r['si']
        elif pos_gold and can and r['s'] < 0 and r['pdn'] - r['pu'] >= EDGE:
            g = units * bid; cash = g * (1 - FEE); trades.append(dict(t=r['t'].isoformat(), act='SELL', px=round(bid, 2), fee=round(g * FEE, 4), s=round(r['s'], 3), pu=r['pu'], pdn=r['pdn']))
            units = 0; pos_gold = False; last_trade_si = r['si']
    last = [r for r in rows if r['t'] < t1][-1]
    bid = last['mid'] - last['spr'] / 2
    return dict(trades=trades, end_t=last['t'].isoformat(), end_bid=round(bid, 2), nav_bid=round(cash + units * bid, 4),
                net_if_sold=round(cash + units * bid * (1 - FEE), 4), fees=round(sum(x['fee'] for x in trades), 4), units=units, cash=cash)

def acc_stats(t0, t1):
    sel = [r for r in rows if t0 <= r['t'] < t1 and r['r10'] is not None and r['r10'] != 0]
    y = np.array([np.sign(r['r10']) for r in sel]); p = np.array([np.sign(r['s']) for r in sel])
    nz = p != 0
    up, dn = (y == 1) & nz, (y == -1) & nz
    rec_up = float(np.mean(p[up] == 1)) if up.any() else None
    rec_dn = float(np.mean(p[dn] == -1)) if dn.any() else None
    big = np.array([abs(r['r10']) > COST for r in sel])
    return dict(n=len(sel), n_called=int(nz.sum()), accuracy=float(np.mean(p[nz] == y[nz])) if nz.any() else None,
                balanced_accuracy=(rec_up + rec_dn) / 2 if rec_up is not None and rec_dn is not None else None,
                up_recall=rec_up, down_recall=rec_dn, base_up_share=float(np.mean(y == 1)),
                accuracy_on_big_moves=float(np.mean(p[nz & big] == y[nz & big])) if (nz & big).any() else None)

def T(s):
    return dt.datetime.fromisoformat(s).replace(tzinfo=UTC)

res = {}
res['dev'] = dict(window='2021-07-01..2022-12-30',
                  portfolio=run_portfolio(T('2021-07-01T00:00'), T('2022-12-31T00:00'), 100.0, 0.0),
                  accuracy_2021H2=acc_stats(T('2021-07-01T00:00'), T('2022-01-01T00:00')),
                  accuracy_2022=acc_stats(T('2022-01-01T00:00'), T('2023-01-01T00:00')))
pa = [r for r in rows if r['t'] >= T('2021-07-01T00:00')][0]; pz = [r for r in rows if r['t'] < T('2022-12-31T00:00')][-1]
res['dev']['passive_net'] = round(100 * (1 - FEE) / (pa['mid'] + pa['spr'] / 2) * (pz['mid'] - pz['spr'] / 2) * (1 - FEE), 4)
res['module_hit_rate_dev_matured'] = {m: (round(hits[m][0] / hits[m][1], 4), hits[m][1]) if hits[m][1] else None for m in MOD}
res['weights_snapshots'] = {r['t'].strftime('%Y-%m-%d %H:%M'): r['w'] for r in rows if r['t'].strftime('%m-%d %H:%M') in ('01-03 06:00', '07-01 06:00') or r['t'].strftime('%Y-%m-%d %H:%M') in ('2023-02-03 13:45', '2023-02-28 13:45')}
res['A1'] = run_portfolio(T('2023-01-03T00:00'), T('2023-01-17T00:00'), 100.0, 0.0)
res['A2'] = run_portfolio(T('2023-01-04T07:21'), T('2023-01-17T00:00'), 0.0, 0.05358252259969825)
res['C_gold'] = run_portfolio(T('2023-01-26T06:01'), T('2023-02-01T00:00'), 0.0, 100 * (1 - FEE) / 1947.71)
res['B_gold'] = run_portfolio(T('2023-01-30T06:01'), T('2023-03-01T00:00'), 0.0, 100 * (1 - FEE) / 1931.64)
res['CONT'] = run_portfolio(T('2023-01-03T00:00'), T('2023-03-01T00:00'), 100.0, 0.0)
res['accuracy_2023_janfeb'] = acc_stats(T('2023-01-03T00:00'), T('2023-03-01T00:00'))
res['ledger_2023'] = [dict(t=r['t'].strftime('%Y-%m-%d %H:%M'), trt=(r['t'] + dt.timedelta(hours=3)).strftime('%Y-%m-%d %H:%M'),
                           s=round(r['s'], 3), pu=None if r['pu'] is None else round(r['pu'], 3), pdn=None if r['pdn'] is None else round(r['pdn'], 3),
                           votes={m: round(v, 2) for m, v in r['votes'].items() if v != 0}, weights=r['w'], info=r['info'],
                           feat=dict(trend20=round(100 * r['trend20'], 2), mom10=round(100 * r['mom10'], 2), z1=round(r['z1'], 2), z3=round(r['z3'], 2),
                                     g24=round(100 * r['g24'], 2), si24=None if r['si24'] is None else round(100 * r['si24'], 2),
                                     zn24=None if r['zn24'] is None else round(100 * r['zn24'], 2), nq24=None if r['nq24'] is None else round(100 * r['nq24'], 2),
                                     gvz5=None if r['gvz5'] is None else round(r['gvz5'], 2)),
                           r10_expost=None if r['r10'] is None else round(100 * r['r10'], 2))
                      for r in rows if r['t'] >= T('2023-01-03T00:00')]
json.dump(res, open(OUT, 'w'), indent=1, default=str)
for k in ('A1', 'A2', 'C_gold', 'B_gold', 'CONT'):
    print(k, res[k]['nav_bid'], res[k]['net_if_sold'], [(x['t'][:16], x['act'], x['px']) for x in res[k]['trades']])
print('DEV', res['dev']['portfolio']['nav_bid'], res['dev']['portfolio']['net_if_sold'], len(res['dev']['portfolio']['trades']), 'passive', res['dev']['passive_net'])
print(json.dumps(res['dev']['accuracy_2021H2'])); print(json.dumps(res['dev']['accuracy_2022'])); print(json.dumps(res['accuracy_2023_janfeb']))
print(json.dumps(res['module_hit_rate_dev_matured']))
