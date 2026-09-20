"""Fetch a bounded HotpotQA subset. Context only in corpus; gold answers separate."""
import argparse,hashlib,json,urllib.request,urllib.parse
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BIOGRAPHIES={'Allie Goertz','Peggy Seeger','Li Na','Henri Leconte','Steffi Graf','Jonathan Stark (tennis)','Pam Teeguarden','Nathalia Ramos','Bruce Harwood','Annette Bening','Kevin Bacon','John Lithgow'}
def convert(rows):
    docs={};evaluation=[]
    for record in rows:
        row=record.get('row',record)
        for title,sentences in zip(row['context']['title'],row['context']['sentences']):
            ident='hp-'+hashlib.sha256(title.encode()).hexdigest()[:24]
            docs.setdefault(ident,{'id':ident,'title':title,'text':' '.join(sentences),'url':'https://en.wikipedia.org/wiki/'+urllib.parse.quote(title.replace(' ','_')),'kind':'person' if title in BIOGRAPHIES else 'article','dataset':'hotpotqa/hotpot_qa','license':'CC-BY-SA-4.0','snapshot':'Historical HotpotQA corpus; not current verification'})
        evaluation.append({'id':row['id'],'question':row['question'],'answer':row['answer'],'supporting_titles':list(dict.fromkeys(row['supporting_facts']['title']))})
    return list(docs.values()),evaluation
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--rows',type=int,default=100);a.add_argument('--input');args=a.parse_args()
    if not 1<=args.rows<=1000:raise SystemExit('Choose 1–1000 rows')
    if args.input:raw=json.load(open(args.input))['rows']
    else:
        raw=[]
        for offset in range(0,args.rows,100):
            params=urllib.parse.urlencode({'dataset':'hotpotqa/hotpot_qa','config':'distractor','split':'train','offset':offset,'length':min(100,args.rows-offset)})
            with urllib.request.urlopen('https://datasets-server.huggingface.co/rows?'+params,timeout=60) as r:raw+=json.load(r)['rows']
    docs,evaluation=convert(raw)
    (ROOT/'data').mkdir(exist_ok=True)
    for filename,data in [('corpus.json',docs),('evaluation.json',evaluation)]:
        (ROOT/'data'/filename).write_text(json.dumps(data,ensure_ascii=False,indent=2))
    print(json.dumps({'documents':len(docs),'questions':len(evaluation),'people':sum(d['kind']=='person' for d in docs)}))
