import json,unittest
from pathlib import Path
from prepare_data import convert
class DatasetTests(unittest.TestCase):
    def test_gold_is_not_in_corpus(self):
        row={'id':'q','question':'secret question','answer':'secret answer','supporting_facts':{'title':['Known']},'context':{'title':['Known'],'sentences':[['Public passage.']]}}
        docs,ev=convert([row]);self.assertNotIn('secret',json.dumps(docs));self.assertEqual(ev[0]['answer'],'secret answer')
    def test_deduplication(self):
        row={'id':'q','question':'q','answer':'a','supporting_facts':{'title':['Known']},'context':{'title':['Known','Known'],'sentences':[['One'],['Two']]}}
        self.assertEqual(len(convert([row])[0]),1)
    def test_bundled_data(self):
        docs=json.loads((Path(__file__).parents[1]/'data/corpus.json').read_text())
        self.assertEqual(len(docs),200);self.assertEqual(sum(d['kind']=='person' for d in docs),12)
        self.assertTrue(all(d['url'].startswith('https://en.wikipedia.org/wiki/') for d in docs))
