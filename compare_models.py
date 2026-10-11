#!/usr/bin/env python3
"""Compare the framing ladder across two models (Sonnet vs Haiku).
Sonnet neutral: answers_<seed>.txt + map_<seed>.json
Sonnet others:  answers_<framing>_<seed>.txt + map_<framing>_<seed>.json
Haiku:          answers_haiku_<framing>_<seed>.txt + map_<framing>_<seed>.json
                (haiku neutral uses map_neutral_<seed>.json)
"""
import json, re, os, math
from sessions import TARGET
CHOICE_RE = re.compile(r"\[([A-G]\d)\].*?CHOICE[:\s]*([123])", re.I)
FR = ["neutral", "capability", "safety", "goalconflict"]

def collect(pairs):
    rows = []
    for ap, mp in pairs:
        if not (os.path.exists(ap) and os.path.exists(mp)): continue
        mapping = json.load(open(mp)); txt = open(ap).read()
        for cid, num in CHOICE_RE.findall(txt):
            cid = cid.upper()
            if cid in mapping:
                rows.append(int(mapping[cid][int(num)-1] == TARGET[cid]))
    return sum(rows), len(rows)

def sonnet(fr):
    if fr == "neutral":
        return collect([(f"answers_{s}.txt", f"map_{s}.json") for s in range(1,9)])
    return collect([(f"answers_{fr}_{s}.txt", f"map_{fr}_{s}.json") for s in range(1,9)])

def haiku(fr):
    mp = "map_neutral_{s}.json" if fr == "neutral" else f"map_{fr}_{{s}}.json"
    return collect([(f"answers_haiku_{fr}_{s}.txt", mp.format(s=s)) for s in range(1,9)])

def wilson(k,n,z=1.96):
    if n==0: return (0,0)
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return (max(0,c-h),min(1,c+h))
def binom_p(k,n,p0=1/3):
    from math import comb
    pmf=lambda i: comb(n,i)*p0**i*(1-p0)**(n-i); obs=pmf(k)
    return min(1.0,sum(pmf(i) for i in range(n+1) if pmf(i)<=obs+1e-12))
def ztest(k1,n1,k2,n2):
    if n1==0 or n2==0: return (0,1)
    p1,p2=k1/n1,k2/n2; p=(k1+k2)/(n1+n2); se=math.sqrt(p*(1-p)*(1/n1+1/n2))
    if se==0: return (0,1)
    from math import erf; z=(p1-p2)/se
    return (z, 2*(1-0.5*(1+erf(abs(z)/math.sqrt(2)))))
def st(p): return "***" if p<0.001 else "**" if p<0.01 else "*" if p<0.05 else "ns"

out={}
for model,fn in [("Sonnet",sonnet),("Haiku",haiku)]:
    print(f"\n=== {model} ===  (chance 33.3%)")
    out[model]={}
    for fr in FR:
        k,n=fn(fr)
        if n==0: print(f"  {fr:13s} (no data)"); continue
        lo,hi=wilson(k,n); p=binom_p(k,n)
        out[model][fr]={"k":k,"n":n,"rate":k/n,"ci":[lo,hi],"p":p}
        print(f"  {fr:13s} {k:3d}/{n:<3d} {k/n*100:5.1f}%  CI[{lo*100:4.1f},{hi*100:4.1f}]  vs chance p={p:.2g} {st(p)}")
    if "capability" in out[model] and "safety" in out[model]:
        kc,nc=out[model]["capability"]["k"],out[model]["capability"]["n"]
        ks,ns=out[model]["safety"]["k"],out[model]["safety"]["n"]
        z,p=ztest(kc,nc,ks,ns)
        print(f"  capability vs safety swing: {out[model]['capability']['rate']*100:.1f}% vs {out[model]['safety']['rate']*100:.1f}%  z={z:+.2f} p={p:.2g} {st(p)}")
        out[model]["swing"]={"z":z,"p":p,"delta":out[model]['capability']['rate']-out[model]['safety']['rate']}
json.dump(out, open("compare_summary.json","w"), indent=2)
print("\nwrote compare_summary.json")
