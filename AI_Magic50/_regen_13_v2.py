"""#13 SAL Grid 단일 재생성 v2 — 우측 패널 축소, 큐브 격자 정리 (2026-05-14)"""
import subprocess, sys, time, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE = Path(r"G:/내 드라이브/333_자료공유폴더/Sunny_Magic_Show/AI_Magic50/슬라이드쇼/covers")
SCRIPT = r"C:/Users/home/.claude/skills/ai-image-기본/scripts/gemini_imagegen.py"

PROMPT = (
    "40s Korean developer seated FAR RIGHT EDGE of frame (face visible but compact, not large). "
    "DOMINANT center element: large ISOMETRIC 3D SAL GRID CUBE filling ~60% of frame width, "
    "with three bold thick axis labels — X=STAGE (S0-S9), Y=AREA (UI/API/DB), Z=LEVEL (Plan/Impl/Verify). "
    "Inside the cube: ONLY 4-5 glowing task nodes at clear coordinates (e.g. 'S2-API'), well spaced — NO dense text overlap. "
    "REMOVE the right sidebar checklist — instead, place 4 floating compact attribute badges "
    "(예: 'Status', 'Deps', 'Score', 'Owner') near the cube as small chips, not a vertical column. "
    "Compact bottom-center caption (one line, small): 'SAL Grid 3D 좌표'. "
    "CRITICAL: leave top-left 30% completely quiet (no text, no diagram, no face) for header overlay. "
    "AVOID: tall right sidebar panel, dense node labels overlapping inside cube, person face in upper-left, "
    "axis labels touching bottom edge. "
    "Style: cozy modern flat illustration, soft anime-influenced, warm amber/orange/teal palette, "
    "16:9 horizontal, evening city window background, indoor desk scene, "
    "natural human anatomy (5 fingers per hand, symmetric glasses), high detail. "
    "Lighting: warm desk lamp + cool city night light contrast. "
    "Negative: photo-realistic, dark/gloomy, beige monochrome, dense crowded labels, "
    "right sidebar panel, text in upper-left."
)

def main():
    out = BASE / "13_new.png"
    cmd = ["python", SCRIPT, PROMPT,
           "--input", str(BASE / "01.png"),
           "--output", str(out),
           "--ratio", "16:9", "--size", "2K",
           "--image-only", "--shuffle",
           "--keys-file", "C:/Users/home/.gemini_keys"]
    t0 = time.time()
    print("=== #13 v2 START ===")
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    dt = time.time() - t0
    if r.returncode == 0 and out.exists():
        print(f"OK {dt:.1f}s {out.stat().st_size//1024}KB")
    else:
        print(f"FAIL {dt:.1f}s")
        print("STDERR:", r.stderr[-400:] if r.stderr else "")
        print("STDOUT:", r.stdout[-400:] if r.stdout else "")

if __name__ == "__main__":
    main()
