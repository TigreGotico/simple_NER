"""Tests for utils/batch.py (BatchProcessor, StreamingProcessor)."""
import tempfile
import unittest

from simple_NER.annotators.email_ner import EmailAnnotator
from simple_NER.pipeline import NERPipeline
from simple_NER.utils.batch import BatchProcessor, StreamingProcessor


def _make_pipeline() -> NERPipeline:
    return NERPipeline([EmailAnnotator()])


class TestBatchProcessor(unittest.TestCase):
    def setUp(self) -> None:
        self.pipeline = _make_pipeline()
        self.processor = BatchProcessor(self.pipeline, batch_size=3)

    def test_single_batch(self) -> None:
        texts = ["contact a@b.com", "no email here", "try x@y.org"]
        results = self.processor.process_batch(texts)
        self.assertEqual(len(results), 3)
        self.assertTrue(any(r for r in results[0]))   # a@b.com found
        self.assertFalse(any(r for r in results[1]))  # no email
        self.assertTrue(any(r for r in results[2]))   # x@y.org found

    def test_multiple_batches(self) -> None:
        texts = [f"user{i}@example.com" for i in range(10)]
        results = self.processor.process_batch(texts)
        self.assertEqual(len(results), 10)
        for r in results:
            self.assertTrue(len(r) > 0)

    def test_progress_callback(self) -> None:
        calls: list[tuple[int, int]] = []
        texts = [f"a{i}@b.com" for i in range(7)]
        self.processor.process_batch(texts, progress_callback=lambda c, t: calls.append((c, t)))
        self.assertTrue(len(calls) > 0)
        self.assertEqual(calls[-1][1], 7)

    def test_progress_property(self) -> None:
        texts = ["a@b.com", "c@d.com"]
        self.processor.process_batch(texts)
        processed, total = self.processor.progress
        self.assertEqual(processed, 2)
        self.assertEqual(total, 2)

    def test_reset_stats(self) -> None:
        self.processor.process_batch(["a@b.com"])
        self.processor.reset_stats()
        self.assertEqual(self.processor.progress, (0, 0))

    def test_process_generator(self) -> None:
        def gen():
            yield "hello a@b.com"
            yield "no match"
            yield "test c@d.org"

        results = list(self.processor.process_generator(gen()))
        self.assertEqual(len(results), 3)
        texts = [r[0] for r in results]
        self.assertIn("hello a@b.com", texts)

    def test_empty_input(self) -> None:
        results = self.processor.process_batch([])
        self.assertEqual(results, [])


class TestStreamingProcessor(unittest.TestCase):
    def setUp(self) -> None:
        self.pipeline = _make_pipeline()
        self.processor = StreamingProcessor(self.pipeline, buffer_size=2)

    def test_process_stream(self) -> None:
        texts = ["a@b.com", "no match", "c@d.org", "e@f.net"]
        results = list(self.processor.process_stream(iter(texts)))
        self.assertEqual(len(results), 4)
        self.assertEqual(results[0][0], "a@b.com")

    def test_process_stream_buffer_boundary(self) -> None:
        # Exactly buffer_size items — tests buffer flush at boundary
        texts = ["x@y.com", "z@w.com"]
        results = list(self.processor.process_stream(iter(texts)))
        self.assertEqual(len(results), 2)

    def test_process_file(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write("contact a@b.com\n\nvisit c@d.org\n")
            path = f.name

        results = list(self.processor.process_file(path))
        self.assertEqual(len(results), 2)  # blank line skipped
        self.assertEqual(results[0][0], "contact a@b.com")


if __name__ == "__main__":
    unittest.main()
