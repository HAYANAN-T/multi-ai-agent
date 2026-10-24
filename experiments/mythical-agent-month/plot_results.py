#!/usr/bin/env python3
"""Generate white-background scientific charts from saved measurements; no synthetic graphics."""
import argparse
import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def plot(results: Path, output: Path):
    output.mkdir(parents=True, exist_ok=True)
    rows=[]
    with (results/'raw_runs.csv').open(newline='',encoding='utf-8') as f:
        for r in csv.DictReader(f):
            for k in ('workers','trial','conflicts'):
                r[k]=int(r[k])
            for k in ('elapsed_seconds','prepare_seconds','worker_wall_seconds','worker_effort_seconds','integrate_seconds','final_test_seconds'):
                r[k]=float(r[k])
            rows.append(r)
    s=json.loads((results/'summary.json').read_text(encoding='utf-8'))
    labels=('1 worker','2 workers','4 workers')
    x=np.arange(3)
    fig,ax=plt.subplots(figsize=(9.4,5.6))
    for ci,typ in enumerate(('independent','coupled')):
        coords=x + (ci-.5)*.18
        for j,worker_n in enumerate((1,2,4)):
            ys=np.array([r['elapsed_seconds'] for r in rows if r['case']==typ and r['workers']==worker_n])
            ax.scatter(np.full(len(ys),coords[j])+np.linspace(-.035,.035,len(ys)),ys,s=18,alpha=.45)
            ax.plot([coords[j]-.075,coords[j]+.075],[np.median(ys)]*2,linewidth=2.8,color='black')
    ax.set_xticks(x,labels)
    ax.set_ylabel('Elapsed time to passing integration (seconds)')
    ax.set_title('The clock includes integration, not just parallel writing',loc='left',weight='bold',pad=16)
    ax.grid(axis='y',alpha=.22)
    ax.spines[['top','right']].set_visible(False)
    ax.text(.01,-.18,'Each dot = one measured run. Black line = condition median. Six conditions, scripted workers.',
            transform=ax.transAxes,fontsize=9)
    fig.tight_layout(rect=[0,.05,1,1]);fig.savefig(output/'fig_01_wall_time_white.png',dpi=170);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9.1,5.3))
    width=.34
    indep=[next(q['median_conflicts'] for q in s if q['case']=='independent' and q['workers']==n) for n in (1,2,4)]
    coupled=[next(q['median_conflicts'] for q in s if q['case']=='coupled' and q['workers']==n) for n in (1,2,4)]
    a=ax.bar(x-width/2,indep,width,label='Independent files')
    b=ax.bar(x+width/2,coupled,width,label='Shared registry')
    ax.bar_label(a,fmt='%.0f',padding=3);ax.bar_label(b,fmt='%.0f',padding=3)
    ax.set_xticks(x,labels);ax.set_ylim(0,4)
    ax.set_ylabel('Text merge conflicts per run')
    ax.set_title('Worktree isolation did not prevent merge conflicts',loc='left',weight='bold',pad=16)
    ax.legend(frameon=False);ax.spines[['top','right']].set_visible(False)
    ax.grid(axis='y',alpha=.16)
    fig.tight_layout();fig.savefig(output/'fig_02_conflicts_white.png',dpi=170);plt.close(fig)
    fig,ax=plt.subplots(figsize=(10.5,5.9))
    entries=[next(q for q in s if q['case']==typ and q['workers']==n) for typ in ('independent','coupled') for n in (1,2,4)]
    names=['Independent\n1','Independent\n2','Independent\n4','Shared\n1','Shared\n2','Shared\n4']
    keys=[('median_prepare_seconds','Set up worktrees'),('median_worker_wall_seconds','Worker wall-clock phase'),('median_integrate_seconds','Cherry-pick + resolve'),('median_final_test_seconds','Final verification')]
    bottoms=np.zeros(6)
    for key,label in keys:
        val=np.array([r[key] for r in entries])
        ax.bar(np.arange(6),val,bottom=bottoms,label=label,width=.67)
        bottoms+=val
    ax.set_xticks(np.arange(6),names)
    ax.set_ylabel('Median phase time, seconds (approximate sum)')
    ax.set_title('What still happens after the workers finish?',loc='left',weight='bold',pad=14)
    ax.spines[['top','right']].set_visible(False)
    ax.legend(frameon=False,ncol=2,loc='upper right',fontsize=9)
    ax.grid(axis='y',alpha=.16)
    ax.text(0,-.24,'Medians are taken separately per phase; their sum need not equal the median total. Cleanup overhead is excluded.',transform=ax.transAxes,fontsize=9)
    fig.tight_layout(rect=[0,.07,1,1]);fig.savefig(output/'fig_03_time_breakdown_white.png',dpi=165);plt.close(fig)
    # A simple correct schematic, never confused with measured time or photographed evidence.
    from matplotlib.patches import FancyBboxPatch
    fig,ax=plt.subplots(figsize=(10.5,4.8));ax.axis('off')
    def node(x,y,w,text,fc='white'):
        p=FancyBboxPatch((x,y),w,.54,boxstyle='round,pad=.08,rounding_size=.06',facecolor=fc,edgecolor='#5c6471',linewidth=1.2)
        ax.add_patch(p);ax.text(x+w/2,y+.27,text,ha='center',va='center',fontsize=10)
    node(.1,1.2,2.6,'Worker A: $10.00 value')
    node(.1,.12,2.6,'Worker B: cents ÷ 100')
    node(3.8,.68,2.0,'Git merges cleanly')
    node(6.9,.68,2.8,'Integrated output: $0.10','#fff0ef')
    for start,end in [((2.8,1.47),(3.7,.94)),((2.8,.39),(3.7,.94)),((5.9,.94),(6.8,.94))]:
        ax.annotate('',xy=end,xytext=start,arrowprops={'arrowstyle':'->','lw':1.4})
    ax.text(.1,2.1,'A semantic conflict Git cannot see',fontsize=17,weight='bold')
    ax.text(.1,-.48,'Constructed, executed counterexample: two independent test suites pass; an end-to-end contract check fails.',fontsize=9)
    ax.set_xlim(-.1,10);ax.set_ylim(-.7,2.55)
    fig.tight_layout();fig.savefig(output/'fig_04_semantic_conflict_white.png',dpi=170);plt.close(fig)
    print('Charts generated:',*[str(p.name) for p in output.glob('fig_*')],sep='\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--results',default='results');p.add_argument('--output',default='../article_assets');a=p.parse_args();plot(Path(a.results),Path(a.output))
