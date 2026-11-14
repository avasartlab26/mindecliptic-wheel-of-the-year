#!/usr/bin/env python3
"""Reproducible MindEcliptic Destiny Matrix short edit.
Fetch existing HeyGen video + Cassidy voice automatically. No generation, no credits.
Only the woman in a navy tailored suit is the continuing protagonist.
"""
from pathlib import Path
import json, math, os, subprocess, sys, urllib.request, time, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parent
MEDIA=ROOT/"media"
OUTPUT=ROOT/"output"
MEDIA.mkdir(exist_ok=True);OUTPUT.mkdir(exist_ok=True)
W,H,FPS=1080,1920,24
BASE="https://resource2.heygen.ai/videos/caa62fc65518455089da3e5988c14526/caa62fc65518455089da3e5988c14526/"
URLS={
"intro":BASE+"01a1daf0-5c0a-783e-b916-8ed390caab61.mp4",
"gold":BASE+"01a1daf2-ffcb-74ac-a6ad-bfd3cd5ffc8c.mp4",
"duo":BASE+"01a1daf9-e6a4-7962-b36c-d9d90a45e280.mp4",
"crystals":BASE+"01a1dafa-67e6-72dc-91b8-a96983fdeea6.mp4",
"wheel":BASE+"01a1dafa-c5d8-7d84-a702-3d956a757d51.mp4",
"hierophant":BASE+"01a1dafb-4a99-7563-b101-48d33f725442.mp4",
"builder":BASE+"01a1dafb-afdb-71e6-a8c7-6ef896ce9f22.mp4",
"cassidy": "https://resource2.heygen.ai/text_to_speech/caa62fc65518455089da3e5988c14526/95d52e056b7b495dab8f090b44fa2ec4/id=a1174e11ec3e49779f85787681d0c928.wav",
}

def run(cmd):
 print("RUN",cmd[0], " ".join(map(str,cmd[1:6])),flush=True)
 subprocess.run([str(a) for a in cmd],check=True)

def length(file):
 p=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",str(file)],capture_output=True,text=True,check=True)
 return float(p.stdout.strip())

def download_all():
 for name,url in URLS.items():
  ext=".wav" if name=="cassidy" else ".mp4"
  dst=MEDIA/(name+ext)
  if dst.exists() and dst.stat().st_size>200000:continue
  for attempt in range(3):
   try:
    print("Downloading already created HeyGen asset",name,flush=True)
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (MindEcliptic editor)"})
    with urllib.request.urlopen(req,timeout=150) as src,open(dst,"wb") as target:
     while True:
      block=src.read(1048576)
      if not block:break
      target.write(block)
    if dst.stat().st_size<200000:raise RuntimeError("Unexpectedly small file")
    print(name,"downloaded",dst.stat().st_size,"bytes",flush=True)
    break
   except Exception as exc:
    dst.unlink(missing_ok=True)
    if attempt==2:raise RuntimeError(f"Unable to download EXISTING asset {name}: {exc}")
    time.sleep(3+attempt*4)
 for name in URLS:
  p=MEDIA/(name+(".wav" if name=="cassidy" else ".mp4"))
  print("Verified",name,"duration",round(length(p),3),flush=True)
 duration=length(MEDIA/"cassidy.wav")
 if not 109<=duration<=115:raise RuntimeError("Cassidy narration not in expected 109-115 second range; refusing to regenerate.")
 return duration

# All times are based on the previously approved 111.88 s Cassidy narration.
# Unsafe alternatives are removed: clip 'hierophant' is cropped to the elder scholar
# and clip 'builder' ends BEFORE the unrelated woman in a white dress appears.
SHOTS=[
 (0,5.00,"intro",0,"full"),
 (5,8.49,"duo",0,"full"),
 (8.49,18.46,"crystals",0,"full"),
 (18.46,24.10,"crystals",3.20,"tight"),
 (24.10,29.87,"duo",3.30,"tight"),
 (29.87,34.87,"gold",0,"full"),
 (34.87,44.87,"wheel",0,"full"),
 (44.87,46.15,"gold",2.50,"tight"),
 (46.15,55.76,"duo",5.00,"full"),
 (55.76,61.06,"crystals",3.00,"full"),
 (61.06,66.06,"intro",0,"tight"),
 (66.06,67.94,"gold",2.5,"full"),
 (67.94,73.00,"hierophant",4.90,"scholar"),
 (73.00,77.94,"wheel",4.90,"tight"),
 (77.94,81.32,"duo",8.00,"full"),
 (81.32,83.72,"builder",0.00,"full"),
 (83.72,88.52,"wheel",2.00,"tight"),
 (88.52,91.07,"builder",0.00,"tight"),
 (91.07,92.97,"duo",12.00,"full"),
 (92.97,98.20,"duo",0,"tight"),
 (98.20,103.85,"duo",6.00,"full"),
 (103.85,111.881882,"duo",5.00,"full"),
]

def make_music(duration):
 sr=24000;N=int(sr*(duration+0.7));music=np.zeros(N,dtype=np.float32)
 bpm=98;beat=60/bpm
 def add(st,dur,freq,amp,kind):
  a=max(0,int(st*sr));b=min(N,int((st+dur)*sr))
  if b<=a:return
  t=np.arange(b-a,dtype=np.float32)/sr
  if kind=="pad":
   s=(.60*np.sin(2*np.pi*freq*t)+.25*np.sin(4*np.pi*freq*t))
   s*=np.minimum(1,t/.6)*np.minimum(1,np.maximum(0,dur-t)/.7)
  elif kind=="bell":
   s=(np.sin(2*np.pi*freq*t)+.3*np.sin(2*np.pi*freq*2.01*t))*np.exp(-4*t/max(.1,dur))
  else:
   s=np.sin(2*np.pi*freq*t)*np.exp(-2.5*t/max(.1,dur))
  ramp=np.minimum(1,t/.02)*np.minimum(1,np.maximum(0,dur-t)/.03)
  music[a:b]+=amp*s*ramp
 chords=[(164.81,196,246.94),(130.81,164.81,196),(146.83,185,220),(196,246.94,293.66)]
 span=4*beat
 for bar in range(math.ceil((duration+.7)/span)):
  st=bar*span;notes=chords[bar%4]
  for f in notes:add(st,span+.8,f,.040,"pad")
  seq=[0,1,2,1,0,1,2,1] if st<60 else [2,1,0,1,2,1,0,1]
  for k,j in enumerate(seq):add(st+k*beat/2,beat*.85,notes[j]*2,.061,"bell")
  add(st,beat*.65,notes[0]/2,.095,"bass")
 for st in [0,29,39,67.94,81.32,103.85]:
  for i,f in enumerate([392,494,587,784]):add(st+i*.30,1.8,f,.045,"bell")
 secs=np.arange(N,dtype=np.float32)/sr
 music*=np.clip(secs/1.4,0,1)*np.clip((duration-secs)/3.0,0,1)
 peak=max(float(np.max(np.abs(music))),1.0)
 a=(music/peak)
 b=np.roll(a,82)*.94;b[:82]=0
 pcm=(np.stack([a,b],axis=-1)*32767).astype("<i2")
 file=MEDIA/"original_music.wav"
 with wave.open(str(file),"wb") as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes(pcm.tobytes())
 print("Created original instrumental bed",length(file),flush=True)
 return file

BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def overlay(name, lines, y0, sizes, gold_indices=(),panel=True):
 img=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(img)
 if panel:
  top=max(0,y0-85);bottom=min(H,y0+len(lines)*130+75)
  d.rounded_rectangle((60,top,1020,bottom),radius=24,fill=(4,10,25,168),outline=(201,163,101,172),width=2)
 yy=y0
 for i,s in enumerate(lines):
  size=sizes[i];f=ImageFont.truetype(BOLD,size)
  while d.textbbox((0,0),s,font=f)[2] > 920:
   size-=1;f=ImageFont.truetype(BOLD,size)
  box=d.textbbox((0,0),s,font=f);x=int((W-(box[2]-box[0]))/2)
  d.text((x,yy),s,font=f,fill=(240,194,111,255) if i in gold_indices else (255,251,239,255),stroke_width=2,stroke_fill=(0,0,0,200))
  yy+=size+25
 p=MEDIA/(name+".png");img.save(p);return p

def make_titles():
 overlay("title",["WHAT'S THE","DIFFERENCE","BETWEEN","DESTINY MATRIX","& NUMEROLOGY?"],175,[92,100,88,84,88],(3,),True)
 overlay("numbers",["5  ·  5  ·  1  ·  2"],1310,[93],(0,),True)
 overlay("wheel_title",["10","WHEEL OF FORTUNE"],1270,[147,63],(0,),True)
 overlay("hierophant_title",["5  ·  THE HIEROPHANT"],1320,[66],(0,),True)
 overlay("builder_title",["22  ·  MASTER BUILDER"],1310,[62],(0,),True)
 overlay("fool_title",["22  ·  THE FOOL"],1310,[73],(0,),True)
 overlay("url",["mindecliptic.com"],1460,[84],(0,),True)

def render_shots(duration):
 segment_files=[]
 for i,(start,end,name,offset,mode) in enumerate(SHOTS):
  if start>=duration:break
  end=min(end,duration)
  frames=round(end*FPS)-round(start*FPS)
  if frames<=0:continue
  inp=MEDIA/(name+".mp4");out=MEDIA/(f"segment_{i:02d}.mp4")
  if mode=="scholar":
   vf="crop=580:1031:0:375,scale=1080:1920:flags=lanczos"
  elif mode=="tight":
   vf="crop=972:1728:54:96,scale=1080:1920:flags=lanczos"
  else:
   vf="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
  vf+=",setsar=1,fps=24,format=yuv420p"
  run(["ffmpeg","-y","-hide_banner","-loglevel","error","-ss",f"{offset:.3f}","-i",inp,"-vf",vf,"-frames:v",str(frames),"-an","-c:v","libx264","-preset","veryfast","-crf","22","-pix_fmt","yuv420p",out])
  if abs(length(out)-(frames/FPS))>0.09:raise RuntimeError(f"Shot {i} insufficient source frames. Refusing to conceal failure.")
  segment_files.append(out)
  print("Rendered segment",i+1,"/",len(SHOTS),flush=True)
 concat=MEDIA/"parts.txt"
 concat.write_text("".join("file '"+str(p.resolve())+"'\n" for p in segment_files))
 merged=MEDIA/"picture.mp4"
 run(["ffmpeg","-y","-hide_banner","-loglevel","error","-f","concat","-safe","0","-i",concat,"-c","copy",merged])
 return merged

def finish(picture,voice_duration):
 out=OUTPUT/"MindEcliptic_Destiny_Matrix_vs_Numerology_FINAL.mp4"
 layers=[
 ("title",0.00,8.30),
 ("numbers",8.49,18.46),
 ("wheel_title",39.0,46.0),
 ("hierophant_title",67.94,77.85),
 ("builder_title",81.32,83.70),
 ("fool_title",83.72,91.07),
 ("url",103.85,voice_duration),
 ]
 cmd=["ffmpeg","-y","-hide_banner","-loglevel","error","-i",picture,"-i",MEDIA/"cassidy.wav","-i",MEDIA/"original_music.wav"]
 for n,_,_ in layers:cmd+=["-loop","1","-framerate","24","-i",MEDIA/(n+".png")]
 filters=["[0:v]format=yuv420p[v0]"]
 for i,(n,a,b) in enumerate(layers):
  filters.append(f"[v{i}][{3+i}:v]overlay=0:0:enable='between(t,{a:.3f},{b:.3f})':eof_action=repeat[v{i+1}]")
 filters.append(f"[v{len(layers)}]format=yuv420p[vout]")
 filters.append("[1:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,asplit=2[voice][side]")
 filters.append("[2:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,volume=0.16[bed]")
 filters.append("[bed][side]sidechaincompress=threshold=0.04:ratio=4:attack=30:release=300[duck]")
 filters.append("[voice][duck]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.91[a]")
 cmd+=["-filter_complex",";".join(filters),"-map","[vout]","-map","[a]","-t",f"{voice_duration:.3f}","-r","24","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p","-c:a","aac","-ar","48000","-b:a","192k","-movflags","+faststart",out]
 run(cmd)
 final_duration=length(out)
 if abs(final_duration-voice_duration)>0.3:raise RuntimeError(f"Unexpected duration: {final_duration} vs Cassidy {voice_duration}")
 print("FINAL MASTER",out,"bytes",out.stat().st_size,"duration",final_duration,flush=True)
 return out

if __name__=="__main__":
 d=download_all()
 make_music(d);make_titles()
 picture=render_shots(d)
 finish(picture,d)
