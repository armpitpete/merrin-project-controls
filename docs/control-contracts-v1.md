# Shared Control Contracts v1.0

## Acceptance Record Contract v1.0

## Purpose

Record an evidence-backed decision at a genuine review boundary.

## Required fields

An acceptance record must identify:

1. the repository or artefact;
2. the bounded scope reviewed;
3. the exact commit or immutable candidate;
4. the evidence actually checked;
5. the decision: `ACCEPT`, `CORRECTIONS REQUIRED`, or `REJECT`;
6. named corrections with exact locations where applicable;
7. work that remains blocked;
8. the reviewer and decision date.

## Rules

- Acceptance applies only to the named scope and exact candidate.
- Unchecked claims must not be presented as evidence.
- Built, tested, accepted and proven in real use are distinct states.
- A moved commit invalidates the review unless the new candidate is reviewed.
- Safe mechanical follow-through may continue after acceptance when already authorised.

Use [`templates/acceptance-record.md`](../templates/acceptance-record.md).

---

## Exact-Head Protection Contract v1.0

## Purpose

Prevent review, approval or merge actions from applying to code that changed after inspection.

## Required checks

Before a protected action:

1. resolve the current full commit SHA;
2. compare it with the full expected SHA;
3. require a clean working tree;
4. identify the current branch;
5. fetch and compare the corresponding remote branch head unless explicitly skipped.

## Failure behaviour

The control must stop with a non-zero exit status and name the failed condition. It must never silently accept a prefix match or a moved remote head.

Implementations:

- [`scripts/protected-head.ps1`](../scripts/protected-head.ps1)
- [`scripts/protected-head.sh`](../scripts/protected-head.sh)

---

## Phrase Contract v1.0

## Purpose

Protect important wording without relying on a reviewer to rediscover every requirement.

## Contract format

A UTF-8 JSON document with:

- `version`: must be `1`;
- `rules`: one or more rule objects.

Each rule contains:

- `id`: unique readable identifier;
- `files`: one path or glob, or a list of paths or globs;
- `required_phrases`: phrases that must appear;
- `forbidden_phrases`: phrases that must not appear;
- `case_sensitive`: optional Boolean, default `false`.

## Behaviour

- Every file pattern must match at least one file.
- Every required phrase must appear in every matched file.
- No forbidden phrase may appear in a matched file.
- Failures must identify the rule, file and phrase.
- The checker returns `0` only when every rule passes.

Implementation: [`scripts/check_phrase_contract.py`](../scripts/check_phrase_contract.py).

---

## Project Status Contract v1.0

## Purpose

Report progress without confusing work already completed with the chance of reaching a credible ending.

## Required judgements

### Percentage complete

A bounded estimate of completed work against a defined finish line.

It must include:

- the percentage or range;
- confidence;
- evidence;
- remaining work;
- blockers;
- the next bounded action.

### Likelihood of completion

A separate judgement using evidence such as:

- a clear finish line;
- bounded remaining work;
- recent meaningful activity;
- a defined next action;
- active blockers;
- repository or production health;
- previous delivery consistency.

Use `low`, `medium` or `high` confidence. Avoid false precision.

Machine-readable records may use [`schemas/project-status.schema.json`](../schemas/project-status.schema.json). Human reports may use [`templates/project-status.md`](../templates/project-status.md).

---

## Plain-Language Project Summary Contract v1.0

## Purpose

Explain a project to a non-technical reader before presenting repository detail.

## The first view must answer

1. What is this project?
2. Who is it for?
3. What works now?
4. What remains?
5. How complete is it?
6. How likely is it to be completed?
7. What is the next meaningful action?

## Rules

- Lead with ordinary language, not branches, frameworks or commit counts.
- Separate completion percentage from likelihood of completion.
- Give plain-language reasons for both judgements.
- Distinguish demonstrated behaviour from intended behaviour.
- Put technical evidence in an optional deeper layer.
- Do not use marketing claims as proof.

Use [`templates/project-summary.md`](../templates/project-summary.md).
