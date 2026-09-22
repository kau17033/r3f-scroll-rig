import copy
import json
import os
import subprocess
import sys
import unittest

from _common import ROOT  # noqa: E402
from dream_replay import (
    INCUMBENT,
    adaptive_next_budget,
    improve_policy,
    load_world,
    select_batch,
)

WORLD = os.path.join(ROOT, "control", "replay_worlds", "bootstrap_convergence_20260922.json")


class DreamReplay(unittest.TestCase):
    def test_bootstrap_search_is_reproducible_and_non_decreasing(self):
        world = load_world(WORLD)
        result = improve_policy(world)
        self.assertGreaterEqual(result["candidate_count"], 1000)
        self.assertTrue(result["replay_non_decrease"])
        self.assertGreaterEqual(
            result["selected"]["result"]["reward"],
            result["incumbent"]["result"]["reward"],
        )

    def test_prefix_only_first_decision_cannot_see_hidden_scores(self):
        world_a = load_world(WORLD)
        world_b = copy.deepcopy(world_a)
        for node in world_b["nodes"]:
            if node["id"] != world_b["root_id"]:
                node["score"] = 9999.0 - node["created_index"]
                node["evidence_gain"] = 999.0
        revealed = {world_a["root_id"]}
        self.assertEqual(
            select_batch(world_a, revealed, INCUMBENT),
            select_batch(world_b, revealed, INCUMBENT),
        )

    def test_adaptive_budget_conserves_when_live_score_improves(self):
        history = [
            {"best_score": 0.4, "attempt_budget": 100},
            {"best_score": 0.5, "attempt_budget": 100},
        ]
        self.assertEqual(80, adaptive_next_budget(history, {}, 20, 200, 100))

    def test_adaptive_budget_expands_on_plateau_with_replay_support(self):
        history = [
            {"best_score": 0.5, "attempt_budget": 80},
            {"best_score": 0.5, "attempt_budget": 80},
        ]
        self.assertEqual(
            100,
            adaptive_next_budget(
                history,
                {"higher_exploration_improves": True},
                20, 200, 80,
            ),
        )

    def test_bootstrap_cli(self):
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "tools", "dream_replay.py"), "--bootstrap-check"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertIn("BOOTSTRAP: PASS", r.stderr)


if __name__ == "__main__":
    unittest.main()
