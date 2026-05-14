"""S3 — Render 51 scenes as PIL diagrams (1920x1080, BuzzLab light palette).

This is an explainer video — diagrams + text > photo-realistic. PIL is fast,
deterministic, cp949-safe with malgun.ttf, and produces consistent typography.

Each scene has: title chip (top), main visual (center), glossary chip (bottom-left).
"""
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.stdout.reconfigure(encoding='utf-8')

PROJ = Path(r"G:\내 드라이브\333_자료공유폴더\Sunny_Magic_Show\AI_Magic50\videos\10_MBO")
OUT = PROJ / "02_assets" / "scenes"
OUT.mkdir(parents=True, exist_ok=True)

# Fonts — malgun.ttf is bundled with Windows, cp949 safe
FONT_PATH = "C:/Windows/Fonts/malgunbd.ttf"  # bold
FONT_REG = "C:/Windows/Fonts/malgun.ttf"

W, H = 1920, 1080

# BuzzLab light palette
BG = (248, 250, 252)
INK = (15, 23, 42)
MUTED = (100, 116, 139)
ACCENT = (37, 99, 235)       # blue-600
GREEN = (22, 163, 74)
RED = (220, 38, 38)
AMBER = (217, 119, 6)
PANEL = (241, 245, 249)
BORDER = (203, 213, 225)

def font(size, bold=True):
    return ImageFont.truetype(FONT_PATH if bold else FONT_REG, size)

def text_size(d, txt, f):
    bbox = d.textbbox((0, 0), txt, font=f)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def base_canvas(scene_num, title, glossary_chip=None):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # Top title chip (left aligned)
    chip_h = 70
    f_t = font(36)
    chip_text = f"#{scene_num:02d}  {title}"
    tw, th = text_size(d, chip_text, f_t)
    d.rounded_rectangle((40, 30, 40 + tw + 60, 30 + chip_h), radius=18, fill=PANEL, outline=BORDER, width=2)
    d.text((70, 30 + (chip_h - th) // 2 - 4), chip_text, font=f_t, fill=INK)
    # Glossary chip bottom-left
    if glossary_chip:
        f_g = font(26, bold=False)
        gw, gh = text_size(d, glossary_chip, f_g)
        d.rounded_rectangle((40, H - 70, 40 + gw + 40, H - 70 + 50), radius=10, fill=(254, 243, 199), outline=AMBER, width=2)
        d.text((60, H - 70 + (50 - gh) // 2 - 4), glossary_chip, font=f_g, fill=INK)
    # Brand bottom-right
    f_b = font(22, bold=False)
    bw, bh = text_size(d, "AI Magic 50  ·  EP10  ·  MBO", f_b)
    d.text((W - bw - 50, H - 50), "AI Magic 50  ·  EP10  ·  MBO", font=f_b, fill=MUTED)
    return img, d

def big_center_text(d, text, y_center, size=120, color=INK):
    f = font(size)
    tw, th = text_size(d, text, f)
    d.text(((W - tw) // 2, y_center - th // 2), text, font=f, fill=color)

def multiline_center(d, lines, y_top, size=72, color=INK, line_gap=24):
    f = font(size)
    y = y_top
    for line in lines:
        tw, th = text_size(d, line, f)
        d.text(((W - tw) // 2, y), line, font=f, fill=color)
        y += th + line_gap
    return y

def card(d, x, y, w, h, title, body_lines, color=ACCENT):
    d.rounded_rectangle((x, y, x + w, y + h), radius=18, fill=PANEL, outline=color, width=4)
    f_t = font(40)
    f_b = font(28, bold=False)
    d.text((x + 24, y + 16), title, font=f_t, fill=color)
    yy = y + 70
    for line in body_lines:
        d.text((x + 24, yy), line, font=f_b, fill=INK)
        yy += 38

def arrow(d, x1, y1, x2, y2, color=ACCENT, width=6):
    d.line((x1, y1, x2, y2), fill=color, width=width)
    # arrowhead
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    h = 18
    d.polygon([
        (x2, y2),
        (x2 - h * math.cos(ang - 0.4), y2 - h * math.sin(ang - 0.4)),
        (x2 - h * math.cos(ang + 0.4), y2 - h * math.sin(ang + 0.4)),
    ], fill=color)

# === Scene definitions (51 scenes) ===
def s01(d, img):
    big_center_text(d, "MBO 방식으로 AI 작업시키기", 380, size=110, color=INK)
    big_center_text(d, "AI 결과물의 어긋남, 한 줄 합의로 끝낸다", 540, size=52, color=MUTED)
    big_center_text(d, "MBO", 770, size=200, color=ACCENT)

def s02(d, img):
    big_center_text(d, "1954년 · 피터 드러커", 380, size=80)
    big_center_text(d, "70년 된 경영 철학을 AI 협업에 이식", 500, size=56, color=MUTED)
    card(d, 660, 620, 600, 280, "The Practice of Management", ["저자: Peter Drucker", "출간: 1954년", "핵심: Management by Objectives"])

def s03(d, img):
    big_center_text(d, "등장 약어 6+", 280, size=80)
    chips = [
        ("MBO", "Management by Objectives"),
        ("OKR", "Objectives and Key Results"),
        ("SMART", "Specific·Measurable·Achievable·Relevant·Time-bound"),
        ("KPI", "Key Performance Indicator"),
        ("PO", "Product Owner"),
        ("SAL Grid", "Stage-Area-Level Grid"),
    ]
    f_a = font(48)
    f_b = font(26, bold=False)
    yy = 420
    for ab, full in chips:
        d.rounded_rectangle((180, yy, 320, yy + 64), radius=12, fill=ACCENT)
        d.text((196, yy + 12), ab, font=f_a, fill=(255,255,255))
        d.text((360, yy + 18), f"= {full}", font=f_b, fill=INK)
        yy += 90

def s04(d, img):
    big_center_text(d, "AI는 모호한 지시를 자기 식으로 해석한다", 320, size=64)
    d.rounded_rectangle((760, 460, 1160, 560), radius=18, fill=PANEL, outline=ACCENT, width=4)
    d.text((820, 488), "지시 (모호)", font=font(40), fill=INK)
    branches = ["해석 1", "해석 2", "해석 3", "해석 4", "해석 5", "해석 6"]
    for i, t in enumerate(branches):
        x = 200 + (i % 3) * 540
        y = 720 + (i // 3) * 130
        arrow(d, 960, 580, x + 130, y - 10, color=MUTED, width=4)
        d.rounded_rectangle((x, y, x + 280, y + 80), radius=12, fill=BG, outline=BORDER, width=2)
        d.text((x + 30, y + 20), t, font=font(34), fill=MUTED)

def s05(d, img):
    big_center_text(d, "30개 인스턴스 동시 운용", 280, size=72)
    big_center_text(d, "→ 어긋남이 30배로 곱해진다", 380, size=56, color=RED)
    # Grid 5x6
    sx, sy = 300, 500
    cw, ch = 220, 80
    gap = 12
    for r in range(5):
        for c in range(6):
            x = sx + c * (cw + gap)
            y = sy + r * (ch + gap)
            color = RED if (r + c) % 3 == 0 else AMBER if (r + c) % 3 == 1 else MUTED
            d.rounded_rectangle((x, y, x + cw, y + ch), radius=8, fill=color)
            d.text((x + 60, y + 22), f"AI #{r*6+c+1:02d}", font=font(28), fill=(255,255,255))

def s06(d, img):
    big_center_text(d, "SKILL_ATLAS — S5 사고 사례", 280, size=68)
    stages = ["S1", "S2", "S3", "S4", "S5", "S6"]
    sx = 240
    for i, st in enumerate(stages):
        x = sx + i * 240
        color = RED if st == "S5" else MUTED
        fill_color = RED if st == "S5" else PANEL
        text_color = (255,255,255) if st == "S5" else INK
        d.rounded_rectangle((x, 500, x + 200, 700), radius=18, fill=fill_color, outline=color, width=4)
        d.text((x + 70, 580), st, font=font(80), fill=text_color)
        if i < len(stages) - 1:
            arrow(d, x + 200, 600, x + 240, 600, color=MUTED, width=5)
    big_center_text(d, "배포 후 검증 단계에서 어긋남 발생", 820, size=44, color=MUTED)

def s07(d, img):
    big_center_text(d, "curl 200 OK 만 보고 검증 완료 처리", 280, size=58)
    # Terminal
    d.rounded_rectangle((300, 420, 1620, 820), radius=14, fill=(15, 23, 42))
    d.rectangle((300, 420, 1620, 480), fill=(30, 41, 59))
    d.ellipse((324, 440, 350, 466), fill=RED)
    d.ellipse((360, 440, 386, 466), fill=AMBER)
    d.ellipse((396, 440, 422, 466), fill=GREEN)
    d.text((1500, 442), "bash", font=font(24), fill=MUTED)
    f_term = font(34, bold=False)
    d.text((340, 520), "$ curl -I https://skill-atlas.vercel.app", font=f_term, fill=(167, 243, 208))
    d.text((340, 580), "HTTP/2 200", font=f_term, fill=GREEN)
    d.text((340, 630), "content-type: text/html; charset=utf-8", font=f_term, fill=MUTED)
    d.text((340, 700), "✓ Verified", font=font(40), fill=GREEN)

def s08(d, img):
    big_center_text(d, "그러나 브라우저에서는…", 280, size=64, color=RED)
    # Browser frame
    d.rounded_rectangle((300, 380, 1620, 980), radius=18, fill=PANEL, outline=BORDER, width=3)
    d.rectangle((300, 380, 1620, 440), fill=(226, 232, 240))
    d.text((340, 396), "https://skill-atlas.vercel.app", font=font(28, bold=False), fill=MUTED)
    btns = [("시작하기", 380, 540), ("더 알아보기", 380, 660), ("4개 은하", 1100, 540), ("View All", 1100, 660)]
    for label, x, y in btns:
        d.rounded_rectangle((x, y, x + 380, y + 80), radius=14, fill=BG, outline=RED, width=4)
        d.text((x + 30, y + 22), label, font=font(36), fill=INK)
        # Big X over button
        d.line((x + 320, y + 20, x + 360, y + 60), fill=RED, width=8)
        d.line((x + 360, y + 20, x + 320, y + 60), fill=RED, width=8)
    big_center_text(d, "버튼 4개 모두 무반응", 880, size=50, color=RED)

def s09(d, img):
    big_center_text(d, "두 종류의 KPI", 280, size=72)
    card(d, 200, 460, 720, 460, "데이터 레이어 KPI", ["✅ 테이블에 데이터가 있다", "✅ API 200 OK", "✅ DB row count = 30"], color=GREEN)
    card(d, 1000, 460, 720, 460, "사용자 여정 KPI", ["❌ 합의조차 안 됨", "❌ 버튼 4개 클릭 검증 누락", "❌ 라우트 정상 검증 누락"], color=RED)

def s10(d, img):
    big_center_text(d, "원인 = 합의 부재", 280, size=84, color=RED)
    boxes = [("지시", ACCENT), ("???", RED), ("실행", MUTED), ("결과", AMBER)]
    sx = 200
    for i, (label, color) in enumerate(boxes):
        x = sx + i * 380
        d.rounded_rectangle((x, 540, x + 320, 760), radius=20, fill=PANEL, outline=color, width=5)
        d.text((x + 110, 620), label, font=font(64), fill=color)
        if i < len(boxes) - 1:
            arrow(d, x + 320, 650, x + 380, 650, color=MUTED, width=6)
    big_center_text(d, "합의 단계가 빠져 있다", 880, size=44, color=MUTED)

def s11(d, img):
    multiline_center(d, ["프롬프트가 길수록", "AI가 자기 식으로 해석할 여지가 늘어난다"], 320, size=58)
    card(d, 200, 580, 720, 360, "긴 프롬프트", ["• 수십 줄 지시", "• 모호한 표현 다수", "• 해석 분기 ↑"], color=RED)
    card(d, 1000, 580, 720, 360, "짧은 합의", ["• 4표 양식", "• 수치 KPI", "• 해석 분기 0"], color=GREEN)

def s12(d, img):
    big_center_text(d, "진짜 해결책", 280, size=80)
    multiline_center(d, ["AI가 스스로 목표를 정리해", "PO에게 보여주고 승인받는 구조"], 460, size=58)
    # Approve stamp
    d.rounded_rectangle((760, 740, 1160, 860), radius=20, fill=GREEN)
    d.text((850, 770), "APPROVE", font=font(58), fill=(255, 255, 255))

def s13(d, img):
    big_center_text(d, "MBO", 480, size=300, color=ACCENT)
    big_center_text(d, "Management by Objectives", 760, size=56, color=MUTED)

def s14(d, img):
    big_center_text(d, "MBO = Management by Objectives", 360, size=64)
    big_center_text(d, "목표에 의한 관리", 480, size=80, color=ACCENT)
    big_center_text(d, "1954년 피터 드러커가 제시한 경영 철학", 660, size=44, color=MUTED)

def s15(d, img):
    big_center_text(d, "1954년", 320, size=110, color=ACCENT)
    big_center_text(d, "The Practice of Management", 470, size=64)
    big_center_text(d, "피터 드러커 — 경영의 실제", 580, size=44, color=MUTED)

def s16(d, img):
    multiline_center(d, ["조직 구성원 각자가", "상위 조직의 목표와 자신의 목표를 정렬하고,", "정해진 목표 대비 결과로 평가받는다"], 320, size=52)
    # Pyramid
    pts = [(960, 660), (760, 880), (1160, 880)]
    d.polygon(pts, fill=PANEL, outline=ACCENT, width=4)
    d.text((900, 740), "조직", font=font(40), fill=ACCENT)

def s17(d, img):
    big_center_text(d, "MBO의 가지", 220, size=70)
    # Tree
    d.rounded_rectangle((760, 360, 1160, 440), radius=16, fill=ACCENT)
    d.text((900, 376), "MBO", font=font(48), fill=(255,255,255))
    children = [("OKR", 280), ("SMART", 720), ("KPI", 1380)]
    for label, cx in children:
        arrow(d, 960, 440, cx + 140, 600, color=MUTED, width=4)
        d.rounded_rectangle((cx, 600, cx + 280, 700), radius=14, fill=PANEL, outline=ACCENT, width=3)
        d.text((cx + 70, 620), label, font=font(48), fill=INK)
    big_center_text(d, "70년이 지난 지금도 뿌리로 작동한다", 800, size=40, color=MUTED)

def s18(d, img):
    big_center_text(d, "본질 3단어", 240, size=64, color=MUTED)
    multiline_center(d, ["합의된 목표", "자율 실행", "결과 책임"], 400, size=130, color=ACCENT, line_gap=20)

def s19(d, img):
    big_center_text(d, "약어 정의", 220, size=64)
    boxes = [
        ("OKR", "Objectives and Key Results", "목표와 핵심 결과"),
        ("SMART", "Specific · Measurable · Achievable · Relevant · Time-bound", "5가지 목표 설정 기준 첫 글자"),
    ]
    yy = 380
    for ab, en, ko in boxes:
        d.rounded_rectangle((180, yy, 1740, yy + 200), radius=18, fill=PANEL, outline=ACCENT, width=3)
        d.text((220, yy + 24), ab, font=font(60), fill=ACCENT)
        d.text((220, yy + 100), en, font=font(36, bold=False), fill=INK)
        d.text((220, yy + 150), f"→ {ko}", font=font(34, bold=False), fill=MUTED)
        yy += 240

def s20(d, img):
    big_center_text(d, "OKR · SMART · KPI", 280, size=64)
    big_center_text(d, "서로 경쟁하는 개념이 아니라", 410, size=46, color=MUTED)
    big_center_text(d, "MBO라는 큰 줄기에서 갈라져 나온 가지들", 490, size=46, color=MUTED)
    # Tree (reuse)
    d.rounded_rectangle((760, 600, 1160, 680), radius=16, fill=ACCENT)
    d.text((900, 616), "MBO", font=font(48), fill=(255,255,255))
    children = [("OKR", 360), ("SMART", 800), ("KPI", 1300)]
    for label, cx in children:
        arrow(d, 960, 680, cx + 140, 800, color=MUTED, width=4)
        d.rounded_rectangle((cx, 800, cx + 280, 880), radius=14, fill=PANEL, outline=ACCENT, width=3)
        d.text((cx + 70, 818), label, font=font(40), fill=INK)

def s21(d, img):
    big_center_text(d, "OKR  vs  MBO", 320, size=110)
    big_center_text(d, "차이는 분명하다", 480, size=52, color=MUTED)
    d.rounded_rectangle((300, 600, 880, 920), radius=20, fill=PANEL, outline=AMBER, width=4)
    d.text((480, 640), "OKR", font=font(80), fill=AMBER)
    d.rounded_rectangle((1040, 600, 1620, 920), radius=20, fill=PANEL, outline=ACCENT, width=4)
    d.text((1230, 640), "MBO", font=font(80), fill=ACCENT)

def s22(d, img):
    big_center_text(d, "OKR = Aspirational", 320, size=72, color=AMBER)
    big_center_text(d, "도전 목표 · 70%면 성공", 460, size=56, color=MUTED)
    # Gauge
    d.arc((660, 580, 1260, 1000), start=180, end=0, fill=BORDER, width=40)
    d.arc((660, 580, 1260, 1000), start=180, end=180+180*0.7, fill=AMBER, width=40)
    big_center_text(d, "70%", 800, size=130, color=AMBER)

def s23(d, img):
    big_center_text(d, "MBO = Committed", 320, size=72, color=ACCENT)
    big_center_text(d, "합의 목표 · 100% 달성 의무", 460, size=56, color=MUTED)
    d.arc((660, 580, 1260, 1000), start=180, end=0, fill=BORDER, width=40)
    d.arc((660, 580, 1260, 1000), start=180, end=360, fill=ACCENT, width=40)
    big_center_text(d, "100%", 800, size=130, color=ACCENT)

def s24(d, img):
    big_center_text(d, "1인-AI 협업 구조에 적합한 쪽?", 320, size=58)
    big_center_text(d, "MBO", 600, size=240, color=ACCENT)

def s25(d, img):
    multiline_center(d, ["AI에게는", "도전이 의미가 없다"], 320, size=80)
    multiline_center(d, ["100% 달성  OR  미달성", "둘 중 하나"], 700, size=64, color=MUTED, line_gap=18)

def s26(d, img):
    multiline_center(d, ["절반 달성은 사실상 미달성", "그 사실을 솔직히 보고하게 만드는 구조"], 380, size=58)
    big_center_text(d, "Honest Report", 720, size=100, color=ACCENT)

def s27(d, img):
    big_center_text(d, "PO 철학", 280, size=84, color=ACCENT)
    big_center_text(d, "PO = Product Owner", 460, size=56)
    big_center_text(d, "작업을 시키는 사용자 본인", 560, size=44, color=MUTED)
    big_center_text(d, "1인-AI 협업에서는 사람", 670, size=44, color=MUTED)

def s28(d, img):
    multiline_center(d, ['"과정은 너의 마음대로', '진행해도 좋다"'], 380, size=92, color=ACCENT, line_gap=24)
    big_center_text(d, "— 자율", 760, size=64, color=MUTED)

def s29(d, img):
    multiline_center(d, ['"그러나 나랑 합의를 해서', '사전에 설정한 목표는 무조건 달성해야 한다"'], 350, size=64, color=ACCENT, line_gap=24)
    big_center_text(d, "— 책임", 780, size=64, color=MUTED)

def s30(d, img):
    big_center_text(d, "품질 · 비용 · 시간 — 3 균형", 280, size=58)
    items = [("품질", "최고로", GREEN), ("비용", "합리적", ACCENT), ("시간", "적절하게", AMBER)]
    sx = 240
    for i, (label, val, color) in enumerate(items):
        x = sx + i * 500
        d.rounded_rectangle((x, 480, x + 420, 880), radius=20, fill=PANEL, outline=color, width=5)
        d.text((x + 140, 520), label, font=font(64), fill=color)
        d.text((x + 130, 660), val, font=font(48), fill=INK)
        # mini gauge
        d.arc((x + 60, 740, x + 360, 880), start=180, end=0, fill=BORDER, width=24)
        end_pct = {"품질": 360, "비용": 270, "시간": 270}[label]
        d.arc((x + 60, 740, x + 360, 880), start=180, end=end_pct, fill=color, width=24)

def s31(d, img):
    big_center_text(d, "자율과 책임이 짝", 280, size=70)
    # balance scale
    d.line((960, 380, 960, 600), fill=INK, width=8)
    d.line((600, 600, 1320, 600), fill=INK, width=8)
    d.line((960, 380, 700, 580), fill=INK, width=4)
    d.line((960, 380, 1220, 580), fill=INK, width=4)
    d.rounded_rectangle((480, 700, 800, 860), radius=20, fill=PANEL, outline=ACCENT, width=4)
    d.text((570, 750), "자율", font=font(64), fill=ACCENT)
    d.rounded_rectangle((1120, 700, 1440, 860), radius=20, fill=PANEL, outline=GREEN, width=4)
    d.text((1180, 750), "책임", font=font(64), fill=GREEN)
    big_center_text(d, "방법은 마음대로 / 목표는 무조건", 940, size=42, color=MUTED)

def s32(d, img):
    big_center_text(d, "한 번 합의 → 끝까지 자율", 280, size=64)
    # gate + long track
    d.rounded_rectangle((180, 540, 380, 740), radius=18, fill=ACCENT)
    d.text((220, 600), "합의\n게이트", font=font(40), fill=(255,255,255))
    arrow(d, 380, 640, 1740, 640, color=MUTED, width=10)
    big_center_text(d, "PO 간섭 없음", 800, size=50, color=MUTED)

def s33(d, img):
    big_center_text(d, "MBO  3 PHASE", 240, size=110, color=ACCENT)
    phases = [("PHASE 1", "목표 정의", "PO 승인 필수"), ("PHASE 2", "실행", "PO 간섭 없음"), ("PHASE 3", "결과 보고", "O / X 표기")]
    sx = 200
    for i, (label, title, sub) in enumerate(phases):
        x = sx + i * 540
        d.rounded_rectangle((x, 480, x + 480, 880), radius=24, fill=PANEL, outline=ACCENT, width=5)
        d.text((x + 40, 510), label, font=font(46), fill=ACCENT)
        d.text((x + 40, 600), title, font=font(60), fill=INK)
        d.text((x + 40, 720), sub, font=font(36, bold=False), fill=MUTED)
        if i < 2:
            arrow(d, x + 480, 680, x + 540, 680, color=ACCENT, width=8)

def s34(d, img):
    card(d, 360, 280, 1200, 720, "PHASE 1 — 목표 정의", [
        "맥락 분석 → AS-IS 조사 → TO-BE 정의",
        "→ KPI 설정 → Task 도출",
        "→ PO 승인 대기",
        "",
        "★ 승인 없이 PHASE 2 진입 절대 금지",
    ], color=ACCENT)

def s35(d, img):
    card(d, 360, 280, 1200, 720, "PHASE 2 — 실행", [
        "목표서 파일 저장",
        "Task 순서대로 실행",
        "필요 시 KPI 현황표 중간 점검",
        "",
        "★ PO 간섭 없음 · 자율",
        "★ 합의 범위 이탈 시 즉시 보고",
    ], color=GREEN)

def s36(d, img):
    card(d, 360, 280, 1200, 720, "PHASE 3 — 결과 보고", [
        "AS-IS / TO-BE / 실제 결과  O · X 표",
        "KPI 실측 + 미달성 사유 + 후속조치",
        "총평",
        "",
        "★ 미달성도 정직하게 기록",
        "★ 같은 MBO 파일 하단에 추가",
    ], color=AMBER)

def s37(d, img):
    big_center_text(d, "3 PHASE는 한 묶음", 320, size=72)
    cards_x = [240, 760, 1280]
    for i, (lbl, color) in enumerate(zip(["PHASE 1", "PHASE 2", "PHASE 3"], [ACCENT, GREEN, AMBER])):
        d.rounded_rectangle((cards_x[i], 540, cards_x[i] + 400, 800), radius=20, fill=PANEL, outline=color, width=4)
        d.text((cards_x[i] + 80, 620), lbl, font=font(50), fill=color)
    # Clip
    d.line((220, 860, 1700, 860), fill=INK, width=10)
    big_center_text(d, "셋이 분리되면 의미 없음", 920, size=42, color=MUTED)

def s38(d, img):
    multiline_center(d, ["결과 보고를 빼먹는 게", "가장 큰 손실"], 280, size=72, line_gap=18)
    big_center_text(d, "4,000시간 운용 경험에서 확인", 540, size=46, color=MUTED)
    # Mini chart
    d.line((300, 880, 1620, 880), fill=BORDER, width=3)
    d.line((300, 700, 300, 880), fill=BORDER, width=3)
    pts = [(300, 870), (520, 850), (740, 800), (960, 760), (1180, 720), (1400, 700), (1620, 690)]
    for i in range(len(pts) - 1):
        d.line(pts[i] + pts[i+1], fill=ACCENT, width=6)
    for p in pts:
        d.ellipse((p[0]-8, p[1]-8, p[0]+8, p[1]+8), fill=ACCENT)
    d.text((1300, 860), "정확도 ↑", font=font(34), fill=ACCENT)

def s39(d, img):
    big_center_text(d, "MBO 목표서  4표 양식", 240, size=80, color=ACCENT)
    titles = ["1. 현재 vs 목표", "2. 측정 지표 KPI", "3. 실행 계획", "4. 리스크 · 대응"]
    for i, t in enumerate(titles):
        x = 240 + (i % 2) * 800
        y = 420 + (i // 2) * 280
        d.rounded_rectangle((x, y, x + 720, y + 240), radius=18, fill=PANEL, outline=ACCENT, width=4)
        d.text((x + 40, y + 80), t, font=font(50), fill=INK)

def s40(d, img):
    big_center_text(d, "표 1 — 현재 vs 목표", 240, size=72, color=ACCENT)
    rows = [("항목", "AS-IS", "TO-BE"), ("Lighthouse", "67", "≥ 90"), ("LCP", "4.2s", "≤ 2.5s"), ("버튼 클릭 OK", "0/4", "4/4")]
    sx, sy = 240, 460
    cw = [400, 480, 480]
    rh = 100
    for r, row in enumerate(rows):
        for c, cell in enumerate(row):
            x = sx + sum(cw[:c])
            y = sy + r * rh
            fill = ACCENT if r == 0 else PANEL
            tc = (255,255,255) if r == 0 else INK
            d.rectangle((x, y, x + cw[c], y + rh), fill=fill, outline=BORDER, width=2)
            d.text((x + 30, y + 30), cell, font=font(40), fill=tc)

def s41(d, img):
    big_center_text(d, "AS-IS  =  As Is  =  지금 그대로의 상태", 380, size=58)
    big_center_text(d, "TO-BE  =  To Be  =  지향하는 상태", 540, size=58)
    big_center_text(d, "표 1 = 현재 vs 목표 항목별 대비", 760, size=44, color=MUTED)

def s42(d, img):
    big_center_text(d, "표 2 — 측정 지표 KPI", 240, size=72, color=ACCENT)
    rows = [("지표", "현재값", "목표값", "측정 방법"), ("Lighthouse", "67", "≥ 90", "lighthouse-cli"), ("LCP", "4.2s", "≤ 2.5s", "Web Vitals"), ("Button OK", "0/4", "4/4", "Playwright click")]
    sx, sy = 100, 440
    cw = [320, 320, 320, 600]
    rh = 100
    for r, row in enumerate(rows):
        for c, cell in enumerate(row):
            x = sx + sum(cw[:c])
            y = sy + r * rh
            fill = ACCENT if r == 0 else PANEL
            tc = (255,255,255) if r == 0 else INK
            d.rectangle((x, y, x + cw[c], y + rh), fill=fill, outline=BORDER, width=2)
            d.text((x + 24, y + 30), cell, font=font(36), fill=tc)

def s43(d, img):
    big_center_text(d, "수치화 강제", 280, size=80, color=RED)
    multiline_center(d, ['"좋게 만든다"  ✗', 'Lighthouse 80 → 95  ✓'], 460, size=72, line_gap=18)
    big_center_text(d, "측정 불가능한 KPI는 자동 거부", 800, size=46, color=MUTED)

def s44(d, img):
    big_center_text(d, "표 3 — 실행 계획", 240, size=72, color=ACCENT)
    rows = [("작업", "설명", "예상 결과"), ("이미지 압축", "WebP 변환", "용량 -60%"), ("코드 분할", "route 단위 split", "JS -40%"), ("폰트 서브셋", "한글 KS X 1001", "Font -75%")]
    sx, sy = 100, 440
    cw = [380, 660, 540]
    rh = 100
    for r, row in enumerate(rows):
        for c, cell in enumerate(row):
            x = sx + sum(cw[:c])
            y = sy + r * rh
            fill = ACCENT if r == 0 else PANEL
            tc = (255,255,255) if r == 0 else INK
            d.rectangle((x, y, x + cw[c], y + rh), fill=fill, outline=BORDER, width=2)
            d.text((x + 24, y + 30), cell, font=font(34), fill=tc)

def s45(d, img):
    big_center_text(d, "표 4 — 리스크 · 대응", 240, size=72, color=ACCENT)
    rows = [("리스크", "대응"), ("폰트 서브셋 한글 깨짐", "KS X 1001 전수 테스트"), ("이미지 품질 저하", "사양별 비교 + 임계치")]
    sx, sy = 240, 440
    cw = [620, 800]
    rh = 100
    for r, row in enumerate(rows):
        for c, cell in enumerate(row):
            x = sx + sum(cw[:c])
            y = sy + r * rh
            fill = ACCENT if r == 0 else PANEL
            tc = (255,255,255) if r == 0 else INK
            d.rectangle((x, y, x + cw[c], y + rh), fill=fill, outline=BORDER, width=2)
            d.text((x + 24, y + 30), cell, font=font(32), fill=tc)
    # Approve stamp
    d.rounded_rectangle((660, 800, 1260, 920), radius=20, fill=GREEN)
    d.text((720, 830), "이 목표를 승인하시겠습니까?", font=font(44), fill=(255,255,255))

def s46(d, img):
    big_center_text(d, "KPI는 두 종류 모두 필수", 240, size=64)
    card(d, 200, 460, 720, 460, "데이터 레이어 KPI", ["✅ 테이블 데이터 존재", "✅ API 200 OK", "✅ DB row count"], color=GREEN)
    card(d, 1000, 460, 720, 460, "사용자 여정 KPI", ["✅ 버튼 클릭 OK", "✅ 라우트 네비게이트 OK", "✅ 주요 흐름 E2E"], color=ACCENT)
    big_center_text(d, "한쪽만 있으면 반쪽짜리 합의", 980, size=42, color=MUTED)

def s47(d, img):
    big_center_text(d, "실전 예시 — 랜딩 페이지 성능 개선", 240, size=58)
    big_center_text(d, "Lighthouse  67  →  90", 480, size=110, color=ACCENT)
    # mini gauges
    d.arc((480, 700, 880, 980), start=180, end=0, fill=BORDER, width=30)
    d.arc((480, 700, 880, 980), start=180, end=180+180*0.67, fill=AMBER, width=30)
    d.text((620, 770), "67", font=font(72), fill=AMBER)
    d.arc((1040, 700, 1440, 980), start=180, end=0, fill=BORDER, width=30)
    d.arc((1040, 700, 1440, 980), start=180, end=360, fill=GREEN, width=30)
    d.text((1180, 770), "90+", font=font(72), fill=GREEN)

def s48(d, img):
    big_center_text(d, "KPI 채우기", 240, size=64)
    rows = [("KPI 종류", "값"),
            ("데이터: LCP", "≤ 2.5초"),
            ("사용자 여정: 버튼 4개", "클릭 1초 이내"),
            ("E2E 통과율", "12/12")]
    sx, sy = 240, 420
    cw = [820, 660]
    rh = 100
    for r, row in enumerate(rows):
        for c, cell in enumerate(row):
            x = sx + sum(cw[:c])
            y = sy + r * rh
            fill = ACCENT if r == 0 else PANEL
            tc = (255,255,255) if r == 0 else INK
            d.rectangle((x, y, x + cw[c], y + rh), fill=fill, outline=BORDER, width=2)
            d.text((x + 24, y + 30), cell, font=font(34), fill=tc)

def s49(d, img):
    big_center_text(d, "표 3 · 4 채우기", 240, size=64)
    multiline_center(d, ["실행: 이미지 압축 · 코드 분할 · 폰트 서브셋",
                         "리스크: KS X 1001 한글 깨짐 → 전수 테스트"], 460, size=44, line_gap=18)
    # complete stamp
    d.rounded_rectangle((660, 760, 1260, 900), radius=24, fill=GREEN)
    d.text((780, 790), "4표 완성", font=font(60), fill=(255,255,255))

def s50(d, img):
    big_center_text(d, "실전 6단계", 220, size=80, color=ACCENT)
    steps = ["/mbo 발동", "4표 PO 제시", "KPI 수치화", "파일 저장", "자율 실행", "/mbo report"]
    sx = 100
    for i, s in enumerate(steps):
        x = sx + i * 300
        d.rounded_rectangle((x, 500, x + 280, 760), radius=18, fill=PANEL, outline=ACCENT, width=4)
        d.text((x + 100, 530), str(i + 1), font=font(80), fill=ACCENT)
        d.text((x + 30, 660), s, font=font(28), fill=INK)
        if i < 5:
            arrow(d, x + 280, 630, x + 300, 630, color=MUTED, width=4)
    big_center_text(d, "미달성도 사유 + 후속조치 의무 기재", 850, size=40, color=MUTED)

def s51(d, img):
    # Wide diagram: SAL Grid + MBO + summary
    big_center_text(d, "SAL Grid  ×  MBO", 200, size=80, color=ACCENT)
    big_center_text(d, "두 스킬은 분리해 쓰지 않는다", 320, size=44, color=MUTED)
    # Left: SAL Grid
    d.rounded_rectangle((80, 420, 920, 920), radius=24, fill=PANEL, outline=GREEN, width=4)
    d.text((280, 440), "SAL Grid", font=font(60), fill=GREEN)
    d.text((140, 540), "Stage · Area · Level", font=font(40, bold=False), fill=INK)
    d.text((140, 620), "→ 실행 골격", font=font(36), fill=MUTED)
    d.text((140, 700), "Stage 진입 키워드 감지", font=font(32, bold=False), fill=INK)
    d.text((140, 760), "→ MBO 자동 발동", font=font(32, bold=False), fill=ACCENT)
    # Right: MBO
    d.rounded_rectangle((1000, 420, 1840, 920), radius=24, fill=PANEL, outline=ACCENT, width=4)
    d.text((1280, 440), "MBO", font=font(60), fill=ACCENT)
    d.text((1060, 540), "4표 양식 + 6단계", font=font(40, bold=False), fill=INK)
    d.text((1060, 620), "→ 합의 골격", font=font(36), fill=MUTED)
    d.text((1060, 700), "합의된 목표 · 자율 실행", font=font(32, bold=False), fill=INK)
    d.text((1060, 760), "결과 책임", font=font(32, bold=False), fill=INK)
    # Bottom CTA
    big_center_text(d, "다음 작업 시작 전, /mbo 한 번", 970, size=52, color=ACCENT)

# Map scene number to (renderer, title, glossary chip)
SCENES = {
    1: (s01, "Hook", None),
    2: (s02, "도입 — 1954 드러커", None),
    3: (s03, "약어 미리보기", "약어는 좌하단 · 본문 첫 등장에 음성 풀이"),
    4: (s04, "어긋남의 정체", None),
    5: (s05, "30배로 곱해진다", None),
    6: (s06, "SKILL_ATLAS S5 사고", None),
    7: (s07, "curl 200 OK", "curl = HTTP 요청 명령줄 도구"),
    8: (s08, "버튼 4개 무반응", None),
    9: (s09, "KPI 두 종류", "KPI = Key Performance Indicator (핵심 성과 지표)"),
    10: (s10, "원인 = 합의 부재", None),
    11: (s11, "긴 프롬프트 ≠ 해결책", None),
    12: (s12, "진짜 해결책", "PO = Product Owner (작업을 시키는 사용자)"),
    13: (s13, "MBO 등장", None),
    14: (s14, "MBO 정식 정의", "MBO = Management by Objectives (목표에 의한 관리)"),
    15: (s15, "1954년 출발", None),
    16: (s16, "핵심 원리", None),
    17: (s17, "MBO의 가지", "OKR · SMART · KPI 모두 MBO 뿌리에서 출발"),
    18: (s18, "본질 3단어", None),
    19: (s19, "약어 정의", "OKR = Objectives and Key Results"),
    20: (s20, "큰 줄기에서 갈라져 나온 가지", None),
    21: (s21, "OKR vs MBO", None),
    22: (s22, "OKR = 70%", None),
    23: (s23, "MBO = 100%", None),
    24: (s24, "AI 협업에는 MBO", None),
    25: (s25, "AI에게 도전은 의미 없음", None),
    26: (s26, "솔직 보고 구조", None),
    27: (s27, "PO 철학", "PO = Product Owner (작업을 시키는 사용자)"),
    28: (s28, "과정은 마음대로", None),
    29: (s29, "목표는 무조건", None),
    30: (s30, "품질 · 비용 · 시간", None),
    31: (s31, "자율 + 책임", None),
    32: (s32, "한 번 합의 → 자율", None),
    33: (s33, "3 PHASE 구조", None),
    34: (s34, "PHASE 1 — 목표 정의", None),
    35: (s35, "PHASE 2 — 실행", None),
    36: (s36, "PHASE 3 — 결과 보고", None),
    37: (s37, "셋이 한 묶음", None),
    38: (s38, "결과 보고 누락이 가장 큰 손실", None),
    39: (s39, "4표 양식", None),
    40: (s40, "표 1 — 현재 vs 목표", "AS-IS = As Is · TO-BE = To Be"),
    41: (s41, "AS-IS / TO-BE 정의", None),
    42: (s42, "표 2 — KPI", "Lighthouse = 구글 웹 성능 측정 도구"),
    43: (s43, "수치화 강제", None),
    44: (s44, "표 3 — 실행 계획", None),
    45: (s45, "표 4 — 리스크 · 승인", None),
    46: (s46, "KPI 두 종류 필수", None),
    47: (s47, "실전 예시 — 랜딩 67 → 90", "LCP = Largest Contentful Paint"),
    48: (s48, "KPI 채우기", None),
    49: (s49, "실행 + 리스크 채우기", "KS X 1001 = 한국 산업 표준 한글 인코딩"),
    50: (s50, "실전 6단계", None),
    51: (s51, "SAL Grid × MBO", "SAL Grid = Stage-Area-Level Grid"),
}

print(f"[INFO] Rendering {len(SCENES)} scenes...")
for n, (renderer, title, chip) in SCENES.items():
    img, d = base_canvas(n, title, glossary_chip=chip)
    renderer(d, img)
    out_path = OUT / f"ai_scene_{n:02d}.png"
    img.save(out_path, optimize=True)
    print(f"[{n:02d}] {title}")

print(f"[OK] {len(SCENES)} scenes saved to {OUT}")
