---
name: k8s-verify
description: "Post-deploy Kubernetes verification: pods, rollout status, services, endpoints, events, logs, and optional smoke checks after a deployment."
---

# K8s Verify

Read `references/workflow.md` for command flow and output shape. `references/legacy/` is archival only.

## Workflow

1. Identify namespace, workload, and service from arguments or current context.
2. Run read-only `kubectl` checks first.
3. Verify rollout, pod health, endpoints, recent warning/error events, and recent logs.
4. Run port-forward or smoke checks only when requested or already configured.
5. Report pass/fail with exact failing resources.
