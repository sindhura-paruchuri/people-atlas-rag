"""Offline mechanics test. Random tiny model and mock records, never human data."""
import json,tempfile,sys,unittest
from pathlib import Path
from unittest.mock import patch
import torch
from transformers import GPT2Config,GPT2LMHeadModel,PreTrainedTokenizerFast
from tokenizers import Tokenizer
from tokenizers.models import WordLevel
from tokenizers.pre_tokenizers import Whitespace
import train_rlhf
class TrainingTests(unittest.TestCase):
    def test_reject_synthetic_provenance(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'test.jsonl';p.write_text(json.dumps({'provenance':'synthetic_test'})+'\n')
            with self.assertRaises(ValueError):train_rlhf.load(p)
    def test_mechanics_only(self):
        torch.set_num_threads(1)
        tokenizer=Tokenizer(WordLevel({'[UNK]':0,'[EOS]':1,'question':2,'answer':3,'good':4,'bad':5},unk_token='[UNK]'));tokenizer.pre_tokenizer=Whitespace()
        tok=PreTrainedTokenizerFast(tokenizer_object=tokenizer,unk_token='[UNK]',eos_token='[EOS]')
        cfg=GPT2Config(vocab_size=6,n_positions=512,n_embd=16,n_layer=1,n_head=1,eos_token_id=1,bos_token_id=1)
        records=lambda prefix,n:[{'query_id':prefix+str(i),'prompt':'question','chosen':'good answer','rejected':'bad answer'} for i in range(n)]
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'train').write_text('explicit synthetic test fixture; loader mocked')
            args=['train_rlhf','--model','random-unit-test-model','--train',str(root/'train'),'--validation',str(root/'valid'),'--output',str(root/'out'),'--steps','1','--reward-epochs','1','--device','cpu']
            with patch.object(sys,'argv',args),patch.object(train_rlhf,'load',side_effect=[records('train',10),records('valid',3)]),patch.object(train_rlhf.AutoTokenizer,'from_pretrained',return_value=tok),patch.object(train_rlhf.AutoModelForCausalLM,'from_pretrained',side_effect=lambda _:GPT2LMHeadModel(cfg)):
                train_rlhf.main()
            report=json.loads((root/'out/training-report.json').read_text())
            self.assertEqual(len(report['steps']),1)
            self.assertEqual(report['human_release_review'],'pending')
            self.assertTrue((root/'out/policy/config.json').exists())
if __name__=='__main__':unittest.main()
