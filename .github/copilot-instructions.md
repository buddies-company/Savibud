Always follow Clean Architecture and TDD.


Ensure all Python imports respect Hexagonal Architecture:

- Core domain (`entities`, `use_cases`) must **never** import from adapters or drivers.
- Adapters may import from the core domain (`entities`, `use_cases`), but **not** from drivers.
- Drivers may import from adapters and the core domain, but the core domain must **never** depend on them.
- No circular dependencies between layers.
- Imports should always point inward (toward the core), never outward.

When writing commit messages, follow the Conventional Commits specification: