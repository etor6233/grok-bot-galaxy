# Day 1 memory, computers, and sharing: evidence limits

Dated note: **2026-09-15**, distilled from the recorded Day 1 sessions. Preserve these distinctions when answering from this repository; do not turn conflicting descriptions into an asserted architecture.

| Topic | What the recordings support | Limit |
|---|---|---|
| Bot memory | PM Q&A describes individual memory plus an optional shared team memory pool | The files do not specify the storage or synchronization implementation. [051, 03:10–06:10](../../timelines/051.md) |
| Bot computers | 101 says bots have isolated computers; founder Q&A later describes one VM with per-bot instances and a shared filesystem | **Unresolved wording conflict.** Do not infer a security boundary or claim files are private to a bot. [05](../../timelines/05.md), [06](../../timelines/06.md), [061, 00:00–05:00](../../timelines/061.md) |
| Cross-account communication | Founder Q&A says bot-to-bot communication across people/accounts was not available that day and was being explored | Same-workspace delegation and sharing a template do not demonstrate cross-account bot messaging. [061, 00:00–05:00](../../timelines/061.md) |
| Local execution | The presenter describes an existing setting to enable local execution and drive the user's browser | The exact settings path is not shown in this Q&A; no supported-version guarantee. [061, 00:00–05:00](../../timelines/061.md) |
| Template sharing | Matt says sharing copies metadata/instructions and first-party plugins while excluding sensitive content and chat data | This is a presenter description, not an independently audited export schema. [053, 06:04–08:40](../../timelines/053.md) |
| Deterministic policies | Shubh suggests routing decisions through verifiable code and a decision tree | This is a proposed control pattern; neither model behavior nor arbitrary code is thereby guaranteed deterministic. [060, 00:00–03:25](../../timelines/060.md) |
| Authentication | Human login/API-key setup still caused blockers during the demos | Working computer use is not evidence of universal access to every external service. [043, 06:20–08:20](../../timelines/043.md); [060, 00:00–05:10](../../timelines/060.md) |

## Resolve changes by date and scope

Separate memory from filesystem access, and presenter claims from verified behavior. The PM demo's human-owned merges and FlyLo-only repository rule are workspace instructions; the company build's early ship-to-main rule belongs to another setup and later evolved into PR review. [049, 01:21–02:18](../../timelines/049.md); [050, 05:35–07:40](../../timelines/050.md); [18](../../timelines/18.md); [022, 01:29–02:45](../../timelines/022.md)

Related: [computer basics](../how-to/use-the-computer.md), [memory steering](../how-to/steer-memory.md), [sharing templates](../how-to/share-duplicate-marketplace.md).
