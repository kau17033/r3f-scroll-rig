import hashlib,unittest
from _common import ROOT  # noqa: F401
from c7_prospective import ordered_candidates,batch_size

class C7ProspectiveUnit(unittest.TestCase):
    def test_order_is_outcome_independent_hash_order(self):
        task={"task_id":"X","candidates":["b","a","c"],"target":"secret"}
        got=ordered_candidates(task)
        want=sorted(task["candidates"],key=lambda p:hashlib.sha256(("X|"+p).encode()).hexdigest())
        self.assertEqual(want,got)
        task2=dict(task);task2["target"]="different"
        self.assertEqual(got,ordered_candidates(task2))

    def test_batch_size_is_bounded(self):
        self.assertEqual(4,batch_size({"batch_fraction":1.0},4))
        self.assertEqual(2,batch_size({"batch_fraction":0.5},4))
        self.assertEqual(1,batch_size({"batch_fraction":0.01},4))

if __name__=="__main__":
    unittest.main()
