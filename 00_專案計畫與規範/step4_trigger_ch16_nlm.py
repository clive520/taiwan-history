# -*- coding: utf-8 -*-
"""
第 16 章 NotebookLM 筆記本建立、來源文獻上傳與繁體中文雙軌影音任務送出
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

CH16_ARTICLE = BASE_DIR / "06_戰後重構民主浪潮與矽島傳奇/第16章_時代巨變與傷痕記憶_戰後接收二二八事件與白色恐怖年代.md"
CH16_RESEARCH = BASE_DIR / "歷史資料/06_戰後重構民主浪潮與矽島傳奇/16_時代巨變與傷痕記憶考證史料.md"

PROMPT_FILE = BASE_DIR / "00_專案計畫與規範/ch16_prompt.txt"
prompt_text = PROMPT_FILE.read_text(encoding='utf-8')

# 提取 Video Focus
v_m = re.search(r"【1\. NotebookLM 說明影片生成提示詞 \(Video Focus Prompt\)】\s*\n(.*?)(?=\n【2\.|$)", prompt_text, re.S)
video_focus = v_m.group(1).strip() if v_m else ""

# 提取 Podcast Focus
p_m = re.search(r"【2\. NotebookLM 雙人深度對談播客提示詞 \(Podcast Focus Prompt\)】\s*\n(.*?)(?=\n【3\.|$)", prompt_text, re.S)
podcast_focus = p_m.group(1).strip() if p_m else ""

print("="*70)
print("1. 建立第 16 章 NotebookLM 筆記本...")
print("="*70)

title = "臺灣史 第16章：時代巨變與傷痕記憶——戰後接收、二二八事件與白色恐怖年代"
res = subprocess.run(["nlm", "notebook", "create", title, "--json"], capture_output=True, text=True, encoding="utf-8")
print(res.stdout)
if res.stderr:
    print(res.stderr, file=sys.stderr)

try:
    nb_data = json.loads(res.stdout)
    notebook_id = nb_data.get("notebook_id") or nb_data.get("id")
except Exception:
    m = re.search(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", res.stdout)
    notebook_id = m.group(1) if m else None

if not notebook_id:
    print("[ERROR] 無法取得新建筆記本 ID！")
    sys.exit(1)

print(f"✅ 成功建立筆記本！ID: {notebook_id}")
print(f"🔗 筆記本網址: https://notebook.google.com/notebook/{notebook_id}")
(BASE_DIR / "00_專案計畫與規範/ch16_notebook_id.txt").write_text(notebook_id, encoding='utf-8')

print("\n" + "="*70)
print("2. 上傳核心長文與考證史料至筆記本...")
print("="*70)

print(f"[*] 上傳長文：{CH16_ARTICLE.name}...")
subprocess.run(["nlm", "source", "add", notebook_id, "--file", str(CH16_ARTICLE), "--wait"], check=True)

print(f"[*] 上傳史料：{CH16_RESEARCH.name}...")
subprocess.run(["nlm", "source", "add", notebook_id, "--file", str(CH16_RESEARCH), "--wait"], check=True)

print("✅ 雙來源文獻處理完畢！")

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
    v_id = v_data.get("id") or v_data.get("artifact_id")
    a_id = a_data.get("id") or a_data.get("artifact_id")
    print(f"\n[SUMMARY] Video Task ID: {v_id}, Audio Task ID: {a_id}")
    task_info = {"notebook_id": notebook_id, "video_id": v_id, "audio_id": a_id}
    (BASE_DIR / "00_專案計畫與規範/ch16_tasks.json").write_text(json.dumps(task_info, indent=2, ensure_ascii=False), encoding='utf-8')
except Exception as e:
    print(f"[WARN] 解析任務 ID 異常: {e}")
