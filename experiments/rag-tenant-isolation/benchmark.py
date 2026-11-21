"""Tenant-aware retrieval benchmark. Every record and identity is fictional.

This is NOT a language-model prompt-injection test. It benchmarks TF-IDF retrieval
and a deterministic first-result answer renderer, with 768 equal-overlap queries.
"""
import argparse
import json
from collections import Counter
from pathlib import Path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

MONTHS = ("January", "February", "March", "April", "May", "June")
SUBJECTS = ("Algebra", "Physics", "Robotics", "Literature")
COHORTS = ("Atlas", "Birch", "Cedar", "Delta")
TENANTS = 8
K_VALUES = (1, 3, 5, 8, 12)

def corpus(seed):
    records = []
    for tenant in range(TENANTS):
        for mi, month in enumerate(MONTHS):
            for si, subject in enumerate(SUBJECTS):
                for ci, cohort in enumerate(COHORTS):
                    amount = 25 + ((tenant * 41 + mi * 17 + si * 23 + ci * 13) % 175)
                    records.append({
                        "id": f"T{tenant}-{mi}{si}{ci}", "tenant": tenant,
                        "month": month, "subject": subject, "cohort": cohort,
                        "amount_usd": amount,
                        "text": (f"Fee ledger record; Month {month} 2026; Subject {subject}; "
                                 f"Cohort {cohort}; outstanding balance USD {amount}; "
                                 f"Student Synthetic Student T{tenant:02d}-{mi}{si}{ci}; "
                                 f"organization Synthetic Tutor {tenant}."),
                    })
    rng = np.random.default_rng(seed)
    rng.shuffle(records)
    return records

def measure(seed):
    records = corpus(seed)
    questions = [(t, m, s, c) for t in range(TENANTS)
                 for m in MONTHS for s in SUBJECTS for c in COHORTS]
    texts = [f"Fee ledger record: {m} 2026, subject {s}, cohort {c}, outstanding balance"
             for _, m, s, c in questions]
    tfidf = TfidfVectorizer(ngram_range=(1, 2), lowercase=True)
    indexed = tfidf.fit_transform([r["text"] for r in records])
    q_matrix = tfidf.transform(texts)
    all_ranks = np.argsort(-(q_matrix @ indexed.T).toarray(), axis=1, kind="stable")
    tenant_ix = {t: np.array([i for i, r in enumerate(records) if r["tenant"] == t])
                 for t in range(TENANTS)}
    metrics = []
    examples = []
    for k in K_VALUES:
        counts = Counter()
        for qi, (tenant, month, subject, cohort) in enumerate(questions):
            chosen = [records[int(i)] for i in all_ranks[qi, :k]]
            counts["global_wrong_first"] += chosen[0]["tenant"] != tenant
            counts["global_foreign_context"] += any(r["tenant"] != tenant for r in chosen)
            allowed_after = [r for r in chosen if r["tenant"] == tenant]
            target = lambda r: (r["month"], r["subject"], r["cohort"]) == (month, subject, cohort)
            counts["post_target"] += any(map(target, allowed_after))
            counts["post_empty"] += not allowed_after
            candidates = tenant_ix[tenant]
            ranked_within = candidates[np.argsort(-(
                q_matrix[qi] @ indexed[candidates].T).toarray().ravel(), kind="stable")[:k]]
            allowed_before = [records[int(i)] for i in ranked_within]
            counts["pre_target"] += any(map(target, allowed_before))
            counts["pre_foreign"] += any(r["tenant"] != tenant for r in allowed_before)
            if k == 5 and len(examples) < 3 and not allowed_after:
                correct = next(r for r in records if r["tenant"] == tenant and target(r))
                examples.append({"tenant": tenant, "query": texts[qi],
                                 "expected_id": correct["id"], "expected_usd": correct["amount_usd"],
                                 "global_top5": [r["id"] for r in chosen],
                                 "wrong_first_usd": chosen[0]["amount_usd"],
                                 "postfilter_results": [], "prefilter_first": allowed_before[0]["id"]})
        metrics.append({"k": k, "queries": len(questions), **dict(counts),
                        "post_target_pct": round(100 * counts["post_target"] / len(questions), 2),
                        "pre_target_pct": round(100 * counts["pre_target"] / len(questions), 2)})
    # Simulated client-tenant spoofing; trusted is server-supplied synthetic identity.
    client_spoofed = trusted = 0
    for qi, (caller, _month, _subject, _cohort) in enumerate(questions):
        claimed = (caller + 1) % TENANTS
        for tenant, test in ((claimed, "client"), (caller, "trusted")):
            candidates = tenant_ix[tenant]
            best = candidates[np.argmax((q_matrix[qi] @ indexed[candidates].T).toarray().ravel())]
            foreign = records[int(best)]["tenant"] != caller
            if test == "client": client_spoofed += foreign
            else: trusted += foreign
    result = {"seed": seed, "synthetic_records": len(records), "queries": len(questions),
              "tenants": TENANTS, "method": "scikit-learn TF-IDF cosine; deterministic first result; NO LLM",
              "metrics": metrics, "spoof_attempts": len(questions),
              "foreign_with_client_claim": client_spoofed,
              "foreign_with_trusted_identity": trusted, "examples": examples}
    assert len(records) == len(questions) == 768
    assert next(m for m in metrics if m["k"] == 5)["global_wrong_first"] == 672
    assert next(m for m in metrics if m["k"] == 5)["post_target"] == 480
    assert next(m for m in metrics if m["k"] == 5)["pre_target"] == 768
    assert client_spoofed == 768 and trusted == 0
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20261121)
    parser.add_argument("--output", default="results.json")
    args = parser.parse_args()
    r = measure(args.seed)
    if args.output:
        Path(args.output).write_text(json.dumps(r, indent=2), encoding="utf-8")
    print(json.dumps({"seed": r["seed"], "queries": r["queries"],
                      "top5": next(m for m in r["metrics"] if m["k"] == 5),
                      "spoofed": r["foreign_with_client_claim"],
                      "trusted": r["foreign_with_trusted_identity"]}, indent=2))

if __name__ == "__main__": main()
