import hashlib
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "import_verified_binary", ROOT / "scripts" / "import_verified_binary.py"
)
subject = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(subject)


def git(repository: Path, *args: str) -> str:
    process = subprocess.run(
        ["git", *args],
        cwd=repository,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return process.stdout.strip()


class VerifiedBinaryIngestionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.repository = self.root / "repository"
        self.repository.mkdir()
        git(self.repository, "init", "-b", "main")
        git(self.repository, "config", "user.name", "Test User")
        git(self.repository, "config", "user.email", "test@example.invalid")
        (self.repository / "README.md").write_text("# Fixture\n", encoding="utf-8")
        git(self.repository, "add", "README.md")
        git(self.repository, "commit", "-m", "Initial fixture")
        self.source = self.root / "source.bin"
        self.source.write_bytes(b"\x00fixture\xffbinary\x10")
        self.digest = hashlib.sha256(self.source.read_bytes()).hexdigest()

    def tearDown(self):
        self.temporary.cleanup()

    def ingest(self, **overrides):
        arguments = {
            "repository": self.repository,
            "branch": "main",
            "source": self.source,
            "destination_path": "archive/source.bin",
            "expected_sha256": self.digest,
            "expected_size": self.source.stat().st_size,
            "commit_message": "Import verified source binary",
            "push": False,
        }
        arguments.update(overrides)
        return subject.ingest_binary(**arguments)

    def test_success_commits_exactly_one_verified_file(self):
        before = git(self.repository, "rev-parse", "HEAD")
        result = self.ingest()
        self.assertNotEqual(result.commit, before)
        self.assertEqual(result.sha256, self.digest)
        self.assertEqual(result.destination, "archive/source.bin")
        self.assertFalse(result.pushed)
        self.assertEqual((self.repository / result.destination).read_bytes(), self.source.read_bytes())
        self.assertEqual(
            git(self.repository, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"),
            "archive/source.bin",
        )
        self.assertEqual(git(self.repository, "status", "--porcelain"), "")

    def test_checksum_mismatch_changes_nothing(self):
        before = git(self.repository, "rev-parse", "HEAD")
        with self.assertRaisesRegex(subject.IngestionError, "SHA-256"):
            self.ingest(expected_sha256="0" * 64)
        self.assertEqual(git(self.repository, "rev-parse", "HEAD"), before)
        self.assertFalse((self.repository / "archive" / "source.bin").exists())
        self.assertEqual(git(self.repository, "status", "--porcelain"), "")

    def test_size_mismatch_changes_nothing(self):
        with self.assertRaisesRegex(subject.IngestionError, "source size"):
            self.ingest(expected_size=self.source.stat().st_size + 1)
        self.assertFalse((self.repository / "archive" / "source.bin").exists())
        self.assertEqual(git(self.repository, "status", "--porcelain"), "")

    def test_existing_destination_is_never_overwritten(self):
        destination = self.repository / "archive" / "source.bin"
        destination.parent.mkdir()
        destination.write_bytes(b"existing")
        git(self.repository, "add", "archive/source.bin")
        git(self.repository, "commit", "-m", "Add existing file")
        with self.assertRaisesRegex(subject.IngestionError, "never overwrites"):
            self.ingest()
        self.assertEqual(destination.read_bytes(), b"existing")
        self.assertEqual(git(self.repository, "status", "--porcelain"), "")

    def test_dirty_repository_is_rejected_before_copy(self):
        (self.repository / "README.md").write_text("dirty\n", encoding="utf-8")
        with self.assertRaisesRegex(subject.IngestionError, "not clean"):
            self.ingest()
        self.assertFalse((self.repository / "archive" / "source.bin").exists())

    def test_parent_traversal_is_rejected(self):
        with self.assertRaisesRegex(subject.IngestionError, "parent"):
            self.ingest(destination_path="../outside.bin")
        self.assertFalse((self.root / "outside.bin").exists())


if __name__ == "__main__":
    unittest.main()
