# Find the right guide / Elegí tu tarea

Read one row's first guide, then its evidence when needed. All examples are from **15–17 September 2026**. Exact UI and availability may differ outside those recordings.

| Task / Tarea | Start here | Follow-up |
|---|---|---|
| Understand bots / entender el producto | [Product model](canon/explanation/why-grok-bot.md) | [Maturity curve](canon/explanation/ai-maturity-curve.md) |
| First bot / crear un bot | [Create a bot](canon/how-to/create-a-bot.md) | [101 team](canon/tutorials/meet-the-101-team.md) |
| Computer / computadora | [Use the computer](canon/how-to/use-the-computer.md) | [Computer and memory limits](canon/reference/day-1-memory-and-computer-limits.md) |
| Teach work / enseñar tareas | [Teach a task](canon/how-to/teach-a-task.md) | [Shared playbook](canon/how-to/maintain-a-shared-playbook.md) |
| Permission / permisos | [Approvals](canon/how-to/approvals-and-rules.md) | [Secrets](canon/reference/secrets-and-1password.md) |
| Memory / memoria | [Steer memory](canon/how-to/steer-memory.md) | [Evidence limits](canon/reference/day-1-memory-and-computer-limits.md) |
| Team / equipo | [Operate a team](canon/how-to/operate-a-bot-team.md) | [Bot onboarding](canon/how-to/onboard-a-new-bot-bot-to-bot.md) |
| Cost / consumo de tokens | [Reduce token use](canon/how-to/reduce-bot-token-use.md) | [Local search](../README.md#how-bots-consume-this-repository) |
| Engineering / desarrollo | [Build verification](canon/how-to/build-and-maintain-verification.md) | [Feedback to fixes](canon/how-to/triage-feedback-and-verify-fixes.md) |
| Product / producto | [Data to PRD](canon/how-to/turn-product-data-into-a-prd.md) | [CRM review tool](canon/how-to/build-crm-lead-review-tool.md) |
| Founders / emprendedores | [Founder bot team](canon/how-to/run-a-founder-bot-team.md) | [Research and scope](canon/how-to/research-and-scope-a-new-business.md) |
| Sales engineering / ingeniería de ventas | [Sales engineering](canon/how-to/run-sales-engineering.md) | [Day 2 boundaries](canon/reference/day-2-workflows.md) |
| Sales / ventas | [Sales workflows](canon/how-to/run-sales-workflows.md) | [SDR prospecting](canon/how-to/run-sdr-prospecting.md) |
| Support / soporte | [Customer support](canon/how-to/run-customer-support.md) | [Post-sales desk](canon/how-to/run-post-sales-desk.md) |
| Revenue operations / operaciones comerciales | [RevOps handoffs](canon/how-to/run-revops-task-handoffs.md) | [CRM tool](canon/how-to/build-crm-lead-review-tool.md) |
| Growth / crecimiento | [Growth playbook](canon/how-to/build-a-growth-playbook.md) | [ICP and outreach](canon/how-to/define-icp-and-plan-outreach.md) |
| Marketing / campañas | [Orchestrate a campaign](canon/how-to/orchestrate-marketing-campaign.md) | [Improve the system](canon/how-to/improve-bot-system-with-feedback.md) |
| Metrics / métricas | [Monitor a launch](canon/how-to/monitor-a-product-launch.md) | [Final outcomes](session/day-3-outcomes.md) |
| Share / compartir bots | [Sharing and Marketplace](canon/how-to/share-duplicate-marketplace.md) | [Day 3 boundaries](canon/reference/day-3-capability-boundaries.md) |
| Evidence / fuente y momento | [Timeline index](timelines/INDEX.md) | [Gaps and replays](session/gaps.md) |

Full library: [INDEX.md](INDEX.md). Local queries:

```bash
python scripts/search.py "soporte" --limit 2
python scripts/search.py "PR review" --limit 3 --max-chars 600
```

Search reads public text locally and returns excerpts with paths. It never reads raw sources or sends the corpus to a model. Open the selected guide before applying an excerpt without its surrounding limitations.
