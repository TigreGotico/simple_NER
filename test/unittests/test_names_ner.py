"""Tests for NamesNER sentence-position heuristic (S-001)."""
import unittest

from simple_NER.annotators.names_ner import NamesNER


class TestNamesNERHeuristic(unittest.TestCase):
    """Verify that sentence-boundary heuristic reduces false positives."""

    def setUp(self) -> None:
        self.ner = NamesNER(confidence_threshold=0.65)

    def _entities(self, text: str) -> list[str]:
        return [e.value for e in self.ner.extract_entities(text)]

    # --- sentence-start suppression ---

    def test_sentence_start_single_word_suppressed(self) -> None:
        """'Send' at sentence start should be below threshold (confidence 0.55)."""
        results = self._entities("Send me the report.")
        self.assertNotIn("Send", results)

    def test_sentence_start_after_period(self) -> None:
        """Single word after '.' is sentence-initial and should be suppressed."""
        results = self._entities("We finished. Meeting is tomorrow.")
        self.assertNotIn("Meeting", results)

    def test_sentence_start_after_exclamation(self) -> None:
        results = self._entities("Done! Great work everyone.")
        self.assertNotIn("Great", results)

    # --- mid-sentence proper nouns retained ---

    def test_mid_sentence_proper_noun_kept(self) -> None:
        """Mid-sentence capitalised word should score 0.80 and be kept."""
        results = self._entities("I met Alice yesterday.")
        self.assertIn("Alice", results)

    def test_mid_sentence_confidence(self) -> None:
        entities = list(self.ner.extract_entities("I met Alice yesterday."))
        alice = next((e for e in entities if e.value == "Alice"), None)
        self.assertIsNotNone(alice)
        self.assertAlmostEqual(alice.confidence, 0.80)

    # --- compound names always high confidence ---

    def test_compound_name_at_sentence_start_kept(self) -> None:
        """Multi-word name at sentence start still scores 0.85."""
        results = self._entities("John Doe arrived late.")
        self.assertIn("John Doe", results)

    def test_compound_name_confidence(self) -> None:
        entities = list(self.ner.extract_entities("John Doe arrived late."))
        jd = next((e for e in entities if e.value == "John Doe"), None)
        self.assertIsNotNone(jd)
        self.assertAlmostEqual(jd.confidence, 0.85)

    # --- sentence_initial metadata ---

    def test_sentence_initial_flag_mid_sentence(self) -> None:
        entities = list(self.ner.extract_entities("I met Alice yesterday."))
        alice = next((e for e in entities if e.value == "Alice"), None)
        self.assertIsNotNone(alice)
        self.assertFalse(alice.data.get("sentence_initial"))

    def test_position_zero_is_sentence_initial(self) -> None:
        """_at_sentence_start must return True for offset 0."""
        self.assertTrue(NamesNER._at_sentence_start("Hello world", 0))

    def test_mid_text_is_not_sentence_initial(self) -> None:
        self.assertFalse(NamesNER._at_sentence_start("hello Alice there", 6))


if __name__ == "__main__":
    unittest.main()
