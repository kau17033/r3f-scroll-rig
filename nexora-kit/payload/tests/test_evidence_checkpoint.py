import json
import os
import shutil
import tempfile
import unittest

from _common import ROOT  # noqa: F401
from evidence_checkpoint import (
    all_ok, atomic_write_manifest, build_manifest, load_manifest,
    recover_from_backup, verify_manifest,
)

class EvidenceCheckpoint(unittest.TestCase):
    def setUp(self):
        self.td=tempfile.mkdtemp()
        self.primary=os.path.join(self.td,"primary")
        self.backup=os.path.join(self.td,"backup")
        os.makedirs(os.path.join(self.primary,"a"))
        os.makedirs(os.path.join(self.backup,"a"))
        files={"a/one.txt":b"one\n","a/two.bin":bytes(range(64))}
        for rel,data in files.items():
            for root in (self.primary,self.backup):
                p=os.path.join(root,rel); os.makedirs(os.path.dirname(p),exist_ok=True)
                with open(p,"wb") as f:f.write(data)
        self.paths=sorted(files)
    def tearDown(self):
        shutil.rmtree(self.td)

    def test_manifest_is_deterministic(self):
        a=build_manifest(self.primary,self.paths,"CP-1")
        b=build_manifest(self.primary,list(reversed(self.paths)),"CP-1")
        self.assertEqual(a,b)
        self.assertTrue(all_ok(verify_manifest(self.primary,a)))

    def test_corruption_detected_and_recovered(self):
        m=build_manifest(self.primary,self.paths,"CP-1")
        with open(os.path.join(self.primary,"a/one.txt"),"wb") as f:f.write(b"bad\n")
        before=verify_manifest(self.primary,m)
        self.assertIn("HASH_MISMATCH",{r["status"] for r in before})
        after=recover_from_backup(self.primary,self.backup,m)
        self.assertTrue(all_ok(after))

    def test_invalid_backup_refused(self):
        m=build_manifest(self.primary,self.paths,"CP-1")
        os.unlink(os.path.join(self.primary,"a/one.txt"))
        with open(os.path.join(self.backup,"a/one.txt"),"wb") as f:f.write(b"wrong")
        with self.assertRaisesRegex(RuntimeError,"E_BACKUP_INVALID"):
            recover_from_backup(self.primary,self.backup,m)

    def test_atomic_manifest_roundtrip(self):
        m=build_manifest(self.primary,self.paths,"CP-1")
        path=os.path.join(self.td,"checkpoint.json")
        atomic_write_manifest(path,m)
        self.assertEqual(m,load_manifest(path))

    def test_parent_checkpoint_binding_changes_hash(self):
        a=build_manifest(self.primary,self.paths,"CP-1")
        b=build_manifest(self.primary,self.paths,"CP-2",previous_checkpoint=a["checkpoint_hash"])
        self.assertNotEqual(a["checkpoint_hash"],b["checkpoint_hash"])
        self.assertEqual(a["checkpoint_hash"],b["previous_checkpoint"])

if __name__=="__main__":
    unittest.main()
