from simple_NER import SimpleNER

# adding your own entities
ner = SimpleNER()
ner.add_entity_examples("person", ["bob", "jon", "amy", "kevin"])

assert ner.is_match("jon is ugly", "person")
assert not ner.is_match("i like pizza", "person")

for ent in ner.entity_lookup("where is Kevin", as_json=True):
    assert ent == {'confidence': 1,
                   'data': {},
                   'entity_type': 'person',
                   'rules': [],
                   'source_text': 'where is Kevin',
                   'spans': [(9, 14)],
                   'value': 'kevin'}

# pre loaded list of entities under /res/en-us

from simple_NER.annotators.lookup_ner import LookUpNER

ner = LookUpNER()

text = "My dog is furious"
for e in ner.extract_entities(text):
    print(e.as_json())
    """
   {'entity_type': 'animal', 'spans': [(3, 6)], 'value': 'dog', 'source_text': 'My dog is furious', 'confidence': 1, 'data': {}, 'rules': []}
    {'entity_type': 'emotion', 'spans': [(10, 17)], 'value': 'furious', 'source_text': 'My dog is furious', 'confidence': 1, 'data': {}, 'rules': []}
    """
