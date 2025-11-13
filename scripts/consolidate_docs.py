#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Consolidate ALL markdown files in the repository into a single file at the root.

Behavior:
- Recursively finds all *.md files under the repo root.
- Excludes the output file itself and common transient folders (e.g., .venv, node_modules, __pycache__, .git).
- Includes .github markdown by default so all docs and templates are captured.
- Writes each file preceded by a level-2 heading and the relative path for traceability.
- Optionally delete all other markdown files after consolidation by setting env DELETE_OTHERS=1.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "CONSOLIDATED_DOCUMENTATION.md"

EXCLUDE_DIRS = {
    ".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache",
}

def is_excluded(path: Path) -> bool:
    parts = set(p.name for p in path.resolve().parts)
    return any(name in EXCLUDE_DIRS for name in path.parts)

def find_markdown_files() -> list[Path]:
    md_files: list[Path] = []
    for base, dirs, files in os.walk(ROOT):
        # prune excluded directories in-place for efficiency
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        base_path = Path(base)
        for f in files:
            if not f.lower().endswith(".md"):
                continue
            fp = base_path / f
            if fp.resolve() == OUTPUT.resolve():
                continue
            md_files.append(fp)
    # Stable order: by directory then filename
    md_files.sort(key=lambda p: str(p).lower())
    return md_files

def consolidate(delete_others: bool = False) -> None:
    files = find_markdown_files()
    included = 0

    with OUTPUT.open("w", encoding="utf-8") as out:
        out.write("# Consolidated Documentation\n\n")
        out.write("This file aggregates all markdown content in the repository at generation time.\n\n")
        out.write("---\n\n")

        for fp in files:
            rel = fp.relative_to(ROOT)
            out.write(f"## {rel.as_posix()}\n\n")
            try:
                txt = fp.read_text(encoding="utf-8", errors="ignore")
            except Exception as e:
                txt = f"(Error reading {rel}: {e})\n"
            out.write(txt)
            if not txt.endswith("\n"):
                out.write("\n")
            out.write("\n---\n\n")
            included += 1

        out.write(f"\n\nGenerated from {included} files.\n")

    print(f"✅ Wrote {OUTPUT} with {included} files")

    if delete_others:
        deleted = 0
        for fp in files:
            try:
                fp.unlink()
                deleted += 1
            except Exception as e:
                print(f"⚠️  Could not delete {fp}: {e}")
        print(f"🧹 Deleted {deleted} markdown files (kept {OUTPUT.name})")

if __name__ == "__main__":
    delete = os.getenv("DELETE_OTHERS", "0") in {"1", "true", "True"}
    consolidate(delete_others=delete)
