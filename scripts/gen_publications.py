#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from publications.bib import enrich_entries, is_selected, parse_entries, validate_entries
from publications.render import format_entry, render_sections, sort_entries

BIB_PATH = Path("publications.bib")
PUB_QMD = Path("publications.qmd")
PUB_FULL_QMD = Path("publications-full.qmd")
GENERATED_DIR = Path("generated")
SELECTED_OUT = GENERATED_DIR / "publications-selected.md"
FULL_OUT = GENERATED_DIR / "publications-full.md"


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

    enriched = enrich_entries(entries)
    for item in enriched:
        item["formatted"] = format_entry(item)

    selected_entries = sort_entries([item for item in enriched if is_selected(item["body"])])
    all_entries = sort_entries(enriched)

    selected_block = render_sections(selected_entries)
    full_block = render_sections(all_entries)

    GENERATED_DIR.mkdir(parents=True, exist_ok=True)

    if not SELECTED_OUT.exists() or SELECTED_OUT.read_text(encoding="utf-8") != selected_block:
        SELECTED_OUT.write_text(selected_block, encoding="utf-8")

    if not FULL_OUT.exists() or FULL_OUT.read_text(encoding="utf-8") != full_block:
        FULL_OUT.write_text(full_block, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
