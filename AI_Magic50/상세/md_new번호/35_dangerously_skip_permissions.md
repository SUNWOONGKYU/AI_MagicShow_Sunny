---
id: 35
title: "--dangerously-skip-permissions와 Hooks 가드레일 결합"
subtitle: "승인 자동 yes + Hooks PreToolUse 가드, 속도와 안전을 동시에 잡기"
type: C
group_id: 5
group_name: "환경"
order_in_group: 5
created: 2026-05-06
sources:
  - "Sunny_AI_Magic_48개_종합정리.md #43"
  - "claude --help"
  - "~/.claude/hooks/ (PreToolUse 가드)"
---

# 35. `--dangerously-skip-permissions` 활용하기

## 한 줄 정의

모든 도구 승인 단계를 건너뛰는 옵션 — 속도를 위해 안전을 버리는 것이 아니라, **#11 Hooks의 PreToolUse 가드레일과 결합**해 속도와 안전을 동시에 잡는 운용법.

## 왜 이 노하우가 중요한가

대화형 모드에서 `Bash`·`Edit`·`Write` 마다 매번 승인 버튼을 눌러야 한다면 #31(30개 운용)·#14(소대 편제)·#10(헤드리스)는 굴러가지 않는다. `--dangerously-skip-permissions`는 그 승인을 모두 자동 yes로 만든다.

이름 그대로 위험하다. 승인 없이 `rm -rf /`도 실행될 수 있다. 그러나 본인은 이 옵션을 **#11 Hooks의 PreToolUse 가드와 짝지어** 쓴다. 승인 단계를 사람이 막는 게 아니라 코드가 막는다. 사람이 30번 yes 누르는 시간이 0이 되고, 위험 명령은 hook이 차단한다.

이 결합이 없으면 30개 동시 운용은 불가능하다.

## 핵심 개념

```bash
claude --dangerously-skip-permissions
claude -p "..." --dangerously-skip-permissions   # 헤드리스와 결합
```

PreToolUse hook 가드 패턴(`~/.claude/settings.json` — #11과 동일 형식):
```json
"hooks": {
  "PreToolUse": [{
    "matcher": "Bash",
    "hooks": [{
      "type": "command",
      "command": "node ~/.claude/hooks/bash-guard.js"
    }]
  }]
}
```

`bash-guard.js`가 차단해야 할 패턴 — **이 글은 분석 목적, 가드 강화 권고**:
- `rm -rf /`, `rm -rf ~`, `rm -rf $HOME`
- `git push --force` to `main`/`master`
- `chmod 777`, `curl … | sh` 같은 무인 셸 실행
- `.env`·`*.key`·`*.pem` 삭제·전송

차단 시 hook이 비-0 종료 코드로 도구 실행을 막는다. 사용자 승인이 없어도 위험은 hook 단에서 죽는다.

## 실전 사용법

**1단계** — 단독으로는 절대 쓰지 않는다. 먼저 `~/.claude/hooks/bash-guard.js`·`write-guard.js` 두 가드를 settings.json에 등록한다.

**2단계** — 가드 발동 테스트. `claude -p "rm -rf ~/test-folder"`를 일부러 시켜보고 hook이 차단해 도구가 실행되지 않는지 확인. 차단 안 되면 가드를 못 믿는다.

**3단계** — 30개 인스턴스 또는 헤드리스 크론에 `--dangerously-skip-permissions` 적용. 승인 멈춤이 사라져 실제 throughput이 본인 측정으로 약 3~5배 상승.

**4단계** — 위험도 레벨링. 메인 저장소·운영 서버 작업은 `--dangerously-skip-permissions` **금지**. 격리된 worktree(#37)·임시 폴더·docker 컨테이너 안에서만 허용한다.

**자기 검증 금지 원칙**: hook이 통과시킨 명령이 결과적으로 잘못 동작했더라도, 그것을 같은 인스턴스가 "괜찮았다"고 판정하면 안 된다. **별도 Verification Agent**(#29)가 결과물을 검증한다.

## 관련 항목

- **#11 Hooks** — PreToolUse 가드의 본체. 짝
- **#10 헤드리스 모드 자동화** — 무인 실행의 필수 조합
- **#31 5컴퓨터 30개 운용** — 이 옵션 없이는 운용 자체 불가
- **#37 Git Worktree** — 격리 폴더에서 안전하게 사용
- **#14 군대 소대 편제** — 분대원 인스턴스가 이 옵션으로 굴러감
