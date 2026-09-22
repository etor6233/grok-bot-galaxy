# How to use a bot’s computer

Source: clips 05–06 (Amrita).

**2026-09-22 editorial note:** the isolation wording below is the 101 explanation, not a verified security architecture. Later Day 1 Q&A describes shared filesystem access; preserve this [unresolved distinction](../reference/day-1-memory-and-computer-limits.md). Evidence: [05](../../timelines/05.md), [06](../../timelines/06.md), [061](../../timelines/061.md).

- After a request, the bot starts working. Computer is shown **top-right**. Click in to watch.
- The computer is its **own Linux VM**. It can log into Google Forms / Slides / Docs and any UI a human would use — including tools **without** native MCP/API (Google Forms, Qualtrics called out).
- **Isolation:** one Grok Bot cannot access another Grok Bot’s computer. Slide Sonya and Data Dan can work at the same time without colliding. You can edit slide 10 while Sonya edits slides 1–2 of the same deck.
- VMs are described as lightweight. Amrita outsources computer-use work to Grok Bot on bad airplane Wi‑Fi because the VM’s network is better.
- Computer use is called a hot topic for Grok Bot, Cursor, and SpaceX; expected to keep improving over the following weeks.
- Speed depends on the model / computer-use stack.
