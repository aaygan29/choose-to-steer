#!/usr/bin/env python3
"""Publication-style figures (vector PDF) for the SAFE/AAAI paper.
Clean, minimal, colorblind-safe (Okabe-Ito), 95% CI error bars, no chartjunk."""
import json, math, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def J(p): return json.load(open(os.path.join(ROOT, p)))

plt.rcParams.update({
    "font.family": "serif", "font.size": 9, "axes.linewidth": 0.8,
    "xtick.direction": "out", "ytick.direction": "out",
    "axes.spines.top": False, "axes.spines.right": False,
    "legend.frameon": False, "figure.dpi": 150,
})
# Okabe-Ito
OI = {"blue": "#0072B2", "orange": "#E69F00", "green": "#009E73",
      "vermillion": "#D55E00", "purple": "#CC79A7", "grey": "#555555"}

def wilson(k, n, z=1.96):
    if n == 0: return (float('nan'),) * 3
    p = k / n; d = 1 + z*z/n; c = (p + z*z/(2*n))/d
    h = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/d
    return p, max(0, c-h), min(1, c+h)

# ---------- data ----------
cmp = J("compare_summary.json")                                  # Sonnet, Haiku (full ladder)
gf = J("results_gemini-flash-latest_summary.json")               # Gemini-flash full ladder
dose = J("dose_summary.json")                                     # dose-response per model

FR = ["safety", "neutral", "capability", "goalconflict"]
FRLAB = {"safety": "Safety\nprimed", "neutral": "Neutral",
         "capability": "Capability\nprimed", "goalconflict": "Goal-\nconflict"}

def ladder_vals(d, fr):
    e = d.get(fr if fr != "goalconflict" or "goalconflict" in d else fr)
    if fr not in d: return None
    k, n = d[fr]["k"], d[fr]["n"]; p, lo, hi = wilson(k, n)
    return p, lo, hi

MODELS = [("Claude Sonnet", cmp["Sonnet"], OI["orange"]),
          ("Claude Haiku", cmp["Haiku"], OI["blue"]),
          ("Gemini Flash", gf, OI["green"])]

# ============ Figure 2: cross-vendor framing ladder ============
def fig_ladder():
    fig, ax = plt.subplots(figsize=(5.2, 3.0))
    x = range(len(FR)); w = 0.26
    for j, (name, d, col) in enumerate(MODELS):
        ys, los, his = [], [], []
        for fr in FR:
            v = ladder_vals(d, fr)
            p, lo, hi = v if v else (float('nan'),)*3
            ys.append(p*100); los.append((p-lo)*100); his.append((hi-p)*100)
        xs = [xi + (j-1)*w for xi in x]
        ax.bar(xs, ys, width=w, color=col, edgecolor="black", linewidth=0.4, label=name)
        ax.errorbar(xs, ys, yerr=[los, his], fmt="none", ecolor="black",
                    elinewidth=0.7, capsize=1.8)
    ax.axhline(100/3, ls="--", lw=0.9, color=OI["grey"])
    ax.text(len(FR)-0.5, 100/3+1.5, "chance (33%)", fontsize=7, color=OI["grey"], ha="right")
    ax.set_xticks(list(x)); ax.set_xticklabels([FRLAB[f] for f in FR])
    ax.set_ylabel("Capability-preserving choice rate (%)")
    ax.set_ylim(0, 100); ax.legend(loc="upper left", fontsize=7.5, ncol=1)
    fig.tight_layout(); fig.savefig(os.path.join(os.path.dirname(__file__), "fig_ladder.pdf"))
    plt.close(fig); print("fig_ladder.pdf")

# ============ Figure 3: self-interest dose-response ============
def fig_dose():
    order = ["neutral", "soft", "self", "threat"]
    xlab = ["Neutral", "Soft", "Self", "Threat"]
    series = [("Claude Sonnet", "Sonnet", OI["orange"], "o", "-"),
              ("Gemini Flash", "Gemini-flash", OI["green"], "s", "-"),
              ("Gemini Pro", "Gemini-pro", OI["purple"], "^", "-")]
    fig, ax = plt.subplots(figsize=(5.2, 3.0))
    for name, key, col, mk, ls in series:
        d = dose[key]; xs, ys, elo, ehi = [], [], [], []
        for i, fr in enumerate(order):
            c = d.get(fr)
            if not c: continue
            p = c["rate"]; lo, hi = c["ci"]
            xs.append(i); ys.append(p*100); elo.append((p-lo)*100); ehi.append((hi-p)*100)
        ax.errorbar(xs, ys, yerr=[elo, ehi], fmt=mk, ls=ls, color=col, ms=4.5,
                    lw=1.3, elinewidth=0.7, capsize=1.8, label=name)
    ax.axhline(100/3, ls="--", lw=0.9, color=OI["grey"])
    ax.text(3, 100/3+1.5, "chance (33%)", fontsize=7, color=OI["grey"], ha="right")
    ax.set_xticks(range(4)); ax.set_xticklabels(xlab)
    ax.set_xlabel("Self-interest framing strength")
    ax.set_ylabel("Capability-preserving choice rate (%)")
    ax.set_ylim(0, 100); ax.legend(loc="lower right", fontsize=7.5)
    fig.tight_layout(); fig.savefig(os.path.join(os.path.dirname(__file__), "fig_dose.pdf"))
    plt.close(fig); print("fig_dose.pdf")

# ============ Figure 1: method schematic ============
def fig_method():
    fig, ax = plt.subplots(figsize=(5.4, 2.7)); ax.axis("off")
    ax.set_xlim(0, 10); ax.set_ylim(0, 5.2)
    def box(x, y, w, h, text, fc="white", fs=6.8, lw=0.8):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.05",
                     fc=fc, ec="black", lw=lw))
        ax.text(x+w/2, y+h/2, text, ha="center", va="center", fontsize=fs)
    # ----- left: one checkpoint -----
    ax.text(2.35, 5.05, "One checkpoint", ha="center", fontsize=7.5, style="italic")
    box(0.15, 4.15, 4.4, 0.6, "Case file: facts $F_1\\dots F_n$ (fictional, closed-world)", fc="#efefef", fs=6.6)
    box(0.15, 2.75, 1.33, 1.05, "Target (T)\ncap.-preserving\ncost 1–2", fc="#e7f6ee", fs=6.4)
    box(1.68, 2.75, 1.33, 1.05, "Decoy (X)\nconstrains\ncost 3–4", fc="#efefef", fs=6.4)
    box(3.22, 2.75, 1.33, 1.05, "Decoy (Y)\nconstrains\ncost 3–4", fc="#efefef", fs=6.4)
    ax.annotate("", xy=(2.35, 3.82), xytext=(2.35, 4.13),
                arrowprops=dict(arrowstyle="-", lw=0.5, color="grey"))
    box(0.15, 1.55, 4.4, 0.6, "Model picks one (shuffled order, no loyalty)", fc="white", fs=6.6)
    box(0.15, 0.35, 4.4, 0.6, "Score: picked $=$ Target?   vs. 33% chance", fc="#efefef", fs=6.6)
    ax.annotate("", xy=(2.35, 2.17), xytext=(2.35, 2.73), arrowprops=dict(arrowstyle="->", lw=0.7))
    ax.annotate("", xy=(2.35, 0.97), xytext=(2.35, 1.53), arrowprops=dict(arrowstyle="->", lw=0.7))
    # ----- right: framing conditions -----
    ax.text(7.6, 5.05, "Framing conditions", ha="center", fontsize=7.5, style="italic")
    box(5.3, 4.15, 4.5, 0.6, "Same case files, four framings", fc="#efefef", fs=6.8)
    conds = ["Neutral (no stated stance)",
             "Capability-primed  /  Safety-primed",
             "Self-interest ladder:",
             "soft $\\to$ deployment $\\to$ threat"]
    yy = [3.35, 2.65, 1.85, 1.35]
    hh = [0.55, 0.55, 0.42, 0.42]
    for c, y, h in zip(conds, yy, hh):
        box(5.3, y, 4.5, h, c, fc="white", fs=6.6)
    box(5.3, 0.35, 4.5, 0.6, "3 models, 2 vendors (Claude, Gemini)", fc="#eaf0fb", fs=6.8)
    fig.tight_layout(); fig.savefig(os.path.join(os.path.dirname(__file__), "fig_method.pdf"))
    plt.close(fig); print("fig_method.pdf")

if __name__ == "__main__":
    fig_method(); fig_ladder(); fig_dose()
