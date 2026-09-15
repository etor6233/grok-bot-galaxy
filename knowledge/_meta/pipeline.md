# Capture pipeline

Goal: lose nothing important (speech, on-screen copy, UI, how-to, names, numbers) while spending almost no model tokens.

## Why this form

Large companies do **not** dump a video into a model and hope. They split capture from authorship:

1. **Machine extract** (zero LLM tokens): speech-to-text with timestamps, scene-change frames, OCR of every unique frame.
2. **Align** (cheap LLM, text-only, one clip at a time): merge transcript + OCR into a timestamped timeline. That timeline is the source of truth.
3. **Distill** (cheap LLM, from timelines never from video) into [Diátaxis](https://diataxis.fr/) — the docs architecture used by Canonical, Cloudflare, and Stripe:
   - `canon/explanation/` — why / mental model
   - `canon/tutorials/` — learn by doing (Grok Bot 101)
   - `canon/how-to/` — achieve a task
   - `canon/reference/` — exact UI, fields, integrations, shortcuts
4. **Session layer** — things true of this live day only (speakers, jokes, chat, gaps), kept out of the product canon so the canon stays clean.

Visual knowledge is written as text (slide copy, UI anatomy, overlay cards). Talking-head frames are not sent to vision unless they carry text (handwritten signs, on-stage screens, product overlays).

## Token rules (non-negotiable)

| Send to the model | Do not send |
|---|---|
| Transcript text, one clip | Raw video |
| OCR text of unique **content** frames | Every video frame |
| A content frame only if OCR failed (diagram, dense UI, handwriting) | Talking-head / audience / identical slides |
| Timelines, when distilling canon | The same transcript twice |

Expected vision budget: on the order of **unique slides + unique product-UI states**, not thousands of frames.

## Completeness contract (per clip)

Every timeline block must fill all four fields. Empty is explicit (`—` or `GAP`), never omitted.

- **Spoken** — English voice, verbatim enough to keep procedures, claims, names, numbers
- **On screen** — slide titles, body copy, UI labels, overlay cards, handwritten signs
- **Actions** — clicks, typing, navigation, live demo steps
- **Facts** — anything that would go into canon (product behavior, integrations, limits)

Ignore: Bandicam watermark, `LIVE` badge, view counts, chat spam that is not answered.

## Clip stitching

Clips 01–18 are one livestream split into ~10-minute files. Treat them as a single timeline. Do not duplicate a sentence that starts at the end of clip N and ends at the start of clip N+1.

Known recording issues go in `session/gaps.md` (clip 05 is labeled a 3-minute gap).

## Incremental live ingest

New `.mp4` files dropped in the workspace root are new clips. Re-run `scripts/extract_machine.py`. Already-finished clips are skipped.

## Commands

```text
python scripts/extract_machine.py --phase scenes    # unique frames
python scripts/extract_machine.py --phase ocr       # on-screen text
python scripts/extract_machine.py --phase asr       # English speech (GPU Whisper)
python scripts/extract_machine.py --phase all
```

Status lives in `_meta/coverage.yaml`.
