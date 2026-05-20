---
id: 11
title: "Hooks 활용하기"
subtitle: "사용자 명령 없이 자동 발동되는 강제 실행 레이어"
type: B
group_id: 2
group_name: "실행 프로세스"
order_in_group: 7
created: 2026-05-06
sources:
  - "~/.claude/settings.json hooks 6 events"
  - "~/.claude/hooks/ (skill-trigger.js, hook-logger.js, buzzlab-team-name-guard.js, export-session-to-wiki.js)"
  - "AI_Magic50/Sunny_AI_Magic_48개_종합정리.md (#38)"
  - "Anthropic Claude Code Hooks 공식 문서"
---

# 11. Hooks 활용하기

## 한 줄 정의

**Claude Code의 훅 이벤트(공식 문서 기준 29개 이상, 본인이 활용하는 핵심 6개: UserPromptSubmit · PreToolUse · PostToolUse · Stop · SessionStart · PreCompact) 에 본인 노드 스크립트를 박아 넣어, 사용자 명령 없이 자동으로 발동되는 가드레일·로그·자산화 파이프라인을 깔아두는 것**. 품질관리·보안 가드·세션 백업 같은 *"매번 해야 하지만 사람이 깜빡하는 일"* 을 하네스(harness)가 강제 실행하게 만드는 자동화의 골격.

## 왜 이 노하우가 중요한가

본인 글로벌 CLAUDE.md에 박혀 있는 핵심 원칙 — *"자동 행동(automated behaviors)은 LLM이 아닌 하네스(harness)가 settings.json hooks로 실행한다"*. 이유는 단순하다. AI에게 *"이거 매번 해줘"* 라고 부탁하면 절반은 까먹고, 컨텍스트가 차면 잊고, 다른 슬롯으로 넘어가면 사라진다. **AI 자체에 의존하지 않는 강제 실행 레이어**가 필요하다.

훅이 없으면 어떻게 되는가. (1) 30개 동시 운용에서 어느 슬롯이 무슨 작업을 했는지 추적 불가, (2) 위험 명령(파일 삭제·force push) 이 어느 슬롯에서 들어올지 모름, (3) 컨텍스트 압축 직전 작업 내용이 사라짐. 본인이 수많은 슬롯을 굴리면서 깨달은 사실은 *"AI에게 자기 검증을 시키면 안 된다"* — 별도 레이어가 필요하다. 훅이 그 레이어다.

또 하나 — **#35(`--dangerously-skip-permissions`)와의 짝**. 모든 승인 단계를 건너뛰는 위험한 옵션을 쓰는 이유는 30개 운용에서 매번 승인 클릭이 불가능하기 때문이다. 그 위험은 **PreToolUse 훅이 위험 명령을 사전 차단**해서 상쇄한다. 훅 없이 `--dangerously-skip-permissions` 만 쓰면 자살, 훅과 함께 쓰면 사실상 안전. 이 짝이 #31(30개 운용)·#14(소대 편제)·#10(헤드리스) 같은 대규모 자동화의 진짜 인프라다.

훅의 본질은 **"품질관리·보안·기록을 사용자 명령 없이 강제 발동시키는 도구"**. #28 4종 품질관리 스킬을 자동화로 격상시키는 도구이기도 하다.

## 핵심 개념

### 본인이 활용하는 6개 핵심 훅 이벤트와 발동 시점

| 이벤트 | 발동 시점 | 본인 활용 |
|--------|-----------|----------|
| **UserPromptSubmit** | 사용자가 프롬프트 보낼 때마다 | skill-trigger.js + hook-logger.js |
| **PreToolUse** | 도구 호출 직전 | buzzlab-team-name-guard.js (Agent matcher) + hook-logger.js |
| **PostToolUse** | 도구 호출 직후 | hook-logger.js |
| **Stop** | 응답 종료 시점 | hook-logger.js |
| **SessionStart** | 세션 시작 시점 | hook-logger.js |
| **PreCompact** | 컨텍스트 압축 직전 | export-session-to-wiki.js + hook-logger.js |

본인 settings.json 핵심 구성(요약 — `"hooks": { ... }` 객체 내부의 발췌. 그대로 복사 시 외부 중괄호와 `"hooks":` 키를 감싸야 작동):

```json
"UserPromptSubmit": [{ "hooks": [
  {"command": "node hooks/skill-trigger.js"},
  {"command": "node hooks/hook-logger.js UserPromptSubmit"}
]}],
"PreToolUse": [
  {"matcher": "Agent", "hooks": [{"command": "node hooks/buzzlab-team-name-guard.js"}]},
  {"hooks": [{"command": "node hooks/hook-logger.js PreToolUse"}]}
],
"PreCompact": [{ "hooks": [
  {"command": "node hooks/export-session-to-wiki.js"},
  {"command": "node hooks/hook-logger.js PreCompact"}
]}]
```

### 본인 훅 4개 — 각자의 역할

**1. skill-trigger.js (UserPromptSubmit)**

사용자 프롬프트에서 키워드를 감지해 자동으로 적절한 스킬을 호출 컨텍스트에 주입. 예 — *"S2 실행"* 키워드 → 청룡-sal-grid-dev 스킬 + mbo-코어5 스킬 자동 발동. 사용자가 *"청룡 써"* 라고 말하지 않아도 발동된다.

**2. buzzlab-team-name-guard.js (PreToolUse, matcher=Agent)**

서브에이전트 호출 시 팀명·역할명이 본인 표준(백호·청룡·주작·현무 — 사신 체계)을 벗어나면 차단. *"임의의 작명 금지"* — 표준 팀명만 허용해서 30개 운용에서도 일관성 유지.

**3. hook-logger.js (모든 이벤트)**

6개 이벤트 전부에 박아 둔 통합 로거. 어느 슬롯에서 언제 무슨 일이 일어났는지 단일 로그 파일에 기록. 30개 운용에서 사후 추적의 단일 진실 원천.

**4. export-session-to-wiki.js (PreCompact)**

컨텍스트 압축 직전 자동 발동. 현재 세션 핵심 내용을 `G:\내 드라이브\Claude-Wiki\` Obsidian 볼트로 추출 → MD 파일 생성. 압축 후에도 작업 흐름이 사라지지 않는다. #17(컨텍스트 관리) 의 진짜 안전망.

### Matcher 패턴 (PreToolUse·PostToolUse 전용)

특정 도구에만 적용 가능. 본인 사례 — `"matcher": "Agent"` 는 서브에이전트 호출 도구에만 가드 발동. 다른 패턴 예시:

| Matcher | 적용 |
|---------|------|
| `"Agent"` | 서브에이전트 호출 |
| `"Bash"` | 셸 명령 |
| `"Write|Edit"` | 파일 쓰기 |
| `".*"` (또는 생략) | 모든 도구 |

위험 명령 가드는 보통 `"Bash"` matcher 에 박는다 — `rm -rf` · `git push --force` · `git reset --hard` 정규식 매칭 시 즉시 차단.

### 훅 종료 코드 = 차단 명령

훅 스크립트가 **종료 코드 2** 로 끝나면 도구 실행이 차단된다. PreToolUse 가드의 핵심 메커니즘:

```javascript
// buzzlab-team-name-guard.js 패턴
if (illegalTeamName) {
  console.error("팀명 표준 위반: 사신 체계만 허용");
  process.exit(2);  // 차단
}
process.exit(0);  // 통과
```

훅이 stderr에 출력하는 메시지는 AI에게도 전달돼서, 차단 사유를 알고 다음 시도에 반영할 수 있다.

## 실전 사용법

### #28 4종 품질관리를 훅으로 자동화

본인 운용 — 특정 디렉토리에서 .md/.html 저장 시 PostToolUse 에서 review-evaluate-코어1 자동 발동.

```json
{
  "PostToolUse": [{
    "matcher": "Write|Edit",
    "hooks": [{ "type": "command",
      "command": "node hooks/auto-quality-check.js"
    }]
  }]
}
```

`auto-quality-check.js` 가 파일 경로·크기를 보고 *"품질 검토 필요"* 판정 시 stderr 메시지로 *"/review-evaluate 실행 권장"* 출력. AI가 다음 응답에서 자동 발동.

### 사례 — PreCompact 자동 백업

본인 가장 많이 쓰는 활용. 컨텍스트가 거의 찼을 때 압축이 자동 발동되는데, 압축되면 초반 대화가 요약돼서 사라진다. PreCompact 훅이 *직전에* 발동돼서 핵심 흐름을 Wiki로 빼낸다.

```javascript
// export-session-to-wiki.js 핵심
const { session_id, transcript_path, cwd } = JSON.parse(stdin);
const summary = extractKeyContext(transcript_path);  // 결정사항·산출물 경로·KPI
const slotName = path.basename(cwd);                  // 작업 폴더명을 슬롯 식별자로
const filename = `${date}__${time}_세션백업_${slotName}.md`;
fs.writeFileSync(`G:/내 드라이브/Claude-Wiki/세션백업/${filename}`, summary);
```

다음 세션에서 그 MD 파일 한 번 Read 하면 흐름 복원. #19(`/resume`) 보다 안정적.

### KPI 검증 (양 레이어)

훅 자체에도 KPI 강제. 본인 점검표:

| 레이어 | KPI |
|--------|-----|
| 데이터 | 6개 이벤트 전부 hook-logger 기록 — 30일 누락 0건 |
| 사용자 여정 | PreToolUse 가드가 실제로 위험 명령 차단 (월 1회 의도적 테스트) |

*"훅 등록됐다"* 는 데이터 레이어 KPI. 실제로 차단 작동하는지 테스트해야 사용자 여정 KPI 통과 — Task Agent 결과를 자기가 검증하지 말 것.

### 자주 만나는 함정

| 증상 | 원인 | 해결 |
|------|------|------|
| 훅이 안 발동 | settings.json 경로 오타 | 절대경로·따옴표 확인 |
| 모든 명령이 차단됨 | exit 코드 잘못 | exit(0)이 통과, exit(2)가 차단 |
| 한글 stderr 깨짐 | Windows 콘솔 인코딩 | `process.stderr.write(buf)` UTF-8 명시 |
| 훅이 너무 느림 | 무거운 작업 동기 처리 | 비동기로 큐에 넣고 즉시 종료 |

## 본인 운용 패턴

훅은 **한 번 박으면 영원히 작동**하는 자산이라, 새 PC 셋업할 때 settings.json + hooks/ 폴더 통째로 복사하는 게 30분 안에 끝난다. 본인 누적 운용의 단단한 자산 중 하나.

새 위험 패턴이 발견될 때마다 PreToolUse 가드에 룰 추가, 새 자동화가 필요할 때마다 훅 스크립트 추가. 결과적으로 6개 이벤트 슬롯이 본인 운용의 *"항상 작동하는 백그라운드 직원들"* 역할을 한다.

#35(`--dangerously-skip-permissions`)과 짝으로만 쓴다. 단독 사용은 자살, 짝으로 쓰면 30개 슬롯이 안전하게 자율 실행된다.

## 관련 항목

- **#35 `--dangerously-skip-permissions`** — 훅 가드레일과 짝
- **#33 CLAUDE.md** — 자동 행동 규칙의 명시적 선언, 훅이 그 실행자
- **#17 컨텍스트 관리** — PreCompact 훅이 #17의 진짜 안전망
- **#28 4종 품질관리** — PostToolUse 훅으로 자동 발동 격상
- **#10 헤드리스 모드** — 훅 + 헤드리스가 진짜 자동화 인프라
- **#18 Slash Commands** — 사용자 명령 압축 vs 훅의 자동 발동 (서로 보완)
