#!/usr/bin/env python3
"""Validate required and forbidden phrases in repository files."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Failure:
    rule_id: str
    file: str
    message: str


def _as_list(value: object, field: str, rule_id: str) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return value
    raise ValueError(f"Rule {rule_id!r}: {field} must be a string or list of strings.")


def _load_contract(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Contract not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("Contract root must be a JSON object.")
    if data.get("version") != 1:
        raise ValueError("Contract version must be 1.")
    rules = data.get("rules")
    if not isinstance(rules, list) or not rules:
        raise ValueError("Contract must contain a non-empty rules list.")
    return data


def _matched_files(root: Path, patterns: Iterable[str]) -> list[Path]:
    matched: set[Path] = set()
    for pattern in patterns:
        if Path(pattern).is_absolute():
            raise ValueError(f"Absolute file patterns are not allowed: {pattern}")
        matched.update(path for path in root.glob(pattern) if path.is_file())
    return sorted(matched)


def validate_contract(contract_path: Path, root: Path) -> list[Failure]:
    contract = _load_contract(contract_path)
    failures: list[Failure] = []
    seen_ids: set[str] = set()

    for index, raw_rule in enumerate(contract["rules"], start=1):
        if not isinstance(raw_rule, dict):
            raise ValueError(f"Rule {index} must be a JSON object.")

        rule_id = raw_rule.get("id")
        if not isinstance(rule_id, str) or not rule_id.strip():
            raise ValueError(f"Rule {index} requires a non-empty string id.")
        if rule_id in seen_ids:
            raise ValueError(f"Duplicate rule id: {rule_id}")
        seen_ids.add(rule_id)

        patterns = _as_list(raw_rule.get("files"), "files", rule_id)
        if not patterns:
            raise ValueError(f"Rule {rule_id!r}: files must not be empty.")

        required = _as_list(raw_rule.get("required_phrases"), "required_phrases", rule_id)
        forbidden = _as_list(raw_rule.get("forbidden_phrases"), "forbidden_phrases", rule_id)
        case_sensitive = raw_rule.get("case_sensitive", False)
        if not isinstance(case_sensitive, bool):
            raise ValueError(f"Rule {rule_id!r}: case_sensitive must be Boolean.")

        matched = _matched_files(root, patterns)
        if not matched:
            failures.append(
                Failure(rule_id, ", ".join(patterns), "No files matched the configured pattern.")
            )
            continue

        for file_path in matched:
            try:
                text = file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                failures.append(
                    Failure(rule_id, str(file_path.relative_to(root)), "File is not valid UTF-8.")
                )
                continue

            haystack = text if case_sensitive else text.casefold()
            display_path = str(file_path.relative_to(root))

            for phrase in required:
                needle = phrase if case_sensitive else phrase.casefold()
                if needle not in haystack:
                    failures.append(
                        Failure(rule_id, display_path, f"Required phrase missing: {phrase!r}")
                    )

            for phrase in forbidden:
                needle = phrase if case_sensitive else phrase.casefold()
                if needle in haystack:
                    failures.append(
                        Failure(rule_id, display_path, f"Forbidden phrase present: {phrase!r}")
                    )

    return failures


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path, help="Path to the phrase-contract JSON file.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Root directory used to resolve file patterns. Defaults to the current directory.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()

    try:
        failures = validate_contract(args.contract.resolve(), root)
    except ValueError as exc:
        print(f"CONTRACT ERROR: {exc}", file=sys.stderr)
        return 2

    if failures:
        print(f"Phrase contract failed with {len(failures)} problem(s):", file=sys.stderr)
        for failure in failures:
            print(
                f"- [{failure.rule_id}] {failure.file}: {failure.message}",
                file=sys.stderr,
            )
        return 1

    print(f"Phrase contract passed: {args.contract}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
