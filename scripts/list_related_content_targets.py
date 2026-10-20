#!/usr/bin/env python3
"""List source/*.rst targets for Related-content bulk updates.

Includes docs under source/, excluding underscore path components
(_internal, _static, _templates, etc.) and stakeholder exceptions.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "source"
OUT_DIR = Path(__file__).resolve().parent

# URL path after /en/rolling/ (or bare site root mapped to index)
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


def main() -> int:
    all_rst = sorted(p for p in ROOT.rglob("*.rst") if p.is_file())
    skipped = [p for p in all_rst if is_underscore_path(p)]
    content_rst = [p for p in all_rst if not is_underscore_path(p)]

    print("=== SCAN SUMMARY ===")
    print(f"Total .rst under source/: {len(all_rst)}")
    print(f"Skipped underscore paths: {len(skipped)}")
    for path in skipped:
        print(f"  skip: {path.relative_to(ROOT).as_posix()}")
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

    print("\n=== CONFIRM SPECIAL: About capabilities ===")
    special_cap: set[Path] = set()
    for url in SPECIAL_CAPABILITIES:
        rel = url_to_rel(url)
        path = find_rst(rel, content_rst)
        if path:
            special_cap.add(path.resolve())
            print(f"OK       {rel}")
        else:
            missing.append(rel)
            print(f"MISSING  {rel}")

    print("\n=== CONFIRM SPECIAL: WiP About articles ===")
    special_wip: set[Path] = set()
    for url in SPECIAL_WIP_ABOUT:
        rel = url_to_rel(url)
        path = find_rst(rel, content_rst)
        if path:
            special_wip.add(path.resolve())
            print(f"OK       {rel}")
        else:
            missing.append(rel)
            print(f"MISSING  {rel}")

    bulk_exclude = exclude_files | special_cap | special_wip
    to_update = sorted(
        (p for p in content_rst if p.resolve() not in bulk_exclude),
        key=lambda p: p.relative_to(ROOT).as_posix().lower(),
    )

    named_excludes = sorted(
        (
            p
            for p in exclude_files
            if p.relative_to(ROOT).parts[0] != "Releases"
        ),
        key=lambda p: p.relative_to(ROOT).as_posix().lower(),
    )

    print("\n=== COUNTS ===")
    print(f"Named full exclusions found: {len(named_excludes)}")
    print(f"Releases/ tree: {len(releases_files)}")
    print(f"Special capabilities: {len(special_cap)}")
    print(f"Special WiP About: {len(special_wip)}")
    print(f"TO UPDATE (standard bulk): {len(to_update)}")
    print(f"Missing exception paths: {len(missing)}")

    out_update = OUT_DIR / "related_content_to_update.txt"
    out_exceptions = OUT_DIR / "related_content_exceptions.txt"

    with out_update.open("w", encoding="utf-8") as fh:
        fh.write("# Standard bulk Related-content TO UPDATE\n")
        fh.write(
            "# source/**/*.rst minus _* paths, Releases/, named exclusions, "
            "and special-case pages\n"
        )
        fh.write(f"# Count: {len(to_update)}\n\n")
        for path in to_update:
            fh.write(path.relative_to(ROOT).as_posix() + "\n")

    with out_exceptions.open("w", encoding="utf-8") as fh:
        fh.write("# Confirmed exclusions / special cases (NOT in bulk TO UPDATE)\n\n")
        fh.write("## Full exclusion (no Related content) — named pages\n")
        for url in FULL_EXCLUDE_URLS:
            rel = url_to_rel(url)
            path = find_rst(rel, content_rst)
            status = "FOUND" if path else "MISSING"
            fh.write(f"{status}\t{rel}\n")
        fh.write(
            f"\n## Full exclusion — entire Releases/ tree "
            f"({len(releases_files)} files)\n"
        )
        for path in sorted(
            releases_files, key=lambda p: p.relative_to(ROOT).as_posix().lower()
        ):
            fh.write(path.relative_to(ROOT).as_posix() + "\n")
        fh.write(
            "\n## Special case — About capabilities "
            "(Community-contributed packages + Related articles only)\n"
        )
        for url in SPECIAL_CAPABILITIES:
            rel = url_to_rel(url)
            path = find_rst(rel, content_rst)
            status = "FOUND" if path else "MISSING"
            fh.write(f"{status}\t{rel}\n")
        fh.write("\n## Special case — WiP About articles (depends on OR PRs)\n")
        for url in SPECIAL_WIP_ABOUT:
            rel = url_to_rel(url)
            path = find_rst(rel, content_rst)
            status = "FOUND" if path else "MISSING"
            fh.write(f"{status}\t{rel}\n")

    print(f"\nWrote {out_update}")
    print(f"Wrote {out_exceptions}")
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
