---
title: Build Email Pieces for Email Clients
impact: HIGH
description: Signatures and newsletters use tables with inline styles, hex colors, hosted PNG logos and a font fallback, because email clients ignore stylesheets and SVG
tags: email, signature, newsletter, html
---

## Build Email Pieces for Email Clients

**Impact (HIGH):** A signature built with the component CSS renders broken in _Outlook_ and _Gmail_.

**Guidelines:**

1. Markup as `<table role="presentation">` with inline styles and hex values of the palette tones
2. Logo as a hosted PNG at least 2× the displayed size (`--width_480` shown at 120px; symbol `--width_112` shown at 56px)
3. Font stack `<Family>, Arial, sans-serif`; check the piece in _Arial_, which most clients show; buttons as table cells with background
4. Signature: symbol, vertical separator, name, role, legal name, contact and slogan; no quotes, banners or inactive networks
5. Newsletter: 600px fluid, one topic, one button, optional image with `alt`, footer with legal name, tax ID, address and unsubscribe link
6. Check every piece in _Gmail_ and _Outlook_ dark mode (see `found-single-light-theme`)

**Incorrect (component CSS in an email):**

```html
<link rel="stylesheet" href="bundle.css" /><img
  src="logo__symbol--gradient.svg"
/>
```

**Correct (email-safe markup):**

```html
<table role="presentation" cellpadding="0" cellspacing="0">
  <tr>
    <td>
      <img
        src="https://askit.com.co/firma/logo__symbol--gradient--width_112.png"
        width="56"
        height="56"
        alt="ASKIT"
      />
    </td>
    <td style="font-family:Lexend,Arial,sans-serif;color:#0a0a0a">…</td>
  </tr>
</table>
```

Reference: [Can I email](https://www.caniemail.com/)
