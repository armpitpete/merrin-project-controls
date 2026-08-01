# Merrin Project Controls

Shared, versioned controls for evidence, review, acceptance and plain-language project status across Merrin repositories.

## Purpose

This repository prevents each project from independently rebuilding the same safeguards. It provides small controls that protect genuine risk boundaries without turning process into the work.

## Foundation v0.1

| Control | Version | Purpose |
|---|---:|---|
| Acceptance Record | 1.0 | Records exactly what was reviewed, accepted, corrected and left blocked. |
| Exact-Head Protection | 1.0 | Stops review or merge work when the local or remote branch has moved. |
| Phrase Contract | 1.0 | Checks required and forbidden wording with useful failure evidence. |
| Project Status | 1.0 | Separates percentage complete from likelihood of completion. |
| Plain-Language Project Summary | 1.0 | Explains a project to an ordinary reader before exposing technical detail. |

Versions are recorded in [`control-versions.json`](control-versions.json).

## Repository structure

```text
docs/       Versioned control contracts
templates/  Reusable human-facing records
scripts/    Executable controls
schemas/    Machine-readable validation
examples/   Passing and deliberately failing fixtures
tests/      Permanent behavioural tests
```

## Use

### Exact-head check

PowerShell:

```powershell
./scripts/protected-head.ps1 -ExpectedCommit <full-commit-sha>
```

Bash:

```bash
./scripts/protected-head.sh <full-commit-sha>
```

Both scripts require:

- the current `HEAD` to equal the expected commit;
- a clean working tree;
- the current remote branch head to equal the expected commit.

Use `-SkipRemoteCheck` or `--skip-remote-check` only where no remote branch exists yet.

### Phrase contract check

```bash
python scripts/check_phrase_contract.py examples/contracts/pass.json --root examples/fixture
```

The checker has no third-party dependencies. A contract can require phrases, forbid phrases, match case-sensitively or case-insensitively, and target one or more file globs.

### Tests

```bash
python -m unittest discover -s tests -v
```

The test suite proves that:

1. the positive fixture passes;
2. the negative fixture is rejected for the expected reasons.

## Adoption rule

Adopt one control in one active repository first. Confirm that it reduces risk without adding disproportionate work. Expand only after that proof.

## Boundaries

This repository does **not** centralise:

- story canon or manuscript-specific rules;
- deployment secrets;
- repository-specific wording;
- controls used by only one project;
- every workflow from every repository.

Shared controls must remain stable, understandable and smaller than the work they protect.
