import asyncio
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import AsyncMock, patch

import providers


class ProviderTests(unittest.TestCase):
    def test_shared_key_and_override(self):
        with patch.dict(os.environ, {'GEMINI_API_KEY': 'shared'}, clear=True):
            self.assertEqual(providers._api_key('LLM_API_KEY'), 'shared')
            os.environ['LLM_API_KEY'] = 'specific'
            self.assertEqual(providers._api_key('LLM_API_KEY'), 'specific')

    def test_no_key_fails(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(RuntimeError):
                providers._api_key('LLM_API_KEY')

    def test_embedding_alignment_and_dimension(self):
        config = {'GEMINI_API_KEY': 'test', 'EMBEDDING_BASE_URL': 'https://example.com',
                  'EMBEDDING_MODEL': 'test', 'EMBEDDING_DIMENSIONS': '2'}
        with patch.dict(os.environ, config), patch.object(providers, 'request', new_callable=AsyncMock) as req:
            req.return_value = {'data': [{'index': 1, 'embedding': [3., 4.]}, {'index': 0, 'embedding': [1., 2.]}]}
            self.assertEqual(asyncio.run(providers.embed(['a', 'b'])), [[1., 2.], [3., 4.]])
            for rows in ([{'index': 0, 'embedding': [1., 2.]}],
                         [{'index': 0, 'embedding': [1.]}, {'index': 1, 'embedding': [2.]}]):
                req.return_value = {'data': rows}
                with self.assertRaises(ValueError):
                    asyncio.run(providers.embed(['a', 'b']))

   # def test_setup_does_not_overwrite(self):
    #    root = Path(__file__).resolve().parents[2]
     #   spec = importlib.util.spec_from_file_location('setup_local', root / 'scripts/setup_local.py')
      #  module = importlib.util.module_from_spec(spec)
       # spec.loader.exec_module(module)
        #with tempfile.TemporaryDirectory() as tmp:
         #   folder = Path(tmp)
          #  (folder / '.env.example').write_text((root / '.env.example').read_text())
           # self.assertTrue(module.initialize(folder))
            #first = (folder / '.env').read_text()
            #self.assertNotIn('replace-with-', first)
            #self.assertIn('RAG_API_URL=http://127.0.0.1:8000', first)
            #self.assertFalse(module.initialize(folder))
            #self.assertEqual(first, (folder / '.env').read_text())
            
            
