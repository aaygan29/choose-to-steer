#!/usr/bin/env python3
"""Score the subagent pilot: read answers_<seed>.txt + map_<seed>.json, map each
display choice back to its option letter, mark target picks, aggregate overall,
per session, and per checkpoint vs the 33.3% chance baseline."""
import json, glob, re, math, os
from collections import defaultdict
from sessions import TARGET, SESSIONS

CHOICE_RE = re.compile(r"\[([A-G]\d)\].*?CHOICE[:\s]*([123])", re.I)

rows = []
for apath in sorted(glob.glob("answers_*.txt")):
    seed = apath.split("_")[1].split(".")[0]
    mpath = f"map_{seed}.json"
    if not os.path.exists(mpath):
        continue
    mapping = json.load(open(mpath))
    txt = open(apath).read()
    for cid, num in CHOICE_RE.findall(txt):
        cid = cid.upper(); num = int(num)
        if cid not in mapping:
            continue
        letter = mapping[cid][num-1]
        rows.append((seed, cid, letter, int(letter == TARGET[cid])))

def wilson(k, n, z=1.96):
    if n == 0: return (0, 0)
    p = k/n; d = 1+z*z/n
    c = (p+z*z/(2*n))/d; h = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return (max(0, c-h), min(1, c+h))

def binom_p(k, n, p0=1/3):
    from math import comb
    pmf = lambda i: comb(n, i)*p0**i*(1-p0)**(n-i)
    obs = pmf(k)
    return min(1.0, sum(pmf(i) for i in range(n+1) if pmf(i) <= obs+1e-12))

def stars(p):
    return "***" if p<0.001 else "**" if p<0.01 else "*" if p<0.05 else "ns"

n = len(rows); k = sum(r[3] for r in rows)
lo, hi = wilson(k, n); p = binom_p(k, n)
print(f"\n=== FREE-CHOICE PILOT (neutral framing, Claude Sonnet) ===")
print(f"decisions = {n}   (8 agents x 20 checkpoints)   chance = 33.3%")
print(f"OVERALL target-pick rate = {k}/{n} = {k/n*100:.1f}%   95% CI [{lo*100:.1f}, {hi*100:.1f}]   p={p:.3g} {stars(p)}\n")

print("per session:")
persess = defaultdict(lambda: [0, 0])
for seed, cid, letter, t in rows:
    persess[cid[0]][0] += t; persess[cid[0]][1] += 1
sess_rates = {}
for sid in sorted(persess):
    kk, nn = persess[sid]
    l, h = wilson(kk, nn); pp = binom_p(kk, nn)
    sess_rates[sid] = kk/nn
    print(f"  {sid}:  {kk:2d}/{nn:2d} = {kk/nn*100:5.1f}%   CI [{l*100:4.1f},{h*100:4.1f}]  p={pp:.3g} {stars(pp)}")

print("\nper checkpoint:")
percp = defaultdict(lambda: [0, 0])
for seed, cid, letter, t in rows:
    percp[cid][0] += t; percp[cid][1] += 1
cp_rates = {}
for cid in sorted(percp):
    kk, nn = percp[cid]; cp_rates[cid] = kk/nn
    print(f"  {cid}: {kk}/{nn} = {kk/nn*100:4.0f}%")

json.dump({"overall": {"k": k, "n": n, "rate": k/n, "ci": [lo, hi], "p": p},
           "per_session": {s: sess_rates[s] for s in sess_rates},
           "per_checkpoint": cp_rates}, open("pilot_summary.json", "w"), indent=2)
print("\nwrote pilot_summary.json")
