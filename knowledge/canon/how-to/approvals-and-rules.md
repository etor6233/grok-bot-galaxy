# Approvals and auto-review rules

Source: clips 05–06.

**2026-09-22 editorial note:** this preserves the Day 1 demo. Two-way voice, described below as future rollout, was later demonstrated in [Day 3 clip 152, 00:06:40–00:08:30](../../timelines/152.md). Neither voice nor delegation bypasses configured approval rules. [Day 1 evidence](../../timelines/05.md), [continued demo](../../timelines/06.md).

Bots **ask for approval** before some actions. Enterprises use this to control what bots may do.

Examples spoken:

- Only send an email after permission.
- Only Slack an external customer after approval.
- Do **not** reply to emails unless you explicitly ask first.
- **Do** create slides automatically without asking.

Where: **Settings → General → Auto-review**. Copy on screen: “Grok Bot checks each action before it runs and asks you first when needed.” Rules: “When Grok Bot wants to:” / “It should:” (`Ask first` wins conflicts). Live cards: Allow once / Deny; “The Bot wants to run a task” / “use a connected service.”

Live: an agent trying to reply to email was **blocked by a personal auto-review rule**. She chose **Allow once**, then the UI showed a **draft**. Connecting to outside services also asks permission.

Voice mode: speech-to-text in the demo. A **back-and-forth Grok voice** (bot talks back) was deployed internally; hoped public “sometime within the next week” from Day 1.
