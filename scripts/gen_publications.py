#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from publications.bib import enrich_entries, is_selected, parse_entries, validate_entries
from publications.render import format_entry, render_sections, replace_block, sort_entries

BIB_PATH = Path("publications.bib")
PUB_QMD = Path("publications.qmd")
PUB_FULL_QMD = Path("publications-full.qmd")


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

    pub_text = PUB_QMD.read_text(encoding="utf-8")
    new_pub_text = replace_block(pub_text, selected_block)
    if new_pub_text != pub_text:
        PUB_QMD.write_text(new_pub_text, encoding="utf-8")

    pub_full_text = PUB_FULL_QMD.read_text(encoding="utf-8")
    new_pub_full_text = replace_block(pub_full_text, full_block)
    if new_pub_full_text != pub_full_text:
        PUB_FULL_QMD.write_text(new_pub_full_text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
