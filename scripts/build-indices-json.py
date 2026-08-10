#!/usr/bin/env python3
"""
Generate indices.json from README.md.

README.md is the single source of truth for this repo. indices.json is a
machine-readable mirror of it, consumed by the master index repo
(danielrosehill/Index, scripts/sync-indexing-repos.py) to build its
"Index of Indexes" section.

The two halves were maintained by hand and drifted badly: as of 2026-08-10
the README carried 57 entries while indices.json still held the 29 from
2026-03-25, including three repos that had since been renamed. Deriving one
from the other removes that failure mode — never hand-edit indices.json.

Usage:
    python3 scripts/build-indices-json.py [--check]

    --check  exit 1 if indices.json is out of date instead of rewriting it
"""

import argparse
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
README = PROJECT_ROOT / "README.md"
INDICES_JSON = PROJECT_ROOT / "indices.json"

# An entry is an H3 whose heading is the repo slug, a description paragraph,
# then a "View Repo" badge linking to the repo. The License section at the
# foot is an H2, so it terminates the final entry without matching.
ENTRY_RE = re.compile(
    r"^### (?P<slug>\S+)\n"
    r"\n"
    r"(?P<description>.+?)\n"
    r"\n"
    r"\[!\[View Repo\]\([^)]*\)\]\((?P<url>https://github\.com/[^)]+)\)",
    re.MULTILINE | re.DOTALL,
)


def parse_readme(text: str) -> list[dict]:
    entries = []
    for match in ENTRY_RE.finditer(text):
        slug = match.group("slug")
        url = match.group("url")
        description = " ".join(match.group("description").split())

        if not url.endswith(f"/{slug}"):
            print(
                f"warning: heading '{slug}' does not match link {url}",
                file=sys.stderr,
            )

        entries.append({"title": slug, "description": description, "url": url})
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify indices.json is current without rewriting it",
    )
    args = parser.parse_args()

    entries = parse_readme(README.read_text(encoding="utf-8"))
    if not entries:
        print("error: no entries parsed from README.md", file=sys.stderr)
        return 1

    slugs = [entry["title"] for entry in entries]
    duplicates = {slug for slug in slugs if slugs.count(slug) > 1}
    if duplicates:
        print(f"error: duplicate entries: {', '.join(sorted(duplicates))}", file=sys.stderr)
        return 1

    payload = json.dumps({"indices": entries}, indent=2, ensure_ascii=False) + "\n"

    if args.check:
        current = INDICES_JSON.read_text(encoding="utf-8") if INDICES_JSON.exists() else ""
        if current != payload:
            print("indices.json is out of date — run build-indices-json.py", file=sys.stderr)
            return 1
        print(f"✓ indices.json is current ({len(entries)} entries)")
        return 0

    INDICES_JSON.write_text(payload, encoding="utf-8")
    print(f"✓ Wrote {INDICES_JSON.relative_to(PROJECT_ROOT)} ({len(entries)} entries)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
