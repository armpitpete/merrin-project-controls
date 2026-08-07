import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SchemaContractTextTests(unittest.TestCase):
    def test_planning_fields_disclaim_lifecycle_completion(self):
        schema = json.loads((ROOT / "schemas" / "project-status.schema.json").read_text())
        percentage = schema["properties"]["percentage_complete"]["description"]
        likelihood = schema["properties"]["completion_likelihood"]["description"]
        self.assertIn("does not establish lifecycle completion", percentage)
        self.assertIn("does not establish lifecycle completion", likelihood)
        self.assertIn("lifecycle_status", schema["required"])


if __name__ == "__main__":
    unittest.main()
