#!/usr/bin/env python3
"""
transcript-analyze.py — Claude Code transcript JSONL 분석
출력: KEY=VALUE 형식 (셸이 sed로 파싱)
  TOOLS=<도구별 카운트, 빈도순. 예: Bash:5,Read:3,Edit:2>
  ACTIVE=<현재 실행 중 도구 종류, 쉼표 구분>
  SUBAGENTS=<진행 중 subagent 목록 (이름(경과초), 쉼표 구분)>
  USAGE=<input,cache_creation,cache_read>
    — statusline JSON에 current_usage 없을 때 fallback 데이터 소스로
      마지막 assistant message의 usage 필드를 그대로 추출

마지막 N줄만 분석해 빠르게 응답한다. 인자 상세는 표시하지 않고 카운트만 노출.
"""

import json
import os
import sys
import time

# Windows 콘솔에서 UTF-8 + LF 강제 (sed 파싱 호환)
try:
    sys.stdout.reconfigure(encoding='utf-8', newline='\n')
    sys.stdin.reconfigure(encoding='utf-8')
except Exception:
    pass

TAIL_LINES = 200       # 마지막 몇 줄까지 분석


def read_tail(path, n):
    """파일 마지막 n줄을 효율적으로 반환."""
    try:
        with open(path, 'rb') as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            if size == 0:
                return []
            block = 8192
            data = b''
            pos = size
            while pos > 0 and data.count(b'\n') <= n:
                read_size = min(block, pos)
                pos -= read_size
                f.seek(pos)
                data = f.read(read_size) + data
            lines = data.split(b'\n')
            return [ln.decode('utf-8', errors='replace') for ln in lines[-(n + 1):] if ln]
    except Exception:
        return []


def main():
    if len(sys.argv) < 2:
        print('TOOLS=')
        print('ACTIVE=')
        print('SUBAGENTS=')
        return

    path = sys.argv[1]
    if not os.path.isfile(path):
        print('TOOLS=')
        print('ACTIVE=')
        print('SUBAGENTS=')
        return

    lines = read_tail(path, TAIL_LINES)

    # subagent 추적: tool_use_id → (subagent_type, start_ts, completed?)
    pending_tasks = {}     # id → (label, start_ts)
    completed_ids = set()
    all_tool_uses = []     # [(name, tool_use_id, start_ts, input_dict), ...] in order
    tool_counts = {}       # name → count (TAIL_LINES 윈도우 내)
    last_usage = None      # 마지막 assistant.usage (ctx fallback 소스)

    now = time.time()

    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except Exception:
            continue

        # 타임스탬프 추출
        ts_str = d.get('timestamp') or d.get('created_at') or ''
        ts = None
        if ts_str:
            try:
                # ISO8601 — Python 3.11+은 fromisoformat 더 관대
                from datetime import datetime
                ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00')).timestamp()
            except Exception:
                ts = None

        msg = d.get('message')
        if not isinstance(msg, dict):
            continue
        role = msg.get('role')
        content = msg.get('content', []) or []
        if not isinstance(content, list):
            continue

        if role == 'assistant':
            # usage 추출 (마지막 assistant 것이 최신 상태)
            u = msg.get('usage')
            if isinstance(u, dict):
                last_usage = u
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get('type') != 'tool_use':
                    continue
                name = block.get('name', '')
                inp = block.get('input', {}) or {}
                tu_id = block.get('id', '')

                if not name:
                    continue
                tool_counts[name] = tool_counts.get(name, 0) + 1
                all_tool_uses.append((name, tu_id, ts or now, inp))

                # Task / Agent 도구 (subagent) 등록
                # — 구버전 Claude Code 는 'Task', 신버전은 'Agent' 로 기록함
                if name in ('Task', 'Agent'):
                    sa_label = inp.get('subagent_type') or inp.get('description') or 'agent'
                    pending_tasks[tu_id] = (sa_label, ts or now)

        elif role == 'user':
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get('type') != 'tool_result':
                    continue
                tu_id = block.get('tool_use_id', '')
                if tu_id:
                    completed_ids.add(tu_id)

    # 진행 중 subagent
    active = []
    for tu_id, (label, start_ts) in pending_tasks.items():
        if tu_id in completed_ids:
            continue
        elapsed = int(now - start_ts) if start_ts else 0
        if elapsed < 0:
            elapsed = 0
        active.append(f'{label}({elapsed}s)')

    # 도구 종류별 카운트 (빈도 내림차순, 동률 시 이름 순)
    tools_summary = ','.join(
        f'{name}:{cnt}'
        for name, cnt in sorted(tool_counts.items(), key=lambda x: (-x[1], x[0]))
    )

    # 활성 도구: completed_ids에 없는 tool_use의 이름만 (중복 제거, 순서 유지)
    active_names = []
    seen = set()
    for n, tid, _, _ in all_tool_uses:
        if tid and tid not in completed_ids and n not in seen:
            seen.add(n)
            active_names.append(n)

    # ACTIVE_DETAIL: 가장 최근 미완료 tool_use 1건의 (name, command, elapsed)
    # 형식: name|command|elapsed_seconds  (파이프는 command에서 공백으로 치환)
    active_detail = ''
    for n, tid, start_ts, inp in reversed(all_tool_uses):
        if not tid or tid in completed_ids:
            continue
        elapsed = int(now - start_ts) if start_ts else 0
        if elapsed < 0:
            elapsed = 0
        cmd = ''
        if n == 'Bash':
            cmd = (inp.get('command', '') or '').strip()
        elif n in ('Read', 'Edit', 'Write', 'NotebookEdit'):
            fp = (inp.get('file_path', '') or '')
            cmd = fp.replace('\\', '/').rsplit('/', 1)[-1]
        elif n in ('Glob', 'Grep'):
            cmd = (inp.get('pattern', '') or '')
        elif n == 'Task':
            cmd = (inp.get('description', '') or inp.get('subagent_type', '') or '')
        elif n == 'WebFetch':
            cmd = (inp.get('url', '') or '')
        elif n == 'WebSearch':
            cmd = (inp.get('query', '') or '')
        # 한 줄로 정규화 + 길이 컷(60자)
        cmd = cmd.replace('\n', ' ').replace('\r', ' ').replace('|', ' ')
        if len(cmd) > 60:
            cmd = cmd[:57] + '...'
        active_detail = f'{n}|{cmd}|{elapsed}'
        break

    print(f'TOOLS={tools_summary}')
    print('ACTIVE=' + ','.join(active_names))
    print(f'ACTIVE_DETAIL={active_detail}')
    print('SUBAGENTS=' + ','.join(active))

    # USAGE: statusline JSON에 current_usage 없을 때 fallback
    if last_usage:
        ui = int(last_usage.get('input_tokens', 0) or 0)
        uc = int(last_usage.get('cache_creation_input_tokens', 0) or 0)
        ur = int(last_usage.get('cache_read_input_tokens', 0) or 0)
        print(f'USAGE={ui},{uc},{ur}')
    else:
        print('USAGE=')


if __name__ == '__main__':
    main()
