# Why a fleet of bots (one bot vs many)

Source: Grok Bot for Engineers workshop, Lingxi Li, [023](../../timelines/023.md)–[025](../../timelines/025.md). Dated 2026-09-15.

## The question

"Apparently they are sitting on the same model, and they might be able to do the task. 100%, they will be able to do any task you gave them — even if I gave a UI task to Hogan, they should be able to resolve it."

So why run three engineer bots instead of one?

## The answer: context and fleet management

1. **Every bot has its own context limit.** A single bot switching between too many tasks runs over its context limit.
2. **Every bot has a slightly different pipeline** based on the work it does.
3. **Memory is partitioned per named bot.** Whatever is told to Hogan persists in Hogan's memory. The next time a new task comes in, Hogan takes it based on the context it already has — instead of pulling the instructions again and starting cold. The fleet runs faster because nothing is re-taught.

## The routing layer

You do not talk to the individual engineers unless necessary. You talk to the **chief of staff**, which:

- knows who is working on what,
- routes the request to the right specialist,
- saves its own context from remembering all the engineering workflows.

## Board-first work

The demonstrated fleet is coordinated through a shared Notion board (FlyLo Engineering Fleet): a 30-minute watcher polls boarded rows and each PR's state is tracked on a stage ladder. Ordinary tasks are boarded before work; the nightly-audit bot negotiated boarding its cleanup rows when their PRs open. See [FlyLo fleet rules](../reference/flylo-engineering-fleet.md).

## Fleets shown on stage (Day 1)

- Lingxi Li (workshop): Lingxixi (chief of staff), Craig (UI engineering), Steve (DevX, then nightly-audit in the demo), Hogan (infra), Jenny (head of operations / playbook owner). Demo rename in 025: Lingxi's Engineer Bot → Craig, Nightly Audit Engineer → Steve.
- Lauren (company build): steve (chief of staff), tater (engineering), grokpot (prototyper), hashbrown (reviewer, created off-stream before clip 022), dr eggbot (factory installer).

## Dated extension — 2026-09-15, later sessions

The PM session names three reasons for multiple bots: recognizable roles, scoped learning, and parallel work. It also says a single combined builder can work for simpler cases. [048, 07:55–09:27](../../timelines/048.md); [049, 00:00–00:35](../../timelines/049.md); [051, 03:10–06:10](../../timelines/051.md)

Shubh prefers direct specialist conversations; Jenny describes a chief of staff coordinating 22 bots. These are different user choices, not a mandated hierarchy. More bots and permanent group chats can also increase chatter and token use. [059, 06:35–09:59](../../timelines/059.md); [060, 05:10–08:50](../../timelines/060.md); [061, 06:45–09:56](../../timelines/061.md)

See [token efficiency](../how-to/reduce-bot-token-use.md) and [memory/computer evidence limits](../reference/day-1-memory-and-computer-limits.md).
