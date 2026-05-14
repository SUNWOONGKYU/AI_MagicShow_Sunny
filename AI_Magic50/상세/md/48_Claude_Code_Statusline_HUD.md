---
id: 48
title: "Claude Code Statusline HUD 설치해서 사용하기"
type: C
group_id: 5
group_name: "환경"
order_in_group: 6
created: 2026-05-06
sources:
  - "AI_Magic50/작업지시서_Claude_Code_HUD.md"
  - "~/.claude/my-statusline.sh"
  - "~/.claude/transcript-analyze.py"
  - "~/.claude/hooks/hook-logger.js"
---

# 48. Claude Code Statusline HUD 설치해서 사용하기

## 한 줄 정의

Claude Code 터미널 하단 Status Line을 셸 스크립트로 직접 구성해 컨텍스트·Rate Limit·도구·분대원·분대장을 실시간 표시하는 **30개 동시 운용 가시성 HUD**.

## 왜 이 노하우가 중요한가

Claude Code를 30개 동시 운용할 때 가장 먼저 필요한 것은 **상태 파악 비용 0**이다. 외부 플러그인(Claude HUD, ccusage)을 일주일 굴려본 결과 세 가지 한계가 드러났다.

첫째, **컨텍스트 % 부정확** — 누적 토큰 기반이라 200%·300% 같은 숫자가 찍힌다. 둘째, **7일 Rate Limit 누락** — Anthropic은 5시간·7일 두 한도가 있는데 5시간만 보여주는 도구가 많다. 셋째, **도구와 명령이 한 줄에 섞여** 지금 Bash로 무슨 명령이 도는지 즉시 못 본다.

직접 셸 스크립트로 statusline을 짜면 이 셋이 모두 해결되고, **외부 플러그인 의존 0**의 가시성 인프라가 완성된다.

## 핵심 개념

Claude Code는 statusline을 그릴 때마다 셸 스크립트에 JSON을 stdin으로 흘려준다. 스크립트가 jq로 파싱해 출력하면 본체가 터미널에 그려준다. 즉 statusline은 **단순 셸 명령**이며, 어떤 데이터든 결합 가능하다.

JSON 핵심 필드:
- `context_window.current_usage.{input_tokens, cache_creation_input_tokens, cache_read_input_tokens}` — **마지막 API 호출의 컨텍스트 상태** (누적 아님)
- `context_window.used_percentage` — 2.1.x부터 직접 % 제공
- `rate_limits.{five_hour, seven_day}.{used_percentage, resets_at}` — 두 한도 모두, `resets_at`은 epoch 정수
- `transcript_path` — 도구 호출 이력·진행 중 서브에이전트 추출 소스

외부 데이터 결합: `~/.claude/teams/<팀>/inboxes/*.json`(분대장 inbox), `/tmp/claude-statusline/hooks_<sess>.log`(Hook 발동 이력).

## 실전 사용법

**1단계** — Claude HUD 플러그인 제거(`/plugin remove claude-hud`).

**2단계** — `~/.claude/my-statusline.sh` 작성. jq로 JSON 파싱, `current_usage` 합산으로 컨텍스트 % 계산, `resets_at` epoch → `1h28m` 변환, transcript JSONL 마지막 200줄을 Python(`transcript-analyze.py`)으로 분석해 도구 카운트·진행 중 Task·active command 추출. 색상 임계값: 컨텍스트 ≥80% / Rate ≥70% 빨강.

**3단계** — 5~6줄 분할 배치: LINE0 경고(Context low / 200k 초과 / Rate 임박) → LINE1 폴더·모델·git → LINE2 컨텍스트·5h·7d 막대그래프 → LINE3 도구 카운트 → LINE3B 실행 중 명령(`▶ Bash: git status (12s)`)+Hook → LINE4 분대원(SubAgent) → LINE5 분대장(Teammate).

**4단계** — `settings.json` 등록:
```json
"statusLine": { "type": "command", "command": "bash /c/Users/home/.claude/my-statusline.sh" }
```

**5단계** — 5초 TTL 캐싱(`/tmp/claude-statusline/`)으로 갱신 부하 최소화. Hook Logger(`~/.claude/hooks/hook-logger.js`)로 Hook 발동을 별도 로그에 기록해 LINE3B 표시.

**본인 운용 패턴**: 30개 인스턴스를 한 화면에 띄울 때 LINE2 막대그래프만 보면 어느 인스턴스를 우선 처리할지 즉시 판단된다. 분대원·분대장 호칭은 #9 군대 편제와 동일 어휘.

## 관련 항목

- **#9 군대 소대 편제** — 분대원/분대장 호칭 공유
- **#27 Subagent vs Agent Teams** — LINE4·LINE5가 두 메커니즘 별도 추적
- **#38 Hooks** — hook-logger.js가 LINE3B의 데이터 소스
- **#5 5컴퓨터 30개 운용** — 본 HUD가 그 가시성 인프라
