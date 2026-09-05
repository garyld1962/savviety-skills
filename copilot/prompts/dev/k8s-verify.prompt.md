---
description: >-
  Verify a Kubernetes deployment by checking namespace, rollouts, pod health,
  endpoints, events, and optional logs without guessing runtime details.
argument-hint: '[--namespace <ns>] [--full]'
agent: 'agent'
tools:
  - execute
  - read
  - search
---

# Kubernetes Deploy Verify

Use this prompt after a Kubernetes deployment, rollout restart, or suspicious
cluster event.

Follow the skills:

- `.github/skills/k8s-verify/SKILL.md`
- `.github/skills/execution-environment/SKILL.md`

## Copilot-native usage

- Verify the cluster context and namespace before running checks.
- Keep the report operational and evidence-based.
