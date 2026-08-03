---
title: Effect Discipline
impact: CRITICAL
description: Restricts useEffect to synchronizing with external systems and forbids effects that respond to events, derive state, or fetch on mount.
tags: state, hooks, effects
---

## Effect Discipline

**Impact (CRITICAL):** `useEffect` is an escape hatch for synchronizing with systems outside _React_ — the _DOM_, a subscription, a timer, a third-party _SDK_. Used for anything else it produces the defects that dominate _React_ review: a second render pass with a visible flash, cascades of effects firing in an order nobody controls, stale closures reading last render's values, and infinite loops when a dependency is recreated every render. Most effects in a codebase should not exist.

**Guidelines:**

1.  **What an effect is actually for:**
    - Subscribing to something outside _React_ that offers no hook of its own — an `EventTarget`, a socket, a browser _API_ — with a cleanup that unsubscribes
    - Imperatively driving a non-_React_ widget (a map, a chart, a media element)
    - A store that already exposes a hook is not one of these: it is read through its selector, never through an effect
    - Nothing else qualifies by default
2.  **What belongs in an event handler:**
    - Anything that happens _because the user did something_ — sending the request, showing the toast, navigating
    - An effect that watches a state flag to detect that an event happened is an event handler written backwards
3.  **What belongs in render:**
    - Any value computable from props or state (see the derived-values rule)
4.  **Dependencies are not negotiable:**
    - Never silence the linter with an incomplete array; an omitted dependency is a stale closure waiting for a bug report
    - If a complete array causes a loop, the fix is to move the value out of the effect — into a handler, a ref, or a reducer — not to trim the array
5.  **Cleanup is mandatory for anything ongoing:**
    - Subscriptions, timers, and in-flight requests are cancelled in the cleanup, which also runs between re-renders and on _StrictMode_'s double invocation
6.  **Do not fetch on mount:**
    - Component-level data belongs to the query layer, never to an effect (see the query-layer rule)
    - An effect that fetches also has to reimplement caching, cancellation, retries, and an error branch — and it usually reimplements none of them

**Incorrect (fetch on mount, effect deriving state, effect acting as an event handler, trimmed dependencies):**

```tsx
type Props = {
  cart: Cart;
  onPurchased: () => void;
};

export function CheckoutPanel({ cart, onPurchased }: Props) {
  const [status, setStatus] = useState<'idle' | 'submitting' | 'done'>('idle');
  const [total, setTotal] = useState(0);
  const [coupons, setCoupons] = useState<Coupon[]>([]);

  // Bad: fetching on mount — no cache, no cancellation, no error branch
  useEffect(() => {
    fetch('/api/coupons')
      .then((r) => r.json())
      .then(setCoupons);
  }, []);

  // Bad: derived value stored in state — renders twice and flashes 0 on the first pass
  useEffect(() => {
    setTotal(cart.items.reduce((sum, i) => sum + i.price * i.quantity, 0));
  }, [cart]);

  // Bad: an event handler written backwards — it reacts to state instead of to the click
  useEffect(() => {
    if (status === 'done') {
      onPurchased();
      toast.success('Order placed');
    }
    // Bad: onPurchased omitted to stop the loop, so it is now a stale closure
  }, [status]);

  return (
    <button type="button" onClick={() => setStatus('submitting')}>
      Pay {total}
    </button>
  );
}
```

**Correct (the query layer loads, the mutation tracks its own pending state, the handler owns the consequences):**

```tsx
type Props = {
  cart: Cart;
  onPurchased: () => void;
};

export function CheckoutPanel({ cart, onPurchased }: Props) {
  const coupons = useCoupons();
  const purchase = usePurchase();

  // Good: derived during render, so it can never disagree with the cart
  const total = cart.items.reduce((sum, i) => sum + i.price * i.quantity, 0);

  // Good: what happens because of the click lives in the click
  const handlePay = () => {
    purchase.mutate(cart, {
      onSuccess: () => {
        onPurchased();
        toast.success('Order placed');
      },
    });
  };

  return (
    <>
      <CouponPicker coupons={coupons} />
      <Button type="button" onClick={handlePay} disabled={purchase.isPending}>
        Pay {total}
      </Button>
    </>
  );
}
```

```tsx
// Good: the effect that survives review — an external system with no hook of its
// own, complete deps, real cleanup
useEffect(() => {
  const socket = connectToRoom(roomId);
  socket.on('message', onMessage);

  return () => socket.close();
}, [roomId, onMessage]);
```

Reference: [You Might Not Need an Effect](https://react.dev/learn/you-might-not-need-an-effect)
