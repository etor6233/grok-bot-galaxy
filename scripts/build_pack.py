"""Build local packs for clips 01–18 and 019–157 from existing ASR/OCR.

Only Python's standard library is needed. Packs are derived material under the
gitignored knowledge/sources directory, not published product documentation.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "knowledge" / "sources"
JUNK = re.compile(
    r"www\.?\s*BANDICAM\.com|BANDICAM|LIVE|\d[\d.,]*\s*K\s*views|\d[\d.,]*\s*views",
    re.I,
)


def norm(text: str) -> str:
    t = JUNK.sub(" ", text)
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t


def unique_ocr_blocks(ocr_md: str) -> list[str]:
    blocks: list[tuple[str, str]] = []
    cur_h, cur = None, []
    for line in ocr_md.splitlines():
        if line.startswith("## "):
            if cur_h and cur:
                blocks.append((cur_h, " ".join(cur)))
            cur_h, cur = line, []
        elif line.startswith("# "):
            continue
        elif line.strip():
            cur.append(line.strip())
    if cur_h and cur:
        blocks.append((cur_h, " ".join(cur)))
    kept: list[str] = []
    seen: list[str] = []
    for h, body in blocks:
        body = JUNK.sub(" ", body)
        body = re.sub(r"\s+", " ", body).strip()
        if len(body) < 12:
            continue
        n = norm(body)
        if any(_close(n, prev) for prev in seen[-8:]):
            continue
        seen.append(n)
        kept.append(f"{h}\n{body}")
    return kept


def _close(a: str, b: str) -> bool:
    if a == b:
        return True
    if not a or not b:
        return False
    # cheap overlap: shorter is mostly inside longer
    short, long = (a, b) if len(a) <= len(b) else (b, a)
    return short in long or (len(set(short.split()) & set(long.split())) / max(1, len(short.split())) > 0.82)


def build(clip_id: str) -> Path:
    d = SOURCES / clip_id
    tr = (d / "transcript.md").read_text(encoding="utf-8") if (d / "transcript.md").exists() else ""
    ocr = (d / "ocr.md").read_text(encoding="utf-8") if (d / "ocr.md").exists() else ""
    ocr_u = unique_ocr_blocks(ocr)
    parts = [
        f"# Pack {clip_id}",
        "",
        "## Speech",
        tr.replace(f"# Transcript {clip_id}", "").strip(),
        "",
        "## On-screen (deduped OCR)",
        "\n\n".join(ocr_u) if ocr_u else "_(no OCR yet)_",
        "",
    ]
    path = d / "pack.md"
    path.write_text("\n".join(parts), encoding="utf-8")
    return path


def main() -> int:
    if not SOURCES.is_dir():
        print("No knowledge/sources directory. Packs require an authorized local capture first; the published KB works without them.", file=sys.stderr)
        return 2
    for d in sorted(SOURCES.iterdir()):
        if not d.is_dir():
            continue
        if (d / "transcript.md").exists() or (d / "ocr.md").exists():
            p = build(d.name)
            print(d.name, p.stat().st_size)
    return 0


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    raise SystemExit(main())
