---
title: Environment & Dependency Segregation
impact: MEDIUM
description: Enforces the creation of distinct virtual environments (.venv.development, .venv.production) and split requirement files to isolate build dependencies from runtime logic.
tags: python, virtualenv, dependencies, pip, configuration
---

## Environment & Dependency Segregation

**Impact (MEDIUM):** Strict separation ensures production artifacts remain lightweight and secure by excluding development tools. Using distinct virtual environments prevents accidental "pollution" of the production dependency tree during local testing.

**Guidelines:**

1.  **Dual Virtual Environments:** Do not use a generic `.venv`. Create two explicit environments in the project root:
    - `.venv.development`: For local coding, linting, and testing.
    - `.venv.production`: To simulate the build process and verify clean installs.
2.  **Requirement Files:** Store dependencies in a `requirements/` directory, never in a root `./requirements.txt`.
    - `./requirements/production.txt`: Only libraries required for the application to run.
    - `./requirements/development.txt`: Libraries for type checking (stubs), formatting, and debugging.
3.  **Contextual Installation:** Before installing a package, explicitly decide: "Is this needed for the app logic or for the developer?" Install into the corresponding environment/file.
4.  **Standard Development Stack:** Development requirements must include type stubs for strict typing (e.g., `django-stubs`, `djangorestframework-stubs`).

**Incorrect (Mixed environment & Monolithic file):**

```bash
# Bad: Generic environment
$ python3 -m venv .venv

# Bad: Root file mixing concerns
$ cat ./project/requirements.txt
```

**Correct (Segregated Environments & Files):**

```bash
# 1. Create Production Environment
$ python3 -m venv .venv.production

# 2. Create Development Environment
$ python3 -m venv .venv.development
```

**File Structure:**

```plaintext
./project/
├── .venv.development/
├── .venv.production/
└── requirements/
    ├── development.txt
    └── production.txt
```

**Content Examples:**

```plaintext
# ./requirements/production.txt (example)

django
djangorestframework
gunicorn
psycopg2-binary
```

```plaintext
# ./requirements/development.txt (example)

certifi==2025.8.3
charset-normalizer==3.4.3
django-stubs==5.2.5
django-stubs-ext==5.2.5
djangorestframework-stubs==3.16.3
idna==3.10
requests==2.32.5
types-PyYAML==6.0.12.20250915
types-requests==2.32.4.20250913
typing_extensions==4.15.0
urllib3==2.5.0
```

Reference: [Python venv Documentation](https://docs.python.org/3/library/venv.html)
