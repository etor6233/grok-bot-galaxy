# Maintaining the guide

Maintainer: **etor6233**. Changes must be grounded in the recordings or explicitly labeled editorial guidance. Do not submit guessed product behavior. This repository documents a historical event.

## Read and change the right layer

Read [llms.txt](llms.txt), [INDEX](knowledge/INDEX.md), then the relevant guide and cited timeline. Follow [AGENTS.md](AGENTS.md) and the [evidence policy](knowledge/_meta/evidence-policy.md). Preserve Day 1 observations; add dated notes for corrections or later evidence. Keep ephemeral counts, promotions and company implementation choices in `knowledge/session/`.

A timeline contains YAML identity plus topical blocks with **Spoken / On screen / Actions / Facts**, in that order. Empty evidence is `—` or `GAP`. Times are relative to the clip; replay records link to the original recording. See the [schema](knowledge/_meta/timeline-schema.md).

## Public-data checks

Python **3.11+** is sufficient; CI uses Python 3.12. No recordings, GPUs, cloud accounts or API keys are needed:

```bash
python -m pip install -r requirements-dev.txt
python scripts/build_catalog.py
python scripts/validate_timelines.py
python scripts/validate_repository.py
python -m unittest discover -s scripts/tests
git diff --check
```

The catalog and both generated indexes must be rebuilt after document edits. Their output is deterministic. `build_catalog.py --check` reports stale files without rewriting them. `validate_timelines.py 153.md 157.md` validates a subset; a full run is required before publication.

Repository checks cover local links, Markdown fences, encoding, clip identity, durations, primary-module membership, coverage flags, generated-file freshness and common accidental disclosure patterns. They do not verify remote links, current product availability, every transcription claim or arbitrary secrets. Review the staged diff as well.

## Capture maintenance

The optional [capture pipeline](knowledge/_meta/pipeline.md) has separate system dependencies and `requirements-capture.txt`. It writes ignored local data. Do not run it during ordinary retrieval or public-data CI. Reading raw extraction requires specific maintainer authorization; normal canon updates read timelines.

## Publication

Use small, descriptive commits; verify tests and the staged file list; exclude all raw capture and personal data. Only the maintainer publishes. Push without force and verify the remote commit and CI result. This repository's historical references to "ship to main" describe a demo policy, not a universal publishing instruction.
