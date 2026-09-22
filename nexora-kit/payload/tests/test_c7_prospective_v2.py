import hashlib,unittest
from _common import ROOT  # noqa: F401
from c7_prospective_v2 import batch_size,candidate_order,generate_query

class C7ProspectiveV2Unit(unittest.TestCase):
    def test_candidate_order_does_not_use_outcome(self):
        task={"task_id":"T","candidates":["z.py","a.py","m.py","q.py"]}
        got=candidate_order(task)
        want=sorted(task["candidates"],key=lambda p:hashlib.sha256(("T|"+p).encode()).hexdigest())
        self.assertEqual(want,got)

    def test_query_generator_returns_unique_line(self):
        task={"task_id":"T"}
        bodies={
            "a.py":"common = 123456789012345\nunique_alpha_value = 12345678901234567890\n",
            "b.py":"common = 123456789012345\nunique_beta_value = 123456789012345678901\n",
            "c.py":"common = 123456789012345\nunique_gamma_value = 1234567890123456789012\n",
            "d.py":"common = 123456789012345\nunique_delta_value = 12345678901234567890123\n",
        }
        q,path,count=generate_query(task,bodies)
        self.assertGreaterEqual(count,4)
        self.assertIn(q,bodies[path])
        self.assertEqual(1,sum(q in body for body in bodies.values()))

    def test_batch_size_translation(self):
        self.assertEqual(4,batch_size({"batch_fraction":1.0},4))
        self.assertEqual(3,batch_size({"batch_fraction":2/3},4))

if __name__=="__main__":
    unittest.main()
