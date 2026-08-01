#!/usr/bin/env python3
"""Safely add one checksum-bound binary file to an existing Git branch."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


class IngestionError(RuntimeError):
    """A safe, user-readable ingestion failure."""


@dataclass(frozen=True)
class IngestionResult:
    repository: str
    branch: str
    destination: str
    sha256: str
    size: int
    commit: str
    pushed: bool


def run_git(repository: Path, *args: str) -> str:
    process = subprocess.run(
        ["git", *args],
        cwd=repository,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if process.returncode != 0:
        message = process.stderr.strip() or process.stdout.strip() or "git command failed"
        raise IngestionError(message)
    return process.stdout.strip()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_expected_sha256(value: str) -> str:
    normalised = value.strip().lower()
    if len(normalised) != 64 or any(character not in "0123456789abcdef" for character in normalised):
        raise IngestionError("expected SHA-256 must contain exactly 64 hexadecimal characters")
    return normalised


def resolve_destination(repository: Path, relative_path: str) -> tuple[Path, str]:
    candidate = PurePosixPath(relative_path.replace("\\", "/"))
    if candidate.is_absolute() or not candidate.parts:
        raise IngestionError("destination must be a non-empty repository-relative path")
    if any(part in {"", ".", ".."} for part in candidate.parts):
        raise IngestionError("destination must not contain empty, current or parent path segments")
    if candidate.parts[0].lower() == ".git":
        raise IngestionError("destination must not be inside .git")
    destination = repository.joinpath(*candidate.parts).resolve()
    try:
        destination.relative_to(repository)
    except ValueError as exc:
        raise IngestionError("destination escapes the repository") from exc
    return destination, candidate.as_posix()


def require_clean_repository(repository: Path, branch: str) -> str:
    if not repository.is_dir():
        raise IngestionError("repository path does not exist or is not a directory")
    root = Path(run_git(repository, "rev-parse", "--show-toplevel")).resolve()
    if root != repository:
        raise IngestionError("repository path must be the exact Git worktree root")
    current_branch = run_git(repository, "branch", "--show-current")
    if current_branch != branch:
        raise IngestionError(f"current branch is {current_branch!r}, expected {branch!r}")
    if run_git(repository, "status", "--porcelain=v1", "--untracked-files=all"):
        raise IngestionError("repository worktree is not clean")
    return run_git(repository, "rev-parse", "HEAD")


def require_push_preflight(repository: Path, branch: str, local_head: str) -> None:
    run_git(repository, "fetch", "--quiet", "origin", branch)
    remote_head = run_git(repository, "rev-parse", f"refs/remotes/origin/{branch}")
    if remote_head != local_head:
        raise IngestionError("remote branch moved or local branch is not synchronized")


def staged_paths(repository: Path) -> list[str]:
    raw = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "-z"],
        cwd=repository,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if raw.returncode != 0:
        raise IngestionError(raw.stderr.decode("utf-8", errors="replace").strip())
    return [item.decode("utf-8") for item in raw.stdout.split(b"\0") if item]


def committed_paths(repository: Path) -> list[str]:
    raw = subprocess.run(
        ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "-z", "HEAD"],
        cwd=repository,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if raw.returncode != 0:
        raise IngestionError(raw.stderr.decode("utf-8", errors="replace").strip())
    return [item.decode("utf-8") for item in raw.stdout.split(b"\0") if item]


def ingest_binary(
    *,
    repository: Path,
    branch: str,
    source: Path,
    destination_path: str,
    expected_sha256: str,
    expected_size: int | None,
    commit_message: str,
    push: bool,
) -> IngestionResult:
    repository = repository.expanduser().resolve()
    source = source.expanduser().resolve()
    expected_sha256 = validate_expected_sha256(expected_sha256)
    local_head = require_clean_repository(repository, branch)

    if not source.is_file():
        raise IngestionError("source file does not exist or is not a regular file")
    source_size = source.stat().st_size
    if expected_size is not None and source_size != expected_size:
        raise IngestionError(f"source size is {source_size}, expected {expected_size}")
    actual_sha256 = file_sha256(source)
    if actual_sha256 != expected_sha256:
        raise IngestionError("source SHA-256 does not match the expected value")

    destination, git_path = resolve_destination(repository, destination_path)
    if destination.exists():
        raise IngestionError("destination already exists; verified ingestion never overwrites")
    if push:
        require_push_preflight(repository, branch, local_head)

    destination.parent.mkdir(parents=True, exist_ok=True)
    committed = False
    try:
        shutil.copyfile(source, destination)
        if destination.stat().st_size != source_size or file_sha256(destination) != expected_sha256:
            raise IngestionError("copied destination failed size or checksum verification")

        run_git(repository, "add", "--", git_path)
        if staged_paths(repository) != [git_path]:
            raise IngestionError("staged scope is not exactly the requested destination")
        run_git(repository, "diff", "--cached", "--check")
        run_git(repository, "commit", "-m", commit_message, "--", git_path)
        committed = True

        commit = run_git(repository, "rev-parse", "HEAD")
        if committed_paths(repository) != [git_path]:
            raise IngestionError("created commit contains files outside the requested destination")
        if file_sha256(destination) != expected_sha256:
            raise IngestionError("committed file no longer matches the expected checksum")
        if run_git(repository, "status", "--porcelain=v1", "--untracked-files=all"):
            raise IngestionError("repository is not clean after the commit")

        if push:
            run_git(repository, "push", "--porcelain", "origin", f"HEAD:refs/heads/{branch}")

        return IngestionResult(
            repository=str(repository),
            branch=branch,
            destination=git_path,
            sha256=expected_sha256,
            size=source_size,
            commit=commit,
            pushed=push,
        )
    except Exception:
        if not committed:
            subprocess.run(
                ["git", "restore", "--staged", "--", git_path],
                cwd=repository,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
            if destination.exists():
                destination.unlink()
            parent = destination.parent
            while parent != repository:
                try:
                    parent.rmdir()
                except OSError:
                    break
                parent = parent.parent
        raise


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify and commit exactly one binary file without overwriting existing content."
    )
    parser.add_argument("--repository", required=True, type=Path)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--sha256", required=True)
    parser.add_argument("--size", type=int)
    parser.add_argument("--commit-message", required=True)
    parser.add_argument("--push", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        result = ingest_binary(
            repository=args.repository,
            branch=args.branch,
            source=args.source,
            destination_path=args.destination,
            expected_sha256=args.sha256,
            expected_size=args.size,
            commit_message=args.commit_message,
            push=args.push,
        )
    except IngestionError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result.__dict__, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
