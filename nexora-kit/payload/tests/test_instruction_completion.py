import os,subprocess,sys,unittest
from _common import ROOT
class InstructionCompletion(unittest.TestCase):
    def test_instruction_completion_artifacts(self):
        r=subprocess.run([sys.executable,os.path.join(ROOT,'tools','instruction_completion_check.py')],capture_output=True,text=True)
        self.assertEqual(0,r.returncode,r.stdout+r.stderr)
        self.assertIn('INSTRUCTION_COMPLETION: PASS',r.stdout)
if __name__=='__main__': unittest.main()
