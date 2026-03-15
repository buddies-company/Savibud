# ADR 0001: Choosing FastAPI and UV

**Status**: Accepted

**Context**: We need a high-performance backend for Savibud that handles bank API calls. We also need a modern package manager to reduce Docker build times.

**Decision**: We will use FastAPI for its native async support and uv for dependency management.

**Consequences**:
- :heavy_plus_sign: Blazing fast Docker builds (Multi-stage).
- :heavy_plus_sign: Better type safety with Pydantic.
- :heavy_minus_sign: Team must learn the uv CLI and async/await patterns.
