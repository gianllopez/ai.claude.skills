---
title: API Data Layer & Query Management
impact: HIGH
description: Enforces strict usage of React Query Kit for data fetching, domain-based organization and a centralized Axios client with auth interceptors.
tags: architecture, core, api
---

## API Data Layer & Query Management

**Impact (HIGH):** Centralizing _API_ logic ensures consistent caching strategies, type safety across network boundaries, and unified authentication handling. Letting errors propagate naturally to _React Query_ enables proper error state handling via `isError` and `error` in the consuming component.

**Guidelines:**

1.  **Library Standard:** Must use `react-query-kit` (`createQuery`, `createMutation`) to encapsulate _Query Keys_ and _Fetchers_.
2.  **Directory Structure:**
    - _API_ hooks must be grouped by domain in `@/core/api/<domain>/`.
    - Files should be named `use-<members|action>.ts` (e.g., `use-assets.ts`, `use-create-asset.ts`).
3.  **Type Definitions:**
    - Define `Response` (_API_ Contract), `Data` (UI consumption), and `Variables`.
    - Return types must be explicit.
4.  **Query Keys:**
    - Format: `'@<domain>/<hook-name>'`.
    - Example: `'@users/use-assets'`.
5.  **Axios Configuration:**
    - Use a central instance (`@/core/lib/axios`).
    - Implement `protected: true` via interceptors to inject the `Authorization` header.
    - Augment `AxiosRequestConfig` to support the custom `protected` property.

**Incorrect (Inline fetch, raw keys):**

```typescript
// ./app/users.tsx

// Bad: Inline fetching, no types, hardcoded key, error suppressed with fallback
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

export function Users() {
  const { data } = useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      try {
        return (await axios.get('/users')).data;
      } catch {
        return []; // Bad: Suppresses error — isError will never be true
      }
    },
  });
}
```

**Correct (Structured, Typed, Protected):**

```typescript
// ./core/lib/axios.ts

import axios, { HttpStatusCode } from 'axios';
import * as SessionHelper from '@/core/helpers/session'; // Module import (Best Practice)

export const api = axios.create({ baseURL: process.env.EXPO_PUBLIC_API_URL });

api.interceptors.request.use(
  (config) => {
    if (config.protected) {
      const token = SessionHelper.getToken();
      if (token) {
        config.headers.set('Authorization', `Bearer ${token}`);
      }
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// ... Response interceptor for 401 logout ...
```

```typescript
// ./core/api/users/use-assets.ts

import { createQuery } from 'react-query-kit';
import { QUERY } from '@/core/config/constants';
import { api } from '@/core/lib/axios';
import type { Asset } from '@/core/types/users';

type Response = Asset[];

type Data = Response;

type Variables = string;

export const useAssets = createQuery<Data, Variables>({
  queryKey: ['@users/use-assets'],
  fetcher: request,
  staleTime: QUERY.TIME.NONE,
});

async function request(id: Variables) {
  const { data } = await api.get<Response>(`/users/${id}/assets/`, {
    protected: true,
  });
  return data;
}
```

```typescript
// ./core/typings/axios.d.ts

import 'axios';

declare module 'axios' {
  export interface AxiosRequestConfig {
    protected?: boolean;
  }
}
```

Reference: [React Query Kit](https://tanstack.com/query/v4/docs/framework/react/community/liaoliao666-react-query-kit)
