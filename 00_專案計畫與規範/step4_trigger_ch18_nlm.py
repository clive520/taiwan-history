# -*- coding: utf-8 -*-
"""
第 18 章 NotebookLM 筆記本建立、來源文獻上傳與繁體中文雙軌影音任務送出
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

CH18_ARTICLE = BASE_DIR / "06_戰後重構民主浪潮與矽島傳奇/第18章_矽島崛起與世界舞台_從客廳即工廠竹科奇蹟到台積電的半導體傳奇.md"
CH18_RESEARCH = BASE_DIR / "歷史資料/06_戰後重構民主浪潮與矽島傳奇/18_矽島崛起與世界舞台考證史料.md"

PROMPT_FILE = BASE_DIR / "00_專案計畫與規範/ch18_prompt.txt"
prompt_text = PROMPT_FILE.read_text(encoding='utf-8')

# 提取 Video Focus
v_m = re.search(r"=== 第 18 章 NotebookLM 說明影片提示詞 \(Video Focus Prompt\) ===\s*\n(.*?)(?=\n=== 第 18 章 NotebookLM 播客雙人深度對談提示詞|$)", prompt_text, re.S)
video_focus = v_m.group(1).strip() if v_m else ""

# 提取 Podcast Focus
p_m = re.search(r"=== 第 18 章 NotebookLM 播客雙人深度對談提示詞 \(Podcast Focus Prompt\) ===\s*\n(.*?)(?=\n=== 第 18 章 Faster-Whisper|$)", prompt_text, re.S)
podcast_focus = p_m.group(1).strip() if p_m else ""

print("="*70)
print("1. 建立第 18 章專屬 NotebookLM 筆記本...")
print("="*70)
nb_title = "臺灣史 第18章：矽島崛起與世界舞台——從客廳即工廠、竹科奇蹟到台積電的半導體傳奇"

res_nb = subprocess.run(["nlm", "notebook", "create", nb_title, "--json"], capture_output=True, text=True, encoding="utf-8")
print(res_nb.stdout)
if res_nb.stderr:
    print(res_nb.stderr, file=sys.stderr)

try:
    nb_data = json.loads(res_nb.stdout)
    notebook_id = nb_data.get("notebook_id") or nb_data.get("id")
except Exception as e:
    print(f"解析 JSON 失敗: {e}")
    # 嘗試正規表達式提取 UUID
    m = re.search(r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}", res_nb.stdout)
    notebook_id = m.group(0) if m else None

if not notebook_id:
    print("❌ 無法取得 notebook_id！請檢查輸出。")
    sys.exit(1)

(BASE_DIR / "00_專案計畫與規範/ch18_notebook_id.txt").write_text(notebook_id, encoding='utf-8')
print(f"✅ 筆記本建立成功！ID: {notebook_id}")
print(f"🔗 筆記本網址: https://notebook.google.com/notebook/{notebook_id}")

print("\n" + "="*70)
print("2. 上傳雙來源文獻至筆記本...")
print("="*70)

print(f"[*] 上傳長文：{CH18_ARTICLE.name}...")
subprocess.run(["nlm", "source", "add", notebook_id, "--file", str(CH18_ARTICLE), "--wait"], check=True)

print(f"[*] 上傳史料：{CH18_RESEARCH.name}...")
subprocess.run(["nlm", "source", "add", notebook_id, "--file", str(CH18_RESEARCH), "--wait"], check=True)

print("✅ 雙來源文獻上傳完成！")

print("\n" + "="*70)
print("3. 觸發繁體中文說明影片生成 (Explainer Video, Heritage, zh-TW)...")
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
print("4. 觸發繁體中文播客深度對談生成 (Deep Dive Audio, zh-TW)...")
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
    v_id = v_data.get("id") or v_data.get("artifact_id") or v_data.get("task_id")
    a_id = a_data.get("id") or a_data.get("artifact_id") or a_data.get("task_id")
    print(f"\n[SUMMARY] Video Task ID: {v_id}, Audio Task ID: {a_id}")
    task_info = {"notebook_id": notebook_id, "video_id": v_id, "audio_id": a_id}
    (BASE_DIR / "00_專案計畫與規範/ch18_tasks.json").write_text(json.dumps(task_info, indent=2, ensure_ascii=False), encoding='utf-8')
except Exception as e:
    print(f"⚠️ 解析任務 ID 警告: {e}")
