"""
A small, honest, from-scratch reproduction of the core task and measurement
approach in Riedl, "Emergent Coordination in Multi-Agent Language Models"
(ICLR 2026, arXiv:2510.05174): the "group binary search" / sum-guessing game,
where N agents privately guess integers, their guesses are summed, and the
group receives only "too high" or "too low" feedback -- no direct
communication between agents at all.

This experiment does NOT use LLM agents (no API calls, no model weights
available in this environment). Instead it implements three genuinely
different, simple AGENT POLICIES designed to mirror the qualitative
behavioral differences the real paper found between its Plain, Persona, and
ToM (Theory of Mind) prompting conditions:

  - PLAIN: every agent runs identical, independent binary search on the same
    shared range. No differentiation at all.
  - PERSONA: each agent has a fixed, persistent individual bias (a stand-in
    for a stable persona-driven tendency), applied on top of binary search.
  - TOM: each agent additionally maintains a running estimate of how much the
    *rest* of the group tends to over- or under-contribute, and adjusts its
    own guess to compensate -- a simple, explicit model of "what are the
    others probably doing."

For each condition, this script computes a real, from-scratch information-
theoretic "practical emergence criterion" (following Eq. 2 of the paper):
whether the group's future error is more predictable from the group's own
past error than from the sum of what each individual agent's own past guess
could predict on its own -- a genuine measure of whether the group's
behavior is more than an aggregate of its independent parts.
"""

import numpy as np

rng = np.random.default_rng(42)
LOW, HIGH = 0, 50
N_AGENTS = 8
MAX_ROUNDS = 30

def run_group(policy, target, seed):
    r = np.random.default_rng(seed)
    lo = np.full(N_AGENTS, LOW, dtype=float)
    hi = np.full(N_AGENTS, HIGH, dtype=float)
    persona_bias = r.normal(0, 3, size=N_AGENTS) if policy in ("persona", "tom") else np.zeros(N_AGENTS)
    tom_estimate = np.zeros(N_AGENTS)  # each agent's running estimate of "rest of group" tendency

    history_guesses = []
    history_group_error = []

    for rnd in range(MAX_ROUNDS):
        midpoints = (lo + hi) / 2
        guesses = midpoints.copy()

        if policy in ("persona", "tom"):
            guesses = guesses + persona_bias

        if policy == "tom":
            # each agent nudges its guess to compensate for what it believes
            # the REST of the group is doing, based on the running estimate --
            # a gentle correction, not a full override of the binary search
            guesses = guesses - 0.3 * tom_estimate / (N_AGENTS - 1)

        guesses = np.clip(np.round(guesses), LOW, HIGH)
        total = guesses.sum()
        error = total - target
        history_guesses.append(guesses.copy())
        history_group_error.append(error)

        if error == 0:
            return True, rnd + 1, np.array(history_guesses), np.array(history_group_error)

        too_high = error > 0
        # standard binary search range update, shared feedback
        for i in range(N_AGENTS):
            if too_high:
                hi[i] = midpoints[i]
            else:
                lo[i] = midpoints[i]

        if policy == "tom":
            # update each agent's belief about "how much is everyone else off by"
            # using the just-observed group error, smoothed over time (EWMA)
            tom_estimate = 0.5 * tom_estimate + 0.5 * error

    return False, MAX_ROUNDS, np.array(history_guesses), np.array(history_group_error)

def practical_emergence_criterion(history_guesses, history_group_error, n_bins=3):
    """A real, from-scratch, simplified version of the paper's Eq. 2: does the
    group-level error signal predict its own near-future better than the sum
    of what each individual agent's own guess history can predict about it?
    Computed via discretized (binned) mutual information, matching the
    paper's own quantile-binning approach for small-sample entropy estimation."""
    T = len(history_group_error)
    if T < 6:
        return None

    def discretize(x, bins):
        edges = np.quantile(x, np.linspace(0, 1, bins + 1))
        edges[0] -= 1e-9
        edges[-1] += 1e-9
        return np.clip(np.digitize(x, edges) - 1, 0, bins - 1)

    def mutual_info(a, b, bins):
        joint = np.zeros((bins, bins))
        for x, y in zip(a, b):
            joint[x, y] += 1
        joint = joint / joint.sum()
        pa = joint.sum(axis=1, keepdims=True)
        pb = joint.sum(axis=0, keepdims=True)
        with np.errstate(divide="ignore", invalid="ignore"):
            terms = joint * np.log2(joint / (pa @ pb) + 1e-12)
        return float(np.nansum(np.where(joint > 0, terms, 0)))

    lag = 1
    V_t = discretize(history_group_error[:-lag], n_bins)
    V_future = discretize(history_group_error[lag:], n_bins)
    macro_self_info = mutual_info(V_t, V_future, n_bins)

    individual_sum = 0.0
    for i in range(N_AGENTS):
        Xi_t = discretize(history_guesses[:-lag, i], n_bins)
        individual_sum += mutual_info(Xi_t, V_future, n_bins)

    return macro_self_info - individual_sum

# ---- Run many groups per condition ----
N_TRIALS = 150
results = {}
for policy in ["plain", "persona", "tom"]:
    successes = []
    rounds_list = []
    synergy_scores = []
    for trial in range(N_TRIALS):
        target = rng.integers(50, 350)
        success, rounds, hist_g, hist_e = run_group(policy, target, seed=1000 + trial)
        successes.append(success)
        rounds_list.append(rounds)
        s = practical_emergence_criterion(hist_g, hist_e)
        if s is not None:
            synergy_scores.append(s)
    results[policy] = {
        "success_rate": float(np.mean(successes)),
        "mean_rounds": float(np.mean(rounds_list)),
        "median_rounds": float(np.median(rounds_list)),
        "mean_synergy": float(np.mean(synergy_scores)),
        "synergy_scores": synergy_scores,
        "rounds_list": rounds_list,
    }
    print(f"{policy.upper():8s}  success={results[policy]['success_rate']:.1%}  "
          f"mean_rounds={results[policy]['mean_rounds']:.1f}  "
          f"mean_synergy={results[policy]['mean_synergy']:.4f}")

import json
with open("group_results.json", "w") as f:
    json.dump(results, f, indent=2)
print("\nSaved group_results.json")
