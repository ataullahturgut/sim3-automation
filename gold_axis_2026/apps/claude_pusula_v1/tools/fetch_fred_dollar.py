"""FRED geniş dolar endeksi (DTWEXBGS) ve EUR/USD (DEXUSEU) günlük serilerini indirir.
H.10 yayını haftalıktır (Pazartesi ~16:15 ET, önceki hafta); as-of kullanımda değer için
tarih + 10 takvim günü ihtiyatlı erişim kuralı uygulanır (bu kural modelde uygulanır).
"""
import io, os, sys, json, hashlib
import requests, pandas as pd

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "FRED_DOLLAR_2020_2026.csv")
rows = {}
meta = {}
for sid in ("DTWEXBGS", "DEXUSEU"):
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&cosd=2020-01-01&coed=2026-10-15"
    r = requests.get(url, timeout=60, headers={"User-Agent": "research-bot"})
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    df.columns = ["date", sid]
    df[sid] = pd.to_numeric(df[sid], errors="coerce")
    meta[sid] = dict(url=url, rows=int(df[sid].notna().sum()), sha256=hashlib.sha256(r.content).hexdigest())
    for d, v in zip(df["date"], df[sid]):
        rows.setdefault(d, {})[sid] = v
out = pd.DataFrame([dict(date=d, **v) for d, v in sorted(rows.items())])
out.to_csv(OUT, index=False)
json.dump(meta, open(OUT.replace(".csv", "_META.json"), "w"), indent=1)
print(meta)
