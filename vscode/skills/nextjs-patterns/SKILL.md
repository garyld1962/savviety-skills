---
name: nextjs-patterns
description: "Next.js App Router patterns — server components, client components, server actions, routing, data fetching, middleware"
---

# Next.js App Router Patterns

Opinionated patterns for Next.js with the App Router. Use when writing or reviewing Next.js code.

## Server Components by Default

Every component is a Server Component unless you add `'use client'`. Keep it that way.

```tsx
// CORRECT — Server Component (default, no directive needed)
export default async function JobsPage() {
  const jobs = await getJobs();  // runs on server, no API call needed
  return <JobList jobs={jobs} />;
}

// ONLY add 'use client' when you NEED browser APIs or interactivity
'use client';
export function SearchFilter({ onSearch }: Props) {
  const [query, setQuery] = useState('');
  // Uses useState → must be a Client Component
}
```

**Push `'use client'` as far down as possible.** Don't make a whole page a Client Component because one button needs `onClick`.

## File Routing

```
app/
├── layout.tsx              # Root layout (wraps everything)
├── page.tsx                # / route
├── jobs/
│   ├── page.tsx            # /jobs
│   ├── [id]/
│   │   └── page.tsx        # /jobs/:id
│   └── loading.tsx         # Loading UI for /jobs
├── api/
│   └── jobs/
│       └── route.ts        # API route: /api/jobs
└── error.tsx               # Error boundary
```

## Data Fetching

### Server Components — fetch directly
```tsx
// CORRECT — Server Component fetches data
async function JobsPage() {
  const jobs = await db.query.jobs.findMany();
  return <JobList jobs={jobs} />;
}
```

### Mutations — use Server Actions
```tsx
// CORRECT — Server Action for mutations
'use server';

export async function createJob(formData: FormData) {
  const name = formData.get('name') as string;
  await db.insert(jobs).values({ name });
  revalidatePath('/jobs');
}
```

### Client-side data — use SWR or React Query
```tsx
'use client';
import useSWR from 'swr';

export function LiveJobStatus({ id }: { id: string }) {
  const { data } = useSWR(`/api/jobs/${id}/status`, fetcher);
  return <StatusBadge status={data?.status} />;
}
```

Do NOT use `useEffect` + `fetch` for data loading. Use SWR or React Query.

## API Routes

```typescript
// app/api/jobs/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const jobs = await getJobs();
  return NextResponse.json(jobs);
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  // Validate input
  const result = schema.safeParse(body);
  if (!result.success) {
    return NextResponse.json({ error: result.error }, { status: 400 });
  }
  const job = await createJob(result.data);
  return NextResponse.json(job, { status: 201 });
}
```

## Layouts and Loading States

- Use `layout.tsx` for shared UI (nav, sidebar) — it persists across navigations.
- Use `loading.tsx` for instant loading feedback.
- Use `error.tsx` for error boundaries.

```tsx
// app/jobs/loading.tsx
export default function Loading() {
  return <JobsSkeleton />;  // Shows immediately while page loads
}
```

## Common Mistakes

- **Don't** use `getServerSideProps` or `getStaticProps` — those are Pages Router. Use async Server Components.
- **Don't** create API routes just to fetch data in Server Components — query the database directly.
- **Don't** put `'use client'` at the top of page files — pages should be Server Components.
- **Don't** use `useRouter` for data mutations — use Server Actions.
- **Don't** store server-only secrets in `NEXT_PUBLIC_*` env vars — those are exposed to the browser.
