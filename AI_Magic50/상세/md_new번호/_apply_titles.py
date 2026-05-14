# -*- coding: utf-8 -*-
"""
50개 md 파일의 frontmatter title/subtitle 일괄 정정 + 본문 # 헤더 갱신.
- title = ITEMS.short (짧은 메인 제목)
- subtitle = 짧은 부제 (없으면 생략)
- 본문 첫 `# N. ...` → `# N. {title}`
"""
import re
from pathlib import Path

SRC = Path(r"G:\내 드라이브\333_자료공유폴더\Sunny_Magic_Show\AI_Magic50\상세\md_new번호")

# (id, title, subtitle)  subtitle="" → 부제 없음
TITLES = [
    (1,  "스무고개 브레인스토밍",             "문답으로 막연한 주제를 좁히는 사고 패턴"),
    (2,  "전문가 페르소나 토론",               "3개 분야 전문가 + Devil's Advocate"),
    (3,  "SAL 3차원 좌표",                    "Stage·Area·Level — 대규모 작업의 다축 분해"),
    (4,  "학습·검토·계획 먼저",                "바로 실행하지 말고 미리 충분히"),
    (5,  "Dual Mode 실행",                    ""),
    (6,  "5단계 순차 작업",                    ""),
    (7,  "아젠다별 설명·승인",                 "하나씩 설명듣고 승인하기"),
    (8,  "3대안 + 권고안",                    "3개 이상 대안 제시 + 권고안 표시"),
    (9,  "1개 AI에 Multi Role",               ""),
    (10, "claude -p 헤드리스 자동화",          ""),
    (11, "Hooks 활용",                        ""),
    (12, "MBO 방식으로 작업시키기",            "Management By Objective — 목표에 의한 관리"),
    (13, "SAL Grid 개발방법론",                "끊김없이 대규모 개발업무 진행"),
    (14, "군대 소대 편제 방식",                "대규모 AI 투입의 조직 모델"),
    (15, "멀티 CLI 오케스트레이터",            "Claude Code + Gemini·Codex·Grok CLI 협업"),
    (16, "Subagent vs Agent Teams",          "차이를 이해하고 작업시키기"),
    (17, "Auto Compact 끄고 수동 Compact",     "작업내용을 지정 폴더에 자동 저장"),
    (18, "Slash Commands 활용",               ""),
    (19, "/resume 세션 재개",                  "과거 세션 이어가기"),
    (20, "MCP 서버 활용",                     ""),
    (21, "네이버·구글 검색 활용",              "대량 검색 시 토큰비 절감"),
    (22, "SVG 아키텍처 스킬화",                "반복 프로세스를 관계도·흐름도로 정리하고 스킬화"),
    (23, "멀티 모델 이미지 제작",              "이미지 종류별 제작 프로세스"),
    (24, "나만의 지능형 챗봇 키우기",          "아바타형·도우미형 구분"),
    (25, "미니 풀스택 5시간 연습",             "5시간 이내 풀스택 웹사이트 만들기"),
    (26, "유튜브 1일 1영상",                  "영상 한방에 제작해 매일 올리기"),
    (27, "특허출원서 작성",                    "사업 아이디어 떠오르면 즉시"),
    (28, "4종 품질관리 스킬",                  "수시로 실행하여 완성도 높이기"),
    (29, "스크린샷 자율 검증",                 "스스로 찍고 문제점 찾아 수정"),
    (30, "AI 오류 인정과 창발",                "다단계 검증 + 창발 포착"),
    (31, "5컴퓨터 30개 동시 운용",             "크롬 원격으로 모바일에서도 작업"),
    (32, "Claude 앱 vs Code",                 "브레인스토밍은 앱, 실행은 Code"),
    (33, "CLAUDE.md 활용",                    ""),
    (34, "/model 명령",                       "작업에 맞는 모델 선택"),
    (35, "--dangerously-skip-permissions",    "Hooks 가드레일과 결합해 안전하게"),
    (36, "Statusline HUD",                    "Claude Code 상태표시줄 설치"),
    (37, "Git Worktree 병렬 브랜치",           ""),
    (38, "필요한 Skill·Agent 찾기",            "쉽게 발굴해서 활용"),
    (39, "HTML + Vercel 신속 배포",            "공유 내용을 즉시 배포"),
    (40, "C드라이브 개발 / G드라이브 백업",     "개발은 로컬, 백업은 클라우드 동기화"),
    (41, "피크타임 회피",                      "저녁 11시~새벽 3시 사용 피하기"),
    (42, "포크레인·트랙터 운전",               "삽질/낫질 개선 말고 도구를 바꿔라"),
    (43, "學보다 習",                          "AI는 공부보다 익힘의 대상"),
    (44, "문서화는 나중에",                    "일단 만들어보고 테스트"),
    (45, "DID Loop",                          "Data → Information → Decision 순환"),
    (46, "NeMoTron 100만 한국인",              "엔비디아 한국인 합성 데이터셋"),
    (47, "API 비용 최적화",                    "대규모 API 사용 전 미리 설계"),
    (48, "WiKi_LLM + Obsidian 지식베이스",     ""),
    (49, "hwp 문서 작성",                      ""),
    (50, "사내 AI 에이전트 하우스",            "AX를 위한 기능적 구축 방법"),
]

def apply_title(num, new_title, new_subtitle):
    # 파일 찾기
    files = list(SRC.glob(f"{num:02d}_*.md"))
    if not files:
        print(f"  [SKIP] {num:02d}: 파일 없음")
        return
    md_path = files[0]
    text = md_path.read_text(encoding='utf-8')

    # frontmatter 파싱
    if not text.startswith('---'):
        print(f"  [SKIP] {md_path.name}: frontmatter 없음")
        return
    parts = text.split('---', 2)
    fm = parts[1]
    body = parts[2]

    # title 갱신
    fm = re.sub(r'^title:\s*".*?"', f'title: "{new_title}"', fm, count=1, flags=re.MULTILINE)

    # subtitle 처리 — 기존 subtitle 라인 제거 후 신규 추가 (있으면)
    fm = re.sub(r'^subtitle:\s*".*?"\n', '', fm, flags=re.MULTILINE)
    if new_subtitle:
        # title 라인 뒤에 subtitle 라인 삽입
        fm = re.sub(
            r'^(title:\s*".*?")$',
            r'\1\nsubtitle: "' + new_subtitle + '"',
            fm, count=1, flags=re.MULTILINE
        )

    # 본문 첫 `# N. ...` 헤더 갱신
    body = re.sub(
        r'^#\s+\d+\.\s+[^\n]+',
        f'# {num}. {new_title}',
        body, count=1, flags=re.MULTILINE
    )

    new_text = '---' + fm + '---' + body
    md_path.write_text(new_text, encoding='utf-8')
    sub_tag = f" / sub: {new_subtitle}" if new_subtitle else ""
    print(f"  [OK] {md_path.name} → title: {new_title}{sub_tag}")

if __name__ == "__main__":
    for num, title, subtitle in TITLES:
        apply_title(num, title, subtitle)
    print(f"\n총 {len(TITLES)}개 처리 완료")
