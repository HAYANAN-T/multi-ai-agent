"""Scientific-style, white-background figures generated directly from saved experimental data."""
from pathlib import Path
import csv,json,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from arena import NAMES,AMOUNTS,safe_at
COLORS=['#41658f','#628b9d','#bd8756','#788a4a','#93627d','#2a7067']

def make(input='results',out='generated_figures'):
 inp=Path(input);dest=Path(out);dest.mkdir(parents=True,exist_ok=True)
 summary=json.loads((inp/'summary.json').read_text());policy=summary['policies']
 def fig():
  f,ax=plt.subplots(figsize=(10.6,5.5),dpi=160); f.patch.set_facecolor('white');ax.set_facecolor('white')
  for side in ('top','right'):ax.spines[side].set_visible(False)
  ax.spines['left'].set_color('#9da9b5');ax.spines['bottom'].set_color('#9da9b5')
  ax.tick_params(colors='#2e3a46');ax.grid(axis='y',color='#e9edf2',zorder=0);ax.set_axisbelow(True)
  return f,ax
 def save(f,name):f.tight_layout(pad=2);f.savefig(dest/name,facecolor='white');plt.close(f)
 names=list(NAMES)
 f,ax=fig(); y=np.arange(len(names)); val=[policy[n]['mean_payout'] for n in names]
 ax.barh(y,val,color=COLORS,height=.59);ax.set_yticks(y,names);ax.invert_yaxis();ax.grid(axis='x',color='#e7ebf0');ax.grid(axis='y',visible=False)
 for yi,v in zip(y,val):ax.text(v+400,yi,f'${v:,.0f}',va='center',fontsize=10)
 ax.set_xlim(0,max(val)*1.21);ax.set_xlabel('Average payout per episode (USD)');ax.set_title('Same answers. Different stopping decisions.',fontweight='bold',loc='left',fontsize=15,pad=16)
 ax.text(.01,-.17,'1,200 paired simulations per policy. The mean is sensitive to rare $1m outcomes.',transform=ax.transAxes,fontsize=9,color='#53677b');save(f,'fig_01_mean_payout_white.png')
 f,ax=fig();draw=[]
 with (inp/'tournaments.csv').open(newline='') as z:rows=list(csv.DictReader(z))
 for n in names:
  vals=[int(r[f'{n}_payout']) for r in rows];total=len(vals)
  draw.append([sum(v<1000 for v in vals)/total,sum(1000<=v<32000 for v in vals)/total,sum(32000<=v<1000000 for v in vals)/total,sum(v>=1000000 for v in vals)/total])
 arr=np.array(draw);left=np.zeros(6)
 ax.grid(axis='y',visible=False);ax.grid(axis='x',color='#edf0f5')
 for j,(lab,col) in enumerate(zip(['Below $1k','$1k–$31,999','$32k–$999,999','$1 million'],['#cbd4e3','#7497a9','#3f7967','#b99550'])):
  ax.barh(np.arange(6),arr[:,j],left=left,height=.62,color=col,label=lab);left+=arr[:,j]
 ax.set_yticks(range(6),names);ax.invert_yaxis();ax.set_xlim(0,1);ax.set_xlabel('Share of episodes');ax.set_xticks(np.linspace(0,1,6),[f'{x:.0%}' for x in np.linspace(0,1,6)]);ax.set_title('The prize distribution tells a different story',loc='left',fontweight='bold',fontsize=15,pad=16)
 ax.legend(ncol=4,loc='lower center',bbox_to_anchor=(.52,-.31),frameon=False,fontsize=9);save(f,'fig_02_payout_distribution_white.png')
 with (inp/'calibration.csv').open(newline='') as z:cal=list(csv.DictReader(z))
 f,ax=fig();ax.plot([.2,1],[.2,1],linestyle='--',color='#777777',label='Perfect calibration')
 for field,color,label in [('calibrated_conf','#2a7067','Fitted confidence'),('inflated_conf','#bc655e','Same scores, +20 confidence points')]:
  conf=np.array([float(r[field]) for r in cal]);ys=np.array([int(r['correct']) for r in cal]);xs=[];acc=[];nums=[]
  for j in range(10):
   m=(conf>=j/10)&(conf<(j+1)/10 if j<9 else conf<=1)
   if m.sum()>=20:xs.append(conf[m].mean());acc.append(ys[m].mean());nums.append(m.sum())
  ax.plot(xs,acc,'o-',color=color,label=label,linewidth=2,markersize=6)
 ax.set(xlim=(.2,1.02),ylim=(.2,1.02),xlabel='Stated probability of correctness',ylabel='Observed fraction correct');ax.set_title('Confidence should predict how often answers are right',loc='left',fontweight='bold',fontsize=14,pad=16)
 ax.legend(frameon=False,fontsize=9,loc='upper left');save(f,'fig_03_calibration_white.png')
 with (inp/'lifeline_ablation.csv').open(newline='') as z:abl=list(csv.DictReader(z))
 d=np.array([int(r['difference']) for r in abl]);f,ax=fig();ax.grid(axis='y',visible=False)
 counts=[(d<0).mean(),(d==0).mean(),(d>0).mean()];labels=['Help was worse','Same payout','Help was better'];color=['#bf6d62','#bec8d4','#33846d']
 for i in range(3):ax.barh(i,counts[i],color=color[i],height=.65);ax.text(counts[i]+.01,i,f'{counts[i]*100:.1f}%',va='center')
 ax.set_xlim(0,.87);ax.set_yticks(range(3),labels);ax.invert_yaxis();ax.set_xticks(np.linspace(0,.8,5),[f'{x:.0%}' for x in np.linspace(0,.8,5)])
 ax.set_xlabel('Share of 1,200 paired episodes');ax.set_title('Did lifelines change the outcome for the same evidence?',loc='left',fontweight='bold',fontsize=14,pad=16)
 save(f,'fig_04_lifeline_ablation_white.png')
 with (inp/'lifeline_events.csv').open(newline='') as z:events=list(csv.DictReader(z))
 f,ax=fig();life=['50:50','AUDIENCE','FRIEND'];cols=['#43829c','#be9961','#628b75'];x=np.arange(len(names));bottom=np.zeros(6)
 for ll,col in zip(life,cols):
  y=np.array([sum(r['policy']==n and r['lifeline']==ll for r in events)/summary['episodes'] for n in names])
  ax.bar(x,y,bottom=bottom,color=col,label=ll,width=.63);bottom+=y
 ax.set_xticks(x,names);ax.set_ylabel('Mean lifelines called per episode');ax.set_title('Help was not used equally, or at the same price level',loc='left',fontweight='bold',fontsize=14,pad=16)
 ax.legend(frameon=False,ncol=3);save(f,'fig_05_lifeline_use_white.png')
 f,ax=fig();threshold=[]
 for i,a in enumerate(AMOUNTS):
  won=AMOUNTS[i-1] if i else 0;s=safe_at(won)
  threshold.append((won-s)/(a-s) if a>s else 0)
 ax.step(np.arange(1,16),threshold,where='mid',linewidth=2.5,color='#2a7067');ax.plot(np.arange(1,16),threshold,'o',color='#2a7067')
 ax.set(ylim=(-.04,1.05),xlim=(.4,15.6),xlabel='Question number',ylabel='Minimum probability for one-step EV to beat walking');ax.set_xticks(range(1,16));ax.set_title('The financially rational guess threshold changes with the prize ladder',loc='left',fontweight='bold',fontsize=12.5,pad=16)
 ax.axvline(6,color='#ad9b75',linestyle=':',linewidth=1);ax.axvline(11,color='#ad9b75',linestyle=':',linewidth=1)
 ax.annotate('No downside immediately\nafter a guaranteed milestone',xy=(6,0),xytext=(7.2,.21),fontsize=9,arrowprops={'arrowstyle':'->','color':'#444444'})
 save(f,'fig_06_risk_threshold_white.png')
 print('Saved six data-derived white-background Matplotlib figures')
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--input',default='results');p.add_argument('--output',default='generated_figures');a=p.parse_args();make(a.input,a.output)
