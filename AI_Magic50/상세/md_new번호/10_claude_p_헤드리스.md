---
id: 10
title: "claude -p 헤드리스 모드 자동화"
subtitle: "대화형 UI 없이 명령줄에서 한 번에 호출"
type: C
group_id: 2
group_name: "실행 프로세스"
order_in_group: 6
created: 2026-05-06
sources:
  - "Sunny_AI_Magic_48개_종합정리.md #42"
  - "claude --help (-p 옵션)"
---

# 10. `claude -p` 헤드리스 모드 자동화

## 한 줄 정의

대화형 UI 없이 명령줄에서 한 번에 호출하는 Claude Code 헤드리스 모드 — **셸 스크립트·크론·CI 파이프라인의 진짜 자동화 인프라**.

## 왜 이 노하우가 중요한가

대화형 모드는 본인이 키보드 앞에 있어야 한다. #26 1일 1영상을 진짜로 굴리려면 새벽 3시 본인이 자고 있어도 영상이 만들어져야 한다. `claude -p`는 그것을 가능하게 한다.

한 번 호출에 한 번 응답하고 종료한다. stdin/stdout이 표준 셸 파이프라인에 그대로 꽂힌다. 즉 Claude Code가 **`grep`·`jq`·`curl`과 같은 레벨의 CLI 도구**가 된다. #31(30개 운용), #14(소대 편제), #26(1일 1영상)이 진짜 자동화로 격상되는 분기점이다.

## 핵심 개념

```bash
claude -p "프롬프트" [--model sonnet] [--allowed-tools Read,Write,Bash]
echo "프롬프트" | claude -p
claude -p --output-format json "..."   # JSON 출력
claude -p --resume <session-id> "..."  # 세션 이어가기
```

핵심 옵션:
- `-p` / `--print` : 헤드리스 호출, 응답만 stdout
- `--model` : Opus/Sonnet/Haiku 명시 (#34와 짝)
- `--allowed-tools` : 자동화에서 허용할 도구만 화이트리스트
- `--dangerously-skip-permissions` : #35와 결합해 무인 실행
- `--output-format json` : 후속 파이프라인에서 파싱하기 쉬움

대화형 vs 헤드리스:
| 항목 | 대화형 | 헤드리스 `-p` |
|------|--------|----------------|
| 사용자 입력 | 필수 | 1회 |
| 종료 조건 | 사용자 명시 | 응답 후 자동 |
| 적합 작업 | 탐색·기획 | 반복·배치·CI |
| 가시성 | TUI HUD(#36) | 로그 파일 |

## 실전 사용법

**1단계** — 새벽 자동 발행 크론 등록:
```bash
0 3 * * * cd ~/youtube-pipeline && \
  claude -p "오늘 영상 스크립트 만들어 ./out/$(date +\%F).md 저장" \
  --model sonnet --dangerously-skip-permissions \
  >> ~/logs/youtube-$(date +\%F).log 2>&1
```

**2단계** — 폴더 100개 일괄 처리는 단순 셸 루프로:
```bash
for d in ./projects/*/; do
  claude -p "이 폴더 README 한국어로 다시 써. cwd=$d" \
    --allowed-tools Read,Write
done
```

**3단계** — GitHub Actions 통합. PR 열릴 때마다 `claude -p`로 코드 리뷰 자동 실행, 결과를 PR 코멘트로 게시.

**4단계** — 본인 ax-on.net 운영 자동화에 활용. 매일 새벽 사이트 크롤링 → `claude -p`로 변경점 분석 → Slack 발송.

**주의 — UI 검증 철칙**: 헤드리스로 빌드·배포까지 자동화했다고 해서 "동작한다"고 단정하면 안 된다. **"curl 200 ≠ 동작함"**. 별도 Verification Agent가 Playwright로 클릭 테스트(#29)하지 않으면 SKILL_ATLAS 사고처럼 dead-link가 새벽에 양산된다.

## 관련 항목

- **#26 유튜브 1일 1영상** — 헤드리스 없이는 진짜 자동화 불가
- **#35 --dangerously-skip-permissions** — 무인 실행의 짝
- **#34 /model 명령** — 자동화에서도 모델 선택 의식
- **#29 스크린샷 자율 검증** — 헤드리스 결과의 UI 검증
- **#31 5컴퓨터 30개 운용** — 30개 중 절반 이상이 헤드리스로 굴러감
