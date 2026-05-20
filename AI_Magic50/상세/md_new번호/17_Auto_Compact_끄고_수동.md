---
id: 17
title: "컨텍스트 관리 — 모니터링·수동 Compact·자동 저장의 3종 세트"
subtitle: "HUD 모니터링 + 수동 Compact + 직전 자동 저장 3종 세트로 정보 손실 0"
type: C
group_id: 3
group_name: "실행 방법"
order_in_group: 4
created: 2026-05-06
sources:
  - "AI_Magic50/Sunny_AI_Magic_48개_종합정리.md (#30)"
  - "~/.claude/my-statusline.sh"
  - "~/.claude/settings.json (PreCompact hook)"
  - "Claude-Wiki/skill-atlas/wiki/2026_05_06__06.29_세션내용_익스포트.md (외 5건 — PreCompact hook 자동 export: session_id / transcript_path / cwd / hook_event_name 메타 보존)"
---

# 17. 컨텍스트 관리 — 모니터링·수동 Compact·자동 저장의 3종 세트

## 한 줄 정의

Auto Compact를 끄고 **HUD 모니터링 + 수동 Compact + Compact 직전 자동 저장** 세 가지를 묶어 운용하는 본인 표준 컨텍스트 관리법. 30개 동시 운용 시 정보 손실을 0으로 만드는 기본기.

## 왜 이 노하우가 중요한가

Auto Compact는 편한 대신 **언제 어디서 무엇이 잘렸는지 사용자가 모른다**. 누적 운용 결과, 자동으로 잘린 시점 직후의 응답이 갑자기 맥락을 잃는 사례가 반복됐다. 다인스턴스 운용 환경에서는 한 인스턴스의 정보 손실이 다른 분대원에게 잘못 인계되며 연쇄 오류로 번진다.

수동 Compact + 사전 저장으로 바꾸면 (1) **언제 잘릴지 사용자가 결정**하고 (2) **잘리기 직전 상태가 디스크에 남아** /resume(#19)·다음 인스턴스로 깨끗하게 인계된다.

## 핵심 개념

3종 세트 구성:

| 요소 | 도구 | 역할 |
|------|------|------|
| 모니터링 | #36 HUD LINE2 막대그래프 | 컨텍스트 % 실시간 가시화 |
| 수동 Compact | `/compact` 슬래시 명령 | 사용자 시점 결정 |
| 자동 저장 | settings.json `PreCompact` hook | Compact 직전 transcript·요약 디스크 백업 |

판단 임계값(본인 운용):
- **70%**: 작업 마무리 단계 진입 신호
- **80%**: HUD가 빨강 — 즉시 `/compact` 또는 세션 분할 결정
- **90%**: 비상. 진행 중 도구 호출 1개만 더 받고 강제 정리

## 실전 사용법

**1단계** — `~/.claude/settings.json`에서 Auto Compact 비활성화. 동시에 PreCompact hook 등록해 transcript JSONL과 마지막 요약을 `~/.claude/compacts/<session>_<timestamp>.md`로 저장.

**2단계** — #36 HUD LINE2 막대그래프 상시 확인. 30개 인스턴스 한 화면에 띄울 때 LINE2만 훑으면 어느 인스턴스를 우선 처리할지 즉시 보인다.

**3단계** — 70% 도달 시 **인계 노트** 작성을 AI에 지시. "지금까지 한 일 / 다음에 할 일 / 미해결 이슈" 3블록.

**4단계** — `/compact <추가 지시문>` 실행. 이때 본인은 *"인계 노트 경로와 미해결 이슈 보존"* 같은 지시문을 함께 넣어 핵심 컨텍스트를 살린다.

**5단계** — 장기 작업은 **세션 분할**. SAL Grid Stage 단위로 인스턴스를 새로 띄우고 인계 노트로 이어받는다. /resume(#19)은 비상용일 뿐, 평상시 컨텍스트 운용은 #17에 의존.

**금지 사항**: 80% 넘긴 채 새 도구 호출 연발 — Task Agent ≠ Verification Agent 원칙이 무너진다. 검증은 새 인스턴스에 맡겨야 자기검증 함정을 피한다.

> Vault 사례: `skill-atlas/wiki/2026_05_06__06.29_세션내용_익스포트.md` 외 5건의 *세션내용_익스포트* 노트는 PreCompact hook이 발동했을 때 세션 메타(session_id / transcript_path / cwd / hook_event_name: PreCompact / trigger: manual)를 자동 저장한 실제 산출물이다. #17 4단계 *"`/compact`에 인계 노트 경로와 미해결 이슈 보존 지시문 함께"* 가 사람의 의식적 행동이라면, 이 자동 export는 *3단계(자동 저장)*의 백그라운드 안전망 — 본인이 인계 노트 작성을 깜빡해도 transcript 자체는 무조건 Vault로 백업된다. PreCompact 훅(#11) + 세션 백업이 #17의 마지막 안전선임을 보여주는 노트군.

## 관련 항목

- **#36 Statusline HUD** — LINE2 막대그래프가 #17의 모니터링 도구
- **#19 /resume 세션 재개** — 비상용. 평상시 운용은 #17이 우선
- **#11 Hooks** — PreCompact hook이 자동 저장의 실행 메커니즘
- **#31 5컴퓨터 30개 운용** — 30개 인스턴스 정보 손실 방지의 기본기
- **#14 군대 소대 편제** — 분대원 간 인계 노트 표준화
