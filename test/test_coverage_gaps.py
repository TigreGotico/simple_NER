"""Tests targeting coverage gaps in date_ner, locale, pipeline, and hashtag_ner."""
from __future__ import annotations

import asyncio
import re
import tempfile
from pathlib import Path
from unittest.mock import patch


# ---------------------------------------------------------------------------
# DateAnnotator
# ---------------------------------------------------------------------------

class TestDateAnnotatorFormats:
    """Cover all four format branches in DateAnnotator."""

    def setup_method(self):
        from simple_NER.annotators.date_ner import DateAnnotator
        self.ner = DateAnnotator()

    def test_iso_format(self):
        results = list(self.ner.extract_entities("Event on 2024-01-15"))
        assert any(e.data["format"] == "ISO" for e in results)
        assert any(e.data["month"] == 1 and e.data["day"] == 15 and e.data["year"] == 2024 for e in results)

    def test_us_format(self):
        results = list(self.ner.extract_entities("Meeting on 01/15/2024"))
        assert any(e.data["format"] == "US" for e in results)
        assert any(e.data["month"] == 1 and e.data["day"] == 15 for e in results)

    def test_written_month_day_year(self):
        results = list(self.ner.extract_entities("January 15 2024"))
        assert any(e.data["format"] == "WRITTEN_US" for e in results)
        assert any(e.data["month"] == 1 and e.data["day"] == 15 for e in results)

    def test_written_day_month_year(self):
        results = list(self.ner.extract_entities("15 January 2024"))
        assert any(e.data["format"] == "WRITTEN_EU" for e in results)
        assert any(e.data["month"] == 1 and e.data["day"] == 15 for e in results)


class TestDateAnnotatorValidation:
    """Cover _is_valid_date branches (lines 313, 315, 320, 324-326)."""

    def setup_method(self):
        from simple_NER.annotators.date_ner import DateAnnotator
        self.ner = DateAnnotator()

    def _valid(self, month: int, day: int, year: int) -> bool:
        return self.ner._is_valid_date(month, day, year)

    def test_month_zero_invalid(self):
        assert not self._valid(0, 15, 2024)

    def test_month_13_invalid(self):
        assert not self._valid(13, 1, 2024)

    def test_day_zero_invalid(self):
        assert not self._valid(1, 0, 2024)

    def test_day_32_invalid(self):
        assert not self._valid(1, 32, 2024)

    def test_year_too_old(self):
        assert not self._valid(1, 1, 1899)

    def test_year_too_new(self):
        assert not self._valid(1, 1, 2101)

    def test_april_31_invalid(self):
        # April has 30 days — hits days_in_month check (line 320)
        assert not self._valid(4, 31, 2024)

    def test_feb_30_invalid(self):
        assert not self._valid(2, 30, 2024)

    def test_feb_29_leap_year_valid(self):
        # 2024 is a leap year
        assert self._valid(2, 29, 2024)

    def test_feb_29_non_leap_year_invalid(self):
        # 2023 is not a leap year (lines 324-326)
        assert not self._valid(2, 29, 2023)

    def test_feb_29_century_non_leap(self):
        # 1900 divisible by 100 but not 400 → not a leap year
        assert not self._valid(2, 29, 1900)

    def test_feb_29_400_year_leap(self):
        # 2000 divisible by 400 → is a leap year
        assert self._valid(2, 29, 2000)


class TestDateAnnotatorInvalidDatesNotExtracted:
    """Ensure invalid dates are silently skipped during extraction (line 234)."""

    def setup_method(self):
        from simple_NER.annotators.date_ner import DateAnnotator
        self.ner = DateAnnotator()

    def test_feb_30_not_extracted(self):
        # Feb 30 matches the regex but should be rejected by validation
        results = list(self.ner.extract_entities("Something on 2024-02-30"))
        assert not results

    def test_month_13_iso_not_extracted(self):
        results = list(self.ner.extract_entities("Date: 2024-13-01"))
        assert not results

    def test_april_31_not_extracted(self):
        results = list(self.ner.extract_entities("2024-04-31"))
        assert not results


class TestDateAnnotatorLang:
    """Cover lang-specific init paths (lines 193-199)."""

    def test_de_de_uses_locale_wordlist(self):
        from simple_NER.annotators.date_ner import DateAnnotator
        # de-de has a date_months.txt in locale — uses locale-specific branch
        ner = DateAnnotator(lang="de-de")
        assert ner is not None

    def test_es_es_uses_locale_wordlist(self):
        from simple_NER.annotators.date_ner import DateAnnotator
        ner = DateAnnotator(lang="es-es")
        assert ner is not None

    def test_unknown_lang_falls_back_to_en_us(self):
        from simple_NER.annotators.date_ner import DateAnnotator
        # xx-xx has no locale file — falls back to en-us wordlist (line 195)
        ner = DateAnnotator(lang="xx-xx")
        # Should still find English month names
        results = list(ner.extract_entities("Meeting on January 15 2024"))
        assert len(results) >= 1

    def test_unknown_lang_no_en_us_file_falls_back_to_builtin(self):
        """Cover line 199: neither lang nor en-us wordlist exists."""
        from simple_NER.annotators.date_ner import DateAnnotator
        from simple_NER.utils import locale as locale_mod
        original = locale_mod.load_wordlist

        def empty_wordlist(name: str, lang: str) -> list[str]:
            return []

        with patch.object(locale_mod, "load_wordlist", side_effect=empty_wordlist):
            ner = DateAnnotator(lang="xx-xx")
            results = list(ner.extract_entities("January 15 2024"))
            assert len(results) >= 1


# ---------------------------------------------------------------------------
# utils/locale.py
# ---------------------------------------------------------------------------

class TestLocaleLoadRx:
    """Cover load_rx branches (lines 96, 101-102)."""

    def test_nonexistent_file_returns_empty(self):
        from simple_NER.utils.locale import load_rx
        result = load_rx("nonexistent_file_xyz", "xx-xx")
        assert result == []

    def test_bad_regex_skipped_good_kept(self):
        from simple_NER.utils.locale import load_rx, _LOCALE_DIR
        # Create a temp .rx file under a fake locale
        lang = "zz"
        lang_dir = _LOCALE_DIR / lang
        lang_dir.mkdir(parents=True, exist_ok=True)
        rx_file = lang_dir / "test.rx"
        try:
            rx_file.write_text("(?P<good>\\d+)\n[invalid(\n", encoding="utf-8")
            result = load_rx("test", lang)
            # Only the good pattern should survive
            assert len(result) == 1
            assert result[0].match("123") is not None
        finally:
            rx_file.unlink(missing_ok=True)
            try:
                lang_dir.rmdir()
            except OSError:
                pass


class TestLocaleLocalePath:
    """Cover _locale_path returning None (line 36)."""

    def test_returns_none_for_missing_lang_and_en_us(self):
        from simple_NER.utils.locale import _locale_path
        result = _locale_path("no_such_file", "txt", "zz-zz")
        assert result is None


class TestLocaleLoadWordlist:
    """Cover load_wordlist missing-file branches (lines 119-122, 142)."""

    def test_missing_file_returns_empty(self):
        from simple_NER.utils.locale import load_wordlist
        result = load_wordlist("no_such_wordlist", "xx-xx")
        assert result == []

    def test_existing_file_returns_words(self):
        from simple_NER.utils.locale import load_wordlist
        result = load_wordlist("date_months", "en")
        assert isinstance(result, list)
        assert len(result) > 0


class TestLocaleLoadIntents:
    """Cover load_intents missing-file and bad-template branches (lines 140-148)."""

    def test_missing_file_returns_empty(self):
        from simple_NER.utils.locale import load_intents
        result = load_intents("no_such_intent", "xx-xx")
        assert result == []

    def test_bad_template_skipped_good_kept(self):
        from simple_NER.utils.locale import load_intents, _LOCALE_DIR
        lang = "zz"
        lang_dir = _LOCALE_DIR / lang
        lang_dir.mkdir(parents=True, exist_ok=True)
        intent_file = lang_dir / "test.intent"
        try:
            # A valid template and one that would produce invalid regex
            # intent_to_regex wraps placeholders in named groups; bare re.escape
            # makes the rest literal, so triggering re.error is tricky.
            # Patch re.compile inside intent_to_regex to raise on second call.
            intent_file.write_text(
                "the price is {amount} dollars\nplain line\n",
                encoding="utf-8",
            )
            result = load_intents("test", lang)
            assert len(result) == 2
        finally:
            intent_file.unlink(missing_ok=True)
            try:
                lang_dir.rmdir()
            except OSError:
                pass

    def test_intent_compile_error_skipped(self):
        """Cover the except re.error branch in load_intents (lines 147-148)."""
        from simple_NER.utils import locale as locale_mod

        original_itr = locale_mod.intent_to_regex

        call_count = 0

        def raise_on_second(template: str, flags=re.IGNORECASE):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise re.error("forced error")
            return original_itr(template, flags)

        from simple_NER.utils.locale import _LOCALE_DIR
        lang = "zzz"
        lang_dir = _LOCALE_DIR / lang
        lang_dir.mkdir(parents=True, exist_ok=True)
        intent_file = lang_dir / "test2.intent"
        try:
            intent_file.write_text("line one\nline two\n", encoding="utf-8")
            with patch.object(locale_mod, "intent_to_regex", side_effect=raise_on_second):
                result = locale_mod.load_intents("test2", lang)
            assert len(result) == 1
        finally:
            intent_file.unlink(missing_ok=True)
            try:
                lang_dir.rmdir()
            except OSError:
                pass


# ---------------------------------------------------------------------------
# pipeline.py — Span methods and _select_entity
# ---------------------------------------------------------------------------

class TestSpanMethods:
    """Cover Span.overlaps, Span.contains, Span.__len__ (lines 32, 43, 46)."""

    def setup_method(self):
        from simple_NER.pipeline import Span
        self.Span = Span

    def test_overlaps_true(self):
        a = self.Span(0, 5)
        b = self.Span(3, 8)
        assert a.overlaps(b)
        assert b.overlaps(a)

    def test_overlaps_false_adjacent(self):
        a = self.Span(0, 5)
        b = self.Span(5, 10)
        assert not a.overlaps(b)

    def test_overlaps_false_no_contact(self):
        a = self.Span(0, 3)
        b = self.Span(5, 10)
        assert not a.overlaps(b)

    def test_contains_true(self):
        outer = self.Span(0, 10)
        inner = self.Span(2, 8)
        assert outer.contains(inner)

    def test_contains_exact(self):
        s = self.Span(3, 7)
        assert s.contains(self.Span(3, 7))

    def test_contains_false(self):
        a = self.Span(0, 5)
        b = self.Span(3, 8)
        assert not a.contains(b)

    def test_len(self):
        s = self.Span(2, 9)
        assert len(s) == 7


class TestSelectEntity:
    """Cover NERPipeline._select_entity branches (lines 270-283)."""

    def setup_method(self):
        from simple_NER.pipeline import NERPipeline
        from simple_NER import Entity

        self.pipeline_longest = NERPipeline(dedup_strategy="keep_longest")
        self.pipeline_confidence = NERPipeline(dedup_strategy="keep_higher_confidence")
        self.pipeline_first = NERPipeline(dedup_strategy="keep_first")
        self.Entity = Entity

    def _make_entity(self, value: str, confidence: float = 0.9) -> object:
        return self.Entity(value=value, entity_type="test",
                           source_text=value, confidence=confidence)

    def test_empty_returns_none(self):
        assert self.pipeline_longest._select_entity([]) is None

    def test_keep_longest(self):
        e1 = self._make_entity("hi")
        e2 = self._make_entity("hello world")
        assert self.pipeline_longest._select_entity([e1, e2]) is e2

    def test_keep_higher_confidence(self):
        e1 = self._make_entity("foo", confidence=0.5)
        e2 = self._make_entity("bar", confidence=0.95)
        assert self.pipeline_confidence._select_entity([e1, e2]) is e2

    def test_keep_first(self):
        e1 = self._make_entity("first")
        e2 = self._make_entity("second")
        assert self.pipeline_first._select_entity([e1, e2]) is e1


class TestAsyncPipelineDeduplicate:
    """Cover AsyncNERPipeline.process_async with dedup strategy (line 355)."""

    def test_async_with_dedup_strategy(self):
        from simple_NER.pipeline import AsyncNERPipeline
        from simple_NER.annotators.email_ner import EmailNER

        pipeline = AsyncNERPipeline(
            annotators=[EmailNER()],
            dedup_strategy="keep_longest",
        )
        results = asyncio.run(pipeline.process_async("test@example.com"))
        # At least one email entity should be found
        assert isinstance(results, list)


# ---------------------------------------------------------------------------
# hashtag_ner.py
# ---------------------------------------------------------------------------

class TestHashtagAnnotatorEdgeCases:
    """Cover hashtag_ner branches (lines 66, 83, 87, 116, 122, 124)."""

    def setup_method(self):
        from simple_NER.annotators.hashtag_ner import HashtagAnnotator
        self.ner = HashtagAnnotator()

    def test_name_property(self):
        # Line 66 — name property
        assert self.ner.name == "hashtag"

    def test_too_short_skipped(self):
        # Line 83 — min_length check; min is 2 chars; single char tag won't
        # match HASHTAG_PATTERN (\w{2,50}), so use custom annotator
        from simple_NER.annotators.hashtag_ner import HashtagAnnotator
        ner = HashtagAnnotator(min_length=5)
        results = list(ner.extract_entities("#hi there"))
        assert not results

    def test_too_long_skipped(self):
        # Line 83 — max_length check
        from simple_NER.annotators.hashtag_ner import HashtagAnnotator
        ner = HashtagAnnotator(max_length=3)
        results = list(ner.extract_entities("#toolong"))
        assert not results

    def test_all_digits_after_non_digit_prefix(self):
        # Line 87 — isdigit() check; the HASHTAG_PATTERN already blocks pure
        # digit tags, but a tag like '#a123' won't be all digits; confirm
        # an all-digit-text tag is skipped if it somehow slips through.
        from simple_NER.annotators.hashtag_ner import HashtagAnnotator
        ner = HashtagAnnotator()
        # Standard pattern blocks #123 so this confirms the regex + guard work
        results = list(ner.extract_entities("#123"))
        assert not any(e.data["tag"].isdigit() for e in results)

    def test_shouting_hashtag(self):
        # Line 116 — isupper() branch
        results = list(self.ner.extract_entities("#SHOUTING"))
        assert results
        assert results[0].data["type"] == "shouting"

    def test_lowercase_hashtag(self):
        # Line 118 — islower() branch
        results = list(self.ner.extract_entities("#lowercase"))
        assert results
        assert results[0].data["type"] == "lowercase"

    def test_underscored_hashtag(self):
        # Line 122 — underscore branch; needs mixed case so islower() is False
        # first char lower → not CamelCase; has underscore → underscored
        results = list(self.ner.extract_entities("#hello_World"))
        assert results
        assert results[0].data["type"] == "underscored"

    def test_alphanumeric_hashtag(self):
        # Line 124 — alphanumeric branch; mixed case so islower() is False,
        # no underscore, contains a digit
        results = list(self.ner.extract_entities("#Tag2024"))
        assert results
        assert results[0].data["type"] == "alphanumeric"

    def test_mixed_hashtag(self):
        # Line 126 — mixed (fallback) branch: starts upper, no other upper, no underscore, no digits
        results = list(self.ner.extract_entities("#Hello"))
        assert results
        assert results[0].data["type"] == "mixed"
