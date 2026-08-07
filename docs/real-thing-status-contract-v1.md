# Real-Thing Project Status Contract v1

## Authority

This contract adopts Threadkeeper’s Real-Thing Proof and Completion Status Protocol v0.1 from exact commit `a5bc55336c86097301b378d8654ac92a26ef81e5`.

## Two different questions

A project-status record answers two separate questions:

1. **Planning:** how much bounded work appears done, and how likely is the current finish line?
2. **Lifecycle proof:** what consequential state is directly supported by evidence from the required real environment?

Planning percentages and forecasts must never answer the lifecycle-proof question.

## Lifecycle stages

Every record contains all eight stages: designed, implemented, automated checks, independent review, merged, deployed, live behaviour, and human acceptance.

Each stage declares whether it is required. A required stage declares its required environment. A non-required stage uses `NOT_APPLICABLE` and records a rationale.

## Evidence results

- `PASS` — direct evidence exercised the declared required environment and supports the stage.
- `FAIL` — direct evidence exercised the declared required environment and disproves the stage.
- `INSUFFICIENT` — evidence is missing, proxy-only, environment-mismatched, or inconclusive.
- `NOT_APPLICABLE` — the project contract excludes the stage with an explicit rationale.

A proxy cannot pass or fail the real stage. A fixture can prove a validator; it cannot prove a deployed consumer. CI can prove checks; it cannot prove owner acceptance.

## Verified status

The verified status is derived from the evidence required up to the claimed stage. Any direct failure yields `failed`. Any missing, proxy-only, inconclusive, or environment-mismatched required stage yields `insufficient`.

`complete` requires direct passing evidence for every required stage. A planning estimate of 100% has no power to change this result.

## Consumer boundary

Adoption by this repository does not automatically update or validate consumers. Each consumer must adopt the control through its own collision-checked issue, exact branch, tests, review, and merge lane.
