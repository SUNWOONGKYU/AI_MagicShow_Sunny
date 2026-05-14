---
id: 16
title: "일반 Subagent와 Agent Teams 차이를 이해하고 작업시키기"
subtitle: "메인에게만 보고하고 끝나는 하위 작업자 vs 팀메이트끼리 직접 통신하는 조직 단위 협업"
type: B
group_id: 3
group_name: "실행 방법"
order_in_group: 3
created: 2026-05-06
sources:
  - "~/.claude/settings.json (CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1)"
  - "~/.claude/skills/백호-platoon-formation/SKILL.md (44명 편제 표준)"
  - "~/.claude/skills/deploy-subagent-기본/SKILL.md (분대장 주도 + 서브에이전트 보조)"
  - "Claude Code 공식 문서 — code.claude.com/docs/en/agent-teams"
  - "AI_Magic50/Sunny_AI_Magic_48개_종합정리.md (#27)"
  - "Claude-Wiki/ax-practical-project/wiki/2026_05_03_21.05_import_2026_04_01__PHASE_Bravo_S5S6_instruction_rework.md (Bravo 2분대장 30 Task instruction+verification 1일 재작성 — Agent Teams 분대 단위 위임 정상 사례)"
---

# 16. 일반 Subagent와 Agent Teams 차이를 이해하고 작업시키기

## 한 줄 정의

**Subagent** 는 단일 세션 내 메인이 호출한 *하위 작업자* — 메인에게만 보고하고 끝. **Agent Teams** 는 본인 `settings.json` 의 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 환경변수로 활성화되는 공식 기능 — 팀리더 + 팀메이트들이 **각자 독립 컨텍스트 윈도우** 를 갖고 **팀메이트끼리 직접 통신** 하는 *조직 단위 협업 구조*. 양쪽 경계를 모르면 30개 동시 운용에서 컨텍스트가 무너진다.

## 왜 이 노하우가 중요한가

본인이 30개 동시 Claude Code 인스턴스를 굴리기 시작한 초기, 가장 많이 만난 사고가 *"분명히 작업 시켰는데 메인이 받은 보고가 단편적"* 이었다. 이유는 단순했다 — **Subagent 와 Agent Teams 를 같은 것으로 착각** 하고 있었기 때문이다. Subagent 는 메인 컨텍스트의 *연장선* 이라 자기 결과를 메인에게 1회 텍스트로 보고하고 사라진다. Agent Teams 의 팀메이트는 *독립 인스턴스* 라 자기 컨텍스트를 따로 유지하면서 옆 팀메이트와 직접 통신한다. 둘은 도구가 다른 게 아니라 **조직 모델 자체가 다르다**.

이 차이가 결정적인 이유는 **장기 작업의 정보 손실** 이다. SAL Grid Stage 5단계짜리 프로젝트에서 분대장 3명이 각자 Stage 1~5 를 굴린다고 치자. Subagent 모델로 하면 분대장 3명이 각자 메인에게만 보고 → 메인 컨텍스트가 3배속으로 차서 Stage 3 즈음 / compact 발동 → 정보 유실. Agent Teams 모델로 하면 분대장(팀메이트)끼리 직접 통신해서 Stage 간 인계가 메인을 거치지 않는다 → 메인 컨텍스트는 지휘만 담당, 끝까지 깨끗.

본인 글로벌 `~/.claude/settings.json` 첫 줄 인용 (실제 본인 설정 파일):

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

이 한 줄로 백호 스킬(`백호-platoon-formation`) 의 44명 편제 — 소대장 1명 + 분대장 N명(Alpha/Bravo/Charlie/Delta/Echo) + 분대원들 + 외부 용병 4명 + 21 Skills — 가 실제로 작동한다. 이 변수 없이 백호 스킬을 호출하면 *분대장끼리 통신* 부분이 모두 메인 경유 텍스트 보고로 격하된다 — 실질적으로 Subagent 모드로 다운그레이드.

또 하나 — `deploy-subagent-기본` 의 8대 철칙 1번 *"분대장 주도"* 와 정확히 짝. **분대장(팀메이트)은 위임만 하는 지휘관이 아니라 자기도 총 쏘면서 분대원(Subagent)을 지휘하는 실전 지휘관**. 즉 Agent Teams 의 팀메이트가 자기 안에서 Subagent 를 또 호출할 수 있다 — 2계층 조직.

## 핵심 개념

### 양자 비교표

| 차원 | Subagent | Agent Teams (팀메이트) |
|------|----------|------------------------|
| **활성화** | 기본 제공 | `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` 필수 |
| **호출 도구** | Task tool | SendMessage / 팀 매니페스트 |
| **컨텍스트 윈도우** | 메인 세션 일부 차감 | **각자 독립 윈도우** (200K씩 별개) |
| **세션 수명** | 작업 1회분 (응답 후 소멸) | **장기 (세션 종료까지 유지)** |
| **통신 방향** | 메인 → Subagent → 메인 (1왕복) | 팀리더 ↔ 팀메이트 / **팀메이트 ↔ 팀메이트 직접** |
| **상태 보존** | 없음 (호출마다 초기화) | 있음 (대화 누적) |
| **메인 컨텍스트 부담** | 결과 텍스트 흡수 (수십 KB) | 보고 요약만 흡수 (수백 byte) |
| **계층** | 1계층 (메인 → 분대원) | 2계층 가능 (팀메이트 → Subagent) |
| **모델 지정** | 호출 시 (haiku/sonnet) | 팀 정의 시 (각 팀메이트별) |
| **병렬성** | 가능 (Task 동시 호출) | 가능 + 팀메이트 간 직접 메시지 |
| **사용 시점** | 단순·반복·전문 위임 | 장기 협업·Stage 인계·다관점 토론 |

### Subagent — 분대원 모델

`deploy-subagent-기본` 표 인용:

| 역할 | 직접 수행 | 서브에이전트 투입 |
|------|----------|-----------------|
| 소대장 (Claude Code 메인) | X — 지휘/조율만 | 분대장에게 임무 부여 |
| 분대장 (Teammate) | **O — 직접 일함** | 필요시 서브에이전트/용병 소환 |
| 분대원 (Subagent) | O — 위임받은 일 | X |
| 용병 (외부 AI) | O — 전문 분야 | X |

분대원(Subagent)은 *능력 확장 수단*. 분대장 대체가 아니다. 본인 분대원 호출 시점은 **3가지** 로 좁혀져 있다:
1. **전문성 부족** — Rust 최적화·DB 튜닝 등 자기가 못 하는 분야
2. **병렬 처리** — 코딩하면서 동시에 테스트
3. **대량 반복** — 100개 파일 포맷 변환

이 3가지 외에는 분대장이 직접 한다.

### Agent Teams — 팀 편제 모델

백호 스킬의 44명 편제 골격 인용:

```
소대장(team-lead, opus) — 지휘·조율, 직접 코딩 최소화
  ├─ 1분대장 Alpha (sonnet, 임무 시 역할 배정)
  ├─ 2분대장 Bravo (sonnet)
  ├─ 3분대장 Charlie (sonnet)
  ├─ 4분대장 Delta (sonnet)  ← B형 추가
  ├─ 5분대장 Echo (sonnet)   ← B형 추가
  └─ 6분대장+ Foxtrot~ (sonnet) ← C형 지정 시
+ 외부 용병 4명 (Codex / Gemini / Grok / Perplexity — #22)
+ 21 Skills (분대장이 호출 가능)
```

각 분대장은 **독립 컨텍스트 윈도우** 를 가지므로 *5개 분대 = 5×200K = 1M 토큰* 의 작업 공간이 동시 가동. 메인은 보고만 받으니 메인 컨텍스트는 거의 안 차오른다.

분대장 간 직접 통신이 Agent Teams 의 결정적 가치 — Bravo 가 Charlie 에게 직접 *"내가 만든 API 스펙 확인해 줘"* 라고 메시지를 보낼 수 있다. 메인 경유가 아니라 팀메이트 간 SendMessage. 이 경로가 없으면 모든 통신이 메인을 거쳐 컨텍스트가 폭발.

### 어떤 작업에 어느 모델

| 작업 성격 | Subagent | Agent Teams |
|-----------|----------|-------------|
| 한 함수 리팩터링 | O | 과잉 |
| 100개 파일 포맷 변환 | O | 과잉 |
| 5단계 SAL Grid 프로젝트 | 부족 | **O** |
| 다관점 페르소나 토론 (#1) | 부족 | **O** (각 페르소나가 팀메이트) |
| 단순 조사 1건 | O (haiku) | 과잉 |
| 풀스택 24시간 작업 | 부족 | **O** |
| Stage 간 인계 보장 | 약함 | **O** |
| 30개 동시 운용 분산 | 분담 가능 | **O** (체계화) |

판단 기준은 단순하다 — *"세션 끝나도 살아 있어야 하는가"* 가 YES 면 Agent Teams, NO 면 Subagent.

### 자기 검증 금지 — 양쪽 공통

Subagent 든 팀메이트든 **자기 산출물을 자기가 검증하면 안 된다**. Bravo 가 만든 UI 는 Charlie 가 Playwright 로 클릭 검증, Alpha 가 만든 API 는 Bravo 가 호출 검증. *Task Agent ≠ Verification Agent* 원칙은 Agent Teams 에서 더 엄격하게 강제된다 (백호 스킬에 박혀 있음).

## 실전 사용법

### 1단계 — 환경변수 활성화 확인

```bash
grep AGENT_TEAMS ~/.claude/settings.json
# → "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" 가 있어야 함
```

없으면 Agent Teams 호출 자체가 안 되거나 Subagent 모드로 다운그레이드. 본인 글로벌 settings.json 에 박혀 있어 모든 프로젝트에서 자동.

### 2단계 — 의사결정 — Subagent 또는 Agent Teams

| 질문 | YES → Subagent | YES → Agent Teams |
|------|----------------|-------------------|
| 응답 1회로 끝나는가? | O | — |
| 메인 컨텍스트 200K 중 절반 이하 사용 중인가? | O | — |
| 작업이 4시간 이상 지속되는가? | — | O |
| Stage 간 인계가 필요한가? | — | O |
| 팀메이트 간 직접 통신이 필요한가? | — | O |
| 30개 동시 운용 중인가? | — | O |

### 3단계 — Subagent 호출 시 필수 주입

`deploy-subagent-기본` 8대 철칙 8번 — **저장 위치 규칙** 을 프롬프트에 박지 않으면 투입 금지:

```
## 저장 위치 규칙 (필수)
1. Stage 폴더 (원본): SAL_Grid_Dev_Suite/Process/S{N}_스테이지명/{Area폴더}/
2. 루트 디렉토리 (배포용): app/, components/, lib/ 등
- Stage 폴더 저장 누락 시 Verification 에서 FAIL
```

이 블록 없으면 본인이 S1 Batch 에서 겪은 *"5개 Task 중 4개 Stage 폴더 누락"* 사고 재발.

### 4단계 — Agent Teams 호출 — 백호 스킬

본인 백호 스킬(`백호-platoon-formation`) 한 줄 호출:

```
/백호-platoon-formation A형 — Alpha/Bravo/Charlie 3분대 즉시 스폰
```

A형(3분대 기본) → B형(5분대) → C형(지휘관 지정 N분대) 단계적 확장. 분대장 스폰 후 소대장이 AskUserQuestion 으로 임무 + 분대 수 질문, 그 다음 작업 분해(TaskCreate) + 통합 배정(SendMessage) 으로 각 분대장에게 *업무 + 모델 등급 + 도구 권한* 일괄 지정.

### 5단계 — 검증 분리

| 산출물 | 검증자 |
|--------|--------|
| Alpha 산출 코드 | Bravo (다른 팀메이트) |
| Bravo 산출 UI | Charlie (Playwright 클릭 검증) |
| Charlie 산출 문서 | review-evaluate-코어1 스킬 |
| 외부 용병(Codex) 산출 | 메인 Claude Code 또는 Bravo |

자기 검증 절대 금지. 별도 Verification Agent 가 클릭/실행/측정으로 통과시켜야 *Verified*.

### 본인 운용 패턴

본인은 **3시간 미만 작업 = Subagent, 3시간 이상 = Agent Teams** 로 단순화해 운용. 5개 컴퓨터 × 6개 인스턴스 = 30 인스턴스 운용 시 각 컴퓨터가 1개 소대(소대장 1 + 분대장 N) 단위로 묶여 컴퓨터 간에는 메인 채팅으로만 인계 — 컴퓨터 안에서는 Agent Teams 의 팀메이트 간 직통 통신 활용.

장기 SAL Grid 프로젝트에서는 Stage 1~5 를 분대장 5명에게 분배하고 인계는 직통 메시지로 처리. 메인은 Stage Gate 통과 보고만 받음. 누적 운용에서 가장 큰 컨텍스트 효율 향상이 이 변경에서 나왔다 — *메인 컨텍스트가 8시간 작업 후에도 30% 미만* 유지.

미달성 사례 — 단순 작업에 Agent Teams 를 무리하게 적용하면 팀 스폰 오버헤드(약 30~60초)가 작업 시간보다 큰 역전 현상 발생. *오버킬 금지* 원칙. 본인 운용 첫 1개월에 이 실수를 가장 많이 했다.

> Vault 사례: `ax-practical-project/wiki/2026_05_03_21.05_import_2026_04_01__PHASE_Bravo_S5S6_instruction_rework.md` 는 *Bravo (2분대장)* 가 S5DS·S5SC·S5MD·S6 등 30개 Task의 instruction + verification 한 쌍을 1일 안에 전면 재작성한 노트다. Phase 1~30이 모두 `[x]` 로 닫혀 있고, 분대장 한 명이 자기 관할 영역 30개를 완결한 *Agent Teams 운용의 정상 사례* — 메인 컨텍스트는 *"Bravo, S5/S6 30개 재작성 시작 → 완료 보고만 받음"* 으로 끝난다. 27번 본 항목의 *"Stage 1~5를 분대장 5명에게 분배하면 메인 컨텍스트가 8시간 작업 후에도 30% 미만"* 명제의 실측 증거.

## 관련 항목

- **#31 5컴퓨터 30개 운용** — Agent Teams 가 30개 분산의 골격
- **#14 군대 소대 편제** — 백호 스킬과 직접 짝
- **#1 전문가 페르소나 토론** — 페르소나 = 팀메이트
- **#22 오케스트레이터 + 멀티 CLI** — 17번이 외부 용병, 27번이 내부 팀
- **#32 CLAUDE.md 활용** — 환경변수·스킬 규칙을 글로벌 CLAUDE.md 에 박기
- **#14 1개 AI Multi Role** — 단일 인스턴스 다역할 vs 27번 다인스턴스
- **#15 컨텍스트 관리** — Agent Teams 가 메인 컨텍스트 보호 도구
- **#49 스크린샷 자율 검증** — Verification Agent 자리에 들어가는 도구
