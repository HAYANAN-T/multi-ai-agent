# The Mythical Agent-Month — a reproducible Git coordination experiment

This is the **code-only** research project accompanying the Medium essay *The Mythical Agent-Month*. It runs deterministic Python workers in real Git worktrees and integrates them via real commits and cherry-picks. **It does not invoke or benchmark ChatGPT, Claude, Cursor, Codex, or any other LLM.** No API keys needed.

## Run it yourself

Requires Python 3.10+ and Git.

```bash
python run_worktree_experiment.py --trials 12 --delay 0.11 --output results
python semantic_conflict_demo.py --output results/semantic_conflict.json
python -m unittest discover -s tests -v
```

For the article's ordinary white-background Python charts and optional explanatory GIF:

```bash
python -m pip install -r requirements.txt
python plot_results.py --results results --output ../article_assets
python render_merge_animation.py --output ../article_assets/fig_worktree_merge_replay.gif
```

The charts and photographs are **not stored in this repo**, only the scripts that produce the analysis graphics and the measured experiment results.

## What the experiment controls

- Four Python feature tasks per run, always the same task count.
- 1, 2 or 4 simultaneous **scripted** workers.
- Independent files versus concurrent changes to a shared registry line.
- Isolated Git worktrees, actual local commits, cherry-picks, a deterministic resolver of simple text conflicts, and a final five-test suite.
- The `--delay` is synthetic per-task time (default 0.11 seconds), **not** an AI inference or thought-time measurement.
- 12 saved trials for each of the six conditions (72 total). Results are environment-sensitive. Order of conditions varied deterministically by trial.

`results/raw_runs.csv` includes phase times, worker effort sums, exact conflicts and final-test status for every run. `results/summary.json` stores medians and inter-trial ranges. `results/run_metadata.json` records interpreter, Git version and experimental settings. `results/semantic_conflict.json` records an independent **constructed counterexample**, not a frequency study.

### Semantic counterexample

Two branches modify separate files. One silently redefines an amount from cents to dollars; another consumes that amount as cents. Each unit test passes in its isolated branch; the combined isolated tests pass; Git reports zero conflicts. The real end-to-end contract check reports $0.10 instead of $10.00. This is not an AI hallucination measurement; it demonstrates a *class of integration bugs* that Git cannot detect.

## Limitations

- Four tiny Python tasks and five simple tests do not represent a production codebase.
- The resolver understands one predetermined shared-registry format. Real conflicts may require significant engineer judgment.
- Local worktree setup, subprocess startup and disk scheduling can dominate timings.
- Not measured: LLM quality, API tokens, dollars, human review time, bug incidence in production, model thinking time, or production-scaled concurrency.
- Percentiles across 12 runs are descriptive, not causal confidence intervals. Speedups are ratios of medians in this host environment only.

Results are open for audit and independent reruns. Never present this script as a commercial-model head-to-head test.
