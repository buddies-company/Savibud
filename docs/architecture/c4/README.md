# C4 Architecture Documentation

This directory contains C4 model diagrams documenting the Savibud system architecture.

## C4 Model Overview

The C4 model provides a hierarchical way to document software architecture:

1. **Context** - System in its environment
2. **Container** - High-level technology choices
3. **Component** - Components within containers
4. **Code** - Implementation details

## Diagrams

### [Context Diagram](context.md)
Shows Savibud in relation to users and external systems (Powens API, Database).

### [Container Diagram](container.md)
Details the technology stack and container interactions within Savibud.

### [Component Diagram](component.md)
Illustrates key components and their relationships within each container.

### [Code Diagram](code.md)
Shows important classes and design patterns at the implementation level.

## Reading Guide

- Start with **Context** to understand the system scope
- Move to **Container** for technology overview
- Use **Component** for detailed interactions
- Refer to **Code** for implementation specifics

## Architecture Principles

- **Clean Architecture**: Dependency inversion between layers
- **Separation of Concerns**: Clear boundaries between components
- **Test-Driven Development**: Comprehensive test coverage
- **Domain-Driven Design**: Business logic at the core

## Tools Used

- **Diagrams**: Mermaid.js for visual representation
- **Documentation**: Markdown for maintainable docs
- **Version Control**: Git for change tracking

## Maintenance

- Update diagrams when architecture changes
- Keep diagrams consistent across levels
- Use consistent styling and notation
- Review during design and code reviews