#!/usr/bin/env python3
"""Example: New annotators (URL, Phone, Currency, Organization, Hashtag, Date).

This example demonstrates the new annotators added in v0.9.0:
- URLAnnotator: Extract URLs from text
- PhoneAnnotator: Extract phone numbers
- CurrencyAnnotator: Extract money/currency values
- OrganizationAnnotator: Extract company/organization names
- HashtagAnnotator: Extract hashtags
- DateAnnotator: Extract explicit dates
"""

from simple_NER.annotators.factory import create_pipeline


def example_url_extraction() -> None:
    """Demonstrate URL extraction."""
    print("\n" + "=" * 70)
    print("URL EXTRACTION")
    print("=" * 70)

    from simple_NER.annotators.url_ner import URLAnnotator

    ner = URLAnnotator()
    text = """
    Visit our website at https://example.com for more info.
    API docs: http://api.example.com/v1/users?id=123
    Local server: http://localhost:8080/test
    """

    print(f"Text: {text.strip()}\n")

    for ent in ner.extract_entities(text):
        print(f"  {ent.value:40} -> {ent.entity_type} (conf: {ent.confidence:.2f})")


def example_phone_extraction() -> None:
    """Demonstrate phone number extraction."""
    print("\n" + "=" * 70)
    print("PHONE NUMBER EXTRACTION")
    print("=" * 70)

    from simple_NER.annotators.phone_ner import PhoneAnnotator

    ner = PhoneAnnotator()
    text = """
    Contact us at +1-555-123-4567 (international).
    US office: (555) 987-6543
    Local: 555.123.4567 or 123-4567
    UK: +44 20 7946 0958
    """

    print(f"Text: {text.strip()}\n")

    for ent in ner.extract_entities(text):
        data = ent.data
        print(f"  {ent.value:25} -> {data['type']:15} (digits: {data['digit_count']})")


def example_currency_extraction() -> None:
    """Demonstrate currency extraction."""
    print("\n" + "=" * 70)
    print("CURRENCY EXTRACTION")
    print("=" * 70)

    from simple_NER.annotators.currency_ner import CurrencyAnnotator

    ner = CurrencyAnnotator()
    text = """
    Product prices: $99.99, €85.50, £70.00
    Budget: USD 5000, EUR 4000, GBP 3500
    Large amounts: $1,000,000.00
    """

    print(f"Text: {text.strip()}\n")

    for ent in ner.extract_entities(text):
        data = ent.data
        print(f"  {ent.value:20} -> {data['amount']:12.2f} {data['currency']}")


def example_organization_extraction() -> None:
    """Demonstrate organization extraction."""
    print("\n" + "=" * 70)
    print("ORGANIZATION EXTRACTION")
    print("=" * 70)

    from simple_NER.annotators.organization_ner import OrganizationAnnotator

    # Strict mode (default) - fewer false positives
    ner = OrganizationAnnotator(strict_mode=True)
    text = """
    Apple Inc announced partnership with Microsoft Corp.
    Google LLC will work with Stanford University.
    Research at Johns Hopkins Hospital shows promising results.
    """

    print(f"Text: {text.strip()} (strict mode)\n")

    for ent in ner.extract_entities(text):
        data = ent.data
        print(f"  {ent.value:30} -> {data['org_type']:15} (conf: {ent.confidence:.2f})")

    # Relaxed mode - more matches, more false positives
    print("\n(relaxed mode)")
    ner_relaxed = OrganizationAnnotator(strict_mode=False)
    for ent in ner_relaxed.extract_entities(text):
        data = ent.data
        print(f"  {ent.value:30} -> {data['org_type']:15} (conf: {ent.confidence:.2f})")


def example_hashtag_extraction() -> None:
    """Demonstrate hashtag extraction."""
    print("\n" + "=" * 70)
    print("HASHTAG EXTRACTION")
    print("=" * 70)

    from simple_NER.annotators.hashtag_ner import HashtagAnnotator

    ner = HashtagAnnotator()
    text = """
    Great day! #awesome #BestDayEver #summer2024
    Tech trends: #MachineLearning #AI #Tech_News
    Skip #123 (numbers only) but keep #tag123
    """

    print(f"Text: {text.strip()}\n")

    for ent in ner.extract_entities(text):
        data = ent.data
        print(f"  {ent.value:20} -> {data['type']:15} (len: {data['length']})")


def example_date_extraction() -> None:
    """Demonstrate date extraction."""
    print("\n" + "=" * 70)
    print("DATE EXTRACTION")
    print("=" * 70)

    from simple_NER.annotators.date_ner import DateAnnotator

    ner = DateAnnotator()
    text = """
    Meeting scheduled for 12/25/2024 (US format).
    Deadline: 2024-01-15 (ISO format).
    Event on January 5, 2025 or maybe 5 Jan 2025.
    Conference: 15/03/2025 (EU format).
    """

    print(f"Text: {text.strip()}\n")

    for ent in ner.extract_entities(text):
        data = ent.data
        print(f"  {ent.value:25} -> {data['month']:2}/{data['day']:2}/{data['year']} ({data['format']})")


def example_combined_pipeline() -> None:
    """Demonstrate all new annotators in a single pipeline."""
    print("\n" + "=" * 70)
    print("COMBINED PIPELINE (ALL NEW ANNOTATORS)")
    print("=" * 70)

    # Create pipeline with all new annotators
    pipeline = create_pipeline([
        'url', 'phone', 'currency',
        'organization', 'hashtag', 'date'
    ])

    text = """
    Apple Inc announced on 12/25/2024.
    Visit https://apple.com for $999.
    Call +1-555-123-4567 #Apple #Tech
    Budget: €5000 from Microsoft Corp.
    """

    print(f"Text: {text.strip()}\n")
    print("Entities found:")
    print("-" * 70)

    entities = pipeline.process(text)
    for ent in entities:
        print(f"  {ent.value:25} -> {ent.entity_type}")

    print(f"\nTotal: {len(entities)} entities")


def main() -> None:
    """Run all examples."""
    print("=" * 70)
    print(" SIMPLE_NER: NEW ANNOTATORS EXAMPLE ")
    print("=" * 70)

    example_url_extraction()
    example_phone_extraction()
    example_currency_extraction()
    example_organization_extraction()
    example_hashtag_extraction()
    example_date_extraction()
    example_combined_pipeline()

    print("\n" + "=" * 70)
    print(" ALL EXAMPLES COMPLETED ")
    print("=" * 70)
    print("\nNew annotators in v0.9.0:")
    print("  - URLAnnotator (url, urls)")
    print("  - PhoneAnnotator (phone, phone_number)")
    print("  - CurrencyAnnotator (currency, money)")
    print("  - OrganizationAnnotator (organization, org, company)")
    print("  - HashtagAnnotator (hashtag, hashtags, tag)")
    print("  - DateAnnotator (date, dates)")
    print("\nTotal: 24 annotators available!")
    print()


if __name__ == "__main__":
    main()
