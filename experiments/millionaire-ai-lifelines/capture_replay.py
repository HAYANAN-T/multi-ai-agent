"""Actual browser captures of replay states, saved outside code-only repository.
Usage: python capture_replay.py --viewer viewer/millionaire_replay.html --output ../gifs
"""
from pathlib import Path
import argparse, io
from PIL import Image,ImageOps
from playwright.sync_api import sync_playwright

SEQUENCES={
 '01_thirty_seconds_to_answer':[(5,0),(5,1),(5,2),(5,3)],
 '02_the_fifty_fifty':[(5,4),(5,5),(5,6),(5,7)],
 '03_phone_a_friend':[(5,7),(5,8),(5,9),(5,10)],
 '04_ask_the_audience':[(5,9),(5,10),(5,11)],
 '05_walk_or_guess':[(5,10),(5,11),(0,4),(0,5)],
}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--viewer',default='viewer/millionaire_replay.html');ap.add_argument('--output',default='generated_gifs');a=ap.parse_args()
 dest=Path(a.output);dest.mkdir(exist_ok=True,parents=True)
 html=Path(a.viewer).read_text(encoding='utf-8')
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-gpu'])
  page=browser.new_page(viewport={'width':1280,'height':880},device_scale_factor=1)
  page.set_content(html,wait_until='load')
  page.screenshot(path=str(dest/'studio_screenshot.png'),full_page=True)
  for name,items in SEQUENCES.items():
   imgs=[]
   for agent,step in items:
    page.evaluate('([a,s])=>window.go(a,s)',[agent,step])
    by=page.screenshot(full_page=True)
    im=Image.open(io.BytesIO(by)).convert('RGB')
    size=(900,int(im.height*900/im.width))
    im=im.resize(size,Image.Resampling.LANCZOS)
    imgs.append(im.quantize(colors=120,method=Image.Quantize.FASTOCTREE))
   fp=dest/(name+'.gif')
   imgs[0].save(fp,save_all=True,append_images=imgs[1:],duration=[1100]*(len(imgs)-1)+[1900],loop=0,optimize=True,disposal=2)
   print(fp.name,round(fp.stat().st_size/1024),'KB')
  page.evaluate('window.go(5,5)')
  page.screenshot(path=str(dest/'screenshot_5050.png'),full_page=True)
  page.evaluate('window.go(5,10)')
  page.screenshot(path=str(dest/'screenshot_audience.png'),full_page=True)
  page.evaluate('window.go(5,11)')
  page.screenshot(path=str(dest/'screenshot_walk.png'),full_page=True)
  browser.close()
if __name__=='__main__':main()
