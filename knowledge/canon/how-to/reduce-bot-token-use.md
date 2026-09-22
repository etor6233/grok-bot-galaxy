# Reduce repeated work and bot token use

Source: Day 1, 2026-09-15, engineering, PM, and founder workshops. These are qualitative techniques demonstrated or recommended on stage; the recordings provide **no measured token-savings benchmark**.

| If this repeats | Change the workflow | Evidence |
|---|---|---|
| Browser clicks for the same job | Prefer available APIs/tools; learn the workflow once, then reuse an appropriate callable interface | [059, 02:30–05:15](../../timelines/059.md) |
| Fresh verification scripts for every agent | Build one reusable driver and a feature map; execute and maintain it | [028, 00:00–03:15](../../timelines/028.md) |
| Polling with nothing new | Reduce frequency or use an incoming signal; stay quiet on no-op runs | [059, 02:30–05:15](../../timelines/059.md); [051, 00:00–01:35](../../timelines/051.md) |
| Every bot replying in a group | Use a targeted mention or one-time handoff when that suffices | [060, 05:10–08:50](../../timelines/060.md) |
| Teaching each bot the same rule | Keep one owned playbook and distribute the changed rule once | [026, 01:16–04:35](../../timelines/026.md) |
| A manager remembering every active PR | Keep task/stage/agent references in an external board and read the relevant rows | [026, 05:03–06:29](../../timelines/026.md) |
| Unrelated history interfering with a role | Partition by expertise; ask to forget specific obsolete topics | [059, 05:15–09:59](../../timelines/059.md); [060, 05:10–08:50](../../timelines/060.md) |
| The same human correction | Ask the bot to learn it, or assign a bot to audit repeated failures and routines | [059, 00:00–02:30 and 05:15–06:35](../../timelines/059.md) |

## Set cadence from the job

Every 15 minutes means **96 scheduled runs per day** (24 × 4). The presenter rounded this to “100”; it was a cost illustration, not a recommended cadence. A daily pulse, event trigger, or temporary urgent monitor serves a different need. The engineering P0 example removed its five-minute monitor when the task reached the named stage. [059, 02:30–05:15](../../timelines/059.md); [026, 03:47–04:35](../../timelines/026.md)

## Avoid overcorrecting

Persistent bots were presented as an investment: teach, verify, and improve instead of repeatedly replacing them. A narrow role can grow as its competence grows. The founder Q&A also acknowledged that UI automation and authentication still create friction; “use an API” does not establish access to one. [059, 00:00–02:30 and 06:35–09:59](../../timelines/059.md); [060, 00:00–08:50](../../timelines/060.md)

For consuming this repository, start with [the index](../../INDEX.md), open one relevant guide, and follow a timeline link only for the needed evidence. Do not load replay timelines as new facts or load raw recordings. This retrieval practice is repository guidance, not a claimed Grok Bot feature.

Related: [verification](build-and-maintain-verification.md), [shared playbooks](maintain-a-shared-playbook.md).

## Dated addition — Day 2, 2026-09-16

The sales, SDR, and support workshops add the following techniques. They do not establish a universal cheapest setup or a guaranteed percentage saving.

| Source of avoidable work | Apply this change | Evidence |
|---|---|---|
| Searching all tickets for “Alex” | Pass the exact ticket ID or bounded set of IDs | [111, 01:20–02:15](../../timelines/111.md) |
| Opening a browser for a supported operation | Prefer a suitable authorized MCP; keep computer use for gaps | [089, 00:00–01:14](../../timelines/089.md) |
| Routine runs without an actionable change | Fit the cadence to the job; compare daily and weekly batches | [087, 05:35–06:53](../../timelines/087.md); [102, 00:00–04:05](../../timelines/102.md) |
| Routing a small known task through a whole fleet | Ask the relevant specialist directly when coordination adds no value | [089, 00:00–01:14](../../timelines/089.md) |
| Several bots doing overlapping jobs | Reuse an existing bot/routine; split only when the workload needs it | [101, 05:55–09:05](../../timelines/101.md) |
| Every support ticket loading the full complex workflow | Bucket simple cases and constrain the context they need | [110, 08:25–09:59](../../timelines/110.md) |
| Repeatedly reconstructing shared project context | Point the bot at the maintained plan or durable digest | [072, 02:05–04:00](../../timelines/072.md); [104, 05:45–09:58](../../timelines/104.md) |
| Excessive conversational output | Request a concise response style | [072, 00:00–02:05](../../timelines/072.md) |

**Choose coordination deliberately.** Simon's chief-of-staff pattern reduces human context switching and gives parallel workers a shared goal. The sales presenter preferred direct specialist conversations for some tasks. These are compatible choices for different workloads; extra orchestration itself consumes work. Low-context research workers and bounded batches help control scope, but more parallel agents do not imply fewer total tokens. [089, 00:00–01:14](../../timelines/089.md); [101, 05:55–09:05](../../timelines/101.md); [102, 00:00–04:05](../../timelines/102.md)

**Measure against useful output.** The presenters advised measuring the actual instance because research depth, enrichment, usage-data context, classifiers, and evaluation steps vary. A practical editorial application is to compare a small representative batch before/after one change, keeping answer quality and handoff checks constant. This comparison procedure is a recommendation derived from the discussion, not a demonstrated Grok Bot cost dashboard. [101, 09:05–09:59](../../timelines/101.md); [102, 00:00–04:05](../../timelines/102.md); [110, 08:25–09:59](../../timelines/110.md)

The reported **$20–30 for a slide deck** and **$1–2 for a medium/complex ticket** were individual anecdotes on September 16. They are neither prices nor transferable budgets. Amrita said response style could be adjusted, but did not identify a user control for computer-use intensity. [072, 00:00–02:05](../../timelines/072.md); [110, 08:25–09:59](../../timelines/110.md)

Related: [team coordination](operate-a-bot-team.md), [SDR workflow](run-sdr-prospecting.md), [support workflow](run-customer-support.md).
