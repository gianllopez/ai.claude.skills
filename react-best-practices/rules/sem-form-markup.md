---
title: Form Markup & Field Association
impact: HIGH
description: Requires every form to go through react-hook-form and the Form components, with grouped fields, specific input types, and real submission instead of hand-held field state.
tags: semantics, forms, jsx
---

## Form Markup & Field Association

**Impact (HIGH):** A form built from `div`s and a click handler loses submission on _Enter_, autofill, and the correct mobile keyboard. These are behaviors users expect and nobody reimplements completely. The same holds one level up: a component that keeps its own field state and its own error strings rebuilds what the form library already does, and the two copies drift — the label stops matching its control, the message stops matching the field.

**Guidelines:**

1.  **Every form goes through `react-hook-form`:**
    - The form instance owns every value; no component keeps field state of its own
    - Reading values back out of the _DOM_ by hand — `FormData`, a ref per input, `event.target.elements` — means the form was built twice
2.  **Fields are declared through the Form components:**
    - `FormField` / `FormItem` / `FormLabel` / `FormControl` / `FormMessage` wire the label to the control and the message to the field; writing `htmlFor` and an id by hand duplicates what they already do
    - A control rendered outside `FormControl` loses that wiring, and nothing reports it
    - The placeholder stays an example value (`jane@acme.co`) — the label is the label
3.  **A group of controls carries a label of its own:**
    - Related controls that only make sense together — radio groups, address blocks, date ranges — get one label for the group and one per option
    - The `Form` components express that with a group-level `FormLabel` and a nested `FormItem` per option; they emit no `fieldset` / `legend`, and wrapping one around them only declares the grouping twice
    - What review checks is that the group is named at all — an option list whose only labels are its options is a group nobody named
4.  **Type and name:**
    - Use the specific `type` (`email`, `tel`, `url`, `number`, `date`, `search`); it selects the mobile keyboard and parses the value
    - The `name` on `FormField` is what identifies the value — keep it identical to the key the mutation expects, so no mapping layer appears between them
5.  **Validation speaks once, and it is the form library:**
    - The `form` carries `noValidate`, so the browser's own checking never interrupts and every message the user reads comes from `FormMessage`
    - Constraints live on `FormField`'s `rules` and nowhere else — alongside `noValidate` a `required` attribute does nothing, and a component holding its own error string is a second source of truth
    - The `type` still earns its place through the mobile keyboard and the parsing; with native checking off it is no longer a validator, so it never competes for the message
6.  **Submission stays a real submission:**
    - A `form` element with `button type="submit"`, wrapping `handleSubmit`; never an action bound only to a button's `onClick`
    - The mutation hook is what the submit handler calls, not what replaces the form

**Incorrect (hand-held field state, no form element, no association, parallel error string):**

```tsx
export function SignupForm() {
  // Bad: field state by hand — the form library already owns this
  const [email, setEmail] = useState('');
  const [plan, setPlan] = useState('basic');
  const [emailError, setEmailError] = useState('');

  // Bad: not a form, so Enter does nothing and autofill has no context
  return (
    <div className="space-y-4">
      {/* Bad: placeholder used as the field name, no label, no association */}
      <input
        type="text"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        className="w-full rounded-md border px-3 py-2"
      />
      {/* Bad: an error string tracked in parallel to the field it describes */}
      <p className="text-sm text-destructive">{emailError}</p>
      {/* Bad: the options are labelled, the group they belong to is not */}
      <div className="flex gap-4">
        <input type="radio" value="basic" onChange={() => setPlan('basic')} />{' '}
        Basic
        <input type="radio" value="pro" onChange={() => setPlan('pro')} /> Pro
      </div>
      <button
        onClick={submitForm}
        className="rounded-md bg-primary px-4 py-2"
      >
        Continue
      </button>
    </div>
  );
}
```

**Correct (the form owns the values, the Form components own the wiring and the grouping):**

```tsx
type FormValues = {
  email: string;
  phone: string;
  plan: 'basic' | 'pro';
};

export function SignupForm() {
  const createAccount = useCreateAccount();
  const form = useForm<FormValues>({
    defaultValues: {
      email: '',
      phone: '',
      plan: 'basic',
    },
  });

  const handleSubmit = (values: FormValues) => {
    createAccount.mutate(values);
  };

  return (
    <Form {...form}>
      {/* Good: noValidate hands every message to the form library */}
      <form
        noValidate
        onSubmit={form.handleSubmit(handleSubmit)}
        className="space-y-4"
      >
        <FormField
          control={form.control}
          name="email"
          rules={{ required: 'Email is required' }}
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input type="email" placeholder="jane@acme.co" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="phone"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Phone</FormLabel>
              <FormControl>
                <Input type="tel" {...field} />
              </FormControl>
            </FormItem>
          )}
        />
        {/* Good: the group is named by its own FormLabel, each option by its own */}
        <FormField
          control={form.control}
          name="plan"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Plan</FormLabel>
              <FormControl>
                <RadioGroup
                  onValueChange={field.onChange}
                  defaultValue={field.value}
                  className="flex gap-4"
                >
                  <FormItem className="flex items-center gap-2">
                    <FormControl>
                      <RadioGroupItem value="basic" />
                    </FormControl>
                    <FormLabel className="font-normal">Basic</FormLabel>
                  </FormItem>
                  <FormItem className="flex items-center gap-2">
                    <FormControl>
                      <RadioGroupItem value="pro" />
                    </FormControl>
                    <FormLabel className="font-normal">Pro</FormLabel>
                  </FormItem>
                </RadioGroup>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" disabled={createAccount.isPending}>
          Continue
        </Button>
      </form>
    </Form>
  );
}
```

Reference: [shadcn/ui Form](https://ui.shadcn.com/docs/components/form)
