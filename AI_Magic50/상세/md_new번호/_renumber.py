# -*- coding: utf-8 -*-
"""
MD frontmatter id 및 본문 #번호 상호참조를 새 번호로 갱신
- 옛 번호 → 새 번호 매핑
- 모든 #XX, #X 패턴(1~50)을 새 번호로 변환
- frontmatter id 갱신
"""
import os
import re
from pathlib import Path

# 옛 번호 → 새 번호 매핑
OLD_TO_NEW = {
    1: 5, 2: 1, 3: 7, 4: 48, 5: 31, 6: 28, 7: 27, 8: 46, 9: 14, 10: 12,
    11: 26, 12: 8, 13: 2, 14: 3, 15: 22, 16: 39, 17: 15, 18: 21, 19: 42, 20: 44,
    21: 30, 22: 24, 23: 33, 24: 25, 25: 6, 26: 9, 27: 16, 28: 38, 29: 49, 30: 17,
    31: 45, 32: 47, 33: 32, 34: 4, 35: 13, 36: 40, 37: 41, 38: 11, 39: 18, 40: 20,
    41: 37, 42: 10, 43: 35, 44: 34, 45: 19, 46: 29, 47: 23, 48: 36, 49: 43, 50: 50,
}

# 새 번호 → 새 파일명 매핑 (frontmatter id 갱신용)
NEW_FILE_TO_NUM = {}

BASE = Path(r"G:\내 드라이브\333_자료공유폴더\Sunny_Magic_Show\AI_Magic50\상세\md_new번호")

# 파일명에서 새 번호 추출
for f in sorted(BASE.glob("*.md")):
    name = f.name
    if name.startswith("_"):
        continue
    m = re.match(r"^(\d{2})_", name)
    if m:
        NEW_FILE_TO_NUM[name] = int(m.group(1))

def renumber_refs(text: str) -> str:
    """본문에서 #XX, #X 형태 상호참조(옛 번호)를 새 번호로 변환.
    파일명 안의 숫자는 건드리지 않음 (예: `02_명세서.md` 등)."""

    def repl_two_digit(m):
        # #01 ~ #50 (두 자리)
        n = int(m.group(1))
        if 1 <= n <= 50:
            new_n = OLD_TO_NEW.get(n)
            if new_n:
                return f"#{new_n:02d}"
        return m.group(0)

    def repl_one_digit(m):
        # #1 ~ #50 (한 자리 또는 두 자리, 패딩 없음)
        # 단, 뒤에 숫자가 더 오면 매치 안 함 (e.g., #123)
        n = int(m.group(1))
        if 1 <= n <= 50:
            new_n = OLD_TO_NEW.get(n)
            if new_n:
                return f"#{new_n}"
        return m.group(0)

    # #01~#99 두 자리 패딩 형식만 우선 변환
    text = re.sub(r'#(\d{2})(?!\d)', repl_two_digit, text)
    # #1~#50 패딩 없는 형식 (#앞이 공백/구두점일 때만, 색상 hex 회피)
    text = re.sub(r'(?<![0-9a-fA-F])#(\d{1,2})(?![0-9a-fA-F])', repl_one_digit, text)

    return text

def update_frontmatter_id(text: str, new_num: int) -> str:
    """frontmatter의 id: 값을 새 번호로 갱신."""
    pattern = re.compile(r'^(id:\s*)(\d+)', re.MULTILINE)
    return pattern.sub(lambda m: f"{m.group(1)}{new_num}", text, count=1)

def process_file(path: Path):
    new_num = NEW_FILE_TO_NUM.get(path.name)
    if not new_num:
        return None

    text = path.read_text(encoding='utf-8')

    # frontmatter 분리
    if text.startswith('---'):
        parts = text.split('---', 2)
        if len(parts) >= 3:
            fm = parts[1]
            body = parts[2]
            # frontmatter id 갱신
            fm_new = update_frontmatter_id(fm, new_num)
            # 본문 #번호 상호참조 갱신
            body_new = renumber_refs(body)
            text_new = '---' + fm_new + '---' + body_new
        else:
            text_new = renumber_refs(text)
    else:
        text_new = renumber_refs(text)

    if text_new != text:
        path.write_text(text_new, encoding='utf-8')
        return True
    return False

if __name__ == "__main__":
    changed = []
    unchanged = []
    for f in sorted(BASE.glob("*.md")):
        if f.name.startswith("_"):
            continue
        result = process_file(f)
        if result is True:
            changed.append(f.name)
        elif result is False:
            unchanged.append(f.name)

    print(f"갱신됨: {len(changed)}개")
    print(f"변경 없음: {len(unchanged)}개")
    for n in changed:
        print(f"  CHG  {n}")
    for n in unchanged:
        print(f"  ---  {n}")
