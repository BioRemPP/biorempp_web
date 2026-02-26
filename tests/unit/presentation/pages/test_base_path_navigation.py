"""Tests for base-path aware navigation links in presentation components."""

from __future__ import annotations

from typing import Any

from config.settings import get_settings
from src.presentation.components.base.header_component import create_header
from src.presentation.components.composite.upload_panel import create_upload_panel


def _collect_component_prop(node: Any, prop_name: str) -> list[str]:
    """Collect a property recursively from Dash component trees."""
    values: list[str] = []

    def visit(value: Any) -> None:
        if value is None:
            return
        if isinstance(value, (list, tuple)):
            for item in value:
                visit(item)
            return
        prop_value = getattr(value, prop_name, None)
        if isinstance(prop_value, str):
            values.append(prop_value)
        children = getattr(value, "children", None)
        if children is not None:
            visit(children)

    visit(node)
    return values


def test_header_links_include_base_path_when_configured(monkeypatch):
    """Main navigation links should include configured URL base path."""
    settings = get_settings()
    monkeypatch.setattr(settings, "URL_BASE_PATH", "/biorempp/")

    header = create_header(show_nav=True)
    hrefs = set(_collect_component_prop(header, "href"))

    assert "/biorempp/about" in hrefs
    assert "/biorempp/help/user-guide" in hrefs
    assert "/biorempp/schemas" in hrefs
    assert "/biorempp/regulatory" in hrefs
    assert "/biorempp/methods" in hrefs
    assert "/biorempp/faq" in hrefs
    assert "/biorempp/help/contact" in hrefs


def test_upload_panel_example_link_includes_base_path(monkeypatch):
    """Public example download link should include base path."""
    settings = get_settings()
    monkeypatch.setattr(settings, "URL_BASE_PATH", "/biorempp/")

    panel = create_upload_panel()
    hrefs = set(_collect_component_prop(panel, "href"))

    assert "/biorempp/data/exemple_dataset.txt" in hrefs
