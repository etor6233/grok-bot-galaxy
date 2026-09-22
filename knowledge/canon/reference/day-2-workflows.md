# Day 2 workflow and evidence map

> Event date: **2026-09-16**. Editorial distillation: **2026-09-22**. Scope: all **48 existing timelines, 065–112**. Review used the written timelines, not raw ASR/OCR, frames, or recordings. “Aligned” is inherited ingest metadata, not a claim of independent audiovisual verification.

Read a task guide first. Open the linked timeline for exact on-screen wording, spoken attribution, or a clip-local timestamp. Filename/module labels follow the recordings and can span unrelated sessions.

## Task routes

| Need | Guide |
|---|---|
| Technical customer answers, competitor comparisons, case-study slides | [Sales engineering](../how-to/run-sales-engineering.md) |
| Meeting prep, account research, call follow-up, account plans | [Sales workflows](../how-to/run-sales-workflows.md) |
| ICP, enrichment, ranking, draft outreach, sequence state | [SDR prospecting](../how-to/run-sdr-prospecting.md) |
| Ticket answers, policy decisions, handoffs, KB improvement | [Customer support](../how-to/run-customer-support.md) |
| Shared plans, specialists, verification, fleet updates | [Team coordination](../how-to/operate-a-bot-team.md) |
| Cadence, exact IDs, bounded context, MCPs | [Token usage](../how-to/reduce-bot-token-use.md) |

## Coverage by clip range

Every ID from 065 through 112 is included below. Ranges describe reviewed content, not uninterrupted demonstration time.

| Clips | Content | Evidence entry points |
|---|---|---|
| 065–066 | Pop-up → game-studio pivot; proposed game, monetization, pstack planning | [065 · 00:00:00–00:05:00](../../timelines/065.md); [066 · 00:08:30–00:09:58](../../timelines/066.md) |
| 067–072 | Sales engineering: Sherlock, Serena, Mimi, taught skill, bot-created team; approvals/cost Q&A; return to build | [068 · 00:01:40–00:09:43](../../timelines/068.md); [071 · 00:00:00–00:09:36](../../timelines/071.md) |
| 073–078 | Cupcake planning, adjustable prototypes, visual iteration, engineering handoffs; 074 technical break; coffee-shop customer story | [075 · 00:01:30–00:09:59](../../timelines/075.md); [077 · 00:02:40–00:05:00](../../timelines/077.md) |
| 079–081 | Karen X. Cheng: newspaper, package/stock trackers, API-connected devices, login friction | [079 · 00:03:10–00:09:59](../../timelines/079.md); [081 · 00:00:00–00:04:21](../../timelines/081.md) |
| 082–085 | Game UI, client/server boundary, visual assets, animation experiments, reusable bot roles | [083 · 00:06:10–00:09:58](../../timelines/083.md); [084 · 00:02:05–00:09:58](../../timelines/084.md) |
| 086–090 | Build handoff; sales workshop, demos, token advice, templates; intermission | [087 · 00:03:56–00:09:59](../../timelines/087.md); [089 · 00:00:00–00:06:15](../../timelines/089.md) |
| 091–093 | Guest stories: listings, sponsor proposals, knowledge search, bills; coordination friction; Nokia Cursor case study | [091 · 00:01:19–00:07:48](../../timelines/091.md); [092 · 00:03:50–00:09:19](../../timelines/092.md); [093](../../timelines/093.md) |
| 094–098 | Job-search bot fleet and writer/critic loop; Remotion assets; SDR session opening | [095 · 00:00:00–00:06:35](../../timelines/095.md); [098 · 00:01:00–00:02:35 and 00:06:07–00:09:59](../../timelines/098.md) |
| 099–102 | SDR workflow, research roles, CSV state, draft-only sequences, cadence; return to game build | [100](../../timelines/100.md); [101](../../timelines/101.md); [102 · 00:00:00–00:04:05](../../timelines/102.md) |
| 103–107 | Notion/Slack operations, Fleet Pulse, game backend, ads research, animation/audio bots; support handoff | [104 · 00:01:25–00:03:00 and 00:05:45–00:09:58](../../timelines/104.md); [107](../../timelines/107.md) |
| 108–111 | Support setup, sandbox refunds, handoffs, internal Q&A, human-approved knowledge changes, eval/PR suggestions | [109](../../timelines/109.md); [110](../../timelines/110.md); [111](../../timelines/111.md) |
| 112 | Day-end sound direction, working login, import/leaderboard bugs, fleet audit, next-day plans | [112 · 00:03:20–00:09:34](../../timelines/112.md) |

## Additional patterns and their limits

**Personal and business automations.** Customer stories described a POS-connected chief of staff, scheduled printed newspapers, package and stock alerts, sales listings, sponsor proposals, and job-search research. The reusable pattern is a defined input, one output, an appropriate schedule/trigger, and an explicit point for human decisions. Printer discovery, iMessage control, and third-party service access were described without a complete reproducible setup; these notes do not establish universal plug-and-play support. [077 · 00:02:40–00:05:00](../../timelines/077.md), [079–081 entry](../../timelines/079.md), [091 · 00:01:19–00:05:19](../../timelines/091.md), [095 · 00:00:00–00:04:30](../../timelines/095.md).

**Code as creative source.** The studio generated visual assets and translated game styling into Remotion compositions at multiple aspect ratios. The reusable lesson is to keep assets/styles available to the agent and inspect rendered output. It does not make Remotion, image-generation providers, or the pstack playbooks built-in Grok Bot features. [096 · 00:01:20–00:05:45](../../timelines/096.md), [098 · 00:01:00–00:02:35](../../timelines/098.md), [103 · 00:05:40–00:08:40](../../timelines/103.md).

## Evidence boundaries and dated clarifications

- **Approval behavior:** the “finished work” pitch in 067 is qualified by the actual Ask first/Allow automatically UI in [071 · 00:06:55–00:08:55](../../timelines/071.md) and blocked/approved actions in [109–110 entry](../../timelines/109.md). Autonomy does not remove configured approvals.
- **Templates:** Lauren described selective/generic memories alongside skills and routines in [065 · 00:02:30–00:05:00](../../timelines/065.md). This is a dated statement; it is not proof that every template exports memory safely or a reason to silently replace Day 1 duplicate/template notes.
- **Game rules changed:** the rarity pools in [073 · 00:07:00–00:08:10](../../timelines/073.md) differ from [075 · 00:00:00–00:01:30](../../timelines/075.md); later discussion revisits mint permanence. Authentication and hosting also changed. Treat every Cupcake claim as a timestamped project state, never a Grok Bot capability.
- **End-of-day completion:** real login was reported working, but bot import and leaderboard bugs remained in [112 · 00:03:20–00:05:00](../../timelines/112.md). Day 2 does not establish a fully launched product.
- **Names and transcript gaps:** Karen spells **Cheng** in [081 · 00:03:20–00:04:21](../../timelines/081.md), resolving earlier “Chang” notes. **Plain** is explicit in [109](../../timelines/109.md), while 108 transcribes “Plane.” The sales introduction names Krista/Mark, while later demo attribution says Chris; that identity mismatch remains unresolved. [067](../../timelines/067.md) records an ASR loop around 00:03:35–00:05:43; 072 marks model-name uncertainty.
- **Privacy and scope:** recording-machine/private-window interruptions are excluded from product evidence. Fictional sales/support customers, Stripe sandbox actions, guest anecdotes, bot-generated competitive claims, and the Cursor-specific Nokia story must retain those labels. No credential values were needed to distill the workflows.

This reference preserves the difference between demonstrated behavior, presenter advice, proposals, and unresolved gaps. Current product availability, pricing, contest eligibility, and external links were not verified as part of this historical distillation.
