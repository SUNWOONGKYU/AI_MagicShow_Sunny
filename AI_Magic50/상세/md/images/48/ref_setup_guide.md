# Claude Code 커스텀 스테이터스라인 설치 가이드

터미널 하단에 컨텍스트·Rate Limit·도구 통계·SubAgent 현황 등을 실시간으로 표시하는 HUD입니다.

---

## 📦 포함 파일

| 파일 | 역할 |
|------|------|
| `my-statusline.sh` | HUD 본체 스크립트 (핵심) |
| `transcript-analyze.py` | 도구 통계·SubAgent 분석용 Python 헬퍼 |
| `settings_statusline_example.json` | settings.json 등록 예시 |
| `README_설치가이드.md` | 이 파일 |

---

## 🖥️ 표시 내용 (8줄 구조)

```
줄1: [NATIVE] ⚠ Context low (15% remaining)      ← 컨텍스트 부족 시 자동 출현
줄2: [CUSTOM] 📁 프로젝트명  |  🤖 모델명 (등급)  |  git브랜치 *dirty
줄3: [CUSTOM] ctx ████░░░░░░ 38%  |  5h ██░░░░░░░░ 22% ⏰ 1h12m  |  7d █████░░░░░ 48%
줄4: [CUSTOM] Bash×12  Edit×8  Read×15  Write×3  Grep×6  Agent×2
줄5: [CUSTOM] ▶ npm run dev  (Bash)   Hook(PreToolUse)
줄6: [CUSTOM] SubAgent (분대원) [작업명1, 작업명2]  ← 활성 SubAgent 있을 때만
줄7: [NATIVE] @Alpha  @Bravo                        ← 팀메이트 있을 때만
줄8: [NATIVE] ✓ bypassPermissions
```

- **CUSTOM**: `my-statusline.sh`가 출력하는 줄
- **NATIVE**: Claude Code가 자체적으로 표시하는 줄 (스크립트 제어 불가)

---

## ⚙️ 사전 요구사항

| 도구 | 확인 방법 | 설치 |
|------|----------|------|
| **Git Bash** 또는 **WSL** | `bash --version` | https://gitforwindows.org |
| **jq** | `jq --version` | `choco install jq` (관리자 권한) 또는 https://jqlang.org/download/ |
| **Python 3.8+** | `python --version` | https://python.org |

---

## 🚀 설치 방법

### Step 1. 파일 복사

`my-statusline.sh`와 `transcript-analyze.py`를 `~/.claude/` 폴더에 복사합니다.

**Windows 경로**: `C:\Users\【사용자명】\.claude\`

```bash
# Git Bash에서
cp my-statusline.sh ~/.claude/
cp transcript-analyze.py ~/.claude/
```

### Step 2. 실행 권한 부여 (Git Bash)

```bash
chmod +x ~/.claude/my-statusline.sh
```

### Step 3. settings.json 수정

`C:\Users\【사용자명】\.claude\settings.json`을 열고 아래 내용을 추가합니다:

```json
{
  "statusLine": {
    "type": "command",
    "command": "bash /c/Users/【사용자명】/.claude/my-statusline.sh"
  }
}
```

> ⚠️ **중요**: `【사용자명】` 부분을 실제 Windows 사용자명으로 바꿔야 합니다.
> 예: `home` → `john` 이면 `/c/Users/john/.claude/my-statusline.sh`

### Step 4. Claude Code 재시작

settings.json 저장 후 Claude Code를 완전히 종료하고 다시 시작합니다.

---

## 🔧 동작 원리

```
Claude Code 이벤트 발생
        ↓
bash my-statusline.sh 실행 (stdin으로 JSON 수신)
        ↓
jq로 JSON 파싱 (모델명, ctx%, rate limit 등)
        ↓
transcript-analyze.py 실행 (도구 통계, SubAgent 탐지)
        ↓
ANSI 색상 코드 포함 텍스트 출력
        ↓
Claude Code 터미널 하단에 표시
```

---

## 🐛 트러블슈팅

### 스테이터스라인이 아예 안 보인다
- `settings.json`에 `statusLine` 항목이 정확히 들어갔는지 확인
- 경로의 사용자명이 실제 Windows 사용자명과 일치하는지 확인
- Claude Code를 완전히 재시작했는지 확인

### `jq 미설치` 경고가 뜬다
```bash
# 관리자 권한 Git Bash에서
choco install jq
```
또는 https://jqlang.org/download/ 에서 수동 설치 후 PATH 등록

### 도구 통계(줄4)가 안 보인다
`transcript-analyze.py`가 `~/.claude/` 폴더에 있는지 확인:
```bash
ls ~/.claude/transcript-analyze.py
```

### ctx 막대가 `--`로 표시된다
Claude Code가 컨텍스트 정보를 아직 전달하지 않은 상태입니다. 대화를 시작하면 자동으로 표시됩니다.

### SubAgent 줄(줄6)이 안 보인다
SubAgent가 활성화된 경우에만 표시됩니다 (Agent 도구로 투입한 서브에이전트가 있어야 함). 없으면 줄 자체가 숨겨집니다.

---

## 📁 캐시 파일 위치

스크립트는 성능을 위해 임시 캐시를 사용합니다:
- 위치: `/tmp/claude-statusline/` (Git Bash 기준)
- 캐시 유효시간: git 정보 5초, 계정 등급 5분
- 문제 시 해당 폴더를 삭제하면 초기화됩니다

---

## 📝 라이선스

개인 사용 자유. 재배포 시 출처 표기 권장.
