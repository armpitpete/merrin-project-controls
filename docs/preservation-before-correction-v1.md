# Preservation Before Correction (PBC) v1.0

Status: adopted as the default development-repair rule on 16 October 2026, subject to each repository's authority and protected merge gates.

## Purpose

Prevent repair-induced regressions, opportunistic redesign and endless fix-on-fix loops. The goal is the smallest evidenced correction that preserves accepted behaviour.

## Mandatory repair gate

1. **Accepted baseline:** Identify the last accepted commit, version or artefact. Freeze it; work in an isolated candidate. List behaviours and files that must remain unchanged.
2. **Demonstrated problem:** Identify a reproduced failing behaviour and evidence, or explicitly classify it as a hypothesis. Where live reproduction is unsafe, use bounded, non-destructive evidence.
3. **Minimum sufficient change:** Specify the one fault, permitted change surface and exit criterion. No unrelated refactoring, feature additions, visual redesign or new safeguards in a repair lane.
4. **Before/after evidence:** When safe and practical, demonstrate the failure before repair. Verify the target condition afterward and rerun all directly affected accepted/regression checks. Record actual outputs and exact candidate identity.
5. **Regression response:** If accepted behaviour regresses, stop the candidate and restore the *isolated* candidate to its accepted baseline before authorising a new bounded attempt. Never silently revert a production deployment, erase work or bypass release authority.
6. **Outcome honesty:** Report exact changed files, tests run, tests not run, regressions introduced and PASS / REPAIR / BLOCKED / NOT TESTED. One passing unit test never substitutes for the full agreed acceptance gate.
7. **Stop at acceptance:** Once the complete authorised gate passes, stop. Any later enhancement, cleanup or speculative risk reduction requires a separate authorised lane.

## Minimal evidence record

Add to the existing issue, pull request or acceptance record, rather than creating another reporting system:

- Baseline and protected behaviour:
- Demonstrated fault and permitted scope:
- Before/after tests, regressions and result:
- Decision and stop point:

## Exceptions and precedence

A necessary security or safety mitigation, or an intentional change to accepted behaviour, may exceed the minimal change only with an explicit justification, scoped authority and regression evidence. Project-specific stronger safety, privacy, provenance, review and release rules continue to apply.

No historical PASS is automatically invalidated. No currently active project, release or repository is silently migrated by adopting this shared contract.

## Adoption

For local development, an ancestor `AGENTS.md` can state the rule for tools that honour those instructions. For GitHub projects, incorporate the rule in that repository's own `AGENTS.md` and existing PR review/acceptance process through its normal protected change process.

Writing this shared contract does **not** itself prove that every assistant, repository or automation enforces it.
