# Multi-Tenancy — Decisions

## Isolation Model Selection Matrix

| Factor | Pooled (shared schema) | Schema per tenant | Database per tenant | Instance per tenant |
|--------|----------------------|------------------|--------------------|--------------------|
| **Tenant count** | Thousands | Hundreds | Tens–hundreds | Tens |
| **Data sensitivity** | Low–medium | Medium | High | Critical |
| **Regulatory requirement** | None | Light (SOC2 Type I) | Heavy (HIPAA, SOC2 Type II) | Strictest (FedRAMP, financial) |
| **Cost sensitivity** | Very high | High | Medium | Low |
| **Migration complexity** | Lowest | Medium | High | Highest |
| **Schema migration** | Single migration | N migrations (batch) | N migrations (batch) | N migrations per env |
| **Backup granularity** | Shared backup | Per-schema | Per-database | Full infra snapshot |
| **Query performance** | Shared contention | Isolated | Isolated | Isolated |

**Decision rule**: Start at pooled. Move to schema-per-tenant when you win your first enterprise customer with compliance requirements. Move to database-per-tenant when a customer's contract requires physical data isolation. Instance-per-tenant is a special-case for regulated industries — rarely needed before Series B.

---

## Row-Level Security vs Schema Separation

**Use Row-Level Security (RLS) when**:
- Pooled model; many small tenants
- Single Postgres instance; cost constraints
- You have strong DBA discipline and can enforce policies consistently

**Use schema separation when**:
- Tenant data is meaningfully sensitive and you want schema-level enforcement
- You need per-tenant schema customization (different columns per customer)
- Migration rollout needs to be per-tenant (canary deployments)

**The RLS trap**: RLS is only as strong as your policy coverage. One table without a policy, one `SECURITY DEFINER` function that bypasses RLS, or a connection that runs as a superuser silently bypasses all isolation. Test with a non-privileged role. Force RLS even for table owners: `ALTER TABLE orders FORCE ROW LEVEL SECURITY`.

---

## Per-Tenant vs Shared Infrastructure for Compute

| | Shared compute | Dedicated compute per tenant |
|---|---|---|
| **Cost** | Much lower | 5–20x higher |
| **Isolation** | Application-enforced | Infrastructure-enforced |
| **Noisy neighbor risk** | Yes | No |
| **Compliance** | Usually sufficient | Required by some enterprise buyers |
| **Complexity** | Low | High (orchestration, scaling) |

Start shared. Add dedicated compute only when a customer's contract demands it or noisy-neighbor incidents become chronic.

---

## Migration Strategy When Changing Isolation Models

Changing isolation models is one of the hardest migrations in SaaS engineering. Plan for 3–6 months of engineering time.

**Pooled → Schema per tenant**:
1. Add schema creation to tenant provisioning (new tenants get own schema immediately)
2. Build a migration script that copies tenant data from shared tables to tenant schema
3. Run dual-write: write to both shared and tenant schema, read from tenant schema
4. Migrate tenants in batches of 10–20, verify, pause, continue
5. Remove shared table reads after all tenants migrated

**Schema per tenant → Database per tenant**:
1. Provision new database
2. Replicate schema + data using logical replication or dump/restore
3. Switch connection string in tenant config
4. Decommission old schema after validation period

**Critical**: Never run schema migrations against all tenants simultaneously. Use rolling batches with canary validation. One migration failure should pause the rollout, not leave half your tenants on a different schema version.

---

## Naming Conventions for Tenant-Scoped Resources

Consistent naming prevents accidental cross-tenant access:

```
# Database schema
schema: tenant_{tenant_id}

# S3 buckets / object keys
s3://my-app/{tenant_id}/uploads/{filename}

# Redis keys
{tenant_id}:{resource_type}:{resource_id}

# Job queue names
jobs::{tenant_id}::{job_type}

# Log streams
/app/{environment}/{tenant_id}/{service}
```

Tenant ID must always be the first segment in any namespaced resource — makes ACL policies and prefix-based access controls trivial to implement.
