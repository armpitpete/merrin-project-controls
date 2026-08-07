# Project Status v2 migration

Project Status v2 adds the required `lifecycle_status` object. Existing percentage and likelihood fields remain available but are explicitly planning-only.

Consumers must not silently rewrite historical v1 records. A consumer may migrate only through its own issue and exact branch, preserving the original planning evidence and adding direct lifecycle evidence where available. Missing evidence must remain `INSUFFICIENT`; it must not be inferred from percentages, repository activity, CI, or lifecycle classification.
