# Agent Guidelines

You are acting as a specialized _Django_ developer. Your goal is to generate code that strictly adheres to the project's defined best practices.

## 1. Rule Application Protocol

Before generating any code, you must:

1.  **Consult `rules/_sections.md`** to identify the relevant category.
2.  **Read the specific rule file** to understand the constraints.
3.  **Apply the correct patterns** defined in the rule, ignoring incorrect ones even if they are valid standard _Django_ code.

## 2. Key Enforcements

### Architecture & Config

- **App Structure:** All apps must reside in `apps/` (e.g., `apps/users`). Convert `models.py` and `views.py` into packages with `__init__.py`.
- **Settings:** Never modify `settings.py` directly for environment values; use `development.py` or `production.py`.
- **Dependencies:** Distinguish between `requirements/production.txt` and `requirements/development.txt`.
- **Docker:** Use reverse-domain naming (`com.example.project`) and always use `slim` python images.

### Coding Standards

- **Models:** One model per file. Enforce `db_table` for multi-word models (snake_case). Always translate `verbose_name`.
- **Serializers:** Use conditional imports. Implement `DelegateRepresentationMixin` for write serializers that require read-like responses.
- **Views:** Prefer generic views for CRUD. Use `APIView` with explicit parameter typing (`request: Request`) for custom logic; omit return type annotations when the `return` statement makes the type self-evident.
- **Typing:** Add type hints only when they add real value to the reader — primarily on parameters whose type is not obvious from their name or context. Omit return annotations when the return expression is self-documenting (e.g., `return Response(...)`, `return self.email`). Never annotate dunder methods whose contract is defined by the protocol (e.g., `__str__`, `__repr__`).

## 3. Environment Awareness

- When installing packages, explicitly ask or deduce if it belongs in the production list (runtime) or development list (stubs, linters).
- Be aware of the dual virtual environment setup (`.venv.development` and `.venv.production`).
