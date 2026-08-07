import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_project_status.py"
SPEC = importlib.util.spec_from_file_location("validate_project_status", MODULE_PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(module)


def stage(name, *, required=True, result="PASS", relationship="direct", observed=True):
    if not required:
        return {
            "stage": name,
            "required": False,
            "rationale": "Not required by this project contract.",
            "result": "NOT_APPLICABLE",
            "relationship": "not-applicable",
            "evidence": [],
            "limitations": [],
        }
    environment = f"real:{name}"
    item = {
        "stage": name,
        "required": True,
        "required_environment": environment,
        "result": result,
        "relationship": relationship,
        "evidence": [f"evidence:{name}"] if relationship != "missing" else [],
        "limitations": [],
    }
    if observed:
        item["observed_environment"] = environment
    return item


def record(claimed="complete", verified="complete"):
    return {
        "project": "owner/example",
        "finish_line": "Direct evidence for all required stages.",
        "percentage_complete": {
            "estimate": 100,
            "confidence": "high",
            "evidence": ["All planned tasks counted."],
            "remaining_work": [],
            "blockers": [],
        },
        "completion_likelihood": {
            "assessment": "very_likely",
            "confidence": "high",
            "reasons": ["Bounded work."],
        },
        "lifecycle_status": {
            "claimed": claimed,
            "verified": verified,
            "authority": "docs/status-contract.md",
            "stages": [stage(name) for name in module.STAGES],
            "limitations": [],
        },
        "next_bounded_action": "Maintain the completed control.",
    }


class EvidenceBoundStatusTests(unittest.TestCase):
    def test_direct_real_environment_can_verify_complete(self):
        self.assertEqual(module.validate(record())["lifecycle_status"]["verified"], "complete")

    def test_percentage_100_does_not_override_missing_deployment(self):
        data = record(verified="insufficient")
        data["lifecycle_status"]["stages"][5] = stage(
            "deployed", result="INSUFFICIENT", relationship="missing", observed=False
        )
        self.assertEqual(module.validate(data)["percentage_complete"]["estimate"], 100)
        self.assertEqual(data["lifecycle_status"]["verified"], "insufficient")

    def test_proxy_pass_is_rejected(self):
        data = record(verified="insufficient")
        data["lifecycle_status"]["stages"][6] = stage(
            "live-behaviour", result="PASS", relationship="proxy"
        )
        with self.assertRaisesRegex(module.StatusError, "requires direct evidence"):
            module.validate(data)

    def test_wrong_environment_is_rejected(self):
        data = record(verified="insufficient")
        data["lifecycle_status"]["stages"][4]["observed_environment"] = "proxy:merge"
        with self.assertRaisesRegex(module.StatusError, "must exercise required environment"):
            module.validate(data)

    def test_missing_human_acceptance_blocks_complete(self):
        data = record(verified="insufficient")
        data["lifecycle_status"]["stages"][7] = stage(
            "human-acceptance", result="INSUFFICIENT", relationship="missing", observed=False
        )
        self.assertEqual(module.validate(data)["lifecycle_status"]["verified"], "insufficient")

    def test_duplicate_stage_is_rejected(self):
        data = record()
        data["lifecycle_status"]["stages"][7]["stage"] = "designed"
        with self.assertRaisesRegex(module.StatusError, "duplicate lifecycle stage"):
            module.validate(data)


if __name__ == "__main__":
    unittest.main()
