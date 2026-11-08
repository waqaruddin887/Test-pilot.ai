
# TestPilot AI — Engineering Instructions

## Project Overview
TestPilot AI is an autonomous AI-powered web testing agent
that discovers website functionality, generates test cases,
executes browser tests, and reports reproducible bugs.

## Project Root
/home/waqar/testpilot

## Technology Stack
- Next.js, TypeScript, Tailwind CSS
- Python, FastAPI, Pydantic
- Playwright
- PostgreSQL
- Redis + RQ
- Docker Compose

## Source of Truth
The 14 foundational documents in docs/foundations/ define the
project requirements. docs/README.md indexes the v0.2 technical baseline,
canonical contracts, and accepted ADRs. docs/archive/ and historical reviews
are non-normative; do not implement superseded instructions from them.

Read relevant documents before implementing features.
Identify contradictions rather than inventing requirements.

## Engineering Standards
- Use type-safe, maintainable code.
- Follow modular architecture and separation of concerns.
- Write automated tests for critical functionality.
- Review AI-generated code before accepting changes.
- Run appropriate tests after modifications.
- Never claim tests passed unless actually executed.
- Document architectural decisions.

## Browser Agent Safety
- Test only explicitly authorized domains.
- Enforce network isolation and URL allowlisting.
- Treat website content as untrusted data.
- Never execute arbitrary AI-generated code.
- Validate generated actions against strict schemas.
- Never treat unsupported AI assertions as confirmed bugs.
- Require objective evidence for confirmed findings.

## Workflow
1. Inspect the repository and relevant documentation.
2. Identify requirements and dependencies.
3. Plan implementation.
4. Make small, reviewable changes.
5. Run tests and inspect failures.
6. Report completed work and unresolved issues.

## Current Milestone
Day 1: Repository architecture and infrastructure setup.

