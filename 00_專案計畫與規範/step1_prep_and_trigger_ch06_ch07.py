# -*- coding: utf-8 -*-
import subprocess
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")

CH06_NOTEBOOK = "c5354897-5c84-4a22-81e7-bc4ee2d0585b"
CH07_NOTEBOOK = "c3127091-0bff-4fea-be05-93089cfaeeb1"

CH06_OLD_VIDEO = "4b50468c-6fa1-4516-9ea3-9b407d208f5d"
CH06_OLD_AUDIO = "1a3d3d47-d37c-49a2-b49b-f55c0578d7dd"

CH07_OLD_VIDEO = "dd5d0a8b-030c-4ebb-aa6a-cf2f49e54277"
CH07_OLD_AUDIO = "f83c37fe-0864-4b74-ae00-56aff9df6fa0"

CH06_RESEARCH_FILE = BASE_DIR / "歷史資料" / "02_大航海時代與荷西競逐" / "06_郭懷一抗荷事件與早期漢人移民考證史料.md"
CH07_RESEARCH_FILE = BASE_DIR / "歷史資料" / "03_明鄭東寧與海上孤忠" / "07_鄭成功攻臺之役與熱蘭遮城圍城考證史料.md"

def run_nlm(cmd_args, desc=""):
    print(f"\n[EXEC] {desc} -> {' '.join(cmd_args)}", flush=True)
    res = subprocess.run(cmd_args, capture_output=True, text=True, encoding="utf-8")
    if res.stdout:
        print(res.stdout.strip())
    if res.stderr:
        print(f"[STDERR] {res.stderr.strip()}", file=sys.stderr)
    return res

print("="*70)
print("1. 刪除第 06 章與第 07 章舊的英文 Studio Artifacts")
print("="*70)

# Delete Ch06 artifacts
run_nlm(["nlm", "studio", "delete", CH06_NOTEBOOK, CH06_OLD_VIDEO, "-y"], "刪除 Ch06 英文 Video")
run_nlm(["nlm", "studio", "delete", CH06_NOTEBOOK, CH06_OLD_AUDIO, "-y"], "刪除 Ch06 英文 Audio")

# Delete Ch07 artifacts
run_nlm(["nlm", "studio", "delete", CH07_NOTEBOOK, CH07_OLD_VIDEO, "-y"], "刪除 Ch07 英文 Video")
run_nlm(["nlm", "studio", "delete", CH07_NOTEBOOK, CH07_OLD_AUDIO, "-y"], "刪除 Ch07 英文 Audio")

print("\n"+"="*70)
print("2. 補充第 06 章與第 07 章考證史料 Source 至 NotebookLM")
print("="*70)

if CH06_RESEARCH_FILE.exists():
    run_nlm(["nlm", "source", "add", CH06_NOTEBOOK, str(CH06_RESEARCH_FILE)], "添加 Ch06 考證史料")
else:
    print(f"[WARN] 找不到 Ch06 考證史料: {CH06_RESEARCH_FILE}")

if CH07_RESEARCH_FILE.exists():
    run_nlm(["nlm", "source", "add", CH07_NOTEBOOK, str(CH07_RESEARCH_FILE)], "添加 Ch07 考證史料")
else:
    print(f"[WARN] 找不到 Ch07 考證史料: {CH07_RESEARCH_FILE}")

print("\n✅ 清理與來源補充完成！")
