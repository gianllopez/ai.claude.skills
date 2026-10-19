---
title: Register Every Asset and Leave No Orphans
impact: HIGH
description: Every stored file is registered in the index and documented in its group file, replacements are swapped safely, and nothing unregistered or unused remains
tags: governance, assets, registry, cleanup
---

## Register Every Asset and Leave No Orphans

**Impact (HIGH):** Orphan files and broken references accumulate silently and make the system look larger and less trustworthy than it is.

**Guidelines:**

1. The index (`design-system.json`) holds one record per stored file (blob); each asset group also has a `README.md` listing every file with its use
2. To replace a file: upload the new one, update the index record (blob id and size), publish, verify, and only then delete the old blob
3. After any removal, search the whole system for references to the old name (except the changelog) and update or remove every reference found
4. The number of stored blobs must equal the number of index records
5. A file no component or piece uses is removed, as a major version (see `gov-versioning`), except the logo variant set that `brand-logo-variants` requires for derived designs

**Incorrect (delete first, update later):**

```text
delete blob 3710751f…  →  index still points to it  →  print file broken until the next publish
```

**Correct (safe swap):**

```text
upload print__folder--229x305.pdf → blob 81f1a4bd… (44173 bytes)
update design-system.json print record → publish → read back and verify → delete old blob ab8feac7…
```

Reference: [ASKIT design system](https://claude.ai/artifact/9eCaJesYHHVPdcU3Unoq1W)
