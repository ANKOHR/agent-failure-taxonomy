"""Synthetic planted data; fixed construction, no random seed required."""
import json
from pathlib import Path
from .core import CATEGORIES

# Independently hand-counted: 50 successes and 25 cases in each failure class.
EXPECTATIONS = {"synthetic": True, "total": 200, "failures": 150, "counts": {"success": 50, "timeout": 25, "permission_denied": 25, "tool_error": 25, "invalid_output": 25, "policy_violation": 25, "unknown_failure": 25}, "labelled": 200, "correct": 200, "false_positives": 0, "missed_failures": 0}

def generate(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    records = []
    for category in CATEGORIES:
        for _ in range(50 if category == "success" else 25):
            records.append({"id": f"case-{len(records)+1:03}", "synthetic": True, "date": "2026-09-30", "status": "success" if category == "success" else "failure", "signal": "none" if category in ("success", "unknown_failure") else category, "description": f"Synthetic explicit observation: {category}", "expected_category": category})
    (out / "records.jsonl").write_text("# SYNTHETIC fixture: planted labels, no real operational data\n" + "".join(json.dumps(r, sort_keys=True) + "\n" for r in records), encoding="utf-8")
    (out / "expectations.json").write_text(json.dumps(EXPECTATIONS, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "README.md").write_text("<!-- SYNTHETIC fixture -->\nSynthetic: true. All 200 records are planted examples.\n", encoding="utf-8")
