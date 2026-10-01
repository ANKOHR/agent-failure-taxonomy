"""Reports expose observed counts and provenance without estimated benefits."""
import json

def banner(result):
    p = result["provenance"]
    return f"Data provenance: {p['synthetic']} synthetic fixture records; {p['real_user_supplied']} real user-supplied records (declared by input, not independently verified)."

def render(result, fmt):
    if fmt == "json":
        return json.dumps({"banner": banner(result), **result}, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    lines = ["# Agent Failure Taxonomy", "", banner(result), "", f"As-of: {result['as_of']}", f"Records: {result['total']}", f"Failures: {result['failures']}", "", "| Category | Count |", "| --- | ---: |"]
    lines += [f"| {k} | {v} |" for k, v in result["counts"].items()]
    lines += ["", "Ground truth comparison (only supplied labels):"]
    lines += [f"- {k}: {v}" for k, v in result["validation"].items()]
    lines += ["", result["savings"], "", "Per-record trace:", ""]
    lines += [f"- {json.dumps(r['id'], ensure_ascii=False)}: {r['category']} ({'synthetic' if r['synthetic'] else 'real user-supplied'})" for r in result["records"]]
    return "\n".join(lines) + "\n"
