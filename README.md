# Agent Failure Taxonomy

A CPU-only, dependency-free Python CLI that classifies explicit agent failure observations. It makes no network or model calls. Hypothesis: deterministic classification of supplied evidence can provide a trustworthy operational tool. Synthetic acceptance demonstrates rule correctness, not real-world accuracy.

## Quickstart

Python 3.10 or later. From the repository:

```powershell
python -m pip install -e . --no-build-isolation --no-index --disable-pip-version-check
python -m pytest -q
aft fixtures --out demo
aft run --input demo
aft report --format md
```

If the Python Scripts directory is absent from PATH, use `python -m agent_failure_taxonomy.cli` in place of `aft`, or add that directory to PATH. A five-record hand-written synthetic example is in `examples/tiny`; run it with `aft run --input examples/tiny`.

The fixture contains 200 synthetic records, including 50 successes and 25 cases in each of six failure categories. The acceptance target is exact ground truth reconciliation and an end-to-end demo under five seconds. Tests time the fixture workflow; local evidence is in EVIDENCE.md.

## Input reference

Input is a directory of UTF-8 JSON arrays or JSONL files. JSONL allows blank lines and header comments starting with `#`. Files are read in filename order. `expectations.json` and `README.md` are reserved fixture metadata and are excluded. CSV and YAML are explicitly rejected with a named format error. Other extensions are ignored. No files are recursively traversed.

```json
[{"id":"henry-001","synthetic":false,"date":"2026-09-30","status":"failure","signal":"timeout","description":"Tool exceeded its configured deadline"}]
```

Required fields: `id`, `synthetic`, `date`, `status`, `signal`, `description`. IDs must be unique across files. ID and description must be nonempty strings up to 100000 characters. Unicode and Windows paths are supported. Em dashes are rejected to keep outputs within the build constraint. `synthetic` must be a boolean. Set it to false only for actual observations entered by Henry; provenance is a declaration, not verified ownership.

Dates are ISO calendar dates and cannot exceed the explicit `--as-of` cutoff (default 2026-09-30). This fixed cutoff preserves reproducibility; pass a later date when recording later observations. Status is `success` or `failure`. Signal is `none`, `timeout`, `permission_denied`, `tool_error`, `invalid_output`, or `policy_violation`. Successful observations require `none`. Failures with `none` become `unknown_failure`. Each record has exactly one category. Description is trace context, never used for keyword guessing.

Optional `expected_category` supplies hand-checked ground truth from the seven categories. It does not influence classification. Optional `amount` is a nonnegative integer in minor units, validated but not aggregated because currency and baseline are absent. Booleans, floats, negative values, unknown fields, duplicate IDs, and conflicting success signals are rejected. No invalid record is silently dropped.

## Commands

- `aft fixtures --out demo`: generate deterministic labelled synthetic data and independent expectations.
- `aft run --input demo --results result.json`: compute and atomically persist a result. Add `--as-of 2026-10-01` for a different explicit date cutoff.
- `aft report --format md --results result.json --out report.md`: render a traceable report; use `--format json` for machine-readable output. Default results path is `.aft-results.json`.
- `aft classify --input demo`: print categories and their complete computed report as JSON.
- `aft audit --input demo`: print comparison with supplied labels as JSON. Correct counts include all category matches; false positives mean labelled successes classified as failures; missed failures mean labelled failures classified as successes. Wrong failure subtypes reduce correct counts.

Every command has `--help` with an example. Errors return code 2 without a traceback. Parse errors identify filename and line; schema errors identify field and source location (JSON arrays identify item index and line 1). Duplicate errors identify global record index and ID. Missing input errors suggest how to generate fixtures. File write errors leave no partial output and preserve any existing destination. Unsupported result schemas produce ResultError. Reports require a result produced by `run`.

## Architecture

```text
JSON / JSONL directory -> CLI validation -> pure core rules -> computed result
fixture generator -> planted records + independent expectations
computed result -> report renderer -> Markdown / JSON with provenance
```

Only the CLI and fixture generator perform file I/O. Core accepts explicit inputs and an explicit date cutoff. There is no randomness, so no seed is needed. Sorted filenames, record IDs, and JSON keys make repeated runs byte-identical on identical inputs and settings.

## Honesty boundary

All counts are computed from supplied records. Categories describe explicit signals, not discovered root causes. Label comparison is measured only on records carrying supplied ground truth. Zero labelled records does not imply verified accuracy. No savings or time estimates are generated: reports state that savings are unmeasured and hypothetical savings are not computed. Runtime evidence measures this machine and this synthetic workflow only. Real operational performance remains unmeasured.

## Fixture labelling

Every generated record has `synthetic: true`. JSONL has a SYNTHETIC header comment; expectations JSON has a synthetic field; fixture Markdown has a synthetic header comment and visible label. JSON does not permit header comments. All reports give separate synthetic and real user-supplied counts and a provenance banner. Expectations are independently specified, never read by the classifier. A corrupt supplied ground truth changes audit figures, while an altered observed signal changes classification counts.

## Real trial and improvement hook

Henry can enter real observations by hand in the schema above, retain the input privately, and add hand-checked expected labels. Do not commit real trial data. After two weeks from the first real use, measure exact category accuracy on the hand-checked sample: incorrect classifications / labelled records. Record sample size, dates, usage count, observed error rate, and top failure cause in a private trial log. If error exceeds 10 percent or the tool was not used, fix the top cause and repeat measurement or kill with a recorded reason. No accuracy percentage is claimed for a sample of zero.

Verdict is pending that evidence window. Record expand for demonstrated daily use or revenue, integrate for heavy overlap with a sibling project, commercialise for demonstrated buyer willingness to pay as-is, maintain for portfolio evidence otherwise, or kill for no use or failed acceptance. Do not infer a verdict from synthetic correctness. See VERDICT.md.
