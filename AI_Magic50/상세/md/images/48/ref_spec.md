# Claude Code 커스텀 스테이터스라인 사양서

> 최종 확정: 2026-05-07
> 구현 파일: `my-statusline.sh` + `transcript-analyze.py`

---

## 1. 8줄 구조 (위→아래 표시 순서)

| 줄 | 유형 | 내용 | 표시 조건 |
|---|---|---|---|
| 줄1 | **NATIVE** | `⚠ Context low (N% remaining) · /model /compact` | 컨텍스트 잔량 25% 이하 시 자동 출현 |
| 줄2 | **CUSTOM** | `📁 폴더명 │ 🤖 모델명 (등급) │ 브랜치 *dirty` | 항상 |
| 줄3 | **CUSTOM** | `ctx 막대 % │ 5h 막대 % ⏰ 남은시간 │ 7d 막대 % ⏰` | 항상 |
| 줄4 | **CUSTOM** | `도구명×횟수, ...` (누적 도구 사용 통계) | 도구 사용 후 |
| 줄5 | **CUSTOM** | `▶ 명령어 (도구명) Hook(이벤트)` (현재 실행 중) | 실행 중일 때 |
| 줄6 | **CUSTOM** | `SubAgent (분대원) [이름1, 이름2]` | 활성 SubAgent 있을 때만 |
| 줄7 | **NATIVE** | `@Alpha  @Bravo` | 팀메이트 있을 때만 |
| 줄8 | **NATIVE** | `✓ bypassPermissions` | 항상 (권한 모드 표시) |

- **CUSTOM**: `my-statusline.sh`가 출력 (스크립트로 제어 가능)
- **NATIVE**: Claude Code가 자체 생성 (스크립트 제어 불가)

---

## 2. CUSTOM 줄 상세

### 줄2 — 디렉토리·모델·Git (LINE1)

```
📁 SKILL_ATLAS  │  🤖 Sonnet 4.6 (max)  │  main *dirty
```

- `📁 폴더명` — 현재 CWD의 마지막 폴더명 (전체 경로 아님)
- `🤖 모델명 (등급)` — Claude 모델 + 구독 등급 (`credentials.json` 에서 읽음, 5분 캐시)
- `브랜치 *dirty` — git 브랜치명, 미커밋 변경 시 *dirty 표시

### 줄3 — 컨텍스트·Rate Limit 막대 (LINE2)

```
ctx ████░░░░░░ 38%  │  5h ██░░░░░░░░ 22% ⏰ 1h12m  │  7d █████░░░░░ 48% ⏰ 3d14h
```

- `ctx 막대 %` — 세션 컨텍스트 사용률 (statusline JSON `context_window.used_percentage`)
- `5h 막대 % ⏰` — 5시간 Rate Limit 소진율 + 리셋까지 남은 시간
- `7d 막대 % ⏰` — 7일 Rate Limit 소진율 + 리셋까지 남은 시간
- 막대 색상: 초록(0~49%) / 노랑(50~69%) / 빨강(70%+)

### 줄4 — 도구 사용 통계 (LINE3)

```
Bash×12, Read×8, Edit×5, Agent×2
```

- `transcript-analyze.py`가 transcript JSONL 마지막 200줄 분석
- 도구별 호출 횟수, 빈도 내림차순 정렬
- 5초 캐시 적용

### 줄5 — 현재 명령줄·Hook (LINE3B)

```
▶ Bash: npm run dev (5s)  Hook(PreToolUse)
```

- 현재 미완료 tool_use 중 가장 최근 1건 표시
- `hook-logger.js`가 `/tmp/claude-statusline/hooks_<session>.log`에 기록 → 최근 3초 이내 Hook 이벤트 표시
- 대기 중이면 이 줄 자체가 숨겨짐

### 줄6 — SubAgent 현황 (LINE4)

```
SubAgent (분대원) [statusline 라이브 테스트, grade-report 진단]
```

- `~/.claude/projects/<proj>/<session>/subagents/agent-*.meta.json` 파일 직접 스캔
- mtime 기준 **600초(10분) 이내** 파일만 활성으로 판정
- 이름은 `meta.json`의 `description` 또는 `agentType` 필드 (최대 20자)
- 활성 SubAgent 없으면 줄 자체 출력 안 함 (개행도 없음)

---

## 3. 계급 체계

| 계급 | 호칭 | 역할 | spawn 방법 |
|---|---|---|---|
| 소대장 | (메인 세션) | 전체 지휘 | — |
| 분대장 | Teammate (NATO 단일 이름: Alpha/Bravo/Charlie…) | 병렬 세션 | Agent 도구 + `team_name` |
| 분대원 | SubAgent (직무명) | 단위 작업 | Task/Agent 도구 |

**표기 규칙:**
- `SubAgent (분대원)` — 변형 금지 (`Subagent`, `Sub-Agent`, `서브에이전트` 등)
- `Teammate (분대장)` — 변형 금지 (`TeamMate`, `팀메이트` 등)
- 팀메이트 이름: NATO 단일 이름만 (Alpha/Bravo/Charlie, 복합명 `scout-alpha` 등 금지)

---

## 4. 의존 파일

| 파일 | 위치 | 역할 |
|---|---|---|
| `my-statusline.sh` | `~/.claude/` | HUD 본체, bash 스크립트 |
| `transcript-analyze.py` | `~/.claude/` | 도구 통계·SubAgent 분석 Python 헬퍼 |
| `hook-logger.js` | `~/.claude/hooks/` | Hook 이벤트 로깅 (줄5 표시용) |
| `~/.claude/settings.json` | `~/.claude/` | `statusLine.command` 등록 |

> `hook-logger.js`는 Hook 이벤트 로깅용으로, 없어도 줄2~4·6은 정상 동작. 줄5 Hook 표시만 비활성화됨.

---

## 5. 설정 등록

`~/.claude/settings.json`:
```json
{
  "statusLine": {
    "type": "command",
    "command": "bash /c/Users/【사용자명】/.claude/my-statusline.sh"
  }
}
```

---

## 6. 캐시

| 항목 | 캐시 위치 | TTL |
|---|---|---|
| transcript 분석 결과 | `/tmp/claude-statusline/transcript_<sess>.cache` | 5초 |
| git 정보 | `/tmp/claude-statusline/git_<sess>.cache` | 5초 |
| 계정 등급 | `/tmp/claude-statusline/account_tier.cache` | 300초 (5분) |
