#!/usr/bin/env python3
"""Reproduce an API-unit mismatch invisible to Git's text-conflict detector.

Two branches pass their own unit tests. They change separate files and
merge without Git conflict. Isolated tests still pass after merging; an
end-to-end contract check reveals the incompatible interpretations.
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ENV={**os.environ, 'GIT_AUTHOR_NAME':'Semantic Demo', 'GIT_COMMITTER_NAME':'Semantic Demo',
     'GIT_AUTHOR_EMAIL':'experiment@example.invalid', 'GIT_COMMITTER_EMAIL':'experiment@example.invalid',
     'PYTHONDONTWRITEBYTECODE':'1'}

def sh(cwd, *cmd, check=True):
    p=subprocess.run(cmd,cwd=str(cwd),env=ENV,capture_output=True,text=True,timeout=20)
    if check and p.returncode: raise RuntimeError(f'{cmd}: {p.stderr}\n{p.stdout}')
    return p

def write(path, value):
    path.parent.mkdir(exist_ok=True,parents=True)
    path.write_text(value,encoding='utf-8')

def main(output='results/semantic_conflict.json'):
    with tempfile.TemporaryDirectory(prefix='semantic_git_') as root:
        root=Path(root);repo=root/'repo';repo.mkdir()
        sh(repo,'git','init','-q','-b','main')
        write(repo/'billing.py', 'def get_amount():\n    """Initial contract: cents."""\n    return 1000\n')
        write(repo/'tests'/'test_baseline.py','import unittest\nfrom billing import get_amount\nclass Baseline(unittest.TestCase):\n    def test_value_positive(self): self.assertGreater(get_amount(),0)\n')
        sh(repo,'git','add','.');sh(repo,'git','commit','-qm','base')
        branches={}
        isolated_tests={}
        for name in ('A','B'):
            wt=root/f'worker-{name}'
            sh(repo,'git','worktree','add','-q','-b',f'worker-{name}',str(wt),'HEAD')
            if name=='A':
                write(wt/'billing.py','def get_amount():\n    """New interpretation: dollars (silent contract change)."""\n    return 10.0\n')
                write(wt/'tests'/'test_units_A.py', 'import unittest\nfrom billing import get_amount\nclass TestA(unittest.TestCase):\n    def test_new_dollar_value(self): self.assertEqual(get_amount(),10.0)\n')
            else:
                write(wt/'invoice.py','from billing import get_amount\ndef invoice_total_dollars():\n    return get_amount()/100\n')
                write(wt/'tests'/'test_units_B.py', 'import unittest\nfrom unittest.mock import patch\nfrom invoice import invoice_total_dollars\nclass TestB(unittest.TestCase):\n    @patch("invoice.get_amount", return_value=1000)\n    def test_old_cents_assumption(self, _): self.assertEqual(invoice_total_dollars(),10.0)\n')
            isolated_tests[name]=sh(wt,sys.executable,'-m','unittest','discover','-s','tests','-q').returncode==0
            sh(wt,'git','add','.');sh(wt,'git','commit','-qm',f'worker {name}')
            branches[name]=sh(wt,'git','rev-parse','HEAD').stdout.strip()
            sh(repo,'git','worktree','remove','--force',str(wt))
        conflicts=0
        for sha in branches.values():
            result=sh(repo,'git','cherry-pick',sha,check=False)
            conflicts+=int(result.returncode!=0)
            if result.returncode: raise RuntimeError(result.stderr)
        unit=sh(repo,sys.executable,'-m','unittest','discover','-s','tests','-q',check=False)
        full_check=sh(repo,sys.executable,'-c','from invoice import invoice_total_dollars; assert invoice_total_dollars()==10.0, f"Expected $10.00, got ${invoice_total_dollars():.2f}"',check=False)
        out={'worker_A_unit_tests_pass':isolated_tests['A'], 'worker_B_unit_tests_pass':isolated_tests['B'],
             'git_text_conflicts':conflicts,'combined_isolated_unit_tests_pass':unit.returncode==0,
             'end_to_end_contract_check_pass':full_check.returncode==0,
             'expected_dollars':10.0,
             'observed_dollars':sh(repo,sys.executable,'-c','from invoice import invoice_total_dollars;print(invoice_total_dollars())').stdout.strip(),
             'reason':'Worker A changed the unit semantics of get_amount from cents to dollars while worker B still divides by 100. Mock-isolated tests hide the cross-module mismatch.',
             'notes':'One deliberately constructed counterexample, not a measured incidence rate.'}
        output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(json.dumps(out,indent=2),encoding='utf-8')
        print(json.dumps(out,indent=2))
        assert all(isolated_tests.values()) and conflicts==0 and unit.returncode==0 and full_check.returncode!=0
        return out

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='results/semantic_conflict.json')
    args=parser.parse_args(); main(args.output)
