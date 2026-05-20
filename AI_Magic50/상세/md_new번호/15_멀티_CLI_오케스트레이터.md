---
id: 15
title: "Claude Code 오케스트레이터 + 멀티 CLI"
subtitle: "Codex CLI·Gemini CLI·Grok CLI와 실행형 협업 (실행·로그·검증·재실행)"
type: B
group_id: 3
group_name: "실행 방법"
order_in_group: 2
created: 2026-05-06
sources:
  - "~/.claude/skills/deploy-subagent-기본/SKILL.md (8대 철칙)"
  - "~/.claude/skills/ai-image-기본/SKILL.md (5모델 비교 워크플로우)"
  - "MagicShow강의자료 슬라이드 26번 (매직 8: 다른 AI 용병 부리기)"
  - "AI_Magic50/Sunny_AI_Magic_48개_종합정리.md (#17)"
  - "Claude-Wiki/claude-platoons-control/wiki/2026_05_03_21.07_import_CPC_ARCHITECTURE_OVERVIEW.md (CPC 통신 아키텍처: Supabase 중앙·MCP 브리지·5개 도구·16개 소대 등록)"
---

# 15. Claude Code 오케스트레이터 + 멀티 CLI

## 한 줄 정의

Claude Code 를 **지휘자(오케스트레이터)** 로 두고 Codex CLI · Gemini CLI · Grok CLI 를 각자 **특화된 실행 도구(용병)** 로 호출 — *대화형 협업*에서 *실행형 협업*(실행 → 로그 → 검증 → 재실행 루프)으로 격상시키는 멀티 모델 운용 패턴. MagicShow 강의자료 **슬라이드 26번**(매직 8 위치, 분량이 아니라 n번째 슬라이드 — [분류표 SSOT](../_PHASE/2026_05_06__19.50_분류표_확정.md#사실-키-ssot-single-source-of-truth)) *"매직 8: Claude Code로 다른 AI 용병 부리기"* 의 본체.

## 왜 이 노하우가 중요한가

단일 AI에 모든 일을 시키면 두 가지가 동시에 깨진다 — *첫째* 컨텍스트 윈도우가 빨리 차서 긴 자료 처리에 약하고, *둘째* 각 모델이 가진 강점을 활용 못 하니 결과 품질이 평균치에 머문다. 본인 4,000시간 누적에서 가장 효용이 큰 변곡점은 **2025년 말 멀티 CLI 운용 전환** 이었다. ChatGPT 앱과 Claude 앱을 번갈아 열고 복붙하던 *대화형 협업* 에서, Claude Code가 직접 다른 CLI를 호출하고 stdout 을 받아 처리하는 *실행형 협업* 으로 넘어간 순간 작업 속도가 4~5배가 됐다.

핵심 차이는 단순하다. **CLI 협업은 루프가 자동이고, API/대화 협업은 사람이 매 단계 개입한다.** Claude Code 가 Codex CLI 에 *"이 함수 리팩터링해서 결과를 ./out/refactored.ts 에 써라"* 라고 명령하면 Codex 가 실행하고, Claude Code 가 그 파일을 Read 하고 검증하고, 실패면 다시 다른 프롬프트로 재실행한다. 사람은 처음 한 번 시켰을 뿐. *실행 → 로그 → 검증 → 재실행* 의 4단계가 주도권을 사람에게 한 번도 넘기지 않고 돈다.

이게 슬라이드 26번 — *"CLI 방식(실행 기반 협업) vs API 방식(텍스트 왕복) / CLI = 실행 → 로그 → 검증 → 재실행 루프"* — 의 핵심이다. *"Claude가 오케스트레이터, 나머지 AI가 전문 도구 역할"* 한 줄에 본인 운용 철학이 압축돼 있다.

또 하나 중요한 부수 효과 — **각 CLI 가 독립 컨텍스트** 라는 점. Gemini CLI 에 200MB 짜리 PDF 를 던져도 Claude Code 메인 세션의 컨텍스트는 *"Gemini 에 던졌다"* 한 줄만 차지한다. 메인 컨텍스트는 지휘만 담당하니 끝까지 깨끗하다. 이건 #17(컨텍스트 관리 3종) 의 가장 강력한 도구이기도 하다.

## 핵심 개념

### CLI 협업 vs API 협업

| 차원 | CLI 협업 (실행형) | API/대화 협업 (텍스트형) |
|------|-------------------|--------------------------|
| **루프 주체** | Claude Code 자체 | 사람 (복붙 매개) |
| **사이클 시간** | 분 단위 | 시간 단위 |
| **재시도** | 자동 (조건부 분기 포함) | 수동 |
| **컨텍스트 격리** | 각 CLI 독립 | 단일 세션 누적 |
| **로그 보존** | stdout/stderr 파일 자동 | 채팅 히스토리만 |
| **검증** | 다음 CLI 가 파일 검증 가능 | 사람 시각 의존 |
| **확장성** | N개 CLI 병렬 호출 | 사람 처리 한계 |

API/대화 협업은 *"같은 일을 N번 다른 모델에게 물어보고 답을 비교"* 가 한계다. CLI 협업은 *"같은 파일을 N개 모델이 순차/병렬로 가공해서 단일 산출물 생성"* 까지 간다.

### 3 CLI 강점 분리표

`deploy-subagent-기본` 8대 철칙 중 5번 — *"용병 투입: 서브 에이전트로 안 되면 외부 AI(Codex, Gemini, Grok) 활용"* — 의 강점 분리.

| CLI | 핵심 강점 | 본인 활용 패턴 | 모델 |
|-----|----------|----------------|------|
| **Codex CLI** | 리팩터링·코드 생성 / 이미지 생성 (GPT Image) | TS·Python 함수 단위 리팩터링, GPT Image 1 호출 | GPT-5 / GPT Image 1 |
| **Gemini CLI** | 대용량 컨텍스트 (1M+ 토큰) / 이미지 (Nano Banana) | 200MB PDF 요약, 5,000줄 로그 분석, Gemini 3 Pro Image | Gemini 3 Pro / Image |
| **Grok CLI** | 실시간 리서치 (X 데이터) / 트렌드 분석 | 최신 모델 출시 동향, X 여론 스냅샷 | Grok-4 |

각 CLI 가 잘하는 것만 시키는 게 원칙이다. Codex 에게 리서치 시키지 않고 Grok 에게 리팩터링 시키지 않는다. 슬라이드 26번 *"각 AI 강점 활용: Codex=리팩터링/이미지 만들기, Gemini=대용량 처리/이미지 만들기, Grok=리서치"* 가 정확히 이 표.

### 오케스트레이터 의사결정 트리

```
작업 도착
  ├─ 코드 변경(리팩터링·생성·테스트)
  │   └─ Codex CLI (Claude Code 메인이 직접 못 할 때만)
  ├─ 대용량 파일 분석(>50KB 텍스트, >100MB 미디어)
  │   └─ Gemini CLI
  ├─ 최근 1주 이내 정보·X 트렌드
  │   └─ Grok CLI
  ├─ 이미지 생성 (사실적/일러스트)
  │   └─ ai-image-기본 비교 워크플로우 (5모델 동시)
  └─ 그 외 → Claude Code 본인 처리
```

### 실행 → 로그 → 검증 → 재실행 루프

```
[1] 실행      Claude Code → Bash("codex run refactor.ts > ./out/log.txt")
[2] 로그      Claude Code Read ./out/log.txt
[3] 검증      KPI 체크 (예: 빌드 통과 / 테스트 12/12 / Lighthouse 90+)
[4] 재실행    실패 시 다른 프롬프트로 다시 [1] (최대 5회 — 5times-debug-loop-코어3)
[5] 보고      성공 시 결과 + 미달성 항목 보고 (MBO 결과보고서 양식)
```

루프의 종결 조건은 *"KPI 통과 OR 5회 시도 완료"* 둘 중 하나. 무한 루프는 청룡 스킬의 sal-guard hook 이 차단한다.

### `ai-image-기본` 의 정점 사례 — 5모델 동시 비교

이미지 생성에서는 *어느 모델이 이번 작업에 맞는지* 미리 알 수 없다. 따라서 같은 프롬프트를 **5개 모델(Gemini 3 Pro / Gemini 3.1 Flash / Gemini 2.5 Flash / GPT Image 1 / DALL·E 3) 에 동시 호출 → 갤러리 자동 생성 → PO 가 1장 선택 → 고품질 재생성** 의 4단계 깔때기. 이게 멀티 CLI 운용의 표본이다 — *비교가 기본, 단일 호출은 예외*.

```bash
python "$HOME/.claude/skills/ai-image-기본/scripts/compare_models.py" \
  "프롬프트 한 줄" \
  --outdir "C:/Users/home/Desktop/{작업명}_compare"
# → 5장 PNG + Pillow 후처리(라벨/워터마크/EXIF) + 콜라주 + index.html 자동
```

## 실전 사용법

### 1단계 — 의사결정 트리 적용

작업 도착 즉시 *"내가 직접 할 일인가, 용병 호출할 일인가"* 판단. 본인 기준 ≈ 70% 는 메인 Claude Code 직접 처리, 30% 가 용병 위임. 위임 비율을 무리하게 올리면 컨텍스트 전달 비용 때문에 오히려 느려진다.

### 2단계 — 프롬프트에 저장 위치 규칙 주입 (필수)

`deploy-subagent-기본` 8대 철칙 중 8번 강제 — *"⛔ 저장 위치 규칙 필수 주입"*. 외부 CLI 도 동일. Stage 폴더(원본) + 루트 디렉토리(배포용) 양쪽 경로를 프롬프트에 박지 않으면 산출물이 엉뚱한 곳에 떨어진다. 본인이 S1 Batch 에서 5개 Task 중 4개가 Stage 폴더 누락된 사고가 정확히 이 빠짐 때문이었다.

### 3단계 — 병렬 호출 (독립 작업만)

Gemini CLI 가 PDF 요약하는 동안 Grok CLI 가 X 트렌드 검색하고 Codex CLI 가 리팩터링하는 — 3개 CLI 가 동시에 도는 패턴. 단, *서로 결과 의존성이 없을 때만*. Codex 가 만든 코드를 Gemini 가 검토해야 하는 순서 의존이 있으면 직렬 — 슬라이드 26번 *"실행 → 로그 → 검증 → 재실행"* 4단계 중 *검증* 자리에 다음 CLI 가 들어간다.

### 4단계 — 검증 KPI 양쪽 확보

검증 원칙 — *"curl 200 ≠ 동작함"*. 외부 CLI 산출물 검증도 데이터 레이어 KPI(파일 크기 / 빌드 통과 / 테스트 개수) + 사용자 여정 KPI(브라우저 클릭 / 실제 화면 확인) 둘 다 측정해야 통과. 단일 KPI 만 보고 *Verified* 처리 금지.

### 5단계 — 자기 검증 금지 원칙

각 CLI 가 자기 산출물을 자기가 검증하면 안 된다. Codex 가 만든 코드는 Gemini 또는 Claude Code 가 검증, Gemini 가 요약한 PDF 는 Claude Code 가 SSOT 와 대조. 별도 Verification Agent 를 따로 돌려야 한다.

### 본인 운용 패턴 — 30개 동시 운용에서

5개 컴퓨터 × 6개 Claude Code = 30 인스턴스 운용 시(#31), 각 인스턴스가 개별로 Codex/Gemini/Grok CLI 를 호출하면 API 키 충돌·rate limit 폭주가 발생한다. 본인은 *Gemini 29키 로테이션* (`ai-image-기본` 내장) 처럼 키 풀을 분배하고, Grok 처럼 단일 키 모델은 *리서치 전담 인스턴스 1개* 만 호출 권한 부여. #47(API 비용 최적화) 와 짝.

비용 측면 — Gemini 3 Pro 는 대용량이라 1회 호출 비용 높지만 컨텍스트 절약 효과가 그 이상. 본인 월간 API 사용 비용의 약 65% 가 Gemini 대용량 처리, 27% Codex 코드 생성, 8% Grok. *(측정: 본인 월간 각 CLI 청구서 합산 비율, 30개 운용 환경 기준)*

## 관련 항목

- **#31 5컴퓨터 30개 운용** — 멀티 CLI 가 가로 확장의 동력
- **#14 군대 소대 편제** — 멀티 CLI = 외부 용병 4명, 본인 분대장과 분리
- **#9 1개 AI Multi Role** — 단일 인스턴스 다역할 vs 15번 다인스턴스 다역할
- **#16 Subagent vs Agent Teams** — 내부 위임 메커니즘, 15번은 외부 용병
- **#17 컨텍스트 관리** — 외부 CLI 가 메인 컨텍스트 보호 도구
- **#47 API 비용 최적화** — 멀티 CLI 비용 통제 사전 설계
- **#20 MCP 서버** — 15번이 CLI 레벨, MCP 는 데이터·시스템 레벨 협업
- **#23 멀티 모델 이미지 제작** — 15번을 이미지 트랙에 적용한 정점 사례

> Vault 사례: `claude-platoons-control/wiki/CPC_ARCHITECTURE_OVERVIEW.md` 가 본인이 멀티 CLI 운용을 *"각자 흩어진 16개 소대 + 외부 용병"* 으로 통합한 통신 인프라 기록이다. **CPC(Supabase + Vercel API)** 가 중앙 명령 센터 역할을 하고, **MCP 서버(`cpc_mcp_server.py` + Channel)** 가 Claude Code ↔ CPC 브리지로 *"명령 폴링·결과 보고·5개 도구(`wait_cpc_command`/`report_cpc_result` 등)"* 를 노출한다. 16개 소대(5 프로젝트 × 3소대 + trader-bot) 가 등록되어 IDLE/RUNNING/PAUSED/DONE 상태가 중앙에서 관리되고, 모바일에서 ax-on.net 웹챗봇 UI로 명령을 던질 수 있다. 본 항목 §본인 운용 패턴(*30개 동시 운용에서 키 풀 분배*) 가 단순 키 로테이션을 넘어 **명령 라우팅 인프라**로 격상한 흔적이 이 노트다.
