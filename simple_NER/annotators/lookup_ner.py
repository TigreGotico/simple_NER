"""Lookup-based entity extraction from wordlists.

This module provides entity extraction using predefined wordlists
stored in resource files (.entity files).
"""
from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

from simple_NER import Entity
from simple_NER.annotators.base import BaseAnnotator
from simple_NER.utils import resolve_resource_file
from simple_NER.utils.log import LOG

from ahocorasick_ner import AhocorasickNER


class LookUpNER(BaseAnnotator):
    """Extract entities from predefined wordlists.

    This annotator loads entity lists from ``.entity`` files in the
    resource directory and matches them against input text.

    Backend: uses ``ahocorasick-ner`` (Aho-Corasick automaton) when
    available for O(N) single-pass lookup regardless of wordlist size.
    Falls back to per-pattern ``re.search`` if the package is absent.

    Language support: per-language resource files under ``res/<lang>/``.

    Attributes:
        lang: Language code for resource files.
        case_sensitive: Whether matching is case-sensitive.

    Example:
        ```python
        from simple_NER.annotators.lookup_ner import LookUpNER

        ner = LookUpNER()
        for ent in ner.extract_entities("The sky is blue"):
            print(f"{ent.value} -> {ent.entity_type}")
            # "blue" -> "color" (if color.entity exists)
        ```
    """

    def __init__(
        self,
        lang: str = "en-us",
        case_sensitive: bool = False,
        confidence: float = 1.0,
        label_confidence: dict[str, float] | None = None,
    ) -> None:
        """Initialize LookUpNER.

        Args:
            lang: Language code for resource files.
            case_sensitive: Whether matching is case-sensitive.
            confidence: Default confidence score for entities.
            label_confidence: Optional per-label confidence overrides.
                Keys are label names; values override the flat ``confidence``
                for that label.  Missing labels fall back to ``confidence``.
        """
        super().__init__(confidence=confidence, lang=lang)
        self._case_sensitive = case_sensitive
        self._label_confidence: dict[str, float] = label_confidence or {}
        self.entities: dict[str, list[str]] = {}
        self._ac: AhocorasickNER | None = None
        self._load_entities()
        self._build_automaton()

    @property
    def name(self) -> str:
        """Return annotator name."""
        return "lookup"

    def _load_entities(self) -> None:
        """Load entity wordlists from resource files."""
        resource_dir = resolve_resource_file(self.lang)

        if resource_dir is None:
            # Try to find the res directory
            lang_key = self.lang.lower().split("-")[0]
            res_dir = Path(__file__).parent.parent / "res" / lang_key
            if res_dir.exists():
                resource_dir = str(res_dir)
            else:
                LOG.warning(f"Resource directory not found for language: {self.lang}")
                return

        folder = Path(resource_dir)
        if not folder.exists():
            LOG.warning(f"Resource folder does not exist: {folder}")
            return

        loaded = 0
        for entity_file in folder.iterdir():
            if not entity_file.suffix == ".entity":
                continue

            try:
                entity_name = entity_file.stem
                with open(entity_file, encoding="utf-8") as f:
                    entities = [
                        line.strip().lower()
                        for line in f
                        if line.strip()
                    ]
                    self.entities[entity_name] = entities
                    loaded += 1
            except (OSError, UnicodeDecodeError) as e:
                LOG.error(f"Error loading {entity_file}: {e}")

        if loaded > 0:
            LOG.info(f"Loaded {loaded} entity types from {folder}")
        else:
            LOG.warning(f"No entity files found in {folder}")

    def _build_automaton(self) -> None:
        """Build (or rebuild) the Aho-Corasick automaton from ``self.entities``."""
        if not self.entities:
            self._ac = None
            return
        ac = AhocorasickNER(case_sensitive=self._case_sensitive)
        for label, wordlist in self.entities.items():
            for word in wordlist:
                if word:
                    ac.add_word(label, word)
        ac.fit()
        self._ac = ac
        LOG.debug(f"LookUpNER: Aho-Corasick automaton built with {sum(len(v) for v in self.entities.values())} patterns")

    def annotate(self, text: str) -> Generator[Entity, None, None]:
        """Extract entities from text using Aho-Corasick wordlist lookup.

        Args:
            text: Input text to analyze.

        Yields:
            Entity objects for matched wordlist entries.
        """
        if not self.entities or self._ac is None:
            return

        for match in self._ac.tag(text, min_word_len=1):
            conf = self._label_confidence.get(match["label"], self.confidence)
            yield Entity(
                match["word"],
                match["label"],
                source_text=text,
                confidence=conf,
                data={"source": "wordlist", "language": self.lang,
                      "start": match["start"], "end": match["end"]},
            )

    def add_wordlist(self, label: str, words: list[str]) -> None:
        """Add a custom wordlist at runtime.

        Args:
            label: Entity type label for the wordlist.
            words: List of words to match.
        """
        self.entities[label] = words
        self._build_automaton()
        LOG.debug(f"Added wordlist '{label}' with {len(words)} words")

    def remove_wordlist(self, label: str) -> bool:
        """Remove a wordlist by label.

        Args:
            label: Entity type label to remove.

        Returns:
            True if wordlist was removed, False if not found.
        """
        if label in self.entities:
            del self.entities[label]
            self._build_automaton()
            return True
        return False

    @property
    def loaded_types(self) -> list[str]:
        """Return list of loaded entity types."""
        return list(self.entities.keys())


if __name__ == "__main__":
    from pprint import pprint

    print("=" * 60)
    print("LOOKUP NER")
    print("=" * 60)

    ner = LookUpNER()

    print(f"\nLoaded entity types: {ner.loaded_types}")
    print("-" * 60)

    text = "The sky is blue and grass is green"
    print(f"Text: {text}")
    print("-" * 60)

    for r in ner.extract_entities(text):
        print(f"{r.value} -> {r.entity_type}")
        pprint(r.as_json())
