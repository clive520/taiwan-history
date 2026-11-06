# -*- coding: utf-8 -*-
"""
第 17 章 NotebookLM 筆記本建立、來源文獻上傳與繁體中文雙軌影音任務送出
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

CH17_ARTICLE = BASE_DIR / "06_戰後重構民主浪潮與矽島傳奇/第17章_走出戒嚴的民主奇蹟_美麗島事件野百合學運與總統直選之路.md"
CH17_RESEARCH = BASE_DIR / "歷史資料/06_戰後重構民主浪潮與矽島傳奇/17_走出戒嚴的民主奇蹟考證史料.md"

PROMPT_FILE = BASE_DIR / "00_專案計畫與規範/ch17_prompt.txt"
prompt_text = PROMPT_FILE.read_text(encoding='utf-8')

# 提取 Video Focus
v_m = re.search(r"=== 第 17 章 NotebookLM 說明影片提示詞 \(Video Focus Prompt\) ===\s*\n(.*?)(?=\n=== 第 17 章 NotebookLM 播客雙人深度對談提示詞|$)", prompt_text, re.S)
video_focus = v_m.group(1).strip() if v_m else ""

# 提取 Podcast Focus
p_m = re.search(r"=== 第 17 章 NotebookLM 播客雙人深度對談提示詞 \(Podcast Focus Prompt\) ===\s*\n(.*?)(?=\n=== 第 17 章 Faster-Whisper|$)", prompt_text, re.S)
podcast_focus = p_m.group(1).strip() if p_m else ""

notebook_id = "f67192ed-1c3c-4ddb-9d5c-cd94baa311a2"
(BASE_DIR / "00_專案計畫與規範/ch17_notebook_id.txt").write_text(notebook_id, encoding='utf-8')
print(f"✅ 使用第 17 章筆記本！ID: {notebook_id}")
print(f"🔗 筆記本網址: https://notebook.google.com/notebook/{notebook_id}")

print("\n" + "="*70)
print("1. 確保雙來源文獻上傳至筆記本...")
print("="*70)

# 檢查已存在來源
src_list = subprocess.run(["nlm", "source", "list", notebook_id, "--json"], capture_output=True, text=True, encoding="utf-8")
existing_titles = []
try:
    src_data = json.loads(src_list.stdout)
    existing_titles = [s.get("title", "") for s in src_data]
    print(f"[*] 現有來源: {existing_titles}")
except Exception:
    pass

if not any("第17章_走出戒嚴的民主奇蹟" in t for t in existing_titles):
    print(f"[*] 上傳長文：{CH17_ARTICLE.name}...")
    subprocess.run(["nlm", "source", "add", notebook_id, "--file", str(CH17_ARTICLE), "--wait"], check=True)

if not any("17_走出戒嚴的民主奇蹟考證史料" in t for t in existing_titles):
    print(f"[*] 上傳史料：{CH17_RESEARCH.name}...")
    subprocess.run(["nlm", "source", "add", notebook_id, "--file", str(CH17_RESEARCH), "--wait"], check=True)

print("✅ 雙來源文獻處理完畢！")

print("\n" + "="*70)
print("2. 觸發繁體中文說明影片生成 (Explainer Video, Heritage, zh-TW)...")
print("="*70)
cmd_v = [
    "nlm", "video", "create", notebook_id,
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
print("3. 觸發繁體中文播客深度對談生成 (Deep Dive Audio, zh-TW)...")
print("="*70)
cmd_a = [
    "nlm", "audio", "create", notebook_id,
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
    task_info = {"notebook_id": notebook_id, "video_id": v_id, "audio_id": a_id}
    (BASE_DIR / "00_專案計畫與規範/ch17_tasks.json").write_text(json.dumps(task_info, indent=2, ensure_ascii=False), encoding='utf-8')
except Exception as e:
    print(f"[WARN] 解析任務 ID 異常: {e}")
