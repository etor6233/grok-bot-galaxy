"""Regression fixtures for malformed archives and selected-file validation."""

from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import validate_timelines as validator


class TimelineValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.path = self.directory / "019.md"
        self.meta = {
            "clip": "019",
            "file": "19-Engineering- 2026-09-15.mp4",
            "day": "2026-09-15",
            "module": "engineering",
            "duration": "00:09:59",
            "speakers": ["Presenter"],
            "status": "aligned",
        }
        self.inventory = {
            "019": {
                "id": "019",
                **{key: self.meta[key] for key in ("file", "day", "module", "duration")},
                "duration_seconds": 599.233,
            }
        }
        self.inventory_path = self.directory / "inventory.yaml"
        self.inventory_path.write_text(
            yaml.safe_dump({"clips": list(self.inventory.values())}), encoding="utf-8"
        )

    @staticmethod
    def block(start="00:00:00", end="00:09:59", kind="ui-demo", facts="- Observed fact"):
        return (
            f"## {start}–{end}  [{kind}]\n"
            "**Spoken:** Recorded statement.\n"
            "**On screen:** —\n"
            "**Actions:** GAP\n"
            f"**Facts:**\n{facts}\n"
        )

    def write(self, body=None, meta=None):
        frontmatter = yaml.safe_dump(self.meta if meta is None else meta, sort_keys=False)
        text = f"---\n{frontmatter}---\n\n{self.block() if body is None else body}"
        self.path.write_text(text, encoding="utf-8")
        return text

    def errors(self):
        return validator.check(self.path, self.inventory)

    def test_valid_document_and_explicit_empty_markers(self):
        for facts in ("- Observed fact", "—", "GAP", "- —", "- GAP"):
            with self.subTest(facts=facts):
                self.write(self.block(facts=facts))
                self.assertEqual([], self.errors())

    def test_ceiling_of_fractional_probe_is_allowed(self):
        self.write(self.block(end="00:10:00"))
        self.assertEqual([], self.errors())
        self.write(self.block(end="00:10:01"))
        self.assertTrue(any("exceeds clip duration" in e for e in self.errors()))

    def test_no_probe_uses_declared_duration_without_extra_grace(self):
        del self.inventory["019"]["duration_seconds"]
        self.write(self.block(end="00:10:00"))
        self.assertTrue(any("exceeds clip duration" in e for e in self.errors()))

    def test_invalid_timestamp_components(self):
        for start in ("00:60:00", "00:00:60"):
            with self.subTest(start=start):
                self.write(self.block(start=start))
                self.assertTrue(any("invalid timestamp" in e for e in self.errors()))

    def test_reverse_interval_and_overlap_fail(self):
        self.write(self.block(start="00:02:00", end="00:01:00"))
        self.assertTrue(any("end before start" in e for e in self.errors()))
        self.write(self.block(end="00:02:00") + self.block(start="00:01:59"))
        self.assertTrue(any("overlaps" in e for e in self.errors()))

    def test_touching_blocks_and_explicit_gap_are_valid(self):
        self.write(
            self.block(end="00:01:00")
            + self.block(start="00:01:00", end="00:02:00", kind="gap", facts="GAP")
            + self.block(start="00:02:00")
        )
        self.assertEqual([], self.errors())

    def test_unsupported_kind_and_malformed_heading(self):
        self.write(self.block(kind="inferred"))
        self.assertTrue(any("unsupported kind" in e for e in self.errors()))
        self.write(self.block().replace("00:00:00", "00:00"))
        self.assertTrue(any("bad heading" in e for e in self.errors()))

    def test_fields_exactly_once_in_order(self):
        variants = [
            self.block().replace("**Actions:** GAP", "**Actions:** GAP\n**Actions:** Duplicate"),
            self.block().replace("**On screen:** —\n", ""),
            self.block().replace("**On screen:** —\n**Actions:** GAP", "**Actions:** GAP\n**On screen:** —"),
            self.block().replace("**Facts:**", "**Inferred:** Extra\n**Facts:**"),
        ]
        for body in variants:
            with self.subTest(body=body):
                self.write(body)
                self.assertTrue(any("exactly once in order" in e for e in self.errors()))

    def test_empty_fields_and_unstructured_facts_fail(self):
        self.write(self.block().replace("**On screen:** —", "**On screen:**"))
        self.assertTrue(any("empty On screen" in e for e in self.errors()))
        self.write(self.block(facts=""))
        self.assertTrue(any("empty Facts" in e for e in self.errors()))
        self.write(self.block(facts="Unstructured fact"))
        self.assertTrue(any("Facts must be bullets" in e for e in self.errors()))

    def test_no_blocks_is_invalid(self):
        self.write("Notes but no timed blocks.\n")
        self.assertIn("no timeline blocks", self.errors())

    def test_yaml_is_parsed_not_searched_for_substrings(self):
        meta = dict(self.meta)
        del meta["file"]
        meta["notes"] = "file: looks present but is not a field"
        self.write(meta=meta)
        self.assertIn("frontmatter missing file", self.errors())

    def test_invalid_and_duplicate_yaml_fail(self):
        text = self.write()
        self.path.write_text(text.replace("speakers:\n- Presenter", "speakers: [broken"), encoding="utf-8")
        self.assertTrue(any("invalid YAML" in e for e in self.errors()))
        self.path.write_text(text.replace("status: aligned", "status: aligned\nstatus: aligned"), encoding="utf-8")
        self.assertTrue(any("duplicate key" in e for e in self.errors()))

    def test_frontmatter_types_and_date(self):
        for key, value in (("clip", 19), ("speakers", "Presenter"), ("day", "2026-02-30"), ("status", "draft")):
            with self.subTest(key=key):
                self.write(meta={**self.meta, key: value})
                self.assertTrue(self.errors())

    def test_inventory_identity_and_duration_match(self):
        for key, value in (("file", "wrong.mp4"), ("day", "2026-09-16"), ("module", "founders"), ("duration", "00:09:58")):
            with self.subTest(key=key):
                self.write(meta={**self.meta, key: value})
                self.assertTrue(any(f"{key} does not match inventory" in e for e in self.errors()))

    def test_missing_inventory_row_and_invalid_probe(self):
        self.write()
        self.assertIn("clip absent from inventory", validator.check(self.path, {}))
        for invalid in (float("nan"), float("inf"), -1, True, "599.2"):
            with self.subTest(invalid=invalid):
                self.inventory["019"]["duration_seconds"] = invalid
                self.assertTrue(any("duration_seconds must be" in e for e in self.errors()))

    def test_invalid_utf8_is_reported(self):
        self.path.write_bytes(b"\xff\xfe")
        self.assertTrue(any("cannot read UTF-8" in e for e in self.errors()))

    def test_inventory_duplicate_ids_rejected(self):
        self.inventory_path.write_text(
            yaml.safe_dump({"clips": [self.inventory["019"], self.inventory["019"]]}), encoding="utf-8"
        )
        with self.assertRaisesRegex(ValueError, "duplicate inventory"):
            validator.load_inventory(self.inventory_path)

    def test_cli_selected_filename_ignores_unselected_failure(self):
        self.write()
        (self.directory / "020.md").write_text("invalid unrelated timeline", encoding="utf-8")
        with patch.object(validator, "TDIR", self.directory), redirect_stdout(StringIO()) as output:
            status = validator.main(["019.md", "--inventory", str(self.inventory_path), "--quiet"])
        self.assertEqual(0, status)
        self.assertIn("1 timelines checked, 0 failed", output.getvalue())

    def test_cli_all_ignores_generated_index(self):
        self.write()
        (self.directory / "INDEX.md").write_text("# Generated routing index", encoding="utf-8")
        with patch.object(validator, "TDIR", self.directory), redirect_stdout(StringIO()) as output:
            status = validator.main(["--inventory", str(self.inventory_path), "--quiet"])
        self.assertEqual(0, status)
        self.assertIn("1 timelines checked, 0 failed", output.getvalue())

    def test_cli_all_detects_inventory_clip_without_timeline(self):
        with patch.object(validator, "TDIR", self.directory), redirect_stdout(StringIO()) as output:
            status = validator.main(["--inventory", str(self.inventory_path), "--quiet"])
        self.assertEqual(1, status)
        self.assertIn("inventory clip has no timeline", output.getvalue())

    def test_cli_missing_selected_file_is_error(self):
        with patch.object(validator, "TDIR", self.directory), redirect_stdout(StringIO()) as output:
            status = validator.main(["019.md", "--inventory", str(self.inventory_path), "--quiet"])
        self.assertEqual(1, status)
        self.assertIn("cannot read UTF-8 timeline", output.getvalue())


if __name__ == "__main__":
    unittest.main()
