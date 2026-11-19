"""
07_currency_multilang.py — CurrencyAnnotator on EN, DE, FR text
===============================================================
Goal: Show amount/currency extraction from different decimal formats
      (US: 1,299.99 vs EU: 1.299,99).
Run:  python examples/07_currency_multilang.py
"""

from simple_NER.annotators.currency import CurrencyAnnotator


def main() -> None:
    ann = CurrencyAnnotator()

    samples = [
        # English / US format
        ("en", "The laptop costs $1,299.99 and the monitor is $349.00 USD."),
        ("en", "We invoiced £2,500 for services and received €1,800 back."),
        # German / EU format
        ("de", "Das Gerät kostet 1.299,99 € und der Versand 9,95 EUR."),
        ("de", "Gesamtbetrag: 4.750,00 CHF inkl. MwSt."),
        # French
        ("fr", "Le prix est de 599,00 € TTC et l'option coûte 49,99 €."),
        # Mixed in one sentence
        ("mixed", "Convert $500 USD to €450 EUR or £390 GBP."),
    ]

    for lang, text in samples:
        print(f"\n[{lang}] {text}")
        entities = list(ann.extract_entities(text))
        if not entities:
            print("  (no currency entities found)")
            continue
        for e in entities:
            amount = e.data.get("amount")
            currency = e.data.get("currency", "")
            symbol = e.data.get("currency_symbol", "")
            print(
                f"  value={e.value!r:<18}  amount={amount!r:<10}  "
                f"currency={currency!r:<6}  symbol={symbol!r}"
            )


if __name__ == "__main__":
    main()
