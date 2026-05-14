"""S2 — ElevenLabs TTS for 10_MBO video.

Strips section markers [...] and synthesizes Korean narration.
Outputs: 01_voice/narration_v1.mp3, then leadin variant.
"""
import os
import re
import sys
import requests
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

PROJ = Path(r"G:\내 드라이브\333_자료공유폴더\Sunny_Magic_Show\AI_Magic50\videos\10_MBO")
SCRIPT_TXT = PROJ / "00_script" / "script.txt"
OUT_MP3 = PROJ / "01_voice" / "narration_v2.mp3"
OUT_LEADIN = PROJ / "01_voice" / "narration_v2_leadin.mp3"

# Load .env.local
def load_env():
    env_path = Path(__file__).resolve().parents[5] / ".env.local"  # repo root
    # Fallback: scan upwards from project for .env.local
    if not env_path.exists():
        for parent in [Path(r"C:\Dev\buzzlab-nextjs")]:
            cand = parent / ".env.local"
            if cand.exists():
                env_path = cand
                break
    if env_path.exists():
        for line in env_path.read_text(encoding='utf-8', errors='ignore').splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env()
API_KEY = os.environ.get("ELEVENLABS_API_KEY")
if not API_KEY:
    print("ERROR: ELEVENLABS_API_KEY not set")
    sys.exit(1)

# Korean voice — use the user's registered voice ID (no default fallback)
VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID")
if not VOICE_ID:
    print("ERROR: ELEVENLABS_VOICE_ID not set in .env.local")
    sys.exit(1)
MODEL = "eleven_multilingual_v2"

# Load script and strip [...] markers
text = SCRIPT_TXT.read_text(encoding='utf-8')
clean = re.sub(r'\[[^\]]+\]', '', text)
# Collapse multiple newlines
clean = re.sub(r'\n{3,}', '\n\n', clean).strip()

print(f"[INFO] Source script chars (no whitespace): {len(re.sub(chr(92)+'s', '', clean))}")
print(f"[INFO] Voice ID: {VOICE_ID}")
print(f"[INFO] Output: {OUT_MP3}")

OUT_MP3.parent.mkdir(parents=True, exist_ok=True)

url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
headers = {
    "xi-api-key": API_KEY,
    "Content-Type": "application/json",
    "Accept": "audio/mpeg",
}
payload = {
    "text": clean,
    "model_id": MODEL,
    "voice_settings": {
        "stability": 0.55,
        "similarity_boost": 0.75,
        "style": 0.15,
        "use_speaker_boost": True,
    },
}

print("[INFO] Calling ElevenLabs API...")
r = requests.post(url, headers=headers, json=payload, timeout=300)
if r.status_code != 200:
    print(f"ERROR {r.status_code}: {r.text[:500]}")
    sys.exit(1)

OUT_MP3.write_bytes(r.content)
print(f"[OK] Saved {OUT_MP3} ({len(r.content)/1024:.1f} KB)")

# Generate leadin (1.5s silence prepended) using ffmpeg
import subprocess
ffmpeg = "ffmpeg"
cmd = [
    ffmpeg, "-y",
    "-f", "lavfi", "-i", "anullsrc=channel_layout=mono:sample_rate=44100",
    "-i", str(OUT_MP3),
    "-filter_complex", "[0:a]atrim=0:1.5[lead];[lead][1:a]concat=n=2:v=0:a=1[out]",
    "-map", "[out]",
    "-c:a", "libmp3lame", "-b:a", "192k",
    str(OUT_LEADIN),
]
print("[INFO] Generating leadin (1.5s silence prepended)...")
result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
if result.returncode != 0:
    print(f"FFmpeg ERROR:\n{result.stderr[:1000]}")
    sys.exit(1)
print(f"[OK] Saved {OUT_LEADIN}")

# Probe duration
probe = subprocess.run(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(OUT_LEADIN)],
    capture_output=True, text=True
)
dur = float(probe.stdout.strip())
print(f"[INFO] Final duration: {dur:.2f}s = {dur/60:.2f}min")
