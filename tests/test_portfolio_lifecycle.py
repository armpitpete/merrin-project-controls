import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PortfolioLifecycleTests(unittest.TestCase):
    def test_all_64_repositories_are_classified_once(self):
        document = json.loads((ROOT / "portfolio-lifecycle.json").read_text(encoding="utf-8"))
        classifications = document["classifications"]
        self.assertEqual(set(classifications), {"active", "parked", "completed", "archived"})

        repositories = [
            repository
            for category in ("active", "parked", "completed", "archived")
            for repository in classifications[category]
        ]
        self.assertEqual(len(repositories), 64)
        self.assertEqual(len(set(repositories)), 64)
        self.assertTrue(all(repository.startswith("armpitpete/") for repository in repositories))

        expected_counts = document["counts"]
        self.assertEqual(expected_counts["total"], 64)
        for category in ("active", "parked", "completed", "archived"):
            self.assertEqual(expected_counts[category], len(classifications[category]))

    def test_pending_archive_state_is_explicit(self):
        document = json.loads((ROOT / "portfolio-lifecycle.json").read_text(encoding="utf-8"))
        archived = document["classifications"]["archived"]
        self.assertEqual(
            document["archive_setting_pending"],
            ["armpitpete/project-control-disposable-proof-20260717"],
        )
        self.assertEqual(archived, document["archive_setting_pending"])
        self.assertEqual(document["actual_github_archived_count"], 0)


if __name__ == "__main__":
    unittest.main()
