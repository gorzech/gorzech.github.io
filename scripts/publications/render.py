from __future__ import annotations


AUTO_START = "<!-- AUTO-GENERATED:START -->"
AUTO_END = "<!-- AUTO-GENERATED:END -->"


def format_authors(value: str) -> str:
    if not value:
        return ""
    raw_parts = [part.strip() for part in value.replace("\n", " ").split(" and ") if part.strip()]

    def normalize_author(author: str) -> str:
        compact = " ".join(author.split())
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
    title = fields.get("title", "")
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


def render_sections(entries: list[dict[str, str]]) -> str:
    grouped: dict[str, list[dict[str, str]]] = {}
    for entry in entries:
        grouped.setdefault(entry["category"], []).append(entry)

    order = ["Journal articles", "Conference papers", "Book chapters", "Theses", "Other"]
    lines: list[str] = []
    for category in order:
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

