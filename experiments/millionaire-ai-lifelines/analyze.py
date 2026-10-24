"""Recompute independent paper figures and lifeline inspection CSV from seeds."""
import argparse,csv,json
from collections import Counter,defaultdict
from pathlib import Path
from statistics import mean
import numpy as np
from arena import NAMES,play,train_calibrator,bootstrap_paired,csv_write

def main():
 p=argparse.ArgumentParser();p.add_argument('--input',default='results');p.add_argument('--episodes',type=int,default=1200);p.add_argument('--seed',type=int,default=2026);a=p.parse_args()
 dest=Path(a.input);model=train_calibrator()
 lifeline_events=[];run_status=[];belief_changes=[]
 for seed in range(a.seed,a.seed+a.episodes):
  for name in NAMES:
   player=play(seed,name,model,detail=True)
   for ev in player.log:
    if ev['action'] in ('50:50','AUDIENCE','FRIEND'):
     lifeline_events.append({'seed':seed,'policy':name,'round':ev['question_number'],'lifeline':ev['action'],'confidence_before':ev['estimated_confidence'],'confidence_after':max(ev['beliefs_after']), 'audience_misconception':int(ev['help'].get('correlated_misconception',False)), 'audience_majority_wrong':int(ev['action']=='AUDIENCE' and max(range(4),key=lambda i:ev['help']['counts'][i])!=ev['correct_index']) if ev['action']=='AUDIENCE' else ''})
   run_status.append({'seed':seed,'policy':name,'exit':player.status,'prize':player.final,'used':player.lifelines})
 csv_write(dest/'lifeline_events.csv',lifeline_events)
 by=defaultdict(list)
 for row in lifeline_events:by[(row['policy'],row['lifeline'])].append(row)
 summary={}
 for (policy,life), rows in by.items():
  summary[f'{policy}_{life}']={'n':len(rows),'mean_before':round(mean(float(x['confidence_before']) for x in rows),3),'mean_after':round(mean(float(x['confidence_after']) for x in rows),3),'round_median':int(np.median([int(x['round']) for x in rows]))}
 aud=[x for x in lifeline_events if x['lifeline']=='AUDIENCE']
 summary['audience']={'n':len(aud),'misconception_rate':round(mean(int(x['audience_misconception']) for x in aud),3),'wrong_majority_rate':round(mean(int(x['audience_majority_wrong']) for x in aud),3)} if aud else {}
 (dest/'lifeline_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
