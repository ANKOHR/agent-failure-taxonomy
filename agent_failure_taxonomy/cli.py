"""Local file CLI. No network, model calls, or hidden classification estimates."""
import argparse
from datetime import date
import json
import os
from pathlib import Path
import tempfile
from .core import AS_OF, CATEGORIES, InputError, analyze
from .fixtures import generate
from .report import render

def read_input(directory):
    directory = Path(directory)
    if not directory.is_dir():
        raise InputError(f"MissingInput: {directory}: use aft fixtures --out demo or supply an input directory")
    records = []
    for path in sorted(directory.iterdir()):
        if path.name in ("expectations.json", "README.md"):
            continue
        if path.suffix.lower() in (".csv", ".yaml", ".yml"):
            raise InputError(f"ParseError: {path}: line 1: unsupported format; use JSON or JSONL")
        if path.suffix.lower() not in (".json", ".jsonl"):
            continue
        text = path.read_text(encoding="utf-8")
        try:
            if path.suffix.lower() == ".jsonl":
                for line, content in enumerate(text.splitlines(), 1):
                    if not content.strip() or content.lstrip().startswith("#"):
                        continue
                    try:
                        record = json.loads(content)
                    except json.JSONDecodeError as exc:
                        raise InputError(f"ParseError: {path}: line {line}: {exc.msg}") from exc
                    from .core import validate
                    try:
                        validate(record, f"{path}: line {line}", read_input.as_of)
                    except InputError:
                        raise
                    records.append(record)
            else:
                data = json.loads(text)
                if not isinstance(data, list):
                    raise InputError(f"SchemaError: {path}: line 1: field root: expected record array")
                from .core import validate
                for index, record in enumerate(data, 1):
                    validate(record, f"{path}: line 1: array item {index}", read_input.as_of)
                records.extend(data)
        except json.JSONDecodeError as exc:
            raise InputError(f"ParseError: {path}: line {exc.lineno}: {exc.msg}") from exc
    return records

read_input.as_of = AS_OF

def atomic_write(path, text):
    path = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(text)
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()

def main(argv=None):
    parser = argparse.ArgumentParser(prog="aft", description="Classify explicit failure signals using deterministic rules. Examples: aft fixtures --out demo; aft run --input demo; aft report --format md")
    subs = parser.add_subparsers(dest="command", required=True)
    p = subs.add_parser("fixtures", help="Generate 200 labelled synthetic observations", description="Example: aft fixtures --out demo")
    p.add_argument("--out", required=True)
    for name, help_text in (("run", "Classify records and persist computed results"), ("classify", "Print per-record classifications"), ("audit", "Compare computed categories with supplied ground truth")):
        p = subs.add_parser(name, help=help_text, description=f"{help_text}. Example: aft {name} --input demo")
        p.add_argument("--input", required=True)
        p.add_argument("--as-of", type=date.fromisoformat, default=AS_OF, help="Explicit date cutoff, default 2026-09-30; no wall-clock dependence")
        if name == "run":
            p.add_argument("--results", default=".aft-results.json")
    p = subs.add_parser("report", help="Render computed results with provenance", description="Example: aft report --format md --out report.md")
    p.add_argument("--format", choices=("md", "json"), default="md")
    p.add_argument("--results", default=".aft-results.json")
    p.add_argument("--out")
    args = parser.parse_args(argv)
    try:
        if args.command == "fixtures":
            generate(args.out)
            print("Generated 200 SYNTHETIC records with planted ground truth.")
        elif args.command in ("run", "classify", "audit"):
            read_input.as_of = args.as_of
            result = analyze(read_input(args.input), args.as_of)
            if args.command == "run":
                atomic_write(args.results, render(result, "json"))
                print(f"Computed {result['total']} records. Synthetic: {result['provenance']['synthetic']}; real user-supplied: {result['provenance']['real_user_supplied']}. Results: {args.results}")
            else:
                print(render(result, "json"), end="")
        else:
            try:
                result = json.loads(Path(args.results).read_text(encoding="utf-8"))
                output = render(result, args.format)
            except (json.JSONDecodeError, KeyError, TypeError, AttributeError, ValueError, IndexError) as exc:
                raise InputError(f"ResultError: {args.results}: invalid result schema; rerun aft run") from exc
            if args.out:
                atomic_write(args.out, output)
            else:
                print(output, end="")
        return 0
    except (InputError, OSError, UnicodeError) as exc:
        message = str(exc).replace(chr(0x2014), "-")
        print(f"{message if isinstance(exc, InputError) else 'FileError: ' + message}", file=__import__('sys').stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
