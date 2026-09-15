# Ship with Grok Bot + Cursor cloud agents

Source: Engineering 13–18.

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
