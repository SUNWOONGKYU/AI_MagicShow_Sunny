# 이미지 폴더 규칙

본 시리즈 48개 항목의 이미지 자산 저장 규칙.

## 폴더 구조

```
상세/md/images/
├── 01/                  # 항목 #1
├── 02/                  # 항목 #2
├── ...
├── 48/                  # 항목 #48
└── README.md            # 본 규칙 문서
```

각 항목 번호는 본문 MD 파일명 앞 두 자리(`NN_*.md`)와 1:1 대응. zero-padded 2자리 고정 (`01`, `02`, ..., `48`).

## 파일 명명 규칙

| 용도 | 파일명 형식 | 예시 |
|------|------------|------|
| 표지 1장 | `cover.{png\|svg\|jpg}` | `48/cover.png` |
| 본문 그림 N장 | `fig_{순번}_{slug}.{ext}` | `48/fig_1_8line_hud.png` |
| 스크린샷 | `screenshot_{slug}.{ext}` | `48/screenshot_skill_atlas.png` |
| 다이어그램 | `diagram_{slug}.{ext}` | `35/diagram_sal_grid_3d.svg` |
| 보조 자료 | `ref_{slug}.{ext}` | `07/ref_patent_filing.png` |

규칙:
- `slug` 은 영문 소문자 + 언더스코어, 한글·공백 금지
- 순번은 `1`, `2`, `3`... (zero-pad 안 함)
- 확장자 우선순위: SVG (벡터·다이어그램) > PNG (스크린샷·합성 이미지) > JPG (사진)

## 본문에서 참조

각 항목 MD 파일 내부에서 상대 경로로 참조:

```markdown
![8줄 Statusline HUD](images/48/cover.png)
```

또는 Markdown 그림 캡션:

```markdown
![](images/35/fig_1_sal_grid_3d.svg)
*그림 1. SAL Grid 3차원 좌표계 (Stage × Area × Level)*
```

## 캡션·alt text 규칙

- alt text(대괄호 안)는 **간단한 설명** (예: "8줄 HUD")
- 캡션(이미지 다음 줄 *이탤릭*)은 **그림 N. 제목** 형식
- 시각장애인 접근성 고려, alt 비우지 마라

## 이미지 출처·저작권

스크린샷 등 본인 산출물 외 자료는 항목 파일 frontmatter `sources` 에 출처 명시.

## 관련 인프라

- Phase 4 (이미지 담당 인스턴스)가 일괄 생성 시 본 폴더 구조 사용
- Phase 5 슬라이드쇼는 본 폴더 이미지를 그대로 임베드
- Phase 6 검수 단계에서 모든 본문의 이미지 참조 깨짐 여부 검증

생성일: 2026-05-06
