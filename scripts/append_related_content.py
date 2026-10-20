#!/usr/bin/env python3
"""Append canonical Related content block to to_append list files.

Skips Get-Started/Installation/Snapshot-Repository.rst (missing :area:).

Target block:

Related content
---------------

Related articles:

.. ros-related-articles::
"""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "source"
LIST = Path(__file__).resolve().parent / "related_content_to_append.txt"
SKIP = {"Get-Started/Installation/Snapshot-Repository.rst"}

BLOCK = (
    "Related content\n"
    "---------------\n"
    "\n"
    "Related articles:\n"
    "\n"
    ".. ros-related-articles::\n"
)


def load_targets() -> list[str]:
    paths: list[str] = []
    for line in LIST.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        paths.append(line)
    return paths


def append_block(text: str) -> str:
    body = text.rstrip() + "\n\n" + BLOCK
    if text.endswith("\n"):
        # keep a single trailing newline on file
        return body
    return body


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report files that would change without writing",
    )
    args = parser.parse_args()

    changed: list[str] = []
    skipped: list[str] = []
    already: list[str] = []

    for rel in load_targets():
        if rel in SKIP:
            skipped.append(rel)
            continue

        path = ROOT / rel
        raw = path.read_bytes()
        newline = "\r\n" if b"\r\n" in raw else "\n"
        text = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")

        if "Related content\n---------------" in text or ".. ros-related-articles::" in text:
            already.append(rel)
            continue

        new_text = append_block(text)
        changed.append(rel)
        if not args.dry_run:
            path.write_bytes(new_text.replace("\n", newline).encode("utf-8"))

    mode = "DRY RUN" if args.dry_run else "APPLIED"
    print(f"=== {mode}: append Related content ===")
    print(f"Would change / changed: {len(changed)}")
    print(f"Skipped (no area): {len(skipped)}")
    for rel in skipped:
        print(f"  skip: {rel}")
    print(f"Already had block: {len(already)}")
    for rel in already:
        print(f"  already: {rel}")
    if args.dry_run:
        print("\nFirst 10 targets:")
        for rel in changed[:10]:
            print(f"  {rel}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
