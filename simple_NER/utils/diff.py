from collections.abc import Generator
from difflib import SequenceMatcher
from typing import Tuple


class TextDiff:
    """Create word-level diffs between two text snippets."""

    def __init__(self, source: str, target: str) -> None:
        """Initialise with source and target texts.

        Args:
            source: Original text.
            target: Modified text.
        """
        self.source: list[str] = source.split()
        self.target: list[str] = target.split()
        self.deleteCount: int = 0
        self.insertCount: int = 0
        self.replaceCount: int = 0
        self.cruncher: SequenceMatcher = SequenceMatcher(None, self.source, self.target)

    def dif_tags(self) -> Generator[Tuple[Tuple[str, str, str], Tuple[int, int], Tuple[int, int]], None, None]:
        """Yield tagged word-level diff operations.

        Yields:
            Tuples of ``((tag, deleted, inserted), (alo, ahi), (blo, bhi))``
            where *tag* is one of ``'replace'``, ``'delete'``, or ``'insert'``.
        """
        for tag, alo, ahi, blo, bhi in self.cruncher.get_opcodes():
            inserted = ""
            deleted = ""
            if tag == 'replace':
                deleted = " ".join(self.source[alo:ahi])
                inserted = " ".join(self.target[blo:bhi])
                yield (tag, deleted, inserted), (alo, ahi), (blo, bhi)
                self.replaceCount += 1
            elif tag == 'delete':
                # Text deleted
                deleted = " ".join(self.source[alo:ahi])
                self.deleteCount += 1
                yield (tag, deleted, inserted), (alo, ahi), (blo, bhi)
            elif tag == 'insert':
                # Text inserted
                inserted = " ".join(self.target[alo:ahi])
                self.insertCount += 1
                yield (tag, deleted, inserted), (alo, ahi), (blo, bhi)


if __name__ == "__main__":
    ch1 = """Today, a generation raised in the shadows of the Cold
     War assumes new responsibilities in a world warmed by the sunshine of
     freedom"""

    ch2 = """Today, pythonistas raised in the shadows of the Cold
     War assumes responsibilities in a world warmed by the sunshine of
     spam and freedom"""

    differ = TextDiff(ch1, ch2)

    for tag, span in differ.dif_tags():
        print(tag, span)
        print(ch2.split()[span[0]:span[1]])
