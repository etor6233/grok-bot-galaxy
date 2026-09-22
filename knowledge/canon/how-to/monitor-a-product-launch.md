# Monitor a product launch with a data bot

Evidence: Day 3, 2026-09-17. Roshan's Thursday Arena launch used a configured **Data** bot and connected production sources. The numbers below are historical snapshots.

1. Give the bot the relevant data definitions and access. The studio connected its application database, Vercel, GitHub and other operational tools.
2. Define a compact launch pulse: timestamp, key counts, changes since the prior snapshot, funnel, relevant quality metrics and unresolved questions.
3. Ask for the pulse in the channel where you work. This demo delivered chart packs directly in the bot chat every 15 minutes.
4. Request a new data slice conversationally. The hosts added hourly activity and cumulative users, and sent engine results to **Crit**, the game-design bot.
5. Check definitions before acting or quoting the numbers. The hosts explicitly questioned what counted as practice-to-sign-in conversion.

| Keep separate | Why |
|---|---|
| Practice sessions and unique people | A person can start several practice sessions |
| Signed-in players and matches | Match totals do not establish user count or concurrency |
| Matches in flight and active users | The demo warned against presenting 48 in-flight matches as peak concurrent users |
| Async ghost matches and live PvP | Most finishes in the cited snapshot were ghost-rated |
| Web analytics and full launch totals | Vercel Analytics was enabled around noon, after the morning spike |
| Win rate and loss rate | The presenter called 41.8% a loss ratio; the screen labeled it **win rate** |

One source-qualified snapshot at about 14:42 PT: **4,500 practice sessions, 1,650 X sign-ins, 4,898 public matches, 47.9% public win rate, 875 unique public players**. The separate Vercel view showed **2,370 visitors and 17,050 pageviews** since analytics was enabled. These are different populations and observation windows; do not combine them into a single funnel or infer missing totals.

The final recorded refresh around **16:15 PT** reported **4,884 practice sessions, 1,902 X signups, 6,546 public matches, 48.5% public win rate and 1,020 unique public players**; Vercel reported **3,477 visitors and 28,521 pageviews**. The bot disclosed that its **16:00 pulse had failed**. Requesting a fresh retrieval and checking the timestamp was therefore part of the workflow, not an optional cosmetic detail. The hosts also reported a production outage during the closing segment; a growing cumulative chart did not establish current service health.

An adapted brief:

> At the agreed cadence, report launch counts and deltas with source, time window and metric definitions. Keep sessions, unique users, matches and concurrency separate. Show anomalies and questions, then send the relevant evidence to the specialist who can interpret it. Do not invent missing values.

The 15-minute cadence suited this active launch. For steady operations, use the [routine-cost guidance](improve-bot-system-with-feedback.md) to choose a cadence that earns its cost.

Evidence: pulse setup in [122 · 00:07:30–00:09:59](../../timelines/122.md) and [123 · 00:02:00–00:08:40](../../timelines/123.md); Data → Crit in [124 · 00:00:00–00:03:45](../../timelines/124.md); claim limits in [133 · 00:04:50–00:07:40](../../timelines/133.md); funnel uncertainty in [141 · 00:00:00–00:04:30](../../timelines/141.md); afternoon snapshot in [152 · 00:03:35–00:06:40](../../timelines/152.md); failed pulse, final refresh and outage in [157 · 00:01:59–00:03:29](../../timelines/157.md).
