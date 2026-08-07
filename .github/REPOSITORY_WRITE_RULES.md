# Repository Write Rules — Real-Thing Proof adoption v0.1

## Canonical authority

This repository adopts Threadkeeper’s **Real-Thing Proof and Completion Status Protocol v0.1** from exact release:

```text
repository: armpitpete/threadkeeper
commit: a5bc55336c86097301b378d8654ac92a26ef81e5
protocol: docs/REAL_THING_PROOF_AND_COMPLETION_STATUS_V0_1.md
```

Local rules may strengthen that protocol. They must not weaken it.

## Governing rule

> Never test a proxy when the claim concerns the real thing. Never allow `complete` to absorb implementation, deployment, live verification and human acceptance into one vague word.

## Project-control boundary

Merrin Project Controls defines schemas, templates and reusable controls. Passing these controls proves only that a submitted record satisfies the declared contract. It does not prove the external project condition described by the record.

Therefore:

- percentage estimates and completion likelihood are planning information only;
- repository activity, lifecycle classification, generated reports and CI cannot establish product completion;
- a shared-control version does not prove consumer integration;
- consumer integration does not prove deployment or live behaviour;
- automated validation does not prove owner acceptance;
- proxy-only, missing or inconclusive required evidence is `INSUFFICIENT`;
- `complete` is valid only when every required lifecycle stage has direct passing evidence in its declared environment.

## Required lifecycle states

Consequential status records preserve these separate stages:

1. designed;
2. implemented;
3. automated-checks;
4. independent-review;
5. merged;
6. deployed;
7. live-behaviour;
8. human-acceptance.

A stage may be not applicable only with an explicit rationale. At least one stage must be required.

## Direct proof in this repository

- **Designed** — exact accepted control contract or issue.
- **Implemented** — exact commit containing the shared control.
- **Automated checks** — exact-head workflow result.
- **Independent review** — review bound to the exact candidate head.
- **Merged** — exact default-branch commit.
- **Deployed** — exact release or distribution receipt where the control is distributed.
- **Live behaviour** — direct observation of the actual claimed consumer or protected-head enforcement path.
- **Human acceptance** — explicit owner acceptance where the project contract requires it.

Fixtures and examples may prove validator behaviour. They cannot substitute for a real consumer, deployment, protected branch, live runtime or owner decision.

## Protected boundaries

This adoption does not authorise mass consumer mutation, project-template changes outside a separate lane, lifecycle reclassification, deployment, historical record rewriting, disclosure of private evidence, merge without exact-head checks, or portfolio-wide completion claims.

## Adoption record

- local issue: `armpitpete/merrin-project-controls#4`;
- rollout issue: `armpitpete/threadkeeper#123`;
- baseline: `09891a09975235ae99b2b3430adeaa6cb81f5378`;
- canonical release: `a5bc55336c86097301b378d8654ac92a26ef81e5`.
