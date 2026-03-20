---
description: >-
  Post-deploy verification for Kubernetes: checks pod health, service endpoints,
  recent events, log errors, and rollout status. Use after any K8s deployment.
argument-hint: '[--namespace <ns>] [--full]'
agent: 'agent'
tools:
  - execute
  - read
  - search
---

# Kubernetes Post-Deploy Verification

Systematic health check after a Kubernetes deployment. Verifies pods are running, services have endpoints, no error events, and applications are responding.

## When to Use

- After deploying to Kubernetes (kubectl apply, helm install, kustomize)
- After a rollout restart
- When something feels wrong but you're not sure what
- As a smoke test before handing off to users

## Arguments

- `--namespace <ns>` — Kubernetes namespace to check
- `--full` — include pod log analysis (slower, more thorough)

---

## CRITICAL: Do Not Guess

- **Namespace**: If `--namespace` was not provided, DETECT it. Do NOT assume "default" or any other namespace. Follow the discovery steps below.
- **Pod names**: Always get actual pod names from `kubectl get pods`. Do NOT construct pod names from deployment names — pod suffixes are random hashes.
- **Health endpoints**: Only attempt HTTP health checks if you can VERIFY the endpoint exists in the deployment spec or project docs. Do NOT guess `/health` or `/healthz`.
- **kubectl context**: Verify you are connected to the right cluster before running commands. A wrong context means wrong results.
- **Port numbers**: Read them from service specs. Do NOT assume 80, 8080, or 3000.

---

## Step 1: Namespace Discovery

If `--namespace` was NOT provided, detect it in this order:

```bash
# 1. Check for kustomization.yaml with namespace field
grep -r "namespace:" kustomization.yaml 2>/dev/null | head -1

# 2. Check current kubectl context
kubectl config view --minify -o jsonpath='{..namespace}' 2>/dev/null

# 3. Check .github/copilot-instructions.md for namespace references
```

If none found: **ASK the user.** Do NOT default to "default" namespace.

### Example: Correct

```
No --namespace provided. Detected "bakerst" from kustomization.yaml.
Using namespace: bakerst
```

### Example: INCORRECT

```
# WRONG: Assuming a namespace without checking
kubectl get pods -n default  # ← might be completely wrong
```

---

## Step 2: Pod Health

```bash
kubectl get pods -n <namespace> -o wide --no-headers
```

For EACH pod in the output, classify its status:

| Status | Verdict | Action |
|--------|---------|--------|
| Running, all containers ready (e.g., `1/1`, `2/2`) | PASS | None |
| Running, not all ready (e.g., `0/1`, `1/2`) | WARN | Check readiness probes |
| CrashLoopBackOff | **FAIL** | Check logs (Step 7) |
| ImagePullBackOff | **FAIL** | Image not found or auth issue |
| Pending | WARN | Check events for scheduling issues |
| Error | **FAIL** | Check logs (Step 7) |
| Terminating | INFO | Cleanup in progress — check again in 30s |
| Completed | INFO | Job or init container finished normally |

**Count:** Total pods, healthy, warning, failed.

### Example: Pod health output

```
Pod Health (namespace: bakerst)
  brain-7d4f8b6c9-x2k4m    Running  1/1  ✓
  worker-5c8a9d3e7-m8n2p    Running  1/1  ✓
  gateway-6b3e7f1a2-q9w5r   Running  1/1  ✓
  ui-4a2c6d8e0-j3k7t        CrashLoopBackOff  0/1  ✗

  Result: 3/4 healthy, 1 FAILED
```

---

## Step 3: Rollout Status

For each deployment and statefulset in the namespace:

```bash
kubectl rollout status deploy/<name> -n <namespace> --timeout=10s 2>&1
```

**Important:** Use `--timeout=10s` to prevent hanging on stalled rollouts.

Report whether each rollout is complete or still progressing.

### Example: Correct

```bash
# Check EACH deployment separately with timeout
kubectl rollout status deploy/brain -n bakerst --timeout=10s 2>&1
kubectl rollout status deploy/worker -n bakerst --timeout=10s 2>&1
```

### Example: INCORRECT

```bash
# WRONG: No timeout — will hang indefinitely if rollout is stuck
kubectl rollout status deploy/brain -n bakerst
```

---

## Step 4: Service Endpoints

```bash
kubectl get svc -n <namespace> -o wide --no-headers
kubectl get endpoints -n <namespace> --no-headers
```

For each service, check that it has at least one endpoint.

**If a service has ZERO endpoints:** **FAIL** — pods may not match the service selector. This is a common deployment issue.

### Example: Endpoint check

```
Service Endpoints (namespace: bakerst)
  brain     ClusterIP  10.96.1.5:3000   → 1 endpoint  ✓
  gateway   ClusterIP  10.96.1.6:8080   → 1 endpoint  ✓
  ui        NodePort   10.96.1.7:8080   → 0 endpoints ✗  ← FAIL: no matching pods
```

---

## Step 5: Recent Events

```bash
kubectl get events -n <namespace> --sort-by=.lastTimestamp --field-selector type!=Normal 2>/dev/null | tail -20
```

Flag any Warning or Error events. Common patterns to watch for:

| Event Reason | Meaning | Severity |
|-------------|---------|----------|
| `FailedScheduling` | Resource pressure or node affinity mismatch | WARN |
| `Unhealthy` | Liveness or readiness probe failing | WARN |
| `BackOff` | Container crash loop | FAIL |
| `FailedMount` | Volume mount issue (PVC, ConfigMap, Secret) | FAIL |
| `FailedCreate` | Controller cannot create pod | FAIL |
| `FailedPull` / `ErrImagePull` | Image not found or registry auth | FAIL |

---

## Step 6: HTTP Health Checks (if applicable)

**Only attempt this if** you can verify health endpoints exist from:
- Deployment spec `readinessProbe` or `livenessProbe` configuration
- Project documentation (`.github/copilot-instructions.md`)

**Do NOT guess health endpoint paths.** If you cannot verify, SKIP this step.

If verified:

```bash
# Port-forward with a timeout
kubectl port-forward -n <namespace> svc/<name> <local>:<remote> &
PF_PID=$!
sleep 2
curl -sf --max-time 5 http://localhost:<local>/<verified-path>
RESULT=$?
kill $PF_PID 2>/dev/null
```

**Always clean up the port-forward process**, even on error.

---

## Step 7: Log Analysis (with `--full` only)

For each FAILED or WARNING pod:

```bash
kubectl logs -n <namespace> <pod-name> --tail=50 --timestamps
```

Scan for (case-insensitive):
- `error`, `fatal`, `panic`, `exception`
- Stack traces
- `connection refused`, `timeout`, `ECONNREFUSED`
- Auth failures (`401`, `403`, `unauthorized`)

For CrashLoopBackOff pods, also check previous container:

```bash
kubectl logs -n <namespace> <pod-name> --previous --tail=30
```

**Do NOT read logs for healthy pods** unless `--full` was passed — it adds noise.

---

## Step 8: Report

```
## Deploy Verification: <namespace>

| Check | Result | Details |
|-------|--------|---------|
| Pods | PASS/WARN/FAIL | N/N healthy |
| Rollouts | PASS/FAIL | N/N complete |
| Endpoints | PASS/FAIL | N/N services have endpoints |
| Events | PASS/WARN | N warnings in last 10m |
| Health HTTP | PASS/FAIL/SKIP | N/N responding (or "skipped — no verified endpoints") |
| Logs | PASS/WARN/SKIP | N error patterns found (or "skipped — no --full") |

**Verdict: HEALTHY / DEGRADED / UNHEALTHY**

[If DEGRADED or UNHEALTHY: list specific issues with suggested remediation]
```

### Verdict Logic

- **HEALTHY**: All checks PASS or INFO
- **DEGRADED**: Any WARN, no FAIL
- **UNHEALTHY**: Any FAIL

---

## Rules

1. **Non-destructive.** This prompt only READS. It NEVER modifies, restarts, scales, or deletes anything.
2. **Timeout everything.** Every kubectl command must have `--timeout` or be wrapped in a timeout. Hanging commands block the user.
3. **Adapt to the cluster.** Not all clusters have metrics-server, ingress, or HPA. Skip checks gracefully when resources aren't available. Do NOT error on missing optional resources.
4. **Port-forward cleanup.** ALWAYS kill port-forward processes, even on error.
5. **Sensitive data.** NEVER print Secret values. Only report Secret names and whether they exist.
