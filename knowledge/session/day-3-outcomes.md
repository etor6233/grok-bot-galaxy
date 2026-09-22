# Day 3 outcomes and remaining limits

Dated 2026-09-17. Summary of the recorded session, not the current state of the product or game. Detailed evidence is in clips 113–157.

**Thursday Arena launched as a public playtest.** The team demonstrated a working game, repeated UI changes, a feedback-to-engineering loop, bot-driven reporting, and several business workflows. The closing sponsor test failed; the recording does not establish earned revenue.

| Workstream | Recorded outcome | Material limit |
|---|---|---|
| Game launch | Playtest released as Thursday Arena; sign-ins and gameplay observed | Bugs remained throughout the day |
| Engineering | PR previews, playtesting, review and merging coordinated by bots | Duplicate work, conflicts and inconsistent bot statuses persisted; a closing production outage was reported |
| Feedback | Web and phone input reached Slack; bots investigated reports | Moderation instructions were not proof of immunity to malicious input |
| Growth | Notion playbook, ranked hypotheses and win-share implementation work | No validated conversion lift for the full proposed playbook |
| Partnerships | ICP, audience hypotheses, source-qualified outreach drafts | Clay and Amplemarket were not connected in that demonstration; no signed partnership shown |
| Post-sales | Draft packs, account reset, staff deliberation and a published ROI form | Customer sending stayed held; live Meet join was incomplete |
| Marketing | Research-to-positioning-to-page pipeline; paused ads shell; earlier-data analysis | New ads spending remained held; three further campaigns were scoped, not proven completed |
| Payments | Link approval/cancellation discussion; paid placement implementation | Canceled purchase demo; final sponsor moderation failure; no demonstrated settled revenue |

Evidence: launch in [122 · 00:04:15–00:07:30](../timelines/122.md); operating workflow in [126](../timelines/126.md) and [127](../timelines/127.md); partnership limits in [134](../timelines/134.md); post-sales in [136](../timelines/136.md) and [137](../timelines/137.md); campaign states in [149](../timelines/149.md) and [150](../timelines/150.md); final failure in [157 · 00:07:43–00:09:26](../timelines/157.md).

The final refreshed data pack was timestamped approximately **16:15 PT**. Its counters describe different populations and must not be added together:

| Reported measure | Snapshot |
|---|---:|
| Practice sessions | 4,884 |
| X signups | 1,902 |
| Reported practice → X conversion | 7.7% |
| SAP arena matches | 1,794 |
| Public matches | 6,546 |
| Reported public win rate | 48.5% |
| Unique public players | 1,020 |
| Feedback items | 371 |
| Vercel visitors | 3,477 |
| Vercel pageviews | 28,521 |

The bot disclosed that the **16:00 scheduled pulse failed** before producing this refresh. Vercel Analytics had been enabled after the morning launch. The 7.7% funnel figure is the bot's reported conversion metric, not the quotient of all X signups and practice sessions. The goal of 2,000 signups was not verified in the final recording. [Snapshot and failure disclosure](../timelines/157.md), [analytics collection window](../timelines/152.md).

The closing sequence contains a useful reliability lesson. Around 00:02:55 in clip 157, Matt reported that a bad SQL query from the software factory brought production down. Around 00:07:33 he said production was back. The subsequent sponsor walkthrough still failed moderation at roughly 00:09:08. These are host-reported service states and an observed failed transaction flow; they do not establish a comprehensive recovery check or revenue.

The hosts also acknowledged that the livestream audience gave the launch unusual distribution, and that their normal engineering review was more rigorous. Their reusable lessons were to agree on a focused idea, learn the domain, remove unnecessary features, verify the work and carry an improved workflow into the next product. [Review rigor](../timelines/153.md), [distribution and scope retrospective](../timelines/156.md).

For actionable patterns, use [launch monitoring](../canon/how-to/monitor-a-product-launch.md), [verified feedback fixes](../canon/how-to/triage-feedback-and-verify-fixes.md), and the [capability boundaries](../canon/reference/day-3-capability-boundaries.md).
