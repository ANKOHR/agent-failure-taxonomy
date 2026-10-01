"""Pure, deterministic rules over explicit observations, not inferred causes."""
from collections import Counter
from datetime import date

CATEGORIES = ("success", "timeout", "permission_denied", "tool_error", "invalid_output", "policy_violation", "unknown_failure")
FIELDS = {"id", "synthetic", "date", "status", "signal", "description", "amount", "expected_category"}
SIGNALS = {"timeout", "permission_denied", "tool_error", "invalid_output", "policy_violation", "none"}
AS_OF = date(2026, 9, 30)

class InputError(ValueError):
    """Named, actionable input failure."""

def validate(record, location="input", as_of=AS_OF):
    def fail(field, reason):
        raise InputError(f"SchemaError: {location}: field {field}: {reason}")
    if not isinstance(record, dict):
        fail("record", "must be an object")
    for field in sorted(set(record) - FIELDS):
        fail(field, "unknown field")
    for field in ("id", "synthetic", "date", "status", "signal", "description"):
        if field not in record:
            fail(field, "required")
    for field in ("id", "description"):
        if not isinstance(record[field], str) or not record[field] or len(record[field]) > 100000:
            fail(field, "must be a nonempty string of at most 100000 characters")
        if chr(0x2014) in record[field]:
            fail(field, "em dash is not allowed; use a hyphen")
    if type(record["synthetic"]) is not bool:
        fail("synthetic", "must be boolean")
    try:
        observed = date.fromisoformat(record["date"])
    except (ValueError, TypeError):
        fail("date", "must be an ISO calendar date")
    if observed > as_of:
        fail("date", f"future date after explicit as-of {as_of}")
    if record["status"] not in ("success", "failure"):
        fail("status", "must be success or failure")
    if not isinstance(record["signal"], str) or record["signal"] not in SIGNALS:
        fail("signal", "unsupported observed signal")
    if record["status"] == "success" and record["signal"] != "none":
        fail("signal", "success must use none")
    if "amount" in record and (type(record["amount"]) is not int or record["amount"] < 0):
        fail("amount", "must be nonnegative integer minor units; no savings are inferred")
    if "expected_category" in record and record["expected_category"] not in CATEGORIES:
        fail("expected_category", "unsupported label")
    return record

def classify(record):
    if record["status"] == "success":
        return "success"
    return record["signal"] if record["signal"] != "none" else "unknown_failure"

def analyze(records, as_of=AS_OF):
    seen = set()
    results = []
    for index, record in enumerate(records, 1):
        validate(record, f"record {index}", as_of)
        if record["id"] in seen:
            raise InputError(f"SchemaError: record {index}: field id: duplicate {record['id']!r}")
        seen.add(record["id"])
        results.append({"id": record["id"], "category": classify(record), "synthetic": record["synthetic"], **({"expected_category": record["expected_category"]} if "expected_category" in record else {})})
    results.sort(key=lambda r: r["id"])
    counts = Counter(r["category"] for r in results)
    labelled = [r for r in results if "expected_category" in r]
    return {"as_of": str(as_of), "total": len(results), "failures": len(results) - counts["success"], "counts": {c: counts[c] for c in CATEGORIES}, "provenance": {"synthetic": sum(r["synthetic"] for r in results), "real_user_supplied": sum(not r["synthetic"] for r in results)}, "validation": {"labelled": len(labelled), "correct": sum(r["category"] == r["expected_category"] for r in labelled), "false_positives": sum(r["category"] != "success" and r["expected_category"] == "success" for r in labelled), "missed_failures": sum(r["category"] == "success" and r["expected_category"] != "success" for r in labelled)}, "savings": "Unmeasured: no baseline supplied; time or money saved is not reported. Hypothetical savings are not computed.", "records": results}
