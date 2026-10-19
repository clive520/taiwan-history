# -*- coding: utf-8 -*-
"""
第08章 YouTube 影音全自動發布管線
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
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

PYTHON_EXE = r"C:\Users\admin\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"

def run_cmd(cmd):
    print(f"\n[EXEC] {' '.join(cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    print(res.stdout)
    if res.stderr:
        print(res.stderr, file=sys.stderr)
    return res.returncode, res.stdout

def upload_ch08():
    base_dir = Path("d:/Antigravity/科技歷史/臺灣史")
    uploader_script = base_dir / "00_專案計畫與規範" / "youtube_api_uploader.py"
    
    # 1. 說明影片
    v1_file = base_dir / "03_明鄭東寧與海上孤忠" / "第08章_海外別立乾坤_說明影片.mp4"
    v1_title = "【臺灣史 EP08】海外別立乾坤：陳永華的屯墾、孔廟儒學與東寧王國治理"
    v1_desc = base_dir / "03_明鄭東寧與海上孤忠" / "ch08_desc.txt"
    v1_thumb = base_dir / "assets" / "images" / "ch08" / "ch08_youtube_thumbnail.jpg"
    v1_srt = base_dir / "03_明鄭東寧與海上孤忠" / "第08章_海外別立乾坤_說明影片.srt"
    v1_schedule = "2026-11-02 17:30"
    
    print("\n" + "=" * 60)
    print("🚀 [1/2] 正在上傳第 08 章 重點解說影片...")
    print("=" * 60)
    
    cmd1 = [
        PYTHON_EXE, str(uploader_script),
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
        print(f"✅ 解說影片上傳成功！Video ID: {v1_id}")
    else:
        up_file1 = v1_file.with_suffix(".uploaded")
        if up_file1.exists():
            v1_id = up_file1.read_text(encoding="utf-8").strip()
            print(f"✅ 解說影片已存在或已上傳！Video ID: {v1_id}")
    
    # 2. 播客影片
    v2_file = base_dir / "03_明鄭東寧與海上孤忠" / "第08章_海外別立乾坤_播客深度對談.mp4"
    v2_title = "【臺灣史 PODCAST EP08】海外別立乾坤：陳永華的屯墾、孔廟儒學與東寧治理（深度對談）"
    v2_desc = base_dir / "03_明鄭東寧與海上孤忠" / "ch08_podcast_desc.txt"
    v2_thumb = base_dir / "assets" / "images" / "ch08" / "ch08_podcast_thumbnail.jpg"
    v2_srt = base_dir / "03_明鄭東寧與海上孤忠" / "第08章_海外別立乾坤_雙人對談.srt"
    v2_schedule = "2026-11-02 19:30"
    
    print("\n" + "=" * 60)
    print("🚀 [2/2] 正在上傳第 08 章 雙人對談播客影片...")
    print("=" * 60)
    
    cmd2 = [
        PYTHON_EXE, str(uploader_script),
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
        print(f"✅ 播客影片上傳成功！Video ID: {v2_id}")
    else:
        up_file2 = v2_file.with_suffix(".uploaded")
        if up_file2.exists():
            v2_id = up_file2.read_text(encoding="utf-8").strip()
            print(f"✅ 播客影片已存在或已上傳！Video ID: {v2_id}")
            
    # 3. 更新 js/data.js
    if v1_id and v2_id:
        update_data_js(v1_id, v2_id)
        update_markdown_links(v1_id, v2_id)

def update_data_js(v1_id, v2_id):
    data_js = Path("d:/Antigravity/科技歷史/臺灣史/js/data.js")
    content = data_js.read_text(encoding="utf-8")
    
    # 查找 ch08 區塊
    pattern = r'(\{\s*"id":\s*"ch08",[\s\S]*?"status":\s*)"planned"'
    replacement = r'\1"published"'
    content = re.sub(pattern, replacement, content)
    
    # 加入 youtube 與 podcastYoutube 等屬性
    props = f'''    "youtube": "{v1_id}",
    "podcastYoutube": "{v2_id}",
    "audioFile": "https://github.com/clive520/taiwan-history/releases/download/v1.0.0/ch08_podcast_deepdive.m4a",
    "notebooklm": "https://notebook.google.com/notebook/63f06a2e-10ea-41f4-b39b-2deec72d9b87",
    "srtFile": "第08章_海外別立乾坤_說明影片.srt",'''
    
    if '"youtube":' not in content[content.find('"id": "ch08"'):content.find('"id": "ch09"')]:
        ch08_target = r'(\{\s*"id":\s*"ch08",[\s\S]*?"status":\s*"published",)'
        content = re.sub(ch08_target, r'\1\n' + props, content)
        
    data_js.write_text(content, encoding="utf-8")
    print(f"✅ js/data.js 已成功更新第 08 章 YouTube IDs 與音訊串流連結！")

def update_markdown_links(v1_id, v2_id):
    md_file = Path("d:/Antigravity/科技歷史/臺灣史/03_明鄭東寧與海上孤忠/第08章_海外別立乾坤_陳永華的屯墾孔廟儒學與東寧王國治理.md")
    content = md_file.read_text(encoding="utf-8")
    content = content.replace("https://youtu.be/PENDING_CH08_VIDEO", f"https://youtu.be/{v1_id}")
    content = content.replace("https://youtu.be/PENDING_CH08_PODCAST", f"https://youtu.be/{v2_id}")
    content = content.replace("https://notebook.google.com/notebook/PENDING_CH08_NOTEBOOK", "https://notebook.google.com/notebook/63f06a2e-10ea-41f4-b39b-2deec72d9b87")
    md_file.write_text(content, encoding="utf-8")
    print(f"✅ Markdown 文章頭部影音連結已替換為真實 YouTube 連結！")

if __name__ == "__main__":
    upload_ch08()
