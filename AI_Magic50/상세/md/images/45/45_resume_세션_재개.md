---
id: 45
title: "/resume으로 과거 세션 재개하기"
type: C
group_id: 3
group_name: "실행 방법"
order_in_group: 5
created: 2026-05-06
sources:
  - "Sunny_AI_Magic_48개_종합정리.md #45"
  - "claude --resume / /resume"
  - "Claude-Wiki/skill-atlas/wiki/2026_05_06__15.10_세션내용_익스포트.md (외 5건 — PreCompact hook으로 transcript_path 자동 백업: /resume의 비상용 안전망)"
---

# 45. `/resume`으로 과거 세션 재개하기

## 한 줄 정의

종료된 Claude Code 세션의 컨텍스트를 다시 불러와 이어가는 명령 — **비상·짧은 이어가기 전용 카드**, 평상시 컨텍스트 운용은 #30이 본진.

## 왜 이 노하우가 중요한가

세션이 갑자기 죽거나(네트워크 끊김·노트북 셧다운), 작업 중 점심 먹으러 잠깐 자리를 비우거나, 어제 진행하던 짧은 디버깅을 오늘 5분만 더 이어 끝내고 싶을 때 — `/resume`은 그 1~2회용 비상 카드다.

본인이 강조하는 핵심은 **"평상시에 의존하지 마라"**. 세션이 길어질수록 컨텍스트가 80%·90%로 차고, 그 상태로 resume하면 첫 응답부터 Auto Compact가 발동하거나 응답 품질이 무너진다. 평상시 본인은 #30(수동 Compact + 인계 노트 + 폴더 저장)으로 컨텍스트를 갈아치우며 운용하지, `/resume`을 일상 도구로 쓰지 않는다.

## 핵심 개념

```bash
/resume                          # 대화 중 세션 목록에서 선택
claude --resume <session-id>     # CLI에서 직접 지정
claude --resume <session-id> -p "이어서 …"   # 헤드리스 결합
```

내부적으로 세션 transcript JSONL을 다시 로드해 LLM에 재주입한다. 따라서:
- transcript가 길수록 첫 응답 latency·비용 상승
- 컨텍스트 % 가 죽기 직전 그대로 복원됨 (예: 75%로 죽었으면 76%부터 시작)
- 도구 호출 이력·하위 에이전트 상태도 함께 복원

#30 vs #45:
| 항목 | #30 컨텍스트 관리 3종 | #45 /resume |
|------|---------------------|-------------|
| 적합 시점 | 평상시 | 비상 |
| 컨텍스트 상태 | 의도적 정리 후 인계 | 죽은 시점 그대로 |
| 작업 길이 | 장기 | 짧은 이어가기 |
| 정보 손실 위험 | 낮음 | 중간 |
| 비용 | 분산 | 첫 응답 무거움 |

## 실전 사용법

**1단계** — 세션 죽은 직후라면 즉시 `/resume`. 본인 운용에서는 죽은 후 5분 이내 + 진행 중이던 단일 작업이 있을 때만 카드 발동.

**2단계** — 세션 목록 확인:
```bash
claude --resume   # 인터랙티브 목록
ls ~/.claude/projects/*/*.jsonl   # 작업 디렉토리별 세션 transcript 직접 확인
```
한 폴더에 누적된 세션 transcript JSONL 중 가장 최근 것을 고른다(파일명에 session-id 포함).

**3단계** — resume 직후 첫 명령은 **현재 컨텍스트 % 확인**. #48 HUD가 떠 있으면 LINE2 막대그래프로 즉시 본다. 80% 넘으면 그 자리에서 #30의 수동 Compact 또는 인계 노트로 전환.

**4단계** — 평상시 작업이 길어진다 싶으면 `/resume`을 기대지 말고 미리 인계 노트 작성:
```
~/work-notes/2026-05-06_<주제>_handoff.md
```
다음 세션은 이 노트만 읽고 새 컨텍스트로 시작. 이게 #30이 권하는 본진이다.

**5단계** — 헤드리스(#42) 자동화에서는 `--resume`을 거의 쓰지 않는다. 자동화는 매 호출이 독립이어야 디버깅이 쉽다.

> Vault 사례: `skill-atlas/wiki/2026_05_06__15.10_세션내용_익스포트.md` 외 5건의 *세션내용_익스포트* 노트는 본인이 PreCompact hook으로 자동 백업한 transcript 메타다 — `session_id`·`transcript_path`·`cwd: C:\Dev\SKILL_ATLAS`·`hook_event_name: PreCompact` 필드가 그대로 박혀 있다. /resume 도 이 transcript_path 파일을 읽어 들이는 구조라서, 본 항목 본문 *"resume은 비상용·평상시 본진은 #30"* 의 *비상용 안전망* 실체가 그 자동 export 노트군이다 — 의식적 인계 노트가 없어도 transcript 자체는 Vault에 보존되므로 resume이라는 마지막 카드가 작동한다.

## 관련 항목

- **#30 컨텍스트 관리 3종** — 평상시 본진. /resume의 반대 기둥
- **#48 Statusline HUD** — resume 직후 컨텍스트 % 즉시 확인
- **#42 헤드리스 모드 자동화** — 자동화에선 거의 미사용
- **#37 피크타임 회피** — 피크타임 응답 끊김 후 resume 카드 자주 발동
