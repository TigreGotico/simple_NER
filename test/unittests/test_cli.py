"""Tests for simple_NER/cli.py."""
import io
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

from simple_NER.cli import (
    format_entity_csv,
    format_entity_text,
    format_entity_json,
    list_annotators,
    process_text,
    process_file,
)
from simple_NER import Entity


def _make_entity(value: str = "test@example.com", entity_type: str = "email") -> Entity:
    e = Entity(value, entity_type, source_text=f"send to {value}")
    return e


class TestFormatFunctions(unittest.TestCase):
    def test_format_entity_text(self) -> None:
        e = _make_entity()
        out = format_entity_text(e)
        self.assertIn("test@example.com", out)
        self.assertIn("email", out)

    def test_format_entity_text_with_spans(self) -> None:
        e = _make_entity()
        out = format_entity_text(e, show_spans=True)
        self.assertIn("test@example.com", out)

    def test_format_entity_json(self) -> None:
        e = _make_entity()
        d = format_entity_json(e)
        self.assertIsInstance(d, dict)
        self.assertIn("value", d)

    def test_format_entity_csv(self) -> None:
        e = _make_entity()
        line = format_entity_csv(e)
        self.assertIn("test@example.com", line)
        parts = line.split(",")
        self.assertGreaterEqual(len(parts), 4)

    def test_format_entity_csv_escapes_quotes(self) -> None:
        e = _make_entity(value='say "hello"', entity_type="word")
        line = format_entity_csv(e)
        self.assertIn('""hello""', line)


class TestListAnnotators(unittest.TestCase):
    def test_list_annotators_prints(self) -> None:
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            list_annotators()
        out = buf.getvalue()
        self.assertIn("Available annotators", out)
        self.assertGreater(len(out), 50)


class TestProcessText(unittest.TestCase):
    def test_text_format(self) -> None:
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            process_text("contact a@b.com", ["email"], "keep_all", "text")
        out = buf.getvalue()
        self.assertIn("a@b.com", out)

    def test_json_format(self) -> None:
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            process_text("contact a@b.com", ["email"], "keep_all", "json")
        data = json.loads(buf.getvalue())
        self.assertIn("entities", data)
        self.assertGreater(data["count"], 0)

    def test_csv_format(self) -> None:
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            process_text("contact a@b.com", ["email"], "keep_all", "csv")
        out = buf.getvalue()
        self.assertIn("value,entity_type", out)
        self.assertIn("a@b.com", out)

    def test_no_entities_text(self) -> None:
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            process_text("no entities here", ["email"], "keep_all", "text")
        self.assertIn("No entities", buf.getvalue())

    def test_no_entities_json(self) -> None:
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            process_text("no entities", ["email"], "keep_all", "json")
        data = json.loads(buf.getvalue())
        self.assertEqual(data["entities"], [])

    def test_no_entities_csv(self) -> None:
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            process_text("no entities", ["email"], "keep_all", "csv")
        self.assertIn("value,entity_type", buf.getvalue())

    def test_invalid_annotator_exits(self) -> None:
        with self.assertRaises(SystemExit):
            process_text("hello", ["nonexistent_annotator_xyz"], "keep_all", "text")


class TestProcessFile(unittest.TestCase):
    def _write_temp(self, content: str) -> str:
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8")
        f.write(content)
        f.flush()
        f.close()
        return f.name

    def test_process_file_text_stdout(self) -> None:
        path = self._write_temp("hello a@b.com\nno email\n")
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            process_file(path, None, ["email"], "keep_all", "text")
        self.assertIn("a@b.com", buf.getvalue())

    def test_process_file_json_stdout(self) -> None:
        path = self._write_temp("hello a@b.com\n")
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            process_file(path, None, ["email"], "keep_all", "json")
        data = json.loads(buf.getvalue())
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)

    def test_process_file_to_output_file(self) -> None:
        inpath = self._write_temp("hello a@b.com\n")
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as out:
            outpath = out.name
        buf = io.StringIO()
        with patch("sys.stdout", buf):
            process_file(inpath, outpath, ["email"], "keep_all", "json")
        self.assertIn("Results written to", buf.getvalue())
        with open(outpath, encoding="utf-8") as f:
            data = json.load(f)
        self.assertIsInstance(data, list)

    def test_process_file_missing_input_exits(self) -> None:
        with self.assertRaises(SystemExit):
            process_file("/nonexistent/path.txt", None, ["email"], "keep_all", "text")


class TestMain(unittest.TestCase):
    def test_list_annotators_flag(self) -> None:
        buf = io.StringIO()
        with patch("sys.argv", ["cli", "--list-annotators"]), patch("sys.stdout", buf):
            from simple_NER.cli import main
            main()
        self.assertIn("Available", buf.getvalue())

    def test_main_text_arg(self) -> None:
        buf = io.StringIO()
        with patch("sys.argv", ["cli", "contact a@b.com", "-a", "email"]), patch("sys.stdout", buf):
            from simple_NER.cli import main
            main()
        self.assertIn("a@b.com", buf.getvalue())

    def test_main_no_input_prints_help(self) -> None:
        buf = io.StringIO()
        with patch("sys.argv", ["cli"]), patch("sys.stdin") as mock_stdin, patch("sys.stdout", buf):
            mock_stdin.isatty.return_value = True
            from simple_NER.cli import main
            main()
        # Should print help (no crash)

    def test_main_json_format(self) -> None:
        buf = io.StringIO()
        with patch("sys.argv", ["cli", "a@b.com", "-a", "email", "--format", "json"]), \
             patch("sys.stdout", buf):
            from simple_NER.cli import main
            main()
        data = json.loads(buf.getvalue())
        self.assertIn("entities", data)


class TestVersionCoverage(unittest.TestCase):
    def test_version_importable(self) -> None:
        from simple_NER.version import __version__, VERSION_MAJOR, VERSION_MINOR, VERSION_BUILD
        self.assertIsInstance(__version__, str)
        self.assertGreaterEqual(VERSION_MAJOR, 0)
        self.assertGreaterEqual(VERSION_MINOR, 0)
        self.assertGreaterEqual(VERSION_BUILD, 0)


if __name__ == "__main__":
    unittest.main()
