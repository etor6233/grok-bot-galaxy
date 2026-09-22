# Turn product data into a reviewed prototype

Source: Day 1 PM workshop, 2026-09-15, [048](../../timelines/048.md)–[051](../../timelines/051.md). **FlyLo Airlines and its numbers are a seeded demo**, not Grok Bot production metrics. The recording ends with engineering in progress, not a verified final release. [049, 02:18–02:47](../../timelines/049.md); [050, 08:27–09:59](../../timelines/050.md)

## Set up the roles

| Bot in demo | Responsibility | Required context shown |
|---|---|---|
| Ashley | Data questions, charts, success metrics | Connected data warehouse |
| PM Pete | Short PRD with priorities and non-goals | Customer/product context; Notion |
| Pixel | Design alternatives and acceptance notes | Figma design system, visual preferences |
| Emily | Break down work and coordinate verification | Engineering team and repositories |
| Engineer bots | Implement scoped changes via cloud agents | Runnable code and test environment |

Roster sources: [048, 04:58–07:55](../../timelines/048.md); [050, 03:13–07:40](../../timelines/050.md). Names are examples of user-created roles, not required product components.

## Follow the demonstrated handoffs

1. Ask a concrete data question: purchases yesterday by mobile versus web. Request charts and definitions for the breakdowns you care about. Ashley queried the external data layer and returned the split. [049, 02:47–05:52](../../timelines/049.md)
2. Validate the diagnosis before writing requirements. The presenters thought seat selection was the largest drop; Ashley corrected it to **search → fare selection, 53.8% step conversion**. Seat/extras was 82.4%. [049, 05:52–08:37](../../timelines/049.md)
3. Ask the data bot to tag the product bot with the finding and draft a concise PRD. Pete separated P0 fare selection, P1 mid-funnel health, P2 seat polish, and non-goals. Review the doc and leave comments; the presenters described bots reading Notion comments. [049, 07:38–09:14](../../timelines/049.md); [050, 00:00–01:48](../../timelines/050.md)
4. Lock the metric and constraints. The demo targeted fare selection **53.8% → 65% in 90 days**; overall conversion **17.4% → 20%** depended on keeping mid-funnel steps at least 80%. Honest fares and no account wall constrained the design. These are demo targets, not measured improvements. [050, 03:13–04:23](../../timelines/050.md)
5. Hand the PRD to design and engineering in parallel. Pixel offered cabin-ladder and price-led alternatives; humans chose cabin ladder and forwarded that choice to Emily. [050, 01:08–01:48 and 04:23–05:35](../../timelines/050.md)
6. Let the engineering manager assign bounded work: Eileen UI, Larry API payload, Nova instrumentation, Einstein QA, Igor performance. Emily's brief limited repositories and prohibited merges without the human. [050, 05:35–06:31](../../timelines/050.md)
7. Review implementation evidence against the original goal. Nova requested permission to launch a cloud agent, explicitly **PR only, no merge**. The proposed review layers were engineer → QA/engineering manager → human as needed. [050, 06:31–08:27](../../timelines/050.md)

```mermaid
flowchart LR
  A[Business question] --> B[Ashley: data and diagnosis]
  B --> C[Pete: concise PRD]
  C --> D[Pixel: alternatives]
  C --> E[Emily: scoped engineering]
  D --> F[Human selects design]
  F --> E
  E --> G[Cloud agents]
  G --> H[Evidence and review]
```

## Keep the loop useful

Ask the chief of staff to compare actual attention with priorities, and stay quiet when nothing material changed. A daily data routine can deliver a pulse instead of requiring dashboard visits; the demo used **6 AM PT**, not a product default. [048, 02:47–03:43](../../timelines/048.md); [049, 04:02–05:52](../../timelines/049.md); [051, 00:00–01:35](../../timelines/051.md)

Related: [verification](build-and-maintain-verification.md), [shared playbooks](maintain-a-shared-playbook.md), [memory and architecture caveats](../reference/day-1-memory-and-computer-limits.md).
