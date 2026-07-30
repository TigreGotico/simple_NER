"""Unit tests for visualization utilities."""

from simple_NER import Entity
from simple_NER.utils.visualization import (
    COLORS,
    ENTITY_COLORS,
    get_color_for_entity,
    print_colored_entities,
    visualize_entities_json,
    visualize_entities_table,
    visualize_text_html,
    visualize_text_terminal,
)


# ---------------------------------------------------------------------------
# Color Utility Tests
# ---------------------------------------------------------------------------

class TestColorUtilities:
    """Tests for color utility functions."""

    def test_get_color_for_entity_email(self):
        """Test color for email entity type."""
        color = get_color_for_entity("email")
        assert color == "cyan"

    def test_get_color_for_entity_person(self):
        """Test color for person entity type."""
        color = get_color_for_entity("person")
        assert color == "green"

    def test_get_color_for_entity_location(self):
        """Test color for location entity type."""
        color = get_color_for_entity("Country")
        assert color == "blue"

    def test_get_color_for_entity_datetime(self):
        """Test color for datetime entity type."""
        color = get_color_for_entity("relative_date")
        assert color == "yellow"

    def test_get_color_for_entity_default(self):
        """Test default color for unknown entity type."""
        color = get_color_for_entity("unknown_type_xyz")
        assert color == ENTITY_COLORS["default"]

    def test_get_color_case_insensitive(self):
        """Test that color lookup is case insensitive."""
        color1 = get_color_for_entity("EMAIL")
        color2 = get_color_for_entity("email")
        color3 = get_color_for_entity("EmAiL")
        assert color1 == color2 == color3


# ---------------------------------------------------------------------------
# Terminal Visualization Tests
# ---------------------------------------------------------------------------

class TestTerminalVisualization:
    """Tests for terminal visualization."""

    def test_visualize_text_no_entities(self):
        """Test visualization with no entities returns original text."""
        text = "No entities here"
        result = visualize_text_terminal(text, [])
        assert result == text

    def test_visualize_text_single_entity(self):
        """Test visualization with single entity."""
        text = "Contact john@example.com"
        entity = Entity(
            "john@example.com",
            "email",
            source_text=text,
        )
        result = visualize_text_terminal(text, [entity])

        # Should contain ANSI color codes
        assert "\033[" in result
        # Should contain entity value
        assert "john@example.com" in result

    def test_visualize_text_with_confidence(self):
        """Test visualization showing confidence scores."""
        text = "Test"
        entity = Entity("Test", "test", source_text=text, confidence=0.95)
        result = visualize_text_terminal(text, [entity], show_confidence=True)

        # Should show confidence
        assert "0.9" in result or "conf" in result.lower()

    def test_visualize_text_multiple_entities(self):
        """Test visualization with multiple entities."""
        text = "John at john@example.com"
        entities = [
            Entity("John", "person", source_text=text),
            Entity("john@example.com", "email", source_text=text),
        ]
        result = visualize_text_terminal(text, entities)

        # Should contain both entities
        assert "John" in result
        assert "john@example.com" in result


# ---------------------------------------------------------------------------
# HTML Visualization Tests
# ---------------------------------------------------------------------------

class TestHTMLVisualization:
    """Tests for HTML visualization."""

    def test_visualize_html_no_entities(self):
        """Test HTML visualization with no entities."""
        text = "No entities"
        result = visualize_text_html(text, [])
        # Should escape HTML
        assert "No entities" in result

    def test_visualize_html_single_entity(self):
        """Test HTML visualization with single entity."""
        text = "Contact test@example.com"
        entity = Entity("test@example.com", "email", source_text=text)
        result = visualize_text_html(text, [entity])

        # Should contain HTML span tags
        assert "<span" in result
        assert "</span>" in result
        # Should contain inline styles
        assert "style=" in result
        assert "background-color" in result

    def test_visualize_html_escapes_special_chars(self):
        """Test that HTML visualization escapes special characters."""
        text = "Test <script>alert('xss')</script>"
        result = visualize_text_html(text, [])

        # Should escape HTML
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_visualize_html_multiple_entities(self):
        """Test HTML visualization with multiple entities."""
        text = "John at john@example.com"
        entities = [
            Entity("John", "person", source_text=text),
            Entity("john@example.com", "email", source_text=text),
        ]
        result = visualize_text_html(text, entities)

        # Should have multiple spans
        assert result.count("<span") >= 2


# ---------------------------------------------------------------------------
# Table Visualization Tests
# ---------------------------------------------------------------------------

class TestTableVisualization:
    """Tests for table visualization."""

    def test_visualize_table_no_entities(self):
        """Test table visualization with no entities."""
        result = visualize_entities_table([])
        assert "No entities found" in result

    def test_visualize_table_single_entity(self):
        """Test table visualization with single entity."""
        entity = Entity("test", "test_type", confidence=0.95)
        result = visualize_entities_table([entity])

        # Should have header
        assert "Value" in result
        assert "Type" in result
        assert "Conf" in result
        # Should have entity data
        assert "test" in result
        assert "test_type" in result

    def test_visualize_table_multiple_entities(self):
        """Test table visualization with multiple entities."""
        entities = [
            Entity("value1", "type1", confidence=0.9),
            Entity("value2", "type2", confidence=0.8),
        ]
        result = visualize_entities_table(entities)

        # Should have separator line
        assert "---" in result
        # Should have both entities
        assert "value1" in result
        assert "value2" in result


# ---------------------------------------------------------------------------
# JSON Visualization Tests
# ---------------------------------------------------------------------------

class TestJSONVisualization:
    """Tests for JSON visualization."""

    def test_visualize_json_structure(self):
        """Test JSON visualization structure."""
        entity = Entity("test", "test_type", confidence=0.9)
        result = visualize_entities_json([entity], text="test text")

        assert "entities" in result
        assert "count" in result
        assert "by_type" in result
        assert "text" in result
        assert result["count"] == 1
        assert result["text"] == "test text"

    def test_visualize_json_grouping_by_type(self):
        """Test that JSON visualization groups by type."""
        entities = [
            Entity("test1", "type1", confidence=0.9),
            Entity("test2", "type1", confidence=0.8),
            Entity("test3", "type2", confidence=0.7),
        ]
        result = visualize_entities_json(entities)

        assert "type1" in result["by_type"]
        assert "type2" in result["by_type"]
        assert len(result["by_type"]["type1"]) == 2
        assert len(result["by_type"]["type2"]) == 1

    def test_visualize_json_without_text(self):
        """Test JSON visualization without text parameter."""
        entity = Entity("test", "test_type")
        result = visualize_entities_json([entity])

        assert "entities" in result
        assert "text" not in result


# ---------------------------------------------------------------------------
# Print Colored Entities Tests
# ---------------------------------------------------------------------------

class TestPrintColoredEntities:
    """Tests for print_colored_entities function."""

    def test_print_colored_entities(self, capsys):
        """Test that print_colored_entities outputs to stdout."""
        entity = Entity("test", "test_type", confidence=0.95)
        print_colored_entities([entity])

        captured = capsys.readouterr()
        output = captured.out

        # Should contain entity value
        assert "test" in output
        # Should contain entity type
        assert "test_type" in output
        # Should contain confidence
        assert "0.95" in output or "conf" in output.lower()

    def test_print_colored_entities_multiple(self, capsys):
        """Test printing multiple colored entities."""
        entities = [
            Entity("test1", "type1"),
            Entity("test2", "type2"),
        ]
        print_colored_entities(entities)

        captured = capsys.readouterr()
        output = captured.out

        assert "test1" in output
        assert "test2" in output

    def test_print_colored_entities_empty(self, capsys):
        """Test printing empty list of entities."""
        print_colored_entities([])

        captured = capsys.readouterr()
        # Should not raise error, may print nothing
        assert captured.out == "" or captured.out is not None


# ---------------------------------------------------------------------------
# Integration Tests
# ---------------------------------------------------------------------------

class TestVisualizationIntegration:
    """Integration tests for visualization utilities."""

    def test_full_visualization_workflow(self, capsys):
        """Test complete visualization workflow."""
        from simple_NER.annotators.email_ner import EmailAnnotator

        # Extract entities
        ner = EmailAnnotator()
        text = "Contact test@example.com"
        entities = list(ner.extract_entities(text))

        # Visualize in different formats
        terminal = visualize_text_terminal(text, entities)
        html = visualize_text_html(text, entities)
        table = visualize_entities_table(entities)
        json_data = visualize_entities_json(entities, text=text)

        # Verify all formats work
        assert terminal is not None
        assert html is not None
        assert table is not None
        assert json_data is not None
        assert json_data["count"] == 1

        # Print colored
        print_colored_entities(entities)
        captured = capsys.readouterr()
        assert "example.com" in captured.out
