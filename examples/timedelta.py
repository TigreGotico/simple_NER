from simple_NER.annotators.datetime_ner import TimedeltaNER

ner = TimedeltaNER()

for r in ner.extract_entities(
        "5 minutes ago was X 10 minutes from now is Y in 19 hours will "
        "be N"):
    assert r.entity_type == "duration"
    print(r.value, r.total_seconds)
    """
    5 minutes 300.0
    10 minutes 600.0
    19 hours 68400.0
    """

for r in ner.extract_entities(
        "What President served for five years six months 2 days"):
    # NOTE months/years are not supported because they are not explicit
    # how many days is 1 month? how many days is 1 year?
    assert r.entity_type == "duration"
    print(r.value, r.total_seconds)
    """2 days 172800.0"""

for r in ner.extract_entities("starts in 5 minutes"):
    assert r.entity_type == "duration"
    print(r.value, r.total_seconds)
    """5 minutes 300.0"""

for r in ner.extract_entities("starts in five minutes"):
    assert r.entity_type == "duration"
    print(r.value, r.total_seconds)
    """5 minutes 300.0"""


