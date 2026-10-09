#!/usr/bin/env python3
"""Validate the repository's Markdown structure and Python examples."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]

NUMBERED_TRACKS = {
    "AI-ML": ("AI-ML/aiml-chapter-{number}.md", 19),
    "DSA": ("DSA/dsa-chapter-{number}.md", 15),
    "HLD": ("HLD/hld-chapter-{number}.md", 16),
    "LLD": ("LLD/lld-chapter-{number}.md", 20),
    "Interview-Topics": (
        "Interview-Topics/interview-topics-chapter-{number}.md",
        10,
    ),
    "Behavioural": (
        "Behavioural/chapter-{number:02d}/behavioural-chapter-{number}.md",
        10,
    ),
}

FOUNDATIONS_CHAPTERS = {
    1: "Foundations/1-sql-and-databases/sql/ch1-sql.md",
    2: "Foundations/1-sql-and-databases/sql/ch2-sql.md",
    3: "Foundations/1-sql-and-databases/sql/ch3-sql.md",
    4: "Foundations/1-sql-and-databases/sql/ch4-sql.md",
    5: "Foundations/2-operating-systems/ch5-os.md",
    6: "Foundations/2-operating-systems/ch6-os.md",
    7: "Foundations/3-networking/ch7-networking.md",
    8: "Foundations/3-networking/ch8-networking.md",
    9: "Foundations/4-putting-it-together/ch9-concurrency.md",
    10: "Foundations/4-putting-it-together/ch10-python.md",
    11: "Foundations/4-putting-it-together/ch11-python-objects.md",
    12: "Foundations/4-putting-it-together/ch12-ritual.md",
    13: "Foundations/5-bonus/ch13-data-teams.md",
    14: "Foundations/5-bonus/ch14-git.md",
    15: "Foundations/6-distributed-systems/ch15-when-one-machine-becomes-many.md",
}

TRACK_READMES = {
    "LLD": "LLD/lld-README.md",
    "HLD": "HLD/hld-README.md",
    "DSA": "DSA/dsa-README.md",
    "Behavioural": "Behavioural/behavioural-README.md",
    "AI-ML": "AI-ML/aiml-README.md",
    "Foundations": "Foundations/foundations-README.md",
    "Interview-Topics": "Interview-Topics/interview-topics-README.md",
}

MARKDOWN_LINK = re.compile(r"!?\[[^\]]*]\(([^)]+)\)")
EXTERNAL_SCHEMES = ("http://", "https://", "mailto:")


def validate_chapters() -> list[str]:
    errors: list[str] = []

    for track, (pattern, count) in NUMBERED_TRACKS.items():
        for number in range(1, count + 1):
            relative_path = pattern.format(number=number)
            if not (ROOT / relative_path).is_file():
                errors.append(f"{track}: missing chapter {number}: {relative_path}")

    for number, relative_path in FOUNDATIONS_CHAPTERS.items():
        if not (ROOT / relative_path).is_file():
            errors.append(f"Foundations: missing chapter {number}: {relative_path}")

    return errors


def local_link_target(markdown_file: Path, raw_target: str) -> Path | None:
    target = raw_target.strip()
    if not target or target.startswith(("#", *EXTERNAL_SCHEMES)):
        return None

    if target.startswith("<") and ">" in target:
        target = target[1 : target.index(">")]
    else:
        target = target.split(maxsplit=1)[0]

    target = unquote(target.split("#", 1)[0])
    if not target:
        return None

    return (markdown_file.parent / target).resolve()


def validate_chapter_counts() -> list[str]:
    errors: list[str] = []
    expected_counts = {
        track: count for track, (_, count) in NUMBERED_TRACKS.items()
    }
    expected_counts["Foundations"] = len(FOUNDATIONS_CHAPTERS)

    for track, relative_path in TRACK_READMES.items():
        readme = ROOT / relative_path
        if not readme.is_file():
            errors.append(f"{track}: missing track README: {relative_path}")
            continue
        match = re.search(
            r"\b[Aa]n? (\d+)-chapter primer\b", readme.read_text(encoding="utf-8")
        )
        if match is None or int(match.group(1)) != expected_counts[track]:
            errors.append(
                f"{relative_path}: expected a {expected_counts[track]}-chapter "
                "primer declaration"
            )

    root_readme = ROOT / "README.md"
    if not root_readme.is_file():
        errors.append("missing root README.md")
        return errors
    count_row = next(
        (
            line
            for line in root_readme.read_text(encoding="utf-8").splitlines()
            if line.startswith("| Length |")
        ),
        "",
    )
    actual = [int(value) for value in re.findall(r"\b(\d+) ch\b", count_row)]
    expected = [expected_counts[track] for track in TRACK_READMES]
    if actual != expected:
        errors.append(f"README.md: chapter counts {actual} should be {expected}")

    return errors


def validate_markdown_links() -> list[str]:
    errors: list[str] = []

    for markdown_file in sorted(ROOT.rglob("*.md")):
        if ".git" in markdown_file.parts:
            continue

        content = markdown_file.read_text(encoding="utf-8")
        for line_number, line in enumerate(content.splitlines(), start=1):
            for match in MARKDOWN_LINK.finditer(line):
                target = local_link_target(markdown_file, match.group(1))
                if target is not None and not target.exists():
                    relative_file = markdown_file.relative_to(ROOT)
                    errors.append(
                        f"{relative_file}:{line_number}: broken local link "
                        f"{match.group(1)!r}"
                    )

    return errors


def validate_python_syntax() -> list[str]:
    errors: list[str] = []

    for python_file in sorted(ROOT.rglob("*.py")):
        if any(part in {".git", ".venv", "__pycache__"} for part in python_file.parts):
            continue

        relative_file = python_file.relative_to(ROOT)
        try:
            source = python_file.read_text(encoding="utf-8")
            compile(source, str(relative_file), "exec")
        except (SyntaxError, UnicodeError) as error:
            errors.append(f"{relative_file}: {error}")

    return errors


def main() -> int:
    checks = (
        ("chapter structure", validate_chapters),
        ("chapter counts", validate_chapter_counts),
        ("local Markdown links", validate_markdown_links),
        ("Python syntax", validate_python_syntax),
    )
    error_count = 0

    for name, check in checks:
        errors = check()
        if errors:
            error_count += len(errors)
            print(f"FAIL: {name}")
            for error in errors:
                print(f"  - {error}")
        else:
            print(f"PASS: {name}")

    if error_count:
        print(f"\nValidation failed with {error_count} error(s).")
        return 1

    print("\nContent validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
