# Multi-Tenancy — Patterns

## Four Isolation Models

| Model | Description | Cost | Isolation | Use When |
|-------|-------------|------|-----------|----------|
| **Pooled (shared schema)** | All tenants in one DB, `tenant_id` on every row | Lowest | Weakest — one bug leaks everything | Cost-sensitive, many small tenants, early stage |
| **Schema per tenant** | Separate Postgres schema per tenant, shared DB instance | Moderate | Good — schema boundary limits blast radius | Moderate compliance needs, hundreds of tenants |
| **Database per tenant** | Dedicated DB per tenant | Higher | Strong — full DB isolation | Enterprise customers, HIPAA/SOC2 Type II |
| **Instance per tenant** | Dedicated infrastructure per tenant | Highest | Full — complete separation | Largest enterprise, regulated industries (finance, government) |

**Migration path**: Design for the next tier up even when starting at pooled. Adding `tenant_id` to a table you forgot later requires a migration against live data. Changing isolation tier after launch is a multi-month project — plan for it, but don't build it prematurely.

---

## Tenant Context Propagation

Tenant identity must flow through every layer of the stack. The two safe approaches:

**Node.js: AsyncLocalStorage**
```ts
import { AsyncLocalStorage } from 'async_hooks';

const tenantContext = new AsyncLocalStorage<{ tenantId: string }>();

// Middleware: set at request entry
app.use((req, res, next) => {
  const tenantId = resolveTenantId(req); // from subdomain, JWT, or header
  tenantContext.run({ tenantId }, next);
});

// Anywhere in the call stack
function getCurrentTenant(): string {
  const ctx = tenantContext.getStore();
  if (!ctx) throw new Error('No tenant context — called outside request scope');
  return ctx.tenantId;
}
```

**Python: contextvars**
```python
from contextvars import ContextVar

current_tenant: ContextVar[str] = ContextVar('current_tenant')

# Middleware
async def tenant_middleware(request, call_next):
    tenant_id = resolve_tenant_id(request)
    token = current_tenant.set(tenant_id)
    try:
        return await call_next(request)
    finally:
        current_tenant.reset(token)  # always clean up
```

Never use global variables or thread-locals for tenant context in async code — they leak between requests under concurrent load.

**Tenant ID resolution priority**: subdomain (`tenant.app.com`) → JWT claim → `X-Tenant-ID` header → path parameter. Always validate server-side; never trust a client-supplied tenant ID without checking authorization.

---

## Per-Tenant Feature Flags

Tenant-scoped feature flags let you roll out features to enterprise customers first, run A/B tests per tenant, or offer premium features by plan tier.

```ts
async function isFeatureEnabled(tenantId: string, feature: string): Promise<boolean> {
  const override = await cache.get(`ff:${tenantId}:${feature}`);
  if (override !== null) return override === 'true';

  const tenant = await db.tenant.findUnique({ where: { id: tenantId } });
  return tenant?.plan === 'enterprise' && ENTERPRISE_FEATURES.includes(feature);
}
```

Store overrides in Redis with a TTL. Fall back to plan-based defaults.

---

## Tenant-Aware Background Jobs

The most common source of cross-tenant data leaks is background jobs that forget to scope to a tenant.

```ts
// TRAP: processes all records, no tenant scoping
async function sendWeeklyDigest() {
  const users = await db.user.findMany({ where: { digestEnabled: true } });
  for (const user of users) await sendEmail(user.email, ...);
}

// FIX: tenant-scoped job, run per-tenant
async function sendWeeklyDigestForTenant(tenantId: string) {
  const users = await db.user.findMany({
    where: { tenantId, digestEnabled: true }
  });
  for (const user of users) await sendEmail(user.email, ...);
}
```

Job queues should carry `tenantId` as a mandatory field. Workers must set tenant context before any DB access. Audit logs should record which tenant each job ran for.

---

## Tenant Lifecycle Management

```
provisioning → active → suspended → pending_deletion → deleted
```

| State | What Changes |
|-------|-------------|
| `provisioning` | Resources allocated; writes enabled; billing not yet started |
| `active` | Full access; billing running; quotas enforced |
| `suspended` | Read-only or no access; billing paused; data retained |
| `pending_deletion` | No access; retention timer running (per regulatory requirements) |
| `deleted` | Data purged; audit log retained per compliance policy |

Automate provisioning (schema creation, default config, seed data). Manual provisioning doesn't scale past 50 tenants. Build suspension and deletion as first-class workflows from day one — enterprise customers will ask about your offboarding story during procurement.
