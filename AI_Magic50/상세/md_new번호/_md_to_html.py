# -*- coding: utf-8 -*-
"""
MD 50개를 슬라이드쇼 patent/ 폴더에 HTML로 일괄 변환.
- 기존 14개 HTML(특허 페이지)이 있는 항목은 SKIP (덮어쓰지 않음)
- 브랜드 디자인 시스템 적용 (골드+포레스트그린+크림 + Pretendard)
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
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/variable/pretendardvariable.css">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
:root{{
  --c-dark:#0A1F14;--c-forest:#2D6A4F;--c-sage:#9FC7AF;
  --c-gold:#C9A961;--c-gold-deep:#A88A4A;--c-gold-soft:#E3CB8C;
  --c-alert:#8B2635;
  --c-bg:#FAFAF7;--c-surface:#FFFFFF;--c-border:#E6E2D6;
  --c-text:#1a2332;--c-body:#3a4558;--c-muted:#5f6b7a;
}}
html,body{{font-family:'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif;background:var(--c-bg);color:var(--c-body);line-height:1.7}}
.hero{{background:linear-gradient(135deg,#0A1F14 0%,#2D6A4F 100%);padding:50px 24px 40px;text-align:center;border-bottom:3px solid var(--c-gold)}}
.hero .tag{{color:var(--c-gold-soft);font-size:13px;font-weight:900;letter-spacing:5px;margin-bottom:12px}}
.hero h1{{font-size:clamp(22px,4vw,40px);font-weight:900;line-height:1.25;margin-bottom:8px;color:#fff;text-shadow:0 4px 24px rgba(0,0,0,0.4)}}
.hero .subtitle{{font-size:clamp(13px,1.6vw,17px);color:var(--c-sage);font-weight:600;letter-spacing:0.3px;margin-bottom:14px}}
.hero .meta{{display:inline-flex;gap:10px;flex-wrap:wrap;justify-content:center;margin-top:10px}}
.hero .badge{{background:rgba(201,169,97,0.18);color:var(--c-gold-soft);padding:5px 14px;border-radius:20px;font-size:12px;font-weight:900;letter-spacing:1px;border:1px solid rgba(201,169,97,0.45)}}
.hero .badge.type-a{{background:rgba(139,38,53,0.25);color:#e8b4bd;border-color:rgba(139,38,53,0.55)}}
.hero .badge.type-b{{background:rgba(159,199,175,0.2);color:var(--c-sage);border-color:rgba(159,199,175,0.5)}}
.hero .badge.type-c{{background:rgba(255,255,255,0.14);color:#fff;border-color:rgba(255,255,255,0.35)}}
.back{{position:absolute;top:20px;left:20px;color:#fff;text-decoration:none;font-size:13px;font-weight:700;padding:7px 14px;border:2px solid rgba(255,255,255,0.55);border-radius:18px}}
.back:hover{{background:#fff;color:var(--c-forest)}}
.content{{max-width:900px;margin:0 auto;padding:40px 24px 60px}}
.content h1{{display:none}}
.content h2{{font-size:clamp(20px,2.8vw,28px);font-weight:900;color:var(--c-forest);margin:32px 0 16px;letter-spacing:0.5px;border-left:5px solid var(--c-gold);padding-left:14px}}
.content h2:first-child{{margin-top:0}}
.content h3{{font-size:18px;font-weight:900;color:var(--c-text);margin:24px 0 12px}}
.content h4{{font-size:16px;font-weight:700;color:var(--c-gold-deep);margin:18px 0 10px}}
.content p{{font-size:15px;color:var(--c-body);margin-bottom:14px}}
.content ul,.content ol{{margin:0 0 16px 24px;color:var(--c-body)}}
.content li{{font-size:15px;margin-bottom:6px;line-height:1.7}}
.content strong{{color:var(--c-text);font-weight:900}}
.content em{{color:var(--c-gold-deep);font-style:normal;font-weight:600}}
.content code{{background:rgba(201,169,97,0.16);color:var(--c-gold-deep);padding:2px 6px;border-radius:4px;font-size:13px;font-family:'JetBrains Mono','D2Coding','Consolas',monospace}}
.content pre{{background:#F4F2EA;border:1px solid var(--c-border);border-radius:8px;padding:16px;overflow-x:auto;margin:16px 0}}
.content pre code{{background:none;color:var(--c-body);padding:0;font-size:13px}}
.content blockquote{{border-left:4px solid var(--c-gold);background:#F4F2EA;padding:14px 20px;margin:16px 0;border-radius:0 8px 8px 0;color:var(--c-body)}}
.content table{{width:100%;border-collapse:collapse;margin:18px 0;background:var(--c-surface);border:1px solid var(--c-border);border-radius:8px;overflow:hidden;font-size:14px}}
.content th,.content td{{padding:10px 12px;text-align:left;border-bottom:1px solid var(--c-border)}}
.content th{{background:var(--c-forest);color:#fff;font-weight:900}}
.content td{{color:var(--c-body)}}
.content tr:last-child td{{border-bottom:none}}
.content hr{{border:none;border-top:1px solid var(--c-border);margin:30px 0}}
.content a{{color:var(--c-gold-deep);text-decoration:none;border-bottom:1px dashed rgba(168,138,74,0.5)}}
.content a:hover{{border-bottom-style:solid}}
.footer{{background:var(--c-dark);border-top:3px solid var(--c-gold);padding:24px;text-align:center;color:var(--c-sage);font-size:13px}}
.footer a{{color:var(--c-gold-soft);text-decoration:none;margin:0 10px}}
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
  <div style="margin-top:10px;color:rgba(159,199,175,0.65);font-size:12px;letter-spacing:0.3px">© 2026 SUN WOONGKYU · SUNNY AI MAGIC 50 · CC BY-NC-ND 4.0 · 특허 별도 보유</div>
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
