import subprocess,sys,os,unittest
from _common import ROOT

class OTSExternalAnchor(unittest.TestCase):
    def test_frozen_pending_proof(self):
        r=subprocess.run([sys.executable,os.path.join(ROOT,"tools","ots_anchor_check.py")],capture_output=True,text=True)
        self.assertEqual(0,r.returncode,r.stdout+r.stderr)
        self.assertIn("pending=4 bitcoin=0",r.stdout)

if __name__=="__main__":
    unittest.main()
