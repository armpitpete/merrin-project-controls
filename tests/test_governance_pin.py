from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = "a5bc55336c86097301b378d8654ac92a26ef81e5"


class GovernancePinTests(unittest.TestCase):
    def test_write_rules_pin_canonical_release(self):
        rules = (ROOT / ".github" / "REPOSITORY_WRITE_RULES.md").read_text()
        self.assertIn(CANONICAL, rules)
        self.assertIn("must not weaken", rules)
        self.assertIn("INSUFFICIENT", rules)


if __name__ == "__main__":
    unittest.main()
