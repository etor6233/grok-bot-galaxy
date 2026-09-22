# FlyLo Engineering Fleet (reference)

Source: Grok Bot for Engineers workshop, Lingxi Li, [025, 00:00–02:00](../../timelines/025.md) (fleet-rules briefing shown on screen). Dated 2026-09-15. This is Lingxi's demo fleet for **FlyLo** (flylo-air.com airline demo product), not the Ship by Thursday company.

## Fleet

| Bot | Job |
|---|---|
| Lingxixi | Chief of staff (ASR "Ling Xixi") |
| Craig | UI engineering; in the demo, Lingxi's Engineer Bot renamed Craig — the fleet supervisor that onboards new bots |
| Steve | DevX; in the demo, the Nightly Audit Engineer renamed Steve |
| Hogan | Infra (ASR "Hogan1K1") |
| Jenny | Head of operations; sole owner of the engineering playbook in Notion |

## Repos / stack (from the fleet briefing)

Frontend: **Next 16 App Router + React 19 + TypeScript + Tailwind v4** across `web`, `booking-frontend`, `crew-app`, `factory`. Prefer RSC; await params/cookies; Tailwind v4 CSS-first; no drive-by UI kits; preserve paper/ink brand on marketing/booking.

## Fleet rules (condensed from Craig's briefing to Steve)

### Code & merge

- All code work goes through Cursor cloud agents. They prove remote tip, mergeability, CI green, and real product proof.
- **Humans own every merge.** Never merge unless Lingxi explicitly says so.
- Never open new PRs against the default branch on your own. If a blocker is on default, flag and wait.
- One cloud agent per PR stream: reply for rebases/bugbot/CI/re-proof; fresh launch only for a brand-new task or intentional rewrite.

### Board-first (Notion: FlyLo Engineering Fleet)

- Create the board row (Stage=Working) before digging or launching.
- Fields only: **Task name, Owner, Stage, PRs, Cloud agent, Last commit**. Never Status / Assignee / Due date.
- Task name = clean short title only (no PR#/stage crumbs).
- Never re-board another owner's PR — query that PR number across owners first.
- Follow-ups on an unmerged PR fold into the same row + same cloud agent.

### Stages & CLEAN ladder

- Stages: **Working → Watching 1/3 → 2/3 → 3/3 → Ready for review** (also Holding, Blocked, Done, Cancelled). No "Waiting for merge/bugbot".
- Ladder = 4 consecutive CLEAN ticks; **Ready is terminal pre-merge**. Never invert; never stop at 3/3.
- Working = actively fixing only (findings on HEAD, dirty rebase, or agent coding). Waiting on CI/bugbot/proofs = Watching. **Ready for review is pre-merge; Done = merged only.**
- CLEAN ignores review-only gates; still blocks on CI failures, security findings, failing check-runs, unresolved bot/security threads.

### Rebase / CI / proof

- Rebase only on real conflicts, or when a default-branch CI fix lands and the PR needs it. Behind alone ≠ rebase. Always rebase onto default; never merge default into the branch. Confirm mergeability with a second poll before rebase.
- Don't weaken failing checks — fix the root cause.
- Visual proof = real product chrome (verified). No captions-as-proof, no white-canvas mocks. Video must be playable mp4. Proof goes in the PR body as hosted artifacts, never committed into the branch.

### Watcher hygiene

- 30-min fleet watcher polls boarded rows only — never list-all-open-PRs / unboarded audits.
- Board only when Lingxi fires a task or a cloud agent opens a PR.
- Last commit = PR tip committed date in UTC from the same batched poll.
- Keep messages short. When mentioning a PR use #N + review URL inline.

## Nightly audit mandate (Steve) — negotiated conflict

Steve's marketplace mandate (research whole tree → one cleanup cloud agent per area → opens PRs) conflicted with "never open new PRs against default on your own" and "board only when Lingxi fires a task or a cloud agent opens a PR." Steve proposed, and Lingxi confirmed: stay research-quiet until a tree is named / the run is armed; cleanups go through cloud agents only; board the row when the PR opens (Owner=him); never merge; never touch another owner's PR. Nightly routine saved **paused**: "Nightly code-quality audit at 4am".

## Other artifacts seen

- P0 trip lookup: bug boarded as "Trip lookup broken" (flylo-air.com /trips stub), fix agent + 5-minute watch until Watching 1/3.
- Steve's research pass: four research-only cloud agents (booking-frontend, web, crew-app, factory), cleanup ships only after aggregate; first cleanup: factory "dead API + leftover poll".

## Dated clarification — 2026-09-15

The earlier draft of this reference conflated “agent finished” with Done. The on-screen briefing explicitly reserves **Done for merged work**. [025, 00:00–02:00](../../timelines/025.md)

Jenny later added two shared rules: temporary P0 monitoring ends at Watching 1/3 or Ready, and missing PR proof blocks Ready. See [P0 monitoring](../how-to/escalate-urgent-work-p0.md) and [shared playbooks](../how-to/maintain-a-shared-playbook.md). [026, 03:47–05:03](../../timelines/026.md)
