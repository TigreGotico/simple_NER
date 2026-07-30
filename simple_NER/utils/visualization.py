"""Entity visualization utilities for simple_NER.

This module provides utilities for visualizing extracted entities
in text with colors, HTML output, and terminal formatting.
"""
from __future__ import annotations

from typing import Any

from simple_NER import Entity


# ANSI color codes for terminal output
COLORS = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
    "white": "\033[97m",
    "reset": "\033[0m",
    "bold": "\033[1m",
}

# Entity type to color mapping
ENTITY_COLORS = {
    "email": "cyan",
    "person": "green",
    "noun": "green",
    "country": "blue",
    "capital city": "blue",
    "city": "blue",
    "location": "blue",
    "relative_date": "yellow",
    "duration": "yellow",
    "written_number": "magenta",
    "keyword": "magenta",
    "energy": "red",
    "length": "red",
    "mass": "red",
    "default": "white",
}


def get_color_for_entity(entity_type: str) -> str:
    """Get color name for entity type.

    Args:
        entity_type: Entity type string.

    Returns:
        Color name.
    """
    type_lower = entity_type.lower()
    for key, color in ENTITY_COLORS.items():
        if key in type_lower:
            return color
    return ENTITY_COLORS["default"]


def visualize_text_terminal(
    text: str,
    entities: list[Entity],
    show_confidence: bool = False,
) -> str:
    """Visualize entities in text using ANSI colors.

    Args:
        text: Original text.
        entities: List of extracted entities.
        show_confidence: Show confidence scores.

    Returns:
        Formatted text with colored entities.

    Example:
        ```python
        from simple_NER.utils.visualization import visualize_text_terminal

        result = visualize_text_terminal(text, entities)
        print(result)
        ```
    """
    if not entities:
        return text

    # Sort entities by start position (reverse for replacement)
    sorted_entities = sorted(
        entities,
        key=lambda e: e.spans[0][0] if e.spans else 0,
        reverse=True,
    )

    result = text

    for entity in sorted_entities:
        if not entity.spans:
            continue

        start, end = entity.spans[0]
        color = get_color_for_entity(entity.entity_type)
        conf_str = f" ({entity.confidence:.1f})" if show_confidence else ""
        replacement = (
            f"{COLORS['bold']}{COLORS[color]}{text[start:end]}"
            f"[{entity.entity_type}{conf_str}]"
            f"{COLORS['reset']}"
        )
        result = result[:start] + replacement + result[end:]

    return result


def visualize_text_html(
    text: str,
    entities: list[Entity],
    show_confidence: bool = False,
) -> str:
    """Visualize entities in text as HTML.

    Args:
        text: Original text.
        entities: List of extracted entities.
        show_confidence: Show confidence scores.

    Returns:
        HTML string with styled entity spans.

    Example:
        ```python
        html = visualize_text_html(text, entities)
        with open("output.html", "w") as f:
            f.write(f"<html><body>{html}</body></html>")
        ```
    """
    # Color mapping for HTML
    html_colors = {
        "email": "#00bcd4",
        "person": "#4caf50",
        "noun": "#4caf50",
        "country": "#2196f3",
        "capital city": "#2196f3",
        "city": "#2196f3",
        "location": "#2196f3",
        "relative_date": "#ffeb3b",
        "duration": "#ffeb3b",
        "written_number": "#e91e63",
        "keyword": "#e91e63",
        "energy": "#f44336",
        "length": "#f44336",
        "mass": "#f44336",
    }

    if not entities:
        return escape_html(text)

    # Sort entities by start position (reverse for replacement)
    sorted_entities = sorted(
        entities,
        key=lambda e: e.spans[0][0] if e.spans else 0,
        reverse=True,
    )

    result = text

    for entity in sorted_entities:
        if not entity.spans:
            continue

        start, end = entity.spans[0]
        color = html_colors.get(
            entity.entity_type.lower(),
            html_colors.get("keyword", "#9e9e9e"),
        )
        conf_str = f" ({entity.confidence:.1f})" if show_confidence else ""
        replacement = (
            f'<span style="background-color: {color}33; '
            f'border-bottom: 2px solid {color}; '
            f'padding: 2px 4px; '
            f'border-radius: 3px;" '
            f'title="{entity.entity_type}{conf_str}">'
            f"{escape_html(text[start:end])}"
            f'</span>'
        )
        result = result[:start] + replacement + result[end:]

    return result


def escape_html(text: str) -> str:
    """Escape HTML special characters.

    Args:
        text: Text to escape.

    Returns:
        Escaped text.
    """
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def visualize_entities_table(entities: list[Entity]) -> str:
    """Create a table visualization of entities.

    Args:
        entities: List of entities.

    Returns:
        Formatted table string.
    """
    if not entities:
        return "No entities found."

    # Table header
    lines = [
        f"{'Value':<30} {'Type':<20} {'Conf':<6} {'Spans':<15}",
        "-" * 75,
    ]

    for entity in entities:
        spans_str = str(entity.spans[0]) if entity.spans else "N/A"
        lines.append(
            f"{entity.value:<30} {entity.entity_type:<20} "
            f"{entity.confidence:<6.2f} {spans_str:<15}"
        )

    return "\n".join(lines)


def visualize_entities_json(
    entities: list[Entity],
    text: str | None = None,
) -> dict[str, Any]:
    """Create a JSON-serializable visualization data structure.

    Args:
        entities: List of entities.
        text: Optional original text.

    Returns:
        Dictionary with visualization data.
    """
    data: dict[str, Any] = {
        "entities": [entity.as_json() for entity in entities],
        "count": len(entities),
        "by_type": {},
    }

    # Group by type
    for entity in entities:
        entity_type = entity.entity_type
        if entity_type not in data["by_type"]:
            data["by_type"][entity_type] = []
        data["by_type"][entity_type].append(entity.as_json())

    if text:
        data["text"] = text

    return data


def print_colored_entities(entities: list[Entity]) -> None:
    """Print entities with colored output.

    Args:
        entities: List of entities to print.
    """
    for entity in entities:
        color = get_color_for_entity(entity.entity_type)
        print(
            f"{COLORS[color]}{entity.value}{COLORS['reset']} "
            f"({COLORS['bold']}{entity.entity_type}{COLORS['reset']}, "
            f"conf: {entity.confidence:.2f})"
        )
