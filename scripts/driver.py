"""Resumable per-clip pipeline driver: scenes -> ocr -> asr -> pack -> QC.

Usage:
    python scripts/driver.py            # every clip in inventory order
    python scripts/driver.py --ids 019  # smoke test one clip
    python scripts/driver.py --ids 019-157 --force

Per clip: stability guard (live Bandicam files), machine extract, token-cheap
pack, QC gates. Progress is printed and appended to `_meta/run_*.log`; metrics
and warnings land in `_meta/coverage.yaml`. Finished clips are skipped on re-run.
`--force` revisits finished clips but keeps cached intermediate files; it does
not delete or re-transcribe existing extracts. Configure external tools using
PATH or GBG_FFMPEG / GBG_TESSERACT; see extract_machine.py for Whisper settings.
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import extract_machine as em  # noqa: E402
import build_pack as bp  # noqa: E402


def select_clips(ids: str | None) -> list[dict]:
    inv = em.load_yaml(em.INV_PATH)
    clips = inv["clips"]
    if not ids:
        return clips
    want: list[int] = []
    for part in ids.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            lo_s, hi_s = part.split("-", 1)
            want.extend(range(int(lo_s), int(hi_s) + 1))
        else:
            want.append(int(part))
    known = {int(c["id"]) for c in clips}
    missing = sorted(set(want) - known)
    if missing:
        raise ValueError(f"Requested clip IDs are absent from inventory: {missing}")
    selected = [c for c in clips if int(c["id"]) in want]
    if not selected:
        raise ValueError("No clips selected; use an ID or ascending range such as 019-157")
    return selected


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", default=None, help="e.g. 019, 019-157 or 019,020")
    ap.add_argument("--force", action="store_true", help="revisit done clips; preserve cached intermediate files")
    args = ap.parse_args()

    try:
        clips = select_clips(args.ids)
    except ValueError as exc:
        ap.error(str(exc))
    log_path = ROOT / "knowledge" / "_meta" / f"run_{datetime.now():%Y%m%d_%H%M%S}.log"
    t0 = time.time()
    processed = failed = 0

    def say(msg: str) -> None:
        line = f"[{datetime.now():%H:%M:%S}] {msg}"
        print(line, flush=True)
        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    say(f"driver start: {len(clips)} clips selected -> {log_path.name}")
    for i, clip in enumerate(clips, 1):
        cid = clip["id"]
        row = em.ensure_row(cid)["status"][cid]
        if not args.force and row.get("asr") == "done" and (em.SOURCES / cid / "pack.md").exists():
            say(f"[{i}/{len(clips)}] {cid} skip (already done)")
            continue
        t1 = time.time()
        try:
            stable, why = em.file_stable(clip)
            if not stable:
                say(f"[{i}/{len(clips)}] {cid} SKIP unstable: {why}")
                continue
            em.extract_scenes(clip)
            em.extract_ocr(clip)
            em.extract_asr(clip)
            bp.build(cid)
            em.qc_check(clip)
        except Exception as exc:  # keep the batch alive overnight
            failed += 1
            em.set_status(cid, error=str(exc)[:240])
            say(f"[{i}/{len(clips)}] {cid} ERROR {type(exc).__name__}: {exc}")
            continue
        dt = time.time() - t1
        processed += 1
        cov = em.load_yaml(em.COV_PATH)["status"].get(cid, {})
        eta_min = (len(clips) - i) * (dt / 60)
        say(
            f"[{i}/{len(clips)}] {cid} done in {dt / 60:.1f}m "
            f"wpm={cov.get('asr_wpm', '-')} scenes={cov.get('scenes_n', '-')} "
            f"ocr_chars={cov.get('ocr_chars', '-')} warns={cov.get('warnings', [])} "
            f"eta_remaining~{eta_min:.0f}m"
        )

    cov = em.load_yaml(em.COV_PATH)
    cov.setdefault("runs", []).append(
        {
            "started": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "log": log_path.name,
            "selected": len(clips),
            "processed": processed,
            "failed": failed,
            "elapsed_min": round((time.time() - t0) / 60, 1),
        }
    )
    em.save_yaml(em.COV_PATH, cov)
    say(f"driver end: processed={processed} failed={failed} total={(time.time() - t0) / 60:.1f}m")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
