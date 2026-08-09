---
title: Derived Values Over Stored State
impact: HIGH
description: Computes values from existing props and state during render instead of duplicating them into useState and keeping them in sync.
tags: state, hooks, rendering
---

## Derived Values Over Stored State

**Impact (HIGH):** Every piece of state that could have been computed is a second source of truth, and two sources of truth eventually disagree. The disagreement reaches users as a stale total, a filter one keystroke behind, or a row that survives its own deletion. Deriving during render makes the inconsistent state impossible to represent, which is a stronger guarantee than remembering to synchronize it.

**Guidelines:**

1.  **If it can be computed, compute it:**
    - A value derived from props or state is calculated in render, not stored
2.  **Props copied into state freeze at mount:**
    - `useState(props.value)` captures the first value and stops responding to the prop; the component then works right up until the prop changes, which is what makes it hard to spot in review
    - Use the prop directly, or remount deliberately with `key` when a reset is the actual intent (see the identity rule)
3.  **Store the minimal representation:**
    - An `id`, not the selected object; a sort key, not a sorted copy; a filter string, not the filtered array
    - Storing the object means holding a snapshot that goes stale when the source updates
4.  **Deriving is not a performance question:**
    - An unmemoized derivation is correct, and the compiler memoizes what render produces anyway
    - A hand-written `useMemo` around a derivation is the exception, and it has to say what the compiler could not see (see the render-stability rule)
5.  **Flags derived from status stay in render:**
    - `const isPending = status === 'submitting'` is a variable, never its own state

**Incorrect (a prop frozen into state, two states an effect has to keep in sync, a stale snapshot):**

```tsx
type Props = {
  users: User[];
  query: string;
};

export function UserPicker({ users, query }: Props) {
  // Bad: a prop copied into state — nothing ever calls setLocalQuery, so from the
  // second render on this can only be stale
  const [localQuery, setLocalQuery] = useState(query);
  const [filtered, setFiltered] = useState(users);
  const [hasResults, setHasResults] = useState(true);
  // Bad: holds a snapshot — after the user is renamed upstream this still shows the old name
  const [selected, setSelected] = useState<User | null>(null);

  useEffect(() => {
    const next = users.filter((u) => u.name.includes(localQuery));
    setFiltered(next);
    setHasResults(next.length > 0);
  }, [users, localQuery]);

  return (
    <Results
      items={filtered}
      empty={!hasResults}
      selectedName={selected?.name}
      onSelect={setSelected}
    />
  );
}
```

**Correct (the prop is read as a prop, one state for the one real input, the rest derived):**

```tsx
type Props = {
  users: User[];
  query: string;
};

export function UserPicker({ users, query }: Props) {
  // Good: store the identity, not the object
  const [selectedId, setSelectedId] = useState<string | null>(null);

  // Good: cannot disagree with users or query, because it is recomputed from them
  const filtered = users.filter((u) => u.name.includes(query));
  const selected = users.find((u) => u.id === selectedId) ?? null;

  return (
    <Results
      items={filtered}
      selectedName={selected?.name}
      onSelect={setSelectedId}
    />
  );
}
```

Reference: [Choosing the state structure](https://react.dev/learn/choosing-the-state-structure)
