import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from run_worktree_experiment import case, summarise
from semantic_conflict_demo import main as semantic_check

class TestGitExperiment(unittest.TestCase):
    def test_independent_smoke(self):
        r=case(2,False,0,0.0)
        self.assertEqual(r['conflicts'],0)
        self.assertTrue(r['tests_passed'])
        self.assertEqual(r['final_test_count'],5)

    def test_coupled_conflicts_are_detectable(self):
        r=case(4,True,0,0.0)
        self.assertEqual(r['conflicts'],3)
        self.assertTrue(r['tests_passed'])

    def test_semantic_conflict_evades_local_tests(self):
        with tempfile.TemporaryDirectory() as td:
            r=semantic_check(str(Path(td)/'semantic.json'))
        self.assertEqual(r['git_text_conflicts'],0)
        self.assertTrue(r['combined_isolated_unit_tests_pass'])
        self.assertFalse(r['end_to_end_contract_check_pass'])
        self.assertEqual(float(r['observed_dollars']),0.1)

if __name__=='__main__':unittest.main()
