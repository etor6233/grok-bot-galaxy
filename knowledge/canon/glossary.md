# Glossary

Terms as used on stage and on screen, Grok Bot Galaxy Day 1.

| Term | Meaning here | First seen |
|---|---|---|
| Grok Bot | Product: persistent teammate bots in a chat UI, cloud-hosted, with a computer | 01 / 04 |
| Bot | A named job you return to — not a disposable chat | 04 |
| Teammate paradigm | Bots as colleagues with memory, vs a new chat per task | 04 |
| Computer / Linux VM | Each bot’s isolated machine; drives UIs that have no MCP | 05 |
| MCP / plugin | Native integration (X, Notion, pstack, Vercel, …) from Marketplace | 04–06, 10 |
| Teach a task | You drive the bot’s computer once; recording becomes a **skill** | 05, 09 |
| Skill | Saved procedure (name, description, instructions, typed inputs) | 09 |
| Auto-review | Settings rules: ask first vs allow automatically; Allow once | 05–06 |
| Routine | Scheduled job on a bot (e.g. weekdays 8:00 AM outbound queue) | 04 |
| Group chat | Visibility surface for several bots + you in one thread | 07 |
| Manager / orchestrator | Bot whose job is updates and blockers from specialists | 08 |
| Marketplace | Featured public bots + team plugins; share as template | 06, 09 |
| Share as template | Header control to publish a bot for others to copy | 06–07 |
| Memory | Long-lived; S3; steerable; can be told to forget / stop delegating | 07, 09 |
| Secrets modal | 1Password / API / env secrets in Grok Bot UI, not on the VM | 09 |
| p-stack / P-Stack | Lauren’s open-source Marketplace plugin (skills + eng workflows) | 02, 13 |
| Dr. Eggbot | Factory bot: spawn specialists, install kits | 10–18 |
| steve | Lauren’s chief-of-staff bot | 10–18 |
| grokpot | Prototyper bot (HTML/CSS mocks in-app) | 13–16 |
| tater | Engineering bot; Cursor cloud agents | 17–18 |
| Cloud agent | Cursor cloud VM doing real coding, spawned from Grok Bot | 01, 17 |
| Project agent | Long-running cloud agent that keeps engineering context | 17 |
| Ship by Thursday | Live company / GitHub org for the 72-hour build | 03, 10 |
| Potato / @poteto | Lauren | 01 |
| AI Maturity Curve | Chatbots → Copilots → Bot → Team of Bots | 03–04 |
| Hashbrown | Lauren's reviewer bot (reviews PRs that tater opens) | 022 |
| pstack repo plugin | pstack installed at project scope via `.cursor/settings.json`; cloud agents/automations in the repo get `/poteto-mode` without per-user installs | 022 |
| Cursor automation | Trigger-based automation on Cursor Cloud Agents (e.g. new PR posted to Slack → automation reviews/merges) | 022 |
| Repo AGENTS.md | Repo file routing non-trivial work through `/poteto-mode` (poteto-agent subagent; report failure rather than silently degrade) | 022 |
| Fleet board | Notion board coordinating a bot fleet (schema: Task name, Owner, Stage, PRs, Cloud agent, Last commit) | 024–025 |
| CLEAN ladder | Stage ladder Working → Watching 1/3 → 2/3 → 3/3 → Ready; 4 consecutive CLEAN ticks; Done = merged only | 025 |
| P0 escalation | Routine: bot checks cloud agents every 5 minutes and interrupts off-track/needless tool calls | 025–026 |
| Bot-to-bot onboarding | An existing bot renames and briefs a new bot with fleet rules; new bot absorbs into memory and negotiates mandate conflicts | 025 |
| FlyLo | Lingxi Li's demo airline product (flylo-air.com / book / crew); repo flylo-air/booking-frontend | 024–025 |
| Nightly audit | Overnight code-quality bot (Marketplace): research whole tree, one cleanup PR per area, ~4 a.m. | 024–025 |
| Bugbot | Bot in Lingxi's workspace that owns bug threads (Bugbot/Approval loops on PRs) | 024–025 |
| thursday repo | Ship by Thursday repo `shipbythursday/thursday` (renamed from `popup`, clip 022) | 022 |

## Days 2–3 additions (editorial review 2026-09-22)

The table above preserves Day 1 terminology. Architecture wording is not settled: see [memory and computer limits](reference/day-1-memory-and-computer-limits.md).

| Term | Meaning in this event | Evidence |
|---|---|---|
| Sherlock | Sales-engineering bot grounding technical customer answers in a repository | [068](../timelines/068.md) |
| SDR | Sales development representative; prospect research and outbound workflows | [096](../timelines/096.md) |
| RevOps / MarOps | Revenue / marketing operations; human-owned business processes supported by bots | [113](../timelines/113.md), [119](../timelines/119.md) |
| Juno / Ondes | PM and engineering bots in the Lead Deck case study | [116](../timelines/116.md) |
| Lead Deck | Swipe-style CRM lead-review tool with rep-specific identity and workflow ownership | [116](../timelines/116.md) |
| ICP | Ideal customer profile; a hypothesis to ground research and outreach | [132](../timelines/132.md), [134](../timelines/134.md) |
| Gus | Post-sales chief of staff; coordinates specialists and returns one consolidated pack | [135](../timelines/135.md) |
| Frankie | Follow-up specialist; prepares follow-up work from account/call context | [135](../timelines/135.md), [136](../timelines/136.md) |
| Franny Form | Forms specialist; builds the ROI questionnaire in Google Forms | [136](../timelines/136.md), [137](../timelines/137.md) |
| Wally | Drafting specialist for the user's writing voice | [135](../timelines/135.md) |
| Trudy | Sourced answers from internal documents | [135](../timelines/135.md) |
| Scout | Internal updates radar | [135](../timelines/135.md) |
| Thursday Arena | Public game built during the event; game rules are distinct from Grok Bot capabilities | [122](../timelines/122.md), [155](../timelines/155.md) |
| Cupcake | Earlier project/code name retained in repositories and feedback channels | [154](../timelines/154.md) |
| Bake / Play / Review / Land | Named roles in one engineering verification/merge loop, not required product roles | [157](../timelines/157.md) |
| Mash | Team's potato-themed word for merging a PR | [157](../timelines/157.md) |
| Ghost | Saved opponent board used in Arena's rated play; unrelated to a Grok Bot runtime instance | [155](../timelines/155.md), [156](../timelines/156.md) |
| Voice chat | Two-way bot call demonstrated on Day 3; distinct from earlier voice dictation and the xAI telephone agent | [152](../timelines/152.md), [154](../timelines/154.md) |
| llms.txt / rules.md | Compact entrypoint and Markdown game rules shown for agent consumption | [155](../timelines/155.md) |
| Done / merged / verified | Distinct completion claims that must be checked against their evidence | [153](../timelines/153.md), [157](../timelines/157.md) |
