# Four-minute demonstration outline

**0:00–0:35 — Scope and architecture.** Open Projects. Explain that this is a
restricted synthetic browser-testing prototype with an explicit deterministic
planner. Show “Restricted fixture mode” and worker readiness. Do not imply a live
LLM, external-site coverage, production isolation certification or general accuracy.

**0:35–1:20 — Passing control.** Create/select known-good fixture, choose `/form`,
submit a smoke run. Show the generated finite plan, independent FORM-001@1
requirement, stages and the requirement pass. Explain that workflow completion
is separate from a product-quality verdict.

**1:20–2:20 — Seeded violation.** Run the seeded fixture on the same neutral path.
Open Finding Detail, inspect failed expected/actual text, initial and clean-context
reproduction steps, both screenshots and trace downloads. Show the oracle source,
manifest hashes and evidence availability.

**2:20–3:05 — Human review.** Explain why it initially stays suspected while human
oracle review is pending. A reviewer may inspect/seal the requirement under
Configuration, rerun to create new verified evidence, then explicitly accept the
finding after inspection. Do not prelabel an automated test as human signoff.
Show acceptance disabled without the prerequisites and the separate review history.

**3:05–4:00 — Measured limits.** Show evaluation/results/latest.json and the report:
30 deterministic trials, raw denominators, reproduced candidates, control false
positives, latency, zero live-provider calls and pending human-review metrics.
Show the security-status table: no external targets, SQLite development mode,
PostgreSQL/RQ/cgroups/provider integration unfinished. End with the exact next
engineering milestone, not an accuracy or production-readiness claim.

Concise project description:

> TestPilot AI is a local browser-testing prototype that generates strict
> deterministic fixture plans, executes Playwright in a network-disabled sandbox,
> reproduces independent requirement violations, and presents expiring screenshots,
> traces and separate human review. Live LLM and production infrastructure
> integration remain planned.
