# Copyright 2026 Open Robotics and contributors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Sphinx directive that lists allowed ``.. meta::`` values from ``enhance.yaml``.

Usage in RST::

    .. enhance-allowed:: area

The argument is a metadata field name from ``tools/enhance.yaml`` (for example
``area``, ``experience``, or ``content-type``). Field names match after
normalizing case and separators, so ``contentType`` and ``content-type`` are
the same field. The directive emits a bullet list of the configured
``allowed`` vocabulary for that field.
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml
from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.application import Sphinx
from sphinx.errors import ExtensionError

# Path to the Enhance checker vocabulary, relative to the directory that holds
# conf.py (the repository root). This is the same file ensure_enhancements.py
# reads, so the docs and the checker stay on one source of truth.
DEFAULT_ENHANCE_YAML = Path('tools') / 'enhance.yaml'


def _normalize_field_name(raw: str) -> str:
    """Normalize a metadata field name for comparison (case and separators)."""
    return ''.join(ch for ch in (raw or '').lower() if ch.isalnum())


def _load_enhance_yaml(path: Path) -> dict:
    """Load and return the enhance configuration mapping."""
    try:
        with path.open(encoding='utf-8') as handle:
            data = yaml.safe_load(handle)
    except OSError as exc:
        raise ExtensionError(
            f'enhance-allowed: could not read {path}: {exc}'
        ) from exc
    if not isinstance(data, dict):
        raise ExtensionError(f'enhance-allowed: {path} must be a mapping')
    return data


def _allowed_values_for_field(config: dict, field_name: str) -> list[str]:
    """Return the ``allowed`` list for *field_name* from the ``meta`` rules."""
    meta = config.get('meta')
    if not isinstance(meta, dict):
        raise ExtensionError('enhance-allowed: enhance.yaml has no `meta` mapping')

    wanted = _normalize_field_name(field_name)
    if not wanted:
        raise ExtensionError('enhance-allowed: a field name argument is required')

    for key, rule in meta.items():
        if _normalize_field_name(str(key)) != wanted:
            continue
        if not isinstance(rule, dict):
            raise ExtensionError(
                f'enhance-allowed: the `{key}` rule in enhance.yaml must be a mapping'
            )
        allowed = rule.get('allowed')
        if allowed is None:
            raise ExtensionError(
                f'enhance-allowed: the `{key}` field in enhance.yaml has no '
                '`allowed` values'
            )
        if not isinstance(allowed, list) or not all(
            isinstance(item, str) for item in allowed
        ):
            raise ExtensionError(
                f'enhance-allowed: the `allowed` values for `{key}` in '
                'enhance.yaml must be a list of strings'
            )
        return list(allowed)

    known = ', '.join(sorted(str(k) for k in meta))
    raise ExtensionError(
        f'enhance-allowed: unknown field `{field_name}` '
        f'(fields in enhance.yaml: {known})'
    )


class EnhanceAllowedDirective(Directive):
    """Emit a bullet list of allowed values for one enhance.yaml meta field."""

    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {}

    def run(self):
        env = self.state.document.settings.env

        # enhance.yaml sits next to conf.py (the repository root), not under the
        # source directory, so resolve it from confdir.
        yaml_path = (Path(env.app.confdir) / DEFAULT_ENHANCE_YAML).resolve()

        if not yaml_path.is_file():
            raise ExtensionError(
                f'enhance-allowed: {DEFAULT_ENHANCE_YAML.as_posix()} not found '
                f'(looked in {yaml_path})'
            )

        # Rebuild the page whenever enhance.yaml changes, so an edit to the
        # vocabulary shows up without a clean build.
        env.note_dependency(os.fspath(yaml_path))

        field_name = self.arguments[0].strip()
        config = _load_enhance_yaml(yaml_path)
        allowed = _allowed_values_for_field(config, field_name)

        # Each value is rendered as inline literal text so the vocabulary reads
        # as fixed tokens rather than prose.
        bullet_list = nodes.bullet_list()
        for value in allowed:
            item = nodes.list_item()
            paragraph = nodes.paragraph()
            paragraph += nodes.literal(value, value)
            item += paragraph
            bullet_list += item

        return [bullet_list]


def setup(app: Sphinx) -> dict:
    """Register the ``enhance-allowed`` directive with Sphinx."""
    app.add_directive('enhance-allowed', EnhanceAllowedDirective)
    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
