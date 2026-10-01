import json
import time
import pytest
from agent_failure_taxonomy.cli import main, atomic_write

def test_run_completes_on_fixture(fixture_dir, tmp_path, capsys):
    start = time.perf_counter()
    output = tmp_path / "results.json"
    assert main(["run", "--input", str(fixture_dir), "--results", str(output)]) == 0
    assert main(["report", "--results", str(output), "--format", "md"]) == 0
    assert time.perf_counter() - start < 5
    assert "Records: 200" in capsys.readouterr().out

def test_empty_input_renders_without_traceback(tmp_path, capsys):
    source = tmp_path / "empty"
    source.mkdir()
    output = tmp_path / "results.json"
    assert main(["run", "--input", str(source), "--results", str(output)]) == 0
    assert main(["report", "--results", str(output)]) == 0
    assert "Records: 0" in capsys.readouterr().out

@pytest.mark.parametrize("suffix,content,line", [("jsonl", '# header\n{broken', 2), ("json", '[\n{broken', 2), ("csv", 'bad,csv', 1), ("yaml", 'bad: [', 1)])
def test_malformed_input_named_error(tmp_path, capsys, suffix, content, line):
    p = tmp_path / ("bad." + suffix)
    p.write_text(content)
    assert main(["run", "--input", str(tmp_path)]) == 2
    error = capsys.readouterr().err
    assert "ParseError" in error and p.name in error and f"line {line}" in error
    assert "Traceback" not in error

def test_determinism_byte_identical(fixture_dir, tmp_path):
    out = tmp_path / "results.json"
    args = ["run", "--input", str(fixture_dir), "--results", str(out)]
    assert main(args) == 0
    first = out.read_bytes()
    assert main(args) == 0
    assert out.read_bytes() == first
    for fmt in ("md", "json"):
        report = tmp_path / fmt
        args = ["report", "--results", str(out), "--format", fmt, "--out", str(report)]
        main(args)
        first = report.read_bytes()
        main(args)
        assert first == report.read_bytes()

def test_cli_smoke_all_subcommands(fixture_dir, tmp_path, capsys):
    assert main(["fixtures", "--out", str(tmp_path / "new")]) == 0
    for cmd in ("classify", "audit"):
        assert main([cmd, "--input", str(fixture_dir)]) == 0
    for cmd in ("fixtures", "run", "report", "classify", "audit"):
        with pytest.raises(SystemExit) as exc:
            main([cmd, "--help"])
        assert exc.value.code == 0
    assert chr(0x2014) not in capsys.readouterr().out

def test_missing_input_named_error(tmp_path, capsys):
    assert main(["run", "--input", str(tmp_path / "missing")]) == 2
    assert "MissingInput" in capsys.readouterr().err

def test_schema_drift_named_error(tmp_path, capsys):
    (tmp_path / "input.jsonl").write_text('{"id":"x"}\n')
    assert main(["run", "--input", str(tmp_path)]) == 2
    error = capsys.readouterr().err
    assert "SchemaError" in error and "synthetic" in error and "line 1" in error

def test_report_write_failure_no_partial(fixture_dir, tmp_path, capsys):
    output = tmp_path / "results.json"
    main(["run", "--input", str(fixture_dir), "--results", str(output)])
    destination = tmp_path / "directory"
    destination.mkdir()
    before = sorted(p.name for p in tmp_path.iterdir())
    assert main(["report", "--results", str(output), "--out", str(destination)]) == 2
    assert sorted(p.name for p in tmp_path.iterdir()) == before
    assert "FileError" in capsys.readouterr().err

def test_corrupt_results_named_error(tmp_path, capsys):
    p = tmp_path / "result.json"
    p.write_text('{}')
    assert main(["report", "--results", str(p)]) == 2
    assert "ResultError" in capsys.readouterr().err
