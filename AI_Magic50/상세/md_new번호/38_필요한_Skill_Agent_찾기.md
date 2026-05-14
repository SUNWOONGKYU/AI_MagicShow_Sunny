---
id: 38
title: "나에게 필요한 Skill, Agent 등의 도구를 쉽게 찾아서 활용하기"
subtitle: "외부 오픈 생태계에서 찾아 검증한 뒤 자기 자산으로 만들기"
type: A
group_id: 5
group_name: "환경"
order_in_group: 8
created: 2026-05-06
sources:
  - "~/.claude/skills/find-skills-기본/SKILL.md"
  - "https://skills.sh/ (오픈 스킬 레지스트리)"
  - "https://github.com/revfactory/skills (revfactory/skills 저장소 — 본인 발굴 사례 누적)"
  - "AI_Magic50/Sunny_AI_Magic_48개_종합정리.md (#28)"
  - "본인 글로벌 스킬 41개 자기 자산화 운용 기록 (~/.claude/skills/)"
  - "외부 스킬 다중 버전 누적 운용 사례 — 본인 톤 재단 흔적"
  - "Tool Atlas — 본인이 운영하는 스킬·에이전트 발굴 인프라 (Next.js + Supabase 기반)"
---

# 38. 나에게 필요한 Skill, Agent 등의 도구를 쉽게 찾아서 활용하기

## 한 줄 정의

외부 오픈 생태계(skills.sh · revfactory/skills · GitHub 공개 저장소)에서 필요한 스킬과 서브에이전트를 **검색 → 검증 → 자기 자산화**하는 3단계 발굴 운용. 본인 글로벌 환경 `~/.claude/skills/` 41개 스킬 가운데 절반 이상이 이 발굴 루프를 통해 들어왔거나, 외부 자산을 본인 운용 패턴에 맞춰 재단·증설한 결과다.

## 왜 이 노하우가 중요한가

Claude Code를 30개 동시 운용하다 보면 가장 빨리 한계에 부딪히는 곳은 모델 성능이 아니라 **본인이 직접 쓴 도구의 양**이다. 모든 작업을 자기 손으로 스킬화하려 들면 4,000시간이 와도 부족하다. 본인이 4,000시간 누적 끝에 내린 결론은 단순하다 — *"잘 만들어진 외부 스킬은 발굴해서 검증한 뒤 자기 자산으로 흡수하고, 시간은 본인만이 만들 수 있는 스킬에 쓴다."* 이게 안 되면 1인 운용은 한 명분 인건비를 쓰는 1인 운용에 머무르고, 30개 인스턴스의 잠재력을 절대 끌어내지 못한다.

또 하나, 외부 스킬 발굴은 **자기 사고의 사각지대를 메우는 가장 빠른 길**이다. 본인이 떠올리지 못한 패턴을 누군가 이미 코드로 구현해놨을 때, 그 SKILL.md를 한 번 읽는 것만으로 사고의 새 차원이 열린다. 본인 글로벌 스킬에 들어와 있는 `frontend-design`, `simplify`, `loop`, `schedule`, `claude-api`, `update-config`, `keybindings-help`, `add-pc` 같은 스킬들은 모두 외부 오픈 생태계에서 발굴해 본인 환경에 흡수한 것이다. 본인이 처음부터 만들 생각조차 못 했던 패턴이 있고, 발굴 한 번이 사고의 영토를 그만큼 넓혀준다.

세 번째 이유 — **검증 없이 도입하는 것은 더 위험하다**. 외부 스킬은 본인 글로벌 CLAUDE.md의 보안 가드(`G:\내 드라이브\` 경로 보호, .env 차단, 한국어 출력 규칙 등) · Hooks · MBO·SAL Grid 자동 감지 등 본인 환경 전체와 충돌할 수 있다. 검증 없이 글로벌 설치하면 30개 인스턴스 전체가 동시에 오염된다. 그래서 발굴은 *"찾기"* 가 아니라 *"찾기 + 시험 + 합본"* 의 운용 사이클이다. 슬로건처럼 *"AI 시대엔 도구 발굴이 곧 실력"* 이라 말하는 사람은 많지만, 본인 운용 기준으론 정확히는 — **"발굴 자체가 아니라 검증 후 자기 자산화까지 가는 흐름이 실력"** 이다.

## 핵심 개념

### 발굴 3단계 루프 (본인 운용 패턴)

| 단계 | 행위 | 실패 시 |
|------|------|---------|
| ① 검색 (Find) | 키워드로 후보 5~10개 추출 | 후보 없음 → 직접 작성 검토 |
| ② 검증 (Verify) | SKILL.md Read · 실 트라이얼 (1회 이상) · KPI 체크 | 실패 → 폐기 또는 fork |
| ③ 자산화 (Assetize) | `~/.claude/skills/`에 흡수 + CLAUDE.md 헌법 등재 | 미흡수 → 다음 작업에 재발굴 비용 발생 |

검증 없는 1단계 종료는 금지. *"오 이 스킬 좋네"* 로 끝나면 다음 세션에서 똑같은 검색을 반복하게 된다.

### 오픈 생태계 3대 출처

1. **skills.sh** — 공식 레지스트리(`https://skills.sh/`). 카테고리(웹 개발 · 테스트 · DevOps · 문서화 · 코드 품질 · 디자인 · 생산성)별 검색.
2. **revfactory/skills** — `https://github.com/revfactory/skills`. 검증된 저장소로 본인 발굴 1차 후보지. 슬라이드·종합정리에서도 *"17번 멀티 CLI · 28번 발굴 시 사례"* 로 인용.
3. **GitHub 일반 검색** — `claude-code skill` · `agent skill` 키워드로 비공식 저장소 추적. 본인이 활용 중인 `frontend-design`, `simplify` 등이 이 경로로 들어왔다.

### 본인이 만드는 발굴 인프라 — Tool Atlas

세 출처(skills.sh · revfactory/skills · GitHub)를 4,000시간 굴려본 결과, 세 곳 모두 "읽기 위주의 카탈로그"라는 한계가 보였다. SKILL.md를 열어 읽고, 좋으면 설치 명령은 또 다른 곳에서 찾고, 검증은 본인이 알아서 한다. *"잘 만들어진 외부 자산을 본인 운용에 즉시 흡수"* 라는 본 챕터 결론을 한 단계 빠르게 만들 인프라가 필요하다는 결론이 나왔고, 그 답이 본인이 직접 만들고 있는 **Tool Atlas** (Next.js 14 + Supabase, CC BY-SA 4.0, alpha 단계)다.

Tool Atlas의 차별점은 세 가지.

1. **형식 무관 통합** — Skill에 한정하지 않고 Skill·Agent·MCP·Prompt·Workflow·CLI까지 한 카탈로그에서 검색·평가·연결. skills.sh가 Skill 전용이라면, Tool Atlas는 AI 도구 전체의 메타 카탈로그.
2. **실행 가능한 형태** — "읽기만 하는 위키"가 아니라 각 항목이 설치·실행 가능한 코드·프롬프트를 함께 가지고 있다. 발견에서 실행까지 한 화면.
3. **시맨틱 검색 + 4 은하 분류** — pgvector + OpenAI 임베딩으로 의미 검색, 정치(PL)·경제(EC)·사회(SO)·문화(CL) 4 은하 분류 + Three.js 3D 우주 뷰로 시각화. 키워드를 정확히 모를 때 도메인부터 좁히고 들어가는 흐름.

본인 입장에서 Tool Atlas는 *"외부 발굴 사용자에서 발굴 인프라 제공자로 한 발 넘어간 자리"* 다. 본 챕터 결론(*발굴 → 검증 → 자산화*)의 다음 단계 — *"본인 자산화 흐름 자체를 생태계에 환원하는 단계"*.

### find-skills-기본 스킬 (본인 글로벌)

본인이 운용 중인 발굴 전용 스킬은 `~/.claude/skills/find-skills-기본/SKILL.md`에 박혀 있다. 검색·결과 표시·설치·관리 5단계가 명세되어 있고 핵심 명령어는 다음과 같다.

```bash
# 검색
npx skills find "react performance"

# 글로벌 설치 (모든 프로젝트에서 사용)
npx skills add owner/repo@skill-name -g -y

# 프로젝트 로컬 설치
npx skills add owner/repo@skill-name -y

# 업데이트 점검·일괄 적용·제거
npx skills check
npx skills update
npx skills remove owner/repo@skill-name
```

이 스킬을 만든 이유는 단순하다 — *"필요할 때마다 검색 명령을 다시 떠올리지 않기 위해"*. 키워드 카테고리 표(`react`, `pr review`, `tailwind css`, `testing jest`, `mcp integration`, `data scientist` 등)를 SKILL.md 안에 박아둔 것도 같은 이유. **자주 쓰는 검색은 스킬 안에 박아 둔다** 는 것 자체가 본인 운용 헌법이다.

### 검증 KPI (도입 가부 판정)

발굴된 스킬을 자산화할지 결정할 때 본인은 5개 지표를 본다.

| 지표 | 합격선 | 측정 방법 |
|------|--------|-----------|
| SKILL.md 명료성 | 사용 시점·실행 절차·예시 모두 존재 | Read 1회로 5분 내 이해 |
| 본인 운용과의 충돌 | 0건 (한국어 출력 · 보안 가드 위반 없음) | CLAUDE.md 헌법 대조 |
| 트라이얼 통과 | 1회 이상 실제 작업 적용 | 사용자 여정 KPI 통과 |
| 의존성 추가 부담 | npm/pip 추가 없음 또는 1개 이하 | 설치 로그 점검 |
| 자기 검증 가능성 | 결과물에 객관 검증 가능 | Verification Agent 별도 투입 가능 여부 |

5개 중 4개 미만이면 자산화 보류. 이 가운데 *"본인 운용과의 충돌 0건"* 은 **타협 불가** — 글로벌 헌법(`~/.claude/CLAUDE.md`)에 박힌 한국어 출력 규칙·보안 가드·SAL Grid 자동 감지·MBO 자동 발동을 깨는 스킬은 아무리 기능이 좋아도 글로벌에 들이지 않고 프로젝트 로컬에만 둔다.

### 본인 글로벌 41개 스킬 분류

자산화의 산물은 `~/.claude/skills/` 41개로 누적되어 있다. 카테고리별 분포는 본인 운용의 거울이다.

| 분류 | 대표 스킬 | 비고 |
|------|----------|------|
| 본인 발명·자가 코어 | `청룡-sal-grid-dev` · `백호-platoon-formation` · `주작-sal-da` · `현무-buzzlab-simulation` · `mbo-코어5` · `review-evaluate-코어1` · `pro-persona-debate-코어6` · `5times-debug-loop-코어3` | 외부 발굴 不可, 본인이 누적 운용으로 만든 자산 |
| 외부 발굴 → 자산화 | `frontend-design` · `simplify` · `loop` · `schedule` · `claude-api` · `update-config` · `keybindings-help` · `add-pc` | revfactory/skills 외부 출처를 검증 후 글로벌 등재 |
| 도메인 도구 (자체+외부 혼합) | `youtube-기본` · `video-frames-기본` · `ai-image-기본` · `image-기본` · `architecture-svg` · `create-image-기본` · `doc-generator-기본` · `db-schema-기본` · `ui-ux-builder-기본` · `api-builder-기본` · `api-test-기본` · `e2e-test-기본` · `cicd-setup-기본` · `performance-check-기본` · `security-audit-기본` · `troubleshoot-기본` · `n8n-workflow-test` | 외부 자산을 본인 톤·KPI로 재단해 흡수 |
| 발굴 메타 스킬 | `find-skills-기본` · `deploy-skill-기본` · `deploy-subagent-기본` | 발굴·편성 자체를 자산화 |
| 인프라·배포 | `vercel-private-url-배포` · `cpc-setup` · `cpc-engage` · `cpc-add-project` | 본인 대규모 동시 운용 인프라 |
| 도메인 비즈 | `buzzlab-politician-winning-strategy` · `campaign-route-strategy` · `weekly-opinion-report` | 정치 분석 도메인 자산 |

발굴 → 자산화 카테고리 8개가 결정적이다. 누적 운용 가운데 가장 큰 ROI는 *"내가 못 만들 스킬을 잘 발굴해 본인 운용에 흡수한 부분"* 이고, 이 카테고리가 그 증거다.

## 실전 사용법

### 1단계 — 요구사항 좌표화

발굴 전에 *"무엇을 찾는가"* 를 한 줄로 좌표화한다. 도메인(예: 프론트엔드 디자인) · 구체 작업(예: shadcn/ui 컴포넌트 생성) · 본인 운용 제약(예: 한국어 주석 자동 출력) 3축. 이 단계를 건너뛰면 검색 결과 5~10개가 들어와도 결정 불가에 빠진다.

### 2단계 — `npx skills find` 실행

`find-skills-기본` 스킬의 키워드 표를 그대로 활용. 예 — `npx skills find "frontend design"` · `npx skills find "pr review"` · `npx skills find "mcp integration"`. 결과로 스킬 이름·설명·설치 명령어·skills.sh 링크 4종이 나온다.

### 3단계 — SKILL.md Read로 1차 필터

후보 5~10개 가운데 SKILL.md를 Read로 직접 본다. 5분 내 이해 안 되면 탈락. 이 1차 필터가 80%를 걸러낸다.

### 4단계 — 트라이얼 (반드시 프로젝트 로컬)

```bash
npx skills add owner/repo@skill-name -y   # 글로벌 -g 빼고 로컬에만
```

로컬 설치 후 본인 실작업에 1회 이상 적용. 산출물을 `review-evaluate-코어1`로 5기준 검증, UI가 있으면 Playwright 클릭 테스트. **자기 검증 금지** — 스킬을 발굴한 본인이 자기 검증하면 안 된다. Verification Agent를 별도 투입해 *"이 스킬의 결과물이 본인 KPI를 충족하는가"* 를 객관 평가한다. 이때 *"curl 200 ≠ 동작함"* 원칙은 외부 스킬에도 그대로 적용된다.

### 5단계 — 글로벌 자산화 (-g)

검증 통과한 스킬만 `-g` 플래그로 글로벌 등재.

```bash
npx skills add owner/repo@skill-name -g -y
```

이후 `~/.claude/CLAUDE.md` 헌법에 등재 사실을 1줄 적어둔다. 글로벌 헌법에 안 적으면 컴팩션 후 본인 자신도 잊는다. *"파일이 진실이다, 기억은 신뢰하지 마라"* 는 본인 운용 4번 규칙(미완료 Phase 건너뜀 금지)이 여기에도 그대로 적용된다.

### 6단계 — 정기 점검 (`npx skills check` · `update`)

```bash
npx skills check    # 업데이트 가능 항목 표시
npx skills update   # 일괄 적용
```

월 1회 정기 실행. 스킬 업데이트가 본인 운용 패턴을 깰 수 있으므로, **update 직후 1~2일은 회귀 모니터링**. 회귀 발생 시 `npx skills remove`로 즉시 롤백하고 fork 검토.

### 7단계 — 발굴 자체를 SAL Grid Task로 등록

대규모 작업 시작 시 *"필요 스킬 발굴"* 을 SAL Grid의 별도 Task(예: `S0E1` Engineering 영역 Level 1)로 박는다. 이러면 발굴 비용이 프로젝트 진행률 % 에 반영되고, *"발굴 빠뜨려서 작업 지연"* 사고가 사라진다. SAL Grid Recorder가 발굴·검증·자산화 시각까지 grid_records JSON에 박아준다.

## 본인 운용 패턴

본인 41개 글로벌 스킬은 *"발굴해서 끝"* 이 아니라 *"발굴 → 검증 → 본인 운용 톤으로 재단 → 자산화 → 정기 점검"* 의 5단 흐름이 한 번 이상 적용된 결과다. 외부에서 들여온 `frontend-design` 같은 스킬도 본인 글로벌 CLAUDE.md의 한국어 출력 규칙·보안 가드와 한 번 충돌 점검을 거친 뒤 등재됐다. 발굴은 시작이고, 자산화는 운용 끝까지 따라간다.

또 하나 — 발굴은 본인이 *"필요해진 시점"* 이 아니라 *"필요할 가능성이 보이는 시점"* 에 한다. 30개 동시 운용에서 그날 그날 필요한 스킬을 그날 발굴하면 이미 늦다. 본인은 매주 1회 `npx skills check`와 함께 *"이번 주 작업 시계열에서 사용할 가능성 30% 이상의 스킬"* 을 미리 발굴한다. 이 선제 발굴 루틴이 5번 30개 운용 · 9번 소대 편제 · 17번 멀티 CLI를 끊김 없이 돌리는 숨은 골격이다.

> Vault 사례: `333-knowledge-share/wiki/2026_05_03_21.00_import_SKILL_v3_pre_refactor.md` 같은 SKILL_v1 / v2 / v2_260306 / v3_pre_refactor 다중 스냅샷이 한 폴더에 누적돼 있다는 사실 자체가 *발굴 → 검증 → 본인 톤으로 재단 → 자산화 → 정기 점검*의 5단 흐름을 본인이 실제로 돌렸다는 흔적이다. 동일 스킬이 여러 버전으로 박혀 있고 *pre_refactor* 라벨이 붙은 것은 — 외부에서 들여온 원본을 본인 운용 톤(소대 편제 / Subagent 트리거 / Hooks 가드)에 맞춰 재단했다는 의미. 28번 본 항목의 *"발굴은 시작이고, 자산화는 운용 끝까지 따라간다"* 명제가 그 누적 스냅샷 자체로 증명된다.

## 관련 항목

- **#22 오케스트레이터·멀티 CLI** — 발굴된 스킬을 다중 CLI(Codex/Gemini/Grok)와 결합해 운용
- **#25 지능형 챗봇 만들기** — 발굴 능력이 챗봇 자산화의 전제
- **#24 SVG → 스킬 자산화** — 본인이 만드는 자산화 흐름의 짝
- **#32 CLAUDE.md 활용** — 자산화 후 헌법 등재 단계
- **#39 Subagent vs Agent Teams** — 발굴된 에이전트의 편성 단계
- **#14 군대 소대 편제 + 백호 스킬** — 발굴 후 편성 단계
- **#28 4종 품질관리** — 발굴 검증 단계의 5기준 평가
- **#2 SAL Grid 개발방법론** — 발굴 자체를 Task로 박는 골격
- **find-skills-기본 (본인 글로벌)** — 본 노하우의 코드화된 형태
- **deploy-skill-기본 / deploy-subagent-기본 (본인 글로벌)** — 발굴 결과를 편성·장착하는 메타 스킬
- **revfactory/skills** — 본인 1차 발굴 출처 저장소
- **Tool Atlas (본인 발굴 인프라, alpha)** — 본 챕터 결론의 다음 단계 자리. 참고자료 sources 참조.
