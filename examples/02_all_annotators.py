"""
02_all_annotators.py — every annotator on a tailored sentence
=============================================================
Goal: Show what each annotator detects, including data fields.
Run:  python examples/02_all_annotators.py
"""

from simple_NER.annotators.email import EmailAnnotator
from simple_NER.annotators.phone import PhoneAnnotator
from simple_NER.annotators.url import URLAnnotator
from simple_NER.annotators.currency import CurrencyAnnotator
from simple_NER.annotators.hashtag import HashtagAnnotator
from simple_NER.annotators.organizations import OrganizationAnnotator
from simple_NER.annotators.dates import DateAnnotator
from simple_NER.annotators.numbers import NumberNER
from simple_NER.annotators.temporal import TemporalNER
from simple_NER.annotators.locations import LocationNER


def demo(label: str, annotator, text: str) -> None:
    """Print entities extracted by a single annotator."""
    print(f"\n[{label}]")
    print(f"  Input: {text!r}")
    found = list(annotator.extract_entities(text))
    if not found:
        print("  (no entities found)")
    for e in found:
        print(
            f"  {e.entity_type:<20} {e.value!r:<30} conf={e.confidence:.2f}"
            + (f"  data={e.data}" if e.data else "")
        )


def main() -> None:
    demo("EmailAnnotator",
         EmailAnnotator(),
         "Reach us at support@example.com or billing@corp.io")

    demo("PhoneAnnotator",
         PhoneAnnotator(),
         "Call +1-800-555-0199 or locally at (212) 555-3456")

    demo("URLAnnotator",
         URLAnnotator(),
         "See https://example.com/docs and http://api.example.org/v2/")

    demo("CurrencyAnnotator",
         CurrencyAnnotator(),
         "Price: $1,299.99 USD or €849 EUR")

    demo("HashtagAnnotator",
         HashtagAnnotator(),
         "Trending: #OpenSource #AI_Tools #MachineLearnig2025 #BREAKING")

    demo("OrganizationAnnotator",
         OrganizationAnnotator(strict_mode=False),
         "Google LLC and Massachusetts Institute of Technology partner on AI.")

    demo("DateAnnotator",
         DateAnnotator(lang="en-us"),
         "Project kick-off: 2025-01-15. Deadline: 2025/06/30.")

    demo("NumberNER",
         NumberNER(lang="en-us"),
         "We ordered twenty-three boxes and 4 pallets.")

    demo("TemporalNER",
         TemporalNER(lang="en-us"),
         "The meeting is next Monday at 3pm and lasts two hours.")

    demo("LocationNER (countries + capitals)",
         LocationNER(include_countries=True, include_capitals=True, include_cities=False),
         "Flights from Berlin to Tokyo via London depart on Tuesday.")


if __name__ == "__main__":
    main()
