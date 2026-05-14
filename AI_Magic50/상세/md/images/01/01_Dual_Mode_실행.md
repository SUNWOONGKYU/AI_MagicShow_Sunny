---
id: 1
title: "Dual Mode 실행하기"
type: C
group_id: 2
group_name: "실행 프로세스"
order_in_group: 1
created: 2026-05-06
sources:
  - "AI_Magic50/Sunny_AI_Magic_48개_종합정리.md (#1)"
  - "본인 30개 동시 운용 패턴"
  - "~/.claude/CLAUDE.md (헌법)"
---

# 1. Dual Mode 실행하기

## 한 줄 정의

같은 한 가지 일을 **사고용 인스턴스**와 **실행용 인스턴스** 두 개로 동시에 굴려, 한쪽이 막히면 다른 쪽으로 즉시 넘어가는 본인 고유의 이중화 운용 패턴.

## 왜 이 노하우가 중요한가

Claude Code 한 인스턴스만 굴리면 두 가지 병목이 동시에 터진다. 첫째 **컨텍스트 오염** — 사고와 실행이 같은 윈도우에 쌓여 200k 채워지면 둘 다 죽는다. 둘째 **작업 단절** — 5h Rate Limit 또는 Compact가 발동하면 그 자리에서 멈춘다. 30개 동시 운용 4,000시간을 굴리며 도달한 결론은 단순하다. *"한 일은 두 인스턴스에 동시에 태운다."* 사고용은 Plan/브레인스토밍, 실행용은 Edit/Write/Bash. 한쪽이 Compact 들어가면 다른 쪽이 일을 계속 받는다. **#33 Claude 앱 vs Code**의 사고-실행 분리를 한 작업 단위 안에서 실현한 패턴이다.

## 핵심 개념

Dual Mode = (Plan Mode 인스턴스) + (Execute 인스턴스).

| 항목 | 사고 인스턴스 | 실행 인스턴스 |
|------|---------------|---------------|
| 모드 | Plan Mode (Shift+Tab×2) | 일반 모드 |
| 모델 | Opus | Sonnet (또는 Haiku) |
| 권한 | 읽기·분석만 | `--dangerously-skip-permissions` |
| 컨텍스트 | 길게 누적 | 짧게 끊고 재시작 |
| 산출물 | 계획서 MD | 실제 코드·파일 |

핵심은 **같은 자료를 양쪽에 공유**한다는 점. PHASE 파일·MBO 목표서·SAL Grid Stage 카드를 양쪽이 동일하게 Read한다. 사고 인스턴스가 결정한 다음 Task만 실행 인스턴스에 던진다.

## 실전 사용법

**1단계** — 작업 시작 전 PHASE 파일을 만들어 양쪽이 같은 진실 소스를 본다 (`zz_KingFolder/_TalkTodoPlan/YYYY_MM_DD__HH.MM_PHASE_*.md`).

**2단계** — 사고 인스턴스에 Plan Mode로 진입시켜 *"이 PHASE의 Task를 #N번 단위로 분해해라"* 지시. 결과는 MD로 저장.

**3단계** — 실행 인스턴스는 `--dangerously-skip-permissions` + Sonnet으로 띄우고, 사고 인스턴스가 만든 Task 카드만 받아 실행. 끝나면 결과를 사고 인스턴스에 다시 던져 다음 Task를 받는다.

**4단계** — 한쪽이 Rate Limit·Compact에 걸리면 즉시 다른 쪽이 그 일을 흡수. 사고 인스턴스가 죽으면 실행 인스턴스를 일시 사고 모드로 전환. 반대도 동일.

**5단계** — 본인 운용 KPI: *Task 완료까지 단절 0회*, *컨텍스트 80% 도달 시 즉시 측 전환*. **#48 HUD**의 LINE2 막대로 양쪽 컨텍스트를 동시에 본다.

**주의** — Task Agent ≠ Verification Agent 원칙(글로벌 헌법). 사고 인스턴스가 자기 Task를 자기가 검증하면 안 된다. 검증은 **#46 스크린샷 자율 검증** 별도 트랙에서 수행.

## 관련 항목

- **#33 Claude 앱 vs Code** — 사고-실행 분리 사상의 상위 버전
- **#34 Plan Mode** — 사고 인스턴스의 핵심 도구
- **#41 Git Worktree** — 두 인스턴스의 작업 폴더 분리
- **#5 5컴퓨터 30개 운용** — Dual Mode를 가로 확장한 형태
- **#26 1개 AI Multi Role** — Dual Mode의 단일 인스턴스 변형
