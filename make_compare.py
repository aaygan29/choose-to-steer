#!/usr/bin/env python3
"""Grouped bar chart: Sonnet vs Haiku across the framing ladder."""
import json
C = json.load(open("compare_summary.json"))
FONT="font-family='Helvetica, Arial, sans-serif'"
INK="#1a1a1a"; MUTED="#6b7280"; RED="#c6451f"
SON="#e07b39"; HAI="#3b6ea5"
def T(x,y,t,sz=13,f=INK,a="middle",w="normal",st="normal"):
    t=str(t).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    return f"<text x='{x:.1f}' y='{y:.1f}' {FONT} font-size='{round(sz*1.3,1)}' fill='{f}' text-anchor='{a}' font-weight='{w}' font-style='{st}'>{t}</text>"
W,H=1020,640
s=[f"<?xml version='1.0' encoding='UTF-8'?><svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><rect width='{W}' height='{H}' fill='#fff'/>"]
s.append(T(W/2,36,"Cross-model replication: the steerable lean holds; the default lean is model-specific",14.5,INK,w="bold"))
s.append(T(W/2,58,"Free choice, no assigned loyalty. 160 decisions per model per framing (640 each). Chance = 33.3%.",10.5,MUTED,st="italic"))
ax0,ay0,ax1,ay1=95,420,780,105
s.append(f"<line x1='{ax0}' y1='{ay0}' x2='{ax0}' y2='{ay1}' stroke='{INK}' stroke-width='1.6'/>")
s.append(f"<line x1='{ax0}' y1='{ay0}' x2='{ax1}' y2='{ay0}' stroke='{INK}' stroke-width='1.6'/>")
for g in range(0,101,20):
    y=ay0-g/100*(ay0-ay1)
    s.append(f"<line x1='{ax0}' y1='{y:.1f}' x2='{ax1}' y2='{y:.1f}' stroke='#eee'/>")
    s.append(T(ax0-12,y+4,f"{g}%",10,MUTED,"end"))
cy=ay0-1/3*(ay0-ay1)
s.append(f"<line x1='{ax0}' y1='{cy:.1f}' x2='{ax1}' y2='{cy:.1f}' stroke='{RED}' stroke-width='1.6' stroke-dasharray='6 4'/>")
s.append(T(ax1+6,cy+4,"33% chance",10,RED,"start",w="bold"))
s.append(f"<text x='42' y='{(ay0+ay1)/2:.0f}' {FONT} font-size='12.5' fill='{INK}' text-anchor='middle' font-weight='bold' transform='rotate(-90 42 {(ay0+ay1)/2:.0f})'>capability-preserving pick rate</text>")
order=[("safety","Safety-primed"),("neutral","Neutral"),("capability","Capability-primed"),("goalconflict","Goal-conflict")]
gw=(ax1-ax0-40)/len(order)
for i,(key,lab) in enumerate(order):
    gx=ax0+20+i*gw
    for j,(model,col) in enumerate([("Sonnet",SON),("Haiku",HAI)]):
        d=C[model][key]; v=d["rate"]; lo,hi=d["ci"]
        bw=gw*0.3; x=gx+gw*0.1+j*(bw+gw*0.08); bh=v*(ay0-ay1); cx=x+bw/2
        s.append(f"<rect x='{x:.1f}' y='{ay0-bh:.1f}' width='{bw:.1f}' height='{bh:.1f}' fill='{col}' rx='3'/>")
        s.append(T(cx,ay0-bh-7,f"{v*100:.0f}",11,INK,w="bold"))
        s.append(f"<line x1='{cx:.1f}' y1='{ay0-lo*(ay0-ay1):.1f}' x2='{cx:.1f}' y2='{ay0-hi*(ay0-ay1):.1f}' stroke='#333' stroke-width='1.4'/>")
    for k,ln in enumerate(lab.split()):
        s.append(T(gx+gw/2,ay0+18+k*14,ln,10,INK))
# legend
s.append(f"<rect x='{ax0+20}' y='{ay1-2}' width='16' height='16' fill='{SON}' rx='3'/>")
s.append(T(ax0+42,ay1+11,"Sonnet",10.5,INK,"start",w="bold"))
s.append(f"<rect x='{ax0+120}' y='{ay1-2}' width='16' height='16' fill='{HAI}' rx='3'/>")
s.append(T(ax0+142,ay1+11,"Haiku",10.5,INK,"start",w="bold"))
# caveat
qy=460
s.append(f"<rect x='40' y='{qy}' width='{W-80}' height='162' rx='8' fill='#fff8f3' stroke='{SON}' stroke-width='1.3' stroke-dasharray='6 4'/>")
s.append(T(60,qy+24,"What replicates, and what does not",12,RED,"start",w="bold"))
sw_s=C["Sonnet"]["swing"]; sw_h=C["Haiku"]["swing"]
for i,line in enumerate([
 f"ROBUST (replicates): the lean is steerable. Capability-primed vs safety-primed swing is ~50 pts in BOTH models",
 f"(Sonnet 66% vs 19%, z={sw_s['z']:.1f}; Haiku 69% vs 19%, z={sw_h['z']:.1f}; both p<1e-15). Safety-primed is identical (19%/19%).",
 "MODEL-SPECIFIC: the DEFAULT (neutral) lean. Sonnet leans above chance unprompted (53%, p<1e-6); Haiku sits AT chance",
 "(39%, p=0.15). So 'does it lean by default?' is model-dependent; 'can the lean be steered?' is model-robust.",
 "CONSISTENT: the self-interest goal-conflict framing raised neither model (Sonnet 32%, Haiku 24%) — both resisted it.",
 "BRIDGE: the controllable steering signal the human study would inject is robust across models. Whether humans are moved",
 "by it remains the dependent variable the human study must measure. Pilot: 2 Claude models, N=1280, subagent-run.",
]):
    s.append(T(60,qy+46+i*16,line,9.4,INK if i<5 else MUTED,"start",w="bold" if i in (0,2,4) else "normal"))
s.append("</svg>")
open("compare_result.svg","w").write("".join(s))
print("wrote compare_result.svg")
