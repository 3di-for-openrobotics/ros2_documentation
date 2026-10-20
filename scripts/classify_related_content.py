#!/usr/bin/env python3
"""Classify Related-content shapes in the TO UPDATE list."""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "source"
LIST = Path(__file__).resolve().parent / "related_content_to_update.txt"
OUT = Path(__file__).resolve().parent / "related_content_buckets.txt"


def load_targets() -> list[Path]:
    paths: list[Path] = []
    for line in LIST.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        paths.append(ROOT / line)
    return paths


def classify(text: str) -> str:
    has_related_content = bool(re.search(r"(?im)^Related content\s*$", text))
    has_related_articles = bool(re.search(r"(?im)^Related articles\s*$", text))
    has_related_packages = bool(re.search(r"(?im)^Related packages\s*$", text))
    has_faqs = bool(re.search(r"(?im)^FAQs(\s*\(placeholder\))?\s*$", text))
    has_comment = bool(re.search(r"(?im)^\.\.\s*Related content", text))
    has_example = bool(re.search(r"(?m)^\s*\*\s+Example\s*$", text))
    has_doc_link = bool(re.search(r":doc:`|:ref:`", text))

    if not has_related_content and not has_comment and not has_related_articles:
        return "A_none"

    if has_comment and not has_related_content:
        return "B_comment_placeholder_only"

    if has_related_content and has_related_packages:
        return "H_related_content_with_packages"

    if has_related_content and has_faqs:
        return "G_related_content_plus_faqs"

    if has_related_content and has_related_articles:
        # inspect articles subsection roughly
        m = re.search(
            r"(?is)^Related articles\s*\n\^+\s*\n(.*?)(?=^[A-Za-z].*\n[-=^~]{3,}|\Z)",
            text,
            re.M,
        )
        body = m.group(1) if m else ""
        if ":doc:`" in body or ":ref:`" in body:
            return "C_already_has_article_links"
        if has_example or not re.search(r"^\s*\*", body, re.M):
            return "D_related_articles_empty_or_example"
        return "E_related_articles_other_bullets"

    if has_related_content and has_example:
        return "F_related_content_example_placeholders"

    if has_related_content:
        return "I_related_content_other_shape"

    if has_doc_link and has_related_articles:
        return "J_articles_without_parent_heading"

    return "K_misc"


def snippet(text: str) -> str:
    for rx in (
        r"(?is)(\.\.\s*Related content.{0,350})",
        r"(?is)(Related content\s*\n.{0,450})",
    ):
        m = re.search(rx, text)
        if m:
            lines = m.group(1).strip().splitlines()
            return "\n".join(lines[:14])
    return "(no related-looking block)"


def main() -> int:
    buckets: dict[str, list[str]] = defaultdict(list)
    samples: dict[str, list[tuple[str, str]]] = defaultdict(list)

    targets = load_targets()
    for path in targets:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT).as_posix()
        key = classify(text)
        buckets[key].append(rel)
        if len(samples[key]) < 3:
            samples[key].append((rel, snippet(text)))

    lines: list[str] = []
    lines.append(f"# Related-content shape buckets for TO UPDATE set (n={len(targets)})\n")
    for key in sorted(buckets):
        lines.append(f"## {key}: {len(buckets[key])}")
        for rel in buckets[key]:
            lines.append(rel)
        lines.append("")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"=== BUCKET COUNTS (n={len(targets)}) ===")
    for key in sorted(buckets):
        print(f"{key}: {len(buckets[key])}")

    print("\n=== SAMPLES ===")
    for key in sorted(samples):
        print(f"\n## {key} ({len(buckets[key])})")
        for rel, snip in samples[key]:
            print(f"--- {rel}")
            print(snip)

    print(f"\nWrote {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
