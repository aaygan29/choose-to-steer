# choose-to-steer

Proof-of-concept harness for a single question:

> **Given a free choice and no assigned loyalty, does an AI agent lean toward the
> capability-preserving option when advising a safety researcher — above chance?**

This is the *propensity* complement to a human-subjects study that asks whether an
AI advisor with an **assigned** loyalty can move a scientist's decisions. Here the
loyalty is **free**: the model picks on its own, and we measure the base rate.

## What's here

| File | Purpose |
|---|---|
| `sessions.py` | The five research-scenario sessions (A, C, D, F, G): 20 checkpoints, 60 options, with the capability-preserving **target** option per checkpoint (from the study's answer key). |
| `harness.py` | Model-agnostic runner. Shuffles options, applies a framing, calls an LLM API, records whether the model picked the target, aggregates target-pick rate vs the 33.3% chance baseline with Wilson CIs + an exact binomial test, and emits a CSV + bar-chart SVG. |
| `gen_pilot.py` / `score_pilot.py` | The subagent pilot path: generate per-run randomized prompts + a hidden display→option map, then score written answers. |
| `make_results.py` | Renders `results/pilot_result.svg` from `pilot_summary.json`. |
| `results/` | The pilot run used in the POC: raw per-run answers, maps, `pilot_summary.json`, and the figure. |
| `DESIGN_REVIEW.md` | A critical review of the underlying scenario design (confounds and fixes), partly grounded in the pilot. |

## The design (one checkpoint)

Each checkpoint shows a case file + three options: one **target** (capability-preserving,
expert-coded capability cost 1–2) and two **decoys** that constrain capability by
different mechanisms (cost 3–4). The options are blended so none stands out and the
trade-off is real. The harness shows them in shuffled order, with no hint of which is
which, and asks for a single recommendation.

Four **framings** form an escalation ladder:

- `neutral` — plain advisor role (the base-rate question)
- `capability` — "you value shipping capable models"
- `safety` — "you value caution" (should pull below chance)
- `goalconflict` — the model's deployment depends on shipping capable models (Apollo-style nudge)

**The causal reading is the *contrast***: a pick rate that **moves with the framing**
is a propensity; a rate that is high but framing-invariant is just cost-benefit
reasoning. (See the caveat in `DESIGN_REVIEW.md` §2.)

## Run it

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...        # or OPENAI_API_KEY

# full ladder, all five sessions, 20 samples per checkpoint per framing
python3 harness.py --provider anthropic --model claude-sonnet-4-5 --n 20
python3 harness.py --provider openai    --model gpt-4o           --n 20

# inspect the exact prompts without calling any API
python3 harness.py --dry-run --sessions A --framings neutral --n 1
```

Outputs: `results_<model>.csv`, `results_<model>_summary.json`, `results_<model>.svg`.

## Pilot result (POC)

Claude Sonnet, **neutral framing only**, 160 free-choice decisions (8 runs × 20 checkpoints):

- **Overall target-pick rate = 53.1%** vs 33.3% chance (95% CI [45.4, 60.7], exact binomial *p* < 1e-6).
- Strongly concentrated in sessions **D** (interpretability, 75%) and **F** (math, 75%); at/below chance in **C** (34%) and **G** (28%).

![pilot result](results/pilot_result.png)

**This is a pilot, not a validated result** (one model, N=160, neutral framing only).
An above-chance neutral rate does **not** by itself prove a capability lean — see
`DESIGN_REVIEW.md` §2. Run the capability- vs safety-primed contrast to separate a
propensity from ordinary cost-benefit reasoning.

## Reproducing the pilot

The pilot was driven by an orchestrator that spawned 8 independent model runs, each
answering all 20 checkpoints (neutral framing) in a randomized order. Raw answers
(`results/answers_*.txt`) and the display→option maps (`results/map_*.json`) are kept
for audit. To score from the repo root:

```bash
cp results/answers_*.txt results/map_*.json .
python3 score_pilot.py
```

For new runs against an API, prefer `harness.py`.
