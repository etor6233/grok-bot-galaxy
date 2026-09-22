"""Validate public timelines, YAML identity, and the four-field block contract.

Usage: python scripts/validate_timelines.py [019.md ...] [--quiet]
With no filenames, validate every numeric timeline and inventory coverage.
Recorded durations are whole seconds; block endpoints may reach the ceiling of
the independently probed duration_seconds in inventory. No raw sources are read.
"""

from __future__ import annotations

import argparse
from datetime import date
import math
from pathlib import Path
import re
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
TDIR = ROOT / "knowledge" / "timelines"
INV = ROOT / "knowledge" / "_meta" / "inventory.yaml"
KINDS = {"slide", "ui-demo", "talking-head", "overlay", "gap"}
FIELDS = ["Spoken", "On screen", "Actions", "Facts"]
REQUIRED = {"clip", "file", "day", "module", "duration", "speakers", "status"}
TIME = re.compile(r"^(\d{2}):(\d{2}):(\d{2})$")
HDR = re.compile(r"^(\d{2}:\d{2}:\d{2})[–—−-](\d{2}:\d{2}:\d{2})\s+\[([a-z-]+)\]$")
FIELD = re.compile(r"(?m)^\*\*([^*\r\n]+):\*\*")


class UniqueLoader(yaml.SafeLoader):
    """Reject duplicate mapping keys instead of silently keeping the last one."""


def _mapping(loader: UniqueLoader, node: yaml.MappingNode, deep: bool = False) -> dict:
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in result
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(
                "mapping", node.start_mark, "unhashable key", key_node.start_mark
            ) from exc
        if duplicate:
            raise yaml.constructor.ConstructorError(
                "mapping", node.start_mark, f"duplicate key {key!r}", key_node.start_mark
            )
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)


def seconds(value: Any) -> int:
    match = TIME.fullmatch(value) if isinstance(value, str) else None
    if not match:
        raise ValueError("expected HH:MM:SS string")
    hours, minutes, secs = map(int, match.groups())
    if minutes >= 60 or secs >= 60:
        raise ValueError("minutes and seconds must be in 00..59")
    return hours * 3600 + minutes * 60 + secs


def day_string(value: Any) -> str:
    if isinstance(value, date):
        return value.isoformat()
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("expected ISO date YYYY-MM-DD")
    return date.fromisoformat(value).isoformat()


def load_inventory(path: Path) -> dict[str, dict]:
    data = yaml.load(path.read_text(encoding="utf-8-sig"), Loader=UniqueLoader)
    if not isinstance(data, dict) or not isinstance(data.get("clips"), list):
        raise ValueError("inventory must contain a clips list")
    rows = {}
    for row in data["clips"]:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str):
            raise ValueError("each inventory clip needs a string id")
        clip = row["id"]
        if not clip.isdigit() or clip in rows:
            raise ValueError(f"invalid or duplicate inventory clip id: {clip!r}")
        rows[clip] = row
    return rows


def check(path: Path, inventory: dict[str, dict] | None = None) -> list[str]:
    errors: list[str] = []
    if not path.stem.isdigit():
        return ["timeline filename must have a numeric stem"]
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        return [f"cannot read UTF-8 timeline: {exc}"]
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
    if not match:
        return ["missing or unterminated YAML frontmatter"]
    try:
        meta = yaml.load(match.group(1), Loader=UniqueLoader)
    except yaml.YAMLError as exc:
        return [f"invalid YAML frontmatter: {exc}"]
    if not isinstance(meta, dict):
        return ["frontmatter must be a YAML mapping"]
    for key in sorted(REQUIRED - meta.keys()):
        errors.append(f"frontmatter missing {key}")
    for key in ("clip", "file", "module", "duration", "status"):
        if key in meta and (not isinstance(meta[key], str) or not meta[key].strip()):
            errors.append(f"frontmatter {key} must be a nonempty string")
    if meta.get("clip") != path.stem:
        errors.append(f"clip does not match filename stem {path.stem!r}")
    if meta.get("status") != "aligned":
        errors.append("status must be aligned")
    speakers = meta.get("speakers")
    if not isinstance(speakers, list) or not speakers or any(
        not isinstance(speaker, str) or not speaker.strip() for speaker in speakers
    ):
        errors.append("speakers must be a nonempty list of nonempty strings")
    try:
        current_day = day_string(meta.get("day"))
    except ValueError as exc:
        current_day = None
        errors.append(f"frontmatter day: {exc}")
    try:
        limit = seconds(meta.get("duration"))
    except ValueError as exc:
        limit = None
        errors.append(f"frontmatter duration: {exc}")

    try:
        inventory = load_inventory(INV) if inventory is None else inventory
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return errors + [f"cannot load inventory: {exc}"]
    row = inventory.get(path.stem)
    if row is None:
        errors.append("clip absent from inventory")
    else:
        for key in ("file", "module", "duration"):
            if meta.get(key) != row.get(key):
                errors.append(f"{key} does not match inventory: expected {row.get(key)!r}")
        try:
            if current_day != day_string(row.get("day")):
                errors.append(f"day does not match inventory: expected {row.get('day')!r}")
        except ValueError as exc:
            errors.append(f"invalid inventory day: {exc}")
        if "duration_seconds" in row:
            probed = row["duration_seconds"]
            if (
                isinstance(probed, bool)
                or not isinstance(probed, (int, float))
                or not math.isfinite(probed)
                or probed < 0
            ):
                errors.append("inventory duration_seconds must be finite and nonnegative")
            else:
                limit = math.ceil(probed)

    body = text[match.end():]
    blocks = re.split(r"(?m)^##[ \t]+", body)[1:]
    if not blocks:
        errors.append("no timeline blocks")
    previous_end = None
    for number, block in enumerate(blocks, 1):
        heading, _, content = block.partition("\n")
        heading = heading.strip()
        label = f"block {number}"
        header = HDR.fullmatch(heading)
        if not header:
            errors.append(f"{label}: bad heading {heading[:80]!r}")
        else:
            start_raw, end_raw, kind = header.groups()
            if kind not in KINDS:
                errors.append(f"{label}: unsupported kind {kind!r}")
            try:
                start, end = seconds(start_raw), seconds(end_raw)
            except ValueError as exc:
                errors.append(f"{label}: invalid timestamp: {exc}")
            else:
                if end < start:
                    errors.append(f"{label}: end before start")
                if previous_end is not None and start < previous_end:
                    errors.append(f"{label}: overlaps or precedes the previous block")
                if limit is not None and (start > limit or end > limit):
                    errors.append(f"{label}: timestamp exceeds clip duration ({limit}s ceiling)")
                previous_end = end

        fields = list(FIELD.finditer(content))
        names = [field.group(1) for field in fields]
        if names != FIELDS:
            errors.append(f"{label}: fields must occur exactly once in order {FIELDS}; got {names}")
        for index, field in enumerate(fields):
            stop = fields[index + 1].start() if index + 1 < len(fields) else len(content)
            value = content[field.end():stop].strip()
            if not value:
                errors.append(f"{label}: empty {field.group(1)}; use — or GAP explicitly")
            elif field.group(1) == "Facts" and not (
                value in {"—", "GAP"} or value.startswith(("- ", "* "))
            ):
                errors.append(f"{label}: Facts must be bullets, —, or GAP")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", help="timeline ids, filenames, or paths")
    parser.add_argument("--inventory", type=Path, default=INV)
    parser.add_argument("--quiet", action="store_true", help="print failures and summary only")
    args = parser.parse_args(argv)
    try:
        inventory = load_inventory(args.inventory)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"FAIL inventory: {exc}")
        return 1
    if args.files:
        files = []
        for name in args.files:
            path = Path(name)
            if path.is_absolute() or path.exists() or len(path.parts) > 1:
                candidate = path
            else:
                candidate = TDIR / (name if path.suffix else name + ".md")
            if candidate not in files:
                files.append(candidate)
    else:
        files = sorted((p for p in TDIR.glob("*.md") if p.stem.isdigit()), key=lambda p: int(p.stem))
    bad = 0
    for path in files:
        errors = check(path, inventory)
        if errors:
            bad += 1
            print(f"FAIL {path.name}:")
            for error in errors:
                print(f"    - {error}")
        elif not args.quiet:
            print(f"ok   {path.name}")
    if not args.files:
        for clip in sorted(set(inventory) - {p.stem for p in files}, key=int):
            bad += 1
            print(f"FAIL {clip}.md: inventory clip has no timeline")
    if not files:
        bad += 1
        print("FAIL no numeric timelines selected")
    print(f"\n{len(files)} timelines checked, {bad} failed")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
