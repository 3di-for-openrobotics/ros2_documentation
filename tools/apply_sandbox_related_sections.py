#!/usr/bin/env python3
"""Sandbox helper: append a "Related content" section to ROS-Framework pages.

For testing, this drops a bottom section holding both directives onto every
page under ``source/ROS-Framework`` so each article shows its related article
and related package lists. It pairs with ``apply_sandbox_area_meta.py``, which
gives every page the ``area`` metadata the directives match on.

The section looks like this::

    Related content
    ---------------

    Related articles:

    .. ros-related-articles::

    Related packages:

    .. ros-related-packages::

The script is idempotent: a page that already contains the directives is left
untouched, so it is safe to run more than once and it will not disturb the hub
pages that already have the section.

Usage (from the repository root)::

    python tools/apply_sandbox_related_sections.py            # apply
    python tools/apply_sandbox_related_sections.py --dry-run  # preview
"""

from __future__ import annotations

import argparse
import os
from typing import Tuple

FRAMEWORK_ROOT = os.path.join('source', 'ROS-Framework')

SECTION_LINES = [
    'Related content',
    '---------------',
    '',
    'Related articles:',
    '',
    '.. ros-related-articles::',
    '',
    'Related packages:',
    '',
    '.. ros-related-packages::',
]


def already_has_section(text: str) -> bool:
    """True when the page already carries the related directives."""
    return '.. ros-related-articles::' in text or '.. ros-related-packages::' in text


def append_section(text: str) -> str:
    """Return ``text`` with the Related content section appended."""
    newline = '\r\n' if '\r\n' in text else '\n'
    body = text.rstrip('\r\n')
    block = newline.join(SECTION_LINES)
    return f'{body}{newline}{newline}{block}{newline}'


def iter_rst(root: str):
    """Yield every ``.rst`` path under ``root``."""
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            if name.endswith('.rst'):
                yield os.path.join(dirpath, name)


def process(root: str, dry_run: bool) -> Tuple[int, int]:
    """Append (or preview) the section across ``root``."""
    changed = 0
    skipped = 0
    for path in iter_rst(root):
        with open(path, 'r', encoding='utf-8') as handle:
            text = handle.read()

        if already_has_section(text):
            skipped += 1
            continue

        changed += 1
        print(os.path.relpath(path, root))
        if not dry_run:
            with open(path, 'w', encoding='utf-8', newline='') as handle:
                handle.write(append_section(text))

    return changed, skipped


def main() -> None:
    """Parse arguments and run the section insertion."""
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
    print(f'\n{verb} {changed} file(s); left {skipped} that already had the section.')


if __name__ == '__main__':
    main()
