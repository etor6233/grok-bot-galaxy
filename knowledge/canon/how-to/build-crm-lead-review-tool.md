# Build a CRM lead-review tool with PM and engineering bots

Evidence: Day 3, 2026-09-17. **Lead Deck** was Matthew Silberman's internal-tool case study. The displayed finished interface used dummy data; its timings and adoption gains are presenter reports.

1. Brief a product-manager bot on the problem and a rough interaction. Matthew used **Juno** to explore a swipe-based lead queue.
2. State the authentication requirement immediately: each rep must see their own leads and write back under the correct CRM identity.
3. Resolve the behavioral questions before code. Juno asked about users, queue membership, accepted/rejected leads, offline confirmation and skipped items.
4. Have the PM bot produce a locked specification and hand it to the engineering bot. **Ondes** checked the OAuth and offline-outbox approach, then started a cloud agent for a thin vertical slice.
5. Review a runnable branch preview before relying on the application. The demo explicitly allowed a preview without waiting for a merged PR.

The demonstrated decisions were:

| Decision | Lead Deck example |
|---|---|
| Users | SDRs and account executives |
| Queue | Signed-in rep's New leads |
| Accept | Enroll in a follow-up sequence; do not change CRM status because existing outreach automation owns it |
| Reject | End the lead with a required picklist reason and optional notes |
| Offline | Queue actions and show completion only after confirmation |
| Skip | Local-only; the lead may reappear |

The important handoff is the spec, including deliberate non-actions. For this app, changing a CRM status on acceptance would have duplicated another automation's responsibility. Preserve those ownership rules when adapting the pattern.

Matthew reported roughly ten hours of build time within a two-week implementation/onboarding period, followed by improved lead-review rates. These are case-study observations, not expected delivery times or guaranteed outcomes.

Evidence: problem and auth in [116 · 00:00:00–00:02:20](../../timelines/116.md); decisions and handoff in [116 · 00:02:20–00:05:30](../../timelines/116.md); dummy-data preview and reported adoption in [116 · 00:05:30–00:07:10](../../timelines/116.md) and [119 · 00:00:36–00:02:50](../../timelines/119.md).

Next: [Route RevOps requests](run-revops-task-handoffs.md).
