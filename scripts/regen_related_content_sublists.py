#!/usr/bin/env python3
"""Regenerate Related-content treatment sublists from TO UPDATE set.

Target block:

Related content
---------------

Related articles:

.. ros-related-articles::

Does not modify RST files — writes list files only.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "source"
OUT_DIR = Path(__file__).resolve().parent
TO_UPDATE = OUT_DIR / "related_content_to_update.txt"

CANONICAL = (
    "Related content\n"
    "---------------\n"
    "\n"
    "Related articles:\n"
    "\n"
    ".. ros-related-articles::\n"
)

RELATED_CONTENT_RE = re.compile(r"(?im)^Related content\s*$")
RELATED_PACKAGES_RE = re.compile(r"(?im)^Related packages\s*$")
RELATED_ARTICLES_DIR_RE = re.compile(r"(?m)^\.\.\s*ros-related-articles::\s*$")
COMMENT_RELATED_RE = re.compile(r"(?im)^\.\.\s*Related content")
AREA_RE = re.compile(
    r"(?is)^\.\.\s*meta::.*?(?:^|\n)[ \t]*:(?:area)\s*:\s*(?P<area>[^\n]*)",
    re.M,
)


def load_targets() -> list[Path]:
    paths: list[Path] = []
    for line in TO_UPDATE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        paths.append(ROOT / line)
    return paths


def meta_area(text: str) -> str | None:
    m = AREA_RE.search(text)
    if not m:
        return None
    area = m.group("area").strip()
    return area or None


def write_list(path: Path, title: str, notes: list[str], files: list[str]) -> None:
    lines = [f"# {title}", f"# Count: {len(files)}"]
    for note in notes:
        lines.append(f"# {note}")
    lines.append("")
    lines.extend(files)
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    to_append: list[str] = []
    to_normalize: list[str] = []
    has_related_packages: list[str] = []
    missing_area: list[str] = []
    already_canonicalish: list[str] = []
    comment_placeholder: list[str] = []

    for path in load_targets():
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8")
        area = meta_area(text)
        if area is None:
            missing_area.append(rel)

        has_rc = bool(RELATED_CONTENT_RE.search(text))
        has_packages = bool(RELATED_PACKAGES_RE.search(text))
        has_directive = bool(RELATED_ARTICLES_DIR_RE.search(text))
        has_comment = bool(COMMENT_RELATED_RE.search(text))

        if has_packages:
            has_related_packages.append(rel)
            # still may need normalize of articles half; keep in this list primarily
            continue

        if has_rc and has_directive and "Related articles:" in text:
            # likely already close to target; still list for spot-check
            already_canonicalish.append(rel)
            continue

        if has_comment and not has_rc:
            comment_placeholder.append(rel)
            # placeholders are not live Related content; treat as append targets
            # (special-case About pages are already excluded from TO UPDATE)
            to_append.append(rel)
            continue

        if not has_rc:
            to_append.append(rel)
            continue

        to_normalize.append(rel)

    write_list(
        OUT_DIR / "related_content_to_append.txt",
        "APPEND canonical Related content block",
        [
            "No live 'Related content' heading (may include commented placeholders).",
            "Action: append canonical block at end of file.",
            "Skip / fix first if also listed in missing_area.",
        ],
        to_append,
    )
    write_list(
        OUT_DIR / "related_content_to_normalize.txt",
        "NORMALIZE existing Related content (no Related packages)",
        [
            "Has 'Related content' but not yet the canonical articles directive shape.",
            "Action: replace articles portion with canonical block.",
            "Do not touch Related packages (none expected in this list).",
        ],
        to_normalize,
    )
    write_list(
        OUT_DIR / "related_content_has_related_packages.txt",
        "HAS Related packages — surgical articles-only pass",
        [
            "Action: rewrite Related articles / insert directive only.",
            "Do NOT modify Related packages section.",
        ],
        has_related_packages,
    )
    write_list(
        OUT_DIR / "related_content_missing_area.txt",
        "MISSING or empty meta :area:",
        [
            "Adding .. ros-related-articles:: will fail the Sphinx build.",
            "Fix area before or with the Related content update.",
            "These paths may also appear in other sublists.",
        ],
        missing_area,
    )
    write_list(
        OUT_DIR / "related_content_already_canonicalish.txt",
        "ALREADY looks canonical (spot-check)",
        [
            "Has Related content + 'Related articles:' + ros-related-articles directive.",
            "No write expected unless spot-check finds drift.",
        ],
        already_canonicalish,
    )
    write_list(
        OUT_DIR / "related_content_comment_placeholder.txt",
        "Comment placeholder only (subset of append)",
        [
            "Has '.. Related content' comment, no live Related content heading.",
            "Also included in related_content_to_append.txt.",
        ],
        comment_placeholder,
    )

    # summary index
    summary = OUT_DIR / "related_content_sublists_SUMMARY.txt"
    summary.write_text(
        "\n".join(
            [
                "# Related content sublists SUMMARY",
                f"# Canonical target:\n# {CANONICAL.replace(chr(10), chr(10) + '# ')}",
                "",
                f"to_append: {len(to_append)} -> related_content_to_append.txt",
                f"to_normalize: {len(to_normalize)} -> related_content_to_normalize.txt",
                f"has_related_packages: {len(has_related_packages)} -> related_content_has_related_packages.txt",
                f"missing_area: {len(missing_area)} -> related_content_missing_area.txt",
                f"already_canonicalish: {len(already_canonicalish)} -> related_content_already_canonicalish.txt",
                f"comment_placeholder (info): {len(comment_placeholder)} -> related_content_comment_placeholder.txt",
                "",
            ]
        ),
        encoding="utf-8",
    )

    print(summary.read_text(encoding="utf-8"))
    print(f"Wrote lists under {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
