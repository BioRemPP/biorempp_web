"""
FAQ Item Component - Composite UI Component.

Creates individual FAQ accordion items with question/answer pairs.

Functions
---------
create_faq_item
    Create single FAQ accordion item

Notes
-----
- Composite component using dbc.AccordionItem
- Supports rich content (HTML, code blocks, lists)
- Consistent styling across all FAQ items
"""

from typing import List, Union

import dash_bootstrap_components as dbc
from dash import html


def create_faq_item(
    question: str,
    answer: Union[str, List, html.Div],
    item_id: str,
    icon: str = "fa-question-circle",
) -> dbc.AccordionItem:
    """
    Create FAQ accordion item.

    Parameters
    ----------
    question : str
        The FAQ question text
    answer : Union[str, List, html.Div]
        Answer content (can be string, list of elements, or html.Div)
    item_id : str
        Unique ID for the accordion item
    icon : str, optional
        FontAwesome icon class, by default "fa-question-circle"

    Returns
    -------
    dbc.AccordionItem
        Styled accordion item with question/answer

    Examples
    --------
    >>> faq = create_faq_item(
    ...     question="What file formats are supported?",
    ...     answer="We support file format with KO annotations.",
    ...     item_id="faq-formats"
    ... )

    >>> # Rich content example
    >>> answer_content = html.Div([
    ...     html.P("Multiple formats supported:"),
    ...     html.Ul([
    ...         html.Li("file (.file, .fa)"),
    ...         html.Li("Plain text (.txt)")
    ...     ])
    ... ])
    >>> faq = create_faq_item(
    ...     question="What file formats?",
    ...     answer=answer_content,
    ...     item_id="faq-formats-detailed"
    ... )

    Notes
    -----
    - Question displays in accordion header with icon
    - Answer revealed on click
    - Supports markdown-style formatting in answers
    - Consistent padding and typography
    """
    # Format answer content
    if isinstance(answer, str):
        answer_content = html.P(answer, className="mb-0")
    elif isinstance(answer, list):
        answer_content = html.Div(answer)
    else:
        answer_content = answer

    # Create title with icon
    title = html.Span([html.I(className=f"fas {icon} me-2 text-success"), question])

    return dbc.AccordionItem(
        children=answer_content, title=title, item_id=item_id, className="faq-item"
    )


def create_code_block(code: str, language: str = "bash") -> html.Div:
    """
    Create formatted code block for FAQ answers.

    Parameters
    ----------
    code : str
        Code snippet to display
    language : str, optional
        Programming language for syntax context, by default "bash"

    Returns
    -------
    html.Div
        Styled code block

    Examples
    --------
    >>> code = create_code_block(">sample1_KO:K00001\\n>sample2_KO:K00002")
    """
    return html.Div(
        [
            html.Pre(
                html.Code(code, className=f"language-{language}"),
                className="bg-light p-3 rounded border",
            )
        ],
        className="my-2",
    )


def create_faq_note(text: str, note_type: str = "info") -> dbc.Alert:
    """
    Create styled note/tip box for FAQ answers.

    Parameters
    ----------
    text : str
        Note text content
    note_type : str, optional
        Type of note: "info", "warning", "success", "danger", by default "info"

    Returns
    -------
    dbc.Alert
        Styled alert box

    Examples
    --------
    >>> note = create_faq_note(
    ...     "Tip: Use CTRL+F to search within this page",
    ...     note_type="info"
    ... )
    """
    icon_map = {
        "info": "fa-info-circle",
        "warning": "fa-exclamation-triangle",
        "success": "fa-check-circle",
        "danger": "fa-times-circle",
    }

    icon_class = icon_map.get(note_type, "fa-info-circle")

    return dbc.Alert(
        [html.I(className=f"fas {icon_class} me-2"), text],
        color=note_type,
        className="mb-2",
    )
