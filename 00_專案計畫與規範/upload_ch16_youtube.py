# -*- coding: utf-8 -*-
"""
第 16 章 YouTube 影音全自動發布管線
調用 youtube_api_uploader.py 發布說明影片與播客影片，
設定排程、高清高點擊封面、繁體中文字幕軌與播放清單，並自動更新 js/data.js。
"""
import os
import sys
import json
import re
import subprocess
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

PYTHON_EXE = r"C:\Users\admin\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"
BASE_DIR = Path(r"d:\Antigravity\科技歷史\臺灣史")
UPLOADER_SCRIPT = BASE_DIR / "00_專案計畫與規範" / "youtube_api_uploader.py"

def run_cmd(cmd):
    print(f"\n[EXEC] {' '.join(cmd)}", flush=True)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', bufsize=1)
    full_output = []
    for line in iter(p.stdout.readline, ''):
        print(line, end='', flush=True)
        full_output.append(line)
    p.stdout.close()
    ret = p.wait()
    return ret, ''.join(full_output)

def update_data_js(v1_id, v2_id):
    data_js = BASE_DIR / "js" / "data.js"
    c = data_js.read_text(encoding='utf-8')
    
    old_snippet = """    "status": "planned",
    "file": "第16章_時代巨變與傷痕記憶_戰後接收二二八事件與白色恐怖年代.md",
    "videoSchedule": "2026-11-10 17:30",
    "podcastSchedule": "2026-11-10 19:30"
  },"""

    new_snippet = f"""    "status": "published",
    "bannerImage": "assets/images/ch16/ch16_hero_banner.jpg",
    "youtube": "{v1_id}",
    "podcastYoutube": "{v2_id}",
    "notebooklm": "https://notebook.google.com/notebook/432b3346-0a7d-416c-84e2-8a521834b5c4",
    "audioFile": "https://github.com/clive520/taiwan-history/releases/download/v1.0.0/ch16_podcast_deepdive.m4a",
    "srtFile": "第16章_時代巨變與傷痕記憶_說明影片.srt",
    "file": "第16章_時代巨變與傷痕記憶_戰後接收二二八事件與白色恐怖年代.md",
    "videoSchedule": "2026-11-10 17:30",
    "podcastSchedule": "2026-11-10 19:30"
  }},"""

    c_norm = c.replace("\r\n", "\n")
    if old_snippet in c_norm:
        c_norm = c_norm.replace(old_snippet, new_snippet)
        data_js.write_text(c_norm, encoding='utf-8')
        print("✅ 已成功更新 js/data.js！")
    else:
        print("[WARN] old_snippet 未找到，嘗試替代方案更新 js/data.js...")
        idx = c.find('"id": "ch16"')
        if idx != -1:
            end_idx = c.find('},\n  {\n    "id": "ch17"', idx)
            if end_idx == -1:
                end_idx = c.find('}\n];', idx)
            block = c[idx:end_idx]
            new_block = block.replace('"status": "planned"', '"status": "published"')
            new_block = new_block.replace(
                '"file": "第16章_時代巨變與傷痕記憶_戰後接收二二八事件與白色恐怖年代.md",',
                f'"bannerImage": "assets/images/ch16/ch16_hero_banner.jpg",\n    "youtube": "{v1_id}",\n    "podcastYoutube": "{v2_id}",\n    "notebooklm": "https://notebook.google.com/notebook/432b3346-0a7d-416c-84e2-8a521834b5c4",\n    "audioFile": "https://github.com/clive520/taiwan-history/releases/download/v1.0.0/ch16_podcast_deepdive.m4a",\n    "srtFile": "第16章_時代巨變與傷痕記憶_說明影片.srt",\n    "file": "第16章_時代巨變與傷痕記憶_戰後接收二二八事件與白色恐怖年代.md",'
            )
            c = c[:idx] + new_block + c[end_idx:]
            data_js.write_text(c, encoding='utf-8')
            print("✅ 替代方案更新 js/data.js 成功！")
        
    # 更新 Markdown 正文影音連結
    md_file = BASE_DIR / "06_戰後重構民主浪潮與矽島傳奇/第16章_時代巨變與傷痕記憶_戰後接收二二八事件與白色恐怖年代.md"
    if md_file.exists():
        md_c = md_file.read_text(encoding='utf-8')
        md_c = md_c.replace("*(待生成)*", f"[YouTube 觀看連結](https://youtu.be/{v1_id}) *(預定 2026-11-10 17:30 首播)*", 1)
        md_c = md_c.replace("*(待生成)*", f"[YouTube 專題觀看](https://youtu.be/{v2_id}) *(預定 2026-11-10 19:30 首播)*", 1)
        md_c = md_c.replace("*(待上傳 GitHub Release 雲端串流無損音訊)*", "[GitHub Release 雲端串流無損音訊](https://github.com/clive520/taiwan-history/releases/download/v1.0.0/ch16_podcast_deepdive.m4a)")
        md_file.write_text(md_c, encoding='utf-8')
        print(f"✅ 已成功更新 {md_file.name} 影音超連結！")

def upload_all():
    v1_file = BASE_DIR / "06_戰後重構民主浪潮與矽島傳奇/第16章_時代巨變與傷痕記憶_說明影片.mp4"
    v1_title = "【臺灣史 EP16】時代巨變與傷痕記憶！二二八事件真相與三十八年戒嚴白色恐怖"
    v1_desc = BASE_DIR / "06_戰後重構民主浪潮與矽島傳奇/ch16_desc.txt"
    v1_thumb = BASE_DIR / "assets/images/ch16/ch16_youtube_thumbnail.jpg"
    v1_srt = BASE_DIR / "06_戰後重構民主浪潮與矽島傳奇/第16章_時代巨變與傷痕記憶_說明影片.srt"
    v1_schedule = "2026-11-10 17:30"
    
    print("\n" + "="*70)
    print("🚀 [1/2] 正在上傳第 16 章 說明影片...")
    print("="*70)
    cmd1 = [
        PYTHON_EXE, str(UPLOADER_SCRIPT),
        "--video", str(v1_file),
        "--title", v1_title,
        "--desc-file", str(v1_desc),
        "--thumbnail", str(v1_thumb),
        "--srt", str(v1_srt),
        "--schedule", v1_schedule,
        "--playlist", "台灣史"
    ]
    ret1, out1 = run_cmd(cmd1)
    v1_id = None
    m1 = re.search(r"https://youtu\.be/([a-zA-Z0-9_-]{11})", out1)
    if m1:
        v1_id = m1.group(1)
    else:
        up1 = v1_file.with_suffix('.uploaded')
        if up1.exists():
            v1_id = up1.read_text(encoding='utf-8').strip()
            
    v2_file = BASE_DIR / "06_戰後重構民主浪潮與矽島傳奇/第16章_時代巨變與傷痕記憶_播客深度對談.mp4"
    v2_title = "【臺灣史 PODCAST EP16】直面傷痕與歷史記憶：二二八真相、湯德章的尊嚴與三十八年戒嚴黑牢（深度對談）"
    v2_desc = BASE_DIR / "06_戰後重構民主浪潮與矽島傳奇/ch16_podcast_desc.txt"
    v2_thumb = BASE_DIR / "assets/images/ch16/ch16_podcast_thumbnail.jpg"
    v2_srt = BASE_DIR / "06_戰後重構民主浪潮與矽島傳奇/第16章_時代巨變與傷痕記憶_雙人對談.srt"
    v2_schedule = "2026-11-10 19:30"
    
    print("\n" + "="*70)
    print("🚀 [2/2] 正在上傳第 16 章 播客深度對談影片...")
    print("="*70)
    cmd2 = [
        PYTHON_EXE, str(UPLOADER_SCRIPT),
        "--video", str(v2_file),
        "--title", v2_title,
        "--desc-file", str(v2_desc),
        "--thumbnail", str(v2_thumb),
        "--srt", str(v2_srt),
        "--schedule", v2_schedule,
        "--playlist", "台灣史"
    ]
    ret2, out2 = run_cmd(cmd2)
    v2_id = None
    m2 = re.search(r"https://youtu\.be/([a-zA-Z0-9_-]{11})", out2)
    if m2:
        v2_id = m2.group(1)
    else:
        up2 = v2_file.with_suffix('.uploaded')
        if up2.exists():
            v2_id = up2.read_text(encoding='utf-8').strip()
            
    if v1_id and v2_id:
        print(f"\n🎉 雙軌影片發布成功！\n說明影片: https://youtu.be/{v1_id}\n播客影片: https://youtu.be/{v2_id}")
        update_data_js(v1_id, v2_id)
    else:
        print(f"\n[WARN] 部分影片未取得 ID (v1={v1_id}, v2={v2_id})")

if __name__ == '__main__':
    upload_all()
