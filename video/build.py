#!/usr/bin/env python3
"""Build a 104-second narrated MindEcliptic Wheel of the Year vertical video.
All nine moving scenes and Expressive Evan speech come from already-generated HeyGen assets.
Exactly ONE Celtic instrumental composition runs from first to last frame.
Does not change the live calendar or its HTML/CSS/JS source.
"""
from __future__ import annotations
import base64, json, os, subprocess, sys, urllib.request
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
MEDIA=BASE/"media";MEDIA.mkdir(exist_ok=True)
OUT=BASE/"output";OUT.mkdir(exist_ok=True)
W,H,FPS=720,1280,24
URLS=json.loads(r'''{"intro":"https://resource2.heygen.ai/videos/caa62fc65518455089da3e5988c14526/caa62fc65518455089da3e5988c14526/01a170d4-3844-7c0b-ad20-23282348d8b1.mp4","yule":"https://resource2.heygen.ai/videos/caa62fc65518455089da3e5988c14526/caa62fc65518455089da3e5988c14526/01a170fb-fa38-7f06-a53a-7394db756822.mp4","imbolc":"https://resource2.heygen.ai/videos/caa62fc65518455089da3e5988c14526/caa62fc65518455089da3e5988c14526/01a170fc-021d-77ba-a908-d53ef5fa21e9.mp4","ostara":"https://resource2.heygen.ai/videos/caa62fc65518455089da3e5988c14526/caa62fc65518455089da3e5988c14526/01a170fc-09eb-7e33-80b8-717b43373ed3.mp4","beltane":"https://resource2.heygen.ai/videos/caa62fc65518455089da3e5988c14526/caa62fc65518455089da3e5988c14526/01a170f3-6df3-7c52-82b7-cdef3d9df332.mp4","litha":"https://resource2.heygen.ai/videos/caa62fc65518455089da3e5988c14526/caa62fc65518455089da3e5988c14526/01a170fc-4c6f-7537-b4d8-cb3bda7eb2d2.mp4","lammas":"https://resource2.heygen.ai/videos/caa62fc65518455089da3e5988c14526/caa62fc65518455089da3e5988c14526/01a170fc-581b-7498-9cfd-2adde7c0eee7.mp4","mabon":"https://resource2.heygen.ai/videos/caa62fc65518455089da3e5988c14526/caa62fc65518455089da3e5988c14526/01a170fc-608e-7e5b-9dc4-2297a1858b93.mp4","samhain":"https://resource2.heygen.ai/videos/caa62fc65518455089da3e5988c14526/caa62fc65518455089da3e5988c14526/01a170fc-c57d-71ab-8193-43d3e5030bcf.mp4","voice":"https://resource2.heygen.ai/text_to_speech/caa62fc65518455089da3e5988c14526/3c2a9d4239094aa2bbbdd02d843aa868/id=1efe7e00-c46f-4ce0-a2cf-f8d1921be38c.wav","music":"https://heygen-product.s3-accelerate.amazonaws.com/gen_os/music/8c734200fa8c437b89534e23b8e23306.mp3?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIA3FLD4S3AS7WYJKBK%2F20261025%2Fus-east-2%2Fs3%2Faws4_request&X-Amz-Date=20261025T030556Z&X-Amz-Expires=604800&X-Amz-SignedHeaders=host&X-Amz-Signature=4922db98b18869662b13d22a376e2655ed926b24372a5a910c6bb0126dfd8d2b"}''')

def download_all():
 for name,url in URLS.items():
  dst=MEDIA / (name+(".wav" if name=="voice" else ".mp3" if name=="music" else ".mp4"))
  if dst.exists() and dst.stat().st_size>100000: continue
  print("Downloading",name,flush=True)
  req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 MindEcliptic-Video-Editor"})
  with urllib.request.urlopen(req,timeout=120) as response, open(dst,"wb") as file:
   while True:
    chunk=response.read(1024*1024)
    if not chunk: break
    file.write(chunk)
  print("Downloaded",name,round(dst.stat().st_size/1e6,2),"MB",flush=True)

def record_site():
 dst=MEDIA/"calendar_demo.webm"
 if dst.exists() and dst.stat().st_size>500000:return dst
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=["--allow-file-access-from-files","--disable-web-security","--no-sandbox"])
  ctx=browser.new_context(viewport={"width":720,"height":1280},record_video_dir=str(MEDIA),record_video_size={"width":720,"height":1280},device_scale_factor=1,reduced_motion="reduce")
  page=ctx.new_page()
  html=(ROOT/"index.html").read_text()
  css=(ROOT/"styles.css").read_text()
  js=(ROOT/"app.js").read_text()
  html=html.replace('<link rel="stylesheet" href="./styles.css">',"<style>"+css+"</style>")
  html=html.replace('<script src="./app.js" defer></script>',"<script>"+js+"</script>")
  for img in (ROOT/"assets").glob("*.webp"):
   html=html.replace("./assets/"+img.name,"data:image/webp;base64,"+base64.b64encode(img.read_bytes()).decode("ascii"))
  page.set_content(html,wait_until="load",timeout=45000)
  page.wait_for_timeout(1500)
  page.locator("#year-picker").select_option("2035")
  page.wait_for_timeout(1700)
  page.locator('.rim-label[data-index="3"]').click()
  page.wait_for_timeout(3300)
  page.locator("#detail-panel").scroll_into_view_if_needed()
  page.wait_for_timeout(1800)
  page.locator("details.info-accordion summary").first.click()
  page.wait_for_timeout(2300)
  page.locator("details.info-accordion summary").first.click()
  page.wait_for_timeout(1000)
  page.evaluate('window.scrollTo({top:0,behavior:"smooth"})')
  page.wait_for_timeout(1800)
  page.locator("#next-sabbat").click()
  page.wait_for_timeout(2600)
  page.locator("#year-picker").select_option("2028")
  page.wait_for_timeout(1500)
  page.locator('.rim-label[data-index="7"]').click()
  page.wait_for_timeout(1900)
  page.locator("#detail-panel").scroll_into_view_if_needed()
  page.wait_for_timeout(2500)
  page.evaluate('window.scrollTo({top:0,behavior:"smooth"})')
  page.wait_for_timeout(2200)
  vid=page.video
  ctx.close()
  if vid:os.replace(vid.path(),dst)
  browser.close()
 print("Recorded real calendar",dst,flush=True)
 return dst

class Clip:
 def __init__(self,path):
  self.cap=cv2.VideoCapture(str(path))
  if not self.cap.isOpened():raise RuntimeError("Cannot open "+str(path))
  self.fps=self.cap.get(cv2.CAP_PROP_FPS) or 24
  self.total=int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
  self.last=-1;self.frame=None;self.small=None
 def get(self,t):
  target=max(0,min(self.total-1,int(t*self.fps)))
  if target<self.last:
   self.cap.set(cv2.CAP_PROP_POS_FRAMES,target)
   ok,self.frame=self.cap.read();self.last=target;self.small=None
  while self.last<target:
   ok,frame=self.cap.read()
   if not ok:break
   self.frame=frame;self.last+=1;self.small=None
  if self.frame is None:raise RuntimeError("Cannot decode video frame")
  if self.small is None:
   h,w=self.frame.shape[:2]
   # center crop, preserving vertical source composition
   if w/h>W/H:
    neww=int(h*W/H);self.frame=self.frame[:,(w-neww)//2:(w+neww)//2];h,w=self.frame.shape[:2]
   else:
    newh=int(w*H/W);self.frame=self.frame[(h-newh)//2:(h+newh)//2,:];h,w=self.frame.shape[:2]
   self.small=cv2.resize(self.frame,(W,H),interpolation=cv2.INTER_AREA)
  return self.small

def cta(frame):
 img=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)).convert("RGBA")
 shade=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(shade)
 for y in range(720,H):
  alpha=int(210*(y-720)/(H-720))
  d.line([(0,y),(W,y)],fill=(3,7,15,alpha))
 img=Image.alpha_composite(img,shade);d=ImageDraw.Draw(img)
 fontpath="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
 boldpath="/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
 def centered(s,y,size,bold=False):
  font=ImageFont.truetype(boldpath if bold else fontpath,size)
  box=d.textbbox((0,0),s,font=font)
  x=(W-(box[2]-box[0]))/2
  d.text((x,y),s,font=font,fill="#f5e7be",stroke_width=2,stroke_fill="#171720")
 centered("MindEcliptic",935,63,True)
 centered("mindecliptic.com",1046,44)
 centered("Explore the Wheel of the Year",1144,30)
 return cv2.cvtColor(np.array(img.convert("RGB")),cv2.COLOR_RGB2BGR)

def render():
 clips={n:Clip(MEDIA/(n+(".webm" if n=="demo" else ".mp4"))) for n in [*"intro yule imbolc ostara beltane litha lammas mabon samhain".split(),"demo"]}
 times=[
 ("intro",0,13.68),("yule",13.68,19.30),("imbolc",19.30,24.82),("ostara",24.82,30.20),
 ("beltane",30.20,35.24),("litha",35.24,42.74),("lammas",42.74,48.72),
 ("mabon",48.72,55.34),("samhain",55.34,61.10),("intro",61.10,69.68),
 ("demo",69.68,94.52),("cta",94.52,104)]
 silent=MEDIA/"visual_edit.mp4"
 cmd=["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pixel_format","bgr24","-video_size",f"{W}x{H}","-framerate",str(FPS),"-i","-","-an","-c:v","libx264","-preset","veryfast","-crf","22","-pix_fmt","yuv420p","-movflags","+faststart",str(silent)]
 enc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 intro_frame=clips["intro"].get(0).copy()
 def grab(i,t):
  name,a,b=times[i]
  if name=="cta":return cta(intro_frame)
  local=max(0,t-a)
  return clips[name].get(local)
 count=int(104*FPS)
 for frame_no in range(count):
  t=frame_no/FPS
  i=0
  while i<len(times)-1 and t>=times[i][2]:i+=1
  f=grab(i,t)
  if i<len(times)-1 and t>times[i][2]-.55:
   g=(t-(times[i][2]-.55))/.55
   f=cv2.addWeighted(f,1-g,grab(i+1,times[i][2]),g,0)
  enc.stdin.write(f.tobytes())
  if frame_no%240==0:print("Rendered",int(t),"seconds",flush=True)
 enc.stdin.close()
 if enc.wait():raise RuntimeError("Rendering failed")
 for item in clips.values():item.cap.release()
 final=OUT/"MindEcliptic_Wheel_of_the_Year_DRAFT_104sec_720x1280.mp4"
 # Original approved Expressive Evan narration + exactly one continuous Celtic soundtrack.
 audio="[2:a]atempo=1.153846,volume=0.19,atrim=duration=104,afade=t=out:st=101.8:d=2.2[m];[1:a]volume=1,apad,atrim=duration=104[v];[v][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.96[a]"
 subprocess.run(["ffmpeg","-y","-loglevel","error","-i",str(silent),"-i",str(MEDIA/"voice.wav"),"-i",str(MEDIA/"music.mp3"),"-filter_complex",audio,"-map","0:v","-map","[a]","-c:v","copy","-c:a","aac","-b:a","192k","-t","104","-movflags","+faststart",str(final)],check=True)
 print("FINAL",final,"bytes",final.stat().st_size,flush=True)

if __name__=="__main__":
 download_all()
 demo=record_site()
 if demo!=MEDIA/"demo.webm":os.replace(demo,MEDIA/"demo.webm")
 render()
