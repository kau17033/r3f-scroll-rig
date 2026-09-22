import unittest
from _common import ROOT  # noqa: F401
from bitcoin_header_recon import compact_target, parse_header

HEADER_HEX = (
    "02000000b96394585a281b7e5f438fd1c9ed492645a1fd61cb3802040000000000000000"
    "007ee445d23ad061af4a36b809501fab1ac4f2d7e7a739817dd0cbb7ec661b8a"
    "1e376755f58616186272def6"
)

class BitcoinReconUnit(unittest.TestCase):
    def test_known_header_fields(self):
        h=parse_header(bytes.fromhex(HEADER_HEX))
        self.assertEqual("000000000000000003e892881a8cdcdc117c06d444057c98b6f04a9ee75a2319",h["hash"])
        self.assertEqual("0000000000000000040238cb61fda1452649edc9d18f435f7e1b285a589463b9",h["previousblockhash"])
        self.assertEqual("007ee445d23ad061af4a36b809501fab1ac4f2d7e7a739817dd0cbb7ec661b8a",h["merkle_root_internal"])
        self.assertEqual(1432827678,h["timestamp"])
        self.assertEqual(0x181686f5,h["bits"])
        self.assertEqual(0xf62d2786,h["nonce"])

    def test_compact_target(self):
        self.assertGreater(compact_target(0x181686f5),0)
        self.assertGreater(compact_target(0x1d00ffff),compact_target(0x181686f5))

if __name__=="__main__":
    unittest.main()
