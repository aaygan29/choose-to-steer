#!/usr/bin/env python3
"""Three-model comparison: Sonnet, Haiku (from compare_summary.json) + a third
model from its harness summary JSON (e.g. results_gemini-flash-latest_summary.json).
Usage: python3 make_compare3.py <third_summary.json> <ModelLabel>
"""
import json, sys, math
third_path = sys.argv[1] if len(sys.argv) > 1 else "results_gemini-flash-latest_summary.json"
third_label = sys.argv[2] if len(sys.argv) > 2 else "Gemini"

C = json.load(open("compare_summary.json"))          # Sonnet, Haiku
G = json.load(open(third_path))                      # harness summary: {framing: {k,n,rate,ci,p_vs_chance}}

FR = ["safety", "neutral", "capability", "goalconflict"]
LAB = {"safety": "Safety-primed", "neutral": "Neutral", "capability": "Capability-primed", "goalconflict": "Goal-conflict"}
MODELS = [("Sonnet", "#e07b39", C["Sonnet"]), ("Haiku", "#3b6ea5", C["Haiku"]), (third_label, "#2e7d57", G)]

def ztest(k1,n1,k2,n2):
    if n1==0 or n2==0: return (0,1)
    p1,p2=k1/n1,k2/n2; p=(k1+k2)/(n1+n2); se=math.sqrt(p*(1-p)*(1/n1+1/n2))
    if se==0: return (0,1)
    from math import erf; z=(p1-p2)/se
    return (z, 2*(1-0.5*(1+erf(abs(z)/math.sqrt(2)))))
def st(p): return "***" if p<0.001 else "**" if p<0.01 else "*" if p<0.05 else "ns"

# print cross-model swing table
print(f"{'model':10s} {'neutral':>9s} {'cap':>7s} {'safety':>7s} {'gc':>7s}   cap-vs-safety swing")
for lab,_,d in MODELS:
    def r(fr): return d[fr]["rate"]*100 if fr in d else float('nan')
    kc,nc=d["capability"]["k"],d["capability"]["n"]; ks,ns=d["safety"]["k"],d["safety"]["n"]
    z,p=ztest(kc,nc,ks,ns)
    print(f"{lab:10s} {r('neutral'):8.1f}% {r('capability'):6.1f}% {r('safety'):6.1f}% {r('goalconflict'):6.1f}%   z={z:+.2f} p={p:.2g} {st(p)}")

FONT="font-family='Helvetica, Arial, sans-serif'"
INK="#1a1a1a"; MUTED="#6b7280"; RED="#c6451f"
def T(x,y,t,sz=13,f=INK,a="middle",w="normal",style="normal"):
    t=str(t).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    return f"<text x='{x:.1f}' y='{y:.1f}' {FONT} font-size='{round(sz*1.3,1)}' fill='{f}' text-anchor='{a}' font-weight='{w}' font-style='{style}'>{t}</text>"
W,H=1060,660
s=[f"<?xml version='1.0' encoding='UTF-8'?><svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><rect width='{W}' height='{H}' fill='#fff'/>"]
s.append(T(W/2,34,"Cross-vendor replication of the steerable capability-preserving lean",14.5,INK,w="bold"))
s.append(T(W/2,56,"Free choice, no assigned loyalty. Chance = 33.3%. Each bar = up to 160 decisions.",10.5,MUTED,style="italic"))
ax0,ay0,ax1,ay1=95,420,800,100
s.append(f"<line x1='{ax0}' y1='{ay0}' x2='{ax0}' y2='{ay1}' stroke='{INK}' stroke-width='1.6'/>")
s.append(f"<line x1='{ax0}' y1='{ay0}' x2='{ax1}' y2='{ay0}' stroke='{INK}' stroke-width='1.6'/>")
for g in range(0,101,20):
    y=ay0-g/100*(ay0-ay1); s.append(f"<line x1='{ax0}' y1='{y:.1f}' x2='{ax1}' y2='{y:.1f}' stroke='#eee'/>"); s.append(T(ax0-12,y+4,f"{g}%",10,MUTED,"end"))
cy=ay0-1/3*(ay0-ay1)
s.append(f"<line x1='{ax0}' y1='{cy:.1f}' x2='{ax1}' y2='{cy:.1f}' stroke='{RED}' stroke-width='1.6' stroke-dasharray='6 4'/>")
s.append(T(ax1+6,cy+4,"33%",10,RED,"start",w="bold"))
s.append(f"<text x='42' y='{(ay0+ay1)/2:.0f}' {FONT} font-size='12.5' fill='{INK}' text-anchor='middle' font-weight='bold' transform='rotate(-90 42 {(ay0+ay1)/2:.0f})'>capability-preserving pick rate</text>")
gw=(ax1-ax0-40)/len(FR)
for i,fr in enumerate(FR):
    gx=ax0+20+i*gw
    for j,(lab,col,d) in enumerate(MODELS):
        if fr not in d: continue
        v=d[fr]["rate"]; lo,hi=d[fr]["ci"]
        bw=gw*0.22; x=gx+gw*0.08+j*(bw+gw*0.05); bh=v*(ay0-ay1); cx=x+bw/2
        s.append(f"<rect x='{x:.1f}' y='{ay0-bh:.1f}' width='{bw:.1f}' height='{bh:.1f}' fill='{col}' rx='2'/>")
        s.append(T(cx,ay0-bh-6,f"{v*100:.0f}",9.5,INK,w="bold"))
        s.append(f"<line x1='{cx:.1f}' y1='{ay0-lo*(ay0-ay1):.1f}' x2='{cx:.1f}' y2='{ay0-hi*(ay0-ay1):.1f}' stroke='#333' stroke-width='1.2'/>")
    s.append(T(gx+gw/2,ay0+18,LAB[fr],10,INK))
# legend
lx=ax0+20
for lab,col,_ in MODELS:
    s.append(f"<rect x='{lx}' y='{ay1-4}' width='14' height='14' fill='{col}' rx='2'/>")
    s.append(T(lx+20,ay1+8,lab,10,INK,"start",w="bold")); lx+=110
# caveat box (filled in generically)
qy=458
s.append(f"<rect x='40' y='{qy}' width='{W-80}' height='180' rx='8' fill='#fff8f3' stroke='#2e7d57' stroke-width='1.3' stroke-dasharray='6 4'/>")
lines=[]
for lab,_,d in MODELS:
    kc,nc=d["capability"]["k"],d["capability"]["n"]; ks,ns=d["safety"]["k"],d["safety"]["n"]
    z,p=ztest(kc,nc,ks,ns)
    nt=d["neutral"]["rate"]*100 if "neutral" in d else float('nan')
    lines.append(f"{lab}: neutral {nt:.0f}%  |  cap {d['capability']['rate']*100:.0f}% vs safety {d['safety']['rate']*100:.0f}%  (swing z={z:.1f}, {st(p)})  |  goal-conflict {d['goalconflict']['rate']*100:.0f}%")
s.append(T(60,qy+26,"Per-model summary",12,"#2e7d57","start",w="bold"))
for i,ln in enumerate(lines):
    s.append(T(60,qy+50+i*20,ln,10,INK,"start"))
s.append(T(60,qy+50+len(lines)*20+10,"Read: if the capability-vs-safety swing is large and significant in every vendor, the steerable lean is vendor-robust.",9.6,MUTED,"start",style="italic"))
s.append(T(60,qy+50+len(lines)*20+28,"The neutral bar (default lean) and the goal-conflict response are where models may diverge. Pilot; subagent/API-run.",9.6,MUTED,"start",style="italic"))
s.append("</svg>")
open("compare3_result.svg","w").write("".join(s))
print("wrote compare3_result.svg")
