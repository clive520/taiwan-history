# -*- coding: utf-8 -*-
"""
第 15 章 NotebookLM 繁體中文雙軌影音任務送出腳本
"""
import subprocess
import json
import sys
import re
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
NOTEBOOK_ID = "89f33278-4573-4715-9de5-c5fb6c241c05"

PROMPT_FILE = BASE_DIR / "00_專案計畫與規範/ch15_prompt.txt"
prompt_text = PROMPT_FILE.read_text(encoding='utf-8')

# 提取 Video Focus
v_m = re.search(r"【1\. NotebookLM 說明影片生成提示詞 \(Video Focus Prompt\)】\s*\n(.*?)(?=\n【2\.|$)", prompt_text, re.S)
video_focus = v_m.group(1).strip() if v_m else ""

# 提取 Podcast Focus
p_m = re.search(r"【2\. NotebookLM 雙人深度對談播客提示詞 \(Podcast Focus Prompt\)】\s*\n(.*?)(?=\n【3\.|$)", prompt_text, re.S)
podcast_focus = p_m.group(1).strip() if p_m else ""

print(f"筆記本 ID: {NOTEBOOK_ID}")
print("\n" + "="*70)
print("1. 觸發繁體中文說明影片生成 (Explainer Video, Heritage, zh-TW)...")
print("="*70)
cmd_v = [
    "nlm", "video", "create", NOTEBOOK_ID,
    "--format", "explainer",
    "--style", "heritage",
    "--language", "zh-TW",
    "--focus", video_focus,
    "--confirm", "--json"
]
res_v = subprocess.run(cmd_v, capture_output=True, text=True, encoding="utf-8")
print(res_v.stdout)
if res_v.stderr:
    print(res_v.stderr, file=sys.stderr)

print("\n" + "="*70)
print("2. 觸發繁體中文播客深度對談生成 (Deep Dive Audio, zh-TW)...")
print("="*70)
cmd_a = [
    "nlm", "audio", "create", NOTEBOOK_ID,
    "--format", "deep_dive",
    "--language", "zh-TW",
    "--focus", podcast_focus,
    "--confirm", "--json"
]
res_a = subprocess.run(cmd_a, capture_output=True, text=True, encoding="utf-8")
print(res_a.stdout)
if res_a.stderr:
    print(res_a.stderr, file=sys.stderr)

try:
    v_data = json.loads(res_v.stdout)
    a_data = json.loads(res_a.stdout)
    v_id = v_data.get("id") or v_data.get("artifact_id")
    a_id = a_data.get("id") or a_data.get("artifact_id")
    print(f"\n[SUMMARY] Video Task ID: {v_id}, Audio Task ID: {a_id}")
    task_info = {"notebook_id": NOTEBOOK_ID, "video_id": v_id, "audio_id": a_id}
    (BASE_DIR / "00_專案計畫與規範/ch15_tasks.json").write_text(json.dumps(task_info, indent=2, ensure_ascii=False), encoding='utf-8')
except Exception as e:
    print(f"[WARN] 解析任務 ID 異常: {e}")
