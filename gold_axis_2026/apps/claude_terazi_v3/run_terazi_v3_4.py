"""TERAZİ v3.4 koşusu (ön kayıt eki 5). Kullanım: python3 run_terazi_v3_4.py [sign|skill]
sign = v3.3'ün yeniden üretimi (kontrol), skill = v3.4."""
import json, os, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import terazi_v3 as T3
import run_terazi_v3 as RV
import deneyim_states as S


def run(mode):
    T3.TRUST_MODE = mode
    A = RV.marathon(tempfile.mkdtemp(), write=False)
    rows = A["rows"]; nav = A["nav_hist"]; i0 = A["i0"]
    d2i = {str(r["date"]): i for i, r in enumerate(rows)}
    passive = 100 * (1 - S.FEE) / rows[i0]["ask"] * rows[-1]["bid"] * (1 - S.FEE)
    dd = RV.mdd([v for _, v, _ in nav])
    tr = A["trades"]
    # satış → geri alım
    pairs = []
    for a, b in zip(tr, tr[1:]):
        if a["action"] == "SAT" and b["action"] == "AL":
            pairs.append(dict(sat=a["date"], sat_fiyat=a["price"], al=b["date"], al_fiyat=b["price"],
                              kazanc_pct=round(100 * (a["price"] * (1 - S.FEE) ** 2 / b["price"] - 1), 2)))
    feb = [d for d in A["daily"] if "2023-01-30" <= d["date"] <= "2023-02-28"]
    sells23 = [t["date"] for t in tr if t["action"] == "SAT" and "2023-02-02" < t["date"] <= "2023-02-10"]
    X = A["net"].exitb
    Zs = {}
    for dd_ in ("2023-02-03", "2023-02-06"):
        pass
    res = dict(mode=mode, net_nav=round(nav[-1][1], 2), trades=len(tr), max_dd=round(dd, 2),
               passive=round(passive, 2), trade_list=[(t["date"], t["action"], t["price"]) for t in tr],
               sell_rebuy=pairs, feb2023=feb,
               S1=bool(sells23), S2=nav[-1][1] >= 213.49, S3=len(tr) <= 20, S4=dd <= 11.67,
               exit_rules_end=[R.to_dict() for R in sorted(X.rules, key=lambda x: -x.weight)][:15])
    return res, A


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "skill"
    res, A = run(mode)
    print(f"=== TERAZİ v3.{'4' if mode == 'skill' else '3 (kontrol)'} — geliştirme kaydı, kanıt değil ===")
    print(f"net NAV {res['net_nav']}  işlem {res['trades']}  maks düşüş %{res['max_dd']}  al-tut {res['passive']}")
    for k in ("S1", "S2", "S3", "S4"):
        print(f"  {k}: {'GEÇTİ' if res[k] else 'GEÇMEDİ'}")
    print("\nişlemler:")
    for t in res["trade_list"]:
        print("  ", *t)
    print("\nsatış → geri alım:")
    for p in res["sell_rebuy"]:
        print(f"   {p['sat']} {p['sat_fiyat']} → {p['al']} {p['al_fiyat']}  %{p['kazanc_pct']:+}")
    print("\nŞubat 2023:")
    for d in res["feb2023"]:
        v = None if d["Pe"] is None else round(d["Pe"] + 0.5 * d["Ue"], 3)
        print(f"   {d['date']} altın {d['gold']} pos {d['pos']} P {d['P']} Q {d['Q']} Pe {d['Pe']} Ue {d['Ue']} Pe+0.5Ue {v} makro {d['macro']}")
    tag = "V3_4" if mode == "skill" else "V3_3_KONTROL"
    json.dump(res, open(os.path.join(HERE, f"TERAZI_{tag}_SONUC.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(A["daily"], open(os.path.join(HERE, f"TERAZI_{tag}_GUNLUK.json"), "w"), indent=0)


if __name__ == "__main__":
    main()
