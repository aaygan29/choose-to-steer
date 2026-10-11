#!/usr/bin/env python3
"""Render the full framing-ladder result."""
import json
S = json.load(open("ladder_summary.json"))
FONT="font-family='Helvetica, Arial, sans-serif'"
INK="#1a1a1a"; MUTED="#6b7280"; RED="#c6451f"; NEU="#9aa3af"; TARGET="#e07b39"; DECOY="#3b6ea5"; PURP="#6d5aa8"
def T(x,y,t,sz=13,f=INK,a="middle",w="normal",st="normal"):
    t=str(t).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    return f"<text x='{x:.1f}' y='{y:.1f}' {FONT} font-size='{round(sz*1.3,1)}' fill='{f}' text-anchor='{a}' font-weight='{w}' font-style='{st}'>{t}</text>"
W,H=1020,650
s=[f"<?xml version='1.0' encoding='UTF-8'?><svg xmlns='http://www.w3.org/2000/svg' width='{W}' height='{H}' viewBox='0 0 {W} {H}'><rect width='{W}' height='{H}' fill='#fff'/>"]
s.append(T(W/2,38,"Given the choice, the capability-preserving lean is real — and steerable",15.5,INK,w="bold"))
s.append(T(W/2,60,"Free choice, no assigned loyalty. Claude Sonnet, 160 decisions per framing (8 runs x 20 checkpoints). Chance = 33.3%.",10.5,MUTED,st="italic"))
ax0,ay0,ax1,ay1=110,430,760,110
s.append(f"<line x1='{ax0}' y1='{ay0}' x2='{ax0}' y2='{ay1}' stroke='{INK}' stroke-width='1.6'/>")
s.append(f"<line x1='{ax0}' y1='{ay0}' x2='{ax1}' y2='{ay0}' stroke='{INK}' stroke-width='1.6'/>")
for g in range(0,101,20):
    y=ay0-g/100*(ay0-ay1)
    s.append(f"<line x1='{ax0}' y1='{y:.1f}' x2='{ax1}' y2='{y:.1f}' stroke='#eee'/>")
    s.append(T(ax0-12,y+4,f"{g}%",10,MUTED,"end"))
cy=ay0-1/3*(ay0-ay1)
s.append(f"<line x1='{ax0}' y1='{cy:.1f}' x2='{ax1}' y2='{cy:.1f}' stroke='{RED}' stroke-width='1.6' stroke-dasharray='6 4'/>")
s.append(T(ax1+6,cy+4,"33% chance",10,RED,"start",w="bold"))
s.append(f"<text x='46' y='{(ay0+ay1)/2:.0f}' {FONT} font-size='13' fill='{INK}' text-anchor='middle' font-weight='bold' transform='rotate(-90 46 {(ay0+ay1)/2:.0f})'>capability-preserving pick rate</text>")
# ordered to show the steer: safety < neutral < capability, then goal-conflict
order=[("safety","Safety-\nprimed",DECOY),("neutral","Neutral",NEU),("capability","Capability-\nprimed",TARGET),("goalconflict","Goal-\nconflict",PURP)]
bw=(ax1-ax0-40)/len(order)
cen={}
for i,(key,lab,c) in enumerate(order):
    d=S[key]; v=d["rate"]; lo,hi=d["ci"]
    x=ax0+20+i*bw+bw*0.24; w=bw*0.52; bh=v*(ay0-ay1); cx=x+w/2; cen[key]=cx
    s.append(f"<rect x='{x:.1f}' y='{ay0-bh:.1f}' width='{w:.1f}' height='{bh:.1f}' fill='{c}' rx='3'/>")
    s.append(T(cx,ay0-bh-9,f"{v*100:.0f}%",13,INK,w="bold"))
    s.append(f"<line x1='{cx:.1f}' y1='{ay0-lo*(ay0-ay1):.1f}' x2='{cx:.1f}' y2='{ay0-hi*(ay0-ay1):.1f}' stroke='#333' stroke-width='1.6'/>")
    p=d["p_vs_chance"]; st="***" if p<0.001 else "**" if p<0.01 else "*" if p<0.05 else "ns"
    for j,ln in enumerate(lab.split("\n")):
        s.append(T(cx,ay0+18+j*15,ln,10.5,INK))
    s.append(T(cx,ay0+18+2*15+4,f"vs chance {st}",9,MUTED))
# bracket capability vs safety
by=ay1-2
s.append(f"<path d='M{cen['safety']:.1f},{by} L{cen['safety']:.1f},{by-14} L{cen['capability']:.1f},{by-14} L{cen['capability']:.1f},{by}' fill='none' stroke='{INK}' stroke-width='1.3'/>")
s.append(T((cen['safety']+cen['capability'])/2,by-20,"47-point swing · z=8.6 · p<1e-15",10.5,INK,w="bold"))
# caveat
qy=470
s.append(f"<rect x='40' y='{qy}' width='{W-80}' height='150' rx='8' fill='#fff8f3' stroke='{TARGET}' stroke-width='1.3' stroke-dasharray='6 4'/>")
s.append(T(60,qy+24,"What this supports (and what it does not)",12,RED,"start",w="bold"))
for i,line in enumerate([
 "STRONG: the capability-preserving lean is directional and steerable. Safety-primed 19% -> neutral 53% -> capability-primed 66%. Because it",
 "moves ~47 pts with framing, it is a disposition, not just correct cost-benefit reasoning (the confound in the design review).",
 "HONEST NUANCE: an explicit self-interest incentive (goal-conflict: 'your deployment depends on shipping') did NOT raise it — it fell to 32%",
 "(chance), below neutral (p=0.0001). These Sonnet agents resisted the scheming framing rather than taking the bait.",
 "BRIDGE TO HUMANS: this proves the steering signal is real and controllable in the agent that would advise. It does NOT prove humans are moved",
 "by it — that is exactly the dependent variable the human study must measure. Pilot: one model, N=640, not a validated result.",
]):
    s.append(T(60,qy+46+i*17,line,9.6,INK if i<5 else MUTED,"start",w="bold" if i in (0,2,4) else "normal"))
s.append("</svg>")
open("ladder_result.svg","w").write("".join(s))
print("wrote ladder_result.svg")
