#!/usr/bin/env python3
"""Small explanatory animation of the 4-worker Git workflow. Not a literal screen recording."""
from pathlib import Path
import argparse
from PIL import Image, ImageDraw, ImageFont

def make(path):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    W,H=1000,480
    texts=['Feature alpha','Feature beta','Feature gamma','Feature delta']
    positions=[(80,95),(80,170),(80,245),(80,320)]
    frames=[]
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',17)
    bold=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',24)
    small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
    for step in range(18):
        im=Image.new('RGB',(W,H),'white');d=ImageDraw.Draw(im)
        d.text((55,30),'Four worktrees. One integration branch.',fill=(26,38,52),font=bold)
        d.text((55,65),'Recorded experiment structure • explanatory replay, not a terminal screenshot',fill=(100,108,118),font=small)
        for j,(x,y) in enumerate(positions):
            status='editing' if step<4 else 'committed'
            col=(232,240,252) if step<4 else (222,244,232)
            d.rounded_rectangle((x,y,x+230,y+45),radius=8,fill=col,outline=(120,135,146),width=2)
            d.text((x+10,y+12),texts[j]+'  '+status,fill=(33,42,56),font=font)
            fraction=max(0,min(1,(step-3-j*2)/6))
            destx=int(330+400*fraction)
            d.line([(315,y+23),(destx,y+23)],fill=(96,120,146),width=3)
            if fraction>0:d.ellipse((destx-6,y+17,destx+6,y+29),fill=(40,112,160))
        d.rounded_rectangle((745,135,965,355),radius=10,fill=(246,247,248),outline=(150,154,160),width=2)
        d.text((763,155),'integration / main',fill=(33,42,56),font=font)
        for j,t in enumerate(texts):
            arrived=step >= 9+j*2
            col=(15,112,63) if arrived else (159,168,173)
            d.text((763,200+34*j),('✓ ' if arrived else '○ ')+t.split()[1],fill=col,font=font)
        d.text((55,420),'Parallel branches need a serial decision about the final integrated result.',fill=(56,66,74),font=font)
        frames.append(im)
    frames[0].save(path,save_all=True,append_images=frames[1:],duration=[380]*len(frames),loop=0,optimize=True)
    print('GIF generated:',path,'bytes',path.stat().st_size)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',default='../article_assets/fig_worktree_merge_replay.gif');a=p.parse_args();make(a.output)
