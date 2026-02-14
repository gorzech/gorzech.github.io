from __future__ import annotations

import re
import unicodedata


AUTO_START = "<!-- AUTO-GENERATED:START -->"
AUTO_END = "<!-- AUTO-GENERATED:END -->"


ACCENT_MARKS = {
    "`": "\u0300",   # grave
    "'": "\u0301",   # acute
    "^": "\u0302",   # circumflex
    "~": "\u0303",   # tilde
    "=": "\u0304",   # macron
    "u": "\u0306",   # breve
    ".": "\u0307",   # dot above
    '"': "\u0308",   # diaeresis
    "r": "\u030A",   # ring above
    "H": "\u030B",   # double acute
    "v": "\u030C",   # caron
    "c": "\u0327",   # cedilla
    "k": "\u0328",   # ogonek
}


def decode_latex_accents(value: str) -> str:
    text = value

    # Handle accent commands such as \v{s}, \v s, \'a, and variants with spaces.
    pattern = re.compile(r"\\([`'^~=.urHvck\"])\s*(?:\{\s*([A-Za-z])\s*\}|([A-Za-z]))")

    def replace_accent(match: re.Match[str]) -> str:
        accent_cmd = match.group(1)
        letter = match.group(2) or match.group(3) or ""
        combining = ACCENT_MARKS.get(accent_cmd)
        if not combining or not letter:
            return match.group(0)
        return unicodedata.normalize("NFC", letter + combining)

    text = pattern.sub(replace_accent, text)
    text = text.replace(r"\ss", "ß")
    text = text.replace("{", "").replace("}", "")
    return text


def clean_title(value: str) -> str:
    text = decode_latex_accents(value)
    return text.strip()


def format_authors(value: str) -> str:
    if not value:
        return ""
    raw_parts = [part.strip() for part in value.replace("\n", " ").split(" and ") if part.strip()]

    def normalize_author(author: str) -> str:
        compact = decode_latex_accents(" ".join(author.split()))
        if "," in compact:
            chunks = [chunk.strip() for chunk in compact.split(",") if chunk.strip()]
            if len(chunks) == 2:
                last, first = chunks
                return f"{first} {last}".strip()
            if len(chunks) >= 3:
                last, jr, first = chunks[0], chunks[1], chunks[2]
                if jr:
                    return f"{first} {last}, {jr}".strip()
                return f"{first} {last}".strip()
        return compact

    parts = [normalize_author(part) for part in raw_parts]
    if len(parts) <= 2:
        return " and ".join(parts)
    return ", ".join(parts[:-1]) + ", and " + parts[-1]


def format_entry(entry: dict[str, str]) -> str:
    fields = entry["fields"]
    authors = format_authors(fields.get("author", ""))
    title = clean_title(fields.get("title", ""))
    venue = fields.get("journal") or fields.get("booktitle") or fields.get("publisher") or ""
    year = fields.get("year", "")
    doi = fields.get("doi", "")
    url = fields.get("url", "")
    pdf = fields.get("pdf", "")

    parts: list[str] = []
    if authors:
        parts.append(f"{authors}.")
    if title:
        parts.append(f"\"{title}.\"")
    if venue:
        parts.append(f"*{venue}*.")
    if year:
        parts.append(f"{year}.")

    links: list[str] = []
    if pdf:
        links.append(f"[PDF]({pdf})")
    if doi:
        doi_url = doi if doi.startswith("http") else f"https://doi.org/{doi}"
        links.append(f"[DOI]({doi_url})")
    if url and all(url not in link for link in links):
        links.append(f"[Link]({url})")

    line = " ".join(parts).strip()
    if links:
        line = f"{line} {' '.join(links)}"
    return line


def sort_entries(entries: list[dict[str, str]]) -> list[dict[str, str]]:
    def sort_key(entry: dict[str, str]) -> tuple[int, str]:
        year = entry.get("year", "")
        year_num = int(year) if year.isdigit() else 0
        return (year_num, entry["key"])

    sorted_entries = entries[:]
    sorted_entries.sort(key=sort_key, reverse=True)
    return sorted_entries


def display_section_title(section: str, include_section_codes: bool) -> str:
    if include_section_codes:
        return section
    return re.sub(r"^[A-Z]\.\s*", "", section).strip()


def render_sections(entries: list[dict[str, str]], include_section_codes: bool = False) -> str:
    lines: list[str] = []

    section_order = [
        "A. Refereed Scientific Articles",
        "B. Non-Refereed Scientific Articles",
        "C. Scientific Books (Monographs)",
        "G. Theses",
    ]
    subsection_order = {
        "A. Refereed Scientific Articles": [
            "Journal Articles",
            "Book Sections",
            "Conference Proceedings",
        ],
        "C. Scientific Books (Monographs)": ["Special Issue of a Journal"],
    }

    section_entries = [entry for entry in entries if entry.get("funder_section")]
    for section in section_order:
        in_section = [entry for entry in section_entries if entry.get("funder_section") == section]
        if not in_section:
            continue

        lines.append(f"### {display_section_title(section, include_section_codes)}")
        lines.append("")

        ordered_subsections = subsection_order.get(section, [])
        with_subsection = [entry for entry in in_section if entry.get("funder_subsection")]
        used_keys: set[str] = set()

        for subsection in ordered_subsections:
            subsection_items = [
                entry for entry in with_subsection if entry.get("funder_subsection") == subsection
            ]
            if not subsection_items:
                continue
            lines.append(f"#### {subsection}")
            lines.append("")
            for item in subsection_items:
                lines.append(item["formatted"])
                lines.append("")
                used_keys.add(item["key"])
            lines.append("")

        remaining = [entry for entry in in_section if entry["key"] not in used_keys]
        for item in remaining:
            lines.append(item["formatted"])
            lines.append("")
        if remaining:
            lines.append("")

    # Fallback rendering for entries without explicit funder sections.
    uncategorized = [entry for entry in entries if not entry.get("funder_section")]
    grouped: dict[str, list[dict[str, str]]] = {}
    for entry in uncategorized:
        grouped.setdefault(entry["category"], []).append(entry)

    category_order = ["Journal articles", "Conference papers", "Book chapters", "Theses", "Other"]
    for category in category_order:
        items = grouped.get(category, [])
        if not items:
            continue
        lines.append(f"### {category}")
        lines.append("")
        for item in items:
            lines.append(item["formatted"])
            lines.append("")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def replace_block(text: str, generated: str) -> str:
    if AUTO_START not in text or AUTO_END not in text:
        raise SystemExit("Missing AUTO-GENERATED markers in publications file.")
    before, remainder = text.split(AUTO_START, 1)
    _, after = remainder.split(AUTO_END, 1)
    return f"{before}{AUTO_START}\n\n{generated}\n{AUTO_END}{after}"
