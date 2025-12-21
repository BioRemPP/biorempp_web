# Mappers

Application Layer - Mappers Package.

This package contains mappers for converting between domain entities and application DTOs.
Mappers are stateless and can be used as functions following Single Responsibility Principle.

## Modules

- **[Sample Mapper](mappers/sample_mapper.md)**: Maps between Sample entities and DataFrames
- **[Merged Data Mapper](mappers/merged_data_mapper.md)**: Maps between MergedData entities and DTOs

## Notes

- Mappers are stateless and can be used as functions
- Follow Single Responsibility Principle
- Enable layer independence (Domain ↔ Application)

## Package Overview

::: src.application.mappers
    options:
      show_root_heading: false
      show_root_toc_entry: false
      show_source: false
      heading_level: 2
      members: false
      show_if_no_docstring: true

---
## SampleMapper

::: src.application.mappers.sample_mapper.SampleMapper
    options:
      show_source: true
      heading_level: 3

---
## MergedDataMapper

::: src.application.mappers.merged_data_mapper.MergedDataMapper
    options:
      show_source: true
      heading_level: 3

---

