"""Lookup-based entity extraction from wordlists.

This module provides entity extraction using predefined wordlists
stored in resource files (.entity files).
"""
from __future__ import annotations

import re
from collections.abc import Generator
from pathlib import Path

from simple_NER import Entity
from simple_NER.annotators.base import BaseAnnotator
from simple_NER.utils import resolve_resource_file
from simple_NER.utils.log import LOG


class LookUpNER(BaseAnnotator):
    """Extract entities from predefined wordlists.

    This annotator loads entity lists from .entity files in the
    resource directory and matches them against input text.

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
    ) -> None:
        """Initialize LookUpNER.

        Args:
            lang: Language code for resource files.
            case_sensitive: Whether matching is case-sensitive.
            confidence: Default confidence score for entities.
        """
        super().__init__(confidence=confidence)
        self.lang = lang
        self._case_sensitive = case_sensitive
        self.entities: dict[str, list[str]] = {}
        self._load_entities()

    @property
    def name(self) -> str:
        """Return annotator name."""
        return "lookup"

    def _load_entities(self) -> None:
        """Load entity wordlists from resource files."""
        resource_dir = resolve_resource_file(self.lang)

        if resource_dir is None:
            # Try to find the res directory
            res_dir = Path(__file__).parent.parent / "res" / self.lang
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

    def annotate(self, text: str) -> Generator[Entity, None, None]:
        """Extract entities from text using wordlist lookup.

        Args:
            text: Input text to analyze.

        Yields:
            Entity objects for matched wordlist entries.
        """
        if not self.entities:
            return

        search_text = text if self._case_sensitive else text.lower()

        for label, wordlist in self.entities.items():
            for word in wordlist:
                if not word:  # Skip empty strings
                    continue

                search_word = word if self._case_sensitive else word.lower()

                # Use word boundary matching
                pattern = r"\b" + re.escape(search_word) + r"\b"
                if re.search(pattern, search_text):
                    yield Entity(
                        word,
                        label,
                        source_text=text,
                        confidence=self.confidence,
                        data={"source": "wordlist", "language": self.lang},
                    )

    def add_wordlist(self, label: str, words: list[str]) -> None:
        """Add a custom wordlist at runtime.

        Args:
            label: Entity type label for the wordlist.
            words: List of words to match.
        """
        self.entities[label] = words
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
