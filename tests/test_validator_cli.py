import subprocess
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ValidatorCliTests(unittest.TestCase):
    def test_pass_example_cli(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_project_status.py"), str(ROOT / "examples" / "project-status-pass.json")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("valid project status", result.stdout)


if __name__ == "__main__":
    unittest.main()
