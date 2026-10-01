import pytest
from agent_failure_taxonomy.core import InputError, analyze

def test_fixture_ground_truth_matches_hand_computed(records):
    r = analyze(records)
    assert r["total"] == 200 and r["failures"] == 150
    assert r["counts"] == {"success": 50, "timeout": 25, "permission_denied": 25, "tool_error": 25, "invalid_output": 25, "policy_violation": 25, "unknown_failure": 25}
    assert r["validation"]["correct"] == 200

@pytest.mark.parametrize("field,value", [("amount", -1), ("amount", True), ("amount", 1.5), ("date", "2099-01-01"), ("signal", []), ("synthetic", "true"), ("description", "x" * 100001), ("unexpected", 0)], ids=["negative", "boolean", "float", "future", "signal-type", "provenance-type", "extreme-length", "unknown-field"])
def test_rejects_adversarial_values(records, field, value):
    record = {**records[0], field: value}
    with pytest.raises(InputError, match="SchemaError"):
        analyze([record])

def test_duplicate_ids(records):
    with pytest.raises(InputError, match="duplicate"):
        analyze([records[0], records[0]])

def test_handles_unicode_and_long_inputs(records):
    r = {**records[0], "id": "漢字-🙂", "description": "C:\\Users\\henry " + "é" * 90000}
    assert analyze([r])["records"][0]["id"] == "漢字-🙂"

def test_corrupted_ground_truth_changes_audit(records):
    records[0]["expected_category"] = "timeout"
    assert analyze(records)["validation"]["correct"] == 199
    records[1]["status"] = "failure"
    records[1]["signal"] = "timeout"
    r = analyze(records)
    assert r["counts"]["timeout"] == 26
    assert r["validation"]["false_positives"] == 1

def test_tiny_real_input(records):
    sample = [{**r, "synthetic": False} for r in records[:5]]
    assert analyze(sample)["provenance"] == {"synthetic": 0, "real_user_supplied": 5}
