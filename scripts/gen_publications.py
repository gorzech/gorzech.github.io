#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

BIB_PATH = Path("publications.bib")
PUB_QMD = Path("publications.qmd")


def parse_entries(text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] != "@":
            i += 1
            continue
        j = i + 1
        while j < n and (text[j].isalpha() or text[j] in "-_"):
            j += 1
        entry_type = text[i + 1 : j].strip().lower()
        while j < n and text[j].isspace():
            j += 1
        if j >= n or text[j] not in "{(":
            i = j
            continue
        open_ch = text[j]
        close_ch = "}" if open_ch == "{" else ")"
        j += 1
        k = j
        while k < n and text[k] not in ",\n":
            k += 1
        key = text[j:k].strip()
        if not key:
            i = k
            continue
        k += 1  # skip comma/newline
        depth = 1
        start = k
        while k < n and depth > 0:
            ch = text[k]
            if ch == open_ch:
                depth += 1
            elif ch == close_ch:
                depth -= 1
            k += 1
        body = text[start : k - 1]
        entries.append({"type": entry_type, "key": key, "body": body})
        i = k
    return entries


def is_selected(body: str) -> bool:
    return re.search(r'(?i)\bselected\s*=\s*[{"]\s*true\s*[}"]', body) is not None


def year_value(body: str) -> int:
    m = re.search(r'(?i)\byear\s*=\s*[{"]\s*(\d{4})\s*[}"]', body)
    return int(m.group(1)) if m else 0


def update_nocite_block(front_matter: str, keys: list[str]) -> str:
    lines = front_matter.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.match(r"^nocite\s*:", line):
            i += 1
            while i < len(lines) and (lines[i].startswith(" ") or lines[i].startswith("\\t")):
                i += 1
            continue
        out.append(line)
        i += 1

    if keys:
        block = ["nocite: |"] + [f"  @{k}" for k in keys]
    else:
        block = ['nocite: ""']

    result: list[str] = []
    inserted = False
    for line in out:
        result.append(line)
        if not inserted and re.match(r"^bibliography\s*:", line):
            result.extend(block)
            inserted = True
    if not inserted:
        result.extend(block)
    return "\n".join(result)


def validate_entries(entries: list[dict[str, str]]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not entries:
        errors.append("No BibTeX entries were parsed from publications.bib.")
        return errors, warnings

    seen: set[str] = set()
    duplicates: set[str] = set()
    for e in entries:
        key = e["key"]
        if key in seen:
            duplicates.add(key)
        seen.add(key)
        if is_selected(e["body"]) and not year_value(e["body"]):
            warnings.append(f"Selected entry missing year: {key}")
        if is_selected(e["body"]) and e["type"] != "article":
            warnings.append(f"Selected entry is not @article: {key}")

    if duplicates:
        errors.append(f"Duplicate BibTeX keys: {', '.join(sorted(duplicates))}")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate selected publications list.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate publications.bib and exit without modifying files.",
    )
    args = parser.parse_args()

    if not BIB_PATH.exists():
        raise SystemExit(f"Missing {BIB_PATH}")
    if not PUB_QMD.exists():
        raise SystemExit(f"Missing {PUB_QMD}")

    bib_text = BIB_PATH.read_text(encoding="utf-8")
    entries = parse_entries(bib_text)
    errors, warnings = validate_entries(entries)
    for w in warnings:
        print(f"Warning: {w}", file=sys.stderr)
    if errors:
        for e in errors:
            print(f"Error: {e}", file=sys.stderr)
        return 1
    if args.check:
        return 0

    selected_articles = [
        e for e in entries if e["type"] == "article" and is_selected(e["body"])
    ]
    selected_articles.sort(
        key=lambda e: (year_value(e["body"]), e["key"]), reverse=True
    )
    keys = [e["key"] for e in selected_articles]

    qmd_text = PUB_QMD.read_text(encoding="utf-8")
    if not qmd_text.startswith("---"):
        raise SystemExit("publications.qmd is missing YAML front matter")
    parts = qmd_text.split("---", 2)
    if len(parts) < 3:
        raise SystemExit("publications.qmd front matter is malformed")
    _, front, body = parts
    new_front = update_nocite_block(front.strip(), keys)
    new_text = f"---\n{new_front}\n---{body}"
    if new_text != qmd_text:
        PUB_QMD.write_text(new_text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
