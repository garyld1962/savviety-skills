# Kubernetes Verify Workflow

Use this after deployment or when debugging cluster rollout status.

## Steps

1. Identify namespace, workload, cluster context, and expected version.
2. Check rollout status.
3. Inspect pods, events, readiness, restarts, and image tags.
4. Check service and ingress health when applicable.
5. Read targeted logs for failing pods.
6. Report `PASS`, `WARN`, or `FAIL` with exact commands and evidence.

Ask before running commands against a cluster when context or namespace is unclear.

