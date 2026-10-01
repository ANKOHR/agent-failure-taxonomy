import json
from agent_failure_taxonomy.fixtures import generate
from agent_failure_taxonomy.core import analyze

def test_fixtures_labelled_synthetic(fixture_dir, records):
    assert len(records) == 200 and all(r["synthetic"] is True for r in records)
    assert (fixture_dir / "records.jsonl").read_text().startswith("# SYNTHETIC")
    assert json.loads((fixture_dir / "expectations.json").read_text())["synthetic"] is True
    assert (fixture_dir / "README.md").read_text().startswith("<!-- SYNTHETIC")

def test_expectations_independent(fixture_dir, records):
    expected = json.loads((fixture_dir / "expectations.json").read_text())
    result = analyze(records)
    for key in ("total", "failures", "counts"):
        assert result[key] == expected[key]
    for key in ("labelled", "correct", "false_positives", "missed_failures"):
        assert result["validation"][key] == expected[key]

def test_fixture_generation_deterministic(tmp_path):
    generate(tmp_path / "a")
    generate(tmp_path / "b")
    for p in (tmp_path / "a").iterdir():
        assert p.read_bytes() == (tmp_path / "b" / p.name).read_bytes()
