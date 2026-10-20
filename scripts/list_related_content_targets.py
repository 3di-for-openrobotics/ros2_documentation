#!/usr/bin/env python3
"""List source/*.rst targets for Related-content bulk updates.

Includes docs under source/, excluding underscore path components
(_internal, _static, _templates, etc.) and stakeholder exceptions.

WiP About distinguisher:
  If the page still has a live \"Coming Soon\" line (+ typically a toctree),
  exclude it from this ticket. If Coming Soon is gone, treat like
  Capabilities/About… (special append of Related content > Related articles).
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "source"
OUT_DIR = Path(__file__).resolve().parent

FULL_EXCLUDE_URLS = [
    "Releases.html",
    "About-ROS.html",
    "index.html",
    "Contributing-To-ROS.html",
    "Citations.html",
    "Contact.html",
    "The-ROS2-Project.html",
    "Migration-and-Upgrades.html",
    "Integrations-and-related.html",
    "Capabilities.html",
    "Developer-Tools.html",
    "ROS-Framework.html",
    "Get-Started.html",
    "Developer-Tools/Visualization/RViz/RViz-Main.html",
    "ROS-Framework/client-libraries/Working-with-Client-Libraries.html",
]

SPECIAL_CAPABILITIES = [
    "Capabilities/About-Simulation.html",
    "Capabilities/About-Motion-planning.html",
    "Capabilities/About-Navigation.html",
    "Capabilities/About-Perception.html",
]

SPECIAL_WIP_ABOUT = [
    "Developer-Tools/About-introspection-and-analysis.html",
    "Developer-Tools/About-Launch.html",
    "Developer-Tools/About-Debugging.html",
    "Developer-Tools/About-Build.html",
    "Developer-Tools/About-visualization.html",
    "Developer-Tools/About-package-documentation.html",
]

COMING_SOON_RE = re.compile(r"(?im)^Coming Soon\s*$")
RELATED_DIR_RE = re.compile(r"(?m)^\.\.\s*ros-related-articles::\s*$")


def url_to_rel(url: str) -> str:
    u = url.split("#", 1)[0]
    if u.endswith(".html"):
        u = u[: -len(".html")]
    if u in {"", "index"}:
        return "index.rst"
    return f"{u}.rst"


def is_underscore_path(path: Path) -> bool:
    return any(part.startswith("_") for part in path.relative_to(ROOT).parts)


def find_rst(rel_rst: str, content_rst: list[Path]) -> Path | None:
    direct = ROOT / rel_rst
    if direct.is_file():
        return direct
    needle = rel_rst.lower()
    for path in content_rst:
        if path.relative_to(ROOT).as_posix().lower() == needle:
            return path
    return None


def has_coming_soon(path: Path) -> bool:
    return bool(COMING_SOON_RE.search(path.read_text(encoding="utf-8")))


def write_list(path: Path, header_lines: list[str], files: list[str]) -> None:
    body = header_lines + [""] + files + [""]
    path.write_text("\n".join(body), encoding="utf-8")


def main() -> int:
    all_rst = sorted(p for p in ROOT.rglob("*.rst") if p.is_file())
    skipped = [p for p in all_rst if is_underscore_path(p)]
    content_rst = [p for p in all_rst if not is_underscore_path(p)]

    print("=== SCAN SUMMARY ===")
    print(f"Total .rst under source/: {len(all_rst)}")
    print(f"Skipped underscore paths: {len(skipped)}")
    print(f"Candidate content .rst: {len(content_rst)}")

    exclude_files: set[Path] = set()
    missing: list[str] = []

    print("\n=== CONFIRM FULL EXCLUSIONS (no Related content) ===")
    for url in FULL_EXCLUDE_URLS:
        rel = url_to_rel(url)
        path = find_rst(rel, content_rst)
        if path:
            exclude_files.add(path.resolve())
            print(f"OK       {rel}")
        else:
            missing.append(rel)
            print(f"MISSING  {rel}")

    releases_files = [
        p for p in content_rst if p.relative_to(ROOT).parts[0] == "Releases"
    ]
    for path in releases_files:
        exclude_files.add(path.resolve())
    print(f"\n=== Releases/ tree excluded: {len(releases_files)} files ===")

    print("\n=== SPECIAL: About capabilities (always special) ===")
    special_cap: list[str] = []
    special_cap_paths: set[Path] = set()
    for url in SPECIAL_CAPABILITIES:
        rel = url_to_rel(url)
        path = find_rst(rel, content_rst)
        if path:
            special_cap_paths.add(path.resolve())
            special_cap.append(rel)
            coming = has_coming_soon(path)
            print(f"OK       {rel}  ComingSoon={coming}")
        else:
            missing.append(rel)
            print(f"MISSING  {rel}")

    print("\n=== SPECIAL: WiP About (Coming Soon distinguisher) ===")
    wip_exclude: list[str] = []
    wip_treat_like_cap: list[str] = []
    wip_paths: set[Path] = set()
    for url in SPECIAL_WIP_ABOUT:
        rel = url_to_rel(url)
        path = find_rst(rel, content_rst)
        if not path:
            missing.append(rel)
            print(f"MISSING  {rel}")
            continue
        wip_paths.add(path.resolve())
        if has_coming_soon(path):
            wip_exclude.append(rel)
            print(f"EXCLUDE  {rel}  (has Coming Soon — old / ignore this ticket)")
        else:
            wip_treat_like_cap.append(rel)
            print(f"SPECIAL  {rel}  (no Coming Soon — treat like Capabilities/About)")

    # Over-appended: still Coming Soon but already has related directive
    over_appended: list[str] = []
    for path in content_rst:
        text = path.read_text(encoding="utf-8")
        if COMING_SOON_RE.search(text) and RELATED_DIR_RE.search(text):
            over_appended.append(path.relative_to(ROOT).as_posix())

    bulk_exclude = exclude_files | special_cap_paths | wip_paths
    to_update = sorted(
        (p for p in content_rst if p.resolve() not in bulk_exclude),
        key=lambda p: p.relative_to(ROOT).as_posix().lower(),
    )

    print("\n=== COUNTS ===")
    print(f"Named full exclusions: {len([p for p in exclude_files if p.relative_to(ROOT).parts[0] != 'Releases'])}")
    print(f"Releases/ tree: {len(releases_files)}")
    print(f"Special capabilities: {len(special_cap)}")
    print(f"WiP exclude (Coming Soon): {len(wip_exclude)}")
    print(f"WiP treat like capabilities: {len(wip_treat_like_cap)}")
    print(f"TO UPDATE (standard bulk): {len(to_update)}")
    print(f"Over-appended with Coming Soon still present: {len(over_appended)}")
    print(f"Missing exception paths: {len(missing)}")

    write_list(
        OUT_DIR / "related_content_to_update.txt",
        [
            "# Standard bulk Related-content TO UPDATE",
            "# source/**/*.rst minus _* paths, Releases/, named exclusions,",
            "# Capabilities/About specials, and all WiP About pages (whether",
            "# Coming Soon exclude or treat-like-capabilities special).",
            f"# Count: {len(to_update)}",
        ],
        [p.relative_to(ROOT).as_posix() for p in to_update],
    )

    # exceptions file
    exc_lines = [
        "# Confirmed exclusions / special cases (NOT in bulk TO UPDATE)",
        "",
        "## Full exclusion (no Related content) — named pages",
    ]
    for url in FULL_EXCLUDE_URLS:
        rel = url_to_rel(url)
        path = find_rst(rel, content_rst)
        exc_lines.append(f"{'FOUND' if path else 'MISSING'}\t{rel}")
    exc_lines.append(
        f"\n## Full exclusion — entire Releases/ tree ({len(releases_files)} files)"
    )
    for path in sorted(
        releases_files, key=lambda p: p.relative_to(ROOT).as_posix().lower()
    ):
        exc_lines.append(path.relative_to(ROOT).as_posix())

    exc_lines.append(
        "\n## Special case — About capabilities "
        "(after Community-contributed packages: Related content > Related articles; "
        "no Related packages)"
    )
    for rel in special_cap:
        path = ROOT / rel
        flag = " ComingSoon=yes" if path.is_file() and has_coming_soon(path) else ""
        exc_lines.append(f"FOUND\t{rel}{flag}")

    exc_lines.append(
        "\n## WiP About — EXCLUDE this ticket (still has Coming Soon)"
    )
    for rel in wip_exclude:
        exc_lines.append(f"EXCLUDE\t{rel}")

    exc_lines.append(
        "\n## WiP About — TREAT like Capabilities/About "
        "(Coming Soon gone; append Related content > Related articles at end)"
    )
    for rel in wip_treat_like_cap:
        exc_lines.append(f"SPECIAL\t{rel}")

    exc_lines.append(
        "\n## Possibly over-appended "
        "(still has Coming Soon AND already has .. ros-related-articles::)"
    )
    if over_appended:
        for rel in over_appended:
            exc_lines.append(rel)
    else:
        exc_lines.append("(none)")
    exc_lines.append("")

    (OUT_DIR / "related_content_exceptions.txt").write_text(
        "\n".join(exc_lines), encoding="utf-8"
    )

    write_list(
        OUT_DIR / "related_content_special_capabilities.txt",
        [
            "# Special: Capabilities/About…",
            "# After Community-contributed packages, add Related content > Related articles.",
            "# No Related packages.",
            f"# Count: {len(special_cap)}",
        ],
        special_cap,
    )
    write_list(
        OUT_DIR / "related_content_wip_exclude_coming_soon.txt",
        [
            "# WiP About — EXCLUDE (old: Coming Soon + typically toctree)",
            f"# Count: {len(wip_exclude)}",
        ],
        wip_exclude,
    )
    write_list(
        OUT_DIR / "related_content_wip_treat_like_capabilities.txt",
        [
            "# WiP About — TREAT like Capabilities/About (Coming Soon removed)",
            "# Append Related content > Related articles at end of page.",
            f"# Count: {len(wip_treat_like_cap)}",
        ],
        wip_treat_like_cap,
    )
    write_list(
        OUT_DIR / "related_content_over_appended_coming_soon.txt",
        [
            "# Review/revert candidates: Coming Soon still present, but Related directive already added",
            f"# Count: {len(over_appended)}",
        ],
        over_appended,
    )

    print(f"\nWrote lists under {OUT_DIR}")
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
