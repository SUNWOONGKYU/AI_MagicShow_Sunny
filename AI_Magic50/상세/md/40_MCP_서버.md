---
id: 40
title: "MCP 서버 활용하기"
type: B
group_id: 3
group_name: "실행 방법"
order_in_group: 7
created: 2026-05-06
sources:
  - "~/.claude.json (본인 mcpServers — windows-mcp / stitch / cpc-channel)"
  - "Anthropic MCP 공식 문서 (modelcontextprotocol.io)"
  - "AI_Magic50/Sunny_AI_Magic_48개_종합정리.md (#40)"
  - "C:/claude-project/cpc-agent-server/cpc-channel/dist/cpc-channel.js"
  - "Claude-Wiki/claude-platoons-control/wiki/2026_05_03_21.07_import_CPC_ARCHITECTURE_OVERVIEW.md (CPC MCP 서버 5도구: wait_cpc_command·report_cpc_result + Channel 통신 Bridge)"
---

# 40. MCP 서버 활용하기

## 한 줄 정의

**MCP(Model Context Protocol) 서버를 Claude Code에 붙여서 외부 시스템(Notion·Slack·DB·파일시스템·OS·디자인툴)과 데이터·시스템 레벨에서 직접 통신**시키는 운용 방식. CLI 협업(#17 — Claude Code↔Codex/Gemini/Grok)이 *명령어 레벨*이라면 MCP는 *데이터 레벨*. 둘이 짝이다.

## 왜 이 노하우가 중요한가

Claude Code는 강력하지만 **그 자체로는 "터미널 안에 갇힌 텍스트 에이전트"** 다. 파일 시스템과 셸은 직접 다루지만 그 외 — Notion 페이지에 무엇이 있는지, Slack 채널에 누가 무슨 말을 했는지, Postgres에 어떤 행이 있는지, Windows 알림창이 떠 있는지, Figma 시안이 어떤 모양인지 — 는 *모른다*. 매번 사용자가 복사해 붙여 넣어줘야 한다. 4,000시간을 굴리다 보면 이 "복붙 인계" 가 전체 작업 시간의 20~30%를 잡아먹는 게 보인다.

MCP는 이 가운데 단계를 *프로토콜로 자동화*한다. Anthropic이 2024년 11월 공개한 오픈 프로토콜로, **"AI는 클라이언트(Host) — 외부 시스템은 서버 — 사이의 통신 규약 하나로 통일"** 한다는 단순한 발상이다. 한 번 서버를 띄워두면 Claude Code는 그 서버가 노출한 *Tools / Resources / Prompts* 를 자기 도구처럼 호출한다. 사용자 개입 없이.

본인이 #17 멀티 CLI를 *수평적 협업*이라 부른다면 MCP는 *수직적 통합*이다. 같은 작업을 여러 AI에 분산하는 게 #17, 같은 AI를 여러 시스템에 연결하는 게 MCP. 30개 동시 운용에서 둘 다 빠지면 효율이 절반 이하로 떨어진다. 본인이 1인-AI로 ax-on.net·CPC·V50·SAL Grid를 동시에 굴릴 수 있는 기반의 절반은 MCP다.

또 하나 중요한 건 **MCP가 "내가 만들 수도 있다"** 는 점이다. 기성 서버만 갖다 붙이는 게 아니라 본인 도메인(예: SAL Grid 진행률 조회·CPC 에이전트 통신)을 위해 *전용 서버*를 직접 짜서 붙일 수 있다. 본인은 이미 cpc-channel을 자작 MCP 서버로 운용 중이다.

## 핵심 개념

### CLI 협업 vs MCP 협업 (가장 중요한 구분)

| 축 | CLI 협업 (#17) | MCP 협업 (#40) |
|---|---|---|
| 통신 단위 | 셸 명령어·표준 출력 | JSON-RPC 메시지 |
| 상대방 | 다른 CLI(Gemini/Codex/Grok) | 외부 시스템(Notion/Slack/DB/OS) |
| 관계 | 수평·동급 협업 | 수직·서비스 통합 |
| 비용 | 다른 CLI의 토큰 비용 | 서버 호출 비용(보통 무료·셀프호스팅) |
| 적합 작업 | 코드 생성·검증·교차 의견 | 데이터 조회·자동화·연동 |

→ 두 축이 직교한다. 한쪽으로 부족한 작업은 다른 쪽으로 채운다. 본인은 이 구분을 *4,000시간 동안 헷갈려서 손해 본 부분* 이라 본다 — Slack 자동화를 다른 CLI로 풀려고 한참 헤매다 MCP 한 줄로 끝난 적이 여러 번 있다.

### MCP의 3종 노출 자원

| 자원 | 무엇인가 | 예 |
|---|---|---|
| **Tools** | AI가 호출할 수 있는 함수 | `notion_search(query)`, `slack_post(channel, msg)` |
| **Resources** | AI가 읽을 수 있는 파일·URI | `notion://page/<id>`, `db://query/<sql>` |
| **Prompts** | 미리 등록된 프롬프트 템플릿 | `/review-pr`, `/triage-issue` |

가장 많이 쓰는 건 Tools. Resources는 RAG 형태의 컨텍스트 주입에 좋고, Prompts는 #39 Slash Commands의 *공유 가능한* 형태다.

### 본인 settings.json 등록 현황 (3개 서버 — 발췌. 그대로 복사 시 최상위 `{ ... }` 로 감싸야 유효 JSON)

```json
"mcpServers": {
  "windows-mcp": {
    "command": "uvx",
    "args": ["windows-mcp"]
  },
  "stitch": {
    "command": "npx",
    "args": ["-y", "@_davideast/stitch-mcp", "proxy"]
  },
  "cpc-channel": {
    "command": "bun",
    "args": ["run",
      "C:\\claude-project\\cpc-agent-server\\cpc-channel\\dist\\cpc-channel.js"]
  }
}
```

세 서버 모두 `mcpServers` 단일 키 아래에 등록한다. 성격은 셋이 모두 다르다 — 운영체제 / 디자인 / 자작 프로토콜.

| 서버 | 실행기 | 역할 | 등급 |
|---|---|---|---|
| **windows-mcp** | `uvx`(Python pkg runner) | Windows OS 자동화(파일·창·알림·키보드) | 기성 공개 서버 |
| **stitch** | `npx -y @_davideast/stitch-mcp` | 디자인 시스템·UI 시안 생성 프록시 | 기성 공개 서버 |
| **cpc-channel** | `bun run dist/cpc-channel.js` | CPC(Claude Platoons Control) 에이전트 간 통신 채널 | **본인 전용 자작 서버** |

cpc-channel은 본인 4,000시간 운용 중 *"30개 인스턴스가 서로 메시지를 주고받아야 하는데 표준 도구가 없다"* 는 한계를 뚫기 위해 직접 작성한 MCP 서버다. CPC 소대장-분대원 사이의 명령·보고·승인 메시지를 주고받는다. 기성 서버로 안 풀리면 직접 만든다 — 이게 본인이 `#40`을 강조하는 이유다.

### 등록 우선순위 — 기성 → 검증 → 자작

1. **기성 공개 서버 먼저** — Anthropic·커뮤니티가 만든 것 중 본인 작업 흐름에 맞는 것
2. **검증 후 글로벌 등록** — 1~2시간 굴려보고 안정성·토큰 소모·보안 점검
3. **빈 자리만 자작** — 기성에 없거나 본인 도메인 특화(SAL Grid·CPC·BuzzLab) 만 자작

이 순서를 어기면 *NIH(Not Invented Here) 함정* — 다 만들고 보니 이미 더 잘 만든 게 있더라 — 에 빠진다. 본인도 cpc-channel 만들기 전에 Slack MCP·discord-mcp 다 굴려보고 *그 어느 것도 인스턴스 간 1:1 메시지에 안 맞아서* 자작 결정한 것.

### 보안 — MCP의 가장 큰 함정

MCP 서버는 보통 *로컬에서 띄우지만* 그 도구가 호출되면 외부 API·파일시스템·DB로 나간다. **AI가 잘못된 인자로 호출 시 데이터 유출·삭제·과금 폭탄 모두 가능**. SKILL_ATLAS 사고 교훈을 그대로 적용하면 — *"MCP 도구가 Tool 200 OK라 해서 작동했다고 단정 금지"*. 호출 결과를 사용자가 한 번 더 확인할 수 있는 채널(로그 파일·Slack 알림)을 의무화한다.

본인 운용 규칙:
- 쓰기·삭제 도구는 #38 Hooks의 PreToolUse로 한 번 더 게이트
- DB 도구는 read-only DSN 별도 발급
- 결제·메일 발송 류 MCP는 *명시 승인 모드*에서만 활성화
- 자작 서버는 **테스트 모드 환경변수**(`CPC_MCP_DRYRUN=1`)를 기본값으로

## 실전 사용법

### 1단계 — 기성 서버 후보 발굴

`#28 외부 스킬·에이전트 발굴`과 동일 절차. 후보 출처:
- Anthropic 공식 — `modelcontextprotocol.io/servers`
- 커뮤니티 — `github.com/modelcontextprotocol/servers`, `mcp.so` 인덱스
- 본인 사용 도구 SDK가 MCP 서버 자체 제공하는지 (Notion·Linear·GitHub 등)

발굴 시 체크 4가지: ① 활발 유지보수 ② 인증 방식(API 키·OAuth) ③ 노출 도구 수(너무 많으면 컨텍스트 오염) ④ 토큰 단위 비용.

### 2단계 — 등록 (settings.json 또는 .claude.json)

본인 환경은 글로벌(`~/.claude.json`) 등록 + 프로젝트별 추가 패턴이다. 디자인 작업 비중이 큰 프로젝트는 stitch-mcp만 별도 활성화하는 식으로, 프로젝트 성격에 맞춰 일부만 켠다.

```json
"mcpServers": {
  "<별칭>": {
    "command": "<실행기>",
    "args": [...],
    "env": { "API_KEY": "..." }
  }
}
```

`env` 직접 노출은 위험. 본인은 OS 환경변수로 빼고 settings에는 `${ENV_VAR}` 참조하는 패턴 유지.

### 3단계 — Claude Code 재시작 후 등록 확인

```
/mcp
```

Claude Code 안에서 위 명령으로 활성 서버·노출 도구·연결 상태 확인. 도구 명은 보통 `<서버명>__<함수명>` 형식 — 본인 cpc-channel은 `cpc-channel__send_message`, `cpc-channel__list_squads` 같은 식.

### 4단계 — 첫 호출은 "탐색용 1건"

기성 서버 첫 사용 시 *부담 없는 read 도구 1번* 부터. 예) Notion MCP 등록했으면 첫 호출은 `search_pages("test")`. 이걸로 인증·응답 형태·에러 메시지 패턴까지 파악된 뒤에 쓰기 도구로 진입.

### 5단계 — 자작 서버 (필요 시)

기성 서버로 안 풀리는 본인 도메인 작업이 보이면 자작. 본인 cpc-channel 구조:

```
입력 → JSON-RPC 핸들러(@modelcontextprotocol/sdk)
     → 도구 라우터(send/recv/list)
     → Supabase 저장 + Vercel WebHook 알림
     → 응답
```

언어는 TypeScript(bun 실행) + `@modelcontextprotocol/sdk`. 첫 서버는 *3개 도구·2개 리소스* 정도가 적정 규모. 너무 많으면 Claude Code 컨텍스트가 도구 명세로만 5,000토큰 잡아먹는다.

### 6단계 — 통합 운용

| 작업 | 사용 패턴 |
|---|---|
| 슬라이드 작업 | stitch로 시안 생성 → Pillow(#15)로 마감 |
| Windows 자동화 | windows-mcp로 창·키보드 → 결과 스크린샷 #46으로 자율 검증 |
| CPC 30개 운용 | cpc-channel로 소대장↔분대원 메시지 → MBO(#10) Stage Gate |

→ MCP 서버 한 개씩은 약하다. **#15·#17·#27·#46과 결합될 때** 본인 운용의 진가가 나온다.

## 본인 운용 패턴

기성 3개(windows-mcp·stitch·notion 류) + 자작 1개(cpc-channel) 가 *현재 안정 구성*. 욕심내서 10개씩 붙이면 컨텍스트 오염으로 일반 코딩 작업이 느려진다 — *MCP 도구 명세도 토큰* 이라는 사실을 잊지 말 것.

자작 서버 첫 도전이라면 — 1) `npm create @modelcontextprotocol/server` 템플릿 시작 2) read 도구 1개부터 3) Claude Code에 붙여 손맛 확인 4) 그 다음 도구 추가. 한 번에 풀스택 짜지 말고 점진 확장.

자기 검증 금지 원칙은 MCP에도 적용 — 본인이 만든 자작 서버를 본인 Claude Code 인스턴스가 검증하면 안 된다. 별도 인스턴스(Verification Agent)가 호출 결과를 검증하도록.

## 관련 항목

- **#17 오케스트레이터 + 멀티 CLI** — 수평 협업, MCP의 짝
- **#27 Subagent vs Agent Teams** — 30개 인스턴스 통신 시 cpc-channel과 결합
- **#38 Hooks** — MCP 쓰기 도구 PreToolUse 가드
- **#39 Slash Commands** — MCP의 Prompts 자원과 보완 관계
- **#28 외부 스킬·에이전트 발굴** — 기성 서버 발굴 공통 절차
- **#15 SVG·스킬 자산화** — stitch MCP 결과의 후처리 자산화
- **#46 스크린샷 자율 검증** — windows-mcp 결과의 사용자 여정 검증
