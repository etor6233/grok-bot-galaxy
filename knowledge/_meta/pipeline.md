# Capture and publication pipeline

Capture runs locally under explicit maintainer authorization. Ordinary readers and agents use the published timelines and canon. See [AGENTS.md](../../AGENTS.md) and the [evidence policy](evidence-policy.md).

## Stages

1. **Inventory:** stable clip IDs, recording dates, primary content module and duration.
2. **Machine extraction:** scene selection, local speech recognition and OCR. This uses compute but no hosted LLM inference tokens; it is not free of hardware/time cost.
3. **Alignment:** authorized text packs become compressed timestamped records with Spoken / On screen / Actions / Facts. Unrecoverable content is explicit.
4. **Distillation:** timeline evidence becomes task guides, explanation and reference. Event-only material goes into `session/`.
5. **Publication:** deterministic indexes, link/schema/metadata checks, tests and staged-file review.

Raw material stays in ignored `knowledge/sources/`, recording files and model directories. It is never required for public-data CI or normal retrieval.

## Optional local prerequisites

Python 3.11+ and `python -m pip install -r requirements-capture.txt`. Install FFmpeg/ffprobe and Tesseract separately. ASR requires an FFmpeg build with the Whisper filter and a compatible local model. Executables are discovered through PATH or explicit environment overrides:

| Variable | Purpose |
|---|---|
| `GBG_FFMPEG` | FFmpeg executable |
| `GBG_FFPROBE` | ffprobe executable |
| `GBG_TESSERACT` | Tesseract executable |
| `GBG_WHISPER_MODEL` | Local model path |
| `GBG_WHISPER_USE_GPU` | `1` for GPU or `0` for CPU |
| `GBG_RUNTIME_DIR` | Optional local temporary working directory |

These tools are local prerequisites, not bundled product features. Missing tools fail with an actionable error. Do not install or invoke capture dependencies merely to read the guide.

## Commands for an authorized ingest

```bash
python scripts/manifest.py
python scripts/driver.py --ids 153-157
python scripts/validate_timelines.py 153.md 154.md 155.md 156.md 157.md
python scripts/build_catalog.py
python scripts/validate_repository.py
```

The manifest preserves historical rows when local recordings are absent. Existing identities are not renumbered; collisions and unrecognized recording identities require review. Primary content may differ from the filename: clips 035-042 are engineering replays, and 047 is a transition.

The driver resumes completed extraction, checks recent files for growth, logs failures and stores metrics/warnings in coverage. `--force` reruns selected extraction; it does not authorize raw-source reading or imply a new editorial review. Never mark a clip distilled just because a file exists. Align, review for reusable facts, record the result, then rebuild indexes.

## Quality boundaries

OCR and ASR may hallucinate, lose speech, miss UI transitions or misname people. Mechanical normalization handles known obvious variants but cannot establish uncertain facts. A representative screen sample cannot certify every frame. Inspect one keyframe only when needed to repair specific on-screen copy; never feed a whole video to a model to bypass the evidence workflow.

Clip boundaries can split sentences. Replays point to original material; new replay-only evidence is preserved as a dated addendum. Recording-machine timestamps do not establish broadcast clock times.

The repository currently accounts for 157 supplied clips. Captured duration includes replays and breaks, and uses duration_seconds when available with a HH:MM:SS fallback for the initial 18 clips. It is not unique instructional runtime or proof of uninterrupted event coverage.
