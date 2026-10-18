# -*- coding: utf-8 -*-
"""
第06章 YouTube 影音全自動發布管線
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

def upload_ch06():
    base_dir = Path("d:/Antigravity/科技歷史/臺灣史")
    uploader_script = base_dir / "00_專案計畫與規範" / "youtube_api_uploader.py"
    
    # 1. 說明影片
    v1_file = base_dir / "02_大航海時代與荷西競逐" / "第06章_血濺赤崁與大鹿港_說明影片.mp4"
    v1_title = "【臺灣史 EP06】血濺赤崁與大鹿港：郭懷一抗荷事件與早期漢人移民的悲歌"
    v1_desc = base_dir / "02_大航海時代與荷西競逐" / "ch06_desc.txt"
    v1_thumb = base_dir / "assets" / "images" / "ch06" / "ch06_youtube_thumbnail.jpg"
    v1_srt = base_dir / "02_大航海時代與荷西競逐" / "第06章_血濺赤崁與大鹿港_說明影片.srt"
    v1_schedule = "2026-10-31 17:30"
    
    print("\n" + "=" * 60)
    print("🚀 [1/2] 正在上傳第 06 章 重點解說影片...")
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
    v2_file = base_dir / "02_大航海時代與荷西競逐" / "第06章_血濺赤崁與大鹿港_播客深度對談.mp4"
    v2_title = "【臺灣史 PODCAST EP06】血濺赤崁與大鹿港：郭懷一抗荷事件與殖民清剿真相（深度對談）"
    v2_desc = base_dir / "02_大航海時代與荷西競逐" / "ch06_podcast_desc.txt"
    v2_thumb = base_dir / "assets" / "images" / "ch06" / "ch06_podcast_thumbnail.jpg"
    v2_srt = base_dir / "02_大航海時代與荷西競逐" / "第06章_血濺赤崁與大鹿港_雙人對談.srt"
    v2_schedule = "2026-10-31 19:30"
    
    print("\n" + "=" * 60)
    print("🚀 [2/2] 正在上傳第 06 章 深度雙人對談播客影片...")
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
    print("\n📝 正在更新 js/data.js 中繼資料...")
    data_js_path = base_dir / "js" / "data.js"
    content = data_js_path.read_text(encoding="utf-8")
    
    nl_url = "https://notebook.google.com/notebook/c5354897-5c84-4a22-81e7-bc4ee2d0585b"
    audio_release_url = "https://github.com/clive520/taiwan-history/releases/download/v1.0.0/ch06_podcast_deepdive.m4a"
    
    # 更新 ch06 的屬性
    if v1_id:
        content = re.sub(
            r'("id":\s*"ch06"[\s\S]*?"youtube":\s*")[^"]*(")',
            rf'\g<1>{v1_id}\g<2>',
            content
        )
    if v2_id:
        content = re.sub(
            r'("id":\s*"ch06"[\s\S]*?"podcastYoutube":\s*")[^"]*(")',
            rf'\g<1>{v2_id}\g<2>',
            content
        )
    content = re.sub(
        r'("id":\s*"ch06"[\s\S]*?"audioFile":\s*")[^"]*(")',
        rf'\g<1>{audio_release_url}\g<2>',
        content
    )
            
    data_js_path.write_text(content, encoding="utf-8")
    print("✅ js/data.js 中繼資料更新成功！")
    
    # 4. 更新 Markdown 檔案中的 YouTube 連結
    md_path = base_dir / "02_大航海時代與荷西競逐" / "第06章_血濺赤崁與大鹿港_郭懷一抗荷事件與早期漢人移民的悲歌.md"
    if md_path.exists() and (v1_id or v2_id):
        md_text = md_path.read_text(encoding="utf-8")
        if v1_id:
            md_text = md_text.replace("重點解說影片 (YouTube)", f"[重點解說影片 (YouTube)](https://youtu.be/{v1_id})")
        if v2_id:
            md_text = md_text.replace("雙人對談播客 (YouTube)", f"[雙人對談播客 (YouTube)](https://youtu.be/{v2_id})")
        md_path.write_text(md_text, encoding="utf-8")
        print("✅ Markdown 內影音超連結更新成功！")

if __name__ == "__main__":
    upload_ch06()
