# -*- coding: utf-8 -*-
"""본문 h1 제목 '# NN. ...' 형태에서 옛 번호를 새 번호로 갱신."""
import re
from pathlib import Path

BASE = Path(r"G:\내 드라이브\333_자료공유폴더\Sunny_Magic_Show\AI_Magic50\상세\md_new번호")

def process(path: Path):
    name = path.name
    m = re.match(r"^(\d{2})_", name)
    if not m:
        return None
    new_num = int(m.group(1))

    text = path.read_text(encoding='utf-8')

    # frontmatter 분리
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) >= 3:
            fm = parts[1]
            body = parts[2]
        else:
            fm = ''
            body = text
    else:
        fm = ''
        body = text

    # 본문 첫 줄 h1 '# NN. ' 패턴 갱신
    # 예: '# 2. 스무고개...' → '# 1. 스무고개...'
    new_body, count = re.subn(
        r'^(\s*#\s+)(\d{1,2})(\.\s)',
        lambda m: f"{m.group(1)}{new_num}{m.group(3)}",
        body,
        count=1,
        flags=re.MULTILINE
    )

    if count == 0:
        return False

    if fm:
        new_text = '---' + fm + '---' + new_body
    else:
        new_text = new_body

    if new_text != text:
        path.write_text(new_text, encoding='utf-8')
        return True
    return False

if __name__ == "__main__":
    chg = []
    for f in sorted(BASE.glob("*.md")):
        if f.name.startswith("_"):
            continue
        r = process(f)
        if r:
            chg.append(f.name)
    print(f"갱신 {len(chg)}개")
