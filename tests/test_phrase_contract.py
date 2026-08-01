from __future__ import annotations

import importlib.util
import unittest
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPOSITORY_ROOT / "scripts" / "check_phrase_contract.py"

spec = importlib.util.spec_from_file_location("check_phrase_contract", SCRIPT_PATH)
assert spec and spec.loader
checker = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = checker
spec.loader.exec_module(checker)


class PhraseContractTests(unittest.TestCase):
    def test_positive_fixture_passes(self) -> None:
        failures = checker.validate_contract(
            REPOSITORY_ROOT / "examples" / "contracts" / "pass.json",
            REPOSITORY_ROOT / "examples" / "fixture",
        )
        self.assertEqual([], failures)

    def test_negative_fixture_is_rejected(self) -> None:
        failures = checker.validate_contract(
            REPOSITORY_ROOT / "examples" / "contracts" / "fail.json",
            REPOSITORY_ROOT / "examples" / "fixture",
        )
        messages = [failure.message for failure in failures]

        self.assertEqual(4, len(failures))
        self.assertTrue(any("Required phrase missing" in message for message in messages))
        self.assertEqual(
            2,
            sum("Forbidden phrase present" in message for message in messages),
        )


if __name__ == "__main__":
    unittest.main()
