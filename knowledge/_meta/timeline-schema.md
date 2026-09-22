# Timeline schema (lock this)

One file per clip: `knowledge/timelines/NN.md`. `NN` = `01`…`18` (Day 1, two-digit, historical) or `019`…`157` (three-digit global ids across Days 1–3; `knowledge/_meta/inventory.yaml` maps id → file → day → module).

Language: English. Product name: **Grok Bot** (not Grogbot, not Rockbot). Whisper errors: `MCIs` → `MCPs`, `ship to Maine` → `ship to main`, `poll request` → `pull request`. Do not invent names or features.

## Frontmatter

```yaml
---
clip: "019"
file: "19-Engineering- 2026-09-15.mp4"
day: "2026-09-15"
module: engineering   # bienvenida | grok-bot-101 | engineering | product-managers | founders | sales-engineering | sales | sdrs | customer-support | marketing-operations | post-sales | marketing
duration: "00:10:00"
speakers: ["Amrita"]   # only names actually spoken or shown; else Host / Presenter / Guest
status: aligned
---
```

## Blocks

Group into topical beats of ~20–90 seconds. Heading:

```markdown
## 00:01:17–00:02:31  [slide]
```

Kinds: `slide` | `ui-demo` | `talking-head` | `overlay` | `gap`.

**Editorial normalization, 2026-09-22:** earlier ingest aliases `qa`, `q-and-a`, and `interview` map to `talking-head`; `slides` to `slide`; `break` to `gap`; `promo` to `overlay`. Recorded video is classified by its visible content: the Nokia interview in 127 is `talking-head`, and the recap montage in 144 is `overlay`. This changes taxonomy only; the Spoken, On screen, Actions, and Facts content stays intact.

Every block has exactly these four fields, in this order. Empty = `—` or `GAP`, never omitted.

```markdown
**Spoken:** compressed but complete: keep every procedure, claim, name, number, integration, rule. Not a verbatim dump of filler (um, yeah, so).
**On screen:** slide titles, UI labels, overlay cards, handwritten signs. Quote labels. Ignore Bandicam, LIVE, view counts.
**Actions:** clicks, typing, navigation, who is speaking if useful.
**Facts:**
- one atomic product/session fact per bullet
```

## Gold fragment (clip 04 opening)

```markdown
## 00:00:00–00:01:26  [slide]
**Spoken:** Presenter: Grok Bot originated from these product decisions. It should feel like working with teammates: simple, chat-like. Left sidebar lists bots with jobs (Sales Outbound, Inbox Manager), not a new chat per task. You create a bot for a unit of work / job, return to it, and it learns. Example: you say how you like slides formatted; weeks later it remembers. Teammate paradigm, not task paradigm.
**On screen:** "Introducing Grok Bot" product UI. Sidebar bots: Sales Outbound, Chief of Staff, Inbox Manager, Website designer, Debug. Settings for Sales Outbound / Outbound Assistant. Instruction: overnight pipeline generation and outbound from a Google Sheet; research on the web; context from Hex, Sumble, Salesforce; draft email and LinkedIn sequences in the user's voice; check and update daily. Connected: Hex, Gmail, LinkedIn. Salesforce not signed in. Routines: Morning outbound queue (weekdays 8:00 AM), Reply chase (weekdays 11:00 AM), End-of-day send list (paused). Callouts: Create bots for different jobs; Message bots like teammates; Bots keep context in memory; Log bots into your tools; Set up automations and routines; Easily share your bots with others. Marketplace in the chrome.
**Actions:** Presenter walks the screenshot; not a live click-through yet.
**Facts:**
- Bot = persistent job/role you return to, not a disposable chat
- Memory is long-lived (weeks)
- Teammate paradigm, not task paradigm
```

## Rules

- Stitch: if a sentence starts at the end of clip N, finish it here and mark `(continues from NN)` or `(continues on NN)`.
- Chat overlay: only questions the stage answers. Do not dump the chat.
- Gaps: clip 05 filename flags a 3-minute gap; confirm from silence / black frames.
- Vision: if OCR of a unique slide/UI is garbage, `read_file` **one** keyframe for that beat. Never bulk-read talking-head frames.
- Routine documentation work uses published timelines. For specifically authorized ingestion, align `knowledge/sources/NN/pack.md`; do not open additional raw files by default. Keyframes only to repair specific on-screen copy, under AGENTS.md.
