"""NER Pipeline for executing multiple annotators with deduplication.

This module provides a pipeline system for running multiple annotators
on the same text and merging/deduplicating the results.
"""
from __future__ import annotations

import asyncio
from collections.abc import Generator
from dataclasses import dataclass

from simple_NER import Entity
from simple_NER.annotators.base import Annotator


@dataclass
class Span:
    """Represents a character span in text."""

    start: int
    end: int

    def overlaps(self, other: Span) -> bool:
        """Check if this span overlaps with another span.

        Args:
            other: Another span to check for overlap.

        Returns:
            True if spans overlap, False otherwise.
        """
        return self.start < other.end and other.start < self.end

    def contains(self, other: Span) -> bool:
        """Check if this span fully contains another span.

        Args:
            other: Another span to check.

        Returns:
            True if this span contains the other, False otherwise.
        """
        return self.start <= other.start and other.end <= self.end

    def __len__(self) -> int:
        return self.end - self.start


class NERPipeline:
    """Execute multiple annotators and deduplicate results.

    The pipeline runs all annotators on the input text and merges results,
    handling overlapping entities based on configurable strategies.

    Example:
        ```python
        from simple_NER.pipeline import NERPipeline
        from simple_NER.annotators.email_ner import EmailNER
        from simple_NER.annotators.names_ner import NamesNER

        pipeline = NERPipeline([
            EmailNER(),
            NamesNER(),
        ])

        entities = pipeline.process("Contact John at john@example.com")
        for ent in entities:
            print(f"{ent.value} ({ent.entity_type})")
        ```
    """

    def __init__(
        self,
        annotators: list[Annotator] | None = None,
        dedup_strategy: str = "keep_all",
    ) -> None:
        """Initialize the NER pipeline.

        Args:
            annotators: List of annotators to run. Can be empty, annotators
                can be added later with add_annotator().
            dedup_strategy: Strategy for handling overlapping entities.
                Options:
                - "keep_all": Keep all entities (no deduplication)
                - "keep_longest": Keep the longest entity when overlaps occur
                - "keep_higher_confidence": Keep entity with higher confidence
                - "keep_first": Keep the first entity found
        """
        self._annotators: list[Annotator] = annotators or []
        self._dedup_strategy = dedup_strategy

    @property
    def annotators(self) -> list[Annotator]:
        """Return list of registered annotators."""
        return self._annotators

    @property
    def dedup_strategy(self) -> str:
        """Return current deduplication strategy."""
        return self._dedup_strategy

    @dedup_strategy.setter
    def dedup_strategy(self, strategy: str) -> None:
        """Set deduplication strategy.

        Args:
            strategy: One of "keep_all", "keep_longest",
                "keep_higher_confidence", "keep_first".
        """
        valid_strategies = {
            "keep_all",
            "keep_longest",
            "keep_higher_confidence",
            "keep_first",
        }
        if strategy not in valid_strategies:
            raise ValueError(
                f"Invalid strategy '{strategy}'. "
                f"Must be one of: {valid_strategies}"
            )
        self._dedup_strategy = strategy

    def add_annotator(self, annotator: Annotator) -> None:
        """Add an annotator to the pipeline.

        Args:
            annotator: Annotator instance to add.
        """
        self._annotators.append(annotator)

    def remove_annotator(self, name: str) -> bool:
        """Remove an annotator by name.

        Args:
            name: Name of annotator to remove.

        Returns:
            True if annotator was found and removed, False otherwise.
        """
        for i, annotator in enumerate(self._annotators):
            if annotator.name == name:
                self._annotators.pop(i)
                return True
        return False

    def process(self, text: str) -> list[Entity]:
        """Process text through all annotators.

        Args:
            text: Input text to analyze.

        Returns:
            List of extracted entities, deduplicated according to strategy.
        """
        all_entities: list[Entity] = []

        for annotator in self._annotators:
            for entity in annotator.extract_entities(text):
                all_entities.append(entity)

        if self._dedup_strategy == "keep_all":
            return all_entities

        return self._deduplicate(all_entities, text)

    def process_generator(self, text: str) -> Generator[Entity, None, None]:
        """Process text and yield entities as they are found.

        This is a memory-efficient alternative to process() that yields
        entities one at a time without deduplication.

        Args:
            text: Input text to analyze.

        Yields:
            Entity objects as they are extracted.
        """
        for annotator in self._annotators:
            yield from annotator.extract_entities(text)

    def _deduplicate(self, entities: list[Entity], text: str) -> list[Entity]:
        """Deduplicate entities based on current strategy.

        Args:
            entities: List of entities to deduplicate.
            text: Original text (for span calculation).

        Returns:
            Deduplicated list of entities.
        """
        if not entities:
            return []

        # Group entities by span
        span_groups: dict[tuple[int, int], list[Entity]] = {}
        for entity in entities:
            for span in entity.spans:
                key = (span[0], span[1])
                if key not in span_groups:
                    span_groups[key] = []
                span_groups[key].append(entity)

        # Apply deduplication strategy within each span group
        result: list[Entity] = []
        for span_entities in span_groups.values():
            if len(span_entities) == 1:
                result.append(span_entities[0])
            else:
                selected = self._select_entity(span_entities)
                if selected:
                    result.append(selected)

        # Sort by start position
        result.sort(key=lambda e: e.spans[0][0] if e.spans else 0)
        return result

    def _select_entity(self, entities: list[Entity]) -> Entity | None:
        """Select one entity from a list based on strategy.

        Args:
            entities: List of overlapping entities.

        Returns:
            Selected entity, or None if list is empty.
        """
        if not entities:
            return None

        if self._dedup_strategy == "keep_longest":
            return max(entities, key=lambda e: len(e.value))

        if self._dedup_strategy == "keep_higher_confidence":
            return max(entities, key=lambda e: e.confidence)

        if self._dedup_strategy == "keep_first":
            return entities[0]

        # Default: keep all (should not reach here)
        return entities[0]

    def __repr__(self) -> str:
        annotator_names = [a.name for a in self._annotators]
        return (
            f"NERPipeline(annotators={annotator_names}, "
            f"strategy={self._dedup_strategy})"
        )


# Async support
async def _process_annotator_async(
    annotator: Annotator, text: str
) -> list[Entity]:
    """Process a single annotator (async wrapper).

    Args:
        annotator: Annotator to run.
        text: Text to process.

    Returns:
        List of extracted entities.
    """
    return list(annotator.extract_entities(text))


class AsyncNERPipeline(NERPipeline):
    """Async version of NERPipeline for concurrent annotator execution.

    This pipeline runs all annotators concurrently using asyncio,
    which can significantly improve throughput for I/O bound annotators
    (e.g., remote APIs).

    Example:
        ```python
        import asyncio
        from simple_NER.pipeline import AsyncNERPipeline

        async def main():
            pipeline = AsyncNERPipeline([email_ner, names_ner])
            entities = await pipeline.process_async("John at john@example.com")
            for ent in entities:
                print(ent.value, ent.entity_type)

        asyncio.run(main())
        ```
    """

    async def process_async(self, text: str) -> list[Entity]:
        """Process text through all annotators concurrently.

        Args:
            text: Input text to analyze.

        Returns:
            List of extracted entities, deduplicated according to strategy.
        """
        # Run all annotators concurrently
        tasks = [
            _process_annotator_async(annotator, text)
            for annotator in self._annotators
        ]
        results = await asyncio.gather(*tasks)

        # Flatten results
        all_entities: list[Entity] = []
        for entity_list in results:
            all_entities.extend(entity_list)

        if self._dedup_strategy == "keep_all":
            return all_entities

        return self._deduplicate(all_entities, text)

    async def process_batch_async(
        self, texts: list[str], max_concurrency: int = 10
    ) -> list[list[Entity]]:
        """Process multiple texts concurrently with limited concurrency.

        Args:
            texts: List of texts to process.
            max_concurrency: Maximum number of concurrent texts.

        Returns:
            List of entity lists, one per input text.
        """
        semaphore = asyncio.Semaphore(max_concurrency)

        async def process_with_semaphore(text: str) -> list[Entity]:
            async with semaphore:
                return await self.process_async(text)

        tasks = [process_with_semaphore(text) for text in texts]
        return await asyncio.gather(*tasks)
