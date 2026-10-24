#!/usr/bin/env python3
"""Controlled, repeated Git-worktree experiment; workers are deterministic scripts, never LLMs."""
from __future__ import annotations
import argparse
import ast
import csv
import json
import os
import random
import statistics
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

TASKS = ('alpha', 'beta', 'gamma', 'delta')
ENV = {**os.environ,
       'GIT_AUTHOR_NAME': 'Git Experiment Worker',
       'GIT_COMMITTER_NAME': 'Git Experiment Worker',
       'GIT_AUTHOR_EMAIL': 'worker@example.invalid',
       'GIT_COMMITTER_EMAIL': 'worker@example.invalid',
       'GIT_EDITOR': 'true', 'GIT_SEQUENCE_EDITOR': 'true',
       'PYTHONDONTWRITEBYTECODE': '1'}


def run(*args: str, cwd: Path, check: bool = True) -> subprocess.CompletedProcess[str]:
    p = subprocess.run(args, cwd=str(cwd), env=ENV, text=True, capture_output=True, timeout=35)
    if check and p.returncode != 0:
        raise RuntimeError(f'{args} exited {p.returncode}: {p.stdout}\n{p.stderr}')
    return p


def initialize(repo: Path):
    repo.mkdir(parents=True)
    run('git', 'init', '-q', '-b', 'main', cwd=repo)
    (repo / 'registry.py').write_text('ENABLED = ["base"]\n', encoding='utf-8')
    (repo / 'tests').mkdir()
    (repo / 'tests' / 'test_baseline.py').write_text(
        'import unittest\nfrom registry import ENABLED\n'
        'class Baseline(unittest.TestCase):\n'
        '    def test_registry_starts_with_base(self):\n'
        '        self.assertEqual(ENABLED[0], "base")\n', encoding='utf-8')
    run('git', 'add', '.', cwd=repo)
    run('git', 'commit', '-qm', 'baseline', cwd=repo)


def worker(repo: Path, worktree: Path, task: str, coupled: bool, synthetic_delay: float):
    t0 = time.perf_counter()
    # This delay represents a controlled, simulated work interval; it is NOT model thinking time.
    if synthetic_delay:
        time.sleep(synthetic_delay)
    (worktree / f'feature_{task}.py').write_text(
        f'def handle_{task}(value):\n    return "{task}:" + str(value).strip()\n', encoding='utf-8')
    (worktree / 'tests' / f'test_{task}.py').write_text(
        f'import unittest\nfrom feature_{task} import handle_{task}\n'
        f'class Test_{task}(unittest.TestCase):\n'
        f'    def test_{task}(self):\n'
        f'        self.assertEqual(handle_{task}(" ok "), "{task}:ok")\n', encoding='utf-8')
    if coupled:
        old = ast.literal_eval((worktree / 'registry.py').read_text().split('=', 1)[1].strip())
        (worktree / 'registry.py').write_text('ENABLED = ' + repr(old + [task]) + '\n', encoding='utf-8')
    test = run(sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-q', cwd=worktree)
    run('git', 'add', '.', cwd=worktree)
    run('git', 'commit', '-qm', f'feature: {task}', cwd=worktree)
    sha = run('git', 'rev-parse', 'HEAD', cwd=worktree).stdout.strip()
    return {'task': task, 'sha': sha, 'worker_seconds': time.perf_counter()-t0,
            'test_count': 2, 'test_ok': test.returncode == 0}


def case(workers: int, coupled: bool, trial: int, synthetic_delay: float) -> dict:
    assert workers in (1, 2, 4)
    with tempfile.TemporaryDirectory(prefix='agent_month_git_') as td:
        repo = Path(td) / 'repo'
        initialize(repo)
        started = time.perf_counter()
        prepare_total = 0.0
        working_total = 0.0
        integrate_total = 0.0
        final_test_seconds = 0.0
        sum_worker_seconds = 0.0
        conflicts = 0
        merged = []
        for wave, offset in enumerate(range(0, len(TASKS), workers)):
            tasks = TASKS[offset:offset+workers]
            worktrees = []
            prep_started = time.perf_counter()
            for task in tasks:
                wt = Path(td) / f'worker-{wave}-{task}'
                run('git', 'worktree', 'add', '-q', '-b', f'branch-{wave}-{task}', str(wt), 'HEAD', cwd=repo)
                worktrees.append(wt)
            prepare_total += time.perf_counter()-prep_started
            working_started = time.perf_counter()
            with ThreadPoolExecutor(max_workers=workers) as pool:
                outcomes = list(pool.map(lambda pair: worker(repo, pair[1], pair[0], coupled, synthetic_delay), zip(tasks, worktrees)))
            working_total += time.perf_counter()-working_started
            sum_worker_seconds += sum(x['worker_seconds'] for x in outcomes)
            integrate_started = time.perf_counter()
            for outcome in outcomes:
                applied = run('git', 'cherry-pick', outcome['sha'], cwd=repo, check=False)
                if applied.returncode:
                    if not coupled:
                        raise AssertionError(f'Unexpected independent conflict: {applied.stderr}')
                    conflicts += 1
                    task = outcome['task']
                    (repo / 'registry.py').write_text('ENABLED = ' + repr(['base'] + merged + [task]) + '\n', encoding='utf-8')
                    run('git', 'add', 'registry.py', cwd=repo)
                    run('git', 'cherry-pick', '--continue', cwd=repo)
                merged.append(outcome['task'])
            integrate_total += time.perf_counter()-integrate_started
            for wt in worktrees:
                run('git', 'worktree', 'remove', '--force', str(wt), cwd=repo)
        test_started = time.perf_counter()
        final = run(sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-q', cwd=repo)
        final_test_seconds = time.perf_counter()-test_started
        if coupled:
            registry = ast.literal_eval((repo / 'registry.py').read_text().split('=', 1)[1].strip())
            assert set(registry) == set(['base', *TASKS]), registry
        elapsed = time.perf_counter()-started
        assert len(merged) == 4
        return {'trial': trial, 'case': 'coupled' if coupled else 'independent',
                'workers': workers, 'elapsed_seconds': round(elapsed, 6),
                'prepare_seconds': round(prepare_total, 6),
                'worker_wall_seconds': round(working_total, 6),
                'worker_effort_seconds': round(sum_worker_seconds, 6),
                'integrate_seconds': round(integrate_total, 6),
                'final_test_seconds': round(final_test_seconds, 6),
                'conflicts': conflicts, 'tests_passed': final.returncode == 0,
                'final_test_count': 5, 'synthetic_delay_per_task_seconds': synthetic_delay,
                'workers_are': 'scripted_python_NOT_LLMs'}


def summarise(rows: list[dict]) -> list[dict]:
    summaries = []
    for typ in ('independent', 'coupled'):
        baseline = statistics.median(r['elapsed_seconds'] for r in rows if r['case']==typ and r['workers']==1)
        for workers in (1, 2, 4):
            filtered = [r for r in rows if r['case']==typ and r['workers']==workers]
            def median(key):
                return round(statistics.median(r[key] for r in filtered), 5)
            summaries.append({'case': typ, 'workers': workers, 'trials': len(filtered),
                              'median_elapsed_seconds': median('elapsed_seconds'),
                              'p10_elapsed_seconds': round(sorted(r['elapsed_seconds'] for r in filtered)[max(0, int(.1*(len(filtered)-1)))],5),
                              'p90_elapsed_seconds': round(sorted(r['elapsed_seconds'] for r in filtered)[int(.9*(len(filtered)-1))],5),
                              'speedup_vs_single': round(baseline/median('elapsed_seconds'), 3),
                              'median_prepare_seconds': median('prepare_seconds'),
                              'median_worker_wall_seconds': median('worker_wall_seconds'),
                              'median_worker_effort_seconds': median('worker_effort_seconds'),
                              'median_integrate_seconds': median('integrate_seconds'),
                              'median_final_test_seconds': median('final_test_seconds'),
                              'median_conflicts': median('conflicts'),
                              'all_final_tests_passed': all(r['tests_passed'] for r in filtered)})
    return summaries


def main():
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument('--trials', type=int, default=12)
    a.add_argument('--delay', type=float, default=0.11, help='synthetic per-task work seconds, NOT AI inference')
    a.add_argument('--output', default='results')
    args = a.parse_args()
    assert 1 <= args.trials <= 1000 and 0 <= args.delay <= 3
    dest = Path(args.output)
    dest.mkdir(parents=True, exist_ok=True)
    conditions = [(n, coupled) for coupled in (False, True) for n in (1, 2, 4)]
    rows = []
    for trial in range(args.trials):
        order = conditions[:]
        random.Random(1013 + trial).shuffle(order)
        for n, coupled in order:
            result = case(n, coupled, trial, args.delay)
            rows.append(result)
            print(f'trial {trial+1}/{args.trials}: {result["case"]} / {n} workers: '
                  f'{result["elapsed_seconds"]:.3f}s, {result["conflicts"]} conflicts', flush=True)
    with (dest / 'raw_runs.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summaries = summarise(rows)
    (dest / 'summary.json').write_text(json.dumps(summaries, indent=2), encoding='utf-8')
    (dest / 'run_metadata.json').write_text(json.dumps({'purpose': 'Git coordination mechanics, not actual AI model performance',
            'git_version': run('git', '--version', cwd=dest.resolve()).stdout.strip(),
            'python_version': sys.version.split()[0], 'trials_per_configuration': args.trials,
            'synthetic_delay_per_task_seconds': args.delay,
            'task_count_per_configuration': len(TASKS),
            'clock': 'time.perf_counter() / process wall clock',
            'not_measured': ['LLM reasoning', 'LLM tokens', 'human review', 'true software quality', 'model API cost']},indent=2), encoding='utf-8')
    print('SUMMARY', json.dumps(summaries, indent=2))


if __name__ == '__main__':
    main()
