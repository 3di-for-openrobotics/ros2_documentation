#!/usr/bin/env python3
"""Sandbox helper: add ``content-type`` metadata under ROS-Framework.

Related-article ordering uses ``content-type``. This script fills a sensible
value from the path/filename when the field is missing.

Rules of thumb:
  * ``About-*.rst`` / hub About pages     -> about
  * ``Understanding-*`` / Tutorial paths  -> tutorial
  * ``Working-with-*`` how-tos            -> how-to
  * ``*Example*`` / ``*-example*``        -> example
  * otherwise                             -> how-to

Usage::

    python tools/apply_sandbox_content_type_meta.py
    python tools/apply_sandbox_content_type_meta.py --dry-run
"""

from __future__ import annotations

import argparse
import os
import re

FRAMEWORK_ROOT = os.path.join('source', 'ROS-Framework')
ADORNMENT = set('=-`:\'"~^_*+#<>.')


def guess_content_type(rel: str, stem: str) -> str:
    """Return a content-type token for a page path."""
    low_rel = rel.replace('\\', '/').lower()
    low = stem.lower()
    if low.startswith('about-') or '/about-' in low_rel or low in {
        'about-nodes',
        'about-parameters',
        'about-client-libraries',
        'about-topics',
        'about-services',
        'about-actions',
        'about-interfaces',
        'about-composition',
        'about-discovery',
        'about-domain-id',
        'about-logging',
        'about-tf2',
    }:
        return 'about'
    if 'understanding-' in low or 'tutorial' in low_rel:
        return 'tutorial'
    if 'example' in low or 'example' in low_rel:
        return 'example'
    if 'reference' in low:
        return 'reference'
    if 'learning' in low or 'learning-path' in low_rel:
        return 'learning path'
    if 'process' in low and 'overview' in low:
        return 'process overview'
    return 'how-to'


def is_title_underline(text: str, underline: str) -> bool:
    """True when ``underline`` is a valid RST title adornment for ``text``."""
    stripped = underline.rstrip('\n')
    if len(stripped) < 3:
        return False
    chars = set(stripped)
    if not chars or not chars.issubset(ADORNMENT):
        return False
    return len(stripped) >= len(text.rstrip('\n'))


def find_title_index(lines: list[str]) -> int | None:
    """Return the index of the first title text line, or ``None``."""
    for i in range(len(lines) - 1):
        text = lines[i]
        if not text.strip() or text.startswith((' ', '\t')):
            continue
        if text.lstrip().startswith(('..', ':')):
            continue
        if is_title_underline(text, lines[i + 1]):
            return i
    return None


def already_has_content_type(text: str) -> bool:
    """True when ``content-type`` is already declared."""
    return re.search(r'^\s*:content-type:', text, re.MULTILINE) is not None


def insert_or_extend_meta(text: str, content_type: str) -> str | None:
    """Add ``:content-type:`` to an existing meta block or insert a new one."""
    if already_has_content_type(text):
        return None

    newline = '\r\n' if '\r\n' in text else '\n'
    # Extend existing .. meta:: block.
    meta_match = re.search(r'^(\.\.\s+meta::\s*\n(?:[ \t]+.*\n)*)', text, re.MULTILINE)
    if meta_match:
        block = meta_match.group(1)
        if not block.endswith('\n'):
            block += '\n'
        insertion = f'   :content-type: {content_type}\n'
        updated_block = block.rstrip('\n') + '\n' + insertion
        return text[: meta_match.start(1)] + updated_block + text[meta_match.end(1) :]

    lines = text.split('\n')
    probe = [ln.rstrip('\r') for ln in lines]
    idx = find_title_index(probe)
    if idx is None:
        idx = 0
    block = [
        '.. meta::',
        f'   :content-type: {content_type}',
        '',
    ]
    new_lines = lines[:idx] + block + lines[idx:]
    return newline.join(ln.rstrip('\r') for ln in new_lines)


def main() -> None:
    """Apply content-type metadata under ROS-Framework."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default=FRAMEWORK_ROOT)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    if not os.path.isdir(args.root):
        raise SystemExit(f'Not a directory: {args.root}')

    changed = 0
    skipped = 0
    for dirpath, _dirs, files in os.walk(args.root):
        for name in files:
            if not name.endswith('.rst'):
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, args.root)
            stem = name[: -len('.rst')]
            content_type = guess_content_type(rel, stem)
            with open(path, 'r', encoding='utf-8') as handle:
                text = handle.read()
            updated = insert_or_extend_meta(text, content_type)
            if updated is None:
                skipped += 1
                continue
            changed += 1
            print(f'[content-type: {content_type:<16}] {rel}')
            if not args.dry_run:
                with open(path, 'w', encoding='utf-8', newline='') as handle:
                    handle.write(updated)

    verb = 'Would update' if args.dry_run else 'Updated'
    print(f'\n{verb} {changed} file(s); left {skipped} already tagged.')


if __name__ == '__main__':
    main()
