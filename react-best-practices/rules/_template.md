---
title: \<title>
impact: \<impact>
description: \<description>
tags: \<tags>
---

## \<title>

**Impact (\<impact: LOW, MEDIUM, HIGH, CRITICAL>):** \<description>

Brief explanation of the rule and why it matters. This should be clear and concise, explaining what breaks when the rule is ignored.

**Guidelines:**

1.  **\<Topic>:**
    - \<directive>

**Incorrect (description of what's wrong):**

```tsx
// Bad code example here
export function Bad() {
  return <div onClick={save}>Save</div>;
}
```

**Correct (description of what's right):**

```tsx
// Good code example here
export function Good() {
  return (
    <button type="button" onClick={save}>
      Save
    </button>
  );
}
```

Reference: [Link to documentation or resource](https://example.com)
