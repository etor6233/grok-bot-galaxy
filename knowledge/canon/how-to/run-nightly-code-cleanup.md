# Run a nightly code cleanup

Source: Lingxi Li, Grok Bot for Engineers, [024](../../timelines/024.md)–[025](../../timelines/025.md). Dated 2026-09-15. Marketplace bot: **Nightly Audit Engineer** (from the Grok Bot Team, by Lingxi Li) — "researches a whole codebase, then ships one cleanup PR per area."

## Why night

"Sloppy code" accumulates when every agent applies different rules. Cleaning at night means:

- nobody is shipping → fewer conflicts,
- the changes are low-risk mechanical slops (condense modules, trim long comments),
- you wake up to a set of ready PRs.

## Setup

1. Install Nightly Audit Engineer from the Marketplace (Grok Bot Team).
2. Onboard it: "Please create your routines and write your memories" (plus role details).
3. Set a named repository scope and cadence. The live demo saved **4 a.m., paused**, then armed the run manually. The preceding narration described a **3 a.m.** setup; these are distinct examples, not one product default. [024, 02:30–04:23](../../timelines/024.md); [025, 02:00–02:45 and 06:30–07:30](../../timelines/025.md)
4. Specify who may merge. The actual FlyLo briefing required **human-owned merges** and the audit bot explicitly accepted that boundary. [025, 00:00–02:00](../../timelines/025.md)

## What it audits

Code quality, missing modularization, over-long comments, and security audits ("very important to prevent someone else to [sneak] something").

## Sequence (as demoed)

1. Research pass first: one research-only cloud agent per repo area (booking-frontend, web, crew-app, factory) — all read-only.
2. Cleanup agents start only after the research reports aggregate.
3. Each cleanup opens one PR per area; the bot boards the row when the PR opens, never merges, never touches other owners' PRs (negotiated mandate — see [FlyLo fleet](../reference/flylo-engineering-fleet.md)).
4. First live cleanup seen: factory "dead API + leftover poll".

## Merge policy

**Dated clarification, 2026-09-15:** Lingxi discussed conditional automatic merging as a general pattern in [024, 02:30–04:23](../../timelines/024.md). The subsequently demonstrated FlyLo fleet kept merges with humans. Do not treat the earlier discussion as permission to override the demo fleet's rule. Compare [Lauren's separate review flow](wire-pr-reviews-into-slack.md).
