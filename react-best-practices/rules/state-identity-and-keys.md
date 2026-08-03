---
title: List Keys & Component Identity
impact: HIGH
description: Requires stable data-derived keys and uses key deliberately to reset component state instead of synchronizing it with an effect.
tags: state, rendering, lists
---

## List Keys & Component Identity

**Impact (HIGH):** `key` is not a lint requirement to satisfy — it is how _React_ decides which component instance corresponds to which item. An index key on a list that can be reordered, filtered, or prepended attaches the wrong state to the wrong row: an open menu jumps, an input keeps the previous row's draft, a checkbox stays checked on a different item. The list looks correct right up until state enters it.

**Guidelines:**

1.  **The key is identity from the data:**
    - `item.id` — never the array index, never `Math.random()`, never the position in a composite string
2.  **Index keys are only safe on a static list:**
    - Never reordered, never filtered, never prepended, and holding no internal state
3.  **A key that changes every render destroys the subtree:**
    - Focus, scroll position, uncontrolled input values, and animation state all reset, on every render
    - This is what a random key buys: the warning goes away and the defect gets worse
4.  **Use `key` deliberately to reset:**
    - `<TaskEditor key={task.id} />` restarts the editor's internal state when the task changes — this replaces the effect that copied the prop into state
5.  **Keys are scoped to siblings:**
    - They need to be unique among their siblings, not globally
6.  **A missing identity is a data problem:**
    - Concatenating the index to silence the warning hides it; if the payload has no stable id, fix the payload

**Incorrect (index keys on a filterable list):**

```tsx
type Props = {
  tasks: Task[];
  query: string;
};

export function TaskList({ tasks, query }: Props) {
  const visible = tasks.filter((t) => t.title.includes(query));

  return (
    <ul>
      {/* Bad: filtering shifts every index — row state follows the wrong task */}
      {visible.map((t, index) => (
        <TaskRow key={index} task={t} />
      ))}
    </ul>
  );
}
```

**Incorrect (a random key, which silences the warning and rebuilds every row):**

```tsx
type Props = { entries: LogEntry[] };

export function LogList({ entries }: Props) {
  return (
    <ul>
      {/* Bad: the payload has no id, so the warning was silenced with a random key.
          Every render produces new keys, so every row is destroyed and rebuilt —
          focus, scroll position and any uncontrolled input inside them reset */}
      {entries.map((e) => (
        <LogRow key={Math.random()} entry={e} />
      ))}
    </ul>
  );
}
```

**Incorrect (an effect undoing the defaults that mounting already applied):**

```tsx
type Props = { task: Task };

function TaskEditor({ task }: Props) {
  const form = useForm<FormValues>({
    defaultValues: { title: task.title },
  });

  // Bad: defaultValues are read at mount, so this effect exists only to patch an
  // instance that should have been a new one
  useEffect(() => {
    form.reset({ title: task.title });
  }, [task.id, form]);

  return <TaskForm form={form} />;
}
```

**Correct (identity from the data, and `key` as the reset mechanism):**

```tsx
type Props = {
  tasks: Task[];
  query: string;
};

export function TaskList({ tasks, query }: Props) {
  const visible = tasks.filter((t) => t.title.includes(query));

  return (
    <ul>
      {visible.map((t) => (
        <TaskRow key={t.id} task={t} />
      ))}
    </ul>
  );
}
```

```tsx
type Props = {
  tasks: Task[];
  query: string;
};

export function TaskPanel({ tasks, query }: Props) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const selected = tasks.find((t) => t.id === selectedId) ?? null;

  return (
    <>
      <TaskList tasks={tasks} query={query} onSelect={setSelectedId} />
      {/* Good: a new identity remounts the editor, so no effect has to reset it */}
      {selected ? <TaskEditor key={selected.id} task={selected} /> : null}
    </>
  );
}
```

```tsx
type Props = { task: Task };

function TaskEditor({ task }: Props) {
  // Good: defaultValues are read once at mount, and mounting is what the key controls
  const form = useForm<FormValues>({
    defaultValues: { title: task.title },
  });

  return <TaskForm form={form} />;
}
```

Reference: [Why does React need keys?](https://react.dev/learn/rendering-lists#why-does-react-need-keys)
