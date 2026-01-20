---
title: API Data Layer & Query Management
impact: HIGH
description: Enforces strict usage of React Query Kit for data fetching, domain-based organization, safe error handling, and a centralized Axios client with auth interceptors.
tags: architecture, core, api
---

## API Data Layer & Query Management

**Impact (HIGH):** Centralizing _API_ logic ensures consistent caching strategies, type safety across network boundaries, and unified authentication handling. The safe return pattern prevents UI crashes due to backend failures.

**Guidelines:**

1.  **Library Standard:** Must use `react-query-kit` (`createQuery`, `createMutation`) to encapsulate _Query Keys_ and _Fetchers_.
2.  **Directory Structure:**
    - _API_ hooks must be grouped by domain in `@/core/api/<domain>/`.
    - Files should be named `use-<members|action>.ts` (e.g., `use-assets.ts`, `use-create-asset.ts`).
3.  **Type Definitions:**
    - Define `QueryResponse` (_API_ Contract), `QueryData` (UI consumption), and `QueryVariables`.
    - Return types must be explicit.
4.  **Query Keys:**
    - Format: `'@<domain>/<hook-name>'`.
    - Example: `'@users/use-assets'`.
5.  **Error Handling (safe return):**
    - Fetchers must use `try/catch`.
    - **On Error:** Return a safe fallback (`[]` for lists, `null` for objects) to ensure the UI renders a empty state rather than crashing. Do not throw errors to the UI layer.
6.  **Axios Configuration:**
    - Use a central instance (`@/core/lib/axios`).
    - Implement `protected: true` via interceptors to inject the `Authorization` header.
    - Augment `AxiosRequestConfig` to support the custom `protected` property.

**Incorrect (Inline fetch, unsafe errors, raw keys):**

```typescript
// ./app/users.tsx

// Bad: Inline fetching, no types, hardcoded key
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

export function Users() {
  const { data } = useQuery({
    queryKey: ['users'],
    queryFn: async () => (await axios.get('/users')).data,
  });
  // If API fails, 'data' is undefined and might crash if accessed blindly
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

type QueryResponse = Asset[];

type QueryData = QueryResponse;

type QueryVariables = string;

export const useAssets = createQuery<QueryData, QueryVariables>({
  queryKey: ['@users/use-assets'],
  fetcher: request,
  staleTime: QUERY.TIME.NONE,
});

async function request(id: QueryVariables) {
  try {
    const { data } = await api.get<QueryResponse>(`/users/${id}/assets/`, {
      protected: true, // Custom config
    });
    return data;
  } catch {
    return []; // Safe fallback (No crash)
  }
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
