# BioRemPP Web - Test Suite Documentation

> **Comprehensive test coverage for the BioRemPP web application**

*Version: 1.0.0*  
*Test Framework: pytest*

---

##  Test Coverage Summary

| **Layer**      | **Tests** | **Coverage** | **Status** |
| -------------- | --------- | ------------ | ---------- |
| Domain         | 931       | 86%          | ✅ Passing  |
| Application    | 553       | 82%          | ✅ Passing  |
| Infrastructure | 97        | 77%          | ✅ Passing  |
| **Total**      | **1,581** | **83%**      | ✅ Passing  |

---

##  1. Testing Architecture  

The BioRemPP web application follows **Clean Architecture** principles with four distinct layers:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Presentation Layer          ◆ UI (Dash callbacks, layouts)             │
├─────────────────────────────────────────────────────────────────────────┤
│  Application Layer           ◆ Use cases, services, DTOs               │
├─────────────────────────────────────────────────────────────────────────┤
│  Domain Layer                ◆ Business logic, entities                │
├─────────────────────────────────────────────────────────────────────────┤
│  Infrastructure Layer        ◆ External concerns (DB, cache)           │
└─────────────────────────────────────────────────────────────────────────┘
```

The test suite mirrors this architecture, ensuring comprehensive coverage of each layer.

---

##  2. Test Suite Organization

### 2.1 Directory Structure

```
tests/
├── unit/
│   ├── application/           # Application layer tests (553 tests)
│   │   ├── core/              # Core services (114 tests)
│   │   ├── dto/               # Data Transfer Objects (140 tests)
│   │   ├── mappers/           # Data mappers (20 tests)
│   │   ├── plot_services/     # Plot generation services (129 tests)
│   │   └── services/          # Orchestration services (43 tests)
│   │
│   ├── domain/                # Domain layer tests (931 tests)
│   │   ├── plot_strategies/   # Visualization strategies (869 tests)
│   │   │   ├── base/          # Base strategy (35 tests)
│   │   │   └── charts/        # 19 chart strategies (834 tests)
│   │   ├── test_dataset.py    # Dataset entity (16 tests)
│   │   ├── test_sample.py     # Sample entity (16 tests)
│   │   └── value_objects/     # Value objects (39 tests)
│   │
│   └── infrastructure/        # Infrastructure layer tests (97 tests)
│       ├── cache/             # Caching mechanisms (37 tests)
│       ├── config/            # Configuration management (31 tests)
│       └── persistence/       # Data repositories (29 tests)
│
├── conftest.py                # Pytest fixtures and configuration
└── README.md                   # This documentation file
```

---

##  3. Testing Patterns & Best Practices

### 3.1 Domain Layer Testing

**Focus**: Business logic, entity invariants, value object validation

**Key Patterns**:
- **Entity Testing**: Validate business rules and state transitions
- **Value Object Testing**: Ensure immutability and validation
- **Strategy Pattern Testing**: Verify plot generation algorithms


**Coverage Goals**:
- ✅ All entities have validation tests
- ✅ All value objects have immutability tests
- ✅ All business rules are tested
- ✅ Edge cases and error conditions covered

---

### 3.2 Application Layer Testing

**Focus**: Use case orchestration, service coordination, DTO transformations

**Key Patterns**:
- **Service Testing**: Mock external dependencies, verify orchestration logic
- **DTO Testing**: Validate data transformation and serialization
- **Mapper Testing**: Ensure correct entity ↔ DTO conversions

**Coverage Goals**:
- ✅ All use cases have happy path tests
- ✅ All error scenarios are tested
- ✅ All DTOs have serialization tests
- ✅ All mappers have bidirectional conversion tests

---

### 3.3 Infrastructure Layer Testing

**Focus**: External integrations, caching, persistence, configuration

**Key Patterns**:
- **Repository Testing**: Mock database/file access, verify queries
- **Cache Testing**: Verify cache hit/miss scenarios, eviction policies
- **Config Testing**: Validate configuration loading and validation


**Coverage Goals**:
- ✅ All repositories have CRUD operation tests
- ✅ All cache mechanisms have eviction tests
- ✅ All configuration loaders have validation tests

---

### 3.4 Plot Strategy Testing

**Focus**: Visualization generation, data transformation, Plotly figure creation

**Key Patterns**:
- **Strategy Pattern Testing**: Each chart type has dedicated test suite
- **Data Transformation Testing**: Verify data preparation for plots
- **Figure Validation Testing**: Ensure Plotly figures are well-formed


**Coverage Goals**:
- ✅ All 19 chart strategies have generation tests
- ✅ All strategies have empty data handling tests
- ✅ All strategies have invalid input tests
- ✅ All strategies have figure validation tests

---

##  4. Test Execution

### 4.1 Running Tests

**Run all tests**:
```bash
pytest
```

**Run specific layer**:
```bash
pytest tests/unit/domain/          # Domain layer only
pytest tests/unit/application/     # Application layer only
pytest tests/unit/infrastructure/  # Infrastructure layer only
```

**Run specific test file**:
```bash
pytest tests/unit/domain/test_sample.py
```

**Run with coverage report**:
```bash
pytest --cov=. --cov-report=html
```

**Run with verbose output**:
```bash
pytest -v
```

**Run specific test by name**:
```bash
pytest -k "test_sample_creation"
```
---

