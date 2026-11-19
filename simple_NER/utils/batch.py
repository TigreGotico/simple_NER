"""Batch processing utilities for simple_NER.

This module provides utilities for processing large volumes of text
efficiently with progress tracking and parallel processing support.
"""
from __future__ import annotations

import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Any, Callable, Generator

from simple_NER import Entity
from simple_NER.pipeline import NERPipeline


class BatchProcessor:
    """Process large batches of text efficiently.

    Args:
        pipeline: NERPipeline to use for processing.
        batch_size: Number of texts to process in each batch.
        max_workers: Maximum number of worker processes/threads.

    Example:
        ```python
        from simple_NER.pipeline import NERPipeline
        from simple_NER.utils.batch import BatchProcessor

        pipeline = NERPipeline([email_ner, names_ner])
        processor = BatchProcessor(pipeline, batch_size=100)

        texts = ["text1", "text2", ...]
        results = processor.process_batch(texts)
        ```
    """

    def __init__(
        self,
        pipeline: NERPipeline,
        batch_size: int = 100,
        max_workers: int | None = None,
    ) -> None:
        """Initialize batch processor.

        Args:
            pipeline: NER pipeline to use.
            batch_size: Texts per batch.
            max_workers: Max parallel workers.
        """
        self.pipeline = pipeline
        self.batch_size = batch_size
        self.max_workers = max_workers or mp.cpu_count()
        self._processed = 0
        self._total = 0

    def _process_chunk(self, args: tuple[list[str], NERPipeline]) -> list[list[Entity]]:
        """Process a chunk of texts.

        Args:
            args: Tuple of (texts, pipeline).

        Returns:
            List of entity lists for each text.
        """
        texts, pipeline = args
        # Note: Pipeline needs to be recreated in each process
        # This is a simplified version
        return [pipeline.process(text) for text in texts]

    def process_batch(
        self,
        texts: list[str],
        use_multiprocessing: bool = False,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> list[list[Entity]]:
        """Process a batch of texts.

        Args:
            texts: List of texts to process.
            use_multiprocessing: Use multiprocessing for CPU-bound work.
            progress_callback: Optional callback(current, total).

        Returns:
            List of entity lists, one per input text.
        """
        self._total = len(texts)
        self._processed = 0

        if len(texts) <= self.batch_size:
            # Single batch
            results = [self.pipeline.process(text) for text in texts]
            self._processed = len(texts)
            if progress_callback:
                progress_callback(self._processed, self._total)
            return results

        # Multiple batches
        results: list[list[Entity]] = []
        batches = [
            texts[i : i + self.batch_size]
            for i in range(0, len(texts), self.batch_size)
        ]

        if use_multiprocessing and len(batches) > 1:
            # Multiprocessing
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                for batch_result in executor.map(
                    self._process_chunk,
                    [(batch, self.pipeline) for batch in batches],
                ):
                    results.extend(batch_result)
                    self._processed += len(batch)
                    if progress_callback:
                        progress_callback(self._processed, self._total)
        else:
            # Single process
            for batch in batches:
                batch_results = [self.pipeline.process(text) for text in batch]
                results.extend(batch_results)
                self._processed += len(batch)
                if progress_callback:
                    progress_callback(self._processed, self._total)

        return results

    def process_generator(
        self,
        text_generator: Generator[str, None, None],
    ) -> Generator[tuple[str, list[Entity]], None, None]:
        """Process texts from a generator.

        Memory-efficient processing for large datasets.

        Args:
            text_generator: Generator yielding texts.

        Yields:
            Tuples of (text, entities).
        """
        for text in text_generator:
            entities = self.pipeline.process(text)
            yield text, entities

    @property
    def progress(self) -> tuple[int, int]:
        """Return current progress (processed, total)."""
        return self._processed, self._total

    def reset_stats(self) -> None:
        """Reset processing statistics."""
        self._processed = 0
        self._total = 0


class StreamingProcessor:
    """Stream processing for continuous text input.

    Example:
        ```python
        from simple_NER.pipeline import NERPipeline
        from simple_NER.utils.batch import StreamingProcessor

        pipeline = NERPipeline([email_ner])
        processor = StreamingProcessor(pipeline)

        for text, entities in processor.process_stream(texts):
            print(f"{text}: {len(entities)} entities")
        ```
    """

    def __init__(
        self,
        pipeline: NERPipeline,
        buffer_size: int = 10,
    ) -> None:
        """Initialize streaming processor.

        Args:
            pipeline: NER pipeline to use.
            buffer_size: Size of processing buffer.
        """
        self.pipeline = pipeline
        self.buffer_size = buffer_size

    def process_stream(
        self,
        text_stream: Generator[str, None, None],
    ) -> Generator[tuple[str, list[Entity]], None, None]:
        """Process a stream of texts.

        Args:
            text_stream: Generator yielding texts.

        Yields:
            Tuples of (text, extracted entities).
        """
        buffer: list[str] = []

        for text in text_stream:
            buffer.append(text)

            if len(buffer) >= self.buffer_size:
                # Process buffer
                for t in buffer:
                    yield t, self.pipeline.process(t)
                buffer.clear()

        # Process remaining
        for text in buffer:
            yield text, self.pipeline.process(text)

    def process_file(
        self,
        file_path: str,
        encoding: str = "utf-8",
    ) -> Generator[tuple[str, list[Entity]], None, None]:
        """Process lines from a file.

        Args:
            file_path: Path to input file.
            encoding: File encoding.

        Yields:
            Tuples of (line, extracted entities).
        """
        def line_generator() -> Generator[str, None, None]:
            with open(file_path, encoding=encoding) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        yield line

        yield from self.process_stream(line_generator())
