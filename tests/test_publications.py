from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from publications.render import format_authors, format_entry, sort_entries  # noqa: E402


class TestFormatAuthors(unittest.TestCase):
    def test_normalizes_last_first_to_first_last(self) -> None:
        value = "Orzechowski, Grzegorz and Mikkola, Aki"
        self.assertEqual(format_authors(value), "Grzegorz Orzechowski and Aki Mikkola")

    def test_keeps_first_last_names(self) -> None:
        value = "Grzegorz Orzechowski and Aki Mikkola"
        self.assertEqual(format_authors(value), "Grzegorz Orzechowski and Aki Mikkola")

    def test_handles_mixed_author_styles(self) -> None:
        value = "Han, Seongji and Grzegorz Orzechowski and Kim, Jin-Gyun"
        expected = "Seongji Han, Grzegorz Orzechowski, and Jin-Gyun Kim"
        self.assertEqual(format_authors(value), expected)

    def test_decodes_latex_accents_in_authors(self) -> None:
        value = r"Tang, Yixuan and Prokop, Ale{\v s} and Orzechowski, Grzegorz"
        expected = "Yixuan Tang, Aleš Prokop, and Grzegorz Orzechowski"
        self.assertEqual(format_authors(value), expected)


class TestSortEntries(unittest.TestCase):
    def test_sorts_by_year_desc_then_key_desc(self) -> None:
        entries = [
            {"key": "a", "year": "2024"},
            {"key": "c", "year": "2025"},
            {"key": "b", "year": "2025"},
            {"key": "d", "year": ""},
        ]
        sorted_keys = [entry["key"] for entry in sort_entries(entries)]
        self.assertEqual(sorted_keys, ["c", "b", "a", "d"])


class TestFormatEntry(unittest.TestCase):
    def test_strips_braces_from_title(self) -> None:
        entry = {
            "fields": {
                "author": "Orzechowski, Grzegorz",
                "title": "{A} Study on {MBD}",
                "journal": "Test Journal",
                "year": "2025",
            }
        }
        rendered = format_entry(entry)
        self.assertIn("\"A Study on MBD.\"", rendered)
        self.assertNotIn("{", rendered)
        self.assertNotIn("}", rendered)

    def test_decodes_latex_accents_in_title(self) -> None:
        entry = {
            "fields": {
                "author": "Orzechowski, Grzegorz",
                "title": r"Model of Ale{\v s} system",
                "journal": "Test Journal",
                "year": "2025",
            }
        }
        rendered = format_entry(entry)
        self.assertIn("\"Model of Aleš system.\"", rendered)


if __name__ == "__main__":
    unittest.main()
