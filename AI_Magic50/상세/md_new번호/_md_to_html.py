# -*- coding: utf-8 -*-
"""
MD 50개를 슬라이드쇼 patent/ 폴더에 HTML로 일괄 변환.
- 기존 14개 HTML(특허 페이지)이 있는 항목은 SKIP (덮어쓰지 않음)
- 새로 만드는 HTML은 동일한 다크 테마 스타일 적용
- frontmatter에서 메타데이터 추출
"""
import re
import os
from pathlib import Path
import markdown

SRC = Path(r"G:\내 드라이브\333_자료공유폴더\Sunny_Magic_Show\AI_Magic50\상세\md_new번호")
DST = Path(r"G:\내 드라이브\333_자료공유폴더\Sunny_Magic_Show\AI_Magic50\슬라이드쇼\book")
DST.mkdir(parents=True, exist_ok=True)

# 기존 patent/ HTML이 있는 새 번호 (덮어쓰지 않을 대상)
EXISTING_PATENT_NUMS = {2, 3, 12, 13, 14, 23, 24, 26, 28, 39, 45, 50}

def parse_frontmatter(text):
    if not text.startswith('---'):
        return {}, text
    parts = text.split('---', 2)
    if len(parts) < 3:
        return {}, text
    fm_raw = parts[1]
    body = parts[2].lstrip('\n')
    meta = {}
    for line in fm_raw.splitlines():
        m = re.match(r'^(\w+):\s*(.*)$', line)
        if m:
            key = m.group(1)
            val = m.group(2).strip().strip('"').strip("'")
            if val:
                meta[key] = val
    return meta, body

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow">
<title>SUNNY AI MAGIC 50 · #{num_pad} {title}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{font-family:'Malgun Gothic','Apple SD Gothic Neo',sans-serif;background:#000814;color:#fff;line-height:1.7}}
.hero{{background:radial-gradient(circle at 30% 30%,#002d5c 0%,#000814 70%);padding:50px 24px 40px;text-align:center;border-bottom:3px solid #FF8C00}}
.hero .tag{{color:#FF8C00;font-size:13px;font-weight:900;letter-spacing:5px;margin-bottom:12px}}
.hero h1{{font-size:clamp(22px,4vw,40px);font-weight:900;line-height:1.25;margin-bottom:8px;color:#fff;text-shadow:0 4px 24px rgba(255,140,0,0.35)}}
.hero .subtitle{{font-size:clamp(13px,1.6vw,17px);color:#FF8C00;font-weight:600;letter-spacing:0.3px;margin-bottom:14px;opacity:0.92}}
.hero .meta{{display:inline-flex;gap:10px;flex-wrap:wrap;justify-content:center;margin-top:10px}}
.hero .badge{{background:rgba(255,140,0,0.15);color:#FF8C00;padding:5px 14px;border-radius:20px;font-size:12px;font-weight:900;letter-spacing:1px;border:1px solid rgba(255,140,0,0.4)}}
.hero .badge.type-a{{background:rgba(231,76,60,0.15);color:#e74c3c;border-color:rgba(231,76,60,0.4)}}
.hero .badge.type-b{{background:rgba(52,152,219,0.15);color:#3498DB;border-color:rgba(52,152,219,0.4)}}
.hero .badge.type-c{{background:rgba(63,185,80,0.15);color:#3fb950;border-color:rgba(63,185,80,0.4)}}
.back{{position:absolute;top:20px;left:20px;color:#FF8C00;text-decoration:none;font-size:13px;font-weight:700;padding:7px 14px;border:2px solid #FF8C00;border-radius:18px}}
.back:hover{{background:#FF8C00;color:#001020}}
.content{{max-width:900px;margin:0 auto;padding:40px 24px 60px}}
.content h1{{display:none}}
.content h2{{font-size:clamp(20px,2.8vw,28px);font-weight:900;color:#FF8C00;margin:32px 0 16px;letter-spacing:0.5px;border-left:5px solid #FF8C00;padding-left:14px}}
.content h2:first-child{{margin-top:0}}
.content h3{{font-size:18px;font-weight:900;color:#fff;margin:24px 0 12px}}
.content h4{{font-size:16px;font-weight:700;color:#FF8C00;margin:18px 0 10px}}
.content p{{font-size:15px;color:#dde;margin-bottom:14px}}
.content ul,.content ol{{margin:0 0 16px 24px;color:#dde}}
.content li{{font-size:15px;margin-bottom:6px;line-height:1.7}}
.content strong{{color:#fff;font-weight:900}}
.content em{{color:#FF8C00;font-style:normal;font-weight:600}}
.content code{{background:rgba(255,140,0,0.12);color:#FF8C00;padding:2px 6px;border-radius:4px;font-size:13px;font-family:'D2Coding','Consolas',monospace}}
.content pre{{background:rgba(0,0,0,0.4);border:1px solid rgba(255,140,0,0.25);border-radius:8px;padding:16px;overflow-x:auto;margin:16px 0}}
.content pre code{{background:none;color:#bcd;padding:0;font-size:13px}}
.content blockquote{{border-left:4px solid #FF8C00;background:rgba(255,140,0,0.05);padding:14px 20px;margin:16px 0;border-radius:0 8px 8px 0;color:#bcd}}
.content table{{width:100%;border-collapse:collapse;margin:18px 0;background:rgba(255,255,255,0.03);border-radius:8px;overflow:hidden;font-size:14px}}
.content th,.content td{{padding:10px 12px;text-align:left;border-bottom:1px solid rgba(255,255,255,0.08)}}
.content th{{background:rgba(255,140,0,0.15);color:#FF8C00;font-weight:900}}
.content td{{color:#dde}}
.content tr:last-child td{{border-bottom:none}}
.content hr{{border:none;border-top:1px solid rgba(255,140,0,0.2);margin:30px 0}}
.content a{{color:#FF8C00;text-decoration:none;border-bottom:1px dashed rgba(255,140,0,0.4)}}
.content a:hover{{border-bottom-style:solid}}
.footer{{background:#001020;border-top:1px solid #1a2a3a;padding:24px;text-align:center;color:#7a8c9c;font-size:13px}}
.footer a{{color:#FF8C00;text-decoration:none;margin:0 10px}}
</style>
</head>
<body>
<a href="../index.html" class="back">← 슬라이드쇼로</a>
<section class="hero">
  <div class="tag">SUNNY AI MAGIC 50 · #{num_pad}</div>
  <h1>{title}</h1>
  {subtitle_html}
  <div class="meta">
    <span class="badge">G{gid} · {gname}</span>
    {type_badge}
    {patent_badge}
  </div>
</section>

<section class="content">
{body_html}
</section>

<div class="footer">
  <a href="../index.html">← SUNNY AI MAGIC 50</a>
  <div style="margin-top:10px;color:#5a6c7c;font-size:12px;letter-spacing:0.3px">© 2026 SUN WOONGKYU · SUNNY AI MAGIC 50 · CC BY-NC-ND 4.0 · 특허 별도 보유</div>
</div>
</body>
</html>
"""

def convert(md_path):
    text = md_path.read_text(encoding='utf-8')
    meta, body = parse_frontmatter(text)

    # 파일명에서 새 번호 추출
    m = re.match(r'^(\d{2})_', md_path.name)
    if not m:
        return None
    num = int(m.group(1))
    num_pad = f"{num:02d}"

    title = meta.get('title', md_path.stem)
    subtitle = meta.get('subtitle', '')
    gid = meta.get('group_id', '?')
    gname = meta.get('group_name', '')
    type_letter = meta.get('type', 'C').upper()
    patent = meta.get('patent', '')

    # 본문 첫 줄 h1 제거 (hero에서 표시)
    body = re.sub(r'^\s*#\s+[^\n]+\n+', '', body, count=1)

    # markdown → HTML
    body_html = markdown.markdown(
        body,
        extensions=['tables', 'fenced_code', 'attr_list', 'sane_lists']
    )

    type_badge = f'<span class="badge type-{type_letter.lower()}">{type_letter}타입</span>'
    patent_badge = f'<span class="badge">📜 특허 {patent}</span>' if patent else ''
    subtitle_html = f'<div class="subtitle">{subtitle}</div>' if subtitle else ''

    html = HTML_TEMPLATE.format(
        num_pad=num_pad,
        title=title,
        subtitle_html=subtitle_html,
        gid=gid,
        gname=gname,
        type_badge=type_badge,
        patent_badge=patent_badge,
        body_html=body_html,
    )

    return num, html

if __name__ == "__main__":
    converted = []
    skipped = []
    for f in sorted(SRC.glob("*.md")):
        if f.name.startswith("_"):
            continue
        result = convert(f)
        if result is None:
            continue
        num, html = result

        # book/ 폴더에 모두 저장 (책 원고용)
        out_name = f"{num:02d}.html"
        out_path = DST / out_name
        out_path.write_text(html, encoding='utf-8')
        converted.append(out_name)

    print(f"변환 완료: {len(converted)}개 → book/")
    for n in converted[:5]:
        print(f"  {n}")
    print(f"  ... 외 {len(converted)-5}개")
