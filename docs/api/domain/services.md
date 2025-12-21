
# Domain Services
Domain Services encapsulate **business logic** that doesn't naturally fit within entities or value objects. They orchestrate complex operations across multiple domain objects.

---
## MergeService

::: src.domain.services.merge_service.MergeService
    options:
      show_source: true
      heading_level: 3

---
## ValidationService

::: src.domain.services.validation_service.ValidationService
    options:
      show_source: true
      heading_level: 3

---

## Related Documentation

- [Domain Entities](entities.md) - Business objects

---

## Domain Service Patterns

### When to Use Domain Services

Use domain services when:

1. **Multi-Entity Operations**: Logic spans multiple aggregates
2. **Complex Business Rules**: Too complex for a single entity
3. **External Dependencies**: Requires external data or calculations
4. **Stateless Operations**: No state to maintain

