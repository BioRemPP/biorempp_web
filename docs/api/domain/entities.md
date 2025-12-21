
# Domain Entities
Domain entities are **business objects with unique identity**. They are mutable and equality is determined by their ID, not their attributes.

---

## Sample Entity

::: src.domain.entities.sample.Sample
    options:
      show_source: true
      heading_level: 3

---

## Dataset Entity

::: src.domain.entities.dataset.Dataset
    options:
      show_source: true
      heading_level: 3

---

## MergedData Entity

::: src.domain.entities.merged_data.MergedData
    options:
      show_source: true
      heading_level: 3

---

## Analysis Entity

::: src.domain.entities.analysis.Analysis
    options:
      show_source: true
      heading_level: 3

---

## Related Documentation

- [Value Objects](value_objects.md) - Immutable domain concepts
- [Domain Services](services.md) - Business logic orchestration

---