"""Factory for creating NER annotators.

This module provides a factory pattern for creating annotators
by name, making it easy to configure and instantiate annotators
dynamically.
"""
from __future__ import annotations

from typing import Any

from simple_NER.annotators.base import Annotator
from simple_NER.utils.log import LOG

# Registry of available annotators
_ANNOTATOR_REGISTRY: dict[str, type[Annotator]] = {}


def register_annotator(name: str, annotator_class: type[Annotator]) -> None:
    """Register an annotator class in the factory.

    Args:
        name: Unique name for the annotator.
        annotator_class: Annotator class to register.

    Example:
        ```python
        from simple_NER.annotators.base import BaseAnnotator
        from simple_NER.annotators.factory import register_annotator

        class MyAnnotator(BaseAnnotator):
            def annotate(self, text):
                yield Entity("test", "test", source_text=text)

        register_annotator("my_annotator", MyAnnotator)
        ```
    """
    _ANNOTATOR_REGISTRY[name.lower()] = annotator_class
    LOG.debug(f"Registered annotator: {name}")


def get_annotator(name: str, **kwargs: Any) -> Annotator:
    """Get an annotator instance by name.

    Args:
        name: Name of the annotator to create.
        **kwargs: Arguments to pass to the annotator constructor.

    Returns:
        Annotator instance.

    Raises:
        ValueError: If annotator name is not registered.

    Example:
        ```python
        from simple_NER.annotators.factory import get_annotator

        email_ner = get_annotator("email")
        names_ner = get_annotator("names", confidence=0.9)
        ```
    """
    name_lower = name.lower()
    if name_lower not in _ANNOTATOR_REGISTRY:
        available = ", ".join(sorted(_ANNOTATOR_REGISTRY.keys()))
        raise ValueError(
            f"Unknown annotator: {name}. "
            f"Available annotators: {available}"
        )

    annotator_class = _ANNOTATOR_REGISTRY[name_lower]
    try:
        return annotator_class(**kwargs)
    except TypeError as e:
        LOG.error(f"Error creating annotator '{name}': {e}")
        raise


def list_available_annotators() -> list[str]:
    """List all registered annotator names.

    Returns:
        List of available annotator names.
    """
    return sorted(_ANNOTATOR_REGISTRY.keys())


def create_pipeline(
    annotator_names: list[str],
    dedup_strategy: str = "keep_all",
    **kwargs: Any,
) -> Any:
    """Create a NERPipeline with multiple annotators.

    Args:
        annotator_names: List of annotator names to include.
        dedup_strategy: Deduplication strategy for the pipeline.
        **kwargs: Default arguments to pass to all annotators.

    Returns:
        Configured NERPipeline instance.

    Raises:
        ValueError: If any annotator name is not registered.

    Example:
        ```python
        from simple_NER.annotators.factory import create_pipeline

        pipeline = create_pipeline(
            ["email", "names", "locations"],
            dedup_strategy="keep_higher_confidence"
        )
        entities = pipeline.process("John lives in London")
        ```
    """
    from simple_NER.pipeline import NERPipeline

    annotators = []
    for name in annotator_names:
        try:
            annotator = get_annotator(name, **kwargs)
            annotators.append(annotator)
        except ValueError as e:
            LOG.warning(f"Skipping annotator '{name}': {e}")

    if not annotators:
        raise ValueError("No valid annotators could be created")

    return NERPipeline(annotators, dedup_strategy=dedup_strategy)


# Auto-register built-in annotators
def _register_builtin_annotators() -> None:
    """Register all built-in annotators."""
    # Email
    try:
        from simple_NER.annotators.email_ner import EmailAnnotator, EmailNER

        register_annotator("email", EmailAnnotator)
        # Also register EmailNER for backward compatibility
        if EmailNER is not EmailAnnotator:
            register_annotator("email_regex", EmailNER)
    except ImportError as e:
        LOG.debug(f"Could not register EmailNER: {e}")

    # Names
    try:
        from simple_NER.annotators.names_ner import NamesNER

        register_annotator("names", NamesNER)
    except ImportError as e:
        LOG.debug(f"Could not register NamesNER: {e}")

    # Locations
    try:
        from simple_NER.annotators.locations_ner import LocationNER

        register_annotator("locations", LocationNER)
        register_annotator("countries", LocationNER)
        register_annotator("cities", LocationNER)
    except ImportError as e:
        LOG.debug(f"Could not register LocationNER: {e}")

    # Temporal (datetime/duration)
    try:
        from simple_NER.annotators.temporal_ner import TemporalNER

        register_annotator("temporal", TemporalNER)
        register_annotator("datetime", TemporalNER)
        register_annotator("duration", TemporalNER)
    except ImportError as e:
        LOG.debug(f"Could not register TemporalNER: {e}")

    # Numbers
    try:
        from simple_NER.annotators.numbers_ner import NumberNER

        register_annotator("numbers", NumberNER)
        register_annotator("written_numbers", NumberNER)
    except ImportError as e:
        LOG.debug(f"Could not register NumberNER: {e}")

    # Lookup
    try:
        from simple_NER.annotators.lookup_ner import LookUpNER

        register_annotator("lookup", LookUpNER)
        register_annotator("wordlist", LookUpNER)
    except ImportError as e:
        LOG.debug(f"Could not register LookUpNER: {e}")

    # URL
    try:
        from simple_NER.annotators.url_ner import URLAnnotator

        register_annotator("url", URLAnnotator)
        register_annotator("urls", URLAnnotator)
    except ImportError as e:
        LOG.debug(f"Could not register URLAnnotator: {e}")

    # Phone
    try:
        from simple_NER.annotators.phone_ner import PhoneAnnotator

        register_annotator("phone", PhoneAnnotator)
        register_annotator("phone_number", PhoneAnnotator)
    except ImportError as e:
        LOG.debug(f"Could not register PhoneAnnotator: {e}")

    # Currency
    try:
        from simple_NER.annotators.currency_ner import CurrencyAnnotator

        register_annotator("currency", CurrencyAnnotator)
        register_annotator("money", CurrencyAnnotator)
    except ImportError as e:
        LOG.debug(f"Could not register CurrencyAnnotator: {e}")

    # Organization
    try:
        from simple_NER.annotators.organization_ner import OrganizationAnnotator

        register_annotator("organization", OrganizationAnnotator)
        register_annotator("org", OrganizationAnnotator)
        register_annotator("company", OrganizationAnnotator)
    except ImportError as e:
        LOG.debug(f"Could not register OrganizationAnnotator: {e}")

    # Hashtag
    try:
        from simple_NER.annotators.hashtag_ner import HashtagAnnotator

        register_annotator("hashtag", HashtagAnnotator)
        register_annotator("hashtags", HashtagAnnotator)
        register_annotator("tag", HashtagAnnotator)
    except ImportError as e:
        LOG.debug(f"Could not register HashtagAnnotator: {e}")

    # Date
    try:
        from simple_NER.annotators.date_ner import DateAnnotator

        register_annotator("date", DateAnnotator)
        register_annotator("dates", DateAnnotator)
    except ImportError as e:
        LOG.debug(f"Could not register DateAnnotator: {e}")

    LOG.info(
        f"Registered {len(_ANNOTATOR_REGISTRY)} annotators: "
        f"{', '.join(sorted(_ANNOTATOR_REGISTRY.keys()))}"
    )


# Auto-register on module import
_register_builtin_annotators()


if __name__ == "__main__":
    print("Available Annotators:")
    print("-" * 40)
    for name in list_available_annotators():
        print(f"  - {name}")

    print("\n" + "=" * 60)
    print("Testing Factory")
    print("=" * 60)

    # Test creating individual annotators
    print("\nCreating email annotator...")
    email_ner = get_annotator("email")
    print(f"  Created: {email_ner}")

    print("\nCreating names annotator...")
    names_ner = get_annotator("names")
    print(f"  Created: {names_ner}")

    print("\n" + "=" * 60)
    print("Testing Pipeline Creation")
    print("=" * 60)

    # Test creating a pipeline
    try:
        pipeline = create_pipeline(
            ["email", "names"],
            dedup_strategy="keep_all",
        )
        print(f"\nCreated pipeline: {pipeline}")

        # Test the pipeline
        text = "John Doe can be reached at john@example.com"
        print(f"\nProcessing: {text}")
        print("-" * 60)

        entities = pipeline.process(text)
        for ent in entities:
            print(f"  {ent.value} -> {ent.entity_type}")

    except Exception as e:
        print(f"Pipeline test skipped: {e}")
