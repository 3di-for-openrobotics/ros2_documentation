#!/usr/bin/env python3
"""Sandbox helper: append a Related content section to ROS-Framework pages.

Adds the following block at the end of every ``.rst`` page under
``source/ROS-Framework`` that does not already contain
``ros-related-articles``::

    Related content
    ---------------

    Related articles:

    .. ros-related-articles::

    Related packages:

    .. ros-related-packages::

Idempotent. Meant only for the ``dynamic-lists-sandbox`` branch.

Usage (from the repository root)::

    python tools/apply_sandbox_related_content.py
    python tools/apply_sandbox_related_content.py --dry-run
"""

from __future__ import annotations

import argparse
import os

FRAMEWORK_ROOT = os.path.join('source', 'ROS-Framework')

SECTION = """\
Related content
---------------

Related articles:

.. ros-related-articles::

Related packages:

.. ros-related-packages::
"""


def iter_rst(root: str):
    """Yield every ``.rst`` path under ``root``."""
    for dirpath, _dirs, files in os.walk(root):
        for name in files:
            if name.endswith('.rst'):
                yield os.path.join(dirpath, name)


def process(root: str, dry_run: bool) -> tuple[int, int]:
    """Append the section where missing."""
    changed = 0
    skipped = 0
    for path in iter_rst(root):
        with open(path, 'r', encoding='utf-8') as handle:
            text = handle.read()

        if 'ros-related-articles' in text:
            skipped += 1
            continue

        newline = '\r\n' if '\r\n' in text else '\n'
        body = text.rstrip()
        block = SECTION.replace('\n', newline)
        updated = body + newline + newline + block
        if not updated.endswith(newline):
            updated += newline

        rel = os.path.relpath(path, root)
        print(f'[related content] {rel}')
        changed += 1
        if not dry_run:
            with open(path, 'w', encoding='utf-8', newline='') as handle:
                handle.write(updated)

    return changed, skipped


def main() -> None:
    """Parse arguments and run."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', default=FRAMEWORK_ROOT)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    if not os.path.isdir(args.root):
        raise SystemExit(f'Not a directory: {args.root} (run from the repo root)')

    changed, skipped = process(args.root, args.dry_run)
    verb = 'Would update' if args.dry_run else 'Updated'
    print(f'\n{verb} {changed} file(s); left {skipped} already with the section.')


if __name__ == '__main__':
    main()
