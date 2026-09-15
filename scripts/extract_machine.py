"""Zero-token machine extract: scenes, OCR, ASR. Incremental per clip."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
KNOW = ROOT / "knowledge"
META = KNOW / "_meta"
SOURCES = KNOW / "sources"
INV_PATH = META / "inventory.yaml"
COV_PATH = META / "coverage.yaml"

FFMPEG = Path(
    r"C:\Users\NL\AppData\Local\Microsoft\WinGet\Packages"
    r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\ffmpeg-9.0.1-full_build\bin\ffmpeg.exe"
)
TESSERACT = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
WHISPER_MODEL = META / "models" / "ggml-large-v3-turbo.bin"

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


def set_status(clip_id: str, **fields: str) -> None:
    cov = load_yaml(COV_PATH)
    row = cov["status"][clip_id]
    row.update(fields)
    save_yaml(COV_PATH, cov)


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
    set_status(clip_id, scenes="done")
    print(f"[{clip_id}] scenes={len(scenes)} duration_frames={nframes}")
    return payload


def tesseract_tsv(image: Path) -> tuple[str, list[dict]]:
    cmd = [
        str(TESSERACT),
        str(image),
        "stdout",
        "--psm",
        "6",
        "-l",
        "eng",
        "tsv",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
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
    set_status(clip_id, ocr="done")
    return payload


def ff_filter_path(path: Path) -> str:
    # Filter options are colon-separated; Windows drive letters must be escaped.
    return str(path.resolve()).replace("\\", "/").replace(":", "\\:")


def runtime_model() -> Path:
    """FFmpeg filter graphs split on ':'. Keep model/output off spaced paths."""
    if not WHISPER_MODEL.exists():
        raise FileNotFoundError(f"missing Whisper model: {WHISPER_MODEL}")
    rt = Path(os.environ.get("LOCALAPPDATA", r"C:\Temp")) / "gbg-models"
    rt.mkdir(parents=True, exist_ok=True)
    dest = rt / WHISPER_MODEL.name
    if not dest.exists() or dest.stat().st_size != WHISPER_MODEL.stat().st_size:
        print(f"copying Whisper model -> {dest}")
        shutil.copy2(WHISPER_MODEL, dest)
    return dest


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
    model = runtime_model()
    work = model.parent
    rt_srt = work / f"{clip_id}.srt"
    if rt_srt.exists():
        rt_srt.unlink()
    # cwd=work avoids drive-letter colons in the filter graph.
    # queue=8s keeps sentence context without the 20s CPU stall.
    af = (
        f"whisper=model={model.name}:language=en:use_gpu=1:queue=8:"
        f"destination={rt_srt.name}:format=srt"
    )
    cmd = [str(FFMPEG), "-y", "-i", str(src), "-vn", "-af", af, "-f", "null", "-"]
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
    set_status(clip_id, asr="done")
    print(f"[{clip_id}] ASR done bytes={srt.stat().st_size}")


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
    (out / "transcript.md").write_text("\n".join(lines), encoding="utf-8")


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
    p.add_argument("--clip", default=None, help="optional clip id, e.g. 18")
    args = p.parse_args()
    inv = load_yaml(INV_PATH)
    clips = inv["clips"]
    if args.clip:
        want = args.clip.zfill(2)
        clips = [c for c in clips if c["id"] == want]
        if not clips:
            print(f"unknown clip {args.clip}", file=sys.stderr)
            return 2
    phases = ["scenes", "ocr", "asr"] if args.phase == "all" else [args.phase]
    for clip in clips:
        if "scenes" in phases:
            extract_scenes(clip)
        if "ocr" in phases:
            extract_ocr(clip)
        if "asr" in phases:
            extract_asr(clip)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
