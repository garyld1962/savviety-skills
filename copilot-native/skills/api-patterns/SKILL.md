---
name: api-patterns
description: Backend and service review rubric for shared types, validation, auth, logging, and operational correctness.
---

# API Patterns

Use this skill for backend and service review passes.

## Scope

- service or API packages
- route handlers
- RPC handlers
- background workers when they share the same request and validation patterns

## Review focus

- shared types and constants come from the project's shared contract location
- request input is validated at the boundary
- async handlers follow the project's error handling convention
- auth and authorization match the repo's actual middleware patterns
- logging uses the project's logger and avoids sensitive data
- messaging contracts and cleanup follow the repo's service patterns when
  messaging exists

## Examples

- **HTTP handler review:** Compare a changed route handler to a local reference
  implementation, confirm boundary validation and auth usage, and flag only the
  concrete contract or logging defects with exact evidence.
- **Background worker review:** Apply the same service conventions to a worker
  only when it shares the repo's request, validation, or messaging patterns.

## Guardrails

- Detect the project framework before making pattern claims.
- Read a reference service implementation first.
- Skip messaging-specific checks when the repo does not use messaging.

## Do Nots

- Do not recommend framework patterns or middleware the repo does not use.
- Do not treat generic logging preferences as findings when the real issue is
  absent or unsafe operational evidence.
- Do not invent messaging concerns for repos that have no messaging surface.

## Closed Decisions

- Local service and contract conventions are the authority for this review.
- Boundary validation is required where the repo accepts external input.
- Framework detection comes before pattern claims.
- Messaging-specific review runs only when the repo actually uses messaging.
