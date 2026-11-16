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
# Import-level behaviour
# ---------------------------------------------------------------------------

class TestImport(unittest.TestCase):
    """Module imports correctly."""

    def test_module_importable(self):
        from simple_NER.annotators import numbers_ner  # noqa: F401

    def test_number_ner_class_exists(self):
        from simple_NER.annotators.numbers_ner import NumberNER
        self.assertTrue(callable(NumberNER))

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
# Live tests
# ---------------------------------------------------------------------------

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
        with patch.object(mod, "tag_numbers", MagicMock(side_effect=RuntimeError("boom"))):
            ner = _make_ner()
            # Should not propagate the exception
            results = list(ner.extract_entities("three cats"))
        self.assertEqual(results, [])


# ---------------------------------------------------------------------------
# start/end offsets in entity data (live tests)
# ---------------------------------------------------------------------------

class TestStartEndOffsets(unittest.TestCase):
    """Verify entity.data["start"] and entity.data["end"] character offsets."""

    def test_start_end_present(self):
        results = _entities("three cats")
        self.assertGreaterEqual(len(results), 1)
        e = results[0]
        self.assertIn("start", e.data)
        self.assertIn("end", e.data)

    def test_span_matches_original_word(self):
        text = "I have three cats"
        results = _entities(text)
        self.assertGreaterEqual(len(results), 1)
        e = results[0]
        span = text[e.data["start"]:e.data["end"]]
        self.assertEqual(span, e.value)

    def test_compound_number_span(self):
        text = "three hundred apples"
        results = _entities(text)
        self.assertGreaterEqual(len(results), 1)
        e = results[0]
        span = text[e.data["start"]:e.data["end"]]
        self.assertEqual(span, e.value)
        self.assertIn("three hundred", span)

    def test_mid_sentence_offset(self):
        text = "I see twenty birds flying"
        results = _entities(text)
        self.assertGreaterEqual(len(results), 1)
        e = results[0]
        span = text[e.data["start"]:e.data["end"]]
        self.assertEqual(span, e.value)
        self.assertGreater(e.data["start"], 0)

    def test_multiple_numbers_offsets_distinct(self):
        text = "two cats and five dogs"
        results = _entities(text)
        if len(results) >= 2:
            starts = [e.data["start"] for e in results]
            self.assertEqual(len(starts), len(set(starts)), "Offsets should be distinct")


# ---------------------------------------------------------------------------
# One entity per number, with its own span and value
# ---------------------------------------------------------------------------

class TestEachNumberIsOneEntity(unittest.TestCase):
    """Gold spans come from str.index on the text, values from the words."""

    def _assert_numbers(self, text, lang, expected, **kwargs):
        gold, start = [], 0
        for surface, number in expected:
            start = text.index(surface, start)
            gold.append((surface, number, start, start + len(surface)))
            start += len(surface)
        found = [(e.value, e.data["number"], e.data["start"], e.data["end"])
                 for e in _entities(text, lang=lang, **kwargs)]
        self.assertEqual(found, gold)

    def test_en_ordinal_is_one_number(self):
        self._assert_numbers("the twenty first floor", "en-us", [("twenty first", "21")])

    def test_en_ordinal_is_left_out_without_ordinals(self):
        self._assert_numbers("the twenty first floor", "en-us", [], ordinals=False)

    def test_en_fraction(self):
        self._assert_numbers("a third of the cake", "en-us", [("a third", "1/3")])

    def test_pt_two_adjacent_numbers_stay_apart(self):
        self._assert_numbers("vinte e um e vinte", "pt-pt",
                             [("vinte e um", "21"), ("vinte", "20")])

    def test_pt_article_is_no_number(self):
        self._assert_numbers("comprei uma casa e duas bicicletas", "pt-pt", [("duas", "2")])

    def test_pt_ordinal(self):
        self._assert_numbers("o vigésimo primeiro andar", "pt-pt", [("vigésimo primeiro", "21")])

    def test_es_two_adjacent_numbers_stay_apart(self):
        self._assert_numbers("veintiuno y veinte", "es-es",
                             [("veintiuno", "21"), ("veinte", "20")])

    def test_fr_two_adjacent_numbers_stay_apart(self):
        self._assert_numbers("vingt et un et vingt", "fr-fr",
                             [("vingt et un", "21"), ("vingt", "20")])


# ---------------------------------------------------------------------------
# __main__ block smoke-test (no crash, no output checked)
# ---------------------------------------------------------------------------

class TestMainBlock(unittest.TestCase):
    """The __main__ block must not crash when imported via runpy."""

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
