# Verified Binary Ingestion v1

## Purpose

Add one exact local binary payload to one existing Git branch without using the account owner as an unverified manual transport layer.

The launcher verifies the source before copying, refuses overwrite, commits only the named destination and can push only after proving that the local and remote branch heads agree.

## Command

Run from any directory with Python 3 and Git available:

```powershell
python scripts/import_verified_binary.py `
  --repository "I:\ORDER\GitHub\example-project" `
  --branch "agent/source-import" `
  --source "I:\ORDER\Incoming\Source_Package.zip" `
  --destination "archive/source-package/Source_Package.zip" `
  --sha256 "<64-character-sha256>" `
  --size 123456 `
  --commit-message "Import verified source package" `
  --push
```

Omit `--push` to create and verify the local commit without sending it to GitHub.

## Mandatory safeguards

The launcher:

1. requires the exact Git worktree root;
2. requires the named current branch;
3. requires a completely clean worktree;
4. verifies source size when supplied;
5. verifies the full SHA-256 before copying;
6. rejects absolute paths, parent traversal and `.git` destinations;
7. refuses to overwrite any existing destination;
8. copies and re-verifies the destination;
9. stages exactly one named path;
10. commits exactly that path;
11. verifies the resulting commit scope and checksum;
12. requires local and remote heads to match before an optional push;
13. never force-pushes.

Before a commit is created, a failure removes only the newly created destination and returns the repository to its clean state. After a commit is created, later failures are reported without rewriting history.

## Intended use

Use this for exact source archives, document candidates, PDF proofs and other binary payloads already governed by a recorded path, size and SHA-256. It does not decide whether a file belongs in Git, replace Git Large File Storage, or authorise a manuscript or production candidate.
