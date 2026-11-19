"""Unit tests for async pipeline functionality."""
import asyncio

import pytest

from simple_NER import Entity
from simple_NER.annotators.base import BaseAnnotator
from simple_NER.pipeline import AsyncNERPipeline, NERPipeline


# ---------------------------------------------------------------------------
# Helper Annotators for Testing
# ---------------------------------------------------------------------------

class SlowAnnotator(BaseAnnotator):
    """Slow annotator for testing async concurrency."""

    def __init__(self, delay: float = 0.1, name: str = "slow") -> None:
        super().__init__()
        self._delay = delay
        self._annotator_name = name

    @property
    def name(self) -> str:
        return self._annotator_name

    def annotate(self, text: str):
        """Simulate slow annotation (blocking for test purposes)."""
        import time
        time.sleep(self._delay)
        yield Entity("result", "test", source_text=text)


class FastAnnotator(BaseAnnotator):
    """Fast annotator for testing."""

    @property
    def name(self) -> str:
        return "fast"

    def annotate(self, text: str):
        """Fast annotation."""
        yield Entity("fast_result", "test", source_text=text)


# ---------------------------------------------------------------------------
# AsyncNERPipeline Tests
# ---------------------------------------------------------------------------

class TestAsyncNERPipeline:
    """Tests for AsyncNERPipeline."""

    def test_async_pipeline_single_text(self):
        """Test async pipeline with single text."""
        async def run_test():
            pipeline = AsyncNERPipeline([FastAnnotator()])
            entities = await pipeline.process_async("test text")
            return entities

        entities = asyncio.run(run_test())
        assert len(entities) == 1
        assert entities[0].value == "fast_result"

    def test_async_pipeline_multiple_annotators(self):
        """Test async pipeline with multiple annotators."""
        async def run_test():
            pipeline = AsyncNERPipeline([
                FastAnnotator(),
                FastAnnotator(),
            ])
            entities = await pipeline.process_async("test")
            return entities

        entities = asyncio.run(run_test())
        # Both annotators should run
        assert len(entities) == 2

    def test_async_vs_sync_results(self):
        """Test that async and sync pipelines produce same results."""
        text = "test text"

        # Sync pipeline
        sync_pipeline = NERPipeline([FastAnnotator()])
        sync_results = sync_pipeline.process(text)

        # Async pipeline
        async def run_async():
            async_pipeline = AsyncNERPipeline([FastAnnotator()])
            return await async_pipeline.process_async(text)

        async_results = asyncio.run(run_async())

        # Results should be equivalent
        assert len(sync_results) == len(async_results)
        assert sync_results[0].value == async_results[0].value

    def test_async_batch_processing(self):
        """Test async batch processing."""
        async def run_test():
            pipeline = AsyncNERPipeline([FastAnnotator()])
            texts = ["text1", "text2", "text3"]
            results = await pipeline.process_batch_async(texts)
            return results

        results = asyncio.run(run_test())
        assert len(results) == 3
        for result_list in results:
            assert len(result_list) == 1

    def test_async_concurrency(self):
        """Test that async pipeline runs all annotators."""
        async def run_test():
            # Create 3 annotators
            annotators = [SlowAnnotator(delay=0.05, name=f"slow{i}") for i in range(3)]
            pipeline = AsyncNERPipeline(annotators)

            entities = await pipeline.process_async("test")
            return entities

        entities = asyncio.run(run_test())

        # All annotators should run
        assert len(entities) == 3

    def test_async_max_concurrency(self):
        """Test batch processing with max concurrency limit."""
        async def run_test():
            pipeline = AsyncNERPipeline([FastAnnotator()])
            texts = [f"text{i}" for i in range(10)]

            # Process with max 3 concurrent
            results = await pipeline.process_batch_async(texts, max_concurrency=3)
            return results

        results = asyncio.run(run_test())
        assert len(results) == 10

    def test_async_empty_pipeline(self):
        """Test async pipeline with no annotators."""
        async def run_test():
            pipeline = AsyncNERPipeline([])
            entities = await pipeline.process_async("test")
            return entities

        entities = asyncio.run(run_test())
        assert len(entities) == 0

    def test_async_deduplication(self):
        """Test that async pipeline applies deduplication."""
        async def run_test():
            # Create pipeline with keep_longest strategy
            pipeline = AsyncNERPipeline(
                [FastAnnotator()],
                dedup_strategy="keep_all"
            )
            entities = await pipeline.process_async("test")
            return entities

        entities = asyncio.run(run_test())
        assert len(entities) >= 1


# ---------------------------------------------------------------------------
# Integration Tests
# ---------------------------------------------------------------------------

class TestAsyncIntegration:
    """Integration tests for async functionality."""

    def test_async_with_real_annotators(self):
        """Test async pipeline with real annotators."""
        from simple_NER.annotators.email_ner import EmailAnnotator

        async def run_test():
            pipeline = AsyncNERPipeline([EmailAnnotator()])
            text = "Contact test@example.com"
            entities = await pipeline.process_async(text)
            return entities

        entities = asyncio.run(run_test())
        assert len(entities) == 1
        assert "example.com" in entities[0].value

    def test_async_factory_pattern(self):
        """Test creating async pipeline from factory."""
        from simple_NER.annotators.factory import get_annotator

        async def run_test():
            email_ner = get_annotator("email")
            pipeline = AsyncNERPipeline([email_ner])
            entities = await pipeline.process_async("Email: test@example.com")
            return entities

        entities = asyncio.run(run_test())
        assert len(entities) == 1
