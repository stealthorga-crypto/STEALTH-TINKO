#!/usr/bin/env python3
"""
sanitize_json.py

Trim any trailing garbage after the first complete top-level JSON object in a file.
Creates a .bak backup before writing sanitized content.

Usage:
  python sanitize_json.py <file1> [<file2> ...]
"""
from __future__ import annotations
import sys
import json
from pathlib import Path


def find_first_complete_object(text: str) -> str:
    # Find the first '{' then scan until matching '}' at depth 0
    start = text.find('{')
    if start == -1:
        raise ValueError("No JSON object start '{' found")

    depth = 0
    in_string = False
    escape = False
    end_index = None

    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
                continue
            if ch == '\\':
                escape = True
            elif ch == '"':
                in_string = False
            continue
        else:
            if ch == '"':
                in_string = True
                continue
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    end_index = i + 1
                    break

    if end_index is None:
        raise ValueError("Did not find matching closing '}' for top-level object")

    return text[start:end_index]


def sanitize_file(path: Path) -> None:
    original = path.read_text(encoding='utf-8', errors='replace')
    trimmed = find_first_complete_object(original)
    # Validate
    obj = json.loads(trimmed)

    # Backup
    backup = path.with_suffix(path.suffix + '.bak')
    backup.write_text(original, encoding='utf-8')

    # Write pretty JSON
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding='utf-8')


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: python sanitize_json.py <file1> [<file2> ...]", file=sys.stderr)
        return 2
    code = 0
    for arg in argv[1:]:
        p = Path(arg)
        try:
            sanitize_file(p)
            print(f"Sanitized: {p}")
        except Exception as e:
            print(f"ERROR: {p}: {e}", file=sys.stderr)
            code = 1
    return code


if __name__ == '__main__':
    raise SystemExit(main(sys.argv))
