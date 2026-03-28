---
name: k8s-verification
description: Post-deploy Kubernetes verification checklist for namespace detection, rollout health, endpoints, events, and optional log analysis.
---

# Kubernetes Verification

Use this skill after a Kubernetes deployment, rollout restart, or suspicious
cluster state.

## Relationship to Copilot built-ins

- Use this as a custom operational workflow because Copilot has no built-in
  Kubernetes post-deploy verifier.
- Use `.github/copilot-instructions.md` and deployment manifests as the source
  of truth before issuing commands.

## Verification order

1. Confirm cluster context and namespace
2. Check pod readiness and failures
3. Check rollout status with a timeout
4. Verify services have endpoints
5. Inspect recent warning/error events
6. Run HTTP health checks only when endpoints are documented
7. Inspect logs only for failed or warning pods unless a full pass was requested

## Pod verdicts

- `Running` with all containers ready -> PASS
- partial readiness or `Pending` -> WARN
- `CrashLoopBackOff`, `ImagePullBackOff`, `Error` -> FAIL

## Common failure patterns to surface

- missing or unhealthy probes
- rollouts stuck beyond the timeout
- services with zero endpoints
- recent `BackOff`, `FailedMount`, `FailedPull`, or `Unhealthy` events
- readiness paths or ports guessed instead of verified

## Report format

Return a compact table or bullet summary covering:

- Pods
- Rollouts
- Endpoints
- Events
- HTTP health
- Logs
- Final verdict: `HEALTHY`, `DEGRADED`, or `UNHEALTHY`

## Guardrails

- Never guess namespace, pod names, ports, or health paths.
- Always use a timeout for rollout checks.
- Clean up temporary port-forwards.
