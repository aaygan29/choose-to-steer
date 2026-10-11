#!/usr/bin/env python3
"""Run the capability-primed vs safety-primed contrast across many Gemini models.

Free tier caps generateContent at 20 requests/day PER MODEL, so each model gets
exactly one framing-contrast pass: 2 framings x 10 checkpoints = 20 calls. The
per-model steerable swing (capability - safety) is the quantity of interest.
Writes gemini_multi.csv and prints per-model rates. Tolerant of 404 (gated) and
429 (quota) — a model that errors is simply skipped / truncated.
"""
import csv, random, time, sys
from harness import call_gemini, build_prompt, parse_choice, FRAMINGS
from sessions import TARGET, SESSIONS

# 10 checkpoints: CP1 and CP4 of each session (spread across the design)
CPS = [(s, f"{s}{n}") for s in ["A", "C", "D", "F", "G"] for n in (1, 4)]
FRAMES = ["capability", "safety"]

MODELS = [
    "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash",
    "gemini-3.5-flash-lite", "gemini-3-flash-preview", "gemini-3.1-flash-lite",
    "gemini-3.1-pro-preview", "gemini-pro-latest", "gemini-flash-lite-latest",
    "gemini-2.5-flash-lite", "gemma-4-31b-it",
]

rows = []
for model in MODELS:
    got = 0; exhausted = False; gated = False
    for fr in FRAMES:
        if exhausted or gated:
            break
        system = FRAMINGS[fr]
        for sid, cid in CPS:
            rng = random.Random(hash((model, fr, cid)) & 0xffffffff)
            prompt, letters = build_prompt(sid, cid, rng)
            try:
                out = call_gemini(model, system, prompt)
            except Exception as e:
                msg = str(e)
                if "RESOURCE_EXHAUSTED" in msg or "429" in msg:
                    exhausted = True; break
                if "404" in msg or "NOT_FOUND" in msg or "not supported" in msg.lower():
                    gated = True; break
                continue  # transient; skip this call
            num = parse_choice(out)
            if num is None:
                continue
            picked = letters[num - 1]
            rows.append({"model": model, "framing": fr, "checkpoint": cid,
                         "is_target": int(picked == TARGET[cid])})
            got += 1
            time.sleep(0.8)
    status = "exhausted" if exhausted else ("gated/unavailable" if gated else "ok")
    print(f"{model:28s} {got:2d} calls recorded  [{status}]", flush=True)

with open("gemini_multi.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["model", "framing", "checkpoint", "is_target"])
    w.writeheader(); w.writerows(rows)
print(f"\nwrote gemini_multi.csv ({len(rows)} decisions)")
