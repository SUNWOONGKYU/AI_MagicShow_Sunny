"""S4 — FFmpeg compose: scene PNGs + zoompan + concat + audio + tail-pad 8s.
Outputs: output/videos/v1/MBO_FINAL_v1.mp4 (1920x1080@30fps, CBR 2500k)
"""
import json
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

PROJ = Path(r"G:\내 드라이브\333_자료공유폴더\Sunny_Magic_Show\AI_Magic50\videos\10_MBO")
SCENES_DIR = PROJ / "02_assets" / "scenes"
TIMING = json.loads((PROJ / "output" / "scene_timing.json").read_text(encoding='utf-8'))
AUDIO = PROJ / "01_voice" / "narration_v1_leadin.mp3"
OUT_DIR = PROJ / "output" / "videos" / "v1"
OUT_DIR.mkdir(parents=True, exist_ok=True)
FINAL = OUT_DIR / "MBO_FINAL_v1.mp4"
WORK = OUT_DIR / "_work"
WORK.mkdir(exist_ok=True)

FPS = 30
TAIL_PAD = 8.0

# Ken Burns modes — cycle through
ZP_MODES = [
    "zoompan=z='min(zoom+0.0015,1.25)':d={d}:s=1920x1080:fps=30",  # zin-c
    "zoompan=z='if(eq(on,1),1.25,max(zoom-0.0015,1.0))':d={d}:s=1920x1080:fps=30",  # zout-c
    "zoompan=z='min(zoom+0.0012,1.20)':x='iw*0.10*on/{frames}':d={d}:s=1920x1080:fps=30",  # pan-l
    "zoompan=z='min(zoom+0.0012,1.20)':x='iw-iw*0.10*on/{frames}-iw/zoom':d={d}:s=1920x1080:fps=30",  # pan-r
    "zoompan=z='min(zoom+0.0015,1.25)':x='0':y='0':d={d}:s=1920x1080:fps=30",  # zin-lu
    "zoompan=z='min(zoom+0.0015,1.25)':x='iw-iw/zoom':y='ih-ih/zoom':d={d}:s=1920x1080:fps=30",  # zin-rd
]

# Step 1: render each scene as a video clip
print("[INFO] Step 1: rendering scene clips...")
clips = []
for i, sc in enumerate(TIMING):
    n = sc["scene"]
    dur = sc["duration"]
    if dur < 0.5:
        dur = 0.5
    img = SCENES_DIR / f"ai_scene_{n:02d}.png"
    out = WORK / f"clip_{n:02d}.mp4"
    frames = max(int(dur * FPS), 30)
    mode = ZP_MODES[i % len(ZP_MODES)].format(d=frames, frames=frames)
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", str(img),
        "-vf", f"{mode},format=yuv420p",
        "-t", f"{dur:.3f}",
        "-c:v", "libx264", "-b:v", "2500k", "-minrate", "2500k", "-maxrate", "2500k",
        "-bufsize", "5000k", "-r", str(FPS), "-pix_fmt", "yuv420p",
        "-an", str(out),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    if r.returncode != 0:
        print(f"[ERR scene {n}] {r.stderr[-500:]}")
        sys.exit(1)
    clips.append(out)
    print(f"[clip {n:02d}] {dur:.2f}s mode={i%6}", flush=True)

# Step 2: tail-pad clip (last scene image extended for 8s as tail)
print("[INFO] Step 2: tail pad clip...")
tail_img = SCENES_DIR / f"ai_scene_{TIMING[-1]['scene']:02d}.png"
tail_clip = WORK / "clip_tail.mp4"
cmd = [
    "ffmpeg", "-y", "-loop", "1", "-i", str(tail_img),
    "-vf", f"zoompan=z='min(zoom+0.0008,1.10)':d={int(TAIL_PAD*FPS)}:s=1920x1080:fps={FPS},format=yuv420p",
    "-t", f"{TAIL_PAD}",
    "-c:v", "libx264", "-b:v", "2500k", "-minrate", "2500k", "-maxrate", "2500k",
    "-bufsize", "5000k", "-r", str(FPS), "-pix_fmt", "yuv420p",
    "-an", str(tail_clip),
]
subprocess.run(cmd, capture_output=True, check=True)
clips.append(tail_clip)

# Step 3: concat list
print("[INFO] Step 3: concat...")
list_txt = WORK / "concat.txt"
list_txt.write_text("\n".join(f"file '{c.as_posix()}'" for c in clips), encoding='utf-8')
concat_mp4 = WORK / "concat.mp4"
subprocess.run([
    "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_txt),
    "-c", "copy", str(concat_mp4),
], capture_output=True, check=True)

# Step 4: tail-pad audio (8s anullsrc concat)
print("[INFO] Step 4: tail-pad audio...")
audio_padded = WORK / "audio_padded.mp3"
subprocess.run([
    "ffmpeg", "-y",
    "-i", str(AUDIO),
    "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono:d={TAIL_PAD}",
    "-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1[out]",
    "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "192k",
    str(audio_padded),
], capture_output=True, check=True)

# Step 5: mux video + audio
print("[INFO] Step 5: mux final...")
subprocess.run([
    "ffmpeg", "-y",
    "-i", str(concat_mp4),
    "-i", str(audio_padded),
    "-c:v", "copy",
    "-c:a", "aac", "-b:a", "192k",
    "-shortest",
    str(FINAL),
], capture_output=True, check=True)

# Verify
probe = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration:stream=codec_type,width,height,r_frame_rate,bit_rate","-of","json",str(FINAL)],
                      capture_output=True, text=True)
print(f"[OK] {FINAL}")
print(probe.stdout)
size_mb = FINAL.stat().st_size / 1024 / 1024
print(f"[SIZE] {size_mb:.2f} MB")
