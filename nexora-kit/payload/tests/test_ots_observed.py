import json
import os
import sys
import unittest

from _common import ROOT  # noqa: E402
from ots_observed import OTSError, parse_detached, verify_detached

VECTOR = os.path.join(ROOT, "testvectors", "ots-observed.json")

class OTSObserved(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(VECTOR, encoding="utf-8") as f:
            cls.v = json.load(f)
        cls.proof = bytes.fromhex(cls.v["proof_hex"])
        cls.message = bytes.fromhex(cls.v["message_hex"])

    def test_upstream_proof_executes_end_to_end(self):
        out = verify_detached(self.proof, self.message)
        self.assertEqual(688, out["proof_bytes"])
        self.assertEqual(688, out["consumed_bytes"])
        self.assertEqual(self.v["message_sha256"], out["file_digest_hex"])
        self.assertEqual(1, len(out["attestations"]))
        att = out["attestations"][0]
        self.assertEqual("bitcoin-block-header", att["kind"])
        self.assertEqual(358391, att["height"])
        self.assertEqual(self.v["expected_attestation_message_hex"], att["message_hex"])

    def test_truncation_fails_closed(self):
        with self.assertRaisesRegex(OTSError, "E_OTS_TRUNCATED"):
            parse_detached(self.proof[:-1])

    def test_trailing_bytes_fail_closed(self):
        with self.assertRaisesRegex(OTSError, "E_OTS_TRAILING"):
            parse_detached(self.proof + b"\x00")

    def test_unknown_operation_fails_closed(self):
        bad = bytearray(self.proof)
        # First timestamp item begins after 31-byte magic + version + hash tag + 32-byte digest.
        bad[65] = 0x7E
        with self.assertRaisesRegex(OTSError, "E_OTS_UNKNOWN_OP_7e"):
            parse_detached(bytes(bad))

    def test_message_binding_is_checked(self):
        with self.assertRaisesRegex(OTSError, "E_OTS_FILE_DIGEST_MISMATCH"):
            verify_detached(self.proof, self.message + b"x")

if __name__ == "__main__":
    unittest.main()
