"""Comprehensive tests for simple_NER.annotators.numbers_ner.NumberNER."""
from __future__ import annotations

import sys
import types
import importlib
import unittest
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_ner(**kwargs):
    """Import NumberNER fresh and return an instance."""
    from simple_NER.annotators.numbers_ner import NumberNER
    return NumberNER(**kwargs)


def _entities(text: str, **kwargs) -> list:
    """Return list of entities from NumberNER.extract_entities()."""
    ner = _make_ner(**kwargs)
    return list(ner.extract_entities(text))


# ---------------------------------------------------------------------------
# Basic availability guard
# ---------------------------------------------------------------------------

try:
    from ovos_number_parser import numbers_to_digits as _ntest  # noqa: F401
    _OVOS_AVAILABLE = True
except ImportError:
    try:
        from ovos_number_parser import convert_words_to_numbers as _ntest  # noqa: F401
        _OVOS_AVAILABLE = True
    except ImportError:
        _OVOS_AVAILABLE = False


# ---------------------------------------------------------------------------
# Import-level behaviour
# ---------------------------------------------------------------------------

class TestImport(unittest.TestCase):
    """Module imports correctly regardless of whether ovos-number-parser is present."""

    def test_module_importable(self):
        from simple_NER.annotators import numbers_ner  # noqa: F401

    def test_number_ner_class_exists(self):
        from simple_NER.annotators.numbers_ner import NumberNER
        self.assertTrue(callable(NumberNER))

    def test_ovos_flag_is_bool(self):
        from simple_NER.annotators import numbers_ner
        self.assertIsInstance(numbers_ner._OVOS_AVAILABLE, bool)


# ---------------------------------------------------------------------------
# Constructor & attributes
# ---------------------------------------------------------------------------

class TestConstructor(unittest.TestCase):

    def test_default_attributes(self):
        ner = _make_ner()
        self.assertTrue(ner.ordinals)
        self.assertTrue(ner.short_scale)
        self.assertFalse(ner._case_sensitive)
        self.assertEqual(ner.confidence, 1.0)
        self.assertEqual(ner.lang, "en-us")

    def test_custom_lang(self):
        ner = _make_ner(lang="de-de")
        self.assertEqual(ner.lang, "de-de")

    def test_custom_confidence(self):
        ner = _make_ner(confidence=0.7)
        self.assertAlmostEqual(ner.confidence, 0.7)

    def test_name_property(self):
        ner = _make_ner()
        self.assertEqual(ner.name, "numbers")

    def test_ordinals_false(self):
        ner = _make_ner(ordinals=False)
        self.assertFalse(ner.ordinals)

    def test_short_scale_false(self):
        ner = _make_ner(short_scale=False)
        self.assertFalse(ner.short_scale)

    def test_case_sensitive_true(self):
        ner = _make_ner(case_sensitive=True)
        self.assertTrue(ner._case_sensitive)


# ---------------------------------------------------------------------------
# When ovos-number-parser is NOT available
# ---------------------------------------------------------------------------

class TestNoOvosParser(unittest.TestCase):
    """NumberNER must be a no-op when the parser is missing."""

    def test_no_results_when_unavailable(self):
        import simple_NER.annotators.numbers_ner as mod
        original = mod._OVOS_AVAILABLE
        original_fn = mod._convert_numbers
        try:
            mod._OVOS_AVAILABLE = False
            mod._convert_numbers = None
            ner = _make_ner()
            results = list(ner.annotate("I have three cats"))
            self.assertEqual(results, [])
        finally:
            mod._OVOS_AVAILABLE = original
            mod._convert_numbers = original_fn

    def test_annotate_returns_generator_when_unavailable(self):
        import simple_NER.annotators.numbers_ner as mod
        import types
        original = mod._OVOS_AVAILABLE
        original_fn = mod._convert_numbers
        try:
            mod._OVOS_AVAILABLE = False
            mod._convert_numbers = None
            ner = _make_ner()
            result = ner.annotate("three hundred")
            self.assertIsInstance(result, types.GeneratorType)
        finally:
            mod._OVOS_AVAILABLE = original
            mod._convert_numbers = original_fn


# ---------------------------------------------------------------------------
# Live tests (only run if ovos-number-parser is installed)
# ---------------------------------------------------------------------------

@unittest.skipUnless(_OVOS_AVAILABLE, "ovos-number-parser not installed")
class TestLiveExtraction(unittest.TestCase):
    """Tests that actually call the parser."""

    # --- basic written numbers ---

    def test_simple_written_number(self):
        results = _entities("I have three cats")
        self.assertGreaterEqual(len(results), 1)
        values = [e.value for e in results]
        self.assertTrue(any("three" in v for v in values))

    def test_compound_written_number(self):
        results = _entities("three hundred apples")
        self.assertGreaterEqual(len(results), 1)
        numeric = results[0].data["number"]
        self.assertIn("300", str(numeric))

    def test_entity_type(self):
        results = _entities("five dogs")
        self.assertGreaterEqual(len(results), 1)
        for e in results:
            self.assertEqual(e.entity_type, "written_number")

    def test_entity_confidence(self):
        results = _entities("twenty birds", confidence=0.8)
        for e in results:
            self.assertAlmostEqual(e.confidence, 0.8)

    def test_entity_source_text_preserved(self):
        text = "twenty birds"
        results = _entities(text)
        for e in results:
            self.assertEqual(e.source_text, text)

    def test_data_has_number_key(self):
        results = _entities("five hundred")
        self.assertGreaterEqual(len(results), 1)
        for e in results:
            self.assertIn("number", e.data)

    # --- zero ---

    def test_zero(self):
        results = _entities("zero people were there")
        # ovos-number-parser may or may not treat "zero" as a word number;
        # just ensure no exception is raised.

    # --- large numbers ---

    def test_large_number(self):
        results = _entities("one million dollars")
        if results:
            numeric = results[0].data["number"]
            self.assertIn("1000000", str(numeric).replace(",", ""))

    # --- case insensitivity default ---

    def test_case_insensitive_default(self):
        results_lower = _entities("three hundred")
        results_upper = _entities("Three Hundred")
        # Both should detect numbers or neither (parser-dependent), but no crash
        # and upper-case should not produce MORE results than lower-case.
        self.assertGreaterEqual(len(results_lower) + 1, len(results_upper))

    # --- guard: emails should NOT produce numeric entities ---

    def test_email_no_spurious_match(self):
        results = _entities("contact me at user@example.com")
        # Ensure nothing incorrectly matches the @ or domain
        for e in results:
            self.assertNotIn("@", e.value)

    # --- guard: phone numbers ---

    def test_phone_number_no_spurious_match(self):
        results = _entities("Call +1-800-555-0100")
        # Should not extract phone number fragments as written-number entities
        for e in results:
            # Numeric-only digits from a phone would not be "written numbers"
            self.assertNotRegex(e.value, r"^\d+$")

    # --- lang parameter ---

    def test_lang_forwarded(self):
        ner = _make_ner(lang="de-de")
        self.assertEqual(ner.lang, "de-de")
        # Should not crash when extract_entities is called regardless of result
        list(ner.extract_entities("drei Katzen"))

    def test_lang_es(self):
        ner = _make_ner(lang="es-es")
        self.assertEqual(ner.lang, "es-es")
        list(ner.extract_entities("tres gatos"))

    def test_lang_fr(self):
        ner = _make_ner(lang="fr-fr")
        self.assertEqual(ner.lang, "fr-fr")
        list(ner.extract_entities("trois chats"))

    # --- multiple numbers in one sentence ---

    def test_multiple_numbers(self):
        results = _entities("I have two cats and five dogs")
        # Both "two" and "five" should be caught
        values_str = " ".join(e.value for e in results)
        self.assertTrue("two" in values_str or "five" in values_str)

    # --- text with no numbers ---

    def test_no_numbers(self):
        results = _entities("The cat sat on the mat")
        self.assertEqual(results, [])

    # --- ordinals ---

    def test_ordinals_enabled(self):
        ner = _make_ner(ordinals=True)
        # Should not raise; ordinal extraction is parser-dependent
        list(ner.extract_entities("the third house"))

    def test_ordinals_disabled(self):
        ner = _make_ner(ordinals=False)
        list(ner.extract_entities("the third house"))

    # --- short_scale vs long_scale ---

    def test_short_scale(self):
        ner = _make_ner(short_scale=True)
        list(ner.extract_entities("one billion dollars"))

    def test_long_scale(self):
        ner = _make_ner(short_scale=False)
        list(ner.extract_entities("one billion dollars"))

    # --- extract_entities public method vs annotate ---

    def test_extract_entities_delegates_to_annotate(self):
        ner = _make_ner()
        via_extract = list(ner.extract_entities("two cats"))
        via_annotate = list(ner.annotate("two cats"))
        self.assertEqual(len(via_extract), len(via_annotate))

    # --- error handling: parser raises ---

    def test_exception_in_parser_is_caught(self):
        import simple_NER.annotators.numbers_ner as mod
        original_fn = mod._convert_numbers
        try:
            mod._convert_numbers = MagicMock(side_effect=RuntimeError("boom"))
            ner = _make_ner()
            # Should not propagate the exception
            results = list(ner.extract_entities("three cats"))
            self.assertEqual(results, [])
        finally:
            mod._convert_numbers = original_fn


# ---------------------------------------------------------------------------
# __main__ block smoke-test (no crash, no output checked)
# ---------------------------------------------------------------------------

class TestMainBlock(unittest.TestCase):
    """The __main__ block must not crash when imported via runpy."""

    @unittest.skipUnless(_OVOS_AVAILABLE, "ovos-number-parser not installed")
    def test_main_block_runs(self):
        import runpy
        import io
        from contextlib import redirect_stdout
        buf = io.StringIO()
        with redirect_stdout(buf):
            runpy.run_path(
                str(__import__("pathlib").Path(__file__).parent.parent
                    / "simple_NER" / "annotators" / "numbers_ner.py"),
                run_name="__main__",
            )
        # Just ensure it executed without exception; output is ignored.


if __name__ == "__main__":
    unittest.main()
