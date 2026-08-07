import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_project_status_example", ROOT / "scripts" / "validate_project_status.py"
)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(module)


class ProjectStatusExampleTests(unittest.TestCase):
    def test_example_is_valid_and_does_not_claim_deployment(self):
        record = json.loads((ROOT / "examples" / "project-status-pass.json").read_text())
        validated = module.validate(record)
        self.assertEqual(validated["lifecycle_status"]["verified"], "merged")
        self.assertEqual(validated["percentage_complete"]["estimate"], 100)
        self.assertEqual(validated["lifecycle_status"]["stages"][5]["result"], "NOT_APPLICABLE")


if __name__ == "__main__":
    unittest.main()
