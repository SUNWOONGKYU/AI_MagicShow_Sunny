"""
SUNNY AI MAGIC 50 — 표지 좌상단 헤더 오버레이 합성

각 MD frontmatter의 title/subtitle을 표지 PNG 좌상단에 합성한다.
- 폰트: 맑은 고딕 (Bold/Regular)
- 박스: 반투명 다크 (rgba 0,0,0,150) + 라운드 코너
- 위치: 좌상단 (margin 24px)
- 크기: 가로 60% × 자동 높이
"""

import sys, io, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

MD_DIR = Path(r"G:/내 드라이브/333_자료공유폴더/Sunny_Magic_Show/AI_Magic50/상세/md_new번호")
COVER_DIR = Path(r"G:/내 드라이브/333_자료공유폴더/Sunny_Magic_Show/AI_Magic50/슬라이드쇼/covers")

FONT_BOLD = r"C:/Windows/Fonts/malgunbd.ttf"
FONT_REG = r"C:/Windows/Fonts/malgun.ttf"

def parse_frontmatter(md_path: Path):
    """Extract id, title, subtitle from YAML frontmatter."""
    text = md_path.read_text(encoding='utf-8', errors='replace')
    m = re.search(r'^---\n(.*?)\n---', text, re.DOTALL)
    if not m: return None
    fm = m.group(1)
    out = {}
    for line in fm.split('\n'):
        m2 = re.match(r'^(id|title|subtitle):\s*(.+)$', line)
        if m2:
            k, v = m2.group(1), m2.group(2).strip()
            v = v.strip('"').strip("'")
            out[k] = v
    return out

def tokenize(text):
    """한글/공백/구두점은 단일 토큰, 영문/숫자 연속은 단어 단위 토큰."""
    tokens = []
    i = 0
    while i < len(text):
        if re.match(r'[A-Za-z0-9]', text[i]):
            j = i
            while j < len(text) and re.match(r'[A-Za-z0-9]', text[j]):
                j += 1
            tokens.append(text[i:j])
            i = j
        else:
            tokens.append(text[i])
            i += 1
    return tokens

def wrap_text(draw, text, font, max_w):
    """토큰 기반 줄바꿈. 영문 단어는 가운데서 끊지 않음. 한글은 글자 단위."""
    if not text: return []
    tokens = tokenize(text)
    lines = []
    cur = ""
    for tok in tokens:
        # 토큰 자체가 max_w 초과 → 강제 글자 단위 분할
        if draw.textlength(tok, font=font) > max_w:
            for ch in tok:
                test = cur + ch
                if draw.textlength(test, font=font) > max_w and cur.strip():
                    lines.append(cur.rstrip()); cur = ch
                else:
                    cur = test
            continue
        test = cur + tok
        if draw.textlength(test, font=font) > max_w and cur.strip():
            lines.append(cur.rstrip())
            # 새 줄 시작은 공백 토큰 스킵
            cur = "" if tok.isspace() else tok
        else:
            cur = test
    if cur.strip(): lines.append(cur.rstrip())
    return lines

def overlay(cover_path: Path, num: str, title: str, subtitle: str, out_path: Path):
    img = Image.open(cover_path).convert("RGBA")
    W, H = img.size
    overlay = Image.new("RGBA", (W, H), (0,0,0,0))
    draw = ImageDraw.Draw(overlay)

    # Layout
    margin = int(W * 0.025)
    box_w = int(W * 0.62)
    pad = int(W * 0.018)

    # Font sizes — scale with image width
    f_num_size  = max(int(W * 0.025), 14)
    f_title_size = max(int(W * 0.038), 22)
    f_sub_size   = max(int(W * 0.022), 13)

    f_num = ImageFont.truetype(FONT_REG,  f_num_size)
    f_title = ImageFont.truetype(FONT_BOLD, f_title_size)
    f_sub = ImageFont.truetype(FONT_REG,  f_sub_size)

    # Wrap
    title_lines = wrap_text(draw, title, f_title, box_w - 2*pad)
    sub_lines = wrap_text(draw, subtitle, f_sub, box_w - 2*pad)
    # Limit subtitle to 2 lines max — truncate with ellipsis
    if len(sub_lines) > 2:
        sub_lines = sub_lines[:2]
        last = sub_lines[-1]
        # Truncate last line until it fits with '…'
        while draw.textlength(last + '…', font=f_sub) > box_w - 2*pad and len(last) > 5:
            last = last[:-1]
        sub_lines[-1] = last + '…'

    # Compute box height
    line_gap = int(f_title_size * 0.18)
    sub_gap = int(f_sub_size * 0.22)
    h_num = f_num_size + 4
    h_title = len(title_lines) * f_title_size + (len(title_lines)-1) * line_gap
    h_sub = len(sub_lines) * f_sub_size + (len(sub_lines)-1) * sub_gap
    box_h = pad + h_num + 8 + h_title + 10 + h_sub + pad

    # Rounded rect background
    box_xy = [margin, margin, margin + box_w, margin + box_h]
    radius = int(pad * 0.9)
    draw.rounded_rectangle(box_xy, radius=radius, fill=(15, 20, 35, 205))

    # Accent left bar
    bar_w = int(W * 0.006)
    draw.rounded_rectangle(
        [margin, margin + pad//2, margin + bar_w, margin + box_h - pad//2],
        radius=bar_w, fill=(255, 196, 64, 255)
    )

    # Text positions
    x_text = margin + pad + bar_w + int(W * 0.008)
    y = margin + pad

    # #NN (gray small)
    draw.text((x_text, y), f"#{num}", font=f_num, fill=(200, 210, 230, 255))
    y += h_num + 8

    # Title (white bold)
    for line in title_lines:
        draw.text((x_text, y), line, font=f_title, fill=(255, 255, 255, 255))
        y += f_title_size + line_gap
    y -= line_gap
    y += 10

    # Subtitle (light amber)
    for line in sub_lines:
        draw.text((x_text, y), line, font=f_sub, fill=(255, 220, 150, 255))
        y += f_sub_size + sub_gap

    # Composite
    composed = Image.alpha_composite(img, overlay).convert("RGB")
    composed.save(out_path, "PNG", optimize=True)

def main():
    md_files = sorted(MD_DIR.glob("*.md"))
    md_files = [m for m in md_files if not m.name.startswith('_')]

    print(f"Found {len(md_files)} MD files")
    results = []
    only = sys.argv[1] if len(sys.argv) > 1 else None

    for md in md_files:
        fm = parse_frontmatter(md)
        if not fm: continue
        try:
            num = f"{int(fm['id']):02d}"
        except Exception:
            continue

        if only and only != num:
            continue

        cover = COVER_DIR / f"{num}.png"
        if not cover.exists():
            print(f"[SKIP] #{num}: cover not found")
            continue

        out = COVER_DIR / f"{num}_titled.png"
        try:
            overlay(cover, num, fm.get('title','').strip(), fm.get('subtitle','').strip(), out)
            print(f"[OK] #{num} -> {out.name}")
            results.append(num)
        except Exception as e:
            print(f"[FAIL] #{num}: {e}")

    print(f"\nDONE — {len(results)} 장")

if __name__ == "__main__":
    main()
