"""Base abstract classes for NER annotators.

This module defines the core interfaces that all annotators should implement.
"""
from abc import ABC, abstractmethod
from collections.abc import Generator

from simple_NER import Entity


class Annotator(ABC):
    """Abstract base class for all NER annotators.

    All annotators should inherit from this class and implement the required
    abstract methods. This ensures a consistent interface across all annotators.

    Example:
        ```python
        class MyAnnotator(Annotator):
            @property
            def name(self) -> str:
                return "my_annotator"

            def extract_entities(self, text: str) -> Generator[Entity, None, None]:
                if "hello" in text.lower():
                    yield Entity("hello", "greeting", source_text=text)
        ```
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return unique identifier for this annotator.

        Returns:
            A unique name identifying this annotator type.
        """
        pass

    @abstractmethod
    def extract_entities(
        self, text: str
    ) -> Generator[Entity, None, None]:
        """Extract entities from text.

        Args:
            text: Input text to analyze.

        Yields:
            Entity objects found in the text.
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"


class BaseAnnotator(Annotator):
    """Base class providing common annotator functionality.

    This class implements the boilerplate code common to most annotators,
    reducing duplication. Subclasses only need to implement the specific
    extraction logic.

    Example:
        ```python
        class EmailAnnotator(BaseAnnotator):
            @property
            def name(self) -> str:
                return "email"

            def annotate(self, text: str) -> Generator[Entity, None, None]:
                # Your extraction logic here
                yield Entity(email, "email", source_text=text)
        ```
    """

    def __init__(self, confidence: float = 1.0, lang: str = "en-us") -> None:
        """Initialize base annotator.

        Args:
            confidence: Default confidence score for extracted entities.
            lang: BCP-47 language tag (e.g. ``"de-de"``).  Subclasses that use
                language-sensitive backends (ovos-date-parser, ovos-number-parser)
                forward this to their respective API calls.
        """
        self._confidence = confidence
        self.lang = lang

    @property
    def name(self) -> str:
        """Return annotator name based on class name."""
        return self.__class__.__name__.lower().replace("annotator", "")

    @property
    def confidence(self) -> float:
        """Return default confidence score."""
        return self._confidence

    @abstractmethod
    def annotate(self, text: str) -> Generator[Entity, None, None]:
        """Implement entity extraction logic.

        Args:
            text: Input text to analyze.

        Yields:
            Entity objects found in the text.
        """
        pass

    def extract_entities(
        self, text: str
    ) -> Generator[Entity, None, None]:
        """Extract entities from text (implements Annotator interface).

        Args:
            text: Input text to analyze.

        Yields:
            Entity objects found in the text.
        """
        yield from self.annotate(text)
