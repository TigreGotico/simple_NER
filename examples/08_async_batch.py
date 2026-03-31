"""
08_async_batch.py — AsyncNERPipeline with process_batch_async
=============================================================
Goal: Process 10 sentences concurrently; collect and display results.
Run:  python examples/08_async_batch.py
"""

import asyncio
from simple_NER.async_pipeline import AsyncNERPipeline
from simple_NER.annotators.email import EmailAnnotator
from simple_NER.annotators.phone import PhoneAnnotator
from simple_NER.annotators.url import URLAnnotator
from simple_NER.annotators.currency import CurrencyAnnotator
from simple_NER.annotators.temporal import TemporalNER


SENTENCES = [
    "Reach Alice at alice@wonderland.io",
    "Call Bob: +44 20 7946 0958 before 5pm",
    "Visit https://docs.example.com/api for the spec",
    "Invoice for $2,500 due by 2025-07-15",
    "Email support@corp.io or call 1-800-555-0100",
    "No contact information in this sentence at all",
    "Both info@test.com and https://test.com/page work",
    "International: +49-89-12345678, fee: €99",
    "US number: (212) 555-3456 ext. 78",
    "Final deadline: next Friday, budget capped at £500",
]


async def main() -> None:
    pipe = AsyncNERPipeline(dedup_strategy="keep_longest")
    pipe.add_annotator(EmailAnnotator())
    pipe.add_annotator(PhoneAnnotator())
    pipe.add_annotator(URLAnnotator())
    pipe.add_annotator(CurrencyAnnotator())
    pipe.add_annotator(TemporalNER(lang="en-us"))

    print("Processing 10 sentences with max_concurrency=5...\n")
    results = await pipe.process_batch_async(SENTENCES, max_concurrency=5)

    for text, entities in zip(SENTENCES, results):
        truncated = text[:50]
        if entities:
            for e in entities:
                print(f"  {truncated:<52} [{e.entity_type}] {e.value!r}")
        else:
            print(f"  {truncated:<52} (none)")


if __name__ == "__main__":
    asyncio.run(main())
