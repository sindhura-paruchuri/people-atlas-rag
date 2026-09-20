"""Educational RLHF: Bradley–Terry reward model + KL-regularized REINFORCE.

Uses actual human pairwise data, not thumbs-up heuristics. Not PPO, not a
production trainer. Train a small open-weight causal LM, never Gemini weights.
"""
import argparse,json,random,hashlib
from pathlib import Path
import torch
from torch import nn
from transformers import AutoTokenizer,AutoModelForCausalLM
class Reward(nn.Module):
    """Trainable reward head over frozen causal-LM representations."""
    def __init__(self,base):
        super().__init__();self.base=base;self.head=nn.Linear(base.config.hidden_size,1).to(next(base.parameters()).device)
        for p in self.base.parameters():p.requires_grad=False
    def forward(self,ids):
        with torch.no_grad():h=self.base(ids,output_hidden_states=True).hidden_states[-1][:,-1]
        return self.head(h).squeeze(-1)
def load(path):
    rows=[json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]
    for r in rows:
        if r.get('provenance')!='human_ui_preference' or not all(r.get(k) for k in ['query_id','prompt','chosen','rejected','reviewer']):raise ValueError('Only identified human preference records are accepted')
        if r['chosen']==r['rejected']:raise ValueError('Identical answer pair cannot train preferences')
    return rows
def main():
    p=argparse.ArgumentParser();p.add_argument('--model',required=True);p.add_argument('--train',required=True);p.add_argument('--validation',required=True);p.add_argument('--output',required=True);p.add_argument('--steps',type=int,default=20);p.add_argument('--reward-epochs',type=int,default=3);p.add_argument('--kl',type=float,default=.05);p.add_argument('--device',default='cuda' if torch.cuda.is_available() else 'cpu');a=p.parse_args()
    random.seed(42);torch.manual_seed(42)
    train,valid=load(a.train),load(a.validation)
    if len(train)<10 or len(valid)<3:raise ValueError('Collect at least 10 training and 3 validation comparisons; these are smoke-run minima, not sufficient for quality claims')
    if {r['query_id'] for r in train}&{r['query_id'] for r in valid}:raise ValueError('Query leakage between splits')
    tok=AutoTokenizer.from_pretrained(a.model);tok.pad_token=tok.eos_token
    policy=AutoModelForCausalLM.from_pretrained(a.model).to(a.device).eval()
    reference=AutoModelForCausalLM.from_pretrained(a.model).to(a.device).eval()
    reward=Reward(reference)
    def encode(s,max_length=384):return tok(s,return_tensors='pt',truncation=True,max_length=max_length).input_ids.to(a.device)
    def combined(r,answer):
        # Preserve an answer token budget instead of truncating it behind long evidence.
        prompt=encode(r['prompt']+'\nAnswer: ',256);completion=encode(answer,128)
        return torch.cat([prompt,completion],dim=1)
    opt=torch.optim.AdamW(reward.head.parameters(),lr=1e-3)
    for _ in range(a.reward_epochs):
        for r in train:
            loss=-torch.nn.functional.logsigmoid(reward(combined(r,r['chosen']))-reward(combined(r,r['rejected']))).mean()
            opt.zero_grad();loss.backward();opt.step()
    with torch.no_grad():acc=sum((reward(combined(r,r['chosen']))>reward(combined(r,r['rejected']))).item() for r in valid)/len(valid)
    for param in reward.head.parameters():param.requires_grad=False
    policy_opt=torch.optim.AdamW(policy.parameters(),lr=1e-6)
    logs=[];baseline=0.
    for step in range(a.steps):
        r=train[step%len(train)];prompt=encode(r['prompt']+'\nAnswer: ',256)
        with torch.no_grad():
            # Unfiltered on-policy sampling: log-probabilities below match behavior.
            ids=policy.generate(prompt,attention_mask=torch.ones_like(prompt),max_new_tokens=64,do_sample=True,temperature=1.,top_k=0,top_p=1.,pad_token_id=tok.eos_token_id)
            score=reward(ids).mean()
        start=prompt.shape[1]-1
        logits=policy(ids).logits[:,:-1].float();targets=ids[:,1:]
        logp=logits.log_softmax(-1)
        selected=logp.gather(-1,targets.unsqueeze(-1)).squeeze(-1)[:,start:]
        with torch.no_grad():ref_logp=reference(ids).logits[:,:-1].float().log_softmax(-1)
        kl=(logp[:,start:].exp()*(logp[:,start:]-ref_logp[:,start:])).sum(-1).mean()
        # Sequence-level score-function estimator plus differentiable reference KL.
        advantage=score-baseline
        loss=-advantage.detach()*selected.sum()+a.kl*kl
        policy_opt.zero_grad();loss.backward();torch.nn.utils.clip_grad_norm_(policy.parameters(),1.);policy_opt.step()
        baseline=.9*baseline+.1*score.item()
        logs.append({'step':step,'reward':score.item(),'reference_kl':kl.item(),'loss':loss.item()})
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    policy.save_pretrained(out/'policy');tok.save_pretrained(out/'policy');torch.save(reward.head.state_dict(),out/'reward_head.pt')
    # Blind human comparison of these held-out completions is required for release.
    comparisons=[]
    for r in valid:
        prompt=encode(r['prompt']+'\nAnswer: ',256)
        with torch.no_grad():
            before=reference.generate(prompt,attention_mask=torch.ones_like(prompt),max_new_tokens=64,do_sample=False,pad_token_id=tok.eos_token_id)
            after=policy.generate(prompt,attention_mask=torch.ones_like(prompt),max_new_tokens=64,do_sample=False,pad_token_id=tok.eos_token_id)
        comparisons.append({'query_id':r['query_id'],'prompt':r['prompt'],'baseline':tok.decode(before[0,prompt.shape[1]:],skip_special_tokens=True),'trained':tok.decode(after[0,prompt.shape[1]:],skip_special_tokens=True)})
    report={'algorithm':'Bradley-Terry reward head + KL-regularized REINFORCE','base_model':a.model,'seed':42,'reward_validation_pair_accuracy':acc,'train_pairs':len(train),'validation_pairs':len(valid),'steps':logs,'human_release_review':'pending','training_data_sha256':hashlib.sha256(Path(a.train).read_bytes()).hexdigest()}
    (out/'training-report.json').write_text(json.dumps(report,indent=2));(out/'heldout-comparisons.json').write_text(json.dumps(comparisons,indent=2))
    print('Saved experimental checkpoint and held-out comparisons. No production promotion performed.')
if __name__=='__main__':main()
