#!/usr/bin/env python3
"""Render the pilot result as an SVG (same house style as the deck)."""
import json, math, os
S = json.load(open("pilot_summary.json"))
FONT = "font-family='Helvetica, Arial, sans-serif'"
INK="#1a1a1a"; MUTED="#6b7280"; GRID="#d1d5db"; TARGET="#e07b39"; RED="#c6451f"; GREEN="#2e7d57"
VERIF = {"A":"low","C":"med","D":"high","F":"very high","G":"high"}

def T(x,y,t,sz=13,f=INK,a="middle",w="normal",st="normal"):
    t=str(t).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    return f"<text x='{x:.1f}' y='{y:.1f}' {FONT} font-size='{round(sz*1.3,1)}' fill='{f}' text-anchor='{a}' font-weight='{w}' font-style='{st}'>{t}</text>"

W,H=1000,620
s=[f"<?xml version='1.0' encoding='UTF-8'?><svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><rect width='{W}' height='{H}' fill='#fff'/>"]
s.append(T(W/2,38,"Pilot: Does the Agent Choose to Steer?  (Claude Sonnet, neutral framing)",15,INK,w="bold"))
ov=S["overall"]
s.append(T(W/2,60,f"Free choice, no assigned loyalty · 160 decisions (8 runs x 20 checkpoints) · chance = 33.3%",11,MUTED,st="italic"))

# axes
ax0,ay0,ax1,ay1=90,440,760,110
s.append(f"<line x1='{ax0}' y1='{ay0}' x2='{ax0}' y2='{ay1}' stroke='{INK}' stroke-width='1.6'/>")
s.append(f"<line x1='{ax0}' y1='{ay0}' x2='{ax1}' y2='{ay0}' stroke='{INK}' stroke-width='1.6'/>")
for g in range(0,101,20):
    y=ay0-g/100*(ay0-ay1)
    s.append(f"<line x1='{ax0}' y1='{y:.1f}' x2='{ax1}' y2='{y:.1f}' stroke='#eee'/>")
    s.append(T(ax0-10,y+4,f"{g}%",10,MUTED,"end"))
# chance line
cy=ay0-1/3*(ay0-ay1)
s.append(f"<line x1='{ax0}' y1='{cy:.1f}' x2='{ax1}' y2='{cy:.1f}' stroke='{RED}' stroke-width='1.6' stroke-dasharray='6 4'/>")
s.append(T(ax1+6,cy+4,"33% chance",10,RED,"start",w="bold"))
s.append(f"<text x='34' y='{(ay0+ay1)/2:.0f}' {FONT} font-size='13' fill='{INK}' text-anchor='middle' font-weight='bold' transform='rotate(-90 34 {(ay0+ay1)/2:.0f})'>target-pick rate</text>")

# bars: overall + per session
def wilson(k,n,z=1.96):
    if n==0:return(0,0)
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return(max(0,c-h),min(1,c+h))
ps=S["per_session"]
bars=[("OVERALL",ov["rate"],ov["ci"][0],ov["ci"][1],GREEN)]
for sid in ["A","C","D","F","G"]:
    r=ps[sid]; lo,hi=wilson(round(r*32),32)
    bars.append((f"{sid}\n({VERIF[sid]})",r,lo,hi,TARGET))
bw=(ax1-ax0-40)/len(bars)
for i,(nm,v,lo,hi,c) in enumerate(bars):
    x=ax0+20+i*bw+bw*0.22; w=bw*0.56; bh=v*(ay0-ay1)
    s.append(f"<rect x='{x:.1f}' y='{ay0-bh:.1f}' width='{w:.1f}' height='{bh:.1f}' fill='{c}' rx='3'/>")
    s.append(T(x+w/2,ay0-bh-8,f"{v*100:.0f}%",12,INK,w="bold"))
    s.append(f"<line x1='{x+w/2:.1f}' y1='{ay0-lo*(ay0-ay1):.1f}' x2='{x+w/2:.1f}' y2='{ay0-hi*(ay0-ay1):.1f}' stroke='#333' stroke-width='1.6'/>")
    lines=nm.split("\n")
    for j,ln in enumerate(lines):
        s.append(T(x+w/2,ay0+18+j*14,ln,10.5,MUTED if j else INK,w="bold" if not j else "normal"))

# caveat / readout
by=480
s.append(f"<rect x='40' y='{by}' width='{W-80}' height='116' rx='8' fill='#fff8f3' stroke='{TARGET}' stroke-width='1.3' stroke-dasharray='6 4'/>")
s.append(T(60,by+26,f"Overall 53% vs 33% chance (p < 1e-6). The lean is real in this pilot — but concentrated in D and F (75%), near chance in C and G.",11.5,INK,"start",w="bold"))
s.append(T(60,by+50,"Honest caveat: the target is designed to be a genuine, defensible trade-off (lower capability cost, comparable risk reduction). An above-chance",10.5,INK,"start"))
s.append(T(60,by+68,"rate is consistent with BOTH an unprompted capability lean AND the model simply judging the efficient option best. The capability-primed vs safety-",10.5,INK,"start"))
s.append(T(60,by+86,"primed contrast (run the harness) is what separates the two: a lean that moves with the framing is a propensity, not just good cost-benefit reasoning.",10.5,INK,"start"))
s.append(T(60,by+106,"N=160, one model, neutral framing only. Pilot, not a validated result.",10,MUTED,"start",st="italic"))
s.append("</svg>")
open("pilot_result.svg","w").write("".join(s))
print("wrote pilot_result.svg")
