# 13 — AI Risk & Compliance Assessment

**Draft v0.1. Preliminary issue-spotting, not legal advice or certification. Current legal requirements and vendor contract terms must be verified with authoritative sources before external launch.**

## Planned processing

Local synthetic websites plus browser-generated evidence. No real user accounts, recordings or customer personal data in MVP. Potential later exposure: screenshots/DOM may capture names, email, cookies or other personal information, even incidentally.

## Jurisdiction and applicability

- **India:** assess the Digital Personal Data Protection Act, 2023 and applicable notified rules/commencement provisions when identifiable digital personal data is processed. Obligations may involve notices, lawful grounds/consent where applicable, security, retention, grievances and breach response. Do not assume every provision is currently effective or irrelevant; check current government notifications before rollout.
- **EU GDPR:** may apply if offering services to EU individuals or processing covered personal data; roles (controller/processor), lawful basis, DPA, cross-border transfers, storage security, data-subject rights and retention would require analysis.
- **EU AI Act:** applicability depends on the product's intended purpose, provider/deployer roles, market and relevant effective dates. A generic software test planner is not automatically high-risk simply because it uses AI. Do not claim compliance based on a draft.
- **HIPAA:** generally not applicable to synthetic demo pages; reassess if handling protected health information for a covered entity/business associate.
- Website owner agreements and computer-access authorization are independent from privacy law.

## Controls for MVP

Synthetic fixtures only; authorized site allowlist; block external destinations; exclude sensitive fields, cookies and headers; prompt minimization; local evidence expiry; restrict API key access; deletion and incident workflow; only sanitized demo evidence in repository.

## Third-party LLM due diligence

Before using real application content, document provider, contract/DPA, where prompts are processed, logging and abuse retention, model training opt-out, zero-data-retention eligibility **if actually available**, subprocessors, cross-border handling and deletion. Never assume "not used for training" means zero retention.

## Risk register

| Risk | Likelihood | Impact | Action |
| --- | --- | --- | --- |
| Unintended personal data captured | Medium | High | Synthetic-only MVP, minimization/redaction |
| Unauthorized site automated testing | Medium | High | Domain authorization and policy tests |
| Off-origin leakage to external services | Medium | High | Network isolation and egress limits |
| Misleading automated defect allegation | High | Medium | Independent oracle and human review |
| Vendor logs hold sensitive content | Unknown | High | Vendor contract/settings review |
| Legal requirement changes | Unknown | Medium | Recheck before launch |

## Release decision

Local controlled demo may proceed after security/privacy tests. External customer testing **requires separate legal, permission, security and procurement assessment**. Record reviewer and decision date once actually approved.

## Reference starting points

[India MeitY](https://www.meity.gov.in/), [EU AI Act official portal](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai), [European Data Protection Board](https://www.edpb.europa.eu/).