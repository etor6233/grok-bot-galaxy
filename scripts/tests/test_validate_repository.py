"""Regression tests for publication failures, not the prose in individual notes."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import yaml

from scripts.validate_repository import (
    MOJIBAKE, check_generated_outputs, check_markdown, check_metadata,
    check_security, excluded_material, heading_anchors, markdown_body, validate,
)


class RepositoryFixture(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.inventory = {
            "clips": [{"id": "01", "file": "recording.mp4", "day": "2026-09-15",
                       "module": "intro", "duration": "00:01:00"}],
            "modules": {"intro": {"clips": ["01"], "day": "2026-09-15"}},
            "manifest": {"total_clips": 1, "total_duration_seconds": 60, "total_duration_h": 0.02},
        }
        self.coverage = {"machine_complete": True, "aligned_complete": True, "distilled": True,
                         "status": {"01": dict.fromkeys(("scenes", "ocr", "asr", "aligned", "distilled"), "done")}}
        self.write("knowledge/timelines/01.md", "---\nclip: '01'\nfile: recording.mp4\nday: '2026-09-15'\nmodule: intro\nduration: '00:01:00'\nspeakers: [Presenter]\nstatus: aligned\n---\n\n## 00:00:00–00:01:00  [talking-head]\n**Spoken:** Example.\n**On screen:** —\n**Actions:** —\n**Facts:**\n- Example.\n")

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def metadata_errors(self, inventory=None, coverage=None):
        return check_metadata(self.root, inventory or self.inventory, coverage or self.coverage, expected_count=1)

    def init_git(self):
        subprocess.run(["git", "init", "-q", str(self.root)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.write("knowledge/_meta/inventory.yaml", yaml.safe_dump(self.inventory))
        self.write("knowledge/_meta/coverage.yaml", yaml.safe_dump(self.coverage))
        self.write(".gitignore", "knowledge/sources/\n*.mp4\n")


class MarkdownTests(RepositoryFixture):
    def test_missing_target_and_anchor_report_source_lines(self):
        self.write("guide.md", "# Good\n")
        text = "# Home\n\n[Broken](missing.md)\n[Wrong anchor](guide.md#bad)\n"
        path = self.write("README.md", text)
        errors = check_markdown(self.root, path, text)
        self.assertEqual([e.line for e in errors], [3, 4])

    def test_valid_anchors_spaces_images_and_reference_links(self):
        self.write("A guide.md", "# A `code` title\n\n## Repeat\n\n## Repeat\n\n<a id='custom'></a>\n")
        self.write("diagram.svg", "<svg/>\n")
        text = "[one](<A guide.md#a-code-title>)\n[two](A%20guide.md#repeat-1)\n![diagram](diagram.svg)\n[ref]: A%20guide.md#custom\n"
        path = self.write("README.md", text)
        self.assertEqual(check_markdown(self.root, path, text), [])

    def test_fences_and_inline_code_do_not_create_links(self):
        text = "~~~md\n[example](missing.md)\n~~~\n`[example](missing.md)`\n"
        path = self.write("README.md", text)
        self.assertEqual(check_markdown(self.root, path, text), [])

    def test_longer_fence_closes_but_shorter_fence_does_not(self):
        self.assertEqual(markdown_body("~~~\ntext\n~~~~", "x.md")[1], [])
        errors = markdown_body("````\n```\n", "x.md")[1]
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].line, 1)

    def test_case_mismatch_caught_even_on_windows(self):
        self.write("Guide.md", "# Guide\n")
        text = "[wrong](guide.md)\n"
        path = self.write("README.md", text)
        self.assertTrue(check_markdown(self.root, path, text))

    def test_external_links_are_not_requested(self):
        text = "[web](https://example.invalid/path#fragment)\n[email](mailto:example@example.invalid)\n"
        path = self.write("README.md", text)
        self.assertEqual(check_markdown(self.root, path, text), [])

    def test_private_or_escaping_links_fail_without_reading_target(self):
        self.write("knowledge/sources/clip/transcript.md", "do not read")
        text = "[raw](knowledge/sources/clip/transcript.md)\n[outside](../outside.md)\n"
        path = self.write("README.md", text)
        with patch.object(Path, "read_text", side_effect=AssertionError("link checker read a forbidden target")):
            self.assertEqual(len(check_markdown(self.root, path, text)), 2)

    def test_anchor_slugging_preserves_unicode_and_duplicate_suffixes(self):
        self.assertEqual(heading_anchors("# Guía: `Bot`!\n## Guía: Bot!\n"), {"guía-bot", "guía-bot-1"})


class MetadataTests(RepositoryFixture):
    def test_valid_fixture_needs_no_raw_recording(self):
        self.assertFalse((self.root / "recording.mp4").exists())
        self.assertEqual(self.metadata_errors(), [])

    def test_nonnumeric_timeline_index_is_ignored(self):
        self.write("knowledge/timelines/INDEX.md", "# Index\n")
        self.assertEqual(self.metadata_errors(), [])

    def test_duplicate_id_with_alternate_padding_is_rejected(self):
        inv = deepcopy(self.inventory)
        inv["clips"].append({**inv["clips"][0], "id": "001"})
        errors = self.metadata_errors(inv)
        self.assertTrue(any("duplicate clip" in e.message for e in errors))

    def test_wrong_timeline_module_is_detected(self):
        path = self.root / "knowledge/timelines/01.md"
        path.write_text(path.read_text(encoding="utf-8").replace("module: intro", "module: other"), encoding="utf-8")
        self.assertTrue(any("frontmatter module" in e.message for e in self.metadata_errors()))

    def test_module_partition_cannot_duplicate_members(self):
        inv = deepcopy(self.inventory)
        inv["modules"]["intro"]["clips"].append("01")
        self.assertTrue(any("partition" in e.message for e in self.metadata_errors(inv)))

    def test_duration_totals_use_probed_seconds_when_present(self):
        inv = deepcopy(self.inventory)
        inv["clips"][0]["duration_seconds"] = 60.45
        inv["manifest"]["total_duration_seconds"] = 60.5
        self.assertEqual(self.metadata_errors(inv), [])
        inv["manifest"]["total_duration_seconds"] = 600
        self.assertTrue(any("total_duration_seconds" in e.message for e in self.metadata_errors(inv)))

    def test_missing_coverage_and_false_completion_are_detected(self):
        coverage = deepcopy(self.coverage)
        coverage["status"]["01"]["distilled"] = "pending"
        self.assertTrue(any("distilled disagrees" in e.message for e in self.metadata_errors(coverage=coverage)))
        coverage["status"] = {}
        self.assertTrue(any("IDs do not match" in e.message for e in self.metadata_errors(coverage=coverage)))

    def test_optional_distilled_complete_must_match(self):
        coverage = deepcopy(self.coverage)
        coverage["distilled_complete"] = False
        self.assertTrue(any("distilled_complete" in e.message for e in self.metadata_errors(coverage=coverage)))

    def test_malformed_coverage_fields_report_errors_instead_of_crashing(self):
        coverage = deepcopy(self.coverage)
        coverage["status"]["01"].update(asr=["done"], canon_sources=None)
        errors = self.metadata_errors(coverage=coverage)
        self.assertTrue(any("invalid asr" in e.message for e in errors))
        self.assertTrue(any("canon_sources must be a list" in e.message for e in errors))

    def test_event_dates_cannot_silently_omit_a_day(self):
        inventory = deepcopy(self.inventory)
        inventory["event"] = {"dates": ["2026-09-16"]}
        self.assertTrue(any("event.dates" in e.message for e in self.metadata_errors(inventory)))

    def test_catalog_freshness_is_exact_and_detects_missing_file(self):
        path = self.write("knowledge/catalog.json", "{}\n")
        self.assertEqual(check_generated_outputs(self.root, {path: "{}\n"}), [])
        self.assertEqual(len(check_generated_outputs(self.root, {path: "[]\n"})), 1)
        path.unlink()
        self.assertEqual(len(check_generated_outputs(self.root, {path: "{}\n"})), 1)


class PublicationSecurityTests(RepositoryFixture):
    def test_secret_and_phone_diagnostics_never_repeat_values(self):
        token = "gh" + "p_" + "A" * 36
        phone = "+1" + "202" + "555" + "0198"
        issues = check_security("knowledge/example.md", token + "\n" + phone)
        self.assertEqual(len(issues), 2)
        rendered = "\n".join(map(str, issues))
        self.assertNotIn(token, rendered)
        self.assertNotIn(phone, rendered)
        self.assertIn(":1:", rendered)
        self.assertIn(":2:", rendered)

    def test_only_named_synthetic_fixture_directory_is_exempt(self):
        value = "gh" + "p_" + "B" * 36
        self.assertEqual(check_security("scripts/tests/fixtures/security/negative.txt", value), [])
        self.assertTrue(check_security("scripts/tests/test_something.py", value))
        self.assertTrue(check_security("knowledge/canon/example.md", value))

    def test_encoding_regressions_are_detected_without_rejecting_accents(self):
        self.assertIsNone(MOJIBAKE.search("Guía, André, mañana — 日本語"))
        self.assertIsNotNone(MOJIBAKE.search("bad \ufffd"))
        self.assertIsNotNone(MOJIBAKE.search("caf\u00c3\u00a9"))

    def test_raw_capture_paths_are_recognized(self):
        for path in ("knowledge/sources/01/pack.md", "clip.mp4", "x/keyframes/001.png", "_probe/output.json"):
            self.assertTrue(excluded_material(path), path)
        self.assertFalse(excluded_material("assets/workflow.svg"))

    def test_clean_git_checkout_passes_without_private_sources(self):
        self.init_git()
        self.write("README.md", "# Example\n\n[Timeline](knowledge/timelines/01.md)\n")
        self.assertEqual(validate(self.root, expected_count=1, check_catalog=False), [])

    def test_tracked_raw_material_is_flagged_without_opening_contents(self):
        self.init_git()
        path = self.root / "knowledge/sources/01/ocr.md"
        path.parent.mkdir(parents=True)
        path.write_bytes(b"\xff\xfe\x00")
        subprocess.run(["git", "-C", str(self.root), "add", "-f", str(path)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        original = Path.read_text

        def guarded_read(candidate, *args, **kwargs):
            if "sources" in candidate.parts:
                raise AssertionError("validator read raw content")
            return original(candidate, *args, **kwargs)

        with patch.object(Path, "read_text", guarded_read):
            issues = validate(self.root, expected_count=1, check_catalog=False)
        self.assertEqual(len(issues), 1)
        self.assertIn("contents not read", issues[0].message)


if __name__ == "__main__":
    unittest.main()
