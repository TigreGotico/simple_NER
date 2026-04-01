"""Wrapper around ahocorasick-ner dataset loaders for use in simple_NER pipelines.

This module provides BaseAnnotator wrappers for AhocorasickNER dataset classes,
enabling them to integrate seamlessly with simple_NER's pipeline architecture.
"""
from __future__ import annotations

import logging
from collections.abc import Generator

from simple_NER import Entity
from simple_NER.annotators.base import BaseAnnotator

logger = logging.getLogger(__name__)


class AhocorasickAnnotatorWrapper(BaseAnnotator):
    """Wrap an AhocorasickNER instance as a BaseAnnotator.

    This allows ahocorasick-ner's pre-built dataset loaders (WikidataEntityNER,
    GenericHFDatasetNER, BC5CDRMedicalNER, etc.) to be used in simple_NER
    pipelines without modification.

    Language support: Depends on wrapped AhocorasickNER instance.

    Example:
        ```python
        from ahocorasick_ner.datasets import WikidataEntityNER
        from simple_NER.annotators.ahocorasick_wrapper import AhocorasickAnnotatorWrapper
        from simple_NER.pipeline import NERPipeline

        # Create ahocorasick instance
        animals = WikidataEntityNER(entity_type="Animal", wikidata_qid="Q729")

        # Wrap it
        wrapper = AhocorasickAnnotatorWrapper(animals, lang="en")

        # Use in pipeline
        pipeline = NERPipeline()
        pipeline.add_annotator(wrapper)

        for entity in pipeline.process("I saw a dog and a cat"):
            print(entity.entity_type, entity.value)
        ```
    """

    def __init__(
        self,
        ahocorasick_ner,
        lang: str = "en-us",
        confidence: float = 0.9,
        *,
        min_word_len: int = 5,
    ) -> None:
        """Initialize wrapper.

        Args:
            ahocorasick_ner: An AhocorasickNER or subclass instance
                (e.g. WikidataEntityNER, GenericHFDatasetNER, BC5CDRMedicalNER).
            lang: Language code (passed to BaseAnnotator for API consistency).
            confidence: Default confidence score for extracted entities.
            min_word_len: Minimum character length for a match to be returned.
                Forwarded to ``AhocorasickNER.tag()``. Default ``5`` matches the
                underlying API default. Pass ``1`` when matching short wordlists
                (e.g. colour names, country codes).
        """
        super().__init__(confidence=confidence, lang=lang)
        self.ner = ahocorasick_ner
        self._min_word_len = min_word_len

    @property
    def name(self) -> str:
        """Return annotator name based on wrapped NER instance."""
        if hasattr(self.ner, "entity_type"):
            return self.ner.entity_type.lower()
        return self.ner.__class__.__name__.lower()

    def annotate(self, text: str) -> Generator[Entity, None, None]:
        """Extract entities using wrapped AhocorasickNER.

        Args:
            text: Input text to analyze.

        Yields:
            Entity objects from the automaton matches.
        """
        for match in self.ner.tag(text, min_word_len=self._min_word_len):
            # AhocorasickNER.tag() yields dicts with:
            # {'start': int, 'end': int, 'word': str, 'label': str}
            yield Entity(
                value=match["word"],
                entity_type=match["label"],
                source_text=text,
                confidence=self.confidence,
                data={
                    "start": match["start"],
                    "end": match["end"],
                },
            )
