import json
from agent_failure_taxonomy.core import analyze
from agent_failure_taxonomy.report import render

def test_report_matches_ground_truth_exact(records):
    r = json.loads(render(analyze(records), "json"))
    assert r["total"] == 200 and sum(r["counts"].values()) == 200
    assert r["failures"] == 150 and r["validation"]["correct"] == 200
    assert len(r["records"]) == 200

def test_report_zero_false_positives(records):
    assert json.loads(render(analyze(records), "json"))["validation"]["false_positives"] == 0

def test_report_carries_provenance_banner(records):
    for fmt in ("md", "json"):
        s = render(analyze(records), fmt)
        assert "Data provenance: 200 synthetic fixture records; 0 real user-supplied records" in s

def test_hypothetical_figures_labelled(records):
    for fmt in ("md", "json"):
        s = render(analyze(records), fmt)
        assert "Unmeasured" in s and "Hypothetical savings are not computed" in s

def test_no_em_dashes_in_outputs(records):
    for fmt in ("md", "json"):
        assert chr(0x2014) not in render(analyze(records), fmt)
