"""Regression tests for chapter coverage and declared curriculum counts."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import validate_content


class ChapterValidationTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        root_patch = patch.object(validate_content, "ROOT", self.root)
        root_patch.start()
        self.addCleanup(root_patch.stop)
        counts = {}
        for track, (pattern, count) in validate_content.NUMBERED_TRACKS.items():
            counts[track] = count
            for number in range(1, count + 1):
                self.write(pattern.format(number=number), "# Chapter\n")
        counts["Foundations"] = len(validate_content.FOUNDATIONS_CHAPTERS)
        for path in validate_content.FOUNDATIONS_CHAPTERS.values():
            self.write(path, "# Chapter\n")
        for track, path in validate_content.TRACK_READMES.items():
            self.write(path, f"A {counts[track]}-chapter primer.\n")
        self.write(
            "README.md",
            "| Length | "
            + " | ".join(
                f"{counts[track]} ch + appendix"
                for track in validate_content.TRACK_READMES
            )
            + " |\n",
        )

    def write(self, relative_path, content):
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def test_complete_curriculum_passes(self):
        self.assertEqual(validate_content.validate_chapters(), [])
        self.assertEqual(validate_content.validate_chapter_counts(), [])

    def test_new_chapters_are_required(self):
        for relative_path in (
            "AI-ML/aiml-chapter-19.md",
            "Interview-Topics/interview-topics-chapter-10.md",
            "Foundations/6-distributed-systems/ch15-when-one-machine-becomes-many.md",
        ):
            with self.subTest(path=relative_path):
                (self.root / relative_path).unlink()
                errors = validate_content.validate_chapters()
                self.assertEqual(len(errors), 1)
                self.assertIn(relative_path, errors[0])
                self.write(relative_path, "# Chapter\n")

    def test_stale_track_count_fails(self):
        self.write("AI-ML/aiml-README.md", "An 18-chapter primer.\n")
        errors = validate_content.validate_chapter_counts()
        self.assertEqual(len(errors), 1)
        self.assertIn("19-chapter", errors[0])

    def test_stale_root_count_fails(self):
        path = self.root / "README.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace("19 ch", "18 ch"),
            encoding="utf-8",
        )
        errors = validate_content.validate_chapter_counts()
        self.assertEqual(len(errors), 1)
        self.assertIn("README.md", errors[0])

    def test_missing_count_row_fails(self):
        self.write("README.md", "# Contents\n")
        self.assertEqual(len(validate_content.validate_chapter_counts()), 1)

    def test_missing_track_readme_fails(self):
        (self.root / "AI-ML/aiml-README.md").unlink()
        errors = validate_content.validate_chapter_counts()
        self.assertEqual(len(errors), 1)
        self.assertIn("missing track README", errors[0])

    def test_main_returns_failure_for_invalid_curriculum(self):
        (self.root / "AI-ML/aiml-chapter-19.md").unlink()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(validate_content.main(), 1)
        self.assertIn("FAIL: chapter structure", output.getvalue())
        self.assertIn("aiml-chapter-19.md", output.getvalue())


if __name__ == "__main__":
    unittest.main()
