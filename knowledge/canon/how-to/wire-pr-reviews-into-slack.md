# Wire PR reviews into Slack (the potato factory flow)

Source: Lauren, Engineering, [022](../../timelines/022.md), [027](../../timelines/027.md)–[028](../../timelines/028.md). Dated 2026-09-15. This is the review flow Lauren set up live for Ship by Thursday (repo `shipbythursday/thursday`).

## Goal

"Your bots are just dumping their PRs into that Slack channel, and then the reviewer bot goes off and reviews them, and then if it's good we can merge it."

## Pieces (as built on stream)

1. **Reviewer bot**: a named bot whose job is reviewing PRs from the engineering bot. Lauren's: **Hashbrown** (reviews PRs that **tater** opens) — created off-stream during the break before clip 022.
2. **Repo plugin**: pstack installed at project scope (`.cursor/settings.json` → `{"pstack": {"enabled": true}}`) so cloud agents and automations in the repo get `/poteto-mode` and its principle skills without per-user installs (PR #5).
3. **Repo AGENTS.md**: routes non-trivial work through `/poteto-mode`, prefers the poteto-agent subagent for delegation, and reports failure rather than silently degrading.
4. **Slack channel + webhook**: a #pr-reviews channel with an app (thursday-pr-notify). The bot mints the webhook and stores `SLACK_WEBHOOK_URL` as a GitHub Actions secret so PR events post automatically.
5. **Cursor automation**: a trigger-based automation that picks up the posted PR and reviews correctness, risk, and missing tests. The webhook notification passed a smoke test on PR #5; the review automation was still being finished in 022 and was observed firing on PR #10 in 028. A merge requires the applicable policy, not merely a Slack post. [022, 01:29–02:45](../../timelines/022.md); [027, 06:10–07:03](../../timelines/027.md); [028, 07:54–10:00](../../timelines/028.md)

## Routing on screen

- tater → steve: "pstack/poteto-mode pr: …/pull/5 — hashbrown should review."
- steve (chief of staff) handled the webhook/secret plumbing and routed review to hashbrown.

## Guardrails

- Don't overcook: "something basic, nothing too fancy, but something we can extend later" — the startup survives day to day.
- Keep routing, review, and merge authority separate. [FlyLo's fleet rules](../reference/flylo-engineering-fleet.md) belong to a different demonstration.
- **Dated clarification, 2026-09-15:** the “ship to main” instruction in [18](../../timelines/18.md) was an early company-build decision. Later clips visibly use PRs, review blockers, and human merge instructions; do not promote the early instruction into a general fallback rule. [043, 06:20–08:20](../../timelines/043.md); [046, 06:50–09:30](../../timelines/046.md)
- Review evidence is part of the loop: see [reusable verification](build-and-maintain-verification.md).
