import os,unittest
from unittest.mock import AsyncMock,patch
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['RAG_API_TOKEN'] = 'test-token'
os.environ['INTERNAL_TOKEN'] = 'internal-test-token'
from fastapi.testclient import TestClient
import api
class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client=TestClient(api.app);self.headers={'Authorization':'Bearer test-token'}
    def test_authentication(self):
        self.assertEqual(self.client.get('/people').status_code,401)
    def test_blank_question(self):
        self.assertEqual(self.client.post('/query',headers=self.headers,json={'query':'   '}).status_code,422)
    def test_database_first_and_persistence(self):
        calls=[]
        async def agent(role,payload):
            calls.append(role)
            if role=='retrieval':return {'sources':[{'title':'Maya','text':'Python','type':'database','score':1}],'people':[],'sufficient':True}
            return {'answer':'Python [1]','citation_valid':True,'usage':{}}
        with patch.object(api,'agent',side_effect=agent),patch.object(api.db,'save_query') as save:
            r=self.client.post('/query',headers=self.headers,json={'query':'Python'})
            self.assertEqual(r.status_code,200);self.assertEqual(calls,['retrieval','answer']);save.assert_called_once()
            self.assertEqual(r.json()['sources'][0]['id'],'1')
    def test_missing_evidence_triggers_web(self):
        calls=[]
        async def agent(role,payload):
            calls.append(role)
            if role=='retrieval':return {'sources':[],'people':[],'sufficient':False}
            if role=='research':return {'sources':[{'title':'Source','text':'Evidence','type':'web snippet','url':'https://example.com'}]}
            return {'answer':'Evidence [1]','citation_valid':True,'usage':{}}
        with patch.object(api,'agent',side_effect=agent),patch.object(api.db,'save_query'):
            r=self.client.post('/query',headers=self.headers,json={'query':'Unknown topic'})
            self.assertEqual(r.status_code,200);self.assertEqual(calls,['retrieval','research','answer'])
    def test_web_disabled(self):
        calls=[]
        async def agent(role,payload):
            calls.append(role)
            if role=='retrieval':return {'sources':[],'people':[],'sufficient':False}
            return {'answer':'Insufficient evidence','citation_valid':True,'usage':{}}
        with patch.object(api,'agent',side_effect=agent),patch.object(api.db,'save_query'):
            r=self.client.post('/query',headers=self.headers,json={'query':'Unknown','allow_web':False})
            self.assertEqual(r.status_code,200);self.assertNotIn('research',calls)
    def test_feedback_foreign_key(self):
        with patch.object(api.db,'feedback',return_value=False):
            r=self.client.post('/feedback',headers=self.headers,json={'query_id':'00000000-0000-0000-0000-000000000001','rating':1})
            self.assertEqual(r.status_code,404)
    def test_backend_failure_is_explicit(self):
        with patch.object(api,'agent',new=AsyncMock(side_effect=RuntimeError('secret'))):
            r=self.client.post('/query',headers=self.headers,json={'query':'Python'})
            self.assertEqual(r.status_code,502);self.assertNotIn('secret',r.text)
if __name__=='__main__':unittest.main()

class PreferenceTests(unittest.TestCase):
    def setUp(self):self.client=TestClient(api.app);self.headers={'Authorization':'Bearer test-token'}
    def test_reject_invalid_choice(self):
        r=self.client.post('/preference',headers=self.headers,json={'comparison_id':'00000000-0000-0000-0000-000000000001','choice':'made-up'})
        self.assertEqual(r.status_code,422)
    def test_unknown_comparison(self):
        with patch.object(api.db,'save_preference',return_value=False):
            r=self.client.post('/preference',headers=self.headers,json={'comparison_id':'00000000-0000-0000-0000-000000000001','choice':'tie'})
            self.assertEqual(r.status_code,404)
    def test_human_choice_persisted(self):
        with patch.object(api.db,'save_preference',return_value=True) as save:
            r=self.client.post('/preference',headers=self.headers,json={'comparison_id':'00000000-0000-0000-0000-000000000001','choice':'b'})
            self.assertEqual(r.status_code,200);save.assert_called_once_with('00000000-0000-0000-0000-000000000001','b')
