# Claude Code Statusline 개선 — 작업지시서

## 배경

본 작업지시서는 다음 가이드를 따라 **이미 Claude HUD 플러그인이 설치된 상태**에서 시작합니다.

**참고 가이드**: Claude HUD 플러그인 완벽 가이드
URL: https://fornewchallenge.tistory.com/entry/%F0%9F%86%93-Claude-Code-%EC%83%81%ED%83%9C-%ED%91%9C%EC%8B%9C%EC%A4%84-%EA%BE%B8%EB%AF%B8%EA%B8%B0-Claude-HUD-%ED%94%8C%EB%9F%AC%EA%B7%B8%EC%9D%B8-%EC%99%84%EB%B2%BD-%EA%B0%80%EC%9D%B4%EB%93%9C-1

가이드 그대로 다음 명령으로 설치 완료한 상태:
```
/plugin marketplace add jarrodwatts/claude-hud
/plugin install claude-hud
/claude-hud:setup
```

---

## 문제점

위 가이드대로 Claude HUD를 설치해서 운용해본 결과, 다음 문제들이 발견됨.

### 문제 1. 컨텍스트 사용량이 부정확

Claude HUD가 표시하는 컨텍스트 % 값이 실제 컨텍스트 윈도우 사용량과 일치하지 않음.

원인:
- Claude HUD는 누적 토큰을 기반으로 계산하는 경우가 있음
- 정확한 값은 `current_usage` 필드를 써야 함
- `current_usage`는 `input_tokens + cache_creation_input_tokens + cache_read_input_tokens` 합산이며, 누적이 아닌 마지막 API 호출의 실제 컨텍스트 상태 반영
- `total_input_tokens`·`total_output_tokens`는 세션 누적이라 컨텍스트 윈도우 크기를 초과 가능

### 문제 2. 사용량 한도(Rate Limit)가 정확하지 않음

5시간 한도 표시는 있지만 7일 한도 표시가 없거나, 실제 Anthropic API 한도와 어긋남.

원인:
- Claude HUD는 5시간 사용량만 표시
- Anthropic API는 5시간·7일 두 한도가 모두 있음
- `rate_limits.five_hour`와 `rate_limits.seven_day` 두 필드를 모두 활용해야 정확
- 리셋까지 남은 시간(`resets_at`) 계산이 누락된 경우 있음

### 문제 3. 도구 활동과 실행 중인 명령이 분리되지 않음

Claude HUD는 도구 활동을 다음처럼 표시:
```
✓ TaskOutput ×2 | ✓ mcp_context7 ×1 | ✓ Glob ×1
```

이건 도구 종류와 횟수만 보여줄 뿐, **현재 어떤 명령을 실행 중인지 구체 내용이 안 보임**.

필요한 분리:
- 활성화된 도구 종류 (Bash, Read, Edit 등 카테고리)
- 실행 중인 명령의 구체 내용 (Bash로 어떤 명령, Read로 어떤 파일)

### 문제 4. 서브에이전트는 표시되지만 Agent Teams 팀메이트가 표시 안 됨

Claude HUD가 표시하는 에이전트 상태:
```
✓ Explore: Explore home directory structure (5s)
✓ open-source-librarian: Research React hooks patterns (2s)
```

이건 단순 Subagent (Task 도구로 호출된 것)만 추적함.

**Claude Code의 공식 Agent Teams 기능**(`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`로 활성화, v2.1.32 이상)으로 소환된 **팀메이트들의 상태가 별도로 추적되지 않음**.

Subagent와 Agent Teams 팀메이트는 다른 메커니즘:
- Subagent: 단일 세션 내 하위 작업자, 메인에게만 보고
- Agent Teams 팀메이트: 독립 컨텍스트 윈도우, 팀메이트 간 직접 통신 가능
- 둘 다 별도 표시 필요

### 문제 5. Todo 진행률·세션 비용·일일 비용 등 불필요한 표시

Claude HUD는 다음을 기본 표시:
- Todo 진행률 (5/5)
- 세션 비용 / 일일 누적 비용 / Burn rate

이 항목들은 본 운용에 불필요. 비용은 별도 관리.

(반대로 **컨텍스트와 Rate Limit은 막대 그래프 시각화가 직관적이라 살림** — 항목 3·4·5 참조)

### 문제 6. 항목 표시 순서가 운용 흐름에 맞지 않음

Claude HUD는 모델·컨텍스트·경로·브랜치를 한 줄에 섞어 표시. 작업 디렉토리부터 보고 모델·컨텍스트로 흐르는 자연스러운 순서가 아님.

---

## 작업 지시

위 문제들을 해결하는 **사용자 맞춤 statusline 셸 스크립트**를 직접 작성해달라.
Claude HUD 플러그인은 제거하고, 외부 의존 없이 본인 스크립트로 대체.

### 1단계. 기존 설치 정리

다음 항목들을 정리:
- Claude HUD 플러그인 제거: `/plugin remove claude-hud`
- 마켓플레이스 정리: `/plugin marketplace remove jarrodwatts/claude-hud`
- `~/.claude/settings.json`에 남은 statusLine 설정 백업 후 제거
- `~/.claude/plugins/claude-hud/` 잔여 폴더 정리

### 2단계. 본인 statusline 스크립트 작성

다음 사양으로 셸 스크립트 작성.

#### [표시 항목 — 정확히 이 순서로]

**1. 현재 작업 디렉토리**
- 폴더명만 표시 (전체 경로 X)
- worktree 식별 가능하도록

**2. 모델명**
- Opus / Sonnet / Haiku 등 display_name

**3. 컨텍스트 사용량** (문제 1 해결)
- `current_usage` 기반 정확한 값
- 누적 토큰 (`total_input_tokens` 등) 사용 금지
- `input_tokens + cache_creation_input_tokens + cache_read_input_tokens` 합산
- `/compact` 직후 null인 경우 "--" 표시
- **막대 그래프 시각화 + % 숫자 함께 표시**
  - 예: `█████████░░░░░░░░░░░ 45%`
  - 10단계 또는 20단계 막대로 직관적 표시
  - 색상은 아래 색상 규칙에 따름

**4. 5시간 Rate Limit**
- `rate_limits.five_hour.used_percentage`
- `resets_at`으로 남은 시간 계산해서 표시 (예: 1h28m)
- **막대 그래프 시각화 + % 숫자 + 리셋 시간 함께 표시**
  - 예: `5h ███░░░░░░░ 27% ⏰ 1h28m`

**5. 7일 Rate Limit** (문제 2 해결)
- `rate_limits.seven_day.used_percentage`
- `resets_at`으로 남은 시간 계산
- **막대 그래프 시각화 + % 숫자 + 리셋 시간 함께 표시**
  - 예: `7d ████████░░ 79% ⏰ 11h28m`

**6. 활성화된 도구 종류** (문제 3 해결 — 1/2)
- 현재 Claude가 호출 중인 도구의 카테고리
- 예: Bash, Read, Edit, Write, Grep, Glob, WebFetch, WebSearch
- MCP 도구: `mcp__서버명__도구명` 형식
- Hook 발동: `Hook(PreToolUse)`, `Hook(PostToolUse)` 형식
- transcript JSONL의 가장 최근 tool_use 블록에서 추출
- **도구 종류만 표시, 인자는 다음 항목으로 분리**

**7. 실행 중인 명령의 구체 내용** (문제 3 해결 — 2/2)
- Bash: 실제 실행 중인 명령어
- Read/Edit: 대상 파일 경로
- Grep: 검색 패턴
- WebFetch: 대상 URL
- MCP: 호출 인자 요약
- 너무 길면 60자에서 자르고 ... 추가
- **항목 6과 명확히 분리해서 표시**

**8. 실행 중인 서브에이전트** (문제 4 해결 — 1/2)
- `Task` 도구로 호출된 모든 active subagent
- 형식: `에이전트이름(진행시간)`
- 여러 개면 쉼표로 구분
- transcript JSONL에서 SubagentStart는 있지만 SubagentStop이 아직 없는 것

**9. 소환된 팀메이트** (문제 4 해결 — 2/2 / Agent Teams 활성 시)
- Claude Code 공식 Agent Teams 기능: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
- Claude Code v2.1.32 이상 필요
- Agent Teams 상태 파일 위치 (Claude Code가 본인 기능이므로 위치 알 것) 참조
- 형식: `팀이름 [팀메이트1(역할/상태), 팀메이트2(역할/상태), ...]`
- 예: `code-review [security(작업중), performance(대기), simplicity(완료)]`
- 팀이 활성 아니면 이 줄 자체 생략

**10. Git 브랜치와 상태**
- 현재 브랜치명
- clean/dirty (수정된 파일 있는지)
- ahead/behind 카운트 (origin 대비)

#### [표시 안 할 항목] (문제 5 해결)

- ❌ 세션 비용 / 일일 누적 비용 / Burn rate (전부 불필요)
- ❌ Todo 진행률 (불필요)
- ❌ Plan 등급 표시 (Pro/Max — 불필요)
- ❌ 경과 시간 (Duration — 불필요)
- ❌ 설정 파일 수 (CLAUDE.md, MCP, Hooks 개수 — 불필요)

(컨텍스트 / 5시간 / 7일 한도는 막대 그래프 시각화 유지 — 항목 3·4·5 참조)

### 3단계. 기술 요구사항

- **환경**: Windows + Git Bash
- **JSON 파싱**: jq 필수 (없으면 자동 설치 안내)
- **transcript 분석**: JSONL을 tail로 읽어 도구·서브에이전트 정보 추출
- **다중 줄 statusline**: 3~4줄 배치, 가독성 우선
- **색상** (ANSI):
  - Rate limit ≥ 70% : 빨강
  - Rate limit ≥ 50% : 노랑
  - 그 외 : 초록
  - 컨텍스트 ≥ 80% : 빨강
  - 도구 종류 : 청록
  - 명령 내용 : 흰색
  - 팀메이트 상태별: 작업중=노랑, 완료=초록, 대기=회색
- **캐싱**: 무거운 연산(git status 등)은 5초 캐시
- **캐시 키**: `session_id` 사용

### 4단계. 저장 위치

- 스크립트: `~/.claude/my-statusline.sh`
- `~/.claude/settings.json`의 `statusLine` 항목 자동 업데이트
- 실행 권한: `chmod +x` 부여

### 5단계. 검증 절차

1. 모의 JSON 입력으로 단독 테스트 가능하게 작성
2. echo로 샘플 입력 흘려서 정상 출력 확인
3. 검증 통과 후 Claude Code 완전 재시작 안내
4. 재시작 후 statusline이 표시되지 않으면 진단 단계 안내
5. 항목 9(팀메이트)는 Agent Team 활성화 후 별도 검증

---

## 예외 처리

- `current_usage`가 null인 경우 (세션 첫 호출 전, /compact 직후): "--" 표시
- `rate_limits` 필드가 없는 경우 (구버전): "N/A" 표시
- transcript JSONL 접근 실패 시: 해당 항목만 빈 칸 처리, 다른 항목은 정상 표시
- jq 미설치 환경: 설치 명령 안내 후 종료
- Agent Teams 비활성: 9번 줄 자체 생략

---

## 작업 완료 후 보고 사항

스크립트 작성 완료 후 다음을 보고해줘:

1. Claude HUD 제거 결과
2. 작성된 스크립트 전체 코드
3. settings.json에 추가된 statusLine 설정
4. 모의 입력 테스트 결과
5. Agent Teams 상태 추적 방식 (어떤 파일·경로 사용했는지)
6. 재시작 후 확인 절차

---

## 참고 자료

- 공식 Statusline 문서: https://code.claude.com/docs/en/statusline
- 공식 Agent Teams 문서: https://code.claude.com/docs/en/agent-teams
- Claude HUD 원본: https://github.com/jarrodwatts/claude-hud
- 본 작업지시서가 참조한 가이드:
  https://fornewchallenge.tistory.com/entry/%F0%9F%86%93-Claude-Code-%EC%83%81%ED%83%9C-%ED%91%9C%EC%8B%9C%EC%A4%84-%EA%BE%B8%EB%AF%B8%EA%B8%B0-Claude-HUD-%ED%94%8C%EB%9F%AC%EA%B7%B8%EC%9D%B8-%EC%99%84%EB%B2%BD-%EA%B0%80%EC%9D%B4%EB%93%9C-1

---

## 향후 개선 여지

- 첫 작성에서 9번 항목(팀메이트)이 정확히 동작하지 않으면, 실제 Agent Team 운용 중 생성되는 파일들을 확인 후 2차 개선
- 표시 색상·배치는 일주일 운용 후 본인 선호에 맞춰 조정

---

*본 작업지시서는 Sunny의 AI Magic 50 시리즈 48번
"Claude Code HUD 사용하기" 항목의 구현 자료입니다.
Claude HUD 플러그인 가이드의 한계를 본인 맞춤 스크립트로 보완하는 것이 목적입니다.*
