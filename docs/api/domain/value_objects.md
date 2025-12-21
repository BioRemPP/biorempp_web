
# Value Objects
Value Objects are **immutable objects** that represent domain concepts without identity. Equality is based on their attributes, not on a unique identifier.

---

## KO (KEGG Orthology)

::: src.domain.value_objects.kegg_orthology.KO
    options:
      show_source: true
      heading_level: 3

---
## SampleId

::: src.domain.value_objects.sample_id.SampleId
    options:
      show_source: true
      heading_level: 3

---
## Pathway

::: src.domain.value_objects.pathway.Pathway
    options:
      show_source: true
      heading_level: 3

---
## Compound

::: src.domain.value_objects.compound.Compound
    options:
      show_source: true
      heading_level: 3

---

## Related Documentation

- [Domain Entities](entities.md) - Business objects with identity
- [Domain Services](services.md) - Business logic operations

---

## Value Object Principles

According to **Domain-Driven Design** (DDD):

1. **Immutability**: Once created, cannot be changed
2. **Equality by Value**: Two value objects are equal if all attributes match
3. **No Identity**: Don't have a unique identifier
4. **Validation**: Business rules enforced at construction time
