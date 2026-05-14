---
id: 35
title: "SAL Grid 개발방법론(특허출원된)을 사용해서 한번에 끊김없이 개발업무 진행하기"
type: A
group_id: 2
group_name: "실행 프로세스"
order_in_group: 9
created: 2026-05-06
patent: "10-2026-0009425"
sources:
  - "~/.claude/skills/청룡-sal-grid-dev/SKILL.md (V3.8)"
  - "~/.claude/skills/mbo-코어5/SKILL.md"
  - "patent/특허명세서_통합_제출용.md"
  - "patent/요약서_최종완성본.md"
  - "sal-grid-patent-slideshow.html (26 슬라이드)"
  - "AX-On_Platform/guides/claude-code-guide.html (7,758줄, 본인 자체 SAL Grid Edition 마스터 가이드)"
  - "AI_Magic50/Sunny_AI_Magic_48개_종합정리.md (#14, #35)"
  - "Claude-Wiki/333-knowledge-share/wiki/2026_05_03_21.01_import_PROJECT_SAL_GRID_MANUAL.md (PROJECT SAL GRID MANUAL v3.7, 27 섹션 — 22 속성 정의·5×11 매트릭스·Task 선정 원칙)"
  - "Claude-Wiki/333-knowledge-share/wiki/2026_05_03_21.00_import_SSALWORKS_TASK_PLAN.md (SSALWorks v1.0 실전: 74 Task / 5 Stage × 11 Area)"
  - "Claude-Wiki/333-knowledge-share/wiki/2026_05_03_21.00_import_S9F1_instruction.md (Task 지시서 실예: Kakao 소셜 로그인 S9F1)"
  - "Claude-Wiki/333-knowledge-share/wiki/2026_05_03_21.00_import_S9F1_verification.md (검증 지시서 실예: Task Agent ≠ Verification Agent 분리 적용)"
---

# 35. SAL Grid 개발방법론(특허출원된)을 사용해서 한번에 끊김없이 개발업무 진행하기

## 한 줄 정의

3차원 좌표 — Stage(절차)·Area(영역)·Level(셀 내 의존성) — 를 인코딩한 식별자(SAL ID)를 부여하는 것만으로 의존성·Task 지시서·검증 체계·에이전트 배정이 자동 완성되는 멀티태스크 오케스트레이션 방법론. **특허 출원번호 10-2026-0009425** ([분류표 SSOT](../_PHASE/2026_05_06__19.50_분류표_확정.md#사실-키-ssot-single-source-of-truth)), 본인이 발명한 개발 운영의 골격이며 30개 동시 운용을 끊김 없이 가능케 하는 단 하나의 토대다.

## 왜 이 노하우가 중요한가

Claude Code를 30개 동시 운용하다 보면 가장 먼저 무너지는 것은 **작업의 좌표**다. "지금 어느 단계의 어느 영역에서 몇 번째 작업을 누가 하고 있는가" 를 1인이 추적하지 못하면, AI가 아무리 빨라도 사람이 병목이 된다. 본인 4,000시간 누적 운용에서 가장 큰 손실은 한결같이 "위치 상실" 에서 시작했다 — 같은 작업을 두 번 시켰거나, 의존성이 끊긴 채 다음 단계로 넘어갔거나, 검증 빠진 결과물을 배포한 사고. 모두 좌표가 없어서 생긴 사고다.

기존 도구들 — Jira·Airflow·간트차트·Notion 보드 — 은 모두 **세 가지 한계**를 공유한다.

첫째, **의존성을 사람이 수동으로 선언**해야 한다. Task A가 Task B에 의존한다고 일일이 입력해야 그래프가 그려진다. 빠뜨리면 그래프는 거짓말을 한다. 둘째, **식별자가 무의미한 순차번호**다. JIRA-1234, JIRA-1235만 봐서는 둘이 어떤 관계인지 모른다. 식별자는 단순 일련번호일 뿐, 의미를 담지 못한다. 셋째, **실행과 검증이 별도 도구로 분리**되어 있다. 코드 짜는 곳 따로, 리뷰하는 곳 따로, 결과 기록하는 곳 따로 — 세 곳을 사람이 손으로 동기화한다.

SAL Grid는 이 셋을 **식별자 구조 하나로 동시에 해결**한다. ID에 좌표가 들어 있으니 의존성은 파싱만 하면 자동 추론되고, ID만 봐도 작업 위치가 보이며, 동일 ID 아래 Task 지시서와 Verification 지시서가 짝으로 묶여 분리될 수 없다. 슬라이드 5의 표현을 그대로 옮기면 — *"의존성 선언을 자동화한 것이 아니라, 의존성 개념 자체를 식별자의 구조적 속성으로 치환했다."* 이 문장이 본 발명의 핵심이고, 4,000시간 시행착오 끝에 도달한 결론이며, 특허 청구항 1의 요지이기도 하다.

이 골격이 있으면 30개 인스턴스의 병렬 작업이 1개 인스턴스의 순차 작업처럼 결정론적으로 흐른다. 이 골격이 없으면 5개만 돌려도 무너진다 — 본인이 5번 무너뜨려본 뒤 만든 방법론이다.

## 핵심 개념

### SAL ID 형식

`S{Stage}{Area}{Level}{Variant?}` — 정규식 `^S(\d{1,2})([A-Z]{2})(\d{1,2})([a-z])?$`

예: `S2BI3a` = Stage 2, Area BI(Backend Implementation), Level 3, Variant a.

ID 하나에 **4가지 정보**가 인코딩된다.
- **Stage** — 절차적 순서. S1 완료 후 S2, 건너뛸 수 없다.
- **Area** — 기능적 인접성. 같은 Area는 같은 에이전트·같은 도구 세트.
- **Level** — 셀 내 실행 의존성. L1 완료 후 L2.
- **Variant** — 같은 셀 내 병렬 분기. `a`/`b`/`c`는 동시 실행 가능.

ID를 보는 순간 어디서/어떤 영역의/몇 번째/병렬 가능한지가 동시에 읽힌다. 별도 메타데이터 테이블 조회가 필요 없다.

### 22개 속성 그리드

각 Task는 6그룹 22속성으로 정의된다. 이 22속성이 `grid_records/{TaskID}.json` 한 파일에 실시간 기록된다.

| 그룹 | 속성 수 | 속성 |
|------|--------|------|
| 기본 | 4 | ID·제목·Stage·Area |
| 지시 | 5 | 목표·산출물·도구·에이전트·체크리스트 |
| 실행 | 4 | 시작시각·완료시각·실행에이전트·산출경로 |
| 검증지시 | 2 | 검증기준·검증에이전트 |
| 검증실행 | 4 | 검증시각·결과·점수·증빙 |
| 검증완료 | 3 | 승인자·승인시각·다음Task |

22속성이 한 곳에 모이면 **Task 1건의 전체 생애주기**가 단일 JSON에서 추적 가능하다. PR·이슈·테스트·배포 로그를 따로 뒤질 필요가 없다.

### 핵심 모듈 7개 (특허 청구항 2)

`SAL ID 생성기 → 파서 → 그리드 생성기(Task 지시서 + 검증 지시서 자동 생성) → 시퀀서(Level 충돌 감지) → 배분기(에이전트·도구 배정) → 레코더(실시간 기록) → 뷰어(3D 시각화)`

7개 모듈이 직렬로 연결되어 ID 입력만으로 22속성 골격이 자동 생성된다. 사람이 채우는 것은 "지시" 그룹의 5속성뿐, 나머지 17속성은 시스템이 생성·기록한다.

### TASK_PLAN.md — Stage × Area 매트릭스

본 발명의 가장 시각적인 산출물. N×11 매트릭스에 셀별 Task가 배치된다. 11개 Area는:

`F`(Frontend) · `BA`(Backend Architecture) · `BI`(Backend Implementation) · `S`(Schema) · `D`(DevOps) · `T`(Test) · `M`(Migration) · `U`(UI) · `O`(Operations) · `E`(Engineering) · `C`(Compliance)

실예 — 본인 운영 중인 SSAL Works Project: 5 Stage × 11 Area = 55셀에 74개 Task 배치. 이 한 장의 매트릭스로 프로젝트 전체 진행도가 한눈에 들어온다. 빈 셀은 "그 단계에선 그 영역 작업이 없다", 채워진 셀은 작업과 진행 상태가 색상으로 표시된다.

### 3가지 강제 구조

- **Append-Only ID 체인** — 변경 이력은 `S4BI1_S1BI2_S1BI3` 형태로 ID를 이어붙여 불변 기록. 덮어쓰기 금지. "어떤 결정이 어떤 결정에서 파생됐는가" 가 식별자 자체에 박힌다.
- **실행-검증 일체화** — Executed 상태가 되면 Verification Agent가 **자동 투입**, Verified 아니면 Completed 전환 불가. 청룡 SKILL §7.1의 핵심 규칙이며, "Task Agent ≠ Verification Agent" — 자기가 한 일을 자기가 검증하면 안 된다.
- **Stage Gate** — AI 자동 검증 + PO 최종 승인 없이는 다음 Stage 진입 불가. 거절되면 Task 실행 단계로 회귀. §8.2에 5단계 리포트(누락 점검 → 정합성 체크 → AI 자동 검증 → Stage Gate 리포트 → PO 승인) 강제.

### MBO와의 짝

각 Stage 시작 전 `mbo-코어5`로 목표 제시 → PO 승인 → 자율 실행 → 결과 보고. Stage Gate 통과 시 MBO 결과보고서에서 목표 달성 여부 입증. 청룡 SKILL §6.0이 *"Stage 진입 전 MBO 목표 제시 + PO 승인 필수"* 를 강제한다. SAL Grid가 실행 골격이라면 **MBO는 그 위의 합의 골격**이다. 두 스킬은 한 쌍이며 분리해 쓰지 않는다.

### 운영 모드 3가지 (V3.8)

장기·대규모 프로젝트를 다루기 위한 모드 분기.
- **Lean Mode** — 단순 프로젝트(Stage 3 이하). Variant·Verification 일부 생략, 속도 우선.
- **Standard Mode** — 일반 프로젝트(Stage 4~9). 22속성 풀(full) 적용.
- **Cluster Mode** — 장기 프로젝트(Stage ≥ 10). Stage를 클러스터로 묶어 별도 인덱스 + audit 루프로 관리. **양방향 audit**(orphan/ghost detector)이 정기적으로 SAL Grid와 grid_records의 정합성을 검사한다.

## 실전 사용법

### 1단계 — Project SAL Grid 생성 (S0)

청룡 스킬의 Template을 복사해 `.claude/`, `Process/S0_Project-SAL-Grid_생성/` 구조를 깐다. 신규 프로젝트면 백지에서, 기존 코드면 **소급 도입 모드**로. 사용자 입력(사업계획·기획서)을 수집해 매뉴얼 검토 → SAL Grid 생성 → JSON 생성 → Viewer 확인 → 무결성 검증 워크플로우를 9단계 사이클로 돈다.

### 2단계 — TASK_PLAN 생성

N×11 매트릭스를 분석해 셀별로 Task를 선정하고 SAL ID를 부여한다. ID 부여 즉시 의존성이 자동 추론되므로 별도 그래프 입력은 불필요. Task 지시서와 Verification 지시서가 동일 ID 아래 짝으로 자동 생성된다. 결과를 `TASK_PLAN.md`에 저장. 이 매트릭스가 PO·AI 양쪽이 공유하는 단 하나의 진실 원천(SSOT)이 된다.

### 3단계 — index.json + grid_records 생성

모든 Task의 22속성 골격을 `grid_records/{TaskID}.json`으로 떨어뜨리고, 마스터 인덱스 `index.json`과 `stage_gate_records/`를 생성한다. 여기까지가 PART 1~2(계획·기획서). `node scripts/build-progress.js`로 진행률 0% 베이스라인을 잡고 Viewer로 빈 매트릭스를 한 번 시각화해 PO와 합의 종결.

### 4단계 — Stage 실행 6단계 루프 (PART 3 이후, Stage마다 반복)

- **Stage 진입 전** — MBO 목표 제시 + PO 승인 (§6.0, 강제)
- **Task 실행 6단계** — ① grid_records Read → ② 작업 실행 → ③ 검증 수행 → ④ JSON 업데이트 → ⑤ Git 커밋 → ⑥ Verification 진입
- **Task Agent ≠ Verification Agent** — 다른 에이전트가 검증 (§7.1)
- **Needs Fix 루프** — 검증 실패 → Task 재실행 → 검증 재시작 (최대 5회, 5times-debug-loop과 결합)
- **Stage Gate 5단계 리포트** — 누락 점검 → 정합성 체크 → AI 자동 검증 → Stage Gate 리포트 → PO 승인까지 마쳐야 다음 Stage 진입 (§8.2)

### 5단계 — sal-guard / task-guard pre-commit 활성화

커밋 시점에 TASK_PLAN과 grid_records 무결성을 자동 검증해 의존성 충돌·MBO 미승인·Verification 미완을 **물리적으로 차단**한다(Tier 3). 이게 없으면 30개 동시 운용 시 한 곳의 누락이 전체를 오염시킨다. 사람이 잊어도 시스템이 잊지 않는 마지막 방어선.

### 6단계 — UI 클릭 검증 필수 (V3.8 추가)

UI 산출물은 `curl 200 ≠ 동작함` 원칙. 반드시 Playwright 또는 실제 브라우저에서 주요 버튼·링크를 클릭 테스트해야 Verified 처리된다. SKILL_ATLAS S5 사건 — 사용자가 브라우저에서 보니 4개 버튼 모두 무반응이었던 사고 — 의 직접적 교훈. 자기 검증 금지(Task Agent ≠ Verification Agent)와 결합해 **Verification Agent가 클릭 시나리오를 별도로 수행**한다.

### 7단계 — 양방향 audit (장기 프로젝트)

`scripts/audit.js`가 정기적으로 두 방향을 검사한다. **orphan** — TASK_PLAN에는 있으나 grid_records가 없는 Task. **ghost** — grid_records는 있으나 TASK_PLAN에 없는 Task. 둘 다 정합성 위반이며 자동 알림 → 수동 정리. Cluster Mode에서 특히 중요하다.

## 본인 운용 패턴

Claude Code 글로벌 CLAUDE.md(`~/.claude/CLAUDE.md`)의 "SAL Grid 자동 감지" 규칙으로, 작업 디렉토리에 `SAL_Grid_Dev_Suite/` 폴더가 보이면 별도 지시 없이 청룡 스킬 + mbo-코어5가 자동 발동한다. 사용자가 "청룡 써", "MBO 해" 라고 말하지 않아도 발동 — **이것이 습관에서 인프라로 넘어간 지점**이다. 30개 인스턴스 어디에 들어가도 동일 골격이 즉시 작동한다.

또 하나의 응용: 본인이 직접 만든 `claude-code-guide.html`(7,758줄, ax-on.net에 배포된 Master Guide — SAL Grid Edition)이 SAL Grid 방법론의 첫 자기 적용 사례다. Stage 3개(S1 초급/S2 중급/S3 고급) × Area 6개(CO·ST·WF·TO·QC·CM) = 18셀 학습 그리드로 Claude Code 전체 지식을 분류해 독자가 "지금 어디서 무엇을 배우는지" 좌표로 안내받게 한다. 개발 방법론을 학습 콘텐츠 구조로 재이식한 것이며, 본 방법론의 응용 범용성을 보여주는 증거다.

> Vault 사례: `333-knowledge-share/wiki/PROJECT_SAL_GRID_MANUAL.md` 는 SAL Grid v3.7의 27 섹션 매뉴얼(2025-12-22 최종 수정)이며, 22 속성 정의·Task 선정 원칙·검증 지시서 작성 규칙이 한 문서에 모여 있다. 같은 폴더의 `SSALWORKS_TASK_PLAN.md` 는 본인 운용 중인 SSALWorks v1.0의 **74 Task / 5 Stage × 11 Area** 실전 매트릭스다 — *"P3 중복 제거 / Vercel·OAuth·Resend·결제·도메인 누락 항목 추가 / PoliticianFinder 프로젝트 참조하여 실전 검증됨"* 같은 결정 이력이 그대로 박혀 있다. 그리고 `S9F1_instruction.md`(Kakao 소셜 로그인 Task 지시서)와 그 짝인 `S9F1_verification.md`(검증 체크리스트 — 파일 존재·기능·보안·통합 4부) 가 본문 §실행-검증 일체화·§Task Agent ≠ Verification Agent의 실증이다. 추상적 방법론이 아니라 **실제 누적된 4단 산출물(매뉴얼·매트릭스·Task·검증)** 이 Vault에 쌓여 있다.

## 관련 항목

- **#14 SAL 3차원 좌표** — 본 방법론의 개념적 기초 (이 항목과 짝)
- **#10 MBO** — Stage마다 §6.0에서 짝을 이루는 합의 골격
- **#9 군대 소대 편제** — Task Agent / Verification Agent 분리 운용의 인적 골격
- **#27 Subagent vs Agent Teams** — Task Agent와 Verification Agent의 메커니즘 분기
- **#5 5컴퓨터 30개 운용** — SAL Grid가 다중 인스턴스를 한 골격으로 묶음
- **#6 4종 품질관리** — Stage Gate의 검증 리포트가 review-evaluate / pro-persona-debate / 5times-debug-loop / SAL-DA로 채워짐
- **#23 CLAUDE.md** — SAL Grid 자동 감지 규칙이 본인 글로벌 CLAUDE.md에 헌법으로 박힘
- **#15 패턴 → SVG → 스킬 자산화** — SAL Grid Viewer가 3D 시각화로 패턴을 그대로 보여줌
- **#34 Plan Mode** — S0(Project SAL Grid 생성) 전체가 Plan Mode 관점의 거대화
- **#46 스크린샷 자율 검증 루프** — UI 클릭 검증(§7.1, V3.8)의 Playwright 기반 구현
- **주작-sal-da** — SAL Grid의 **역방향 적용** (기존 코드를 SAL Grid로 역분해하는 감사 방법론)
- **claude-code-guide.html (ax-on.net)** — SAL Grid 방법론의 첫 자기 적용 사례 (학습 콘텐츠 18셀 그리드)
