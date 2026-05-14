"""
SUNNY AI MAGIC 50 — 표지 일괄 재생성 오케스트레이터 (2026-05-13)

32장 비-완벽 챕터를 우선순위 순으로 Gemini 3 Pro Image로 재생성한다.
- 입력 레퍼런스: 01.png (스타일 일관성 유지)
- 비율: 16:9
- 해상도: 2K
- 출력: covers/{NN}_new.png (검수 후 수동 덮어쓰기)
"""

import subprocess
import sys
import time
import io
from pathlib import Path

# Force UTF-8 stdout for Windows cp949 consoles
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE = Path(r"G:/내 드라이브/333_자료공유폴더/Sunny_Magic_Show/AI_Magic50/슬라이드쇼/covers")
REF = str(BASE / "01.png")
SCRIPT = r"C:/Users/home/.claude/skills/ai-image-기본/scripts/gemini_imagegen.py"

COMMON_STYLE = (
    "Style: cozy modern flat illustration, soft anime-influenced, warm color palette, "
    "16:9 horizontal composition, evening city window background, indoor desk scene, "
    "Korean protagonist 40s, monitor or laptop, floating UI icons as semantic overlays. "
    "Lighting: warm desk lamp + cool city night light contrast. "
    "Negative: photo-realistic, dark/gloomy, cluttered, generic stock-photo look."
)

# (챕터번호, 우선순위, 한국어 키 비주얼 프롬프트)
PROMPTS = [
    # 🔴 Tier 1
    ("36", "T1",
     "A 40s Korean developer at desk in a warm-lit study, evening city window. "
     "Foreground: large monitor showing Claude Code terminal with a vivid 5-LINE HUD STRIP at the bottom: "
     "LINE1 green (model+branch), LINE2 yellow-to-red gradient bar (context 70/80/90% threshold), "
     "LINE3 cyan (rate limit 5h/7d bars), LINE4 purple (tool counter+hook events), LINE5 white-on-dark (git+cwd). "
     "Lines clearly separated with color-coded ribbons. Floating legend 'HUD' with 5 mini bars. "
     "Korean caption 'Statusline HUD'."),

    # 🟡 Tier 2
    ("04", "T2",
     "40s Korean developer at desk, monitor split: LEFT 'READ-ONLY' with large orange padlock, shield, "
     "files with magnifying glass only (no write arrows). RIGHT 'EXECUTE' greyed out. "
     "Top banner: 'PLAN MODE — 읽기만 가능, 쓰기 차단'. "
     "Step ribbon below: 1.학습→2.검토→3.계획→4.승인→5.실행 with checkmark gate."),

    ("08", "T2",
     "40s Korean female developer at desk, wide monitor showing THREE vertical option cards side-by-side: "
     "'안 A' (blue), '안 B' (green), '안 C' (orange). Each card has pros (✓) and cons (✗) lists and a score gauge. "
     "Yellow star badge '권고' pinned to card B. AI assistant icon top-right with speech bubble '권고: B (이유 3가지)'."),

    ("13", "T2",
     "40s Korean developer at desk, monitor showing ISOMETRIC 3D GRID CUBE with three labeled axes: "
     "X=Stage(S0~S9), Y=Area(UI/API/DB/DevOps), Z=Level(plan/impl/verify). "
     "Task nodes at coordinates like 'S2-API-impl'. Side panel '22 Attributes' as checklist. "
     "Arrows show auto-inferred dependency. Title 'SAL Grid — 3D Task Coordinate'."),

    ("14", "T2",
     "40s Korean developer at desk, monitor shows MILITARY ORGANIZATION CHART: "
     "TOP 소대장 (1 with helmet). MIDDLE 4 squads with NATO call-signs ALPHA/BRAVO/CHARLIE/DELTA each with 분대장. "
     "BOTTOM each squad has '12 정규병' cluster + '4 용병' cluster (total 44). "
     "Right sidebar '21 Skills' badge grid 3×7. Title 'AI 소대 편제 — 44명 + 21 Skills'."),

    ("19", "T2",
     "40s Korean developer at desk, laptop just had power interruption (lightning bolt icon corner). "
     "Screen shows recovery dialog '이전 세션 발견 — /resume 으로 복원하시겠습니까?'. "
     "Clock rewinding, timeline strip '전 세션→단절→/resume 복원'. "
     "Red warning badge '비상 복구 전용 — 평상시 금지'."),

    ("33", "T2",
     "40s Korean developer at desk, monitor centered showing large 'CLAUDE.md' file icon with "
     "7 colored rule cards radiating outward: 표시규칙/언어운용/UI검증/자동감지/멀티페이즈/도구카탈로그/모바일전달. "
     "Each card has lightning icon = auto-fire trigger. "
     "Glowing arrow shows AI reading the .md and rules auto-firing."),

    ("41", "T2",
     "40s Korean developer at desk at night with 24-hour CLOCK DIAL on monitor color-coded: "
     "00–06 green 'A등급 한산', 06–11 yellow 'B', 11–17 orange 'C', 17–23 red 'D등급 피크'. "
     "Currently 03:00 pointer on green zone. "
     "Background: claude -p batch script icons running in queue during green band. "
     "Title '피크타임 회피 + 헤드리스 배치'."),

    # 🟢 Tier 3
    ("01", "T3",
     "40s Korean male at laptop, evening city. Screen shows BINARY TREE with 'Q1?' at top splitting into "
     "YES (green) / NO (red) branches, fractal deepening to 20 levels, glowing bulb at final leaf 'Idea Found!'. "
     "Cozy desk scene preserved."),

    ("02", "T3",
     "40s Korean developer at desk, monitor centered showing ROUND TABLE with 4 distinct avatars facing each other: "
     "전문가 A (architect helmet), 전문가 B (data scientist glasses), 전문가 C (security shield), "
     "DA (red with flame icon). Speech bubbles overlap. Arrows show S1→S2→S3→S4→S5 phase markers around table."),

    ("05", "T3",
     "40s Korean developer flanked by TWO laptops on same desk: "
     "LEFT 'A 인스턴스 — 실행자' (hammer/wrench icon), "
     "RIGHT 'B 인스턴스 — 검증자' (magnifying glass/check icon). "
     "Bidirectional arrow between labeled '교차 검증'."),

    ("07", "T3",
     "40s Korean developer at desk, monitor shows VERTICAL agenda checklist of 5 items. "
     "ONE current item highlighted yellow with 'EXPLAIN→APPROVE' button pair. "
     "Other 4 items GREYED OUT with tiny lock icons (waiting). Clock indicator '한 번에 하나씩'."),

    ("09", "T3",
     "40s Korean developer at desk, monitor shows ONE central AI character wearing DIFFERENT HATS in sequence along "
     "horizontal timeline: T1 전문가→T2 리뷰어→T3 DA red→T4 컨트래리언. Each transition '→ 5분 후 →'. "
     "Label '1 AI × 4 Roles (순차)'."),

    ("10", "T3",
     "EMPTY desk at 03:00 AM (wall clock visible, dark sleeping city outside). "
     "Laptop alone on desk, terminal showing `claude -p \"...\"` script running unattended. "
     "Small ghost/robot icon beside terminal labeled 'Autonomous / No Human'. Moon icon top-right."),

    ("11", "T3",
     "40s Korean female developer at desk, monitor shows HORIZONTAL pipeline with 6 hook event nodes, "
     "each with distinct icon/color: UserPromptSubmit(blue 📝) → PreToolUse(yellow ⏳) → PostToolUse(green ✅) → "
     "Stop(red 🛑) → SubagentStop(purple 🔁) → PreCompact(orange 💾). Each fires tiny lightning bolt."),

    ("12", "T3",
     "40s Korean developer at desk, monitor shows CIRCULAR LOOP with 4 stages: "
     "PHASE1 목표정의(🎯) → PHASE2 PO승인(✋✅) → PHASE3 실행(⚙️) → PHASE4 보고(📊), arrow returns to Phase1. "
     "Side panel 'MBO 4표 양식 — 현재vs목표/KPI/실행계획/리스크'."),

    ("16", "T3",
     "40s Korean developer at desk, monitor SPLIT LEFT vs RIGHT. "
     "LEFT 'Subagent (1:1)': main at top, one subagent below, single arrow, one '200K context' balloon. "
     "RIGHT 'Agent Teams (peer-mesh)': 4 teammates in circle each with own '200K context' balloon (4 balloons), "
     "peer arrows, each has child Subagent layer (2-tier). Title '수직(1:1) vs 수평(peer mesh)'."),

    ("17", "T3",
     "40s Korean developer at desk, monitor shows CONTEXT USAGE BAR GRAPH with threshold zones: "
     "0–70% green '안전', 70–80% yellow '주의', 80–90% orange '경고', 90%+ red '압축 임박'. "
     "Toggle 'AUTO-COMPACT' set OFF (red X). Manual `/compact` button (hand cursor). "
     "Small Vault icon 'Wiki 저장 위임'."),

    ("18", "T3",
     "40s Korean developer at desk, monitor shows TWO command sources: "
     "LEFT `~/.claude/commands/` (globe 'Global'), RIGHT `./.claude/commands/` (folder 'Project'). "
     "Both feed central slash-command bar `/build /test /deploy`. "
     "Below: 4-step ladder '메모→슬래시→스킬→에이전트' with up-arrows (자산화 격상)."),

    ("26", "T3",
     "40s Korean developer at desk, monitor shows YOUTUBE UPLOAD SCHEDULE CALENDAR — every day has green check video icon (1/day streak). "
     "24-hour clock '오늘 분량 완료 — 자동 파이프라인'. "
     "Pipeline viz: 스크립트→음성→영상→썸네일→업로드."),

    ("27", "T3",
     "40s Korean developer at desk, monitor shows PATENT SPECIFICATION DOCUMENT with prominent '청구항 1, 2, 3...' on left half. "
     "Right half: AI chat dialog with formal claim-syntax prompts, '강제 양식' stamp. "
     "Patent emblem (특허청 style) top corner."),

    ("28", "T3",
     "40s Korean developer at desk, monitor shows 4-RUNG LADDER rising upward: "
     "rung 1 (light) review → rung 2 persona → rung 3 sal-da → rung 4 (heaviest, top) debug. "
     "Each rung different color, verification badge. Score '100' floating at top."),

    ("30", "T3",
     "40s Korean developer at desk, monitor shows CIRCULAR 4-STAGE LOOP: "
     "①인정(humble hand-raise) → ②검증(magnifying glass) → ③해결(wrench) → ④창발(glowing star) → loops back to ①."),

    ("32", "T3",
     "40s Korean developer at desk, TWO monitors: "
     "LEFT 'Claude 앱' (chat bubble UI, creative diagrams, idea sparks, no file system). "
     "RIGHT 'Claude Code' (terminal + file tree + git diff + code execution). "
     "Divider down middle '사고 vs 실행'."),

    ("34", "T3",
     "40s Korean developer at desk, monitor shows 3 MODEL SELECTOR CARDS horizontally: "
     "OPUS (gold 🧠 '고난도 추론' premium), SONNET (silver ⚖ '일반 코딩·요약' balanced), HAIKU (bronze ⚡ '빠른 라벨링' speed). "
     "Each card shows $ count (3$/2$/1$). Cursor hovering over SONNET."),

    ("35", "T3",
     "40s Korean developer at desk, monitor shows RACING TRACK: "
     "Car labeled 'claude --dangerously-skip-permissions' speeding fast. "
     "At each curve, HOOK GUARD (shield icon) auto-fires: pre-bash blocks rm, post-edit auto-tests, user-prompt sanitization. "
     "Speedometer high, but green 'SAFE' lamp stays lit due to hooks."),

    ("38", "T3",
     "40s Korean developer at desk, monitor shows three discovery sources: "
     "LEFT 'Tool Atlas' (world map with skill pins), CENTER 'revfactory/skills' (GitHub repo, branch tree), "
     "RIGHT 'Anthropic skill marketplace' (official badge). "
     "Below: 3-step funnel '발굴→검증→자산화' with arrows into personal Vault folder."),

    ("39", "T3",
     "40s Korean developer at desk, monitor shows 'Deploy' button glowing with 3 floating stickers: "
     "🚫 'noindex meta — 검색 노출 차단', 🔄 '한글 폴더 우회 — ASCII 슬러그', 🔒 'Private access only'. "
     "URL bar `sunny-magic.vercel.app` with green deployment checkmark."),

    ("42", "T3",
     "40s Korean developer NOT typing — seated in OPERATOR CABIN of small EXCAVATOR/TRACTOR, hands on joystick. "
     "Excavator arm digging large '프로젝트' structure. "
     "Floating ribbon '30× 생산성 — 노동자에서 지휘자로'. "
     "Below: small human with shovel labeled '이전' looks tiny in comparison."),

    ("44", "T3",
     "40s Korean developer at desk, monitor split: "
     "LEFT (greyed with X) tall pile of '기획서/명세서/와이어프레임' papers. "
     "RIGHT (highlighted) working prototype mini-app with clickable button, sticky note '빠른 v0 → 즉시 테스트 → 사후 문서화'. "
     "Small sign bottom '단, 큰 작업은 #4 Plan Mode 필수'."),

    ("46", "T3",
     "40s Korean developer at desk, monitor shows STYLIZED KOREA MAP with population dots in red "
     "(서울 dense, 부산 medium, 제주 sparse) labeled '100만 한국인 페르소나'. "
     "Side panel: demographic bars 직업·나이·지역. "
     "Below: regression pipeline 'NeMoTron 데이터→4종 품질관리(#28)→자동 회귀'."),

    ("47", "T3",
     "40s Korean developer at desk, monitor centered shows 5-MINUTE TIMER ticking down at top, "
     "checklist underneath: ☐ 모델 등급 결정, ☐ 캐시 블록 식별, ☐ 배치 가능 작업 분리, ☐ 검색 외주. "
     "Banner 'START — 5분 만에 끝낸다'. Below: cost graph steep DROP after 5-min planning."),
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
        print(f"[{tier}] #{chapter} ✓ {dt:.1f}s {size_kb}KB → {out.name}")
        return True
    else:
        print(f"[{tier}] #{chapter} ✗ FAILED in {dt:.1f}s")
        print("STDOUT:", r.stdout[-500:] if r.stdout else "(empty)")
        print("STDERR:", r.stderr[-500:] if r.stderr else "(empty)")
        return False

def main():
    results = {"ok": [], "fail": []}
    for chapter, tier, prompt in PROMPTS:
        ok = gen(chapter, prompt, tier)
        (results["ok"] if ok else results["fail"]).append(chapter)
    print("\n" + "="*60)
    print(f"DONE — 성공 {len(results['ok'])}/{len(PROMPTS)} | 실패 {len(results['fail'])}")
    if results["fail"]:
        print("실패 챕터:", results["fail"])

if __name__ == "__main__":
    main()
