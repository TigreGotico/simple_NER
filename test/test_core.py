"""Unit tests for simple_NER core: Entity, SimpleNER, RuleNER, RegexNER, NERWrapper.

No external dependencies beyond simplematch and quebra_frases.
"""
import pytest
from simple_NER import Entity, SimpleNER, _SimpleNamespace
from simple_NER.rules import Rule, RuleNER
from simple_NER.rules.rx import RegexNER
from simple_NER.annotators import NERWrapper


# ---------------------------------------------------------------------------
# Entity
# ---------------------------------------------------------------------------

class TestEntity:
    def test_basic_attributes(self):
        e = Entity("Alice", "person", source_text="Hello Alice")
        assert e.value == "Alice"
        assert e.entity_type == "person"
        assert e.source_text == "Hello Alice"
        assert e.confidence == 1

    def test_default_entity_type(self):
        e = Entity("foo")
        assert e.entity_type == "entity"

    def test_spans_case_insensitive(self):
        e = Entity("alice", "person", source_text="Hello Alice", ignore_case=True)
        assert len(e.spans) == 1
        start, end = e.spans[0]
        assert start == 6
        assert end == 11

    def test_spans_case_sensitive(self):
        e = Entity("alice", "person", source_text="Hello Alice", ignore_case=False)
        # Case-sensitive: "alice" not in "Hello Alice"
        assert len(e.spans) == 0

    def test_indexes(self):
        e = Entity("cat", "animal", source_text="cat sat on a cat mat")
        assert e.indexes == [0, 13]

    def test_occurrence_number(self):
        e = Entity("cat", "animal", source_text="cat sat on a cat mat")
        assert e.occurrence_number == 2

    def test_rules_normalised_to_list(self):
        e = Entity("foo", rules="some_rule")
        assert isinstance(e.rules, list)
        assert e.rules == ["some_rule"]

    def test_rules_list_preserved(self):
        e = Entity("foo", rules=["r1", "r2"])
        assert e.rules == ["r1", "r2"]

    def test_data_flat_attributes(self):
        e = Entity("42", data={"score": 0.9, "lang": "en"})
        assert e.score == 0.9
        assert e.lang == "en"

    def test_data_value_key_renamed(self):
        """'value' key in data must not shadow the .value property."""
        e = Entity("hello", data={"value": "world"})
        assert e.value == "hello"
        assert e.data_value == "world"

    def test_data_nested_dict_becomes_namespace(self):
        e = Entity("x", data={"meta": {"author": "jarbasAI"}})
        assert isinstance(e.meta, _SimpleNamespace)
        assert e.meta.author == "jarbasAI"

    def test_as_json_keys(self):
        e = Entity("Alice", "person", source_text="Hello Alice")
        j = e.as_json()
        for key in ("entity_type", "spans", "value", "source_text",
                    "confidence", "data", "rules"):
            assert key in j

    def test_repr(self):
        e = Entity("Alice", "person")
        assert repr(e) == "person:Alice"


# ---------------------------------------------------------------------------
# Rule
# ---------------------------------------------------------------------------

class TestRule:
    def test_as_json(self):
        r = Rule("greeting", ["hello {name}"])
        j = r.as_json()
        assert j["name"] == "greeting"
        assert j["rules"] == ["hello {name}"]

    def test_repr(self):
        r = Rule("greeting", [])
        assert repr(r) == "greeting"


# ---------------------------------------------------------------------------
# SimpleNER
# ---------------------------------------------------------------------------

class TestSimpleNER:
    def test_add_and_lookup(self):
        ner = SimpleNER()
        ner.add_entity_examples("person", ["alice", "bob"])
        results = list(ner.entity_lookup("bob went to the store"))
        assert len(results) == 1
        assert results[0].entity_type == "person"
        assert results[0].value == "bob"

    def test_lookup_as_json(self):
        ner = SimpleNER()
        ner.add_entity_examples("color", ["red"])
        results = list(ner.entity_lookup("I like red things", as_json=True))
        assert isinstance(results[0], dict)

    def test_is_match_true(self):
        ner = SimpleNER()
        ner.add_entity_examples("fruit", ["apple", "banana"])
        assert ner.is_match("I ate an apple", "fruit") is True

    def test_is_match_false(self):
        ner = SimpleNER()
        ner.add_entity_examples("fruit", ["apple"])
        assert ner.is_match("I ate an orange", "fruit") is False

    def test_no_partial_word_match(self):
        """'apple' must not match 'pineapple'."""
        ner = SimpleNER()
        ner.add_entity_examples("fruit", ["apple"])
        assert ner.is_match("I ate pineapple", "fruit") is False

    def test_in_place_annotation(self):
        ner = SimpleNER()
        ner.add_entity_examples("person", ["alice"])
        annotated = ner.in_place_annotation("hello alice")
        assert "(person)" in annotated

    def test_extract_entities_delegates(self):
        ner = SimpleNER()
        ner.add_entity_examples("animal", ["cat"])
        entities = list(ner.extract_entities("the cat sat"))
        assert len(entities) == 1


# ---------------------------------------------------------------------------
# RuleNER
# ---------------------------------------------------------------------------

class TestRuleNER:
    def test_simple_rule_extraction(self):
        ner = RuleNER()
        ner.add_rule("name", "my name is {person}")
        results = list(ner.extract_entities("my name is jarbas"))
        assert len(results) == 1
        assert results[0].entity_type == "person"
        assert results[0].value == "jarbas"

    def test_multiple_rules_same_name(self):
        ner = RuleNER()
        ner.add_rule("greeting", ["hello {name}", "hi {name}"])
        r1 = list(ner.extract_entities("hello world"))
        r2 = list(ner.extract_entities("hi there"))
        assert r1[0].value == "world"
        assert r2[0].value == "there"

    def test_as_json_output(self):
        ner = RuleNER()
        ner.add_rule("item", "I want {thing}")
        results = list(ner.extract_entities("I want coffee", as_json=True))
        assert isinstance(results[0], dict)
        assert results[0]["entity_type"] == "thing"

    def test_entity_examples_via_rule_ner(self):
        ner = RuleNER()
        ner.add_entity_examples("color", ["blue"])
        results = list(ner.entity_lookup("the sky is blue"))
        assert len(results) == 1

    def test_no_match_returns_empty(self):
        ner = RuleNER()
        ner.add_rule("name", "my name is {person}")
        assert list(ner.extract_entities("the sky is blue")) == []


# ---------------------------------------------------------------------------
# RegexNER
# ---------------------------------------------------------------------------

class TestRegexNER:
    def test_simple_regex(self):
        ner = RegexNER()
        ner.add_rule("greeting", r"(hello\s+\w+)")
        results = list(ner.extract_entities("hello world"))
        assert len(results) >= 1
        assert "hello" in results[0].value.lower()

    def test_add_entity_examples_word_boundary(self):
        ner = RegexNER()
        ner.add_entity_examples("person", ["bob", "alice"])
        results = list(ner.entity_lookup("alice went home"))
        assert len(results) == 1
        assert results[0].value == "alice"

    def test_no_partial_word_via_entity_examples(self):
        ner = RegexNER()
        ner.add_entity_examples("name", ["bob"])
        results = list(ner.entity_lookup("bobby went home"))
        # "bobby" should NOT match word-boundary rule for "bob"
        assert len(results) == 0

    def test_as_json(self):
        ner = RegexNER()
        ner.add_rule("email", r"[\w.+-]+@[\w-]+\.[a-z]{2,}")
        results = list(ner.extract_entities("contact foo@bar.com", as_json=True))
        assert isinstance(results[0], dict)

    def test_invalid_regex_skipped(self):
        ner = RegexNER()
        ner.add_rule("bad", r"[unclosed")
        # Should not raise; just yield nothing
        results = list(ner.extract_entities("some text"))
        assert results == []


# ---------------------------------------------------------------------------
# NERWrapper
# ---------------------------------------------------------------------------

class TestNERWrapper:
    def test_single_detector(self):
        ner = RuleNER()
        ner.add_rule("fruit", "I like {fruit}")

        wrapper = NERWrapper()
        wrapper.add_detector(ner.extract_entities)
        results = list(wrapper.extract_entities("I like mango"))
        assert len(results) == 1
        assert results[0].entity_type == "fruit"

    def test_multiple_detectors(self):
        ner1 = RuleNER()
        ner1.add_rule("color", "color is {color}")
        ner2 = RegexNER()
        ner2.add_rule("digit", r"\b(\d+)\b")

        wrapper = NERWrapper()
        wrapper.add_detector(ner1.extract_entities)
        wrapper.add_detector(ner2.extract_entities)
        results = list(wrapper.extract_entities("color is blue and 42"))
        types = {r.entity_type for r in results}
        assert "color" in types
        assert "digit" in types

    def test_as_json(self):
        ner = RegexNER()
        ner.add_rule("num", r"\b(\d+)\b")
        wrapper = NERWrapper()
        wrapper.add_detector(ner.extract_entities)
        results = list(wrapper.extract_entities("there are 3 cats", as_json=True))
        assert isinstance(results[0], dict)
