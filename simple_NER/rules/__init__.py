from collections.abc import Generator
from typing import Any

import simplematch as sm
from quebra_frases.list_utils import flatten

from simple_NER import Entity, SimpleNER


class Rule:
    """A named collection of simplematch or regex pattern strings."""

    def __init__(self, name: str, rules: str | list[str]) -> None:
        """Initialise a Rule.

        Args:
            name: Entity-type label this rule produces.
            rules: One or more pattern strings.
        """
        self._name = name
        self._rules: str | list[str] = rules

    @property
    def rules(self) -> str | list[str]:
        """Pattern string(s) for this rule."""
        return self._rules

    @property
    def name(self) -> str:
        """Entity-type label."""
        return self._name

    def __repr__(self) -> str:
        return self.name

    def as_json(self) -> dict[str, Any]:
        """Serialise to a JSON-safe dict."""
        return {"name": self.name, "rules": self._rules}


class RuleNER(SimpleNER):
    """Simplematch-pattern based NER."""

    def __init__(self) -> None:
        self._rules: dict[str, list[Rule]] = {}
        self._examples: dict[str, list[Entity]] = {}

    @property
    def rules(self) -> dict[str, list[Rule]]:
        """Registered name → Rule list mapping."""
        return self._rules

    @property
    def examples(self) -> dict[str, list[Entity]]:
        """Registered entity-type → example entities mapping."""
        return self._examples

    def add_rule(self, name: str, rules: str | list[str]) -> None:
        """Register simplematch pattern(s) under *name*.

        Args:
            name: Entity-type label.
            rules: One or more simplematch pattern strings.
        """
        if isinstance(rules, str):
            rules = [rules]
        if name not in self._rules:
            self._rules[name] = []
        rules = [r.lower() for r in rules]
        self._rules[name].append(Rule(name, rules))

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

    def extract_entities(
        self, text: str, as_json: bool = False
    ) -> Generator[Entity | dict[str, Any], None, None]:
        """Yield entities extracted from *text* using registered simplematch rules.

        Args:
            text: Input string.
            as_json: If ``True`` yield ``dict`` representations.
        """
        for name, rules in self._rules.items():
            regexes = flatten([r.rules for r in rules])
            for r in regexes:
                entities = sm.match(r, text, case_sensitive=True)
                if entities is None:
                    entities = sm.match(r, text, case_sensitive=False)
                if entities is not None:
                    for k, v in entities.items():
                        ent = Entity(v, entity_type=k, source_text=text, rules=r)
                        yield ent.as_json() if as_json else ent


if __name__ == "__main__":
    from pprint import pprint

    n = RuleNER()
    n.add_rule("name", "my name is {person}")
    for ent in n.extract_entities("my name is jarbas"):
        print("TEXT:", ent.source_text)
        print("ENTITY TYPE: ", ent.entity_type, "ENTITY_VALUE: ", ent.value)
        print("RULES:", ent.rules)

    n.add_entity_examples("person", "jon doe")
    for ent in n.entity_lookup("who is jon doe?", as_json=True):
        pprint(ent)
