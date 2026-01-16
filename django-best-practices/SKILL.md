---
name: django-rest-api-best-practices
description: Django and Django REST Framework optimization guidelines. This skill defines the architectural and performance standards for the back-end, focusing on ORM efficiency, serialization strategies, and API security
license: MIT
metadata:
  author: gianllopez
  version: 1.0.0
---

# Django REST API Best Practices

Comprehensive guide for _Django_ and _Django REST Framework_ development. Contains rules prioritized by impact on database performance, response times, and security.

## When to Apply

Reference these guidelines when:

- Designing or modifying _Django_ models and database schemas (_PostgreSQL_).
- Implementing _Django REST Framework_ serializers and data validation logic.
- Developing _API_ views using _Django REST Framework ViewSets_ or _Generic Views_.
- Optimizing database interactions using the _Django_ ORM (e.g., `select_related`, `prefetch_related`).
- Managing authentication flows, custom permissions, and throttling policies.
- Writing custom _Django_ management commands for administrative tasks.
- Implementing middleware for global request or response processing.
- Handling _Django_ signals and receivers for decoupled event logic.
- Structuring new applications and defining dependencies within the _Django_ project.
- Customizing the _Django_ Admin interface for internal data management.

## Rule Categories by Priority

| Priority | Category                        | Impact      | Prefix  |
| -------- | ------------------------------- | ----------- | ------- |
| 1        | Database Optimization & ORM     | CRITICAL    | `orm-`  |
| 2        | Security & Data Integrity       | CRITICAL    | `sec-`  |
| 3        | API Serialization & Performance | HIGH        | `api-`  |
| 4        | Architecture & Design Patterns  | HIGH        | `arch-` |
| 5        | View Logic & Request Handling   | MEDIUM-HIGH | `view-` |
| 6        | Project Configuration & Tooling | LOW         | `conf-` |

## Quick Reference

### 1. \<name> (\<impact>)

- `<name>` - \<short description>

## How to Use

Read individual rule files for detailed explanations and code examples:

```
rules/*.md
```

Each rule file contains:

- Brief explanation of why it matters
- Incorrect code example with explanation
- Correct code example with explanation
- Additional context and references

## Full Compiled Document

For the complete guide with all rules expanded: `AGENTS.md`
