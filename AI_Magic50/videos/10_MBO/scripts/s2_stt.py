"""S2 — Whisper STT for narration_v1_leadin.mp3.
Outputs segments.json + SRT (English filename, BOM removed, LF).
"""
import json
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

PROJ = Path(r"G:\내 드라이브\333_자료공유폴더\Sunny_Magic_Show\AI_Magic50\videos\10_MBO")
MP3 = PROJ / "01_voice" / "narration_v1_leadin.mp3"
SEG_JSON = PROJ / "output" / "segments.json"
SRT = PROJ / "output" / "MBO_v1_ko.srt"

SEG_JSON.parent.mkdir(parents=True, exist_ok=True)

# Force OpenAI API (CPU local whisper-large-v3 too slow for this session)
USE_LOCAL = False

if USE_LOCAL:
    print("[INFO] Using local whisper (large-v3)")
    model = whisper.load_model("large-v3")
    result = model.transcribe(str(MP3), language="ko", word_timestamps=False, verbose=False)
    segments = [
        {"id": s["id"], "start": s["start"], "end": s["end"], "text": s["text"].strip()}
        for s in result["segments"]
    ]
else:
    print("[INFO] Using OpenAI API whisper-1")
    import requests
    # Load env
    for line in (Path(r"C:\Dev\buzzlab-nextjs\.env.local")).read_text(encoding='utf-8').splitlines():
        if "=" in line and not line.startswith("#"):
            k,v = line.split("=",1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    KEY = os.environ["OPENAI_API_KEY"]
    with open(MP3, "rb") as f:
        r = requests.post(
            "https://api.openai.com/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {KEY}"},
            files={"file": f},
            data={"model": "whisper-1", "language": "ko", "response_format": "verbose_json"},
            timeout=600,
        )
    r.raise_for_status()
    data = r.json()
    segments = [
        {"id": i, "start": s["start"], "end": s["end"], "text": s["text"].strip()}
        for i, s in enumerate(data.get("segments", []))
    ]

# PHONETIC_SUBS — fix Korean misrecognition for English brand terms
PHONETIC_SUBS = {
    "엠비오": "MBO", "엠비 오": "MBO", "M B O": "MBO",
    "오케이알": "OKR", "오 케이 알": "OKR",
    "스마트": "SMART", "에스마트": "SMART",
    "케이피아이": "KPI", "K P I": "KPI",
    "피오": "PO", "피 오": "PO",
    "에이아이": "AI", "에이 아이": "AI",
    "라이트하우스": "Lighthouse",
    "엘씨피": "LCP", "L C P": "LCP",
    "살그리드": "SAL Grid", "살 그리드": "SAL Grid", "셀그리드": "SAL Grid",
    "스킬아틀라스": "SKILL_ATLAS", "스킬 아틀라스": "SKILL_ATLAS",
    "컬": "curl", "큐알엘": "curl",
    "에이즈이즈": "AS-IS", "에이즈 이즈": "AS-IS",
    "투비": "TO-BE", "투 비": "TO-BE",
    "프롬프트": "프롬프트",
    "케이에스 엑스": "KS X",
    "드러커": "드러커",
}
for s in segments:
    for k, v in PHONETIC_SUBS.items():
        s["text"] = s["text"].replace(k, v)

# Save segments.json
SEG_JSON.write_text(json.dumps(segments, ensure_ascii=False, indent=2), encoding='utf-8')
print(f"[OK] {SEG_JSON} — {len(segments)} segments")

# Generate SRT
def fmt(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int((s - int(s)) * 1000):03d}"

lines = []
for i, s in enumerate(segments, 1):
    lines.append(str(i))
    lines.append(f"{fmt(s['start'])} --> {fmt(s['end'])}")
    lines.append(s["text"])
    lines.append("")
srt_text = "\n".join(lines)
# Save with LF, no BOM
SRT.write_bytes(srt_text.encode("utf-8"))
print(f"[OK] {SRT} — {len(srt_text)} bytes")

# Verify last cue end vs mp3 duration
import subprocess
probe = subprocess.run(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(MP3)],
    capture_output=True, text=True
)
dur = float(probe.stdout.strip())
last_end = segments[-1]["end"] if segments else 0
print(f"[CHECK] mp3.duration={dur:.2f}s  last_cue.end={last_end:.2f}s  diff={dur-last_end:.2f}s")
if dur - last_end < 1.0:
    print("[WARN] last cue near end — tail-pad must be added in S4")
