"""
SUNNY AI MAGIC 50 — B+C+D 등급 11장 재생성 (2026-05-14)

평가 결과(표지_디자인_평가_2026-05-14.md) 기반으로 미비점을 반영한 신규 프롬프트.
모든 챕터 공통 제약: 좌상단 30% 영역 비워둠 (헤더 오버레이 충돌 방지).

대상:
- D(1): #45 DID Loop — 해상도/얼굴/톤 전면 재생성
- C(3): #03 SAL 3D, #19 /resume, #23 멀티모델
- B(7): #04, #13, #14, #17, #32, #42, #50
"""

import subprocess
import sys
import time
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE = Path(r"G:/내 드라이브/333_자료공유폴더/Sunny_Magic_Show/AI_Magic50/슬라이드쇼/covers")
REF = str(BASE / "01.png")
SCRIPT = r"C:/Users/home/.claude/skills/ai-image-기본/scripts/gemini_imagegen.py"

# 공통 스타일 + 좌상단 비우기 + 손/얼굴 정확도 강화
COMMON_STYLE = (
    "Style: cozy modern flat illustration, soft anime-influenced, WARM color palette "
    "(amber/orange/teal/cream), 16:9 horizontal, evening city window in background, "
    "indoor desk scene, Korean protagonist (40s, full face and head clearly visible, "
    "natural anatomy, 5 fingers per hand, symmetric glasses if any). "
    "CRITICAL LAYOUT: leave the top-left 30% of the canvas visually QUIET — no important "
    "text labels, no faces, no key diagrams in that zone (will be overlaid with a header box). "
    "Place the main subject in the CENTER or RIGHT half. "
    "Lighting: warm desk lamp + cool city night light contrast. "
    "Negative: photo-realistic, dark/gloomy, beige monochrome, deformed fingers, "
    "asymmetric glasses, headless figure, missing neck, text in upper-left, "
    "duplicate warning labels, cluttered upper-left corner."
)

# (챕터, 등급, 미비점 기반 신규 프롬프트)
PROMPTS = [
    # ===== D 등급 (최우선) =====
    ("45", "D",
     "40s Korean developer at a warm-lit desk in the right half of the frame, evening city window. "
     "Center-right: large monitor showing a 4-stage CIRCULAR LOOP labeled clearly: "
     "①DATA (raw logs icon) → ②INFORMATION (organized chart) → ③DECISION (judge gavel) → ④ACTION (rocket), "
     "each stage in a different warm color (amber/orange/teal/coral) with bold Korean labels. "
     "Loop arrow returns ④→① showing iterative cycle. "
     "Small floating side panel labeled 'DID Loop — 자료→정보→결정' (단 한 줄). "
     "AVOID: yellow flat monochrome background, multiple anonymous figures, low resolution feel. "
     "Render at high detail, cinematic warm evening tones consistent with chapter #01 reference."),

    # ===== C 등급 =====
    ("03", "C",
     "40s Korean developer seated at desk on the RIGHT half of frame, evening city window. "
     "CENTER: large ISOMETRIC 3D SAL CUBE floating above the desk with three clearly labeled axes — "
     "X-axis = Stage (S0~S9, warm orange), Y-axis = Area (UI/API/DB, teal), Z-axis = Level (plan/impl/verify, amber). "
     "Inside cube: a few colored task nodes at coordinate positions like 'S2-API-impl'. "
     "Bold Korean caption (one line, mid-bottom): 'SAL 3차원 좌표'. "
     "AVOID: beige monochrome palette, flat 2D grid, low contrast. Use warm cozy evening tones."),

    ("19", "C",
     "40s Korean developer (full face, glasses clearly drawn with visible eyes behind them) seated RIGHT side. "
     "Laptop on desk, screen shows a single clean RECOVERY DIALOG: '이전 세션 발견 — /resume?' "
     "with two buttons [Yes] [No]. ONE small red badge (not multiple) bottom-right of dialog: '비상 복구 전용'. "
     "Subtle lightning bolt icon corner indicating prior interruption. "
     "Center-bottom: clean timeline ribbon '전 세션 → 단절 → /resume 복원' (3 nodes, single line). "
     "AVOID: duplicate red warning boxes, multiple emergency stickers, anonymous eyes."),

    ("23", "C",
     "40s Korean developer (full face clearly visible, sharp facial features, natural eyes and nose, "
     "5 visible fingers on hands) seated RIGHT side at desk. "
     "CENTER of monitor: large 4-STAGE FUNNEL clearly showing '15장 → 5장 → 5장 마감 → 1~2장 GOLD' "
     "with each stage labeled in bold Korean, sized to dominate the screen (not a tiny corner element). "
     "5 small model badges floating: Gemini / GPT / DALL·E / Imagen / SDXL feeding into top of funnel. "
     "AVOID: blurred face, indistinct eyes, tiny diagrams in screen corner."),

    # ===== B 등급 =====
    ("04", "B",
     "40s Korean developer seated RIGHT, monitor center-right showing TWO vertically stacked panels: "
     "TOP panel 'READ-ONLY' with large orange padlock + magnifying glass over file icons (no write arrows). "
     "BOTTOM panel 'EXECUTE' greyed out with dimmed play button. "
     "BOLD Korean banner across MIDDLE of monitor: '읽기만 가능, 쓰기 차단' (NO English 'PLAN MODE' label). "
     "Step ribbon along bottom edge of screen: 1.학습→2.검토→3.계획→4.승인→5.실행 (kept compact, single row). "
     "AVOID: English text in upper-left area, step icons in upper-left."),

    ("13", "B",
     "40s Korean developer seated FAR RIGHT (face fully visible, not cropped by edge). "
     "CENTER of frame: large ISOMETRIC 3D SAL GRID CUBE dominating the visual, "
     "three thick axis labels in BOLD large font — X=STAGE (S0~S9), Y=AREA (UI/API/DB), Z=LEVEL (Plan/Impl/Verify). "
     "Task nodes glowing at sample coordinates ('S2-API-impl', 'S3-UI-verify'). "
     "Right sidebar: small 22-attribute checklist column. "
     "Compact bottom caption: 'SAL Grid 개발방법론' (one line only). "
     "AVOID: head/face overlap with upper-left corner, thin unreadable axis labels."),

    ("14", "B",
     "40s Korean developer seated RIGHT (face not in upper portion). "
     "CENTER: a CLEAR MILITARY ORG CHART rendered as floating cards: "
     "TOP one 소대장 card (helmet icon), MIDDLE row 4 squad cards labeled ALPHA/BRAVO/CHARLIE/DELTA "
     "each with bold visible 분대장 icon, BOTTOM row showing '12 정규병 + 4 용병' per squad as count badges. "
     "Right side: small 3×7 skill grid '21 Skills'. "
     "Avoid placing the squad cards low on the desk surface — keep them as clear elevated UI cards. "
     "AVOID: chart elements in upper-left 30%, forehead/hair overlap with header zone."),

    ("17", "B",
     "40s Korean developer seated RIGHT half, monitor CENTER-RIGHT showing a horizontal CONTEXT USAGE BAR "
     "with clearly readable Korean labels (NO line-broken English words): "
     "[0–70% 안전 GREEN] [70–80% 주의 YELLOW] [80–90% 경고 ORANGE] [90%+ 압축임박 RED]. "
     "Toggle below labeled 'AUTO-COMPACT OFF' (red X). Hand-cursor on manual button '/compact'. "
     "Small Vault icon side label 'Wiki 저장'. "
     "Keep all text in the center-right area; upper-left stays QUIET. "
     "AVOID: broken word fragments like 'C/ompact', text cut off at edges."),

    ("32", "B",
     "40s Korean developer in CENTER-RIGHT (clearly drawn 5 fingers each hand, natural wrist anatomy). "
     "Two monitors side by side BOTH in the right half of frame: "
     "LEFT monitor 'Claude 앱 — 사고' (chat bubble UI, idea sparks), "
     "RIGHT monitor 'Claude Code — 실행' (terminal + file tree + git diff). "
     "Single thin divider between monitors labeled vertically '사고 ↔ 실행' (small font, no large banner). "
     "Upper-left 30% kept EMPTY for header overlay. "
     "AVOID: large 'THINK vs EXECUTE' English banner across top, deformed fingers, missing knuckles."),

    ("42", "B",
     "40s Korean developer (natural body proportions, head:body ratio ~1:7) seated in OPERATOR CABIN "
     "of a small EXCAVATOR positioned CENTER-RIGHT of frame, hands clearly gripping joysticks "
     "(visible fingers wrapping around handles). "
     "Excavator arm extends to RIGHT, digging a 프로젝트-labeled structure. "
     "Small tiny human with shovel in BOTTOM-RIGHT corner labeled '이전' (NOT bottom-left). "
     "NO ribbon banner in upper-left or upper-center — keep top-left 30% sky/clear. "
     "AVOID: '지휘자로' ribbon across upper area, distorted body proportions, hand-joystick disconnect."),

    ("50", "B",
     "Cross-section view of a 4-story modern building (WARM AMBER and CREAM tones, NOT teal/cyan) "
     "occupying CENTER-RIGHT of frame, labeled '사내 AI 에이전트 하우스'. "
     "Each floor shows distinct AI agent activity: F1 Reception (customer chat), "
     "F2 Contracts (document review), F3 Bidding (analysis), F4 R&D (coding). "
     "Friendly humanoid robot icons (clean detail, defined features, not blurry) on each floor. "
     "One Korean human supervisor in center-right with clear face. "
     "Korean caption bottom only: '사내 AI 에이전트 하우스' (NO English 'HOUSE OF AI AGENTS' banner). "
     "AVOID: teal/cyan dominant palette, English banner top, blurred robot faces, upper-left text."),
]

def gen(chapter, prompt_body, tier):
    out = BASE / f"{chapter}_new.png"
    full_prompt = prompt_body + " " + COMMON_STYLE
    cmd = [
        "python", SCRIPT,
        full_prompt,
        "--input", REF,
        "--output", str(out),
        "--ratio", "16:9",
        "--size", "2K",
        "--image-only",
        "--shuffle",
        "--keys-file", "C:/Users/home/.gemini_keys",
    ]
    print(f"\n=== [{tier}] #{chapter} START ===")
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    dt = time.time() - t0
    if r.returncode == 0 and out.exists():
        size_kb = out.stat().st_size // 1024
        print(f"[{tier}] #{chapter} OK {dt:.1f}s {size_kb}KB")
        return True
    else:
        print(f"[{tier}] #{chapter} FAIL in {dt:.1f}s")
        print("STDOUT:", r.stdout[-400:] if r.stdout else "(empty)")
        print("STDERR:", r.stderr[-400:] if r.stderr else "(empty)")
        return False

def main():
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    results = {"ok": [], "fail": []}
    for chapter, tier, prompt in PROMPTS:
        if only and chapter not in only:
            continue
        ok = gen(chapter, prompt, tier)
        (results["ok"] if ok else results["fail"]).append(chapter)
    print("\n" + "="*60)
    print(f"DONE — OK {len(results['ok'])} | FAIL {len(results['fail'])}")
    if results["fail"]:
        print("FAILED:", results["fail"])

if __name__ == "__main__":
    main()
