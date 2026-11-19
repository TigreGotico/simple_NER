from pprint import pprint

from simple_NER.annotators.locations_ner import CitiesNER, LocationNER

ner = LocationNER()
# NOTE: case sensitive, enable detection of lowercase cities/countries
# ner = LocationNER(lowercase=True)


text = """The Capital of Portugal is Lisbon"""
for r in ner.extract_entities(text):
    print(r.value, "-", r.entity_type)
    pprint(r.as_json())

    """
    Portugal - Country
    {'confidence': 1,
     'data': {'capital': 'Lisbon',
              'country_code': 'PT',
              'hemisphere': 'north',
              'latitude': 39.5,
              'longitude': -8,
              'name': 'Portugal',
              'timezones': ['Europe/Lisbon',
                            'Atlantic/Madeira',
                            'Atlantic/Azores']},
     'entity_type': 'Country',
     'rules': [],
     'source_text': 'The Capital of Portugal is Lisbon',
     'spans': [(15, 23)],
     'value': 'Portugal'}
     
    Lisbon - Capital City
    {'confidence': 1,
     'data': {'country_code': 'PT',
              'country_name': 'Portugal',
              'hemisphere': 'north',
              'name': 'Lisbon'},
     'entity_type': 'Capital City',
     'rules': [],
     'source_text': 'The Capital of Portugal is Lisbon',
     'spans': [(27, 33)],
     'value': 'Lisbon'}
    """


ner = CitiesNER()
# NOTE: case sensitive
# ner = CitiesNER(lowercase=True)

text = """Braga is in northern portugal"""
for r in ner.extract_entities(text):
    print(r.value, "-", r.entity_type)
    pprint(r.as_json())
    """
     Braga - City
    {'confidence': 1,
     'data': {'country_code': 'PT',
              'hemisphere': 'north',
              'latitude': 41.55032,
              'longitude': -8.42005,
              'name': 'Braga'},
     'entity_type': 'City',
     'rules': [],
     'source_text': 'Braga is in northern portugal',
     'spans': [(0, 5)],
     'value': 'Braga'}
    """
