from typing import Any, Callable, Generator

from simple_NER import Entity, SimpleNER


class NERWrapper(SimpleNER):
    """Aggregate multiple NER detector callables into a single interface.

    Each detector is a callable that accepts a ``str`` and yields ``Entity``
    objects.
    """

    def __init__(self) -> None:
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
        """
        for parser in self._detectors:
            for e in parser(text):
                yield e.as_json() if as_json else e
