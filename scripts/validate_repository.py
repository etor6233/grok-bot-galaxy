"""Validate the public knowledge repository without reading local capture material.

Run from any directory: python scripts/validate_repository.py
Requires PyYAML. Diagnostics never include matched credential or phone values.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
import html
import math
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import unicodedata
from urllib.parse import unquote, urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".json", ".py", ".toml", ".sh",
                 ".ps1", ".js", ".ts", ".css", ".html", ".svg", ".csv", ".tsv", ".ini"}
RAW_SUFFIXES = {".mp4", ".mov", ".mkv", ".webm", ".wav", ".mp3", ".m4a", ".flac",
                ".srt", ".vtt", ".bin", ".gguf"}
RAW_NAMES = {"ocr.json", "ocr.md", "pack.md", "transcript.json", "transcript.md"}
STAGES = ("scenes", "ocr", "asr", "aligned", "distilled")
STATES = {"done", "pending", "running", "failed", "blocked", "skipped"}
MOJIBAKE = re.compile(r"\ufffd|\u00c3[\u0080-\u00bf]|\u00c2[\u0080-\u00bf]|\u00e2[\u0080-\u00bf\u20ac]|\u00f0\u0178|\u00ef\u00bb\u00bf")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
INLINE_LINK = re.compile(r"!?\[(?:\\.|[^\]\\\n])*\]\(\s*(<[^>\n]+>|(?:\\.|[^()\s]|\([^()\n]*\))+)(?:\s+[\"'][^\n]*?[\"'])?\s*\)")
REFERENCE_LINK = re.compile(r"(?m)^ {0,3}\[[^\]\n]+\]:\s*(<[^>\n]+>|\S+)")
SECURITY_PATTERNS = (
    ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("credential token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk_(?:live|test)_[A-Za-z0-9]{20,}|sk-(?:proj-|ant-)?[A-Za-z0-9_-]{24,}|AKIA[A-Z0-9]{16}|xox[baprs]-[A-Za-z0-9-]{20,})\b")),
    ("Slack webhook", re.compile(r"https://hooks\.slack\.com/services/[A-Za-z0-9]+/[A-Za-z0-9]+/[A-Za-z0-9]{16,}")),
    ("credential assignment", re.compile(r"(?i)\b(?:api[_-]?key|access[_-]?token|client[_-]?secret|password)\b\s*[:=]\s*['\"]?[A-Za-z0-9+/_=-]{24,}")),
    ("phone number", re.compile(r"(?<![\w])\+[1-9](?:[ ().-]*\d){9,14}(?![\w])|(?<![\w])(?:\(\d{3}\)|\d{3})[ .-]\d{3}[ .-]\d{4}(?![\w])")),
)


@dataclass(frozen=True)
class Issue:
    path: str
    message: str
    line: int | None = None

    def __str__(self) -> str:
        location = self.path + (f":{self.line}" if self.line else "")
        return f"{location}: {self.message}"


def excluded_material(path: str) -> bool:
    """Classify paths without opening them, including accidentally tracked sources."""
    item = PurePosixPath(path.replace("\\", "/"))
    parts = tuple(p.lower() for p in item.parts)
    return (parts[:2] == ("knowledge", "sources") or "_probe" in parts or "keyframes" in parts
            or parts[:3] == ("knowledge", "_meta", "models")
            or item.suffix.lower() in RAW_SUFFIXES or item.name.lower() in RAW_NAMES)


def secret_file(path: str) -> bool:
    item = PurePosixPath(path)
    name = item.name.lower()
    return ((name == ".env" or name.startswith(".env."))
            and name not in {".env.example", ".env.sample", ".env.template"}
            or item.suffix.lower() in {".pem", ".key", ".p12", ".pfx"}
            or name in {"credentials.json", "id_rsa", "id_ed25519"})


def git_paths(root: Path, *, tracked_only: bool = False) -> list[str]:
    command = ["git", "-C", str(root), "ls-files", "-z", "--cached"]
    if not tracked_only:
        command += ["--others", "--exclude-standard"]
    result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return sorted(set(result.stdout.decode("utf-8").split("\0")) - {""})


def check_security(path: str, text: str) -> list[Issue]:
    # Only isolated synthetic negative fixtures are exempt; tests and scripts still get scanned.
    if path.startswith("scripts/tests/fixtures/security/"):
        return []
    issues = []
    for line_number, line in enumerate(text.splitlines(), 1):
        for name, pattern in SECURITY_PATTERNS:
            if pattern.search(line):
                issues.append(Issue(path, f"possible {name}; inspect locally (value suppressed)", line_number))
    return issues


def markdown_body(text: str, path: str) -> tuple[str, list[Issue]]:
    """Mask fenced code and comments while preserving source line numbers."""
    result, issues = [], []
    opened: tuple[str, int, int] | None = None
    for number, line in enumerate(text.splitlines(), 1):
        match = FENCE.match(line)
        if match:
            marks, tail = match.groups()
            if opened is None:
                opened = (marks[0], len(marks), number)
            elif marks[0] == opened[0] and len(marks) >= opened[1] and not tail.strip():
                opened = None
            result.append("")
        else:
            result.append("" if opened else line)
    if opened:
        issues.append(Issue(path, "unclosed fenced code block", opened[2]))
    visible = "\n".join(result)
    visible = re.sub(r"<!--[\s\S]*?-->", lambda m: "\n" * m[0].count("\n"), visible)
    return visible, issues


def heading_anchors(text: str) -> set[str]:
    visible, _ = markdown_body(text, "")
    anchors = set(re.findall(r"<(?:a|[a-z][a-z0-9]*)\b[^>]*?\b(?:id|name)=[\"']([^\"']+)[\"']", visible, re.I))
    headings = re.findall(r"(?m)^ {0,3}#{1,6}\s+(.+?)(?:\s+#+)?\s*$", visible)
    headings += re.findall(r"(?m)^([^\n]+)\n {0,3}(?:={3,}|-{3,})\s*$", visible)
    for heading in headings:
        heading = re.sub(r"!?\[([^]]+)\]\([^)]*\)", r"\1", heading)
        heading = html.unescape(re.sub(r"<[^>]*>", "", heading)).lower()
        base = "".join(c for c in heading if c in "-_" or not unicodedata.category(c).startswith(("P", "S")))
        base = re.sub(r"\s", "-", base)
        slug, suffix = base, 0
        while slug in anchors:
            suffix += 1
            slug = f"{base}-{suffix}"
        anchors.add(slug)
    return anchors


def exact_case_exists(path: Path, root: Path) -> bool:
    current = root
    for part in path.relative_to(root).parts:
        if not current.is_dir() or part not in {p.name for p in current.iterdir()}:
            return False
        current /= part
    return True


def check_markdown(root: Path, path: Path, text: str) -> list[Issue]:
    relative = path.relative_to(root).as_posix()
    body, issues = markdown_body(text, relative)
    body = re.sub(r"(`+)([^\n]*?)\1", lambda m: " " * len(m[0]), body)
    matches = list(INLINE_LINK.finditer(body)) + list(REFERENCE_LINK.finditer(body))
    for match in matches:
        target = html.unescape(match[1].strip("<>"))
        target = re.sub(r"\\([() ])", r"\1", target)
        line = body.count("\n", 0, match.start()) + 1
        try:
            parsed = urlsplit(target)
        except ValueError:
            issues.append(Issue(relative, "malformed link target", line))
            continue
        if parsed.scheme or parsed.netloc:
            if parsed.scheme == "file" or len(parsed.scheme) == 1:
                issues.append(Issue(relative, "nonportable local file link", line))
            continue
        link_path = unquote(parsed.path)
        candidate = ((root / link_path.lstrip("/")) if link_path.startswith("/")
                     else path.parent / link_path) if link_path else path
        candidate = Path(os.path.abspath(candidate))
        resolved = candidate.resolve()
        if not resolved.is_relative_to(root):
            issues.append(Issue(relative, "relative link escapes repository", line))
            continue
        if excluded_material(resolved.relative_to(root).as_posix()):
            issues.append(Issue(relative, "link points to unpublished capture material", line))
            continue
        if not resolved.exists() or not exact_case_exists(candidate, root):
            issues.append(Issue(relative, "missing relative link target or filename case mismatch", line))
            continue
        if parsed.fragment and resolved.suffix.lower() == ".md":
            try:
                anchors = heading_anchors(resolved.read_text(encoding="utf-8"))
            except (OSError, UnicodeError):
                issues.append(Issue(relative, "cannot read linked Markdown target", line))
                continue
            if unquote(parsed.fragment) not in anchors:
                issues.append(Issue(relative, "missing Markdown heading or explicit anchor", line))
    return issues


def seconds(value: object) -> int:
    match = re.fullmatch(r"(\d+):([0-5]\d):([0-5]\d)", str(value))
    if not match:
        raise ValueError("invalid HH:MM:SS duration")
    h, m, s = map(int, match.groups())
    return h * 3600 + m * 60 + s


def frontmatter(text: str) -> dict:
    match = re.match(r"\A---\s*\n(.*?)\n---(?:\s*\n|\Z)", text, re.S)
    if not match:
        raise ValueError("missing YAML frontmatter")
    result = yaml.safe_load(match[1])
    if not isinstance(result, dict):
        raise ValueError("frontmatter must be a mapping")
    return result


def check_metadata(root: Path, inventory: dict, coverage: dict, *, expected_count: int = 157) -> list[Issue]:
    inv_path, cov_path = "knowledge/_meta/inventory.yaml", "knowledge/_meta/coverage.yaml"
    issues: list[Issue] = []
    clips = inventory.get("clips", [])
    if not isinstance(clips, list) or any(not isinstance(c, dict) for c in clips):
        return [Issue(inv_path, "clips must be a list of mappings")]
    ids = [str(c.get("id", "")) for c in clips]
    if any(not value.isdigit() for value in ids):
        return [Issue(inv_path, "clip IDs must be numeric strings")]
    numbers = [int(value) for value in ids]
    if len(set(numbers)) != len(numbers):
        issues.append(Issue(inv_path, "duplicate clip IDs, including alternate zero padding"))
    if set(numbers) != set(range(1, expected_count + 1)) or len(clips) != expected_count:
        issues.append(Issue(inv_path, f"expected exactly contiguous clip IDs 1–{expected_count}"))
    by_id = dict(zip(ids, clips))
    timeline_paths = [p for p in (root / "knowledge/timelines").glob("*.md") if p.stem.isdigit()]
    if {p.stem for p in timeline_paths} != set(ids):
        issues.append(Issue(inv_path, "inventory IDs do not match numeric timeline filenames"))
    for path in timeline_paths:
        rel = path.relative_to(root).as_posix()
        if (path.is_symlink() or not path.resolve().is_relative_to(root)
                or excluded_material(path.resolve().relative_to(root).as_posix())):
            issues.append(Issue(rel, "timeline must not be a symlink"))
            continue
        try:
            data = frontmatter(path.read_text(encoding="utf-8"))
        except (OSError, ValueError, yaml.YAMLError) as exc:
            issues.append(Issue(rel, f"invalid frontmatter ({type(exc).__name__})"))
            continue
        clip = by_id.get(path.stem)
        if clip:
            for key, expected in (("clip", path.stem), ("file", clip.get("file")),
                                  ("day", clip.get("day")), ("module", clip.get("module")),
                                  ("duration", clip.get("duration"))):
                if str(data.get(key)) != str(expected):
                    issues.append(Issue(rel, f"frontmatter {key} differs from inventory"))

    actual_modules: dict[str, list[str]] = defaultdict(list)
    total_seconds = 0.0
    for clip_id, clip in by_id.items():
        if not all(clip.get(key) for key in ("file", "day", "module", "duration")):
            issues.append(Issue(inv_path, f"clip {clip_id} lacks required metadata"))
            continue
        actual_modules[str(clip["module"])].append(clip_id)
        try:
            displayed = seconds(clip["duration"])
            duration = float(clip.get("duration_seconds", displayed))
            if not math.isfinite(duration) or duration <= 0:
                raise ValueError("duration must be positive")
            total_seconds += duration
        except (TypeError, ValueError):
            issues.append(Issue(inv_path, f"clip {clip_id} has invalid duration"))
    event = inventory.get("event", {})
    if isinstance(event, dict) and "dates" in event:
        dates = event["dates"]
        if (not isinstance(dates, list) or Counter(map(str, dates))
                != Counter(set(str(c.get("day")) for c in clips))):
            issues.append(Issue(inv_path, "event.dates do not match clip dates"))
    modules = inventory.get("modules", {})
    if not isinstance(modules, dict):
        issues.append(Issue(inv_path, "modules must be a mapping"))
        modules = {}
    if set(modules) != set(actual_modules):
        issues.append(Issue(inv_path, "module names do not match primary clip modules"))
    for name, members in modules.items():
        if not isinstance(members, dict) or not isinstance(members.get("clips"), list):
            issues.append(Issue(inv_path, f"module {name} requires a clips list"))
            continue
        listed = [str(i) for i in members["clips"]]
        if Counter(listed) != Counter(actual_modules.get(name, [])):
            issues.append(Issue(inv_path, f"module {name} is not the exact primary clip partition"))
        dates = {str(by_id[i]["day"]) for i in listed if i in by_id and "day" in by_id[i]}
        if "day" in members and dates != {str(members["day"])}:
            issues.append(Issue(inv_path, f"module {name} day disagrees with member clips"))
    manifest = inventory.get("manifest", {})
    if not isinstance(manifest, dict) or manifest.get("total_clips") != len(clips):
        issues.append(Issue(inv_path, "manifest.total_clips is inconsistent"))
    if isinstance(manifest, dict):
        for key, expected, tolerance in (("total_duration_seconds", total_seconds, 0.051),
                                          ("total_duration_h", total_seconds / 3600, 0.0051)):
            try:
                valid = math.isclose(float(manifest[key]), expected, rel_tol=0, abs_tol=tolerance)
            except (KeyError, TypeError, ValueError):
                valid = False
            if not valid:
                issues.append(Issue(inv_path, f"manifest.{key} is inconsistent"))

    status = coverage.get("status", {})
    if not isinstance(status, dict):
        return issues + [Issue(cov_path, "status must be a mapping")]
    status = {str(k): v for k, v in status.items()}
    if set(status) != set(ids):
        issues.append(Issue(cov_path, "per-clip status IDs do not match inventory"))
    for clip_id, row in status.items():
        if not isinstance(row, dict):
            issues.append(Issue(cov_path, f"clip {clip_id} status must be a mapping"))
            continue
        for stage in STAGES:
            if not isinstance(row.get(stage), str) or row[stage] not in STATES:
                issues.append(Issue(cov_path, f"clip {clip_id} has invalid {stage} status"))
        if clip_id in {p.stem for p in timeline_paths} and row.get("aligned") != "done":
            issues.append(Issue(cov_path, f"clip {clip_id} has a published timeline but is not aligned/done"))
        if row.get("distilled") == "done" and row.get("aligned") != "done":
            issues.append(Issue(cov_path, f"clip {clip_id} distilled before alignment"))
        sources = row.get("canon_sources", [])
        if not isinstance(sources, list):
            issues.append(Issue(cov_path, f"clip {clip_id} canon_sources must be a list"))
            sources = []
        for source in sources:
            source_path = root / str(source)
            if (not isinstance(source, str) or not source.startswith("knowledge/canon/")
                    or not source_path.resolve().is_relative_to(root / "knowledge/canon")
                    or not source_path.is_file()):
                issues.append(Issue(cov_path, f"clip {clip_id} has an invalid canon_sources path"))
    flags = {"machine_complete": STAGES[:3], "aligned_complete": ("aligned",), "distilled": ("distilled",)}
    if "distilled_complete" in coverage:
        flags["distilled_complete"] = ("distilled",)
    for flag, stages in flags.items():
        expected = bool(ids) and set(status) == set(ids) and all(
            isinstance(status[i], dict) and all(status[i].get(stage) == "done" for stage in stages)
            for i in ids)
        if not isinstance(coverage.get(flag), bool) or coverage[flag] != expected:
            issues.append(Issue(cov_path, f"{flag} disagrees with per-clip states"))
    return issues


def check_generated_outputs(root: Path, outputs: dict[Path, str]) -> list[Issue]:
    issues = []
    for path, content in outputs.items():
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            issues.append(Issue(path.relative_to(root).as_posix(), "stale generated file; run python scripts/build_catalog.py"))
    return issues


def validate(root: Path, *, expected_count: int = 157, check_catalog: bool = True) -> list[Issue]:
    root = root.resolve()
    issues: list[Issue] = []
    unsafe_tree = False
    try:
        tracked = set(git_paths(root, tracked_only=True))
        paths = git_paths(root)
    except (OSError, UnicodeError, subprocess.CalledProcessError):
        return [Issue(".", "cannot inspect Git file list; run validation in a Git checkout")]
    for relative in paths:
        if excluded_material(relative) or secret_file(relative):
            if relative in tracked:
                issues.append(Issue(relative, "tracked capture or secret file is forbidden (contents not read)"))
            continue
        path = root / relative
        if (path.is_symlink() or not path.resolve().is_relative_to(root)
                or excluded_material(path.resolve().relative_to(root).as_posix())):
            issues.append(Issue(relative, "public files must not link outside the checkout or be symlinks"))
            unsafe_tree = True
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"LICENSE", ".gitignore", ".gitattributes"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            issues.append(Issue(relative, "public text is not readable UTF-8"))
            continue
        for number, line in enumerate(text.splitlines(), 1):
            if MOJIBAKE.search(line):
                issues.append(Issue(relative, "replacement character or likely UTF-8 mojibake", number))
        issues.extend(check_security(relative, text))
        if path.suffix.lower() == ".md":
            issues.extend(check_markdown(root, path, text))
    try:
        metadata_paths = [root / f"knowledge/_meta/{name}.yaml" for name in ("inventory", "coverage")]
        if unsafe_tree or any(path.is_symlink() or not path.resolve().is_relative_to(root)
                              or excluded_material(path.resolve().relative_to(root).as_posix())
                              for path in metadata_paths):
            raise ValueError("unsafe metadata paths")
        documents = [yaml.safe_load(path.read_text(encoding="utf-8")) for path in metadata_paths]
        if not all(isinstance(doc, dict) for doc in documents):
            raise ValueError("metadata must be mappings")
        issues.extend(check_metadata(root, *documents, expected_count=expected_count))
    except (OSError, ValueError, yaml.YAMLError) as exc:
        issues.append(Issue("knowledge/_meta", f"cannot load metadata ({type(exc).__name__})"))
    if check_catalog and not unsafe_tree:
        try:
            try:
                from . import build_catalog
            except ImportError:
                import build_catalog
            original_root = build_catalog.ROOT
            try:
                build_catalog.ROOT = root
                issues.extend(check_generated_outputs(root, build_catalog.outputs()))
            finally:
                build_catalog.ROOT = original_root
        except (OSError, ValueError, KeyError, TypeError, yaml.YAMLError) as exc:
            issues.append(Issue("knowledge/catalog.json", f"cannot regenerate catalog ({type(exc).__name__})"))
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="repository checkout to validate")
    args = parser.parse_args()
    issues = validate(args.root)
    for issue in issues:
        print(issue)
    print(f"Public repository validation: {len(issues)} error(s). Raw capture contents were not read.")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
