# Escalate urgent work with a P0 monitor routine

Source: Lingxi Li, Grok Bot for Engineers, [025](../../timelines/025.md)–[026](../../timelines/026.md). Dated 2026-09-15. This is a configured FlyLo workflow, not a built-in global P0 mode.

## Problem

Coding agents run long horizons; when something is urgent, waiting (or manually watching thinking traces and tool calls at your desktop) doesn't scale. Agents told "urgent" may skip steps or guess — you want deterministic results.

## The P0 escalation workflow

1. Define P0 for your bot, including scope, evidence requirements, escalation, and when the temporary monitor stops. The demo instruction began: "Treat this as P0: you need to set up a routine that checks cloud agent every 5 minutes, check if they are off the track."
2. The bot monitors the cloud agents every five minutes: checks progress and the current tool call.
3. If a tool call is unnecessary or time-consuming (e.g. a `sleep 300` meant to wait out tests running async in another shell — while the real tests may finish in a minute), the bot **interrupts immediately** and starts a new prompt based on what's happening.
4. Let it handle monitoring and follow-up prompts within that mandate. The demonstrated FlyLo policy still reserved merges for the human.
5. Stop the temporary watch at **Watching 1/3 or Ready**; ordinary work remains on the 30-minute fleet watcher. Jenny added this rule to the shared playbook and announced it to the engineer bots. [026, 02:00–04:35](../../timelines/026.md)

## Demoed live

- Bug report → Craig boards it ("Trip lookup broken"), verifies on the live site with its computer, marks it **P0 (~1h to Ready)**, starts a fix agent, and runs a **5-minute watch until Watching 1/3** (clip 025).
- The P0 routine was created by chat from the typed definition (clip 025 tail / 026).

## Related

- [Approvals and rules](approvals-and-rules.md), [shared playbook](maintain-a-shared-playbook.md).
- **Dated clarification, 2026-09-15:** the separate ~10-minute on-call threshold was Lingxi's described CI/alert workflow, not the P0 demo's completion guarantee. [024, 05:51–07:19](../../timelines/024.md)
