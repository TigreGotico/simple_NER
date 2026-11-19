"""
Complete example demonstrating all simple_NER features.

This script showcases:
- Rule-based NER with simplematch patterns
- Regex-based NER
- Built-in annotators (email, names, locations, datetime, etc.)
- Custom annotators
- NER wrappers for combining multiple detectors
"""

from pprint import pprint


def example_rule_based():
    """Rule-based NER using simplematch patterns."""
    print("\n" + "=" * 60)
    print("RULE-BASED NER")
    print("=" * 60)

    from simple_NER.rules import RuleNER

    ner = RuleNER()
    ner.add_rule("name", "my name is {person}")
    ner.add_rule("location", "i live in {city}")

    text = "my name is Alice and i live in Lisbon"
    print(f"Text: {text}\n")

    for ent in ner.extract_entities(text):
        print(f"  Entity: {ent.value} ({ent.entity_type})")
        pprint(ent.as_json())


def example_regex():
    """Regex-based NER for custom patterns."""
    print("\n" + "=" * 60)
    print("REGEX-BASED NER")
    print("=" * 60)

    from simple_NER.rules.rx import RegexNER

    ner = RegexNER()

    # Date pattern
    date_pattern = r'\d{2}/\d{2}/\d{4}'
    ner.add_rule("date", date_pattern)

    # Email pattern
    email_pattern = r'[\w.+-]+@[\w-]+\.[a-z]{2,}'
    ner.add_rule("email", email_pattern)

    text = "Contact john@example.com on 12/25/2023"
    print(f"Text: {text}\n")

    for ent in ner.extract_entities(text):
        print(f"  Entity: {ent.value} ({ent.entity_type})")


def example_email():
    """Extract email addresses."""
    print("\n" + "=" * 60)
    print("EMAIL EXTRACTION")
    print("=" * 60)

    from simple_NER.annotators.email_ner import EmailNER

    ner = EmailNER()
    text = "Send emails to support@company.com or sales@store.org"
    print(f"Text: {text}\n")

    for ent in ner.extract_entities(text):
        print(f"  Email: {ent.value}")


def example_names():
    """Extract proper nouns (names)."""
    print("\n" + "=" * 60)
    print("NAME EXTRACTION")
    print("=" * 60)

    from simple_NER.annotators.names_ner import NamesNER

    ner = NamesNER()
    text = "John Doe met Alice Smith in Paris"
    print(f"Text: {text}\n")

    for ent in ner.extract_entities(text):
        print(f"  Name: {ent.value} (confidence: {ent.confidence})")


def example_locations():
    """Extract countries and cities."""
    print("\n" + "=" * 60)
    print("LOCATION EXTRACTION")
    print("=" * 60)

    from simple_NER.annotators.locations_ner import LocationNER

    ner = LocationNER()
    text = "The capital of Portugal is Lisbon"
    print(f"Text: {text}\n")

    for ent in ner.extract_entities(text):
        print(f"  Location: {ent.value} ({ent.entity_type})")
        if ent.data:
            print(f"    Data: {ent.data}")


def example_datetime():
    """Extract datetime expressions."""
    print("\n" + "=" * 60)
    print("DATETIME EXTRACTION")
    print("=" * 60)

    from simple_NER.annotators.datetime_ner import DateTimeNER

    ner = DateTimeNER()

    examples = [
        "my birthday is on december 5th",
        "meeting at 3pm tomorrow",
        "see you next Monday",
    ]

    for text in examples:
        print(f"Text: {text}")
        for ent in ner.extract_entities(text):
            print(f"  DateTime: {ent.value} (type: {ent.entity_type})")
            if hasattr(ent, 'day') and ent.day:
                print(f"    Day: {ent.day}, Month: {ent.month}, Year: {ent.year}")
        print()


def example_numbers():
    """Extract written numbers."""
    print("\n" + "=" * 60)
    print("NUMBER EXTRACTION")
    print("=" * 60)

    from simple_NER.annotators.numbers_ner import NumberNER

    ner = NumberNER()
    text = "I have three hundred apples and 42 oranges"
    print(f"Text: {text}\n")

    for ent in ner.extract_entities(text):
        print(f"  Number: {ent.value} = {ent.data.get('number', 'N/A')}")


def example_keywords():
    """Extract keywords using RAKE."""
    print("\n" + "=" * 60)
    print("KEYWORD EXTRACTION")
    print("=" * 60)

    from simple_NER.annotators.keyword_ner import KeywordNER

    ner = KeywordNER()
    text = "Machine learning is a subset of artificial intelligence that enables systems to learn from data"
    print(f"Text: {text}\n")

    keywords = []
    for ent in ner.extract_entities(text):
        keywords.append((ent.value, ent.score))

    keywords.sort(key=lambda x: x[1], reverse=True)
    print("Top keywords:")
    for kw, score in keywords[:5]:
        print(f"  {kw}: {score}")


def example_units():
    """Extract measurements and units."""
    print("\n" + "=" * 60)
    print("UNIT EXTRACTION")
    print("=" * 60)

    from simple_NER.annotators.units_ner import UnitsNER

    ner = UnitsNER()
    text = "The LHC smashes proton beams at 13.0 TeV"
    print(f"Text: {text}\n")

    for ent in ner.extract_entities(text):
        print(f"  Measurement: {ent.value}")
        print(f"    Value: {ent.data_value}")
        print(f"    Unit: {ent.unit.name if hasattr(ent, 'unit') else 'N/A'}")


def example_custom_annotator():
    """Create a custom annotator."""
    print("\n" + "=" * 60)
    print("CUSTOM ANNOTATOR")
    print("=" * 60)

    from simple_NER import Entity
    from simple_NER.annotators import NERWrapper

    def extract_product_mentions(text):
        """Custom detector for product names."""
        products = ["iphone", "android", "windows"]
        for product in products:
            if product.lower() in text.lower():
                yield Entity(
                    product,
                    "product",
                    source_text=text,
                    confidence=0.9,
                    data={"category": "technology"}
                )

    wrapper = NERWrapper()
    wrapper.add_detector(extract_product_mentions)

    text = "I prefer Android over iPhone"
    print(f"Text: {text}\n")

    for ent in wrapper.extract_entities(text):
        print(f"  Product: {ent.value}")
        print(f"    Category: {ent.data.get('category', 'N/A')}")


def example_combined():
    """Combine multiple detectors with NERWrapper."""
    print("\n" + "=" * 60)
    print("COMBINED NER (MULTIPLE DETECTORS)")
    print("=" * 60)

    from simple_NER.annotators import NERWrapper
    from simple_NER.annotators.email_ner import EmailNER
    from simple_NER.rules import RuleNER
    from simple_NER.rules.rx import RegexNER

    wrapper = NERWrapper()

    # Add rule-based detector
    rule_ner = RuleNER()
    rule_ner.add_rule("greeting", "hello {name}")
    wrapper.add_detector(rule_ner.extract_entities)

    # Add regex detector
    regex_ner = RegexNER()
    regex_ner.add_rule("phone", r'\b\d{3}-\d{3}-\d{4}\b')
    wrapper.add_detector(regex_ner.extract_entities)

    # Add email detector
    wrapper.add_detector(EmailNER().extract_entities)

    text = "hello John, my phone is 555-123-4567 and email is john@test.com"
    print(f"Text: {text}\n")

    entities = list(wrapper.extract_entities(text))
    print(f"Found {len(entities)} entities:")
    for ent in entities:
        print(f"  - {ent.value} ({ent.entity_type})")


def example_in_place_annotation():
    """Show in-place text annotation."""
    print("\n" + "=" * 60)
    print("IN-PLACE ANNOTATION")
    print("=" * 60)

    from simple_NER import SimpleNER

    ner = SimpleNER()
    ner.add_entity_examples("person", ["alice", "bob", "charlie"])
    ner.add_entity_examples("animal", ["cat", "dog"])

    text = "alice and bob took the cat to see charlie's dog"
    print(f"Original: {text}")

    annotated = ner.in_place_annotation(text)
    print(f"Annotated: {annotated}")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("SIMPLE_NER COMPLETE EXAMPLE")
    print("=" * 60)

    example_rule_based()
    example_regex()
    example_email()
    example_names()
    example_locations()
    example_datetime()
    example_numbers()
    example_keywords()
    example_units()
    example_custom_annotator()
    example_combined()
    example_in_place_annotation()

    print("\n" + "=" * 60)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
