"""Portable dependency discovery without invoking capture executables."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from capture_tools import ToolConfigurationError, find_executable


class ToolDiscoveryTests(unittest.TestCase):
    def test_explicit_override_has_precedence(self):
        with patch.dict(os.environ, {"GBG_FFMPEG": "custom-ffmpeg"}, clear=True), \
             patch("capture_tools.shutil.which", return_value="custom-ffmpeg") as which:
            self.assertEqual(find_executable("ffmpeg"), str(Path("custom-ffmpeg").resolve()))
            which.assert_called_once_with("custom-ffmpeg")

    def test_invalid_override_does_not_silently_fall_back(self):
        with patch.dict(os.environ, {"GBG_TESSERACT": "missing"}, clear=True), \
             patch("capture_tools.shutil.which", return_value=None), \
             self.assertRaisesRegex(ToolConfigurationError, "GBG_TESSERACT"):
            find_executable("tesseract", required=False)

    def test_missing_optional_and_required_tool(self):
        with patch.dict(os.environ, {}, clear=True), \
             patch("capture_tools.shutil.which", return_value=None):
            self.assertIsNone(find_executable("ffprobe", required=False))
            with self.assertRaisesRegex(ToolConfigurationError, "GBG_FFPROBE"):
                find_executable("ffprobe")


if __name__ == "__main__":
    unittest.main()
