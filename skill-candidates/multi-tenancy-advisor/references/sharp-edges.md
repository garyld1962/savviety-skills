# Multi-Tenancy — Sharp Edges

---

## Missing Tenant Context in Background Jobs

**Severity**: Critical
**Situation**: A background job processes records across all tenants without scoping to a single tenant.

```python
# TRAP: returns data from ALL tenants
async def send_weekly_digest():
    users = await db.fetch("SELECT * FROM users WHERE digest_enabled = true")
    for user in users:
        await send_email(user.email, ...)

# FIX: job carries tenant_id, sets context before DB access
async def send_weekly_digest(tenant_id: str):
    current_tenant.set(tenant_id)
    users = await db.fetch(
        "SELECT * FROM users WHERE tenant_id = $1 AND digest_enabled = true",
        tenant_id
    )
```

**Fix**: Every job queue message must carry `tenant_id` as a mandatory field. Workers set tenant context before any DB or cache access. Audit logs record the tenant for every job execution.

---

## Caching Without Tenant Isolation

**Severity**: Critical
**Situation**: Cached responses or objects are keyed without tenant scope. Tenant A's request populates a cache entry that Tenant B reads.

```ts
// TRAP: shared cache key — any tenant gets any tenant's data
const data = await cache.get(`user:${userId}`);

// FIX: tenant-scoped key
const data = await cache.get(`${tenantId}:user:${userId}`);
```

**Fix**: Every cache key must be prefixed with `tenantId`. This applies to Redis, CDN caches, in-process caches, and Apollo/React Query caches. Audit all cache.get/set calls. A single unscoped key is a data breach waiting for traffic.

---

## Global State Without Tenant Scope

**Severity**: High
**Situation**: Module-level singletons, in-memory stores, or configuration objects hold state that is not scoped to a tenant. One tenant's data or config bleeds into another's request.

```ts
// TRAP: module-level cache shared across all tenants
const featureFlags: Record<string, boolean> = {};

function isEnabled(feature: string): boolean {
  return featureFlags[feature] ?? false;
}

// FIX: tenant-scoped lookup
function isEnabled(tenantId: string, feature: string): boolean {
  return tenantFeatureFlags.get(tenantId)?.[feature] ?? false;
}
```

**Fix**: Audit every module-level variable, singleton, and in-process store. If it holds data that varies by tenant, it must be keyed by `tenantId`. Use AsyncLocalStorage / contextvars for request-scoped tenant state — not module-level globals.

---

## Shared Database Sequence IDs Leaking Tenant Existence

**Severity**: High
**Situation**: Shared auto-increment sequences expose tenant enumeration. If Tenant A creates record #500 and Tenant B creates record #501, each tenant can infer the other exists and estimate their activity volume.

```sql
-- TRAP: shared sequence, exposes cross-tenant cardinality
CREATE TABLE orders (id SERIAL PRIMARY KEY, tenant_id UUID, ...);

-- FIX: per-tenant UUIDs or random IDs
CREATE TABLE orders (id UUID DEFAULT gen_random_uuid() PRIMARY KEY, tenant_id UUID, ...);
```

**Fix**: Use UUIDs or other non-sequential identifiers for any ID that is exposed to tenants. If sequential IDs are required for performance, use per-tenant sequences and never expose raw DB IDs in APIs.

---

## Over-Engineering Isolation for Early-Stage Products

**Severity**: Medium
**Situation**: A startup with 10 tenants provisions a separate database per tenant. Migrations require N database connections. Backups multiply. Cost spikes. Engineering velocity collapses.

```
10 tenants × separate DB = 10× operational complexity
At 10 tenants you can manually fix a cross-tenant bug in minutes.
At 10 tenants, "isolation" is not your security problem — authentication is.
```

**Fix**: Start with pooled (shared schema + `tenant_id` everywhere). Design the migration path to schema-per-tenant. Build it when your first enterprise customer's contract requires it, not before.

---

## Under-Engineering Isolation for Enterprise Customers

**Severity**: High
**Situation**: A healthcare or financial services customer signs a contract that includes data isolation requirements. Your product uses a shared schema with RLS. Legal says that's not sufficient. Deal falls through or you face audit findings.

```
Regulated industry requirements (examples):
  HIPAA: PHI must be logically or physically separated
  FedRAMP: Data must reside in dedicated environment
  SOC2 Type II: Evidence of isolation controls required
```

**Fix**: Know your target customer segment before choosing an isolation model. If you intend to sell to regulated industries, design for database-per-tenant from the start (even if you defer provisioning it). The migration from shared schema to dedicated DB after you have 500 active tenants is a 6-month project.
