"""Local machine extraction for clips 01–18 and 019–157: scenes, OCR, ASR.

Install requirements-capture.txt for Python dependencies. External executables
use PATH or GBG_FFMPEG / GBG_TESSERACT; ASR requires FFmpeg's whisper filter and
a model supplied through GBG_WHISPER_MODEL (or the documented local default).
GBG_WHISPER_USE_GPU=0 enables CPU execution; the historical default is 1.
This optional capture pipeline never needs to run to consume the published KB.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
import yaml

from capture_tools import ToolConfigurationError, find_executable

ROOT = Path(__file__).resolve().parents[1]
KNOW = ROOT / "knowledge"
META = KNOW / "_meta"
SOURCES = KNOW / "sources"
INV_PATH = META / "inventory.yaml"
COV_PATH = META / "coverage.yaml"

DEFAULT_WHISPER_MODEL = META / "models" / "ggml-large-v3-turbo.bin"

HASH_SIZE = 16
HASH_HAMMING = 18
SAMPLE_FPS = 1.0
TOP_CROP = 42
BOTTOM_CROP = 58
JPEG_Q = 82
OCR_MIN_CONF = 40
TEXT_CHARS_CONTENT = 48


def load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def save_yaml(path: Path, data: dict) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def set_status(clip_id: str, **fields) -> None:
    cov = ensure_row(clip_id)
    row = cov["status"][clip_id]
    row.update(fields)
    save_yaml(COV_PATH, cov)


def ensure_row(clip_id: str) -> dict:
    """Return coverage; create the clip row lazily (multi-day ingest)."""
    cov = load_yaml(COV_PATH)
    if clip_id not in cov["status"]:
        cov["status"][clip_id] = {}
    return cov


def file_stable(clip: dict, settle_s: int = 30) -> tuple[bool, str]:
    """Refuse files that Bandicam may still be writing.

    Files older than 10 minutes are trusted as-is; recent files must keep the
    same byte size across `settle_s` seconds.
    """
    src = ROOT / clip["file"]
    if not src.exists():
        return False, "file missing"
    if time.time() - src.stat().st_mtime > 600:
        return True, ""
    s1 = src.stat().st_size
    time.sleep(settle_s)
    s2 = src.stat().st_size
    if s1 != s2:
        return False, f"still growing {s1} -> {s2} bytes"
    return True, ""


def probe_duration_seconds(clip_id: str) -> float | None:
    """Duration from scenes.json (frames/fps); None if scenes not yet run."""
    scenes_path = SOURCES / clip_id / "scenes.json"
    if not scenes_path.exists():
        return None
    data = json.loads(scenes_path.read_text(encoding="utf-8"))
    return round(data["frames"] / data["fps"], 2)


def qc_check(clip: dict) -> None:
    """Metric gates per clip; warnings land in coverage.yaml, never silent."""
    clip_id = clip["id"]
    cov = load_yaml(COV_PATH)
    row = cov["status"].get(clip_id, {})
    warns: list[str] = []
    if row.get("asr") == "done":
        wpm = row.get("asr_wpm")
        if wpm is not None and wpm < 25:
            warns.append(f"low WPM {wpm} — possible silent/corrupt audio")
        if wpm is not None and wpm > 400:
            warns.append(f"high WPM {wpm} — possible ASR hallucination spam")
    if row.get("ocr") == "done" and row.get("ocr_chars", 0) < 300:
        warns.append(f"sparse OCR {row.get('ocr_chars')} chars")
    inv_sec = clip.get("duration_seconds")
    probe = row.get("duration_probe")
    if inv_sec and probe is not None and abs(inv_sec - probe) > 30:
        warns.append(
            f"duration mismatch probe {probe}s vs manifest {inv_sec}s — file truncated?"
        )
    row["warnings"] = warns
    save_yaml(COV_PATH, cov)


NORMALIZE_RULES: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\bGrogbots?\b", re.I), "Grok Bot"),
    (re.compile(r"\bGarkbots?\b", re.I), "Grok Bot"),
    (re.compile(r"\bRockbots?\b", re.I), "Grok Bot"),
    (re.compile(r"\bMCIs\b"), "MCPs"),
    (re.compile(r"\bship to Maine\b", re.I), "ship to main"),
    (re.compile(r"\bpoll request\b", re.I), "pull request"),
    (re.compile(r"\bpoll requests\b", re.I), "pull requests"),
    (re.compile(r"\bAnne[- ]?Rita\b", re.I), "Amrita"),
    (re.compile(r"\bAnrita\b", re.I), "Amrita"),
    (re.compile(r"\bDr\.?\s*Ipod\b", re.I), "Dr. Eggbot"),
]


def normalize_text(text: str) -> str:
    """Conservative fix of known Whisper errors (raw transcript only)."""
    for pat, repl in NORMALIZE_RULES:
        text = pat.sub(repl, text)
    return text


def clip_dir(clip_id: str) -> Path:
    d = SOURCES / clip_id
    (d / "keyframes").mkdir(parents=True, exist_ok=True)
    return d


def dhash(bgr: np.ndarray, size: int = HASH_SIZE) -> np.ndarray:
    h, w = bgr.shape[:2]
    gray = cv2.cvtColor(bgr[TOP_CROP : max(TOP_CROP + 1, h - BOTTOM_CROP), :], cv2.COLOR_BGR2GRAY)
    small = cv2.resize(gray, (size + 1, size), interpolation=cv2.INTER_AREA)
    return (small[:, 1:] > small[:, :-1]).flatten()


def hamming(a: np.ndarray, b: np.ndarray) -> int:
    return int(np.count_nonzero(a != b))


def mean_luma(bgr: np.ndarray) -> float:
    h, w = bgr.shape[:2]
    crop = bgr[TOP_CROP : max(TOP_CROP + 1, h - BOTTOM_CROP), :]
    return float(cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY).mean())


def classify(kind_luma: float, ocr_chars: int) -> str:
    if kind_luma < 12:
        return "gap"
    if ocr_chars >= TEXT_CHARS_CONTENT:
        return "content"
    return "talking_head"


def extract_scenes(clip: dict) -> dict:
    clip_id = clip["id"]
    src = ROOT / clip["file"]
    out = clip_dir(clip_id)
    scenes_path = out / "scenes.json"
    if scenes_path.exists():
        return json.loads(scenes_path.read_text(encoding="utf-8"))

    cap = cv2.VideoCapture(str(src))
    if not cap.isOpened():
        raise RuntimeError(f"cannot open {src}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    nframes = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    step = max(1, int(round(fps / SAMPLE_FPS)))
    prev_hash = None
    scenes: list[dict] = []
    idx = 0
    frame_i = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if frame_i % step != 0:
            frame_i += 1
            continue
        t = frame_i / fps
        hsh = dhash(frame)
        changed = prev_hash is None or hamming(prev_hash, hsh) >= HASH_HAMMING
        if changed:
            name = f"{idx:04d}_{int(t*1000):08d}.jpg"
            path = out / "keyframes" / name
            cv2.imwrite(str(path), frame, [int(cv2.IMWRITE_JPEG_QUALITY), JPEG_Q])
            scenes.append(
                {
                    "i": idx,
                    "t": round(t, 3),
                    "file": f"keyframes/{name}",
                    "luma": round(mean_luma(frame), 1),
                    "kind": "pending",
                }
            )
            prev_hash = hsh
            idx += 1
        frame_i += 1
    cap.release()
    payload = {
        "clip": clip_id,
        "file": clip["file"],
        "fps": fps,
        "frames": nframes,
        "unique_scenes": len(scenes),
        "scenes": scenes,
    }
    scenes_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    set_status(
        clip_id,
        scenes="done",
        scenes_n=len(scenes),
        frames=nframes,
        duration_probe=round(nframes / fps, 2),
    )
    print(f"[{clip_id}] scenes={len(scenes)} duration_frames={nframes}")
    return payload


def tesseract_tsv(image: Path) -> tuple[str, list[dict]]:
    cmd = [
        find_executable("tesseract"),
        str(image),
        "stdout",
        "--psm",
        "6",
        "-l",
        "eng",
        "tsv",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        raise RuntimeError(
            "Tesseract OCR failed; check the executable and English language data. "
            + proc.stderr.strip()[-800:]
        )
    lines = proc.stdout.splitlines()
    if not lines:
        return "", []
    header = lines[0].split("\t")
    words: list[dict] = []
    texts: list[str] = []
    for line in lines[1:]:
        cols = line.split("\t")
        if len(cols) != len(header):
            continue
        row = dict(zip(header, cols))
        if row.get("level") != "5":
            continue
        text = (row.get("text") or "").strip()
        try:
            conf = float(row.get("conf", "-1"))
        except ValueError:
            conf = -1.0
        if not text or conf < OCR_MIN_CONF:
            continue
        words.append(
            {
                "t": text,
                "c": round(conf, 1),
                "x": int(row["left"]),
                "y": int(row["top"]),
                "w": int(row["width"]),
                "h": int(row["height"]),
            }
        )
        texts.append(text)
    # retry sparse UI if block mode found almost nothing
    if len(" ".join(texts)) < 20:
        cmd[4] = "11"
        proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if proc.returncode != 0:
            raise RuntimeError("Tesseract sparse OCR retry failed: " + proc.stderr.strip()[-800:])
        lines = proc.stdout.splitlines()
        words, texts = [], []
        if lines:
            header = lines[0].split("\t")
            for line in lines[1:]:
                cols = line.split("\t")
                if len(cols) != len(header):
                    continue
                row = dict(zip(header, cols))
                if row.get("level") != "5":
                    continue
                text = (row.get("text") or "").strip()
                try:
                    conf = float(row.get("conf", "-1"))
                except ValueError:
                    conf = -1.0
                if not text or conf < OCR_MIN_CONF:
                    continue
                words.append(
                    {
                        "t": text,
                        "c": round(conf, 1),
                        "x": int(row["left"]),
                        "y": int(row["top"]),
                        "w": int(row["width"]),
                        "h": int(row["height"]),
                    }
                )
                texts.append(text)
    joined = " ".join(texts)
    return joined, words


def extract_ocr(clip: dict) -> dict:
    clip_id = clip["id"]
    out = clip_dir(clip_id)
    ocr_path = out / "ocr.json"
    scenes_path = out / "scenes.json"
    if ocr_path.exists():
        return json.loads(ocr_path.read_text(encoding="utf-8"))
    scenes = json.loads(scenes_path.read_text(encoding="utf-8"))
    items = []
    for sc in scenes["scenes"]:
        img = out / sc["file"]
        text, words = tesseract_tsv(img)
        kind = classify(sc["luma"], len(text))
        sc["kind"] = kind
        items.append(
            {
                "i": sc["i"],
                "t": sc["t"],
                "kind": kind,
                "file": sc["file"],
                "text": text,
                "n_words": len(words),
                "words": words,
            }
        )
        print(f"  [{clip_id}] t={sc['t']:.1f}s kind={kind} chars={len(text)}")
    scenes_path.write_text(json.dumps(scenes, indent=2), encoding="utf-8")
    payload = {"clip": clip_id, "frames": items}
    ocr_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    md_lines = [f"# OCR {clip_id}", ""]
    for it in items:
        if not it["text"].strip():
            continue
        ts = int(it["t"])
        h, m, s = ts // 3600, (ts % 3600) // 60, ts % 60
        md_lines.append(f"## {h:02d}:{m:02d}:{s:02d}  {it['kind']}")
        md_lines.append(it["text"])
        md_lines.append("")
    (out / "ocr.md").write_text("\n".join(md_lines), encoding="utf-8")
    set_status(
        clip_id,
        ocr="done",
        ocr_frames=len(items),
        ocr_chars=sum(len(it["text"]) for it in items),
    )
    return payload


def ff_filter_path(path: Path) -> str:
    # Filter options are colon-separated; Windows drive letters must be escaped.
    return str(path.resolve()).replace("\\", "/").replace(":", "\\:")


def runtime_model() -> Path:
    """FFmpeg filter graphs split on ':'. Keep model/output off spaced paths."""
    model = Path(os.path.expandvars(os.environ.get("GBG_WHISPER_MODEL", str(DEFAULT_WHISPER_MODEL)))).expanduser()
    if not model.is_file() or model.stat().st_size == 0:
        raise ToolConfigurationError(
            "Whisper model missing or empty. Set GBG_WHISPER_MODEL to a local "
            "whisper.cpp-compatible model, or place ggml-large-v3-turbo.bin in "
            "knowledge/_meta/models/. Models are not downloaded automatically."
        )
    rt = Path(os.path.expandvars(os.environ.get("GBG_RUNTIME_DIR", str(Path(tempfile.gettempdir()) / "grok-bot-galaxy")))).expanduser()
    rt.mkdir(parents=True, exist_ok=True)
    # A fixed basename also supports user-supplied model paths containing spaces.
    dest = rt / "whisper-model.bin"
    if dest.resolve() == model.resolve():
        return dest
    if not dest.exists() or (
        dest.stat().st_size != model.stat().st_size
        or dest.stat().st_mtime_ns != model.stat().st_mtime_ns
    ):
        print(f"copying Whisper model -> {dest}")
        shutil.copy2(model, dest)
    return dest


@lru_cache(maxsize=1)
def whisper_ffmpeg() -> str:
    """Check the required FFmpeg filter once, before starting a batch's ASR."""
    ffmpeg = find_executable("ffmpeg")
    proc = subprocess.run(
        [ffmpeg, "-hide_banner", "-filters"], capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=30,
    )
    if proc.returncode != 0 or not re.search(r"^\s*\S+\s+whisper\s+", proc.stdout, re.M):
        raise ToolConfigurationError(
            "ASR requires an FFmpeg build with the whisper audio filter. "
            "Check `ffmpeg -filters` and point GBG_FFMPEG to a compatible build."
        )
    return ffmpeg


def extract_asr(clip: dict) -> None:
    clip_id = clip["id"]
    src = ROOT / clip["file"]
    out = clip_dir(clip_id)
    dest_json = out / "transcript.json"
    srt = out / "transcript.srt"
    if srt.exists() and srt.stat().st_size > 8:
        if not dest_json.exists():
            dest_json.write_text(
                json.dumps({"clip": clip_id, "format": "srt", "path": srt.name}, indent=2),
                encoding="utf-8",
            )
        set_status(clip_id, asr="done")
        return
    ffmpeg = whisper_ffmpeg()
    gpu = os.environ.get("GBG_WHISPER_USE_GPU", "1")
    if gpu not in {"0", "1"}:
        raise ToolConfigurationError("GBG_WHISPER_USE_GPU must be 0 (CPU) or 1 (GPU).")
    model = runtime_model()
    work = model.parent
    rt_srt = work / f"{clip_id}.srt"
    if rt_srt.exists():
        rt_srt.unlink()
    # cwd=work avoids drive-letter colons in the filter graph.
    # queue=8s keeps sentence context without the 20s CPU stall.
    af = (
        f"whisper=model={model.name}:language=en:use_gpu={gpu}:queue=8:"
        f"destination={rt_srt.name}:format=srt"
    )
    cmd = [ffmpeg, "-y", "-i", str(src), "-vn", "-af", af, "-f", "null", "-"]
    print(f"[{clip_id}] ASR starting")
    proc = subprocess.run(
        cmd,
        cwd=str(work),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    (out / "asr.stderr.log").write_text(proc.stderr[-30000:], encoding="utf-8")
    if proc.returncode != 0 or not rt_srt.exists() or rt_srt.stat().st_size < 8:
        raise RuntimeError(f"ASR failed for {clip_id}, see asr.stderr.log")
    shutil.move(str(rt_srt), str(srt))
    strip_whisper_hallucinations(srt)
    write_transcript_md(out, clip_id, srt)
    dest_json.write_text(
        json.dumps({"clip": clip_id, "format": "srt", "path": srt.name}, indent=2),
        encoding="utf-8",
    )
    words = len(srt.read_text(encoding="utf-8", errors="replace").split())
    dur = probe_duration_seconds(clip_id)
    wpm = round(words / (dur / 60), 1) if dur else None
    set_status(clip_id, asr="done", asr_words=words, asr_wpm=wpm)
    print(f"[{clip_id}] ASR done bytes={srt.stat().st_size} words={words} wpm={wpm}")


def write_transcript_md(out: Path, clip_id: str, srt: Path) -> None:
    lines = [f"# Transcript {clip_id}", ""]
    block: list[str] = []
    for raw in srt.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n").split("\n"):
        if raw.strip() == "":
            if len(block) >= 3 and "-->" in block[1]:
                start = block[1].split("-->")[0].strip().split(",")[0]
                text = " ".join(block[2:]).strip()
                if text and text not in {"-", ".", "..."}:
                    lines.append(f"**{start}**  {text}")
                    lines.append("")
            block = []
        else:
            block.append(raw)
    if len(block) >= 3 and "-->" in block[1]:
        start = block[1].split("-->")[0].strip().split(",")[0]
        text = " ".join(block[2:]).strip()
        if text and text not in {"-", ".", "..."}:
            lines.append(f"**{start}**  {text}")
            lines.append("")
    (out / "transcript.md").write_text(normalize_text("\n".join(lines)), encoding="utf-8")


def strip_whisper_hallucinations(srt: Path) -> None:
    """Drop trailing repeated thank-you / empty cues typical of silence."""
    raw = srt.read_text(encoding="utf-8", errors="replace")
    blocks = [b.strip() for b in raw.replace("\r\n", "\n").split("\n\n") if b.strip()]
    junk = {"thank you.", "thank you", ".", "...", "thanks.", "you"}
    while blocks:
        lines = blocks[-1].split("\n")
        text = " ".join(lines[2:]).strip().lower() if len(lines) >= 3 else ""
        if text in junk or not text:
            blocks.pop()
            continue
        break
    srt.write_text("\n\n".join(blocks) + ("\n" if blocks else ""), encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--phase", choices=["scenes", "ocr", "asr", "all"], default="all")
    p.add_argument("--clip", type=int, default=None, help="optional clip ID, e.g. 18, 065 or 157")
    args = p.parse_args()
    inv = load_yaml(INV_PATH)
    clips = inv["clips"]
    if args.clip is not None:
        clips = [c for c in clips if int(c["id"]) == args.clip]
        if not clips:
            print(f"unknown clip {args.clip}", file=sys.stderr)
            return 2
    phases = ["scenes", "ocr", "asr"] if args.phase == "all" else [args.phase]
    for clip in clips:
        stable, why = file_stable(clip)
        if not stable:
            print(f"[{clip['id']}] SKIP unstable file: {why}", file=sys.stderr)
            continue
        if "scenes" in phases:
            extract_scenes(clip)
        if "ocr" in phases:
            extract_ocr(clip)
        if "asr" in phases:
            extract_asr(clip)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
