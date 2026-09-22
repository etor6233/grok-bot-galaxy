"""Allow only published Markdown notes before opening a retrieval candidate."""

from __future__ import annotations

from pathlib import Path, PurePosixPath

PUBLIC_SECTIONS = {"canon", "session", "timelines"}
PRIVATE_PARTS = {"sources", "_meta", "keyframes", "_probe"}
PRIVATE_NAMES = {"ocr.md", "pack.md", "transcript.md"}


def public_note_path(root: Path, relative: str, *, kind: str | None = None) -> Path:
    """Reject private paths and filesystem redirects before reading contents."""
    if not isinstance(relative, str) or "\\" in relative:
        raise ValueError("Public note paths must use repository-relative forward slashes")
    item = PurePosixPath(relative)
    parts = item.parts
    if (len(parts) < 3 or parts[0] != "knowledge" or parts[1] not in PUBLIC_SECTIONS
            or ".." in parts or item.suffix.lower() != ".md"
            or PRIVATE_PARTS.intersection(p.lower() for p in parts)
            or item.name.lower() in PRIVATE_NAMES
            or kind is not None and kind != parts[1]):
        raise ValueError("Catalog paths must identify published canon, session or timeline Markdown")
    root = root.resolve()
    candidate = root.joinpath(*parts)
    current = root
    for part in parts:
        current /= part
        if current.is_symlink() or getattr(current, "is_junction", lambda: False)():
            raise ValueError("Public notes must not use symlinks or directory junctions")
    resolved = candidate.resolve()
    if not resolved.is_relative_to(root / "knowledge" / parts[1]):
        raise ValueError("Public note resolves outside its published section")
    if not resolved.is_file():
        raise ValueError("Catalog references a missing public Markdown note")
    return resolved
