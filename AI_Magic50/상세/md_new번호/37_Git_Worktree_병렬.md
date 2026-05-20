---
id: 37
title: "Git 브랜치·Worktree로 여럿이 같은 저장소 동시 작업하기"
subtitle: "여러 사람·AI가 한 저장소를 동시에 사용해도 서로의 작업을 덮어쓰지 않는 협업체계"
type: C
group_id: 5
group_name: "환경"
order_in_group: 7
created: 2026-05-06
sources:
  - "Sunny_AI_Magic_48개_종합정리.md #41"
  - "git worktree 공식 문서"
---

# 37. Git 브랜치·Worktree로 여럿이 같은 저장소 동시 작업하기

## 한 줄 정의

같은 저장소를 **여러 사람(또는 여러 AI 인스턴스)이 동시에 만져도 서로의 작업을 덮어쓰지 않게** 만드는 Git 협업 골격. 기본은 **브랜치**로 작업을 분리하고, 한 사람이 여러 브랜치를 동시에 봐야 할 때는 **worktree**로 폴더까지 분리한다. 머지 시점에만 합친다.

## 왜 이 노하우가 중요한가

두 사람이 같은 저장소를 동시에 만진다고 해보자. 둘이 같은 폴더·같은 브랜치에서 일하면 파일 덮어쓰기, 커밋 충돌, 리베이스 지옥이 줄줄이 따라온다. Git이 협업 도구가 된 이유 자체가 **"각자 자기 브랜치에서 일하고, 머지 시점에만 합친다"**라는 규칙이다.

브랜치만으로 충분한 경우가 대부분이다 — A는 `feature/login` 폴더에서, B는 `feature/payment` 폴더에서 일하면 끝이다. 그런데 한 사람이 **여러 브랜치를 동시에 들여다봐야 하는 순간**이 온다. 본인이 자기 작업 브랜치를 굴리는 중에 동료 PR을 리뷰해야 한다거나, hotfix 브랜치를 잠깐 띄워 긴급 수정을 해야 한다거나. 이때 한 폴더에서 `git checkout`으로 브랜치를 갈아타면 **node_modules·빌드 캐시·임시 파일이 매번 무너진다**. Claude Code 인스턴스를 두 개 띄워두면 한쪽 작업 중 다른 쪽 checkout이 파일을 덮어쓴다.

worktree는 이 문제를 **물리적으로** 분리한다. 같은 저장소를 여러 폴더에 동시 체크아웃해 폴더마다 다른 브랜치를 띄운다. 폴더가 다르므로 캐시·node_modules·인스턴스가 섞이지 않는다.

AI 협업 시대엔 이 그림이 더 중요해진다. **AI 인스턴스도 "사람 1명"으로 취급**해 각자 자기 브랜치를 받아 PR을 보내게 만들면, 사람 2~3명 + AI 5~10명이 한 저장소를 동시에 굴리는 협업이 가능해진다. 이때 worktree는 각 AI에게 독립 작업 폴더를 깔아주는 인프라가 된다.

## 핵심 개념

### 협업의 기본 — 브랜치로 작업 분리

```bash
git checkout -b feature/login          # A의 브랜치
# 작업 후
git push origin feature/login
# PR 생성 → 리뷰 → 머지

git checkout -b feature/payment        # B의 브랜치 (다른 사람·다른 폴더 가능)
```

여러 사람·여러 AI가 동시에 일해도 각자 자기 브랜치만 만지면 충돌은 머지 시점에만 발생한다. 그 시점은 PR 리뷰로 통제된다.

### 한 사람이 여러 브랜치를 동시에 — Worktree

```bash
git worktree add ../proj-review-PR-42 feature/review-target   # PR 리뷰용
git worktree add ../proj-hotfix       hotfix/urgent           # hotfix용
git worktree list
git worktree remove ../proj-review-PR-42                       # 정리
```

- 메인 저장소는 그대로 유지, 형제 폴더에 다른 브랜치 체크아웃
- 폴더마다 VS Code·Claude Code 인스턴스를 따로 띄움
- 같은 브랜치를 두 worktree에서 동시 체크아웃은 불가 (Git이 막아줌)
- `.git` 본체는 메인 폴더에만 있고, worktree 폴더의 `.git`은 텍스트 파일 (메인을 가리킴)
- `node_modules`·`dist`는 폴더별 독립 → 각 worktree마다 한 번씩 install (pnpm 쓰면 디스크 비용 거의 0)

### 협업 시나리오별 도구 선택

| 시나리오 | 도구 |
|---|---|
| 여러 사람이 각자 자기 작업만 한다 | 브랜치만 |
| 사람 A가 자기 작업 중 사람 B의 PR을 리뷰해야 한다 | A 머신에서 worktree 추가 |
| Hotfix가 들어왔는데 본인 작업을 멈출 수 없다 | hotfix 브랜치 + worktree |
| 같은 저장소를 사람 2~3명 + AI 5~10명이 동시에 굴린다 | 각자 브랜치 + 필요 시 worktree |
| 한 AI에게 두 브랜치를 비교 분석시킨다 | worktree 두 개 |

### 협업 흐름

```
각자 브랜치에서 작업
  ↓
push → PR 생성
  ↓
다른 사람·AI가 리뷰 (필요 시 worktree로 PR 브랜치 체크아웃)
  ↓
승인 후 main에 머지
  ↓
다음 브랜치 시작
```

## 실전 사용법

**1단계** — 팀 규칙 합의. 브랜치 명명 규칙(`feature/`, `fix/`, `hotfix/`), PR 리뷰어 수 최소치, main 직접 push 금지 등. 이게 없으면 worktree 깔아봐야 무너진다.

**2단계** — 각 협업자(사람·AI)가 자기 브랜치를 만들어 작업. 다른 사람 브랜치는 건드리지 않는다. 충돌 위험이 있는 파일을 둘 다 만져야 하는 경우엔 미리 협의.

**3단계** — PR 리뷰가 본인 작업과 겹치는 시점에 worktree 추가.
```bash
git worktree add ../proj-review feature/팀원-A-PR
cd ../proj-review
code .   # 또는 claude code
```
리뷰 끝나면 `git worktree remove`. 본인 메인 작업 폴더는 그대로 살아 있음.

**4단계** — AI 인스턴스에 브랜치 배정. AI 분대원에게 *"`feature/login-form` 브랜치에서 작업해 PR 올려"* 라고 지시. AI는 그 브랜치에서 자율 작업 후 PR 생성. 사람은 PR만 본다. 같은 저장소에 AI 인스턴스 5~10개가 각자 다른 브랜치에서 PR을 만들어 보내는 흐름이 가능해진다.

**5단계** — worktree 정리. 작업 끝난 worktree는 `git worktree remove`로 삭제. 브랜치는 남고 폴더만 사라진다. 폴더가 쌓이면 어느 게 활성인지 헷갈리니 주기적 정리 필수.

**충돌 발생 시** — `git pull --rebase` 또는 PR에서 직접 리졸브. worktree는 충돌 자체를 줄이지 못한다. 같은 파일을 두 사람이 만지면 결국 머지 시점에 풀어야 한다. worktree의 가치는 **동시 작업 중에 환경이 무너지지 않게 하는 것**이지 머지 충돌 자체를 없애는 게 아니다.

## 본인 운용 패턴

본인 환경에서는 같은 저장소에 사람 1명(본인) + AI 인스턴스 3~5명이 동시 작업하는 경우가 많다. 각 AI에게 브랜치 1개씩 배정하고, 본인은 main worktree에서 작업하면서 필요할 때 worktree를 추가해 AI PR을 리뷰한다. 리뷰 끝난 worktree는 즉시 정리. AI가 자율 작업 중 본인이 다른 AI를 도와주려고 폴더를 옮겨도 본인 main 작업이 무너지지 않는다.

같은 저장소에 동시에 살아 있는 폴더는 보통 **main 1개 + 진행 중 PR 리뷰용 1~2개 + hotfix가 들어오면 1개** 정도. 5개를 넘기면 어느 게 어느 작업인지 본인이 잊는다. 적정 수는 사람 인지 한도와 같다.

## 관련 항목

- **#31 5컴퓨터 30개 동시 운용** — 저장소가 여러 개일 때의 확장. worktree는 한 저장소 안 협업
- **#14 군대 소대 편제** — AI 분대원에게 브랜치 1개씩 배정하는 협업 단위
- **#40 C드라이브 + G드라이브 백업** — worktree 폴더도 백업 대상
- **#35 --dangerously-skip-permissions** — AI 인스턴스가 worktree 안에서 자동 작업할 때 가드와 결합
- **#11 Hooks** — 브랜치 보호·PR 검증 hook과 결합
