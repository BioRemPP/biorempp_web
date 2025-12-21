# Visão Geral do Pacote

::: src.presentation.callbacks.module_callbacks
  :docstring:
  :show-root-toc: false
  :show-source: false
  :heading-level: 2
:::

# Module Callbacks
Module callbacks orchestrate analysis workflows for each of the 8 BioRemPP modules, managing use case-specific interactions and visualizations.

---

## Module Orchestrators

Each module has a central orchestrator that registers all use case callbacks for that module.

### Module 1: Database Assessment

::: src.presentation.callbacks.module_callbacks.module1_callbacks
    options:
      show_source: true
      members:
        - register_module1_callbacks
      heading_level: 4

---

### Module 2: Functional Analysis

::: src.presentation.callbacks.module_callbacks.module2_callbacks
    options:
      show_source: true
      members:
        - register_module2_callbacks
      heading_level: 4

---

### Module 3: Pathway Analysis

::: src.presentation.callbacks.module_callbacks.module3_callbacks
    options:
      show_source: true
      members:
        - register_module3_callbacks
      heading_level: 4

---

### Module 4: Toxicity Assessment

::: src.presentation.callbacks.module_callbacks.module4_callbacks
    options:
      show_source: true
      members:
        - register_module4_callbacks
      heading_level: 4

---

### Module 5: Gene Interactions

::: src.presentation.callbacks.module_callbacks.module5_callbacks
    options:
      show_source: true
      members:
        - register_module5_callbacks
      heading_level: 4

---

### Module 6: Comparative Analysis

::: src.presentation.callbacks.module_callbacks.module6_callbacks
    options:
      show_source: true
      members:
        - register_module6_callbacks
      heading_level: 4

---

### Module 7: Statistical Analysis

::: src.presentation.callbacks.module_callbacks.module7_callbacks
    options:
      show_source: true
      members:
        - register_module7_callbacks
      heading_level: 4

---

### Module 8: Export & Reporting

::: src.presentation.callbacks.module_callbacks.module8_callbacks
    options:
      show_source: true
      members:
        - register_module8_callbacks
      heading_level: 4

---

## Related Documentation

- [Core Callbacks](core_callbacks.md) - Upload, processing, navigation
- [Application Services](../application/services.md) - Service layer
