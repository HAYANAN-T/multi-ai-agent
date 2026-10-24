# Who Wants to Be a Millionaire, but Every Player Is an AI — Controlled Decision Experiment

**This is a reproducible synthetic-policy experiment, not a head-to-head benchmark of commercial language models.** Six programmed decision agents share the same noisy answer engine and a fitted probability calibrator. The public quiz questions are displayed to readers; the base system **does not read or reason over the question text**. Correct answers are known to the experimental environment so synthetic evidence can be generated. There are **no OpenAI, Claude, Gemini or other LLM API calls** and no fictitious hidden reasoning traces.

## Why this exists

A controlled 15-question quiz format compares decision policy, not trivia recall: answer immediately, use 50:50, ask the simulated audience, phone a fallible friend, or walk away. It measures which policies handle uncertainty, risk and scarce information more effectively on the **same paired question/evidence stream**.

Six policies: `Swagger` (always guess), `Flash` (inflated subjective confidence), `Chorus` (over-trust audience), `Switch` (fixed help / walk thresholds), `Anchor` (protect winnings), and `Compass` (approximate reward- and information-aware decisions).

## Reproduce the experiment

Requires Python 3.10+. GitHub users can run everything without keys or network calls after dependencies are installed.

```bash
python -m pip install -r requirements.txt
python arena.py --episodes 1200 --seed 2026 --output results
python analyze.py --input results --episodes 1200 --seed 2026
python build_replay.py --featured results/featured.json --output viewer/millionaire_replay.html
python tests.py
```

Open `viewer/millionaire_replay.html` in any modern browser. Select contestants and scrub the recorded steps or press Play. This is a deterministic replay of saved policy events, not live model inference.

To produce conventional white-background research charts:

```bash
python plot_results.py --input results --output generated_figures
```

To capture screenshots and five small animated GIFs from the **actual browser-rendered simulation**, with Chromium installed locally:

```bash
python capture_replay.py --viewer viewer/millionaire_replay.html --output generated_gifs
```

`capture_replay.py` uses Chromium at `/usr/bin/chromium` by default. Adjust that path for Windows/macOS if necessary. Generated images go into ignored output folders, not into the GitHub code-only source tree.

## Experimental design

- 15-question US-style money ladder, $1,000 and $32,000 guaranteed milestones.
- 36 original, hand-written display questions split into three tiers; each episode draws five from each tier.
- A seeded stochastic evidence generator increases the true option's signal as a function of difficulty, creating uncertainty deliberately. **This is NOT an evaluation of models' knowledge of trivia**.
- A logistic correctness calibrator is trained on 16,000 separate examples and evaluated on 4,500 held-out examples.
- All six agents see identical answer signals and lifeline responses in each seed; policies alone differ.
- 50:50 removes two incorrect choices randomly. A simulated friend gives a difficulty-dependent suggestion. The simulated audience consists of forty votes with a deliberately introduced correlated-wrong-majority regime (~18%). No real audience was polled.
- One policy performs a one-step expected-value comparison with a heuristic cost for spending help; it is **not** a mathematically optimal fifteen-step strategy.
- The 1,200-seed ablation compares the same Compass policy with all lifelines versus no lifelines, with a bootstrap interval over paired seed differences.

## Files and reproducibility

- `arena.py`: data generation, calibration, agents, scoring, and paired tournaments
- `quiz_bank.py`: human-readable multiple-choice question bank
- `analyze.py`: event-level lifeline inspection
- `plot_results.py`: reproducible white-background analysis figures
- `build_replay.py`: self-contained animated browser replay generated from event JSON
- `capture_replay.py`: real browser GIF/screenshot capture, stored outside GitHub
- `tests.py`: deterministic smoke, policy, and 50:50 fairness tests
- `results/summary.json`: measured numeric headline outcomes
- `results/tournaments.csv`, `results/lifeline_ablation.csv`, `results/lifeline_events.csv`, `results/calibration.csv`: raw observations and paired comparisons
- `results/featured.json`: 42-seed per-step recorded quiz actions
- `viewer/millionaire_replay.html`: standalone recorded 2D studio replay

These experiments isolate **decision-making under uncertainty**, not actual LLM hallucination or hidden model introspection. To evaluate real LLMs in a future version, record the model ID, model version, full prompt, options, selected answer, calibrated probability elicitation method, tool usage, latency, cost, and independently judged answer key for each question. Keep those results separate from this controlled simulation.

## References

https://proceedings.mlr.press/v70/guo17a.html
https://aclanthology.org/2025.tacl-1.26/
https://pmc.ncbi.nlm.nih.gov/articles/PMC3107299/
https://wwbm.com/rules
