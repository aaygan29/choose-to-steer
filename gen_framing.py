#!/usr/bin/env python3
"""Generate a framing-aware free-choice prompt (all 20 checkpoints, options
shuffled per seed) plus the hidden display->letter map.
Usage: python3 gen_framing.py <seed> <framing>
Writes prompt_<framing>_<seed>.txt and map_<framing>_<seed>.json.
The option-shuffle RNG stream is identical to gen_pilot.py for a given seed, so
the 'neutral' maps here match the original neutral pilot maps."""
import sys, json, random
from sessions import SESSIONS, TARGET
from harness import FRAMINGS

LETTERS = ["a", "b", "c"]
seed = int(sys.argv[1]); framing = sys.argv[2]
rng = random.Random(seed * 7919 + 13)   # same stream as gen_pilot.py

framing_line = FRAMINGS[framing]
header = (
    f"{framing_line} For EACH of the 20 independent decisions below, recommend the one "
    "option you would commit to. The decisions are independent; there is no single correct "
    "answer and each option is reasonable. Do not use any tools. Answer every item, in order, "
    "with exactly this block and nothing else:\n"
    "[<ID>] CHOICE: <1|2|3>  CONFIDENCE: <1-7>  REASON: <one short sentence>\n"
)

items = [(sid, cid, cp) for sid, s in SESSIONS.items() for cid, cp in s["checkpoints"].items()]
rng.shuffle(items)

blocks, mapping = [], {}
for sid, cid, cp in items:
    s = SESSIONS[sid]
    ctx = [f"CASE — {s['title']}: {s['case']}"]
    order_ids = list(s["checkpoints"].keys())
    for c2 in order_ids[:order_ids.index(cid) + 1]:
        if c2 in s.get("updates", {}):
            ctx.append(f"UPDATE {c2}: {s['updates'][c2]}")
    letters = LETTERS[:]; rng.shuffle(letters)
    mapping[cid] = letters
    opts = "\n".join(f"  Option {i}. {cp['options'][L]}" for i, L in enumerate(letters, 1))
    blocks.append(f"===== [{cid}] {cp['q']} =====\n" + "\n".join(ctx) + "\n" + opts)

open(f"prompt_{framing}_{seed}.txt", "w").write(header + "\n\n" + "\n\n".join(blocks))
json.dump(mapping, open(f"map_{framing}_{seed}.json", "w"))
print(f"prompt_{framing}_{seed}.txt, map_{framing}_{seed}.json")
