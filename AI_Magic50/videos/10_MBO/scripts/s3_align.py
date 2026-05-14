"""S3-A4 — Align scenes to Whisper segments via anchor regex.

Reads: output/segments.json + 00_script/anchors.json
Writes: output/scene_timing.json
Strategy: Match each anchor to a Whisper cue. Linear interpolate misses.
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

PROJ = Path(r"G:\내 드라이브\333_자료공유폴더\Sunny_Magic_Show\AI_Magic50\videos\10_MBO")
SEG = json.loads((PROJ / "output" / "segments.json").read_text(encoding='utf-8'))
ANCH = json.loads((PROJ / "00_script" / "anchors.json").read_text(encoding='utf-8'))["anchors"]

# Probe mp3 duration
import subprocess
mp3 = PROJ / "01_voice" / "narration_v1_leadin.mp3"
probe = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",str(mp3)],
                       capture_output=True, text=True)
total_dur = float(probe.stdout.strip())
print(f"[INFO] mp3 duration: {total_dur:.2f}s · {len(SEG)} segments · {len(ANCH)} anchors")

# Match: for each anchor, find first segment (start_idx and onward) whose text matches
matched = []  # list of (anchor_idx, segment_idx, start_time)
seg_start = 0
for ai, pat in enumerate(ANCH):
    rx = re.compile(pat)
    found = -1
    for si in range(seg_start, len(SEG)):
        if rx.search(SEG[si]["text"]):
            found = si
            break
    if found >= 0:
        matched.append((ai, found, SEG[found]["start"]))
        seg_start = found + 1
    else:
        matched.append((ai, None, None))

ok = sum(1 for m in matched if m[1] is not None)
print(f"[INFO] Matched {ok}/{len(ANCH)} ({ok/len(ANCH)*100:.1f}%)")

# Linear interpolate misses
times = [m[2] for m in matched]
for i in range(len(times)):
    if times[i] is None:
        # find prev and next valid
        prev_i, prev_t = None, None
        for j in range(i-1, -1, -1):
            if times[j] is not None:
                prev_i, prev_t = j, times[j]; break
        next_i, next_t = None, None
        for j in range(i+1, len(times)):
            if times[j] is not None:
                next_i, next_t = j, times[j]; break
        if prev_t is not None and next_t is not None:
            times[i] = prev_t + (next_t - prev_t) * (i - prev_i) / (next_i - prev_i)
        elif prev_t is not None:
            times[i] = prev_t + 5.0
        elif next_t is not None:
            times[i] = max(0, next_t - 5.0)
        else:
            times[i] = i * (total_dur / len(ANCH))

# Build scene_timing
scenes = []
for i in range(len(times)):
    start = times[i]
    end = times[i+1] if i+1 < len(times) else total_dur
    scenes.append({"scene": i+1, "start": round(start, 3), "end": round(end, 3),
                   "duration": round(end - start, 3),
                   "matched": matched[i][1] is not None})

OUT = PROJ / "output" / "scene_timing.json"
OUT.write_text(json.dumps(scenes, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"[OK] {OUT}")
print(f"[INFO] First scene: {scenes[0]['start']}~{scenes[0]['end']}s ({scenes[0]['duration']}s)")
print(f"[INFO] Last scene: {scenes[-1]['start']}~{scenes[-1]['end']}s ({scenes[-1]['duration']}s)")
print(f"[CHECK] Last scene end vs mp3 dur: diff={total_dur - scenes[-1]['end']:.2f}s")
