# Onboard a new bot, bot-to-bot

Source: Lingxi Li, Grok Bot for Engineers, [025, 00:00–02:00](../../timelines/025.md). Dated 2026-09-15.

Do not re-tell a new bot everything yourself. Let an existing supervisor bot onboard it.

## Steps (as demoed)

1. Add the new bot (here: Nightly Audit Engineer from Marketplace).
2. Message your existing engineer/supervisor bot: "Hello, I have a new member in the team called [Name], rename them to [Name], and tell them how the engineering workflows are enforced."
3. The supervisor bot renames the newcomer and pings it with the full fleet briefing: board mechanics, definition of clean, the stage ladder, merge and rebase rules (see [FlyLo fleet](../reference/flylo-engineering-fleet.md)).
4. The new bot acknowledges and **absorbs the briefing into its memory** — you never repeat or copy-paste between bots.
5. If the new bot's own mandate conflicts with a rule, it should flag the conflict and propose a resolution instead of breaking the rule or failing silently. Confirm or amend.

## Why

- Bots talk to each other, so the human doesn't re-teach.
- Briefings become memory: next tasks reuse it ("You don't have to repeat or copy-paste every single thing between bots. You just let the bot talk with each other.").
- Standing rules replace per-task instructions ("urgent" prompts make agents skip steps or guess; deterministic rules don't).

## Related

- Routines and memories are created at onboarding: "Please create your routines and write your memories… anything else to bake into that role?" [024, 09:12–10:00](../../timelines/024.md).
- The chief of staff can onboard and handshake specialists so the human only talks to the chief of staff. [025, 04:10–06:30](../../timelines/025.md).
- [Shared playbook ownership](maintain-a-shared-playbook.md) prevents each bot from creating a competing policy.
