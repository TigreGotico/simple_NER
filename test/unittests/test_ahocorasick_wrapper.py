"""Tests for AhocorasickAnnotatorWrapper integration."""
from unittest.mock import MagicMock

import pytest

from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
from simple_NER.pipeline import NERPipeline


class MockAhocorasickNER:
    """Mock AhocorasickNER for testing without downloading datasets."""

    def __init__(self, entity_type="TestEntity"):
        self.entity_type = entity_type
        self._words = {}

    def add_word(self, label, word):
        if label not in self._words:
            self._words[label] = []
        self._words[label].append(word)

    def fit(self):
        pass

    def tag(self, text, min_word_len: int = 5):
        """Simple mock: yield matches for any word added."""
        results = []
        for label, words in self._words.items():
            for word in words:
                idx = text.lower().find(word.lower())
                if idx != -1:
                    results.append({
                        "start": idx,
                        "end": idx + len(word) - 1,
                        "word": text[idx : idx + len(word)],
                        "label": label,
                    })
        # Sort by start position
        return sorted(results, key=lambda x: x["start"])


def test_wrapper_initialization():
    """Test AhocorasickAnnotatorWrapper initialization."""
    mock_ner = MockAhocorasickNER(entity_type="Animal")
    wrapper = AhocorasickAnnotatorWrapper(mock_ner, lang="en-us", confidence=0.95)

    assert wrapper.name == "animal"
    assert wrapper.confidence == 0.95
    assert wrapper.lang == "en-us"


def test_wrapper_extract_entities():
    """Test entity extraction from text."""
    mock_ner = MockAhocorasickNER(entity_type="Animal")
    mock_ner.add_word("Animal", "dog")
    mock_ner.add_word("Animal", "cat")
    mock_ner.fit()

    wrapper = AhocorasickAnnotatorWrapper(mock_ner)
    text = "I have a dog and a cat"
    entities = list(wrapper.extract_entities(text))

    assert len(entities) == 2
    assert entities[0].value == "dog"
    assert entities[0].entity_type == "Animal"
    assert entities[1].value == "cat"
    assert entities[1].entity_type == "Animal"


def test_wrapper_in_pipeline():
    """Test wrapper in simple_NER pipeline."""
    pipeline = NERPipeline()

    # Add two mock NER instances
    mock_animals = MockAhocorasickNER(entity_type="Animal")
    mock_animals.add_word("Animal", "dog")
    mock_animals.add_word("Animal", "cat")
    mock_animals.fit()

    mock_colors = MockAhocorasickNER(entity_type="Color")
    mock_colors.add_word("Color", "red")
    mock_colors.add_word("Color", "blue")
    mock_colors.fit()

    pipeline.add_annotator(AhocorasickAnnotatorWrapper(mock_animals))
    pipeline.add_annotator(AhocorasickAnnotatorWrapper(mock_colors))

    text = "The red cat and blue dog"
    entities = pipeline.process(text)

    # Should find all 4 entities
    assert len(entities) == 4

    # Check entity types and values
    entity_dict = {e.value.lower(): e.entity_type for e in entities}
    assert entity_dict["red"] == "Color"
    assert entity_dict["cat"] == "Animal"
    assert entity_dict["blue"] == "Color"
    assert entity_dict["dog"] == "Animal"


def test_entity_data_structure():
    """Test that extracted Entity objects have correct data structure."""
    mock_ner = MockAhocorasickNER(entity_type="Location")
    mock_ner.add_word("Location", "Paris")
    mock_ner.fit()

    wrapper = AhocorasickAnnotatorWrapper(mock_ner, confidence=0.9)
    entities = list(wrapper.extract_entities("I visited Paris"))

    assert len(entities) == 1
    entity = entities[0]

    # Check all properties
    assert entity.value == "Paris"
    assert entity.entity_type == "Location"
    assert entity.confidence == 0.9
    assert "start" in entity.data
    assert "end" in entity.data
    assert entity.data["start"] == 10
    assert entity.data["end"] == 14


def test_case_insensitive_matching():
    """Test that wrapper preserves original casing from text."""
    mock_ner = MockAhocorasickNER(entity_type="Name")
    mock_ner.add_word("Name", "alice")
    mock_ner.fit()

    wrapper = AhocorasickAnnotatorWrapper(mock_ner)

    # Test with different casings
    for text in ["Alice is here", "ALICE is here", "alice is here"]:
        entities = list(wrapper.extract_entities(text))
        assert len(entities) == 1
        assert entities[0].entity_type == "Name"
        # Original casing should be preserved
        assert entities[0].value == text.split()[0]


def test_min_word_len_default_forwarded():
    """Wrapper uses min_word_len=5 by default, matching AhocorasickNER.tag() default."""
    mock_ner = MagicMock()
    mock_ner.tag.return_value = []
    wrapper = AhocorasickAnnotatorWrapper(mock_ner)
    list(wrapper.annotate("hello world"))
    mock_ner.tag.assert_called_once_with("hello world", min_word_len=5)


def test_min_word_len_custom_forwarded():
    """Custom min_word_len is forwarded to tag()."""
    mock_ner = MagicMock()
    mock_ner.tag.return_value = []
    wrapper = AhocorasickAnnotatorWrapper(mock_ner, min_word_len=1)
    list(wrapper.annotate("hi"))
    mock_ner.tag.assert_called_once_with("hi", min_word_len=1)



if __name__ == "__main__":
    pytest.main([__file__, "-v"])
