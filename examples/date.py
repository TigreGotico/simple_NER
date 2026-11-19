from simple_NER.annotators.datetime_ner import DateTimeNER

ner = DateTimeNER()

for r in ner.extract_entities("my birthday is on december 5th"):
    assert r.entity_type == "relative_date"
    print("day:", r.day, "month:", r.month, "year:", r.year)
    """
    day: 5 month: 12 year: 2019
    """

for r in ner.extract_entities("entries are due by January 4th, 2017 at 8:30pm"):
    assert r.entity_type == "relative_date"
    print("day:", r.day,"month:", r.month, "year:", r.year, "hour:", r.hour,
          "minute:", r.minute)
    """
    day: 4 month: 1 year: 2017 hour: 20 minute: 30
    """

for r in ner.extract_entities(
        "tomorrow is X yesterday was Y in 10 days it will be Z"):
    assert r.entity_type == "relative_date"
    print(r.value,
          "day:", r.day, "month:", r.month, "year:", r.year,
          "hour:", r.hour, "minute:", r.minute)
    """
    tomorrow day: 30 month: 11 year: 2020 hour: 0 minute: 0
    yesterday day: 28 month: 11 year: 2020 hour: 0 minute: 0
    in 10 days day: 9 month: 12 year: 2020 hour: 0 minute: 0
    """
