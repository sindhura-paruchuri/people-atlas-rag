import unittest
from core import rank, evidence_sufficient, validate_answer, safe_url
class CoreTests(unittest.TestCase):
    def test_unknown_is_not_match(self):
        self.assertEqual(rank('quantum entanglement',[{'name':'Maya','skills':['Python']}]),[])
    def test_partial_match_requires_web(self):
        self.assertFalse(evidence_sufficient('Python Austin',[{'text':'Python developer Dallas','score':1}]))
    def test_full_match_skips_web(self):
        self.assertTrue(evidence_sufficient('Python Austin',[{'text':'Python developer Austin','score':1}]))
    def test_citation_rejection(self):
        self.assertFalse(validate_answer('Claim [99]',[{'id':'1'}])[1])
        self.assertFalse(validate_answer('Uncited claim',[{'id':'1'}])[1])
        self.assertTrue(validate_answer('Claim [1]',[{'id':'1'}])[1])
    def test_source_urls(self):
        self.assertIsNone(safe_url('javascript:alert(1)'))
        self.assertIsNone(safe_url('https://user:pass@example.com'))
        self.assertEqual(safe_url('https://example.com'),'https://example.com')
if __name__=='__main__':unittest.main()
