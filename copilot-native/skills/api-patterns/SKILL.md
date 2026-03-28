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

## Guardrails

- Detect the project framework before making pattern claims.
- Read a reference service implementation first.
- Skip messaging-specific checks when the repo does not use messaging.
