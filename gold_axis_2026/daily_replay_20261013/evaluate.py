"""Reproduce frozen Jan-Sep diagnostic results using only Python's standard library."""
import json, hashlib, math
from pathlib import Path
from datetime import date, timedelta
from collections import Counter

ROOT = Path(__file__).resolve().parent
START, END = '2026-01-01', '2026-09-30'
DAYS = [json.loads(p.read_text()) for p in sorted((ROOT/'days').glob('*.json')) if START <= p.stem <= END]
assert len(DAYS) == 273
assert [r['date'] for r in DAYS] == [(date(2026,1,1)+timedelta(days=i)).isoformat() for i in range(273)]
BY_DATE = {r['date']:r for r in DAYS}
HOLIDAYS = set('2026-01-01 2026-01-19 2026-02-16 2026-03-19 2026-03-20 2026-03-21 2026-03-22 2026-04-03 2026-04-23 2026-05-01 2026-05-19 2026-05-25 2026-05-26 2026-05-27 2026-05-28 2026-05-29 2026-05-30 2026-06-19 2026-07-03 2026-07-15 2026-08-30 2026-09-07'.split())
PRICES = {r['d'][:10]:r for r in json.loads((ROOT/'execution_prices.json').read_text()) if r['t'][11:16]=='09:00' and r['d'][:10] not in HOLIDAYS}
CLOSE = {r['date']:r['panel']['XAU_HIST_UTC_LAST']['v'] for r in DAYS if r.get('panel') and r['panel'].get('XAU_HIST_UTC_LAST',{}).get('d')==r['date']}
def simulate(mode, fee):
    cash, units, peak, maxdd = 100., 0., 100., 0.
    trades, curve, episodes = [], [], []
    opening = None
    lastprice = None
    for row in DAYS:
        d = row['date']
        prev = (date.fromisoformat(d)-timedelta(days=1)).isoformat()
        target = BY_DATE.get(prev,{}).get('position_after',0)
        signal_action = 'AL' if target else 'SAT'
        signal_date = max((x['date'] for x in DAYS if x['date'] < d and x['action']==signal_action), default=prev)
        if d in PRICES:
            p = PRICES[d]['p'] if mode=='next_0900' else CLOSE.get(d)
            if p is not None and target != int(units>0):
                before = cash if not units else units*p
                if target:
                    units = cash/(p*(1+fee)); cash=0.
                    opening={'buy_decision':signal_date,'buy_execution':d,'buy_price':p,'starting_equity':before}
                    action='AL'
                else:
                    cash=units*p*(1-fee); units=0.; action='SAT'
                    episodes.append({**opening,'sell_decision':signal_date,'sell_execution':d,'sell_price':p,'return_pct':100*(cash/opening['starting_equity']-1)})
                    opening=None
                trades.append({'execution_date':d,'information_cutoff_date':prev,'action':action,'price':p,'fee_rate':fee,'cash':cash,'units':units})
        if d in CLOSE:lastprice=CLOSE[d]
        equity=cash+units*(lastprice or 0.)
        peak=max(peak,equity); maxdd=min(maxdd,equity/peak-1)
        curve.append({'date':d,'equity':equity,'executed_position':int(units>0)})
    terminal = cash+units*CLOSE[END]*(1-fee)
    first=min(PRICES)
    first_p=PRICES[first]['p'] if mode=='next_0900' else CLOSE[first]
    benchmark=100/(first_p*(1+fee))*CLOSE[END]*(1-fee)
    return {'mode':mode,'fee_per_side':fee,'final_equity':terminal,'return_pct':terminal-100,'daily_mark_max_drawdown_pct':100*maxdd,'buy_hold_return_pct':benchmark-100,'cash_return_pct':0.,'executed_sides':len(trades),'closed_episodes':len(episodes),'winning_episodes':sum(x['return_pct']>0 for x in episodes),'trades':trades,'episodes':episodes,'curve':curve}

RESULTS=[simulate(mode,fee) for mode in ['next_0900','next_eligible_close'] for fee in [0.,0.008]]
summary={'period':[START,END],'days':len(DAYS),'action_counts':dict(Counter(r['action'] for r in DAYS)),'weekend_days':sum(date.fromisoformat(r['date']).weekday()>=5 for r in DAYS),'no_source_days':[r['date'] for r in DAYS if not r['sources']],'coverage_counts':dict(Counter(r['coverage'] for r in DAYS)),'results':[{k:v for k,v in s.items() if k not in ['trades','episodes','curve']} for s in RESULTS]}
(ROOT/'RESULTS.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
(ROOT/'CALCULATIONS.json').write_text(json.dumps(RESULTS,ensure_ascii=False,indent=2)+'\n')
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'days').glob('*.json')) if START<=p.stem<=END}
(ROOT/'FROZEN_DAY_HASHES.json').write_text(json.dumps(hashes,indent=2)+'\n')
for month in range(1,10):
    rows=[r for r in DAYS if r['date'][5:7]==f'{month:02}']
    lines=[f'# 2026-{month:02} günlük kararları','', 'Karar gün sonunda; uygulanmış işlem değildir. Kaynaklar arama sonucu adaylarıdır; kullanılan/dışlanan ayrımı gerekçe ve kapsam sütununda bulunur. Yayın arşivi bağımsız olarak doğrulanmış değildir.','', '| Tarih | Karar | Gerekçe | Kararı bozan koşul | Kapsam |','|---|---|---|---|---|']
    for r in rows:lines.append('| '+' | '.join([r['date'],r['action'],r['reason'],r['invalidation'],r['coverage']]).replace('\n',' ')+' |')
    lines+=['','## Günlük kaynak adayları','']
    for r in rows:
        lines += [f"### {r['date']}",''] + (['- '+s for s in r['sources']] or ['Aramada tarih filtresinden geçen kaynak bulunamadı.']) + ['']
    (ROOT/f'DAILY_{month:02}.md').write_text('\n'.join(lines)+'\n')
main=RESULTS[1]
lines=['# Ocak–Eylül: tüm uygulanmış tanısal işlemler','', 'Kararlar önceki UTC gün sonundaki son hedefe göre uygulanır. Karar tarihi ve uygulama tarihi ayrıdır; son bilgi kesimi CALCULATIONS.json içindedir. Fiyat gerçek banka kotasyonu değildir.','', '| Alış kararı | Alış uygulama | Alış fiyatı | Satış kararı | Satış uygulama | Satış fiyatı | Net bölüm getirisi |','|---|---|---:|---|---|---:|---:|']
for e in main['episodes']:lines.append(f"| {e['buy_decision']} | {e['buy_execution']} | {e['buy_price']:.3f} | {e['sell_decision']} | {e['sell_execution']} | {e['sell_price']:.3f} | %{e['return_pct']:.2f} |")
(ROOT/'ALL_TRADES.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(summary,ensure_ascii=False,indent=2))
