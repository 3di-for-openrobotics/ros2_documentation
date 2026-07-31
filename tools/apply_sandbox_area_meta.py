#!/usr/bin/env python3
"""Sandbox helper: add ``area`` metadata to the ROS-Framework pages.

The related article and related package lists match on the first (most
specific) ``area`` value declared on a page. Most pages do not carry that
metadata yet, so this script fills it in for everything under
``source/ROS-Framework`` based on the folder the page lives in. It is meant
only for the ``dynamic-lists-sandbox`` branch, so the lists have something to
show while the real metadata is being written.

The area chain is ordered most specific first, for example::

    .. meta::
       :area: nodes, framework

Rules of thumb:
  * ``ROS-Framework/nodes/**``            -> ``nodes, framework``
  * ``ROS-Framework/parameters/**``       -> ``parameters, framework``
  * ``ROS-Framework/client-libraries/**`` -> ``client-libraries, framework``
  * ``ROS-Framework/interfaces/topics/**``   -> ``topics, interfaces, framework``
  * ``ROS-Framework/interfaces/services/**`` -> ``services, interfaces, framework``
  * ``ROS-Framework/interfaces/actions/**``  -> ``actions, interfaces, framework``
  * hub pages (``About-*.rst``) map by their name.

The script is idempotent: a page that already has a ``.. meta::`` block with an
``:area:`` field is left untouched.

Usage (from the repository root)::

    python tools/apply_sandbox_area_meta.py          # apply changes
    python tools/apply_sandbox_area_meta.py --dry-run # preview only
"""

from __future__ import annotations

import argparse
import os
import re
from typing import List, Optional, Tuple

FRAMEWORK_ROOT = os.path.join('source', 'ROS-Framework')

# Section adornment characters that mark a title underline in RST.
ADORNMENT = set('=-`:\'"~^_*+#<>.')

INTERFACE_LEAVES = ('topics', 'services', 'actions')


def area_chain(rel_dirs: List[str], stem: str) -> List[str]:
    """Return the ordered area chain (most specific first) for a page."""
    low = stem.lower()

    if not rel_dirs:
        # Hub page directly under ROS-Framework; infer from the file name.
        if 'client' in low:
            return ['client-libraries', 'framework']
        if 'parameter' in low:
            return ['parameters', 'framework']
        if 'node' in low:
            return ['nodes', 'framework']
        if 'topic' in low:
            return ['topics', 'interfaces', 'framework']
        if 'service' in low:
            return ['services', 'interfaces', 'framework']
        if 'action' in low:
            return ['actions', 'interfaces', 'framework']
        return ['interfaces', 'framework']

    seg0 = rel_dirs[0].lower()
    if seg0 == 'interfaces':
        if len(rel_dirs) >= 2 and rel_dirs[1].lower() in INTERFACE_LEAVES:
            return [rel_dirs[1].lower(), 'interfaces', 'framework']
        if 'topic' in low:
            return ['topics', 'interfaces', 'framework']
        if 'service' in low:
            return ['services', 'interfaces', 'framework']
        if 'action' in low:
            return ['actions', 'interfaces', 'framework']
        return ['interfaces', 'framework']

    return [seg0, 'framework']


def area_value(rel_dirs: List[str], stem: str) -> str:
    """Return the comma separated ``area`` string for a page."""
    chain = list(dict.fromkeys(area_chain(rel_dirs, stem)))
    return ', '.join(chain)


def is_title_underline(text: str, underline: str) -> bool:
    """True when ``underline`` is a valid RST title adornment for ``text``."""
    stripped = underline.rstrip('\n')
    if len(stripped) < 3:
        return False
    chars = set(stripped)
    if not chars or not chars.issubset(ADORNMENT):
        return False
    if len(stripped) < len(text.rstrip('\n')):
        return False
    return True


def find_title_index(lines: List[str]) -> Optional[int]:
    """Return the index of the first title text line, or ``None``."""
    for i in range(len(lines) - 1):
        text = lines[i]
        if not text.strip():
            continue
        if text.startswith((' ', '\t')):
            continue
        if text.lstrip().startswith(('..', ':')):
            continue
        if is_title_underline(text, lines[i + 1]):
            return i
    return None


def already_tagged(text: str) -> bool:
    """True when the page already declares an ``area`` via ``.. meta::``."""
    return re.search(r'^\.\.\s+meta::', text, re.MULTILINE) is not None and \
        re.search(r'^\s*:area:', text, re.MULTILINE) is not None


def insert_meta(text: str, area: str) -> Optional[str]:
    """Return ``text`` with a meta block inserted, or ``None`` to skip."""
    if already_tagged(text):
        return None

    newline = '\r\n' if '\r\n' in text else '\n'
    lines = text.split('\n')
    # Normalize away trailing carriage returns for detection only.
    probe = [ln.rstrip('\r') for ln in lines]

    block = [
        '.. meta::',
        f'   :area: {area}',
        '',
    ]

    idx = find_title_index(probe)
    if idx is None:
        idx = 0

    new_lines = lines[:idx] + block + lines[idx:]
    return newline.join(new_lines) if newline == '\n' else \
        newline.join(ln.rstrip('\r') for ln in new_lines)


def iter_rst(root: str):
    """Yield every ``.rst`` path under ``root``."""
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            if name.endswith('.rst'):
                yield os.path.join(dirpath, name)


def process(root: str, dry_run: bool) -> Tuple[int, int]:
    """Apply (or preview) the meta insertion across ``root``."""
    changed = 0
    skipped = 0
    for path in iter_rst(root):
        rel = os.path.relpath(path, root)
        parts = rel.split(os.sep)
        rel_dirs = parts[:-1]
        stem = parts[-1][:-len('.rst')]
        area = area_value(rel_dirs, stem)

        with open(path, 'r', encoding='utf-8') as handle:
            text = handle.read()

        updated = insert_meta(text, area)
        if updated is None:
            skipped += 1
            continue

        changed += 1
        print(f'[area: {area:<34}] {rel}')
        if not dry_run:
            with open(path, 'w', encoding='utf-8', newline='') as handle:
                handle.write(updated)

    return changed, skipped


def main() -> None:
    """Parse arguments and run the meta insertion."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--root',
        default=FRAMEWORK_ROOT,
        help='Folder to scan (default: source/ROS-Framework).',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview the changes without writing files.',
    )
    args = parser.parse_args()

    if not os.path.isdir(args.root):
        raise SystemExit(f'Not a directory: {args.root} (run from the repo root)')

    changed, skipped = process(args.root, args.dry_run)
    verb = 'Would update' if args.dry_run else 'Updated'
    print(f'\n{verb} {changed} file(s); left {skipped} already tagged.')


if __name__ == '__main__':
    main()
