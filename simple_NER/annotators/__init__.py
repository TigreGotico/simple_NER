"""NER annotators package.

This package provides various named entity recognition annotators that can be
used individually or combined using NERWrapper.

Note:
    For new code, consider using the BaseAnnotator ABC from
    simple_NER.annotators.base for a more consistent interface.
"""
from collections.abc import Callable, Generator
from typing import Any

from simple_NER import Entity, SimpleNER


class NERWrapper(SimpleNER):
    """Aggregate multiple NER detector callables into a single interface.

    Each detector is a callable that accepts a ``str`` and yields ``Entity``
    objects.

    Note:
        For new annotators, consider inheriting from BaseAnnotator instead
        of using NERWrapper directly.

    Example:
        ```python
        from simple_NER.annotators import NERWrapper
        from simple_NER import Entity

        def custom_detector(text: str):
            if "hello" in text.lower():
                yield Entity("hello", "greeting", source_text=text)

        wrapper = NERWrapper()
        wrapper.add_detector(custom_detector)

        for entity in wrapper.extract_entities("hello world"):
            print(entity.value, entity.entity_type)
        ```
    """

    def __init__(self) -> None:
        """Initialize NERWrapper."""
        super().__init__()
        self._detectors: list[Callable[[str], Any]] = []

    def add_detector(self, parser: Callable[[str], Any]) -> None:
        """Register an NER detector callable.

        Args:
            parser: Callable ``(text: str) -> Iterable[Entity]``.
        """
        self._detectors.append(parser)

    def extract_entities(
        self, text: str, as_json: bool = False
    ) -> Generator[Entity | dict[str, Any], None, None]:
        """Yield entities from all registered detectors.

        Args:
            text: Input string.
            as_json: If ``True`` yield ``dict`` representations.

        Yields:
            Entity objects or dicts from all detectors.
        """
        for parser in self._detectors:
            for e in parser(text):
                yield e.as_json() if as_json else e
