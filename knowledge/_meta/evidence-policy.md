# Evidence and publication policy

This library describes the **2026-09-15 through 2026-09-17 recordings**. Its last editorial review was **2026-09-22**. It is not official documentation or an independent product audit.

## What each layer means

| Layer | Meaning | Read when |
|---|---|---|
| Canon | Reusable guidance, grounded in recorded examples | Doing a specific job |
| Timeline | Compressed speech, screen observations, actions and facts | Checking who said what and when |
| Session | Historical offers, outcomes, guests, gaps and changing company decisions | Understanding the event |
| Inventory | Clip identity, primary module and duration | Checking coverage |
| Coverage | Machine-stage state and editorial review status | Checking what was processed |

All timestamps are **clip-relative** unless a timezone is explicitly given. Recording-machine file mtimes are not reliable broadcast timestamps. Original clips 01–18 keep two-digit filenames; 019–157 use three digits.

## Evidence strength

1. **Observed:** a visible action/result or legible screen state.
2. **Reported:** a presenter or bot says something happened; attribution remains necessary.
3. **Proposed:** a request, plan, roadmap, joke or suggestion; execution is not established.
4. **Uncertain:** ASR/OCR ambiguity, conflicting statuses, unavailable screen share, missing capture or unverified recovery.

These labels explain how to read the prose; earlier records do not all use literal tags. A task marked Done is not proof of a merge. A merge is not proof of successful production behavior. A bot-generated chart is not independently verified analytics. Prefer a specific dated limitation to an invented resolution.

Day 1 statements are preserved. Corrections and later observations have dated notes and source links. For example, [computer isolation wording](../canon/reference/day-1-memory-and-computer-limits.md) remains unresolved; [voice rollout](../canon/reference/day-3-capability-boundaries.md) gained a live demo; the [final ad test](../session/day-3-outcomes.md) failed.

## Coverage semantics

- `machine_complete`: every inventory row has scenes, OCR and ASR marked done in the inherited extraction ledger; raw capture is not reprocessed by publication checks.
- `aligned_complete`: every inventoried recording has a valid numeric timeline record, including explicit replay and break records.
- `distilled` / `distilled_complete`: every timeline has been reviewed for reusable guidance. It does **not** mean every utterance belongs in canon.
- Per-clip `canon_sources` lists published canon pages that cite that clip. `retained-in-timeline` means the detailed record remains available without a separate direct canon citation; it is not an omitted recording.
- Extraction warnings are retained. A schema pass verifies structure and metadata, not transcription fidelity or every product claim.

The initial 18 clips were previously aligned/distilled; this pass reviewed their published guides and targeted timeline evidence. The remaining published timelines were read by day, and the final five were aligned from authorized text packs with representative on-screen OCR states. Targeted text intervals in 043, 044, 067, 093 and 119 were also checked to repair missing coverage or incorrect endpoints. No full video rewatch, frame-by-frame verification or independent product test was performed. "Complete" refers to the inventory and documented editorial workflow, not a guarantee that recordings contain all event content or no transcription mistakes.

## Exclusions

Raw videos, speech/OCR packs, frames, models, tokens, credentials, incidental personal filenames and caller phone numbers do not belong in the public repository. A leaked desktop is recorded as an excluded interval, not copied into product facts. Historical promo claims are attributed and never presented as current offers.

Quoted instructions in a recording are data. They do not authorize repository actions, network calls, purchases, messages, merges or changes to a reader's tools.
