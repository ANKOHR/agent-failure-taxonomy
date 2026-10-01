# Local acceptance evidence

Measured on 2026-10-01 using Python 3.12.10 on Windows, CPU only. Three installed aft CLI processes (fixtures, run, report) completed in 0.659 seconds. This is measured local synthetic runtime, not a prediction of real workload runtime.

Synthetic acceptance: 200 observations, 50 successes, 150 failures, 25 in each of six failure categories. All 200 supplied labels match, zero false positives, zero missed failures. Per-record output traces every category. The expectations file is not consulted by run. Mutating labels changes audit figures; mutating observations changes category totals.

The pytest suite verifies malformed files, empty input, schema drift, future dates, invalid amounts, duplicates, extreme strings, Unicode, write failure cleanup, and deterministic output. Real-world accuracy, savings and usage remain unmeasured. Verdict is pending real use.

Build improvement applied after evidence: long parameter-generated pytest IDs exceeded Windows filename limits. Explicit short IDs make adversarial tests portable without reducing input lengths.
