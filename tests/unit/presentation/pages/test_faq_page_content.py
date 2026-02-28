"""Unit tests for FAQ content alignment with Job ID/Resume feature updates."""

from typing import Any

from src.presentation.pages.faq_page import create_faq_page


def _collect_text(node: Any) -> str:
    """Collect textual children recursively into a single string."""
    chunks: list[str] = []

    def visit(value: Any) -> None:
        if value is None:
            return
        if isinstance(value, (str, int, float)):
            chunks.append(str(value))
            return
        if isinstance(value, (list, tuple)):
            for item in value:
                visit(item)
            return
        children = getattr(value, "children", None)
        if children is not None:
            visit(children)
        title = getattr(value, "title", None)
        if title is not None:
            visit(title)

    visit(node)
    return " ".join(chunks)


def _collect_component_ids(node: Any) -> set[str]:
    """Collect string IDs/item_ids recursively from Dash component tree."""
    ids: set[str] = set()

    def visit(value: Any) -> None:
        if value is None:
            return
        if isinstance(value, (list, tuple)):
            for item in value:
                visit(item)
            return
        component_id = getattr(value, "id", None)
        if isinstance(component_id, str):
            ids.add(component_id)
        item_id = getattr(value, "item_id", None)
        if isinstance(item_id, str):
            ids.add(item_id)
        children = getattr(value, "children", None)
        if children is not None:
            visit(children)

    visit(node)
    return ids


def test_faq_includes_job_id_resume_copy_guidance():
    """FAQ should include Job ID resume and copy guidance."""
    layout = create_faq_page()
    content = _collect_text(layout)
    component_ids = _collect_component_ids(layout)

    assert "same browser profile" in content
    assert "without reprocessing" in content
    assert "copy icon" in content
    assert "What is the Job ID generated after processing?" in content
    assert "Where can I find and copy my Job ID?" in content
    assert "Why does Resume by Job ID fail?" in content
    assert "faq-job-id-generated" in component_ids
    assert "faq-job-id-copy" in component_ids
    assert "faq-resume-job-id-fails" in component_ids


def test_faq_removes_legacy_resume_and_citation_wording():
    """FAQ should not expose outdated session/redis/citation wording."""
    layout = create_faq_page()
    content = _collect_text(layout)

    assert "Browser closed: Immediate deletion" not in content
    assert "cached in Redis" not in content
    assert "How do I cite BioRemPP before DOI assignment?" not in content
    assert "How do I cite BioRemPP using current templates?" in content
