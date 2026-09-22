# Coverage gaps

- Clip **04** ~00:08:07–00:09:19: Whisper “Thank you” loop + **local Windows desktop** leak. Ignore that desktop as product knowledge.
- Clip **05** inside ~00:00:46–00:01:19 is a loading spinner, **not** a 3-minute blackout. The filename “3 minutos de gap” matches the **wall-clock hole after 05** (~13:22:21–13:25:05, ~2:44) before clip 06. Speech does not stitch across that hole.
- Clip **09** ~00:07:01–00:07:28 “Be right back”; ~54s then Engineering (clip 10).
- Clip **10** ~00:02:23–00:06:39 GitHub/Slack/Notion tour **not on the program feed** (broken screen share). Overlay only.
- Clip **16** ~00:06:08–00:06:34 hold slate (email/Vercel invite).
- Clip **18** ends ~00:02:36–00:02:50 hold / technical difficulties. Factory creation is not completed in the initial 01–18 batch; later factory evidence is in [022](../timelines/022.md) onward. Reviewer bot asked, not created.
- File splits are ~10 minutes; a sentence may straddle clip boundaries. Stitch, do not duplicate.
- Wall-clock gaps between files (recording stopped/restarted) to verify after ASR:
  - after 05 (file end 13:22 → 06 end 13:35)
  - after 09 (101 → Engineering, file end 14:02 → 10 end 14:13)
- Whisper misspellings to correct on sight: Grogbot/Rockbot/Garkbot → Grok Bot; Anne-Rita → Amrita; MCIs → MCPs; ship to Maine → ship to main.
- 2026-09-17 (multi-day ingest): clip **104** = "40-2026-09-16.mp4" has no module label in its filename; classified as **sdrs** from the aligned content in [104](../timelines/104.md); reconciled in inventory on 2026-09-22.
- 2026-09-17 (Day 1, clips 019+): capture-machine desktop leaks repeated on the feed — 019 (~00:03:40 cmd window), 020 (~00:00:36–00:04:24 Task Manager), 021 (~00:01:44 unrelated desktop), 023 (~00:06:39 private session window), 025 (~00:09:49 private session window). All excluded from timelines as not-program-content, same policy as the clip-04 leak.
- 2026-09-17 (Day 1, clips 030–034): the livestream **re-aired** the earlier build segment during 17:45–18:35. Clips 030 and 031 are re-airs of the content already aligned in timelines 15–17 (identical events and chat; player timer confirms replay). Timelines 030/031 are duplicate-markers, not re-narrations; check 032–034 the same way.
- 2026-09-17 (Day 1, re-air map completed): **030 → timelines 15–16** (pink decision, popup.git, Vercel) · **031 → 17** (PlanetScale, domain, guest cancelled) · **032 → 18 + 019 opening** (no PRs rule, hold, Cody hello) · **033 → 020** (Cody: ads take, worst advice, distribution, proof vault, bot-build; no deltas) · **034 → 021 + bonus** (restores the ~2-min window lost between files 20–21: ~$2M ad spend, corporate ads ~40%, 1,600 businesses) · **035 → 022** (recap, potato factory, workshop start). All 030–035 are duplicate-markers in `knowledge/timelines/`.
- 2026-09-17 (Day 1): filenames for 030–035 are unreliable — "35-Product Managers" contains the workshop replay; this initial hypothesis was superseded by the completed replay map below. The actual PM introduction starts in 047 around05:12, continuing 048–051. Verify content, not filenames.
- 2026-09-17 (Day 1, re-air map EXTENDED): the replay block runs 030–042 and covers timelines 15–29 in order, with half-file drift (each replay file ≈ one original file + the opening of the next): **030 → 15–16 · 031 → 17 · 032 → 18+019 · 033 → 020 · 034 → 021 (+bonus window) · 035 → 022 · 036 → 023+024-open · 037 → 024+025-open · 038 → 025+026-open · 039 → 026+027-open · 040 → 027+028-open · 041 → 028+029-open · 042 → 029**. Filenames "35–42-Product Managers" all contain workshop/company-build replays. **NEW live content resumes at clip 043** (company build continues), then the real Product Managers session 048–051 and the Founders block 052–064.
- 2026-09-17 (Day 1): wall-clock gap between files 20 and 21 (~15:48:47–15:50:49, ~2 min) — the first capture stopped; content restored from clip 034's re-air and folded into `session/guest-advice-cody-sanchez.md` (dated addendum).

## 2026-09-22 publication review

- [043](../timelines/043.md) and [044](../timelines/044.md): existing tail prose was complete but block endpoints/frontmatter understated duration. Checked the text-pack tails and corrected the metadata.
- [067](../timelines/067.md) 03:35–05:43: repeated ASR "Thank you" output; no reliable speech recovered. UI overview slide visible. This is an extraction limitation, not proof that recording audio was absent.
- [093](../timelines/093.md) 02:42–02:52: no usable speech/OCR in the checked transition; a BRB slate is recovered at 02:52.
- [119](../timelines/119.md) 06:00–09:09: previously unrepresented intermission, now explicitly recorded; music and promotional transition/BRB slate, no completed live task.
- [074](../timelines/074.md) is a short intermission; [118](../timelines/118.md) is a three-second stub. These still count as inventoried recordings.
- Clips 113/115/116 end a few seconds after their final coarse topical timestamp; the notes do not claim frame-accurate segmentation. File splits and recording-machine mtimes can include uncaptured event intervals; do not infer continuous coverage.
- Replay windows 038–041 were capped at their actual recorded duration; the old generic 09:59 endpoints exceeded the files.
- Unrelated recording-machine windows, personal filenames and caller numbers are excluded. Redaction retains the existence of a capture interruption, not its private contents.
- [157](../timelines/157.md): bot reporting pulse failed at 16:00, refreshed around 16:15 PT. Production outage and recovery were reported; final sponsorship remained blocked. These are workflow/outcome limits, not missing recording footage.

All 157 supplied clips have timeline records. That does not eliminate these evidence gaps or establish complete capture of the underlying event.
