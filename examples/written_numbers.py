from simple_NER.annotators.numbers_ner import NumberNER

ner = NumberNER()
for r in ner.extract_entities("three hundred trillion tons of spinning metal"):
    """
    {'confidence': 1,
     'data': {'number': '300000000000000.0'},
     'entity_type': 'written_number',
     'rules': [],
     'source_text': 'three hundred trillion tons of spinning metal',
     'spans': [(0, 22)],
     'value': 'three hundred trillion'}
    """

ner = NumberNER(short_scale=False)
for r in ner.extract_entities("three hundred trillion tons of spinning metal"):
    """
   {'confidence': 1,
     'data': {'number': '3e+20'},
     'entity_type': 'written_number',
     'rules': [],
     'source_text': 'three hundred trillion tons of spinning metal',
     'spans': [(0, 22)],
     'value': 'three hundred trillion'}
    """

ner = NumberNER()
for r in ner.extract_entities("the 5th number of the third thing"):
    """
   {'confidence': 1,
     'data': {'number': '5'},
     'entity_type': 'written_number',
     'rules': [],
     'source_text': 'the 5th number of the third thing',
     'spans': [(4, 7)],
     'value': '5th'}
    {'confidence': 1,
     'data': {'number': '3'},
     'entity_type': 'written_number',
     'rules': [],
     'source_text': 'the 5th number of the third thing',
     'spans': [(22, 27)],
     'value': 'third'}
    """

ner = NumberNER(ordinals=False)
for r in ner.extract_entities("the 5th number of the third thing"):
    """
   {'confidence': 1,
     'data': {'number': '5'},
     'entity_type': 'written_number',
     'rules': [],
     'source_text': 'the 5th number of the third thing',
     'spans': [(4, 7)],
     'value': '5th'}
    {'confidence': 1,
     'data': {'number': '0.3333333333333333'},
     'entity_type': 'written_number',
     'rules': [],
     'source_text': 'the 5th number of the third thing',
     'spans': [(22, 27)],
     'value': 'third'}
    """
