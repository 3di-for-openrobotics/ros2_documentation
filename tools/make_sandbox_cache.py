#!/usr/bin/env python3
"""Sandbox helper: inject ``<area>`` and ``<related_scope>`` into the rosdistro cache.

Rewrites the gzipped cache so curated packages carry the metadata related-
packages lists expect:

  * ``<area>`` aligned with sandbox article areas (containment match on the
    page's primary area value)
  * ``<related_scope>core</related_scope>`` or ``federation`` for the Core /
    Community split

Typical flow (from the repository root)::

    make html
    python tools/make_sandbox_cache.py
    python -m http.server -d build/html 8000
"""

from __future__ import annotations

import argparse
import gzip
import os
import re
import sys
import urllib.request

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit('PyYAML is required. Install it in the docs environment: pip install pyyaml')

ROSDISTRO_CACHE_TEMPLATE = (
    'https://repo.ros2.org/rosdistro_cache/{distro}-cache.yaml.gz'
)

# name -> (area chain, related_scope)
PACKAGE_META = {
    # Core — nodes (enough for Show N more)
    'rclcpp': ('nodes, framework', 'core'),
    'rclpy': ('nodes, framework', 'core'),
    'rclcpp_components': ('nodes, framework', 'core'),
    'rclcpp_lifecycle': ('nodes, framework', 'core'),
    'rcl_lifecycle': ('nodes, framework', 'core'),
    'composition': ('nodes, framework', 'core'),
    'libstatistics_collector': ('nodes, framework', 'core'),
    'rcl_logging_interface': ('nodes, framework', 'core'),
    'rcl_logging_spdlog': ('nodes, framework', 'core'),
    'rosgraph_msgs': ('nodes, framework', 'core'),
    'tracetools': ('nodes, framework', 'core'),
    'launch': ('nodes, framework', 'core'),
    'launch_ros': ('nodes, framework', 'core'),
    'lifecycle_msgs': ('nodes, framework', 'core'),
    # Federation — nodes (showcase the second list; names must exist in the cache)
    'moveit_ros_planning_interface': ('nodes, framework', 'federation'),
    'joint_state_publisher': ('nodes, framework', 'federation'),
    'robot_state_publisher': ('nodes, framework', 'federation'),
    'xacro': ('nodes, framework', 'federation'),
    'demo_nodes_cpp': ('nodes, framework', 'federation'),
    'demo_nodes_py': ('nodes, framework', 'federation'),
    # parameters
    'rcl_yaml_param_parser': ('parameters, framework', 'core'),
    'rcl_interfaces': ('parameters, framework', 'core'),
    'generate_parameter_library': ('parameters, framework', 'core'),
    # client-libraries
    'rcl': ('client-libraries, framework', 'core'),
    'rclc': ('client-libraries, framework', 'core'),
    'rcpputils': ('client-libraries, framework', 'core'),
    'rcutils': ('client-libraries, framework', 'core'),
    # topics
    'std_msgs': ('topics, interfaces, framework', 'core'),
    'geometry_msgs': ('topics, interfaces, framework', 'core'),
    'sensor_msgs': ('topics, interfaces, framework', 'core'),
    'rmw': ('topics, interfaces, framework', 'core'),
    # services
    'std_srvs': ('services, interfaces, framework', 'core'),
    'example_interfaces': ('services, interfaces, framework', 'core'),
    # actions
    'action_msgs': ('actions, interfaces, framework', 'core'),
    'rclcpp_action': ('actions, interfaces, framework', 'core'),
    'action_tutorials_cpp': ('actions, interfaces, framework', 'core'),
    'action_tutorials_py': ('actions, interfaces, framework', 'core'),
}


def _upsert_export_tag(xml: str, tag_name: str, value: str) -> str:
    """Set ``<tag_name>value</tag_name>`` inside ``<export>`` (or create export)."""
    tag = f'<{tag_name}>{value}</{tag_name}>'
    pattern = rf'<{tag_name}\b[^>]*>.*?</{tag_name}>'
    if re.search(pattern, xml, flags=re.S):
        return re.sub(pattern, tag, xml, count=1, flags=re.S)
    if '</export>' in xml:
        return xml.replace('</export>', f'    {tag}\n  </export>', 1)
    if '</package>' in xml:
        return xml.replace(
            '</package>',
            f'  <export>\n    {tag}\n  </export>\n</package>',
            1,
        )
    return xml + f'\n  <export>\n    {tag}\n  </export>\n'


def inject_package_meta(xml: str, area: str, scope: str) -> str:
    """Return ``xml`` with area and related_scope export tags set."""
    xml = _upsert_export_tag(xml, 'area', area)
    xml = _upsert_export_tag(xml, 'related_scope', scope)
    return xml


def default_input(distro: str) -> str:
    """Pick the built cache if present, else the bundled source cache."""
    name = f'{distro}-cache.yaml.gz'
    built = os.path.join('build', 'html', '_static', 'rosdistro_cache', name)
    source = os.path.join('source', '_static', 'rosdistro_cache', name)
    if os.path.exists(built):
        return built
    return source


def load_cache(path: str, distro: str, allow_download: bool) -> bytes:
    """Return the gzipped cache bytes, downloading them if requested."""
    if os.path.exists(path):
        with open(path, 'rb') as handle:
            return handle.read()
    if not allow_download:
        raise SystemExit(
            f'Cache not found at {path}. Run `make html` first, or pass --download.'
        )
    url = ROSDISTRO_CACHE_TEMPLATE.format(distro=distro)
    print(f'Downloading {url}')
    request = urllib.request.Request(url, headers={'User-Agent': 'sandbox-cache/1.0'})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read()


def main() -> None:
    """Rewrite the rosdistro cache with sandbox area and scope exports."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--distro', default='rolling')
    parser.add_argument('--input')
    parser.add_argument('--output')
    parser.add_argument('--download', action='store_true')
    args = parser.parse_args()

    in_path = args.input or default_input(args.distro)
    out_path = args.output or in_path

    raw = load_cache(in_path, args.distro, args.download)
    data = yaml.safe_load(gzip.decompress(raw))

    xmls = data.get('release_package_xmls') if isinstance(data, dict) else None
    if not isinstance(xmls, dict):
        raise SystemExit('release_package_xmls not found in the cache; unexpected format.')

    matched = []
    missing = []
    for name, (area, scope) in PACKAGE_META.items():
        if name in xmls and isinstance(xmls[name], str):
            xmls[name] = inject_package_meta(xmls[name], area, scope)
            matched.append(f'{name}[{scope}]')
        else:
            missing.append(name)

    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    with gzip.open(out_path, 'wb') as handle:
        handle.write(yaml.safe_dump(data, allow_unicode=True).encode('utf-8'))

    print(f'Read : {in_path}')
    print(f'Wrote: {out_path}')
    print(f'Injected metadata into {len(matched)} package(s): {", ".join(sorted(matched))}')
    if missing:
        print(f'Not in this cache (skipped): {", ".join(sorted(missing))}')


if __name__ == '__main__':
    main()
