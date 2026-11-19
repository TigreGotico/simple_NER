"""Comprehensive tests for OrganizationAnnotator.

Covers: basic extraction, locale patterns, name property, as_json,
no-match text, confidence parameter, entity data fields.
"""
import pytest

from simple_NER.annotators.organization_ner import OrganizationAnnotator


class TestOrganizationBasicExtraction:
    """Basic English suffix extraction."""

    def test_apple_inc(self):
        ner = OrganizationAnnotator()
        results = list(ner.extract_entities("Apple Inc. signed a deal"))
        assert any("Apple" in r.value for r in results)
        assert all(r.entity_type == "organization" for r in results)

    def test_google_llc(self):
        ner = OrganizationAnnotator()
        results = list(ner.extract_entities("Google LLC is hiring engineers"))
        assert any("Google" in r.value for r in results)

    def test_microsoft_corp(self):
        ner = OrganizationAnnotator()
        results = list(ner.extract_entities("Microsoft Corp released an update"))
        assert any("Microsoft" in r.value for r in results)

    def test_multiple_orgs(self):
        ner = OrganizationAnnotator()
        text = "Apple Inc and Google LLC and Microsoft Corp all attended"
        results = list(ner.extract_entities(text))
        values = " ".join(r.value for r in results)
        assert "Apple" in values
        assert "Google" in values
        assert "Microsoft" in values

    def test_limited_suffix(self):
        ner = OrganizationAnnotator()
        results = list(ner.extract_entities("Acme Ltd filed for bankruptcy"))
        assert any("Acme" in r.value for r in results)

    def test_university(self):
        ner = OrganizationAnnotator()
        results = list(ner.extract_entities("Stanford University leads research"))
        assert any("Stanford" in r.value for r in results)

    def test_hospital(self):
        ner = OrganizationAnnotator(strict_mode=False)
        results = list(ner.extract_entities("Patients treated at Johns Hopkins Hospital"))
        assert any("Hopkins" in r.value or "Johns" in r.value for r in results)


class TestOrganizationGermanSuffixes:
    """German legal-form suffixes are included in the en-us patterns."""

    def test_siemens_gmbh(self):
        # GmbH is included in the en-us organization.rx patterns
        ner = OrganizationAnnotator()
        results = list(ner.extract_entities("Siemens GmbH announced earnings"))
        assert any("Siemens" in r.value for r in results)

    def test_bmw_ag(self):
        ner = OrganizationAnnotator()
        results = list(ner.extract_entities("BMW AG reported strong sales"))
        assert any("BMW" in r.value for r in results)

    def test_gmbh_type_is_company(self):
        ner = OrganizationAnnotator()
        results = list(ner.extract_entities("Siemens GmbH announced earnings"))
        org_types = [r.data["org_type"] for r in results if "Siemens" in r.value]
        assert org_types and org_types[0] == "company"


class TestOrganizationNameProperty:
    """name property returns the correct annotator name."""

    def test_name_property(self):
        ner = OrganizationAnnotator()
        assert ner.name == "organization"


class TestOrganizationAsJson:
    """as_json=True / Entity.as_json() path."""

    def test_as_json_structure(self):
        ner = OrganizationAnnotator()
        results = list(ner.extract_entities("Apple Inc is innovative"))
        assert len(results) >= 1
        j = results[0].as_json()
        assert "value" in j
        assert "entity_type" in j
        assert j["entity_type"] == "organization"

    def test_entity_as_json_is_dict(self):
        ner = OrganizationAnnotator()
        results = list(ner.extract_entities("Google LLC"))
        assert len(results) >= 1
        j = results[0].as_json()
        assert isinstance(j, dict)
        assert j["entity_type"] == "organization"


class TestOrganizationNoMatch:
    """No-match text should yield nothing."""

    def test_plain_text(self):
        ner = OrganizationAnnotator()
        results = list(ner.extract_entities("Just some regular text here"))
        assert results == []

    def test_lowercase_only(self):
        ner = OrganizationAnnotator()
        results = list(ner.extract_entities("hello world foo bar"))
        assert results == []

    def test_empty_string(self):
        ner = OrganizationAnnotator()
        results = list(ner.extract_entities(""))
        assert results == []


class TestOrganizationConfidence:
    """confidence parameter is reflected in entities."""

    def test_default_confidence(self):
        ner = OrganizationAnnotator()
        results = list(ner.extract_entities("Apple Inc is great"))
        assert all(r.confidence == pytest.approx(0.85) for r in results)

    def test_custom_confidence(self):
        ner = OrganizationAnnotator(confidence=0.5)
        results = list(ner.extract_entities("Apple Inc is great"))
        assert all(r.confidence == pytest.approx(0.5) for r in results)

    def test_confidence_range(self):
        ner = OrganizationAnnotator(confidence=1.0)
        results = list(ner.extract_entities("Google LLC"))
        assert all(0.0 <= r.confidence <= 1.0 for r in results)


class TestOrganizationDataFields:
    """Entity data dict contains expected keys with valid values."""

    def test_data_has_start_end(self):
        ner = OrganizationAnnotator()
        text = "Apple Inc is great"
        results = list(ner.extract_entities(text))
        assert len(results) >= 1
        data = results[0].data
        assert "start" in data
        assert "end" in data
        assert isinstance(data["start"], int)
        assert isinstance(data["end"], int)

    def test_data_start_end_span_in_source(self):
        ner = OrganizationAnnotator()
        text = "Apple Inc is great"
        results = list(ner.extract_entities(text))
        for r in results:
            span = text[r.data["start"]:r.data["end"]]
            assert r.value in span or span in r.value

    def test_data_has_org_type(self):
        ner = OrganizationAnnotator()
        results = list(ner.extract_entities("Apple Inc is great"))
        assert len(results) >= 1
        assert "org_type" in results[0].data

    def test_data_source_text(self):
        ner = OrganizationAnnotator()
        text = "Apple Inc is great"
        results = list(ner.extract_entities(text))
        assert all(r.source_text == text for r in results)

    def test_org_type_company(self):
        ner = OrganizationAnnotator()
        results = list(ner.extract_entities("Apple Inc"))
        org_types = [r.data["org_type"] for r in results]
        assert "company" in org_types

    def test_org_type_educational(self):
        ner = OrganizationAnnotator()
        results = list(ner.extract_entities("Stanford University"))
        org_types = [r.data["org_type"] for r in results]
        assert "educational" in org_types
