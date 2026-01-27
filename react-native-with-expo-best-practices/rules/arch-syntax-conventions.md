---
title: Syntax & Conciseness Conventions
impact: LOW
description: Enforces specific syntax patterns for iterators and type definitions to prioritize conciseness and visual scanning speed.
tags: architecture, syntax, conventions
---

## Syntax & Conciseness Conventions

**Impact (LOW):** Improves code conciseness and reduces visual noise in high-frequency patterns.

These rules aim to maximize the information density of the code, making it easier to scan logic without getting lost in verbose boilerplate.

### 1. Iterator Naming (Short-Hand Convention)

For inline array methods (`.map`, `.filter`, `.forEach`, etc.), strictly use the first letter of the collection's item name as the argument. This reduces horizontal scrolling and focuses attention on the logic.

**Exceptions:**

- **Complex Logic:** If the callback body requires a multi-line block (`{ ... }`) or complex destructuring, use the full descriptive singular name to maintain context.
- **Nested Loops:** If iterating within another iterator, use full names to avoid confusion (e.g., avoid `u` inside another `u`).

**Incorrect (verbose for simple logic):**

```typescript
// Too noisy for a simple ID extraction
const userIds = users.map((user) => user.id);

// Redundant naming
const activeItems = items.filter((item) => item.isActive);
```

**Correct (concise):**

```typescript
// Clean and focused on the operation
const userIds = users.map((u) => u.id);

const activeItems = items.filter((i) => i.isActive);
```

**Correct (exception for complex logic):**

```typescript
// Complex logic warrants a descriptive name
const richData = users.map((user) => {
  const isEligible = checkEligibility(user);
  return { ...user, isEligible };
});
```

### 2. Single-Property Type Definitions

To conserve vertical screen space, _TypeScript_ types (not interfaces) that contain exactly one property must be defined on a single line.

**Incorrect (wasted vertical space):**

```typescript
// Wastes 3 lines for 1 property
type Props = {
  visible: boolean;
};
```

**Correct (optimized):**

```typescript
// Efficient use of space
type Props = { visible: boolean };
```

### 3. Event Handler Naming Convention

Event handler implementations must use the `handle` prefix to distinguish them semantically from event props (which use the `on` prefix). This creates a clear visual distinction between the prop interface (what events the component accepts) and the implementation (what happens when the event fires). Using `on` for both the prop and the implementation creates ambiguity. The `handle` prefix makes it immediately clear that this is the concrete implementation being passed to the event prop.

**Incorrect (ambiguous naming):**

```typescript
export function MyScreen() {
  // Bad: Using 'on' prefix for implementation
  const onChangeText = (text: string) => {
    console.log(text);
  };

  const onPress = () => {
    console.log('Pressed');
  };

  return (
    <View>
      <Input onChangeText={onChangeText} />
      <Button onPress={onPress}>Continue<Button />
    </View>
  );
}
```

**Correct (semantic clarity):**

```typescript
export function MyScreen() {
  // Good: Using 'handle' prefix for implementations
  const handleChangeText = (text: string) => {
    console.log(text);
  };

  const handlePress = () => {
    console.log('Pressed');
  };

  return (
    <View>
      <Input onChangeText={handleChangeText} />
      <Button onPress={handlePress} />
    </View>
  );
}
```

Reference: [TypeScript Handbook - Object Types](https://www.typescriptlang.org/docs/handbook/2/objects.html)
