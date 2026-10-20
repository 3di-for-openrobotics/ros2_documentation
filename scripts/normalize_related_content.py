#!/usr/bin/env python3
"""Normalize Related content blocks to the canonical articles directive.

Preserves curated/manual bullet links (:doc:, :ref:, external links) from the
old Related-content articles portion. Does not touch Related packages,
Packages/reference, FAQs, or Next steps.

Canonical shape when curated links exist:

Related content
---------------

Related articles:

* :doc:`...`
* ...

.. ros-related-articles::

When none exist, omits the bullet list and keeps only the directive.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "source"
LIST = Path(__file__).resolve().parent / "related_content_to_normalize.txt"
REPORT = Path(__file__).resolve().parent / "related_content_normalize_report.txt"

RELATED_START_RE = re.compile(r"(?m)^Related content\s*\n-+\s*\n")
# Next sibling section (same level underline ----) or packages subsections we must keep
STOP_HEADING_RE = re.compile(
    r"(?m)^(?P<title>"
    r"FAQs(?:\s*\(placeholder\))?|"
    r"Next steps|"
    r"Related packages|"
    r"Packages/reference:"
    r")\s*\n(?P<underline>[-=~^\"']{3,})\s*\n"
)
# Packages/reference uses a label line without underline sometimes
STOP_LABEL_RE = re.compile(r"(?m)^Packages/reference:\s*\n")

BULLET_RE = re.compile(r"(?m)^(?P<item>\*[ \t].*(?:\n[ \t]+\S.*)*)")
DOC_REF_RE = re.compile(r":(?:doc|ref):`[^`]+`")
EXT_LINK_RE = re.compile(r"`[^`]+<(https?://[^>]+)>`__?")
CANONICAL_DIR = ".. ros-related-articles::"


def load_targets() -> list[str]:
    out: list[str] = []
    for line in LIST.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.append(line)
    return out


def find_related_span(text: str) -> tuple[int, int] | None:
    start_m = RELATED_START_RE.search(text)
    if not start_m:
        return None
    start = start_m.start()
    rest = text[start_m.end() :]
    stop_candidates: list[int] = []
    for rx in (STOP_HEADING_RE, STOP_LABEL_RE):
        m = rx.search(rest)
        if m:
            stop_candidates.append(start_m.end() + m.start())
    end = min(stop_candidates) if stop_candidates else len(text)
    return start, end


def _bullet_for_link(token: str) -> str:
    """Turn a :doc:/:ref:/external link token into a curated bullet line."""
    # :doc:`Title <path>` or :doc:`path`
    m = re.match(r":doc:`([^`<]+)(?:<([^>]+)>)?`", token)
    if m:
        title = m.group(1).strip()
        path = (m.group(2) or title).strip()
        if m.group(2):
            return f"* :doc:`{title} <{path}>`"
        return f"* :doc:`{path}`"
    m = re.match(r":ref:`([^`<]+)(?:<([^>]+)>)?`", token)
    if m:
        title = m.group(1).strip()
        target = (m.group(2) or title).strip()
        if m.group(2):
            return f"* :ref:`{title} <{target}>`"
        return f"* :ref:`{target}`"
    m = re.match(r"`([^`<]+)<([^>]+)>`(__?)", token)
    if m:
        label = m.group(1).strip()
        url = m.group(2).strip()
        suffix = m.group(3)
        return f"* `{label} <{url}>`{suffix}"
    return f"* {token}"


def extract_curated_bullets(block: str) -> list[str]:
    """Return bullet items for curated links (bullets + inline prose links)."""
    body = RELATED_START_RE.sub("", block, count=1)
    body = re.sub(r"(?im)^(More articles:|Related articles:?)\s*\n", "", body)

    curated: list[str] = []
    seen_fps: set[str] = set()

    for m in BULLET_RE.finditer(body):
        item = m.group("item").rstrip()
        fps = link_fingerprints(item)
        if not fps:
            continue
        curated.append(item)
        seen_fps |= fps

    # Preserve inline links that were only in prose (not already in a bullet).
    for m in DOC_REF_RE.finditer(body):
        token = m.group(0)
        if token in seen_fps:
            continue
        curated.append(_bullet_for_link(token))
        seen_fps.add(token)

    for m in EXT_LINK_RE.finditer(body):
        token = m.group(0)
        if token in seen_fps:
            continue
        curated.append(_bullet_for_link(token))
        seen_fps.add(token)

    return curated


def link_fingerprints(text: str) -> set[str]:
    """Stable identifiers for curated links (for loss detection)."""
    found: set[str] = set()
    for m in DOC_REF_RE.finditer(text):
        found.add(m.group(0))
    for m in EXT_LINK_RE.finditer(text):
        found.add(m.group(0))
    return found


def build_replacement(curated: list[str]) -> str:
    parts = [
        "Related content",
        "---------------",
        "",
        "Related articles:",
        "",
    ]
    if curated:
        parts.extend(curated)
        parts.append("")
    parts.append(CANONICAL_DIR)
    parts.append("")
    return "\n".join(parts)


def normalize_text(text: str) -> tuple[str, dict]:
    span = find_related_span(text)
    if not span:
        return text, {"status": "no_related_content"}

    start, end = span
    old_block = text[start:end]
    if CANONICAL_DIR in old_block and "Related articles:" in old_block:
        return text, {"status": "already_canonical", "curated": extract_curated_bullets(old_block)}

    curated = extract_curated_bullets(old_block)
    before_fps = link_fingerprints(old_block)
    new_block = build_replacement(curated)
    after_fps = link_fingerprints(new_block)
    lost = sorted(before_fps - after_fps)
    gained = sorted(after_fps - before_fps)

    new_text = text[:start] + new_block + text[end:]
    # Ensure we didn't drop links elsewhere in file either for these fps
    file_after_fps = link_fingerprints(new_text)
    lost_from_file = sorted(before_fps - file_after_fps)

    return new_text, {
        "status": "normalized",
        "curated_count": len(curated),
        "before_links": sorted(before_fps),
        "after_links": sorted(after_fps),
        "lost_in_block": lost,
        "lost_from_file": lost_from_file,
        "gained": gained,
        "old_block": old_block,
        "new_block": new_block,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only check that curated links in Related content are still present "
        "alongside the directive (no writes).",
    )
    args = parser.parse_args()

    report: list[str] = []
    problems = 0
    changed = 0

    for rel in load_targets():
        path = ROOT / rel
        raw = path.read_bytes()
        newline = "\r\n" if b"\r\n" in raw else "\n"
        text = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")

        if args.verify_only:
            span = find_related_span(text)
            if not span:
                report.append(f"VERIFY FAIL  {rel}: no Related content block")
                problems += 1
                continue
            block = text[span[0] : span[1]]
            if CANONICAL_DIR not in block:
                report.append(f"VERIFY WARN  {rel}: missing {CANONICAL_DIR}")
                problems += 1
            fps = link_fingerprints(block)
            curated = extract_curated_bullets(block)
            report.append(
                f"VERIFY OK    {rel}: directive="
                f"{'yes' if CANONICAL_DIR in block else 'no'} "
                f"curated_links={len(fps)} bullets={len(curated)}"
            )
            if fps:
                for fp in sorted(fps):
                    report.append(f"             keep: {fp}")
            continue

        new_text, info = normalize_text(text)
        status = info["status"]
        if status == "no_related_content":
            report.append(f"SKIP  {rel}: no Related content")
            continue
        if status == "already_canonical":
            report.append(
                f"OK    {rel}: already canonical "
                f"(curated bullets={len(info.get('curated') or [])})"
            )
            continue

        lost = info.get("lost_from_file") or []
        if lost:
            problems += 1
            report.append(f"FAIL  {rel}: would LOSE {len(lost)} curated link(s)")
            for item in lost:
                report.append(f"      LOST: {item}")
            report.append("      --- old block ---")
            report.extend("      " + ln for ln in info["old_block"].splitlines())
            report.append("      --- new block ---")
            report.extend("      " + ln for ln in info["new_block"].splitlines())
            continue

        changed += 1
        report.append(
            f"{'DRY ' if args.dry_run else 'APPLIED '} {rel}: "
            f"kept {info['curated_count']} curated bullet(s), "
            f"{len(info['before_links'])} link fingerprint(s)"
        )
        for fp in info["before_links"]:
            report.append(f"      keep: {fp}")
        if not info["before_links"]:
            report.append("      (no curated :doc:/:ref:/external links in old block)")

        if not args.dry_run:
            path.write_bytes(new_text.replace("\n", newline).encode("utf-8"))

    summary = [
        "# Related content normalize report",
        f"# mode: {'verify-only' if args.verify_only else ('dry-run' if args.dry_run else 'apply')}",
        f"# changed_or_would_change: {changed}",
        f"# problems: {problems}",
        "",
        *report,
        "",
    ]
    REPORT.write_text("\n".join(summary), encoding="utf-8")
    print("\n".join(summary))
    print(f"Wrote {REPORT}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
