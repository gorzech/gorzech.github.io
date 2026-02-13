from __future__ import annotations

import re


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
        k += 1
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


def parse_fields(body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    i = 0
    n = len(body)
    while i < n:
        while i < n and body[i].isspace():
            i += 1
        if i >= n:
            break
        name_start = i
        while i < n and (body[i].isalnum() or body[i] in "_-"):
            i += 1
        name = body[name_start:i].strip().lower()
        if not name:
            i += 1
            continue
        while i < n and body[i].isspace():
            i += 1
        if i >= n or body[i] != "=":
            while i < n and body[i] not in ",\n":
                i += 1
            i += 1
            continue
        i += 1
        while i < n and body[i].isspace():
            i += 1
        if i >= n:
            break

        value = ""
        if body[i] == "{":
            i += 1
            depth = 1
            start = i
            while i < n and depth > 0:
                ch = body[i]
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                i += 1
            value = body[start : i - 1]
        elif body[i] == '"':
            i += 1
            start = i
            while i < n:
                ch = body[i]
                if ch == '"' and body[i - 1] != "\\":
                    break
                i += 1
            value = body[start:i]
            if i < n and body[i] == '"':
                i += 1
        else:
            start = i
            while i < n and body[i] not in ",\n":
                i += 1
            value = body[start:i].strip()

        fields[name] = value.strip()
        while i < n and body[i] != ",":
            if body[i] == "\n":
                break
            i += 1
        if i < n and body[i] == ",":
            i += 1
    return fields


def is_selected(body: str) -> bool:
    return re.search(r'(?i)\bselected\s*=\s*[{"]\s*true\s*[}"]', body) is not None


def year_value(body: str) -> int:
    match = re.search(r'(?i)\byear\s*=\s*[{"]\s*(\d{4})\s*[}"]', body)
    return int(match.group(1)) if match else 0


def category_for(entry_type: str) -> str:
    t = entry_type.lower()
    if t == "article":
        return "Journal articles"
    if t in {"inproceedings", "proceedings"}:
        return "Conference papers"
    if t in {"incollection", "inbook", "bookchapter"}:
        return "Book chapters"
    if t in {"phdthesis", "mastersthesis", "bachelorthesis", "thesis"}:
        return "Theses"
    return "Other"


def enrich_entries(entries: list[dict[str, str]]) -> list[dict[str, str]]:
    enriched: list[dict[str, str]] = []
    for entry in entries:
        item = dict(entry)
        fields = parse_fields(item["body"])
        item["fields"] = fields
        item["category"] = category_for(item["type"])
        item["year"] = fields.get("year") or ""
        enriched.append(item)
    return enriched


def validate_entries(entries: list[dict[str, str]]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not entries:
        errors.append("No BibTeX entries were parsed from publications.bib.")
        return errors, warnings

    seen: set[str] = set()
    duplicates: set[str] = set()
    for entry in entries:
        key = entry["key"]
        if key in seen:
            duplicates.add(key)
        seen.add(key)
        if is_selected(entry["body"]) and not year_value(entry["body"]):
            warnings.append(f"Selected entry missing year: {key}")

    if duplicates:
        errors.append(f"Duplicate BibTeX keys: {', '.join(sorted(duplicates))}")
    return errors, warnings

