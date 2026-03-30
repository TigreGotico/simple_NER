import re
from typing import Any, Generator, Iterator
from quebra_frases import find_spans


def find_all(a_str: str, sub: str) -> Iterator[int]:
    """Yield all start positions of *sub* in *a_str* (non-overlapping)."""
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1:
            return
        yield start
        start += len(sub)


class Entity:
    """A single named-entity match with span, confidence, and metadata.

    Attributes:
        data: Arbitrary key/value metadata supplied by the annotator.
            Nested dicts are accessible as dot-notation attributes.
        ignore_case: When ``True`` span lookup is case-insensitive.
    """

    _name: str = "entity"

    def __init__(
        self,
        value: str,
        entity_type: str | None = None,
        source_text: str = "",
        rules: Any = None,
        confidence: float = 1,
        data: dict[str, Any] | None = None,
        ignore_case: bool = True,
    ) -> None:
        """Initialise an Entity.

        Args:
            value: The surface form extracted from *source_text*.
            entity_type: Label for this entity (e.g. ``"person"``).
            source_text: The full input text the entity was extracted from.
            rules: Rule string(s) that produced this entity.
            confidence: Extraction confidence in ``[0, 1]``.
            data: Arbitrary metadata dict; nested dicts become sub-attributes.
            ignore_case: Whether span lookup is case-insensitive.
        """
        if entity_type:
            self._name = entity_type
        self._value = value
        self._source_text = source_text
        self.ignore_case = ignore_case
        if rules and not isinstance(rules, (list, tuple)):
            rules = [rules]
        self._rules: list[Any] = rules or []
        self._confidence = confidence
        self.data: dict[str, Any] = data or {}

        # Expose top-level metadata keys as direct attributes.
        # Nested dicts are flattened into a plain namespace object rather than
        # dynamically created subclasses (replaces types.new_class() usage).
        for k, v in self.data.items():
            if isinstance(v, dict):
                ns = _SimpleNamespace(k, v)
                setattr(self, k, ns)
            elif k == "value":
                # Avoid shadowing the .value property
                setattr(self, "data_value", v)
            else:
                setattr(self, k, v)

    @property
    def spans(self) -> list[tuple[int, int]]:
        """Return ``(start, end)`` character spans of *value* in *source_text*."""
        if self.ignore_case:
            spans = find_spans(self.source_text.lower(), [self.value.lower()])
        else:
            spans = find_spans(self.source_text, [self.value])
        return [(s[0], s[1]) for s in spans]

    @property
    def indexes(self) -> list[int]:
        """Return start-character indexes of each occurrence."""
        return [i[0] for i in self.spans]

    @property
    def occurrence_number(self) -> int:
        """Return how many times *value* appears in *source_text*."""
        return len(self.spans)

    @property
    def confidence(self) -> float:
        """Extraction confidence in ``[0, 1]``."""
        return self._confidence

    @property
    def rules(self) -> list[Any]:
        """Rules that produced this entity."""
        return self._rules

    @property
    def entity_type(self) -> str:
        """Entity label (e.g. ``"person"``)."""
        return self._name

    @property
    def value(self) -> str:
        """Surface form extracted from *source_text*."""
        return self._value

    @property
    def source_text(self) -> str:
        """Full input text this entity was extracted from."""
        return self._source_text

    def as_json(self) -> dict[str, Any]:
        """Serialise the entity to a JSON-safe dict."""
        return {
            "entity_type": self.entity_type,
            "spans": self.spans,
            "value": self.value,
            "source_text": self.source_text,
            "confidence": self.confidence,
            "data": self.data,
            "rules": [r.as_json() if hasattr(r, "as_json") else r for r in self.rules],
        }

    def __repr__(self) -> str:
        return f"{self.entity_type}:{self.value}"


class _SimpleNamespace:
    """Lightweight namespace used to expose nested metadata dicts as attributes.

    Replaces the previous ``types.new_class()`` approach that created anonymous
    ``Entity`` subclasses at runtime.
    """

    def __init__(self, name: str, attrs: dict[str, Any]) -> None:
        self._name = name
        for k, v in attrs.items():
            setattr(self, k, v)

    def __repr__(self) -> str:
        return self._name


class SimpleNER:
    """Keyword-example based NER using whole-word regex matching."""

    def __init__(self) -> None:
        self._examples: dict[str, list[Entity]] = {}

    def is_match(self, text: str, entity: str | Entity) -> bool:
        """Return ``True`` if *entity* (or any example for it) appears in *text*.

        Args:
            text: Input string to search.
            entity: Either an entity-type name (``str``) or an ``Entity`` object.
        """
        entities: list[Entity] = []
        if isinstance(entity, str):
            entities = self._examples[entity]
        if isinstance(entity, Entity):
            entities = [entity]
        for ent in entities:
            if re.findall(r'\b' + ent.value.lower() + r"\b", text.lower()):
                return True
        return False

    @property
    def examples(self) -> dict[str, list[Entity]]:
        """Registered entity-type → example entities mapping."""
        return self._examples

    def add_entity_examples(self, name: str, examples: str | list[str]) -> None:
        """Register example surface forms for entity type *name*.

        Args:
            name: Entity-type label.
            examples: One or more surface-form strings.
        """
        if isinstance(examples, str):
            examples = [examples]
        if name not in self._examples:
            self._examples[name] = []
        for e in examples:
            self._examples[name].append(Entity(e, name))

    def in_place_annotation(self, text: str) -> str:
        """Return *text* with entity-type labels inserted after each match.

        Example::

            "my name is Jarbas(person)"
        """
        new_text = text
        indexes: dict[int, list[tuple[str, str]]] = {}
        for ent in self.extract_entities(text):
            for index in ent.indexes:
                key = index + len(ent.value)
                if key not in indexes:
                    indexes[key] = []
                if (ent.value, ent.entity_type) not in indexes[key]:
                    indexes[key].append((ent.value, ent.entity_type))
        annotations: dict[int, str] = {
            idx: "(" + "|".join(i[1] for i in pairs) + ")"
            for idx, pairs in indexes.items()
        }
        for i in sorted(annotations, reverse=True):
            new_text = new_text[:i] + annotations[i] + new_text[i:]
        return new_text

    def entity_lookup(
        self, text: str, as_json: bool = False
    ) -> Generator[Entity | dict[str, Any], None, None]:
        """Yield entities whose example values appear in *text*.

        Args:
            text: Input string.
            as_json: If ``True`` yield ``dict`` representations instead of
                ``Entity`` objects.
        """
        for ent_name in self.examples:
            for ent in self.examples[ent_name]:
                if re.findall(r'\b' + ent.value.lower() + r"\b", text.lower()):
                    entity = Entity(
                        value=ent.value,
                        entity_type=ent.entity_type,
                        source_text=text,
                    )
                    yield entity.as_json() if as_json else entity

    def extract_entities(
        self, text: str, as_json: bool = False
    ) -> Generator[Entity | dict[str, Any], None, None]:
        """Yield entities extracted from *text* (delegates to ``entity_lookup``).

        Args:
            text: Input string.
            as_json: If ``True`` yield ``dict`` representations.
        """
        yield from self.entity_lookup(text, as_json)


if __name__ == "__main__":
    from pprint import pprint

    n = SimpleNER()
    n.add_entity_examples("person", ["jarbas", "kevin"])
    pprint(n.examples)
    for ent in n.entity_lookup("my name is Jarbas"):
        print("TEXT:", ent.source_text)
        print("ENTITY TYPE: ", ent.entity_type, "ENTITY_VALUE: ", ent.value)
    for ent in n.entity_lookup("where is Kevin", as_json=True):
        pprint(ent)
