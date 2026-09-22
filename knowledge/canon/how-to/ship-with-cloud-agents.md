# Ship with Grok Bot + Cursor cloud agents

Source: Day 1 Engineering, 2026-09-15, [13](../../timelines/13.md)–[18](../../timelines/18.md). Repository names and deployment choices below belong to the live company demo.

**Rule of the harness:** Grok Bot is a lightweight harness (Grok = model), not a full coding harness. Serious code goes to **Cursor cloud agents**, orchestrated from Grok Bot.

**Repo**

- Empty GitHub org cannot mint a cloud repo until Origin exists.
- Demo repo: `shipbythursday/popup` (also `pop-up`), **private during stream**, accept PRs after.
- Empty repo → cloud agent bounces. Seed an **initial commit**, then agents can push.
- Clip 18: **no pull requests; ship to main** until someone objects. Steve’s ~2000-line PR treated as a mistake.

**Prototype path**

1. **grokpot** (prototyper): throwaway HTML/CSS inside Grok Bot (`/workspace/platform-waitlist/`).
2. Lock a direction (A/B/C…); they locked **night-market pink** operator waitlist, CTA “Claim a stall.”
3. Graduate to Next.js on **Vercel**. Framework Preset **Other (static)** for the HTML v0. Deploy from **main**. Custom domain later.
4. Waitlist v0: email + role in **localStorage**; Sheet webhook later. DB ideas: Google Sheet; then PlanetScale Postgres (they overrode Neon). Clerk only if login blocks dogfood. Delay realtime, messaging, payments, design system. Payments = Stripe Connect later.

**Cloud agents**

- “Tell your bot to spawn a cloud agent.”
- On an existing repo, also **set up the environment** so the agent can boot the app.
- Agents run on Cursor’s harness in a cloud VM (click around, tests, CPU traces).
- **Project agent** = long-running cloud agent that holds engineering context.

**Don’t:** update the Grok Bot app on stream; show personal email on stream.

## Dated 2026-09-15 (clips 022–025): cloud-agent patterns from the workshop

- Repo renamed `popup` → **`thursday`** (clip 022). PRs #6–#8 by roshansada: Prototype A “Deadline Newsroom”, B “Mission Control Dock”, C “Quiet Studio” landings.
- Grok Bot manages Cursor Cloud Agents **via tool calls** (no UI driving): read transcripts, start agents, create follow-up replies, and run them on a **private worker** (your own Mac machines).
- Cursor **automations** are trigger-based (e.g. an incoming Slack message) and run 24/7; claimed effect: ~10 parallel machines, no port contention, Cursor team ~10x.
- Fleet pattern from Lingxi Li: one bot per specialty with per-bot memory; chief of staff routes; a 30-minute watcher polls the Notion fleet board; P0 monitor interrupts off-track agents (see [FlyLo fleet](../reference/flylo-engineering-fleet.md), [P0 monitor](escalate-urgent-work-p0.md)).

## Dated continuation — 2026-09-15, clips 026–050

The early ship-to-main instruction was specific to the company at that point. Later work used PRs, reviewer bots, evidence requirements, and explicit merge decisions. A separate PM demo restricted its agents to the FlyLo repositories and held merges for the human. [043, 06:20–08:20](../../timelines/043.md); [049, 01:21–02:18](../../timelines/049.md); [050, 05:35–07:40](../../timelines/050.md)

For the complete demonstrated workflow, pair [reusable verification](build-and-maintain-verification.md) with [PR review routing](wire-pr-reviews-into-slack.md) and [shared playbook rules](maintain-a-shared-playbook.md). The product team explicitly prepared a runnable repository environment and checked cloud-agent results against the original goal. [050, 06:31–08:27](../../timelines/050.md)
