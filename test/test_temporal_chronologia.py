"""TemporalNER and NumberNER rows on real sentences in five languages.

Dates and durations are read with chronologia. The anchor is Wednesday
2025-06-18 10:30, so every expected instant is date arithmetic on it. The
entity value is the words of the sentence the reader consumed.
"""
from datetime import datetime

import pytest

from simple_NER.annotators.numbers_ner import NumberNER
from simple_NER.annotators.temporal_ner import TemporalNER

ANCHOR = datetime(2025, 6, 18, 10, 30)
TOMORROW = "2025-06-19T00:00:00"
DEC_5 = "2025-12-05T00:00:00"
DEC_25 = "2025-12-25T00:00:00"

DATES = [
    ("en-us", "meeting tomorrow", "tomorrow", TOMORROW),
    ("en-us", "see you tomorrow at 3pm", "tomorrow at 3pm", "2025-06-19T15:00:00"),
    ("en-us", "see you tomorrow at three pm", "tomorrow at three pm", "2025-06-19T15:00:00"),
    ("en-us", "the party is on december fifth", "on december fifth", DEC_5),
    ("en-us", "the party is on december 5th", "on december 5th", DEC_5),
    ("en-us", "on the 5th of december", "on the 5th of december", DEC_5),
    ("en-us", "the twenty fifth of december", "the twenty fifth of december", DEC_25),
    ("de-de", "Treffen morgen um 15 Uhr", "morgen um 15 Uhr", "2025-06-19T15:00:00"),
    ("de-de", "am fünften Dezember", "am fünften Dezember", DEC_5),
    ("de-de", "am 5. Dezember", "am 5. Dezember", DEC_5),
    ("de-de", "am fünfzehnten Juni um drei Uhr nachmittags", "am fünfzehnten Juni um drei Uhr nachmittags",
     "2026-06-15T15:00:00"),
    ("es-es", "nos vemos mañana", "mañana", TOMORROW),
    ("es-es", "el 5 de diciembre", "el 5 de diciembre", DEC_5),
    ("es-es", "el cinco de diciembre", "el cinco de diciembre", DEC_5),
    ("es-es", "el veinticinco de diciembre", "el veinticinco de diciembre", DEC_25),
    ("es-es", "mañana a las tres de la tarde", "mañana a las tres de la tarde", "2025-06-19T15:00:00"),
    ("fr-fr", "rendez-vous demain", "demain", TOMORROW),
    ("fr-fr", "le 5 décembre", "le 5 décembre", DEC_5),
    ("fr-fr", "le cinq décembre", "le cinq décembre", DEC_5),
    ("fr-fr", "le vingt-cinq décembre", "le vingt-cinq décembre", DEC_25),
    ("pt-pt", "vemos-nos amanhã", "amanhã", TOMORROW),
    ("pt-pt", "amanhã às três da tarde", "amanhã às três da tarde", "2025-06-19T15:00:00"),
    ("pt-pt", "no dia 25 de dezembro às 15h", "no dia 25 de dezembro às 15h", "2025-12-25T15:00:00"),
    ("pt-pt", "no dia vinte e cinco de dezembro", "no dia vinte e cinco de dezembro", DEC_25),
]

MINUTE, HOUR, DAY = 60, 3600, 86400
DURATIONS = [
    ("en-us", "wait five minutes", "five minutes", 5 * MINUTE),
    ("en-us", "wait 3 days", "3 days", 3 * DAY),
    ("en-us", "see you in three days", "three days", 3 * DAY),
    ("en-us", "it takes two hours and thirty minutes", "two hours and thirty minutes", 2 * HOUR + 30 * MINUTE),
    ("en-us", "wait ten minutes and twenty seconds", "ten minutes and twenty seconds", 10 * MINUTE + 20),
    ("de-de", "warte fünf Minuten", "fünf Minuten", 5 * MINUTE),
    ("de-de", "das dauert zwei Stunden", "zwei Stunden", 2 * HOUR),
    ("de-de", "wir sehen uns in drei Tagen", "drei Tagen", 3 * DAY),
    ("es-es", "espera cinco minutos", "cinco minutos", 5 * MINUTE),
    ("es-es", "tarda dos horas", "dos horas", 2 * HOUR),
    ("es-es", "nos vemos dentro de tres días", "tres días", 3 * DAY),
    ("fr-fr", "attends cinq minutes", "cinq minutes", 5 * MINUTE),
    ("fr-fr", "ça dure deux heures", "deux heures", 2 * HOUR),
    ("fr-fr", "on se voit dans trois jours", "trois jours", 3 * DAY),
    ("pt-pt", "espera cinco minutos", "cinco minutos", 5 * MINUTE),
    ("pt-pt", "demora duas horas", "duas horas", 2 * HOUR),
]

NUMBERS = [
    ("en-us", "I have three hundred apples", "three hundred", "300"),
    ("de-de", "ich habe dreihundert Äpfel", "dreihundert", "300"),
    ("es-es", "tengo trescientas manzanas", "trescientas", "300"),
    ("fr-fr", "j'ai trois cents pommes", "trois cents", "300"),
    ("pt-pt", "tenho trezentas maçãs", "trezentas", "300"),
]


def _entities(text, lang, entity_type):
    ner = TemporalNER(anchor_date=ANCHOR, lang=lang)
    return [e for e in ner.extract_entities(text) if e.entity_type == entity_type]


@pytest.mark.parametrize("lang,text,value,iso", DATES)
def test_date_value_and_instant(lang, text, value, iso):
    found = _entities(text, lang, "relative_date")
    assert [(e.value, e.data["isoformat"]) for e in found] == [(value, iso)]
    assert value in text


@pytest.mark.parametrize("lang,text,value,seconds", DURATIONS)
def test_duration_value_and_length(lang, text, value, seconds):
    found = _entities(text, lang, "duration")
    assert [(e.value, e.data["total_seconds"]) for e in found] == [(value, seconds)]
    assert value in text


@pytest.mark.parametrize("lang,text,value,number", NUMBERS)
def test_written_number(lang, text, value, number):
    found = list(NumberNER(lang=lang).extract_entities(text))
    assert [(e.value, e.data["number"]) for e in found] == [(value, number)]


@pytest.mark.xfail(
    strict=True,
    reason="https://github.com/TigreGotico/chronologia/issues/1215",
)
def test_day_word_of_a_date_is_no_duration():
    assert _entities("no dia 5 de dezembro", "pt-pt", "duration") == []
