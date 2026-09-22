"""Portable discovery for optional, local-only media capture tools.

Set GBG_FFMPEG, GBG_FFPROBE or GBG_TESSERACT to an executable path/name,
or put the corresponding executable on PATH. Importing this module does not
inspect recordings, create output directories, or invoke external programs.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path


class ToolConfigurationError(RuntimeError):
    """A capture dependency is unavailable or explicitly misconfigured."""


def find_executable(name: str, *, required: bool = True) -> str | None:
    """Resolve an explicit GBG_* override, then PATH; never guess a user path."""
    env_name = f"GBG_{name.upper()}"
    override = os.environ.get(env_name)
    if override:
        candidate = os.path.expandvars(os.path.expanduser(override))
        resolved = shutil.which(candidate)
        if resolved:
            return str(Path(resolved).resolve())
        raise ToolConfigurationError(
            f"{env_name} does not resolve to an executable. Set it to the full "
            f"path of {name}, or unset it and add {name} to PATH."
        )
    resolved = shutil.which(name)
    if resolved:
        return str(Path(resolved).resolve())
    if required:
        raise ToolConfigurationError(
            f"{name} was not found. Install it and add it to PATH, or set "
            f"{env_name} to its executable path. Python packages alone do not "
            "install the capture executables."
        )
    return None
