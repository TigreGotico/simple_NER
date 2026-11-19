import re
from collections.abc import Generator
from typing import Any

from simple_NER import Entity
from simple_NER.rules import Rule, RuleNER


class RegexNER(RuleNER):
    """Regex-pattern based NER (extends :class:`RuleNER`)."""

    def _create_regex(self, rule: str) -> re.Pattern[str] | None:
        """Compile *rule* as a case-insensitive regex.

        Args:
            rule: Regex pattern string.

        Returns:
            Compiled pattern, or ``None`` if compilation fails.
        """
        try:
            return re.compile(rule, re.IGNORECASE)
        except re.error:
            return None

    def extract_entities(
        self, text: str, as_json: bool = False
    ) -> Generator[Entity | dict[str, Any], None, None]:
        """Yield entities extracted from *text* using registered regex rules.

        Args:
            text: Input string.
            as_json: If ``True`` yield ``dict`` representations.
        """
        for r in self._rules:
            for rule in self._rules[r]:
                for rul in rule.rules:
                    regex = self._create_regex(rul)
                    if regex is None:
                        continue
                    for match in regex.findall(text):
                        value = match if isinstance(match, str) else match[0]
                        ent = Entity(value, rule.name, source_text=text,
                                     rules=self._rules[r])
                        yield ent.as_json() if as_json else ent

    def add_entity_examples(self, name: str, examples: str | list[str]) -> None:
        """Register example surface forms, auto-converted to word-boundary regexes.

        Args:
            name: Entity-type label.
            examples: One or more surface-form strings.
        """
        if isinstance(examples, str):
            examples = [examples]
        if name not in self._examples:
            self._examples[name] = []
        for e in examples:
            rules = r'\b' + e.lower() + r"\b"
            self._examples[name].append(Entity(e, name, rules=Rule(name, rules)))

    def add_rule(self, name: str, rules: str | list[str]) -> None:
        """Register regex pattern(s) under *name*.

        Args:
            name: Entity-type label.
            rules: One or more regex pattern strings.
        """
        if isinstance(rules, str):
            rules = [rules]
        if name not in self._rules:
            self._rules[name] = []
        self._rules[name].append(Rule(name, rules))


if __name__ == "__main__":
    from pprint import pprint

    n = RegexNER()
    text = "hello there"
    rules = r'(\W*hello\W*\!?\W*)'
    n.add_rule("greeting", rules)
    for e in n.extract_entities(text):
        pprint(e.as_json())

    n.add_entity_examples("person", ["bob", "joe", "amy"])
    text = "hello amy"
    for e in n.entity_lookup(text):
        pprint(e.as_json())
