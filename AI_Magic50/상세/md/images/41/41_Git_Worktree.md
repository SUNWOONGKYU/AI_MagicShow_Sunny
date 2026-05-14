---
id: 41
title: "Git Worktree로 병렬 브랜치 작업하기"
type: C
group_id: 5
group_name: "환경"
order_in_group: 7
created: 2026-05-06
sources:
  - "Sunny_AI_Magic_48개_종합정리.md #41"
  - "git worktree 공식 문서"
---

# 41. Git Worktree로 병렬 브랜치 작업하기

## 한 줄 정의

같은 저장소를 여러 폴더에 동시 체크아웃해 폴더마다 별도 Claude Code 인스턴스를 붙여 병렬 작업하는 **단일 머신 세로 확장**.

## 왜 이 노하우가 중요한가

본인 운용에서 확장은 두 축으로 굴러간다. **가로축**은 #5 — 5컴퓨터에 6개씩 30개 Claude Code를 붙이는 양적 확장이다. **세로축**은 worktree — 한 컴퓨터·한 저장소 안에서 브랜치를 폴더 단위로 분리해 동시에 굴리는 깊이 확장이다.

같은 저장소 한 폴더에서 브랜치를 자주 갈아타면 빌드 캐시·`node_modules`·임시 파일이 매번 무너진다. Claude Code 두 개를 붙이면 한쪽 작업 중 다른 쪽 `git checkout`이 파일을 덮어쓴다. worktree는 이 충돌을 **물리적으로** 분리한다. 폴더가 다르므로 캐시·인스턴스·파일이 섞이지 않는다.

특히 본인 SAL Grid 특허(10-2026-0009425) 작업처럼 **소대장 브랜치(메인)**와 **분대장 브랜치(실험)**를 동시에 굴려야 하는 상황에서 필수다.

## 핵심 개념

```bash
git worktree add ../<폴더명> <브랜치명>
git worktree list
git worktree remove ../<폴더명>
```

- `.git`은 메인 폴더에만 있고 worktree 폴더는 `.git` 파일(텍스트)이 메인을 가리킨다
- 같은 브랜치를 두 worktree에서 동시 체크아웃 불가 — 충돌 방지 설계
- `node_modules`·`dist`는 폴더별 독립 → 각 worktree마다 한 번씩 install
- VS Code·Claude Code 인스턴스를 폴더별로 따로 띄움

#5(가로 확장)와 비교:
| 항목 | #5 다대 컴퓨터 | #41 Worktree |
|------|----------------|--------------|
| 머신 수 | N대 | 1대 |
| 저장소 충돌 | 자연 분리 | 폴더로 분리 |
| 동기화 비용 | push/pull | 즉시 |
| 적합 작업 | 독립 프로젝트 30개 | 한 저장소 다중 브랜치 |

## 실전 사용법

**1단계** — 메인 폴더에서 `git worktree add ../proj-feat-A feature/A`로 worktree 생성. 폴더가 형제 위치에 만들어진다.

**2단계** — 새 폴더에서 Claude Code 신규 인스턴스 기동. `.claude/settings.json`은 메인과 별도로 둘 수 있어 모델·hooks를 worktree별로 다르게 설정 가능. 본인은 실험 worktree에 `Opus`, 메인에 `Sonnet`을 박아둔다.

**3단계** — `node_modules` 한 번 더 install. 이때 pnpm 같은 콘텐츠 어드레서블 패키지 매니저를 쓰면 디스크 비용 거의 0.

**4단계** — 작업 종료 시 `git worktree remove ../proj-feat-A`로 정리. 브랜치는 남고 폴더만 사라진다.

**본인 운용 패턴**: 메인(`main`) 1개 + 진행 중 분대장 worktree 3~4개 + hotfix worktree 1개. SAL Grid Stage Gate를 통과한 브랜치만 main worktree로 머지하고 나머지는 worktree에서 그대로 묻는다.

## 관련 항목

- **#5 5컴퓨터 30개 운용** — 가로 확장의 짝, worktree는 세로 확장
- **#9 군대 소대 편제** — worktree 1개 = 분대 작업 공간
- **#36 C드라이브 + G드라이브 백업** — worktree 폴더도 백업 대상에 포함
- **#43 --dangerously-skip-permissions** — worktree 인스턴스 자동화에 결합
