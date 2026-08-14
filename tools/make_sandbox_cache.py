#!/usr/bin/env python3
"""Sandbox helper: inject ``<area>`` exports into the rosdistro cache.

The related package lists match a page's primary ``area`` against the
``<area>`` export inside each package's ``package.xml``. No package in the
real rosdistro cache carries that export yet, so the lists render empty. This
script rewrites a copy of the cache so a curated set of well known core
packages gain an ``<area>`` that lines up with the sandbox article areas. That
is enough to see the package lists populate end to end.

It only touches the gzipped cache blob (never the plugin or the JavaScript), so
the runtime code under test stays exactly as it ships.

Typical flow (from the repository root)::

    make html                                   # downloads the real cache
    python tools/make_sandbox_cache.py          # rewrites the built copy
    python -m http.server -d build/html 8000    # serve without the proxy

Serving with a plain HTTP server (not the proxy) matters: the proxy would fetch
the untouched upstream cache, so the injected areas would not be seen. Without
the proxy the widget falls back to the bundled cache we just rewrote.
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
except ImportError:  # pragma: no cover - guidance only
    sys.exit('PyYAML is required. Install it in the docs environment: pip install pyyaml')

ROSDISTRO_CACHE_TEMPLATE = (
    'https://repo.ros2.org/rosdistro_cache/{distro}-cache.yaml.gz'
)

# Curated core packages mapped to a sandbox area chain (most specific first).
# The first value is what the package lists actually match on.
AREA_MAP = {
    # nodes (more than 7 so the sandbox can exercise the Show N more control)
    'rclcpp': 'nodes, framework',
    'rclpy': 'nodes, framework',
    'rclcpp_components': 'nodes, framework',
    'rclcpp_lifecycle': 'nodes, framework',
    'rcl_lifecycle': 'nodes, framework',
    'composition': 'nodes, framework',
    'libstatistics_collector': 'nodes, framework',
    'rcl_logging_interface': 'nodes, framework',
    'rcl_logging_spdlog': 'nodes, framework',
    'rosgraph_msgs': 'nodes, framework',
    'tracetools': 'nodes, framework',
    'launch': 'nodes, framework',
    'launch_ros': 'nodes, framework',
    'lifecycle_msgs': 'nodes, framework',

    # parameters
    'rcl_yaml_param_parser': 'parameters, framework',
    'rcl_interfaces': 'parameters, framework',
    'generate_parameter_library': 'parameters, framework',
    # client-libraries
    'rcl': 'client-libraries, framework',
    'rclc': 'client-libraries, framework',
    'rcpputils': 'client-libraries, framework',
    'rcutils': 'client-libraries, framework',
    # topics
    'std_msgs': 'topics, interfaces, framework',
    'geometry_msgs': 'topics, interfaces, framework',
    'sensor_msgs': 'topics, interfaces, framework',
    'rmw': 'topics, interfaces, framework',
    # services
    'std_srvs': 'services, interfaces, framework',
    'example_interfaces': 'services, interfaces, framework',
    # actions
    'action_msgs': 'actions, interfaces, framework',
    'rclcpp_action': 'actions, interfaces, framework',
    'action_tutorials_cpp': 'actions, interfaces, framework',
    'action_tutorials_py': 'actions, interfaces, framework',
}


def inject_area(xml: str, area: str) -> str:
    """Return ``xml`` with an ``<area>`` export set to ``area``."""
    tag = f'<area>{area}</area>'
    if re.search(r'<area\b', xml):
        return re.sub(r'<area\b[^>]*>.*?</area>', tag, xml, count=1, flags=re.S)
    if '</export>' in xml:
        return xml.replace('</export>', f'    {tag}\n  </export>', 1)
    if '</package>' in xml:
        return xml.replace(
            '</package>', f'  <export>\n    {tag}\n  </export>\n</package>', 1
        )
    return xml + f'\n  <export>\n    {tag}\n  </export>\n'


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
    """Rewrite the rosdistro cache with sandbox ``<area>`` exports."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--distro', default='rolling', help='ROS distro (default: rolling).')
    parser.add_argument('--input', help='Cache gz to read (default: built, then source).')
    parser.add_argument('--output', help='Cache gz to write (default: same as input).')
    parser.add_argument(
        '--download',
        action='store_true',
        help='Download the cache from repo.ros2.org if it is not on disk.',
    )
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
    for name, area in AREA_MAP.items():
        if name in xmls and isinstance(xmls[name], str):
            xmls[name] = inject_area(xmls[name], area)
            matched.append(name)
        else:
            missing.append(name)

    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
    with gzip.open(out_path, 'wb') as handle:
        handle.write(yaml.safe_dump(data, allow_unicode=True).encode('utf-8'))

    print(f'Read : {in_path}')
    print(f'Wrote: {out_path}')
    print(f'Injected <area> into {len(matched)} package(s): {", ".join(sorted(matched))}')
    if missing:
        print(f'Not in this cache (skipped): {", ".join(sorted(missing))}')


if __name__ == '__main__':
    main()
