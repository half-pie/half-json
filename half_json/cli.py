from __future__ import annotations

import argparse
import sys

from half_json.core import JSONFixer


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="jsonfixer",
        description="Fix invalid / truncated JSON.",
    )
    parser.add_argument(
        "infile",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="input file (default: stdin)",
    )
    parser.add_argument(
        "outfile",
        nargs="?",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="output file (default: stdout)",
    )
    parser.add_argument("--strict", dest="strict", action="store_true", default=True)
    parser.add_argument("--no-strict", dest="strict", action="store_false")
    parser.add_argument("--js-style", action="store_true", default=False)
    parser.add_argument(
        "--single", action="store_true", default=False, help="treat entire input as one JSON value"
    )
    args = parser.parse_args(argv)

    fixer = JSONFixer(js_style=args.js_style)
    total = 0
    hit = 0

    if args.single:
        text = args.infile.read().strip()
        if text:
            result = fixer.fix(text, strict=args.strict)
            args.outfile.write(result.line + "\n")
    else:
        for line in args.infile:
            line = line.strip()
            if not line:
                continue
            total += 1
            result = fixer.fix(line, strict=args.strict)
            if result.success:
                args.outfile.write(result.line + "\n")
                if not result.origin:
                    hit += 1
            else:
                print(result, file=sys.stderr)
        if total:
            print(f"total is {total} and hit {hit} --> ratio:{hit * 1.0 / total}", file=sys.stderr)


# Backward-compatible entry point (same signature as old main.py:fixjson)
def fixjson() -> None:
    main()


if __name__ == "__main__":
    main()
