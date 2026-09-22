"""Regenerate knowledge/_meta/inventory.yaml from the *.mp4 files in the repo root.

Deterministic identity:
  - Day 1 (2026-09-15): id = leading file number, 3-digit for new clips ("019"–"064").
    Existing clips "01"–"18" keep their historical two-digit ids.
  - Day 2 (2026-09-16): id = 64 + leading file number  -> "065"–"112".
  - Day 3 (2026-09-17): id = 112 + leading file number -> "113"–"157".

Probes each file with ffprobe (duration, size) and records local mtime as
`recorded_end` (Bandicam stops writing at end of recording). Files modified in
the last 20 minutes are flagged as possibly-live; the extraction driver applies
a stability guard before touching them.

Existing inventory rows are preserved by filename, even if recordings are absent
from a fresh checkout (never re-probed or renumbered). Tools are discovered from
GBG_FFPROBE / GBG_FFMPEG or PATH. New files require a successful duration probe.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import yaml

from capture_tools import ToolConfigurationError, find_executable

ROOT = Path(__file__).resolve().parents[1]
META = ROOT / "knowledge" / "_meta"
INV = META / "inventory.yaml"

DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
LABEL_RE = re.compile(r"^\d+-(.+?)\s*-\s*\d{4}-\d{2}-\d{2}")
DAY_BASE = {"2026-09-15": 0, "2026-09-16": 64, "2026-09-17": 112}
DAY_COUNTS = {"2026-09-15": 64, "2026-09-16": 48, "2026-09-17": 45}

MODULE_OF = {
    "Engineering": "engineering",
    "Product Managers": "product-managers",
    "Founders": "founders",
    "Sales Engineering": "sales-engineering",
    "Sales": "sales",
    "SDRs": "sdrs",
    "Customer Support": "customer-support",
    "Marketing Operations": "marketing-operations",
    "Post Sales": "post-sales",
    "Marketing": "marketing",
}

MODULE_TITLE = {
    "engineering": "Engineering",
    "product-managers": "Product Managers",
    "founders": "Founders",
    "sales-engineering": "Sales Engineering",
    "sales": "Sales",
    "sdrs": "SDRs",
    "customer-support": "Customer Support",
    "marketing-operations": "Marketing Operations",
    "post-sales": "Post Sales",
    "marketing": "Marketing",
}


def probe(path: Path) -> dict:
    """Probe a new local recording; fail clearly instead of inventing duration."""
    info = {
        "file": path.name,
        "size_bytes": path.stat().st_size,
        "recorded_end": datetime.fromtimestamp(path.stat().st_mtime).strftime(
            "%Y-%m-%dT%H:%M:%S"
        ),
    }
    duration = None
    ffprobe = find_executable("ffprobe", required=False)
    if ffprobe:
        p = subprocess.run(
            [
                ffprobe,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "json",
                str(path),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
        if p.returncode == 0:
            try:
                duration = float(json.loads(p.stdout)["format"]["duration"])
            except (TypeError, ValueError, KeyError):
                duration = None
    if duration is not None and (not math.isfinite(duration) or duration <= 0):
        duration = None
    if duration is None:
        ffmpeg = find_executable("ffmpeg", required=False)
        if not ffmpeg:
            raise ToolConfigurationError(
                f"Could not probe {path.name}. Install ffprobe (GBG_FFPROBE/PATH) "
                "or ffmpeg (GBG_FFMPEG/PATH); existing inventory is unchanged."
            )
        p = subprocess.run(
            [ffmpeg, "-i", str(path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", p.stderr)
        if m:
            h, mi, s = m.groups()
            duration = int(h) * 3600 + int(mi) * 60 + float(s)
    if duration is None or not math.isfinite(duration) or duration <= 0:
        raise RuntimeError(
            f"No valid duration for {path.name}; verify that the recording is "
            "complete and the configured ffprobe/ffmpeg can read it."
        )
    h, rem = divmod(int(duration), 3600)
    mi, s = divmod(rem, 60)
    info["duration"] = f"{h:02d}:{mi:02d}:{s:02d}"
    info["duration_seconds"] = round(duration, 3)
    return info


def parse_name(name: str) -> tuple[str, int | None, str | None]:
    d = DATE_RE.search(name)
    date = d.group(1) if d else ""
    mnum = re.match(r"^(\d+)-", name)
    num = int(mnum.group(1)) if mnum else None
    lab = LABEL_RE.match(name)
    label = lab.group(1).strip() if lab else None
    return date, num, label


def clip_id(day: str, number: int) -> str:
    """Keep 01–18 historical IDs and prevent out-of-day identity collisions."""
    if day not in DAY_COUNTS or not 1 <= number <= DAY_COUNTS[day]:
        raise ValueError(f"Clip number {number} is outside the authorized range for {day}")
    ordinal = DAY_BASE[day] + number
    return f"{ordinal:02d}" if day == "2026-09-15" and number <= 18 else f"{ordinal:03d}"


def duration_seconds(row: dict) -> float | None:
    """Use measured seconds, falling back to historical HH:MM:SS metadata."""
    value = row.get("duration_seconds")
    if value is not None:
        try:
            seconds = float(value)
            if math.isfinite(seconds) and seconds > 0:
                return seconds
        except (TypeError, ValueError):
            pass
    match = re.fullmatch(r"(\d+):([0-5]\d):([0-5]\d(?:\.\d+)?)", str(row.get("duration", "")))
    if match:
        hours, minutes, seconds = match.groups()
        duration = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
        return duration if duration > 0 else None
    return None


def update_inventory(inv: dict, paths: list[Path]) -> dict:
    """Build metadata without dropping historical rows or rewriting the file."""
    protected: dict[str, dict] = {}
    identities: dict[int, str] = {}
    for row in inv.get("clips", []):
        name = row["file"]
        ordinal = int(row["id"])
        if name in protected or ordinal in identities:
            raise ValueError(f"Duplicate historical inventory filename or clip ID: {name}")
        protected[name] = dict(row)
        identities[ordinal] = name

    recent: list[str] = []
    now_ts = datetime.now().timestamp()
    local_names = {p.name for p in paths}
    for path in sorted(paths, key=lambda p: p.name):
        name = path.name
        date, num, label = parse_name(name)
        if name in protected:
            if date:
                protected[name].setdefault("day", date)
            if path.stat().st_mtime > now_ts - 1200:
                recent.append(protected[name]["id"])
            continue
        if num is None or date not in DAY_BASE:
            print(f"SKIP unparseable {name}", file=sys.stderr)
            continue
        cid = clip_id(date, num)
        if int(cid) in identities:
            raise ValueError(
                f"Clip {cid} already belongs to {identities[int(cid)]}; "
                f"refusing to assign it to {name}. Resolve the rename explicitly."
            )
        info = probe(path)
        row = {"id": cid, **info, "day": date}
        module = MODULE_OF.get(label or "")
        row["module"] = module
        if module is None:
            row["label_missing"] = True
            row["raw_label"] = label
        protected[name] = row
        identities[int(cid)] = name
        if path.stat().st_mtime > now_ts - 1200:
            recent.append(cid)

    rows = sorted(protected.values(), key=lambda r: int(r["id"]))
    unlabeled = [r["id"] for r in rows if not r.get("module")]

    modules: dict = {}
    for key, val in inv.get("modules", {}).items():
        modules[key] = {**val, "clips": list(val.get("clips", []))}
    for row in rows:
        m = row.get("module")
        if not m:
            continue
        if m not in modules:
            modules[m] = {"clips": [], "title": MODULE_TITLE.get(m, m), "day": row.get("day")}
        modules[m].setdefault("day", row.get("day"))
        if row["id"] not in modules[m]["clips"]:
            modules[m]["clips"].append(row["id"])

    # Authoritative module day = day of its first clip (never hardcoded).
    clip_day = {r["id"]: r.get("day") for r in rows}
    for key, val in modules.items():
        ids = val.get("clips", [])
        if ids:
            val["day"] = clip_day.get(ids[0], val.get("day"))

    durations = [duration_seconds(r) for r in rows]
    total_sec = sum(value for value in durations if value is not None)
    result = dict(inv)
    result["clips"] = rows
    result["modules"] = modules
    result["manifest"] = {
        "generated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "total_clips": len(rows),
        "total_duration_seconds": round(total_sec, 1),
        "total_duration_h": round(total_sec / 3600, 2),
        "recent_mtime_possible_live": sorted(recent, key=int),
        "missing_label": unlabeled,
        "missing_local_files": [r["id"] for r in rows if r["file"] not in local_names],
        "unknown_duration": [r["id"] for r, value in zip(rows, durations) if value is None],
    }
    return result


def main() -> int:
    try:
        inv = yaml.safe_load(INV.read_text(encoding="utf-8")) if INV.exists() else {}
        updated = update_inventory(inv or {}, list(ROOT.glob("*.mp4")))
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"manifest: {exc}", file=sys.stderr)
        return 2
    INV.parent.mkdir(parents=True, exist_ok=True)
    # Write only after every new file and identity has passed validation.
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=INV.parent, delete=False) as fh:
            temp_path = Path(fh.name)
            yaml.safe_dump(updated, fh, sort_keys=False, allow_unicode=True)
        os.replace(temp_path, INV)
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()
    meta = updated["manifest"]
    print(f"manifest: {meta['total_clips']} clips, {meta['total_duration_h']:.2f} h total")
    print(f"recent (possible live): {meta['recent_mtime_possible_live']}")
    print(f"unlabeled: {meta['missing_label']}")
    print(f"missing locally (preserved): {meta['missing_local_files']}")
    print(f"unknown duration: {meta['unknown_duration']}")
    return 0


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    raise SystemExit(main())
