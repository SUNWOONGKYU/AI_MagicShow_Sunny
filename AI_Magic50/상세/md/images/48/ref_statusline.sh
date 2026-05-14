#!/usr/bin/env bash
# my-statusline.sh — Sunny 맞춤 Claude Code statusline
# 출처 작업지시서: AI_Magic50/작업지시서_Claude_Code_HUD.md
#
# 표시 항목 (3~4줄):
#   1행:  📁 디렉토리 | 🤖 모델 | git: 브랜치 상태
#   2행:  ctx 막대 % | 5h 막대 % ⏰ | 7d 막대 % ⏰
#   3행:  🔧 도구(▶=실행중) 인자  /  서브에이전트(경과시간)
#   4행:  👥 팀이름 [팀메이트들]            ← Agent Team 활성 시만
#
# stdin: Claude Code가 넘기는 statusline JSON
#   필요 필드: session_id, transcript_path, cwd, workspace.current_dir,
#             model.{display_name,id}, current_usage.{input_tokens,
#             cache_creation_input_tokens, cache_read_input_tokens},
#             rate_limits.{five_hour,seven_day}.{used_percentage,resets_at}

set -uo pipefail

# Claude Code statusline은 기본 PATH가 제한적일 수 있음 → 사용자 bin 보강
export PATH="$HOME/bin:/c/ProgramData/chocolatey/bin:$PATH"
export LANG="${LANG:-en_US.UTF-8}"
export LC_ALL="${LC_ALL:-en_US.UTF-8}"

INPUT="$(cat 2>/dev/null || true)"
[ -z "$INPUT" ] && INPUT='{}'


# ── jq 필수 검사 ─────────────────────────────────────────────
if ! command -v jq >/dev/null 2>&1; then
    printf '%s\n' "⚠ jq 미설치 — Git Bash에서: choco install jq (관리자) 또는 https://jqlang.org/download/"
    exit 0
fi

# ── 색상 (ANSI) ──────────────────────────────────────────────
RED=$'\033[31m';    GREEN=$'\033[32m';   YELLOW=$'\033[33m'
BLUE=$'\033[34m';   MAGENTA=$'\033[35m'; CYAN=$'\033[36m'
WHITE=$'\033[37m';  GRAY=$'\033[90m';    BOLD=$'\033[1m'
BR_YELLOW=$'\033[93m';  BR_GREEN=$'\033[92m';  BR_MAGENTA=$'\033[95m'
RST=$'\033[0m'

# ── 입력 파싱 ────────────────────────────────────────────────
# Windows fork 비용이 커서(jq 1회 ≈ 90ms) 단일 jq 호출로 모든 필드 추출
_jq_all=$(jq -r '
  [
    .session_id // "",
    .transcript_path // "",
    (.cwd // .workspace.current_dir // ""),
    (.model.display_name // .model.id // "?"),
    .version // "",
    .output_style.name // "",
    (.cost.total_cost_usd // ""|tostring),
    (.cost.total_duration_ms // ""|tostring),
    (.cost.total_lines_added // ""|tostring),
    (.cost.total_lines_removed // ""|tostring),
    (.exceeds_200k_tokens // ""|tostring),
    (.context_window.used_percentage // ""|tostring),
    (.context_window.context_window_size // ""|tostring),
    (.context_window.current_usage.input_tokens // .current_usage.input_tokens // ""|tostring),
    (.context_window.current_usage.cache_creation_input_tokens // .current_usage.cache_creation_input_tokens // ""|tostring),
    (.context_window.current_usage.cache_read_input_tokens // .current_usage.cache_read_input_tokens // ""|tostring),
    (.rate_limits.five_hour.used_percentage // ""|tostring),
    (.rate_limits.five_hour.resets_at // ""|tostring),
    (.rate_limits.seven_day.used_percentage // ""|tostring),
    (.rate_limits.seven_day.resets_at // ""|tostring),
    (.context_window.remaining_percentage // ""|tostring)
  ] | join("\u0001")
' <<<"$INPUT")
IFS=$'\x01' read -r SESSION_ID TRANSCRIPT_PATH CWD MODEL_NAME \
    CC_VERSION OUTPUT_STYLE COST_USD COST_DUR_MS LINES_ADD LINES_REM EXCEEDS_200K \
    CTX_PCT_DIRECT CTX_LIMIT_DIRECT USAGE_INPUT USAGE_CC USAGE_CR \
    R5_PCT R5_RESETS R7_PCT R7_RESETS CTX_REMAIN <<<"$_jq_all"

# Windows 경로 정규화 (Git Bash 호환)
CWD_NORM="${CWD//\\//}"
TRANSCRIPT_PATH="${TRANSCRIPT_PATH//\\//}"

# 1) 디렉토리명만
DIR_NAME=$(basename "$CWD_NORM" 2>/dev/null)
[ -z "$DIR_NAME" ] && DIR_NAME="?"

# ── 캐시 헬퍼 (먼저 정의) ────────────────────────────────────
cache_get() {
    local f="$1"; local ttl="${2:-5}"
    [ -f "$f" ] || return 1
    local now; now=$(date +%s)
    local mtime
    mtime=$(stat -c %Y "$f" 2>/dev/null || stat -f %m "$f" 2>/dev/null)
    [ -z "$mtime" ] && return 1
    [ $((now - mtime)) -gt "$ttl" ] && return 1
    cat "$f"
}

# ── 캐시 경로 ────────────────────────────────────────────────
CACHE_DIR="${TMPDIR:-/tmp}/claude-statusline"
mkdir -p "$CACHE_DIR" 2>/dev/null
SESS_KEY="${SESSION_ID:-default}"
SESS_KEY="${SESS_KEY//\//_}"
CACHE_TR="$CACHE_DIR/transcript_${SESS_KEY}.cache"
CACHE_GIT="$CACHE_DIR/git_${SESS_KEY}.cache"
CACHE_TIER="$CACHE_DIR/account_tier.cache"

# 0) Claude 계정 등급 — credentials.json (자주 안 바뀜 → 5분 캐시)
ACCOUNT_TIER=""
CRED_FILE="$HOME/.claude/.credentials.json"
if [ -f "$CRED_FILE" ]; then
    if cached=$(cache_get "$CACHE_TIER" 300); then
        ACCOUNT_TIER="$cached"
    else
        ACCOUNT_TIER=$(jq -r '.claudeAiOauth.subscriptionType // empty' "$CRED_FILE" 2>/dev/null)
        printf '%s' "$ACCOUNT_TIER" > "$CACHE_TIER" 2>/dev/null
    fi
fi

# ── 3) 컨텍스트 입력 — 위 _jq_all 에서 이미 추출됨 ─────────────

# ── 4·5) Rate Limit ──────────────────────────────────────────
fmt_remaining() {
    local resets_at="$1"
    [ -z "$resets_at" ] || [ "$resets_at" = "null" ] && return
    local now; now=$(date +%s)
    local target=""
    # 1) epoch 정수 형식 (Claude Code 2.1.x: rate_limits.*.resets_at)
    if [[ "$resets_at" =~ ^[0-9]+$ ]]; then
        target="$resets_at"
    else
        # 2) ISO 8601 문자열 (구버전·일부 모드)
        target=$(python -c "
import datetime, sys
try:
    s = sys.argv[1].replace('Z','+00:00')
    print(int(datetime.datetime.fromisoformat(s).timestamp()))
except Exception:
    pass
" "$resets_at" 2>/dev/null)
    fi
    [ -z "$target" ] && return
    local diff=$((target - now))
    [ "$diff" -le 0 ] && { echo "0m"; return; }
    local h=$((diff / 3600)); local m=$(((diff % 3600) / 60))
    if [ "$h" -gt 0 ]; then echo "${h}h${m}m"; else echo "${m}m"; fi
}

build_rate_bar() {
    local label="$1"; local pct="$2"; local resets_at="$3"
    if [ -z "$pct" ] || [ "$pct" = "null" ]; then
        printf '%s' "${label} ${GRAY}N/A${RST}"
        return
    fi
    pct=$(printf "%.0f" "$pct" 2>/dev/null || echo "0")
    local filled=$((pct * 10 / 100))
    [ "$filled" -gt 10 ] && filled=10
    local bar=""
    for ((i=0; i<filled; i++)); do bar+="█"; done
    for ((i=filled; i<10; i++)); do bar+="░"; done
    local col
    if   [ "$pct" -ge 70 ]; then col=$RED
    elif [ "$pct" -ge 50 ]; then col=$YELLOW
    else                         col=$GREEN
    fi
    local remain
    remain=$(fmt_remaining "$resets_at")
    local out="${label} ${col}${bar} ${pct}%${RST}"
    [ -n "$remain" ] && out+=" ⏰ ${remain}"
    printf '%s' "$out"
}

# R5/R7 변수는 위 _jq_all 에서 이미 추출됨
R5_DISPLAY=$(build_rate_bar "5h" "$R5_PCT" "$R5_RESETS")
R7_DISPLAY=$(build_rate_bar "7d" "$R7_PCT" "$R7_RESETS")

# ── 6-h) Hook 발동 표시 ──────────────────────────────────────
# hook-logger.js가 /tmp/claude-statusline/hooks_<sess>.log 에 epoch\tevent\ttool 기록.
# 최근 3초 내 발동된 hook event를 중복 제거 후 표시.
HOOK_DISPLAY=""
if [ -n "$SESSION_ID" ]; then
    SAFE_KEY="${SESSION_ID//[^A-Za-z0-9_-]/_}"
    HLOG="$CACHE_DIR/hooks_${SAFE_KEY}.log"
    if [ -f "$HLOG" ]; then
        cutoff=$(($(date +%s) - 3))
        recent=$(awk -F'\t' -v c="$cutoff" '$1 >= c {print $2}' "$HLOG" 2>/dev/null \
                 | tail -5 | awk '!seen[$0]++' | tr '\n' ',' | sed 's/,$//')
        [ -n "$recent" ] && HOOK_DISPLAY="Hook(${recent})"
    fi
fi

# ── 6·7·8) transcript 분석 (도구 카운트·활성 도구·서브에이전트) ──────────
TOOLS_SUMMARY=""; ACTIVE_TOOLS=""; ACTIVE_DETAIL=""; SUBAGENTS=""; TR_USAGE=""
if [ -n "$TRANSCRIPT_PATH" ]; then
    # Windows 경로 → POSIX
    TR_PATH="${TRANSCRIPT_PATH//\\//}"
    if [ -f "$TR_PATH" ]; then
        if cached=$(cache_get "$CACHE_TR" 5); then
            TR_INFO="$cached"
        else
            TR_INFO=$(python "$HOME/.claude/transcript-analyze.py" "$TR_PATH" 2>/dev/null || true)
            printf '%s' "$TR_INFO" > "$CACHE_TR" 2>/dev/null
        fi
        # sed 5회 → bash 내장 파싱 (fork 제거)
        TOOLS_SUMMARY="" ACTIVE_TOOLS="" ACTIVE_DETAIL="" SUBAGENTS="" TR_USAGE=""
        while IFS= read -r _line; do
            case "$_line" in
                TOOLS=*)        [ -z "$TOOLS_SUMMARY" ] && TOOLS_SUMMARY="${_line#TOOLS=}" ;;
                ACTIVE=*)       [ -z "$ACTIVE_TOOLS"  ] && ACTIVE_TOOLS="${_line#ACTIVE=}" ;;
                ACTIVE_DETAIL=*)[ -z "$ACTIVE_DETAIL" ] && ACTIVE_DETAIL="${_line#ACTIVE_DETAIL=}" ;;
                SUBAGENTS=*)    [ -z "$SUBAGENTS"     ] && SUBAGENTS="${_line#SUBAGENTS=}" ;;
                USAGE=*)        [ -z "$TR_USAGE"      ] && TR_USAGE="${_line#USAGE=}" ;;
            esac
        done <<< "$TR_INFO"
    fi
fi

# ── 3-render) ctx 막대 렌더링
# 우선순위: (a) Claude Code 직접 % (가장 정확) → (b) statusline JSON 토큰 합산
#          → (c) transcript의 마지막 assistant.usage fallback
PCT=""
if [ -n "$CTX_PCT_DIRECT" ]; then
    PCT=$(printf "%.0f" "$CTX_PCT_DIRECT" 2>/dev/null || echo "")
fi

if [ -z "$PCT" ]; then
    if [ -z "$USAGE_INPUT$USAGE_CC$USAGE_CR" ] && [ -n "$TR_USAGE" ]; then
        USAGE_INPUT=$(printf '%s' "$TR_USAGE" | cut -d, -f1)
        USAGE_CC=$(printf '%s' "$TR_USAGE" | cut -d, -f2)
        USAGE_CR=$(printf '%s' "$TR_USAGE" | cut -d, -f3)
    fi
    if [ -n "$USAGE_INPUT$USAGE_CC$USAGE_CR" ]; then
        UI=${USAGE_INPUT:-0}; UC=${USAGE_CC:-0}; UR=${USAGE_CR:-0}
        TOTAL=$((UI + UC + UR))
        LIMIT=${CTX_LIMIT_DIRECT:-200000}
        PCT=$((TOTAL * 100 / LIMIT))
    fi
fi

if [ -z "$PCT" ]; then
    CTX_DISPLAY="${GRAY}--${RST}"
else
    [ "$PCT" -gt 100 ] && PCT=100
    FILLED=$((PCT * 10 / 100))
    [ "$FILLED" -gt 10 ] && FILLED=10
    BAR=""
    for ((i=0; i<FILLED; i++));   do BAR+="█"; done
    for ((i=FILLED; i<10; i++));  do BAR+="░"; done
    if   [ "$PCT" -ge 80 ]; then COL=$RED
    elif [ "$PCT" -ge 50 ]; then COL=$YELLOW
    else                         COL=$GREEN
    fi
    CTX_DISPLAY="${COL}${BAR} ${PCT}%${RST}"
fi

# ── 8b) 분대원 — TRANSCRIPT_PATH 기반 subagents 디렉토리 직접 스캔
# 경로: ~/.claude/projects/<proj_key>/<session_uuid>/subagents/agent-*.meta.json
ACTIVE_SUBAGENTS=""
if [ -n "$TRANSCRIPT_PATH" ]; then
    _tr_noext="${TRANSCRIPT_PATH%.jsonl}"
    _sub_dir="${_tr_noext}/subagents"
    if [ -d "$_sub_dir" ]; then
        _now=$(date +%s)
        _sub_names=""
        for _meta in "${_sub_dir}/"agent-*.meta.json; do
            [ -f "$_meta" ] || continue
            [[ "$_meta" == *acompact* ]] && continue
            _mt=$(stat -c %Y "$_meta" 2>/dev/null || echo 0)
            [ $(( _now - _mt )) -gt 600 ] && continue
            # jsonl size 0 → 아직 시작 안 됨 → 제외
            _jsonl="${_meta%.meta.json}.jsonl"
            [ -f "$_jsonl" ] && [ ! -s "$_jsonl" ] && continue
            _raw=$(<"$_meta")
            _desc="${_raw#*\"description\":\"}"
            if [ "$_desc" != "$_raw" ]; then
                _desc="${_desc%%\"*}"
            else
                _desc="${_raw#*\"agentType\":\"}"; _desc="${_desc%%\"*}"
            fi
            [ -n "$_sub_names" ] && _sub_names+=", "
            _sub_names+="${_desc:0:20}"
        done
        ACTIVE_SUBAGENTS="$_sub_names"
    fi
fi

# ── 10) Git ─────────────────────────────────────────────────
GIT_INFO=""
if [ -n "$CWD_NORM" ] && [ -d "$CWD_NORM" ]; then
    if cached=$(cache_get "$CACHE_GIT" 5); then
        GIT_INFO="$cached"
    else
        GIT_INFO=$(
            cd "$CWD_NORM" 2>/dev/null || exit 0
            br=$(git symbolic-ref --short HEAD 2>/dev/null || git rev-parse --short HEAD 2>/dev/null)
            [ -z "$br" ] && exit 0
            if git diff --quiet 2>/dev/null && git diff --cached --quiet 2>/dev/null; then
                st="${GREEN}clean${RST}"
            else
                st="${YELLOW}*dirty${RST}"
            fi
            ahead=$(git rev-list --count '@{u}..HEAD' 2>/dev/null || echo 0)
            behind=$(git rev-list --count 'HEAD..@{u}' 2>/dev/null || echo 0)
            ab=""
            [ "$ahead"  != "0" ] && ab+=" ↑${ahead}"
            [ "$behind" != "0" ] && ab+=" ↓${behind}"
            printf '%s%s%s %s%s' "$MAGENTA" "$br" "$RST" "$st" "$ab"
        )
        printf '%s' "$GIT_INFO" > "$CACHE_GIT" 2>/dev/null
    fi
fi

# ── LINE0: 경고/모드 메시지를 statusline 최상단에 우측 정렬해서 표시.
#   Claude Code native UI는 좌측에 그려지므로, 우리는 동쪽(오른쪽)으로 밀어
#   시각적으로 겹치지 않게 함.
LINE0_PARTS=()

# Context low / very low (Claude Code native와 동일 임계값)
if [ -n "$CTX_REMAIN" ]; then
    rem_int=$(printf '%.0f' "$CTX_REMAIN" 2>/dev/null || echo 100)
    if [ "$rem_int" -lt 10 ]; then
        LINE0_PARTS+=("${RED}⚠ Context very low (${rem_int}% remaining)${GRAY}")
    elif [ "$rem_int" -lt 25 ]; then
        LINE0_PARTS+=("${YELLOW}⚠ Context low (${rem_int}% remaining)${GRAY}")
    fi
fi
[ "$EXCEEDS_200K" = "true" ] && LINE0_PARTS+=("${RED}⚠ Exceeds 200k tokens${GRAY}")

# rate limit 임박 (90% 이상)
R5_PCT_INT=$(printf '%.0f' "${R5_PCT:-0}" 2>/dev/null || echo 0)
R7_PCT_INT=$(printf '%.0f' "${R7_PCT:-0}" 2>/dev/null || echo 0)
[ "$R5_PCT_INT" -ge 90 ] 2>/dev/null && LINE0_PARTS+=("${RED}⚠ 5h limit ${R5_PCT_INT}%${GRAY}")
[ "$R7_PCT_INT" -ge 90 ] 2>/dev/null && LINE0_PARTS+=("${RED}⚠ 7d limit ${R7_PCT_INT}%${GRAY}")

LINE0=""
if [ ${#LINE0_PARTS[@]} -gt 0 ]; then
    joined=""
    for p in "${LINE0_PARTS[@]}"; do
        [ -n "$joined" ] && joined+=" │ "
        joined+="$p"
    done
    LINE0="${GRAY}${joined}${RST}"
fi

# 구분선: 경고 영역과 커스텀 영역 분리 (LINE0가 있을 때만 그림)
SEPARATOR="${GRAY}────────────────────────────────────────${RST}"

LINE1="${BOLD}${CYAN}📁 ${DIR_NAME}${RST} │ ${BOLD}${BR_YELLOW}🤖 ${MODEL_NAME}${RST}"
[ -n "$ACCOUNT_TIER" ] && LINE1+=" ${GRAY}(${ACCOUNT_TIER})${RST}"
[ -n "$GIT_INFO" ] && LINE1+=" │ ${GIT_INFO}"

LINE2="ctx ${CTX_DISPLAY} │ ${R5_DISPLAY} │ ${R7_DISPLAY}"

# LINE3: 도구 카운트 (누적 도구 사용 빈도)
LINE3=""
if [ -n "$TOOLS_SUMMARY" ]; then
    # "Bash:5,Read:3,Edit:2" → "Bash×5, Read×3, Edit×2"
    pretty=$(printf '%s' "$TOOLS_SUMMARY" | sed 's/:/×/g; s/,/, /g')
    LINE3="${CYAN}${pretty}${RST}"
fi

# LINE3B: 실행 중인 명령 (도구명 + 인자 + 경과시간) + Hook
LINE3B=""
if [ -n "$ACTIVE_DETAIL" ]; then
    IFS='|' read -r ad_name ad_cmd ad_elapsed <<< "$ACTIVE_DETAIL"
    if [ -n "$ad_name" ]; then
        if [ -n "$ad_cmd" ]; then
            LINE3B="${BR_YELLOW}▶ ${ad_name}: ${WHITE}${ad_cmd}${RST}"
        else
            LINE3B="${BR_YELLOW}▶ ${ad_name}${RST}"
        fi
        if [ -n "$ad_elapsed" ] && [ "$ad_elapsed" != "0" ]; then
            LINE3B+=" ${GRAY}(${ad_elapsed}s)${RST}"
        fi
    fi
elif [ -n "$ACTIVE_TOOLS" ]; then
    pretty_act=$(printf '%s' "$ACTIVE_TOOLS" | sed 's/,/, /g')
    LINE3B="${BR_YELLOW}▶ ${pretty_act}${RST}"
fi
if [ -n "$HOOK_DISPLAY" ]; then
    [ -n "$LINE3B" ] && LINE3B+=" "
    LINE3B+="${BR_MAGENTA}${HOOK_DISPLAY}${RST}"
fi

# LINE4: 분대원 (SubAgent) — Task/Agent 도구로 진행 중인 일회성 작업자
# 우선순위: tasks/*.output 직접 스캔(ACTIVE_SUBAGENTS) → transcript 분석(SUBAGENTS)
LINE4=""
SUB_DISPLAY="${ACTIVE_SUBAGENTS:-$SUBAGENTS}"
if [ -n "$SUB_DISPLAY" ]; then
    pretty_sub=$(printf '%s' "$SUB_DISPLAY" | sed 's/,/, /g')
    LINE4="${YELLOW}SubAgent (분대원) [${pretty_sub}]${RST}"
fi

# LINE5: 팀메이트(분대장)는 native UI 맨 아래에 이미 표시됨 → 별도 출력 불필요

# 출력 순서: 첫 줄은 빈 줄로 비워둠 → Claude Code native 메시지 전용 공간
printf '\n'
[ -n "$LINE0" ] && printf '%s\n' "$LINE0"
printf '%s\n' "$LINE1"
printf '%s\n' "$LINE2"
[ -n "$LINE3"  ] && printf '%s\n' "$LINE3"
[ -n "$LINE3B" ] && printf '%s\n' "$LINE3B"
[ -n "$LINE4"  ] && printf '%s'   "$LINE4"
exit 0
