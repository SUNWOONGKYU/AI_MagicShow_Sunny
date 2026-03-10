# SAL Grid Dev — 감어인 Cloud 프로젝트 계획서

> 방법론: SAL Grid Dev Suite V3.1
> 프로젝트: 감어인 Cloud (기록관리 SaaS 플랫폼)
> 작성일: 2026-03-10
> 좌표계: Stage(S0~S7) × Area(FE/BE/DB/AI/INF/QA) × Level(L1~L3)

---

## ■ PART 2-P1 — 사업계획 (Business Plan)

### 프로젝트 정의

| 항목 | 내용 |
|------|------|
| **프로젝트명** | 감어인 Cloud — 기록관리 SaaS 플랫폼 |
| **목적** | 기존 설치형 감어인 5종을 클라우드 통합 플랫폼으로 전환 |
| **핵심 가치** | AI 자동화 + SaaS 구독 + 지식베이스 = 기록관리 디지털 전환 |
| **타겟** | 대학·재단·공공기관·기업 아카이브 담당자 |
| **수익 모델** | 월정액 SaaS (Starter 30만 / Pro 150만 / Enterprise 커스텀) |

### 핵심 성과 지표 (KPI)

| KPI | 목표 (1년) | 목표 (3년) |
|-----|-----------|-----------|
| 가입 기관 수 | 30개 | 200개 |
| MRR (월 반복 매출) | 3,000만원 | 2억원 |
| AI 처리 기록 수 | 10만건/월 | 100만건/월 |
| 고객 만족도 NPS | 40+ | 60+ |

---

## ■ PART 2-P2 — 프로젝트 기획 (Project Plan)

### Stage 구성 (동적 Stage: S0~S7)

| Stage | 명칭 | 기간 | 목표 |
|-------|------|------|------|
| **S0** | 기반 설계 | 1개월 | 아키텍처·DB·API 설계 완료 |
| **S1** | 인증/인프라 | 1개월 | 멀티 테넌트·인증·구독 시스템 |
| **S2** | 기록 관리 핵심 | 2개월 | 기록 CRUD·분류·검색 (감어인R+M 통합) |
| **S3** | AI 자동화 | 1.5개월 | OCR 메타데이터 추출 + 구술 전사 |
| **S4** | 지식베이스 | 1개월 | RAG 어시스턴트 + 컨설팅 사례 검색 |
| **S5** | 아카이브 포털 | 1.5개월 | 공개 타임라인·전시·검색 포털 |
| **S6** | IoT 서고 | 1개월 | 환경 센서 모니터링 대시보드 |
| **S7** | 배포/론칭 | 1개월 | CSAP 준비·성능 최적화·론칭 |

**총 개발 기간: 약 10개월 (MVP: S0~S3 = 5.5개월)**

### Area 정의

| Area | 설명 |
|------|------|
| **FE** | Frontend (React + TypeScript + Tailwind) |
| **BE** | Backend (FastAPI + Python) |
| **DB** | Database (PostgreSQL + pgvector) |
| **AI** | AI/ML (LLM·OCR·STT 연동) |
| **INF** | Infrastructure (Docker·AWS·CI/CD) |
| **QA** | 품질보증 (테스트·검증) |

---

## ■ PART 3 — TASK_PLAN (SAL Grid 전체 매트릭스)

> SAL ID 형식: `S{stage}.{AREA}.{번호}`
> 상태: PLAN / TODO / IN_PROG / DONE
> 우선순위: P1(필수) / P2(중요) / P3(선택)

---

### S0 — 기반 설계

| SAL_ID | Task명 | Area | Level | 우선순위 | 상태 | 의존 | 공수 | 완료 기준 |
|--------|--------|------|-------|---------|------|------|------|-----------|
| S0.FE.01 | 디자인 시스템 정의 (색상·컴포넌트·타이포) | FE | L1 | P1 | PLAN | — | 8h | Figma 또는 스타일가이드 문서 완료 |
| S0.FE.02 | 라우팅 구조 설계 (페이지 트리) | FE | L1 | P1 | PLAN | S0.FE.01 | 4h | 페이지 트리 문서 완료 |
| S0.BE.01 | 전체 API 설계 (OpenAPI 스펙) | BE | L1 | P1 | PLAN | — | 16h | OpenAPI yaml 완료 + PO 승인 |
| S0.BE.02 | 멀티 테넌트 아키텍처 설계 | BE | L2 | P1 | PLAN | S0.BE.01 | 8h | 테넌트 격리 전략 문서 완료 |
| S0.DB.01 | ERD 설계 (전체 도메인) | DB | L1 | P1 | PLAN | — | 16h | ERD 완성 + PO 승인 |
| S0.DB.02 | pgvector 스키마 설계 (RAG용) | DB | L2 | P2 | PLAN | S0.DB.01 | 4h | 벡터 테이블 스키마 완료 |
| S0.INF.01 | 개발 환경 세팅 (Docker Compose) | INF | L1 | P1 | PLAN | — | 8h | docker-compose up 성공 |
| S0.INF.02 | CI/CD 파이프라인 구성 | INF | L2 | P2 | PLAN | S0.INF.01 | 8h | GitHub Actions 자동 배포 동작 |

**S0 Stage Gate:** 설계 문서 전체 완료 + PO 승인

---

### S1 — 인증 / 인프라

| SAL_ID | Task명 | Area | Level | 우선순위 | 상태 | 의존 | 공수 | 완료 기준 |
|--------|--------|------|-------|---------|------|------|------|-----------|
| S1.BE.01 | 사용자 인증 API (JWT + Refresh) | BE | L1 | P1 | PLAN | S0.BE.01 | 16h | 로그인·토큰 갱신 API 테스트 통과 |
| S1.BE.02 | 멀티 테넌트 미들웨어 구현 | BE | L2 | P1 | PLAN | S1.BE.01 | 16h | 테넌트별 데이터 격리 검증 완료 |
| S1.BE.03 | 기관(Tenant) CRUD API | BE | L1 | P1 | PLAN | S1.BE.02 | 8h | 기관 등록·수정·삭제 API 완료 |
| S1.BE.04 | 구독 플랜 관리 API | BE | L2 | P2 | PLAN | S1.BE.03 | 12h | Starter/Pro/Enterprise 플랜 분기 |
| S1.FE.01 | 로그인·회원가입 화면 | FE | L1 | P1 | PLAN | S1.BE.01 | 12h | UI 완성 + 인증 연동 |
| S1.FE.02 | 기관 관리자 설정 화면 | FE | L1 | P1 | PLAN | S1.BE.03 | 8h | 기관 정보 편집 UI 완성 |
| S1.DB.01 | users / tenants / subscriptions 테이블 생성 | DB | L1 | P1 | PLAN | S0.DB.01 | 4h | 마이그레이션 성공 |
| S1.QA.01 | 인증 플로우 E2E 테스트 | QA | L1 | P1 | PLAN | S1.FE.01 | 8h | 로그인→대시보드 E2E 통과 |

**S1 Stage Gate:** 인증 및 테넌트 분리 정상 동작 확인

---

### S2 — 기록 관리 핵심 모듈

| SAL_ID | Task명 | Area | Level | 우선순위 | 상태 | 의존 | 공수 | 완료 기준 |
|--------|--------|------|-------|---------|------|------|------|-----------|
| S2.BE.01 | 기록물 CRUD API (등록·수정·삭제·조회) | BE | L1 | P1 | PLAN | S1.BE.02 | 20h | 기록 CRUD 테스트 전체 통과 |
| S2.BE.02 | 분류체계 관리 API (다중분류 지원) | BE | L2 | P1 | PLAN | S2.BE.01 | 16h | 업무/출처/주제/시대 분류 동작 |
| S2.BE.03 | 전문 검색 API (Elasticsearch 또는 PG FTS) | BE | L2 | P1 | PLAN | S2.BE.01 | 20h | 키워드·필터·정렬 검색 동작 |
| S2.BE.04 | 파일 업로드 API (S3/NCP Object Storage) | BE | L1 | P1 | PLAN | S2.BE.01 | 12h | 파일 업로드·다운로드·미리보기 |
| S2.BE.05 | 이관 처리 API (생산시스템 연계) | BE | L3 | P2 | PLAN | S2.BE.02 | 16h | 이관 요청→인수 플로우 완성 |
| S2.FE.01 | 기록 목록 화면 (필터·정렬·페이징) | FE | L1 | P1 | PLAN | S2.BE.03 | 16h | 목록·검색·필터 UI 완성 |
| S2.FE.02 | 기록 등록·편집 폼 | FE | L1 | P1 | PLAN | S2.BE.01 | 12h | 메타데이터 입력 폼 완성 |
| S2.FE.03 | 기록 상세 보기 + 파일 미리보기 | FE | L1 | P1 | PLAN | S2.BE.04 | 12h | 상세 패널 + PDF/이미지 뷰어 |
| S2.FE.04 | 분류체계 트리 편집 UI | FE | L2 | P2 | PLAN | S2.BE.02 | 16h | 드래그앤드롭 분류 트리 |
| S2.FE.05 | 메인 대시보드 (통계 카드·최근 기록) | FE | L1 | P1 | PLAN | S2.BE.01 | 12h | 대시보드 위젯 전체 동작 |
| S2.DB.01 | records / classifications / files 테이블 | DB | L1 | P1 | PLAN | S0.DB.01 | 8h | 마이그레이션 성공 |
| S2.QA.01 | 기록 CRUD E2E 테스트 | QA | L1 | P1 | PLAN | S2.FE.02 | 12h | 기록 등록→검색→삭제 E2E 통과 |

**S2 Stage Gate:** 기록 등록·검색·조회 전체 플로우 정상 동작

---

### S3 — AI 자동화 모듈

| SAL_ID | Task명 | Area | Level | 우선순위 | 상태 | 의존 | 공수 | 완료 기준 |
|--------|--------|------|-------|---------|------|------|------|-----------|
| S3.AI.01 | OCR 엔진 연동 (AWS Textract 또는 클로바) | AI | L2 | P1 | PLAN | S2.BE.04 | 16h | 스캔 문서 텍스트 추출 정확도 85%+ |
| S3.AI.02 | LLM 메타데이터 추출 파이프라인 | AI | L2 | P1 | PLAN | S3.AI.01 | 20h | 생산일자·기관·주제어 자동 추출 |
| S3.AI.03 | 자동 분류코드 추천 API | AI | L2 | P1 | PLAN | S3.AI.02 | 16h | 분류코드 추천 정확도 80%+ |
| S3.AI.04 | STT 전사 API 연동 (Whisper/클로바노트) | AI | L1 | P1 | PLAN | S2.BE.04 | 12h | 구술 MP3/MP4 전사 정확도 90%+ |
| S3.AI.05 | LLM 요약·키워드 태깅 API | AI | L2 | P2 | PLAN | S3.AI.04 | 12h | 전사문 요약 + 키워드 5개 이상 추출 |
| S3.BE.01 | AI 처리 작업 큐 (Celery + Redis) | BE | L2 | P1 | PLAN | S3.AI.01 | 12h | 비동기 AI 작업 처리 정상 동작 |
| S3.BE.02 | AI 결과 Review API (승인·거부·수정) | BE | L1 | P1 | PLAN | S3.AI.02 | 8h | Review-in-the-Loop API 완성 |
| S3.FE.01 | AI 자동화 업로드·처리 화면 | FE | L1 | P1 | PLAN | S3.BE.01 | 16h | 업로드→처리중→결과 확인 UI |
| S3.FE.02 | AI 추천 결과 검토·승인 인터페이스 | FE | L2 | P1 | PLAN | S3.BE.02 | 12h | 추천 수락/거부/수정 UI 완성 |
| S3.FE.03 | 구술 전사 뷰어 (타임코드 연동) | FE | L2 | P2 | PLAN | S3.AI.04 | 16h | 오디오 재생 + 전사문 동기 표시 |
| S3.DB.01 | ai_jobs / ai_results 테이블 | DB | L1 | P1 | PLAN | S0.DB.01 | 4h | 마이그레이션 성공 |
| S3.QA.01 | AI 파이프라인 통합 테스트 | QA | L2 | P1 | PLAN | S3.FE.01 | 12h | 업로드→OCR→메타추출 E2E 통과 |

**S3 Stage Gate:** AI 자동 추출·전사·Review-in-the-Loop 전체 플로우 동작

---

### S4 — 지식베이스 모듈

| SAL_ID | Task명 | Area | Level | 우선순위 | 상태 | 의존 | 공수 | 완료 기준 |
|--------|--------|------|-------|---------|------|------|------|-----------|
| S4.AI.01 | RAG 파이프라인 구축 (pgvector 임베딩) | AI | L3 | P1 | PLAN | S0.DB.02 | 20h | 컨설팅 문서 임베딩 + 검색 정상 동작 |
| S4.AI.02 | AI 어시스턴트 API (LLM + RAG) | AI | L3 | P1 | PLAN | S4.AI.01 | 16h | 질의응답 정확도 검토 기준 통과 |
| S4.BE.01 | 지식 문서 CRUD API | BE | L1 | P1 | PLAN | S4.AI.01 | 8h | 문서 등록·삭제·임베딩 재생성 |
| S4.BE.02 | 지식베이스 검색 API | BE | L1 | P1 | PLAN | S4.AI.02 | 8h | 키워드 + 시맨틱 검색 통합 |
| S4.FE.01 | 지식베이스 검색 화면 | FE | L1 | P1 | PLAN | S4.BE.02 | 12h | 검색창 + 사례 카드 목록 UI |
| S4.FE.02 | AI 어시스턴트 채팅 인터페이스 | FE | L2 | P1 | PLAN | S4.AI.02 | 16h | 채팅 UI + 스트리밍 응답 표시 |
| S4.FE.03 | 문서 등록·관리 화면 (관리자용) | FE | L1 | P2 | PLAN | S4.BE.01 | 8h | 문서 업로드·태깅·삭제 UI |
| S4.DB.01 | knowledge_docs / embeddings 테이블 | DB | L1 | P1 | PLAN | S0.DB.02 | 4h | pgvector 인덱스 포함 마이그레이션 |
| S4.QA.01 | RAG 품질 테스트 (질의 20개 세트) | QA | L2 | P1 | PLAN | S4.FE.02 | 8h | 정답률 75%+ |

**S4 Stage Gate:** AI 어시스턴트 질의응답 품질 기준 통과 + PO 검토

---

### S5 — 아카이브 공개 포털

| SAL_ID | Task명 | Area | Level | 우선순위 | 상태 | 의존 | 공수 | 완료 기준 |
|--------|--------|------|-------|---------|------|------|------|-----------|
| S5.BE.01 | 공개 API 설계 (인증 없는 공개 엔드포인트) | BE | L1 | P1 | PLAN | S2.BE.01 | 8h | 공개/비공개 기록 분기 API |
| S5.BE.02 | 타임라인 데이터 API | BE | L1 | P1 | PLAN | S5.BE.01 | 8h | 연도별 기록 집계 API |
| S5.BE.03 | 포털 테마/설정 API (화이트라벨링) | BE | L2 | P2 | PLAN | S5.BE.01 | 12h | 기관별 컬러·로고·도메인 설정 |
| S5.FE.01 | 공개 포털 랜딩 + 타임라인 화면 | FE | L1 | P1 | PLAN | S5.BE.02 | 20h | 타임라인 인터랙션 완성 |
| S5.FE.02 | 공개 기록 검색·열람 화면 | FE | L1 | P1 | PLAN | S5.BE.01 | 16h | 검색 + 상세보기 UI |
| S5.FE.03 | 온라인 전시관 화면 (갤러리 + 설명) | FE | L2 | P2 | PLAN | S5.BE.01 | 16h | 전시 컬렉션 UI |
| S5.FE.04 | 포털 관리자 설정 화면 (테마·메뉴) | FE | L2 | P2 | PLAN | S5.BE.03 | 12h | 테마 미리보기 + 저장 |
| S5.QA.01 | 포털 접근성·반응형 테스트 | QA | L1 | P2 | PLAN | S5.FE.01 | 8h | WCAG 2.1 AA 기준 통과 |

**S5 Stage Gate:** 공개 포털 타임라인·검색·전시 정상 동작

---

### S6 — IoT 스마트 서고

| SAL_ID | Task명 | Area | Level | 우선순위 | 상태 | 의존 | 공수 | 완료 기준 |
|--------|--------|------|-------|---------|------|------|------|-----------|
| S6.INF.01 | IoT 센서 데이터 수신 API (MQTT/HTTP) | INF | L3 | P2 | PLAN | S1.BE.01 | 16h | 센서 데이터 수신·저장 정상 동작 |
| S6.BE.01 | 서고 환경 데이터 CRUD + 알림 로직 | BE | L2 | P2 | PLAN | S6.INF.01 | 12h | 임계값 초과 시 알림 발송 |
| S6.FE.01 | 서고 모니터링 대시보드 | FE | L2 | P2 | PLAN | S6.BE.01 | 16h | 실시간 온·습도 차트 UI |
| S6.FE.02 | 알림 설정 + 히스토리 화면 | FE | L1 | P3 | PLAN | S6.BE.01 | 8h | 알림 조건 설정 + 이력 조회 |
| S6.DB.01 | iot_readings / alerts 테이블 | DB | L1 | P2 | PLAN | S0.DB.01 | 4h | 마이그레이션 성공 |

**S6 Stage Gate:** IoT 데이터 수신·시각화·알림 동작 확인

---

### S7 — 배포 / 론칭

| SAL_ID | Task명 | Area | Level | 우선순위 | 상태 | 의존 | 공수 | 완료 기준 |
|--------|--------|------|-------|---------|------|------|------|-----------|
| S7.INF.01 | 프로덕션 인프라 구성 (AWS/NCP) | INF | L3 | P1 | PLAN | S6.* | 20h | 프로덕션 환경 배포 완료 |
| S7.INF.02 | CSAP 인증 준비 문서 작성 | INF | L3 | P2 | PLAN | S7.INF.01 | 40h | CSAP 제출 문서 패키지 완성 |
| S7.QA.01 | 전체 성능 테스트 (부하 테스트) | QA | L2 | P1 | PLAN | S7.INF.01 | 16h | 동시 100명 응답시간 2초 이내 |
| S7.QA.02 | 보안 취약점 점검 (OWASP Top 10) | QA | L3 | P1 | PLAN | S7.INF.01 | 16h | Critical 취약점 0건 |
| S7.FE.01 | 온보딩 화면 + 튜토리얼 | FE | L1 | P2 | PLAN | S2.FE.05 | 12h | 신규 기관 온보딩 플로우 완성 |
| S7.BE.01 | 사용량 통계 + 과금 연동 | BE | L2 | P2 | PLAN | S1.BE.04 | 16h | 월별 사용량 집계 + 청구 발행 |

**S7 Stage Gate:** 프로덕션 배포 + 성능/보안 검증 완료 = 론칭 승인

---

## ■ 전체 Task 요약

| Stage | Task 수 | 총 공수 | 핵심 목표 |
|-------|---------|---------|-----------|
| S0 | 8 | 72h | 설계 완료 |
| S1 | 8 | 84h | 인증·인프라 |
| S2 | 12 | 144h | 기록 관리 MVP |
| S3 | 12 | 140h | AI 자동화 |
| S4 | 9 | 92h | 지식베이스 |
| S5 | 8 | 100h | 공개 포털 |
| S6 | 5 | 56h | IoT 서고 |
| S7 | 6 | 120h | 배포·론칭 |
| **합계** | **68** | **808h** | **약 10개월** |

**MVP 범위 (S0~S3): 36 Tasks, 440h, 약 5.5개월**

---

## ■ PART 6~8 실행 원칙

- **PART 6**: Stage별 Tasks를 배치 병렬 처리 + Git 커밋 (Task 단위)
- **PART 7**: Task 완료 후 독립 Verification Agent가 완료 기준 검증
- **PART 8**: Stage 전체 완료 후 5항목 Gate 체크 + PO 수동 테스트 → 통과 시 다음 Stage 진입
- **Needs Fix**: 검증 실패 Task는 PART 6으로 재진입

---

## ■ 다음 단계

1. **현재**: 계획서 완료 (PART 2+3)
2. **다음**: 프론트엔드 프로토타입 (S0.FE 설계 기반)
3. **이후**: PART 4 (Instruction 생성) → PART 5 (SAL Grid Viewer) → PART 6 (실행)
