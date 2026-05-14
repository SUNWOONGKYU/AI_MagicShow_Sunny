#!/usr/bin/env python3
"""47개 항목 이미지 일괄 생성 - Plan C 정석 풀 비교
순서: G1 → G2 → G3 → G4 → G5 → G6
제외: #02 (완성 GOLD), #48 (실제 스크린샷 보유)
"""
import os
import re
import sys
import shutil
import subprocess
import time
import json
import glob
from datetime import datetime

BASE = r"G:\내 드라이브\333_자료공유폴더\Sunny_Magic_Show\AI_Magic50\상세\md"
TMP_BASE = r"C:\Users\home\AppData\Local\Temp\img_batch"
SCRIPT = r"C:\Users\home\.claude\skills\ai-image-기본\scripts\compare_models.py"
LOG = os.path.join(BASE, "_batch_log.txt")

# 그룹 순서대로 처리할 ID 목록 (제외: 2, 48)
ORDER = [
    # G1 구상 및 계획 (3개, #2 제외)
    13, 14, 34,
    # G2 실행 프로세스 (9)
    1, 25, 3, 12, 26, 42, 38, 10, 35,
    # G3 실행 방법 (8)
    9, 17, 27, 30, 45, 39, 40, 18,
    # G4 결과물 및 품질관리 (9)
    15, 47, 22, 24, 11, 7, 6, 46, 21,
    # G5 환경 (10개, #48 제외)
    5, 33, 23, 44, 43, 41, 28, 16, 36, 37,
    # G6 기타 (8)
    19, 49, 20, 31, 8, 32, 4, 29,
]

VISUAL_TONE = "한국인이 컴퓨터 작업을 하는 장면. 모던 미니멀 일러스트, 따뜻한 조명, 16:9, 화면 속 텍스트는 추상 기호로만 표현, 한글 텍스트 없음"

def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        print(msg.encode('ascii', 'replace').decode('ascii'), flush=True)

def find_md(item_id):
    pattern = os.path.join(BASE, f"{item_id:02d}_*.md")
    files = glob.glob(pattern)
    return files[0] if files else None

def extract_definition(md_path):
    """Extract 한 줄 정의 paragraph from MD."""
    with open(md_path, "r", encoding="utf-8") as f:
        c = f.read()
    m = re.search(r"## 한 줄 정의\s*\n+(.+?)(?=\n##|\Z)", c, re.S)
    if not m:
        return ""
    text = m.group(1).strip()
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\s+", " ", text)
    return text[:280]

def extract_title(md_path):
    with open(md_path, "r", encoding="utf-8") as f:
        c = f.read()
    m = re.search(r'^title:\s*"(.+)"', c, re.M)
    return m.group(1) if m else ""

def make_prompt(item_id, title, definition):
    """Compose visual prompt for image generation."""
    base = f"{title}. {definition} {VISUAL_TONE}"
    if len(base) > 600:
        base = base[:600]
    return base

def process_one(item_id):
    md = find_md(item_id)
    if not md:
        log(f"[#{item_id:02d}] MD not found, skip")
        return False

    title = extract_title(md)
    defn = extract_definition(md)
    if not defn:
        log(f"[#{item_id:02d}] definition not found, skip")
        return False

    prompt = make_prompt(item_id, title, defn)
    outdir = os.path.join(TMP_BASE, f"item_{item_id:02d}")
    dst = os.path.join(BASE, "images", f"{item_id:02d}")

    if not os.path.exists(dst):
        os.makedirs(dst, exist_ok=True)

    cover_path = os.path.join(dst, "cover.png")
    if os.path.exists(cover_path):
        log(f"[#{item_id:02d}] cover.png exists, skip")
        return True

    log(f"[#{item_id:02d}] {title[:50]}")
    log(f"[#{item_id:02d}] PROMPT: {prompt[:120]}...")

    cmd = [
        "python", SCRIPT, prompt,
        "--best-of", "3",
        "--outdir", outdir,
    ]

    t0 = time.time()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=900, encoding="utf-8", errors="replace")
        if result.returncode != 0:
            log(f"[#{item_id:02d}] FAILED rc={result.returncode}")
            log(f"  stderr: {result.stderr[-500:] if result.stderr else ''}")
            return False
    except subprocess.TimeoutExpired:
        log(f"[#{item_id:02d}] TIMEOUT")
        return False
    except Exception as e:
        log(f"[#{item_id:02d}] EXCEPTION {e}")
        return False

    elapsed = time.time() - t0

    eval_json = os.path.join(outdir, "final_evaluation.json")
    top_pick_model = None
    if os.path.exists(eval_json):
        try:
            with open(eval_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            tops = data.get("top_picks", [])
            if tops:
                top_pick_model = tops[0].get("model")
        except Exception:
            pass

    if top_pick_model:
        labeled = os.path.join(outdir, "labeled", f"{top_pick_model}.png".replace(".", "_", 1).replace("__", "_"))
        candidates = []
        for variant in [
            f"labeled/{top_pick_model}.png",
            f"labeled/{top_pick_model.replace('.', '_')}.png",
        ]:
            p = os.path.join(outdir, variant)
            if os.path.exists(p):
                candidates.append(p)
        for f in glob.glob(os.path.join(outdir, "labeled", "*.png")):
            base = os.path.basename(f).replace(".png", "")
            if top_pick_model.startswith(base) or base in top_pick_model.replace(".", "_") or base in top_pick_model.replace("-preview", "").replace(".", "_"):
                candidates.append(f)
        if candidates:
            shutil.copy(candidates[0], cover_path)
        else:
            log(f"[#{item_id:02d}] top_pick file not found, fallback to first labeled")
            firsts = sorted(glob.glob(os.path.join(outdir, "labeled", "*.png")))
            if firsts:
                shutil.copy(firsts[0], cover_path)

    for fname in ["index.html", "final_evaluation.json", "scoreboard.json", "collage_facebook.png"]:
        src = os.path.join(outdir, fname)
        if os.path.exists(src):
            target_name = "collage_5models.png" if fname == "collage_facebook.png" else fname
            shutil.copy(src, os.path.join(dst, target_name))

    log(f"[#{item_id:02d}] DONE {elapsed:.1f}s top_pick={top_pick_model}")
    return True


def main():
    os.makedirs(TMP_BASE, exist_ok=True)
    log(f"=== BATCH START - {len(ORDER)} items ===")
    success = 0
    failed = []
    for i, item_id in enumerate(ORDER, 1):
        log(f"--- [{i}/{len(ORDER)}] #{item_id:02d} ---")
        ok = process_one(item_id)
        if ok:
            success += 1
        else:
            failed.append(item_id)
    log(f"=== BATCH END - success={success} failed={len(failed)} ===")
    if failed:
        log(f"Failed IDs: {failed}")


if __name__ == "__main__":
    main()
