---
title: Composition Over Configuration
impact: HIGH
description: Composes components through children and slots instead of growing boolean and render-function props for every variation.
tags: architecture, components, composition
---

## Composition Over Configuration

**Impact (HIGH):** A component configured by flags grows one prop per request until its signature encodes every screen that ever used it, and its body becomes a chain of conditionals nobody can change safely. Composition moves that variation to the call site, where it is visible in the markup, and leaves the component with a single job. The test is simple: if adding a screen means adding a prop, the component is configured rather than composed.

**Guidelines:**

1.  **Slots over flags:**
    - `children` and named slot props (`header`, `actions`, `footer`) instead of booleans that toggle internal markup
2.  **Mutually exclusive booleans are not independent props:**
    - Two flags that are never true together are one discriminated union, or two components
3.  **Compound components express structure:**
    - `Card` / `CardHeader` / `CardBody` lets the caller assemble what this screen needs without the parent configuring it
4.  **Render props only for internal state:**
    - A `renderX` function is justified when the child needs state the parent holds; otherwise `children` already works
5.  **Passthrough props signal a broken boundary:**
    - Props that exist only to travel deeper mean you should be passing the element, not its data

**Incorrect (a flag per screen, conditionals stacking inside):**

```tsx
type Props = {
  title: string;
  showHeader?: boolean;
  showFooter?: boolean;
  isCompact?: boolean;
  hasBorder?: boolean;
  headerAction?: ReactNode;
  renderFooter?: () => ReactNode;
  footerAlign?: 'left' | 'right';
};

export function Card(props: Props) {
  return (
    <div
      className={cn(
        'rounded-lg',
        props.hasBorder && 'border',
        props.isCompact ? 'p-2' : 'p-4',
      )}
    >
      {props.showHeader && (
        <div className="flex items-center justify-between">
          <h3 className="font-semibold">{props.title}</h3>
          {props.headerAction}
        </div>
      )}
      {props.children}
      {props.showFooter && (
        <div
          className={props.footerAlign === 'right' ? 'text-right' : 'text-left'}
        >
          {props.renderFooter?.()}
        </div>
      )}
    </div>
  );
}
```

**Correct (structure assembled at the call site, one job per component):**

```tsx
// Several components in one module, so each type is qualified by its own name
type CardProps = React.ComponentProps<'div'>;

export function Card({ className, ...props }: CardProps) {
  return <div className={cn('rounded-lg border p-4', className)} {...props} />;
}

type CardHeaderProps = React.ComponentProps<'div'>;

export function CardHeader({ className, ...props }: CardHeaderProps) {
  return (
    <div
      className={cn('mb-3 flex items-center justify-between', className)}
      {...props}
    />
  );
}

type CardBodyProps = React.ComponentProps<'div'>;

export function CardBody({ className, ...props }: CardBodyProps) {
  return (
    <div className={cn('text-sm text-muted-foreground', className)} {...props} />
  );
}
```

```tsx
// The screen composes exactly what it needs — no prop was added to support it
<Card className="p-2">
  <CardHeader>
    <h3 className="font-semibold">Q3 summary</h3>
    <Button variant="ghost">Export</Button>
  </CardHeader>
  <CardBody>
    <p>Revenue grew 12% quarter over quarter.</p>
  </CardBody>
</Card>
```

Mutually exclusive props follow the same principle one level down, in the type: the union makes the invalid combination impossible to write rather than something the component has to defend against.

```tsx
// Three alternatives for the same Banner component, not three coexisting declarations

// Bad: three independent booleans describe eight states, five of which are meaningless
type Props = {
  isInfo?: boolean;
  isWarning?: boolean;
  isError?: boolean;
  message: string;
};

// Good: one axis, three valid states, nothing else type-checks
type Props = {
  tone: 'info' | 'warning' | 'error';
  message: string;
};

// Good: when a case carries data the others do not, discriminate on the same axis
type Props =
  | { tone: 'info' | 'warning'; message: string }
  | { tone: 'error'; message: string; onRetry: () => void };
```

Reference: [Passing JSX as children](https://react.dev/learn/passing-props-to-a-component#passing-jsx-as-children)
