"""Unit tests for analysis suggestions link targets."""

from src.presentation.components.composite.analysis_suggestions.guiding_questions import (
    create_guiding_questions_content,
    create_uc_link,
)
from src.presentation.components.composite.analysis_suggestions.basic_exploration import (
    create_basic_exploration_content,
)
from src.presentation.components.composite.analysis_suggestions.data_type_exploration import (
    create_data_type_exploration_content,
)


def test_create_uc_link_defaults_to_compact_view_label() -> None:
    component = create_uc_link("uc-2-1")
    children = getattr(component, "children", [])
    assert isinstance(children, list)
    assert "View UC-2-1" in str(children[1])
    assert getattr(component, "href", None) == "#uc-2-1-card"


def test_create_uc_link_keeps_explicit_label_when_provided() -> None:
    component = create_uc_link("uc-2-1", "Custom Label")
    children = getattr(component, "children", [])
    assert isinstance(children, list)
    assert "Custom Label" in str(children[1])


def test_guiding_questions_uses_compact_uc_labels() -> None:
    content = create_guiding_questions_content()
    serialized = str(content)
    assert "View UC-2-1" in serialized
    assert "Gene Counts Across Samples" not in serialized
    assert "Related UCs" not in serialized
    assert "Relevant Use Cases (" in serialized


def test_basic_exploration_uses_compact_uc_labels() -> None:
    content = create_basic_exploration_content()
    serialized = str(content)
    assert "View UC-2-1" in serialized
    assert "Pathway Profiling by Sample" not in serialized
    assert "Relevant Use Cases (" in serialized


def test_data_type_exploration_uses_compact_uc_labels() -> None:
    content = create_data_type_exploration_content()
    serialized = str(content)
    assert "View UC-1-1" in serialized
    assert "Intersections across BioRemPP, HADEG, and KEGG" not in serialized
    assert "13 use cases" not in serialized
    assert "Relevant Use Cases (" in serialized
