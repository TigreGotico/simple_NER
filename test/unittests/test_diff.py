"""Tests for utils/diff.py (TextDiff)."""
import unittest

from simple_NER.utils.diff import TextDiff


class TestTextDiff(unittest.TestCase):
    def test_replace(self) -> None:
        d = TextDiff("hello world", "hello python")
        ops = list(d.dif_tags())
        tags = [o[0][0] for o in ops]
        self.assertIn("replace", tags)
        self.assertEqual(d.replaceCount, 1)
        self.assertEqual(d.deleteCount, 0)
        self.assertEqual(d.insertCount, 0)

    def test_delete(self) -> None:
        d = TextDiff("hello world foo", "hello world")
        ops = list(d.dif_tags())
        tags = [o[0][0] for o in ops]
        self.assertIn("delete", tags)
        self.assertEqual(d.deleteCount, 1)

    def test_insert(self) -> None:
        d = TextDiff("hello world", "hello world foo")
        ops = list(d.dif_tags())
        tags = [o[0][0] for o in ops]
        self.assertIn("insert", tags)
        self.assertEqual(d.insertCount, 1)

    def test_equal_texts_no_ops(self) -> None:
        d = TextDiff("same text", "same text")
        ops = list(d.dif_tags())
        self.assertEqual(ops, [])
        self.assertEqual(d.replaceCount, 0)
        self.assertEqual(d.deleteCount, 0)
        self.assertEqual(d.insertCount, 0)

    def test_replace_payload(self) -> None:
        d = TextDiff("foo bar", "foo baz")
        ops = list(d.dif_tags())
        replace_ops = [o for o in ops if o[0][0] == "replace"]
        self.assertEqual(len(replace_ops), 1)
        tag, deleted, inserted = replace_ops[0][0]
        self.assertEqual(deleted, "bar")
        self.assertEqual(inserted, "baz")

    def test_delete_payload(self) -> None:
        d = TextDiff("a b c", "a c")
        ops = list(d.dif_tags())
        delete_ops = [o for o in ops if o[0][0] == "delete"]
        self.assertEqual(len(delete_ops), 1)
        _, deleted, _ = delete_ops[0][0]
        self.assertEqual(deleted, "b")

    def test_spans_returned(self) -> None:
        d = TextDiff("a b c", "a x c")
        ops = list(d.dif_tags())
        for op, src_span, tgt_span in ops:
            self.assertIsInstance(src_span, tuple)
            self.assertIsInstance(tgt_span, tuple)
            self.assertEqual(len(src_span), 2)


if __name__ == "__main__":
    unittest.main()
