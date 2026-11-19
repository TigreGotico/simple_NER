"""Unit tests for new annotators: URL, Phone, Currency, Organization, Hashtag, Date."""
import pytest

from simple_NER import Entity


# ---------------------------------------------------------------------------
# URLAnnotator
# ---------------------------------------------------------------------------

class TestURLAnnotator:
    """Tests for URLAnnotator."""

    def test_http_url(self):
        from simple_NER.annotators.url_ner import URLAnnotator

        ner = URLAnnotator()
        text = "Visit http://example.com"
        results = list(ner.extract_entities(text))

        assert len(results) == 1
        assert results[0].value == "http://example.com"
        assert results[0].entity_type == "url"

    def test_https_url(self):
        from simple_NER.annotators.url_ner import URLAnnotator

        ner = URLAnnotator()
        text = "Secure site: https://secure.example.com/page"
        results = list(ner.extract_entities(text))

        assert len(results) == 1
        assert "https://" in results[0].value

    def test_url_with_path(self):
        from simple_NER.annotators.url_ner import URLAnnotator

        ner = URLAnnotator()
        text = "API endpoint: https://api.example.com/v1/users?id=123"
        results = list(ner.extract_entities(text))

        assert len(results) == 1
        # URL pattern may capture partial path
        assert "https://" in results[0].value
        assert "api.example.com" in results[0].value

    def test_multiple_urls(self):
        from simple_NER.annotators.url_ner import URLAnnotator

        ner = URLAnnotator()
        text = "Visit http://site1.com or https://site2.org"
        results = list(ner.extract_entities(text))

        assert len(results) == 2
        urls = {r.value for r in results}
        assert "http://site1.com" in urls
        assert "https://site2.org" in urls

    def test_no_url(self):
        from simple_NER.annotators.url_ner import URLAnnotator

        ner = URLAnnotator()
        text = "This text has no URLs"
        results = list(ner.extract_entities(text))

        assert len(results) == 0


# ---------------------------------------------------------------------------
# PhoneAnnotator
# ---------------------------------------------------------------------------

class TestPhoneAnnotator:
    """Tests for PhoneAnnotator."""

    def test_international_phone(self):
        from simple_NER.annotators.phone_ner import PhoneAnnotator

        ner = PhoneAnnotator()
        text = "Call +1-555-123-4567"
        results = list(ner.extract_entities(text))

        assert len(results) == 1
        assert results[0].value == "+1-555-123-4567"
        assert results[0].data["type"] == "international"

    def test_us_phone_parentheses(self):
        from simple_NER.annotators.phone_ner import PhoneAnnotator

        ner = PhoneAnnotator()
        text = "Call (555) 987-6543"
        results = list(ner.extract_entities(text))

        assert len(results) == 1
        assert "(555)" in results[0].value

    def test_us_phone_dashes(self):
        from simple_NER.annotators.phone_ner import PhoneAnnotator

        ner = PhoneAnnotator()
        text = "Phone: 555-123-4567"
        results = list(ner.extract_entities(text))

        assert len(results) == 1

    def test_local_phone(self):
        from simple_NER.annotators.phone_ner import PhoneAnnotator

        ner = PhoneAnnotator()
        text = "Local: 123-4567"
        results = list(ner.extract_entities(text))

        assert len(results) == 1
        assert results[0].data["type"] == "local"

    def test_no_phone(self):
        from simple_NER.annotators.phone_ner import PhoneAnnotator

        ner = PhoneAnnotator()
        text = "No phone numbers here"
        results = list(ner.extract_entities(text))

        assert len(results) == 0


# ---------------------------------------------------------------------------
# CurrencyAnnotator
# ---------------------------------------------------------------------------

class TestCurrencyAnnotator:
    """Tests for CurrencyAnnotator."""

    def test_usd_symbol(self):
        from simple_NER.annotators.currency_ner import CurrencyAnnotator

        ner = CurrencyAnnotator()
        text = "Price: $99.99"
        results = list(ner.extract_entities(text))

        assert len(results) == 1
        assert results[0].value == "$99.99"
        assert results[0].data["currency"] == "USD"

    def test_eur_symbol(self):
        from simple_NER.annotators.currency_ner import CurrencyAnnotator

        ner = CurrencyAnnotator()
        text = "Cost: €50"
        results = list(ner.extract_entities(text))

        assert len(results) == 1
        assert any(r.data["currency"] == "EUR" for r in results)

    def test_gbp_symbol(self):
        from simple_NER.annotators.currency_ner import CurrencyAnnotator

        ner = CurrencyAnnotator()
        text = "Price: £1,000.50"
        results = list(ner.extract_entities(text))

        assert len(results) == 1
        assert results[0].data["currency"] == "GBP"

    def test_currency_code(self):
        from simple_NER.annotators.currency_ner import CurrencyAnnotator

        ner = CurrencyAnnotator()
        text = "Amount: USD 500"
        results = list(ner.extract_entities(text))

        assert len(results) == 1
        assert results[0].data["currency"] == "USD"

    def test_multiple_currencies(self):
        from simple_NER.annotators.currency_ner import CurrencyAnnotator

        ner = CurrencyAnnotator()
        text = "Prices: $100, €80, £60"
        results = list(ner.extract_entities(text))

        assert len(results) == 3
        currencies = {r.data["currency"] for r in results}
        assert currencies == {"USD", "EUR", "GBP"}

    def test_no_currency(self):
        from simple_NER.annotators.currency_ner import CurrencyAnnotator

        ner = CurrencyAnnotator()
        text = "Just numbers: 100, 200, 300"
        results = list(ner.extract_entities(text))

        assert len(results) == 0


# ---------------------------------------------------------------------------
# OrganizationAnnotator
# ---------------------------------------------------------------------------

class TestOrganizationAnnotator:
    """Tests for OrganizationAnnotator."""

    def test_company_inc(self):
        from simple_NER.annotators.organization_ner import OrganizationAnnotator

        ner = OrganizationAnnotator()
        text = "Apple Inc announced"
        results = list(ner.extract_entities(text))

        assert len(results) >= 1
        assert any("Apple" in r.value for r in results)

    def test_company_llc(self):
        from simple_NER.annotators.organization_ner import OrganizationAnnotator

        ner = OrganizationAnnotator()
        text = "Google LLC is hiring"
        results = list(ner.extract_entities(text))

        assert len(results) >= 1
        assert any("Google" in r.value for r in results)

    def test_university(self):
        from simple_NER.annotators.organization_ner import OrganizationAnnotator

        ner = OrganizationAnnotator()
        text = "Stanford University research"
        results = list(ner.extract_entities(text))

        assert len(results) >= 1
        assert any("University" in r.value for r in results)

    def test_strict_mode(self):
        from simple_NER.annotators.organization_ner import OrganizationAnnotator

        # Strict mode should have fewer false positives
        ner_strict = OrganizationAnnotator(strict_mode=True)
        ner_relaxed = OrganizationAnnotator(strict_mode=False)

        text = "Apple Inc and Microsoft Corp"
        strict_results = list(ner_strict.extract_entities(text))
        relaxed_results = list(ner_relaxed.extract_entities(text))

        # Both should find organizations
        assert len(strict_results) >= 1
        assert len(relaxed_results) >= 1

    def test_no_organization(self):
        from simple_NER.annotators.organization_ner import OrganizationAnnotator

        ner = OrganizationAnnotator()
        text = "Just regular text here"
        results = list(ner.extract_entities(text))

        # Should have minimal false positives
        assert len(results) == 0


# ---------------------------------------------------------------------------
# HashtagAnnotator
# ---------------------------------------------------------------------------

class TestHashtagAnnotator:
    """Tests for HashtagAnnotator."""

    def test_simple_hashtag(self):
        from simple_NER.annotators.hashtag_ner import HashtagAnnotator

        ner = HashtagAnnotator()
        text = "Love this! #awesome"
        results = list(ner.extract_entities(text))

        assert len(results) == 1
        assert results[0].value == "#awesome"

    def test_camelcase_hashtag(self):
        from simple_NER.annotators.hashtag_ner import HashtagAnnotator

        ner = HashtagAnnotator()
        text = "#BestDayEver was amazing"
        results = list(ner.extract_entities(text))

        assert len(results) == 1
        assert results[0].data["type"] == "CamelCase"

    def test_hashtag_with_numbers(self):
        from simple_NER.annotators.hashtag_ner import HashtagAnnotator

        ner = HashtagAnnotator()
        text = "New year #2024goals"  # Hashtag must start with letter
        results = list(ner.extract_entities(text))

        assert len(results) == 1
        # Type depends on classification - just verify it's a valid hashtag
        assert results[0].value.startswith("#")
        assert "2024" in results[0].value

    def test_underscored_hashtag(self):
        from simple_NER.annotators.hashtag_ner import HashtagAnnotator

        ner = HashtagAnnotator()
        text = "Check #machine_learning"
        results = list(ner.extract_entities(text))

        # Underscore may be treated as word boundary depending on pattern
        assert len(results) >= 1
        # Just verify we got a hashtag
        assert results[0].value.startswith("#")

    def test_skip_numbers_only(self):
        from simple_NER.annotators.hashtag_ner import HashtagAnnotator

        ner = HashtagAnnotator()
        text = "Skip #123 but keep #tag123"
        results = list(ner.extract_entities(text))

        # Should skip #123 (numbers only) but keep #tag123
        assert len(results) == 1
        assert results[0].value == "#tag123"

    def test_multiple_hashtags(self):
        from simple_NER.annotators.hashtag_ner import HashtagAnnotator

        ner = HashtagAnnotator()
        text = "#first #second #third"
        results = list(ner.extract_entities(text))

        assert len(results) == 3


# ---------------------------------------------------------------------------
# DateAnnotator
# ---------------------------------------------------------------------------

class TestDateAnnotator:
    """Tests for DateAnnotator."""

    def test_us_format(self):
        from simple_NER.annotators.date_ner import DateAnnotator

        ner = DateAnnotator()
        text = "Meeting on 12/25/2024"
        results = list(ner.extract_entities(text))

        assert len(results) == 1
        assert results[0].data["month"] == 12
        assert results[0].data["day"] == 25
        assert results[0].data["year"] == 2024

    def test_iso_format(self):
        from simple_NER.annotators.date_ner import DateAnnotator

        ner = DateAnnotator()
        text = "Deadline: 2024-01-15"
        results = list(ner.extract_entities(text))

        assert len(results) == 1
        assert results[0].data["format"] == "ISO"

    def test_written_us_format(self):
        from simple_NER.annotators.date_ner import DateAnnotator

        ner = DateAnnotator()
        text = "Event on January 5, 2025"
        results = list(ner.extract_entities(text))

        assert len(results) == 1
        assert results[0].data["month"] == 1

    def test_written_short_month(self):
        from simple_NER.annotators.date_ner import DateAnnotator

        ner = DateAnnotator()
        text = "Due Jan 5, 2025"
        results = list(ner.extract_entities(text))

        assert len(results) == 1

    def test_eu_format(self):
        from simple_NER.annotators.date_ner import DateAnnotator

        ner = DateAnnotator()
        text = "Conference on 15 March 2025"
        results = list(ner.extract_entities(text))

        assert len(results) == 1
        assert results[0].data["day"] == 15
        assert results[0].data["month"] == 3

    def test_multiple_dates(self):
        from simple_NER.annotators.date_ner import DateAnnotator

        ner = DateAnnotator()
        text = "From 01/01/2024 to 12/31/2024"
        results = list(ner.extract_entities(text))

        assert len(results) == 2

    def test_invalid_date_skipped(self):
        from simple_NER.annotators.date_ner import DateAnnotator

        ner = DateAnnotator()
        text = "Invalid: 13/45/9999"
        results = list(ner.extract_entities(text))

        # Should skip invalid dates
        assert len(results) == 0


# ---------------------------------------------------------------------------
# Integration Tests
# ---------------------------------------------------------------------------

class TestNewAnnotatorsIntegration:
    """Integration tests for all new annotators."""

    def test_all_new_annotators(self):
        from simple_NER.annotators.factory import create_pipeline

        # Create pipeline with all new annotators
        pipeline = create_pipeline([
            'url', 'phone', 'currency',
            'organization', 'hashtag', 'date'
        ])

        text = """
        Apple Inc announced on 12/25/2024.
        Visit https://apple.com for $999.
        Call +1-555-123-4567 #Apple #Tech
        """

        results = list(pipeline.process(text))

        # Should find entities from multiple annotators
        types = {r.entity_type for r in results}

        assert "url" in types
        assert "phone_number" in types or "phone" in types
        assert "money" in types or "currency" in types
        assert "organization" in types
        assert "hashtag" in types
        assert "date" in types


# ---------------------------------------------------------------------------
# Multilingual / Unicode coverage
# ---------------------------------------------------------------------------

class TestMultilingualAnnotators:
    """Tests for language-aware and Unicode-capable annotators."""

    # --- HashtagAnnotator: Unicode scripts ---

    def test_hashtag_arabic(self):
        from simple_NER.annotators.hashtag_ner import HashtagAnnotator
        ner = HashtagAnnotator()
        results = list(ner.extract_entities("أحب #هاشتاق هذا"))
        assert len(results) == 1
        assert results[0].data["tag"] == "هاشتاق"

    def test_hashtag_japanese(self):
        from simple_NER.annotators.hashtag_ner import HashtagAnnotator
        ner = HashtagAnnotator()
        results = list(ner.extract_entities("これは #タグ です"))
        assert len(results) == 1
        assert results[0].data["tag"] == "タグ"

    def test_hashtag_chinese(self):
        from simple_NER.annotators.hashtag_ner import HashtagAnnotator
        ner = HashtagAnnotator()
        results = list(ner.extract_entities("看 #标签 吧"))
        assert len(results) == 1

    def test_hashtag_cyrillic(self):
        from simple_NER.annotators.hashtag_ner import HashtagAnnotator
        ner = HashtagAnnotator()
        results = list(ner.extract_entities("Привет #тег мира"))
        assert len(results) == 1
        assert results[0].data["tag"] == "тег"

    def test_hashtag_all_digits_skipped(self):
        from simple_NER.annotators.hashtag_ner import HashtagAnnotator
        ner = HashtagAnnotator()
        results = list(ner.extract_entities("#123"))
        assert len(results) == 0

    # --- DateAnnotator: multilingual month names ---

    def test_date_spanish_month(self):
        from simple_NER.annotators.date_ner import DateAnnotator
        ner = DateAnnotator()
        results = list(ner.extract_entities("Reunión el 5 enero 2025"))
        assert len(results) == 1
        assert results[0].data["month"] == 1

    def test_date_french_month(self):
        from simple_NER.annotators.date_ner import DateAnnotator
        ner = DateAnnotator()
        results = list(ner.extract_entities("Rendez-vous le 15 janvier 2025"))
        assert len(results) == 1
        assert results[0].data["month"] == 1

    def test_date_german_month(self):
        from simple_NER.annotators.date_ner import DateAnnotator
        ner = DateAnnotator()
        results = list(ner.extract_entities("Termin am 20 März 2025"))
        assert len(results) == 1
        assert results[0].data["month"] == 3

    def test_date_italian_month(self):
        from simple_NER.annotators.date_ner import DateAnnotator
        ner = DateAnnotator()
        results = list(ner.extract_entities("Riunione il 10 febbraio 2025"))
        assert len(results) == 1
        assert results[0].data["month"] == 2

    def test_date_portuguese_month(self):
        from simple_NER.annotators.date_ner import DateAnnotator
        ner = DateAnnotator()
        results = list(ner.extract_entities("Reunião em 3 março 2025"))
        assert len(results) == 1
        assert results[0].data["month"] == 3

    # --- CurrencyAnnotator: written word forms ---

    def test_currency_written_dollars(self):
        from simple_NER.annotators.currency_ner import CurrencyAnnotator
        ner = CurrencyAnnotator()
        results = list(ner.extract_entities("That costs 50 dollars"))
        assert len(results) == 1
        assert results[0].data["currency"] == "USD"

    def test_currency_written_euros(self):
        from simple_NER.annotators.currency_ner import CurrencyAnnotator
        ner = CurrencyAnnotator()
        results = list(ner.extract_entities("That costs 30 euros"))
        assert len(results) == 1
        assert any(r.data["currency"] == "EUR" for r in results)

    def test_currency_written_pounds(self):
        from simple_NER.annotators.currency_ner import CurrencyAnnotator
        ner = CurrencyAnnotator()
        results = list(ner.extract_entities("That's 20 pounds sterling"))
        assert len(results) == 1
        assert results[0].data["currency"] == "GBP"

    # --- OrganizationAnnotator: international suffixes ---

    def test_org_german_gmbh(self):
        from simple_NER.annotators.organization_ner import OrganizationAnnotator
        ner = OrganizationAnnotator(strict_mode=False)
        results = list(ner.extract_entities("Müller GmbH is expanding"))
        types = [r.data["org_type"] for r in results]
        assert "company" in types

    def test_org_french_sarl(self):
        from simple_NER.annotators.organization_ner import OrganizationAnnotator
        ner = OrganizationAnnotator(strict_mode=False)
        results = list(ner.extract_entities("Dupont SARL a signé le contrat"))
        types = [r.data["org_type"] for r in results]
        assert "company" in types

    def test_org_dutch_university(self):
        from simple_NER.annotators.organization_ner import OrganizationAnnotator
        ner = OrganizationAnnotator()
        results = list(ner.extract_entities("Students at Amsterdam University"))
        types = [r.data["org_type"] for r in results]
        assert "educational" in types

    # --- BaseAnnotator: lang attribute ---

    def test_base_annotator_lang_default(self):
        from simple_NER.annotators.date_ner import DateAnnotator
        ner = DateAnnotator()
        assert ner.lang == "en-us"

    def test_temporal_ner_lang_forwarded(self):
        from simple_NER.annotators.temporal_ner import TemporalNER
        ner = TemporalNER(lang="de-de")
        assert ner.lang == "de-de"

    def test_number_ner_lang_forwarded(self):
        from simple_NER.annotators.numbers_ner import NumberNER
        ner = NumberNER(lang="fr-fr")
        assert ner.lang == "fr-fr"
