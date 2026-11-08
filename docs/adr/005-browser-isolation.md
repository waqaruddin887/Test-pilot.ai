# ADR-005: Separate browser privileges from planner and supervisor

Status: Accepted technical baseline, 2026-11-08. Implementation pending.

## Context

A browser worker sharing credentials and networks can reach infrastructure forbidden by the threat model.

## Decision

Trusted orchestrator invokes a narrow supervisor protocol; unprivileged Playwright/browser run in a fixture-only namespace communicating through bounded pipes. No provider/DB/queue secrets, host mounts, Docker socket or raw browser debug endpoint.

## Alternatives considered

A shared Compose bridge or request interception alone cannot establish directed isolation.

## Consequences and verification

Concrete sandbox provisioning and negative connectivity/cleanup tests block browser enablement; broad host privileges are not authorized by this ADR. See the [normative specification](../architecture/runner-protocol.md) and [readiness gates](../implementation-readiness.md) for implementation requirements and evidence still needed.

This decision supersedes conflicting v0.1 wording; it does not claim controls have been implemented or tested.
