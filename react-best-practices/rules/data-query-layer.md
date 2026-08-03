---
title: Query Layer & Data Ownership
impact: HIGH
description: Encapsulates every server request in a typed react-query-kit hook grouped by domain, and keeps fetching, caching, and auth out of components.
tags: data, react-query, architecture
---

## Query Layer & Data Ownership

**Impact (HIGH):** A component that fetches takes on a problem it cannot finish: caching, deduplication, cancellation, retry, and invalidation. Spread across components, each one solves a different subset, and the same endpoint ends up requested three times per screen under three different key strings. A typed query layer answers all of that once and leaves the component consuming state instead of orchestrating requests.

**Guidelines:**

1.  **One way to reach the network:**
    - Every request goes through `createQuery` / `createMutation` from `react-query-kit`; components never call `useQuery`, `useMutation`, or `axios` directly
2.  **Structure by domain, keys declared once:**
    - Hooks live under `core/api/<domain>/`, named `use-<members|action>.ts` (see the folder-structure rule)
    - Query keys follow `'@<domain>/<hook-name>'`, declared in the hook itself — a bare `['invoices']` written at a call site is how two components end up with two caches of the same data
    - Invalidate with the owning hook's `getKey()`, never a hand-written copy of the key
3.  **The client and the middlewares are configured once:**
    - The _Axios_ instance, the query client, and the mutation middlewares are configured library instances, so they live where the structure rule puts them: `core/lib/`
    - Nothing outside that folder constructs one of these; the rest of the codebase imports the already-configured instance, so there is exactly one cache and one interceptor chain per process
4.  **Types at the boundary, in request order:**
    - Declare `Variables`, then `Response`, then `Data` — the order follows the request's own direction: what goes out, what comes back, what the _UI_ consumes
    - When the payload needs no transform, `Data` is an alias and says so: `type Data = Response`
    - When they diverge, the transform belongs in the fetcher, so every consumer sees the same shape
5.  **Let errors propagate:**
    - A `try`/`catch` in the fetcher that returns `[]` makes `isError` permanently false and the error branch unreachable — the screen then reports "no results" for what was actually a failure
6.  **Auth is not a component concern:**
    - Token injection and 401 handling live in the _Axios_ interceptors, declared once
    - Access control before render belongs to the protected layout route, driven by the session query and a declarative redirect
    - A `useEffect` that navigates is the wrong tool for both: it paints the protected screen first and redirects after
7.  **Parallel by default, dependent only when it is:**
    - Independent hooks called in the same component already run in parallel — nothing to arrange
    - Chaining with `enabled` makes the second request wait for the first, so use it only when the second genuinely needs the first's result
8.  **Paginated queries hold the previous page:**
    - When the page is part of the key, every page change is a fresh cache entry with no data, so the consumer's pending branch fires and the whole table blanks on each step
    - `placeholderData: keepPreviousData` in the hook definition serves the previous page while the next one resolves, which turns that blank into an `isPlaceholderData` dim (see the async-states rule)
9.  **Mutations invalidate through a middleware:**
    - Compose invalidation with `use` on `createMutation`, so it is declared beside the mutation instead of hand-written into every `onSuccess`
    - Pass the keys the mutation actually affects; a mutation that invalidates everything is a cache with extra steps
    - Calling a query's `refetch()` from a mutation, or writing the response into local state, forks the cache

**Incorrect (inline query, hand-written key, swallowed error, effect that redirects, needless waterfall):**

```tsx
// ./app/routes/invoices.tsx
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

export default function InvoicesRoute() {
  const navigate = useNavigate();
  const session = useSessionStore((s) => s.session);

  // Bad: the protected screen paints, then navigates away
  useEffect(() => {
    if (!session) {
      navigate('/login');
    }
  }, [session, navigate]);

  // Bad: inline query, key written at the call site, error swallowed so isError never fires
  const { data } = useQuery({
    queryKey: ['invoices'],
    queryFn: async () => {
      try {
        return (await axios.get('/invoices')).data;
      } catch {
        return [];
      }
    },
  });

  // Bad: enabled turns two independent requests into a waterfall
  const { data: customers } = useQuery({
    queryKey: ['customers'],
    queryFn: fetchCustomers,
    enabled: Boolean(data),
  });

  return <InvoiceTable invoices={data} customers={customers} />;
}
```

**Correct (typed hook per domain, types in request order, key declared once):**

```ts
// ./app/core/api/invoices/use-invoices.ts

import { createQuery } from 'react-query-kit';
import { api } from '~/core/lib/axios';
import type { Invoice } from '~/core/types/invoices';

type Variables = { status: string };

type Response = Invoice[];

type Data = Response;

export const useInvoices = createQuery<Data, Variables>({
  queryKey: ['@invoices/use-invoices'],
  fetcher: request,
});

async function request({ status }: Variables) {
  const { data } = await api.get<Response>('/invoices/', {
    params: { status },
    protected: true,
  });

  return data;
}
```

```ts
// ./app/core/lib/react-query/middlewares.ts

export const withInvalidation = (...keys: QueryKey[]): MiddlewareFn => {
  return (useMutationNext) => {
    return (options) => {
      return useMutationNext({
        ...options,
        onSuccess: (_data, _variables, _onMutateResult, context) => {
          for (const key of keys) {
            context.client.invalidateQueries({ queryKey: key });
          }

          options.onSuccess?.(_data, _variables, _onMutateResult, context);
        },
      });
    };
  };
};
```

```ts
// ./app/core/api/invoices/use-mark-paid.ts

import { createMutation } from 'react-query-kit';
import { api } from '~/core/lib/axios';
import { withInvalidation } from '~/core/lib/react-query/middlewares';
import type { Invoice } from '~/core/types/invoices';
import { useInvoices } from './use-invoices';

type Variables = {
  id: string;
  reference: string;
};

type Response = Invoice;

type Data = Response;

export const useMarkPaid = createMutation<Data, Variables>({
  mutationFn: request,
  // Good: invalidation declared beside the mutation, with the key its owner exposes
  use: [withInvalidation(useInvoices.getKey())],
});

async function request({ id, reference }: Variables) {
  const { data } = await api.patch<Response>(
    `/invoices/${id}/paid/`,
    { reference },
    { protected: true },
  );

  return data;
}
```

```tsx
// ./app/routes/invoices.tsx

export default function InvoicesRoute() {
  // Good: two independent hooks, so both requests start together
  const invoices = useInvoices({ variables: { status: 'open' } });
  const customers = useCustomers();

  return <InvoiceTable invoices={invoices.data} customers={customers.data} />;
}
```

```tsx
// ./app/routes/protected-layout.tsx

export default function ProtectedLayout() {
  const session = useSession();

  if (session.isPending) {
    return <AppSkeleton />;
  }

  // Good: the redirect is part of the render output, so nothing protected paints first
  if (!session.data) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}
```

Reference: [React Query Kit](https://github.com/liaoliao666/react-query-kit)
