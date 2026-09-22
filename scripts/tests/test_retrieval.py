"""Retrieval boundaries and bounded Unicode output, using synthetic notes only."""

from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build_catalog
from public_paths import public_note_path
import search


class RetrievalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "knowledge/canon").mkdir(parents=True)

    def note(self, body, relative="knowledge/canon/example.md", title="Example", kind="canon"):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        entry = {"path": relative, "title": title, "kind": kind, "words": len(body.split())}
        (self.root / "knowledge/catalog.json").write_text(
            json.dumps({"documents": [entry]}, ensure_ascii=False), encoding="utf-8")
        return path

    def run_search(self, query, max_chars=80):
        with patch.object(search, "ROOT", self.root):
            return search.search(query, "canon", 1, max_chars)

    def test_unbroken_word_respects_exact_excerpt_limit(self):
        word = "needle" + "x" * 200
        self.note(word)
        excerpt = self.run_search(word)[0]["excerpt"]
        self.assertEqual(len(excerpt), 80)
        self.assertTrue(excerpt.endswith("…"))

    def test_word_boundary_excerpt_stays_bounded(self):
        self.note("needle " + "a useful finding " * 30)
        excerpt = self.run_search("needle")[0]["excerpt"]
        self.assertLessEqual(len(excerpt), 80)
        self.assertTrue(excerpt.endswith("…"))

    def test_exact_length_excerpt_is_not_truncated(self):
        word = "n" * 80
        self.note(word)
        self.assertEqual(self.run_search(word)[0]["excerpt"], word)

    def test_excerpt_contains_evidence_instead_of_repeating_title(self):
        self.note("# Support\n\nSupport drafts require approval before sending.", title="Support")
        excerpt = self.run_search("support")[0]["excerpt"]
        self.assertEqual(excerpt, "Support drafts require approval before sending.")

    def test_private_metadata_catalog_entry_is_rejected(self):
        self.note("needle synthetic fixture", "knowledge/_meta/private-fixture.txt")
        with self.assertRaisesRegex(ValueError, "published"):
            self.run_search("needle")

    def test_raw_capture_catalog_entry_is_rejected(self):
        # No source directory is created or opened, even for this fixture.
        with self.assertRaisesRegex(ValueError, "published"):
            public_note_path(self.root, "knowledge/sources/01/transcript.md", kind="canon")

    def test_traversal_and_kind_mismatch_are_rejected(self):
        self.note("needle")
        for relative, kind in [
            ("knowledge/canon/../_meta/private.md", "canon"),
            ("knowledge/canon/example.md", "session"),
            ("knowledge/canon/transcript.md", "canon"),
            ("knowledge\\canon\\example.md", "canon"),
        ]:
            with self.subTest(relative=relative), self.assertRaises(ValueError):
                public_note_path(self.root, relative, kind=kind)

    def test_resolved_outside_path_is_rejected_without_opening_it(self):
        candidate = self.note("needle")
        original_resolve = Path.resolve

        def resolve(path, *args, **kwargs):
            if path == candidate:
                return self.root.parent / "outside-fixture.md"
            return original_resolve(path, *args, **kwargs)

        with patch.object(Path, "resolve", resolve), self.assertRaisesRegex(ValueError, "outside"):
            public_note_path(self.root, "knowledge/canon/example.md", kind="canon")

    def test_catalog_rejects_symlink_flag_before_reading_contents(self):
        candidate = self.note("# Synthetic private fixture title")
        original_is_symlink = Path.is_symlink

        def is_symlink(path):
            return path == candidate or original_is_symlink(path)

        with patch.object(build_catalog, "ROOT", self.root), \
             patch.object(Path, "is_symlink", is_symlink), \
             patch.object(Path, "read_text", side_effect=AssertionError("must not read")), \
             self.assertRaisesRegex(ValueError, "symlinks"):
            build_catalog.records()

    def test_catalog_keeps_speaker_metadata(self):
        timeline = self.root / "knowledge/timelines/065.md"
        timeline.parent.mkdir()
        timeline.write_text(
            '---\nclip: "065"\nday: "2026-09-16"\nmodule: sales-engineering\n'
            'duration: "00:01:00"\nspeakers: ["Amrita", "Audience"]\n---\n', encoding="utf-8")
        with patch.object(build_catalog, "ROOT", self.root):
            records = build_catalog.records()
        self.assertEqual(records[0]["speakers"], ["Amrita", "Audience"])

    def test_spanish_json_roundtrip_with_captured_stdout(self):
        self.note("Soporte → español: guía útil.", title="Guía de soporte")
        output = io.StringIO()
        with patch.object(search, "ROOT", self.root), \
             patch.object(sys, "argv", ["search.py", "soporte", "--json"]), \
             redirect_stdout(output):
            self.assertEqual(search.main(), 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result[0]["title"], "Guía de soporte")
        self.assertIn("→ español", result[0]["excerpt"])

    def test_cli_reconfigures_legacy_stdout_to_utf8(self):
        self.note("Soporte → español: guía útil.", title="Guía de soporte")
        buffer = io.BytesIO()
        output = io.TextIOWrapper(buffer, encoding="cp1252")
        with patch.object(search, "ROOT", self.root), \
             patch.object(sys, "argv", ["search.py", "soporte", "--json"]), \
             redirect_stdout(output):
            self.assertEqual(search.main(), 0)
            output.flush()
            payload = buffer.getvalue().decode("utf-8")
        self.assertIn("→ español", json.loads(payload)[0]["excerpt"])
        output.close()


if __name__ == "__main__":
    unittest.main()
