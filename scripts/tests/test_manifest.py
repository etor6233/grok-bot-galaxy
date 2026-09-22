"""Manifest regression tests using metadata and temporary files only.

No test opens event recordings or anything under knowledge/sources.
"""

from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import manifest


class ManifestTests(unittest.TestCase):
    def test_clip_identity_at_every_day_boundary(self):
        cases = [
            ("2026-09-15", 1, "01"), ("2026-09-15", 18, "18"),
            ("2026-09-15", 19, "019"), ("2026-09-15", 64, "064"),
            ("2026-09-16", 1, "065"), ("2026-09-16", 48, "112"),
            ("2026-09-17", 1, "113"), ("2026-09-17", 45, "157"),
        ]
        for day, number, expected in cases:
            with self.subTest(day=day, number=number):
                self.assertEqual(manifest.clip_id(day, number), expected)

    def test_out_of_day_numbers_cannot_collide_with_next_day(self):
        for day, number in [("2026-09-15", 65), ("2026-09-16", 49),
                            ("2026-09-17", 46), ("2026-09-17", 0)]:
            with self.subTest(day=day, number=number), self.assertRaises(ValueError):
                manifest.clip_id(day, number)

    def test_historical_duration_and_measured_seconds(self):
        self.assertEqual(manifest.duration_seconds({"duration": "00:10:00"}), 600)
        self.assertEqual(manifest.duration_seconds({"duration": "01:02:03.5"}), 3723.5)
        self.assertEqual(manifest.duration_seconds({"duration_seconds": 599.233,
                                                   "duration": "00:09:59"}), 599.233)
        self.assertEqual(manifest.duration_seconds({"duration_seconds": float("nan"),
                                                   "duration": "00:10:00"}), 600)
        self.assertIsNone(manifest.duration_seconds({"duration": "00:99:00"}))
        self.assertIsNone(manifest.duration_seconds({"duration_seconds": 0}))

    def test_checkout_without_recordings_preserves_rows_and_totals(self):
        inv = {
            "event": {"name": "fixture"},
            "clips": [
                {"id": "01", "file": "old.mp4", "duration": "00:10:00",
                 "day": "2026-09-15", "module": "engineering", "notes": "keep"},
                {"id": "157", "file": "last.mp4", "duration_seconds": 12.5,
                 "day": "2026-09-17", "module": "marketing"},
            ],
            "modules": {"engineering": {"clips": ["01"], "title": "Historical"}},
        }
        original = copy.deepcopy(inv)
        with patch.object(manifest, "probe", side_effect=AssertionError("must not probe")):
            updated = manifest.update_inventory(inv, [])
        self.assertEqual(inv, original)
        self.assertEqual(updated["clips"], original["clips"])
        self.assertEqual(updated["manifest"]["total_duration_seconds"], 612.5)
        self.assertEqual(updated["manifest"]["missing_local_files"], ["01", "157"])
        self.assertEqual(updated["manifest"]["unknown_duration"], [])
        self.assertEqual(updated["event"], {"name": "fixture"})

    def test_new_last_clip_does_not_remove_missing_first_clip(self):
        inv = {"clips": [{"id": "01", "file": "historical.mp4", "duration": "00:10:00"}]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "45-Marketing- 2026-09-17.mp4"
            path.touch()
            with patch.object(manifest, "probe", return_value={
                "file": path.name, "duration_seconds": 60, "duration": "00:01:00"
            }) as probe:
                updated = manifest.update_inventory(inv, [path])
        probe.assert_called_once_with(path)
        self.assertEqual([r["id"] for r in updated["clips"]], ["01", "157"])
        self.assertEqual(updated["manifest"]["total_duration_seconds"], 660)
        self.assertEqual(updated["manifest"]["missing_local_files"], ["01"])

    def test_known_local_filename_is_never_reprobed_or_renumbered(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "1-Bienvenida- 2026-09-15.mp4"
            path.touch()
            inv = {"clips": [{"id": "01", "file": path.name,
                              "duration": "00:10:00", "day": "2026-09-15"}]}
            with patch.object(manifest, "probe", side_effect=AssertionError("must not probe")):
                updated = manifest.update_inventory(inv, [path])
        self.assertEqual(updated["clips"], inv["clips"])
        self.assertEqual(updated["manifest"]["missing_local_files"], [])

    def test_rename_identity_collision_is_rejected_before_probe(self):
        inv = {"clips": [{"id": "065", "file": "old-name.mp4"}]}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "1-Sales Engineering- 2026-09-16.mp4"
            path.touch()
            with patch.object(manifest, "probe") as probe, self.assertRaisesRegex(ValueError, "already belongs"):
                manifest.update_inventory(inv, [path])
        probe.assert_not_called()

    def test_duplicate_historical_identity_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            manifest.update_inventory({"clips": [
                {"id": "01", "file": "first.mp4"},
                {"id": "001", "file": "second.mp4"},
            ]}, [])

    def test_missing_duration_is_reported_without_dropping_the_clip(self):
        updated = manifest.update_inventory({"clips": [{"id": "01", "file": "old.mp4"}]}, [])
        self.assertEqual(updated["manifest"]["unknown_duration"], ["01"])
        self.assertEqual(updated["manifest"]["total_clips"], 1)

    def test_failed_probe_leaves_inventory_file_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inventory = root / "inventory.yaml"
            original = "clips: []\n"
            inventory.write_text(original, encoding="utf-8")
            (root / "45-Marketing- 2026-09-17.mp4").touch()
            with patch.object(manifest, "ROOT", root), patch.object(manifest, "INV", inventory), \
                 patch.object(manifest, "probe", side_effect=RuntimeError("fixture probe failed")):
                self.assertEqual(manifest.main(), 2)
            self.assertEqual(inventory.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()
