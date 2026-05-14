---
id: 48
title: "WiKi_LLM과 Obsidian을 활용한 지식베이스 관리하기"
subtitle: "장기 기억 인프라 — AI가 자기 위키에 쓰고 다음 작업 전에 그 위키를 먼저 읽는다"
type: A
group_id: 6
group_name: "기타"
order_in_group: 7
created: 2026-05-06
sources:
  - "G:\\내 드라이브\\Claude-Wiki\\ (본인 Obsidian Vault 루트, 15개 프로젝트 폴더)"
  - "G:\\내 드라이브\\Claude-Wiki\\CLAUDE.md (Wiki-LLM Schema & 명명 규칙)"
  - "AI_Magic50/Sunny_AI_Magic_48개_종합정리.md (#4, #22, #23)"
  - "~/.claude/skills/find-skills-기본/SKILL.md (외부 자산 도입)"
  - "Claude-Wiki/llmwiki-obsidian-guide/wiki/2026_05_03_15.30_research_wiki-llm-implementation.md (Karpathy LLM 위키 패턴 본인 Vault 적용 — RAG 한계 vs LLM 위키 장점 비교표)"
  - "Claude-Wiki/llmwiki-obsidian-guide/wiki/2026_05_03_16.00_session_wiki-llm-obsidian-integration-complete.md (Vault + Obsidian 통합 완료 세션 기록 — raw/wiki/index 3계층 + ingest.js/compile.js)"
  - "Claude-Wiki/llmwiki-obsidian-guide/wiki/2026_05_03_17.30_session_wiki-llm-integration-completion.md (최종 결론: 커맨드 인프라 폐기, '저장해' 한 마디로 충분)"
---

# 48. WiKi_LLM과 Obsidian을 활용한 지식베이스 관리하기

## 한 줄 정의

Andrej Karpathy가 제안한 것으로 알려진 **LLM 위키** 패턴(AI가 작업 기록을 마크다운 위키로 자동 정제·누적하는 방식)을 **Obsidian** 같은 마크다운 노트 도구 위에 얹어, 한 세션 안에서 끝나지 않는 **세션 너머의 장기 기억 인프라**를 만드는 노하우. AI 작업이 일회성으로 사라지지 않고, 과거 결정·실패·패턴이 다음 작업의 입력 자산으로 회수되게 만드는 운용 기반.

> **호칭 정리** — 이 책 제목·시리즈에서 쓰는 "WiKi_LLM"은 본문의 "LLM 위키"·"Karpathy 패턴"과 같은 대상을 가리킨다. 정확한 호칭은 *LLM 위키*(LLM이 주체) 이며, 본문은 이 표기를 따른다.

## 왜 이 노하우가 중요한가

AI 도구의 컨텍스트 윈도우는 길어야 200K 토큰 수준이고, 압축이 한 번 들어가면 그 안의 결정·근거·시행착오가 **손실을 동반한 요약**으로 사라진다. 이 한계는 단일 세션 안에서는 일부 관리(`/compact` 끄기, 컨텍스트 절제 등)로 버틸 수 있지만, **세션 너머**의 누적은 불가능하다. 한 달 전에 푼 같은 문제를 오늘 다시 푼다면, 그것은 AI 도구의 한계가 아니라 *사용자가 외부 기억 인프라를 가지지 않았기 때문*이다.

기존 도구들 — 메모장·노션·구글독스·VS Code 폴더 — 은 모두 같은 한계를 공유한다. 첫째, **AI가 직접 정제·갱신하지 못한다**. 사람이 복붙해서 컨텍스트에 넣어줘야 한다. 둘째, **링크 그래프가 약하다**. "이 결정이 어느 결정에서 파생됐는가" 가 보이지 않는다. 셋째, **마크다운 표준화가 안 된 채 누적되어** 다음 작업에서 재사용하기 어렵다.

LLM 위키 + Obsidian 조합은 이 세 한계를 동시에 푼다. **마크다운만 사용**해 별도 인프라(벡터 DB·서버) 없이 작동하고, **양방향 링크와 그래프 뷰**가 결정 간 의존성을 시각화하며, **AI가 직접 새 노트를 작성·정제·인덱싱**한다. 한 줄로 — AI가 자기 작업을 자기 위키에 적어두고 다음 작업 전에 그 위키를 먼저 보는 구조다.

## 핵심 개념

### LLM 위키 (Karpathy 패턴)

2026년 4월 Andrej Karpathy(OpenAI 공동 창립자)가 제시한 패턴. 핵심 아이디어 — *"RAG처럼 매번 벡터 검색하지 말고, AI가 직접 마크다운 위키를 누적시켜 그 위키를 자체 인덱스로 네비게이션하라"*. 차이를 표로 정리하면:

| 구분 | RAG | LLM 위키 |
|------|-----|---------|
| 검색 방식 | 매번 벡터 검색 | 자체 인덱스 네비게이션 |
| 지식 누적 | 상태 없음(stateless) | 상태 있음(stateful) |
| 인프라 | 벡터 DB 필요 | 마크다운만 |
| 적정 규모 | 100+ 문서에서 비효율 | 개인·팀 규모에 최적 |

핵심은 *"누적이 손실 없이 일어난다"* 는 점. 한 번 적은 노트가 다음 작업의 입력이 되고, 그 작업의 결과가 다시 노트로 누적된다.

### 3계층 아키텍처 — raw → wiki → index

LLM 위키의 기본 골격.

- **raw/** — 원본 저장. 세션 기록·연구 노트·결정 메모·버그 픽스 회고가 마크다운으로 곧장 저장된다. **불변**.
- **wiki/** — 정제 레이어. AI가 raw를 읽어 frontmatter 정리·양방향 링크 보강·중복 제거를 수행한 결과물. 사람이 검색·재사용할 자료.
- **index.md** — 자동 인덱스. wiki 안의 노트를 주제·날짜·태그로 묶어 진입점 역할.

raw에는 사람이 자유롭게 적고, wiki는 AI가 정제하며, index는 자동 갱신된다. 이 흐름이 *"기록 → 정제 → 검색"* 의 3단을 분리해주는 게 핵심이다 — 한 폴더에 다 적으면 정제할 시점에 무엇이 원본인지 모르게 된다.

### Obsidian이 적합한 이유

LLM 위키 패턴은 어떤 마크다운 도구에서도 작동하지만, Obsidian이 잘 맞는 이유 4가지:

1. **양방향 링크** `[[노트A]]` — 노트 A가 노트 B를 참조하면 B에서도 A의 backlink가 자동 표시. 결정 가지치기가 양쪽으로 보인다.
2. **그래프 뷰** — 노트 간 링크를 시각적 노드 그래프로 본다. 고립 노드(orphan)나 끊긴 링크(ghost)를 한눈에 잡는다.
3. **로컬 마크다운** — 별도 서버·DB 없이 사용자 컴퓨터의 폴더 하나가 곧 데이터 저장소. 클라우드 동기화 폴더에 두면 여러 기기에서 동일 상태로 공유된다.
4. **플러그인 생태계** — Dataview(쿼리)·Templater(템플릿)·Periodic Notes(일일 노트) 등으로 운용을 자동화할 수 있다.

이 4가지가 LLM 위키 패턴의 *"마크다운만으로 충분"* 이라는 전제와 정확히 맞물린다.

### 자동화의 함정 — 단순화의 가치

LLM 위키를 처음 구축하면 흔히 빠지는 함정 — *"세션을 실시간 모니터링하는 데몬"*, *"파일 변화 자동 감지 스크립트"*, *"슬래시 커맨드로 한 번에 wiki 갱신"* 같은 정교한 자동 인프라를 먼저 짠다. 결과적으로 자동화 인프라 자체가 깨지거나 작동하지 않고, 정작 *"저장"* 이라는 본질이 흐려진다.

이 패턴에서 가장 단순한 진실 — **AI에게 "이거 raw/에 저장해" 라고 말하면 즉시 저장된다**. AI는 대화 인터페이스다. 별도 데몬·hook·커맨드 없이도 *"저장"* 한 마디로 raw가 채워지고, AI가 직접 ingest·compile 스크립트를 실행해 wiki에 반영한다. 인간 대화 인터페이스가 어떤 자동 인프라보다 강한 이유는 *유연성*과 *맥락성* 둘 다 가지기 때문이다.

부수적으로 — 컨텍스트 자동 압축(Auto-Compaction)이 LLM 위키 시스템과 충돌한다. 위키가 세션 보존을 담당하기로 했으면 자동 압축은 꺼두는 게 일관적이다.

### RAG와의 짝 — 일방 대체가 아니다

LLM 위키가 RAG를 완전히 대체하지는 않는다. 위키는 *개인·팀 규모의 누적 지식*에 최적이고, RAG는 *고정된 대규모 외부 코퍼스*(법령·논문·사양서 100,000건+)에 적합하다. 본인이 매일 만지는 결정·실패·패턴은 LLM 위키에 두고, 변하지 않는 외부 표준 문서는 RAG에 둔다. 두 인프라가 짝을 이룬다.

## 실전 사용법

### 1단계 — Vault 초기화

Obsidian 설치 후 동기화 폴더(Google Drive·Dropbox·iCloud 등) 안에 Vault 디렉터리 하나를 만든다. 클라우드 동기화 폴더에 두면 PC·모바일·태블릿 어디서 켜도 같은 상태를 본다. C드라이브 + G드라이브 백업 원칙(#40)의 직접 적용.

> **모바일·원격접속 운용 보너스** — Vault를 Google Drive 같은 동기화 폴더에 두면, 외출 중 스마트폰에서 Obsidian 모바일·구글 드라이브 앱으로 wiki/ 노트를 곧장 열람할 수 있다. 데스크탑 AI가 raw에 새 결정 파일을 만들면 동기화로 모바일에도 즉시 반영되고, 반대로 모바일에서 메모해 둔 파일을 데스크탑 AI가 다음 세션에 ingest한다. *"머리에 외운다 → 모바일에서도 본다"* 의 전환이 이 단순한 폴더 배치 하나로 일어난다.

### 2단계 — raw/ → wiki/ → index.md 3계층 폴더 생성

```
Vault/
├── raw/        ← 원본 (프로젝트별 하위 폴더 권장)
├── wiki/       ← 정제된 문서
├── _meta/      ← 메타데이터(태그·통계)
├── scripts/    ← ingest·compile 자동화
└── index.md    ← 자동 인덱스
```

raw 안에서 **프로젝트별 하위 폴더로 한 번 더 나누는** 것이 운용 키. 프로젝트가 늘어나도 원본 영역이 무너지지 않는다.

### 3단계 — frontmatter 표준화

모든 노트 상단에 YAML frontmatter를 둔다. 표준 예:

```yaml
---
date: 2026-05-13
type: session | research | decision | bug-fix | incident | pattern
project: 프로젝트명
tags: [...]
status: draft | ready-for-wiki | archived
priority: p0 | p1 | p2
---
```

이 표준이 있어야 ingest 스크립트가 raw를 읽고 분류할 수 있고, Obsidian의 Dataview 쿼리가 통한다.

### 4단계 — "저장해" 한 마디 운용

파일 쓰기 권한이 있는 AI CLI(예: Claude Code, Cursor, Aider 등 로컬 디렉터리에 직접 마크다운을 쓸 수 있는 도구)에 대화 도중 한국어 한 문장을 입력한다. 예:

```
이 결정 raw/buzzlab-nemotron/ 에 저장해. 파일명은 오늘 날짜·시간_decision_{한줄제목}.md, frontmatter 채워서.
```

AI가 즉시 frontmatter 포함 마크다운으로 raw에 파일을 생성한다. ChatGPT 웹·Claude 웹처럼 *로컬 쓰기 권한이 없는* 인터페이스를 쓰는 경우엔, AI에게 *"방금 결정을 위 frontmatter 표준대로 마크다운 한 덩어리로 출력해줘"* 라고 시킨 뒤 출력 결과를 직접 raw/에 붙여넣으면 된다. watch 데몬·슬래시 커맨드 같은 자동 인프라보다 이 단순한 *말 한 마디 + 복붙* 운용이 견고하다.

### 5단계 — ingest·compile 자동화 (선택)

raw가 일정량 쌓이면 정제 스크립트를 만든다.
- **ingest.js** — raw 마크다운을 읽어 frontmatter 정합 확인, 중복 제거, 양방향 링크 보강
- **compile.js** — wiki 디렉터리의 모든 노트를 훑어 index.md를 갱신

ingest.js의 가장 단순한 골격(Node.js, 20줄 미만):

```javascript
// scripts/ingest.js — raw → wiki 정제
const fs = require('fs');
const path = require('path');
const matter = require('gray-matter');  // frontmatter 파서

const RAW = 'raw', WIKI = 'wiki';

function walk(dir, files = []) {
  for (const f of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, f.name);
    f.isDirectory() ? walk(p, files) : f.name.endsWith('.md') && files.push(p);
  }
  return files;
}

for (const file of walk(RAW)) {
  const { data, content } = matter(fs.readFileSync(file, 'utf8'));
  if (data.status !== 'ready-for-wiki') continue;
  const out = path.join(WIKI, path.basename(file));
  fs.writeFileSync(out, matter.stringify(content, data));
  console.log('✓', out);
}
```

compile.js는 wiki/ 안 모든 파일의 frontmatter를 읽어 *날짜·태그·프로젝트별 표* 를 index.md에 출력하는 정도면 충분하다. AI에게 두 스크립트 실행을 *"raw 정리해줘"* 한 마디로 위임 가능하다.

### 6단계 — 그래프 뷰로 양방향 정합성 점검

월 1회 Obsidian Graph View를 열어:
- **고립 노드(orphan)** — 어디에도 링크되지 않은 노트
- **유령 링크(ghost)** — 존재하지 않는 노트로의 링크

두 가지를 점검한다. SAL Grid 개발방법론(#13)의 양방향 audit과 동일 사상의 적용.

### 7단계 — 챗봇 RAG 소스로 연결

지능형 챗봇(#24)을 만들 때 wiki/ 디렉터리를 RAG 소스로 지정. 챗봇이 *"사용자 본인의 과거 결정"* 까지 답할 수 있게 된다. 단, raw/는 RAG 소스에서 제외하는 게 안전 — 정제 전 메모가 챗봇 답변에 그대로 노출되면 곤란하다.

### 8단계 — 장기 누적 시 Cluster 운영

노트가 수천 건을 넘어가면 wiki 자체가 SAL Grid 개발방법론(#13)의 Cluster Mode 대상이 된다. 도메인별 클러스터로 분리하고, 자동 audit 스크립트를 돌려 정합성을 자동 유지한다.

## 본인 운용 사례 (가벼운 인용)

본인 Vault 루트는 `G:\내 드라이브\Claude-Wiki\`. 15개 프로젝트(buzzlab-nemotron / sal-grid-dev / skill-atlas / llmwiki-obsidian-guide 등)별 폴더에 raw/wiki/index 3계층을 그대로 깔았다. 가장 큰 깨달음 한 줄 — *"커맨드 인프라보다 '저장해' 한 마디가 강하다"*. 처음엔 watch 데몬·슬래시 커맨드 등을 만들어봤지만 다 폐기하고, 음성 명령 기반 운용으로 단순화한 뒤로 누적이 끊기지 않는다.

또 한 가지 — 컨텍스트 자동 압축을 꺼두고(Auto-Compaction OFF, #17 참고) 세션 보존을 Vault에 위임했다. 같은 함정에 두 번 빠지지 않는 단 하나의 이유는 *"누적 운용 동안 같은 결정의 흔적이 모두 wiki에 남아있고, 다음 작업 전에 AI가 그 wiki를 먼저 읽기 때문"*. Vault는 단순한 노트 저장소가 아니라 **사고 인프라**다 — 사람의 머리는 인덱스 작성만, 본문은 Vault에 둔다는 분업이 다중 인스턴스 운용(#31)의 실제 골격이다.

> Vault 사례: `llmwiki-obsidian-guide/wiki/2026_05_03_15.30_research_wiki-llm-implementation.md` 에 Karpathy LLM 위키 패턴과 RAG의 비교표가 그대로 박혀 있고, 같은 폴더 `17.30_session_wiki-llm-integration-completion.md` 에 *"watch 스크립트 폐기 → '저장해' 한 마디로 단순화"* 라는 최종 결론이 일자별 근거와 함께 남아 있다. 본 챕터의 *"자동화의 함정"* 단락은 이 두 노트에서 직접 도출된 것이다.

## 관련 항목

- **#24 지능형 챗봇 키우기** — wiki/를 RAG 소스로 직접 사용하는 짝
- **#33 CLAUDE.md 활용** — Vault 운용 규칙을 헌법층에 박는 짝
- **#38 필요한 Skill·Agent 찾기** — 외부에서 발견한 자산을 Vault에 흡수하는 입구
- **#17 Auto Compact 끄고 수동** — 단발성 기억(컨텍스트) ↔ 장기 기억(Vault) 분업의 짝
- **#40 C드라이브 + G드라이브 백업** — Vault를 동기화 폴더에 두는 인프라적 근거
- **#13 SAL Grid 개발방법론** — 양방향 audit·Cluster Mode 운영이 동일 사상의 다른 적용
- **#31 5컴퓨터 30개 동시 운용** — 다중 인스턴스가 한 Vault를 공유하는 구조
- **#22 SVG 아키텍처 스킬화** — Vault에 누적된 패턴이 SVG·스킬로 결정화되는 흐름
- **#44 문서화는 나중에** — 일단 만들고 사후 정리해서 Vault에 누적하는 운용
