# -*- coding: utf-8 -*-
"""
第10章 YouTube 影音全自動發布管線
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

def upload_ch10():
    base_dir = Path("d:/Antigravity/科技歷史/臺灣史")
    uploader_script = base_dir / "00_專案計畫與規範" / "youtube_api_uploader.py"
    
    # 1. 說明影片
    v1_file = base_dir / "04_清領時代的拓墾烽火與變革" / "第10章_唐山過臺灣的黑水溝血淚_說明影片.mp4"
    v1_title = "【臺灣史 EP10】唐山過臺灣：黑水溝生死血淚與八堡圳大拓荒"
    v1_desc = base_dir / "04_清領時代的拓墾烽火與變革" / "ch10_desc.txt"
    v1_thumb = base_dir / "assets" / "images" / "ch10" / "ch10_youtube_thumbnail.jpg"
    v1_srt = base_dir / "04_清領時代的拓墾烽火與變革" / "第10章_唐山過臺灣的黑水溝血淚_說明影片.srt"
    v1_schedule = "2026-11-04 17:30"
    
    print("\n" + "=" * 60)
    print("🚀 [1/2] 正在上傳第 10 章 重點解說影片...")
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
    v2_file = base_dir / "04_清領時代的拓墾烽火與變革" / "第10章_唐山過臺灣的黑水溝血淚_播客深度對談.mp4"
    v2_title = "【臺灣史 PODCAST EP10】黑水溝偷渡秘辛：羅漢腳與水利奇蹟（深度對談）"
    v2_desc = base_dir / "04_清領時代的拓墾烽火與變革" / "ch10_podcast_desc.txt"
    v2_thumb = base_dir / "assets" / "images" / "ch10" / "ch10_podcast_thumbnail.jpg"
    v2_srt = base_dir / "04_清領時代的拓墾烽火與變革" / "第10章_唐山過臺灣的黑水溝血淚_雙人對談.srt"
    v2_schedule = "2026-11-04 19:30"
    
    print("\n" + "=" * 60)
    print("🚀 [2/2] 正在上傳第 10 章 雙人對談播客影片...")
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

def update_data_js(v1_id, v2_id):
    data_js = Path("d:/Antigravity/科技歷史/臺灣史/js/data.js")
    content = data_js.read_text(encoding="utf-8")
    
    # 查找 ch10 區塊
    pattern = r'(\{\s*"id":\s*"ch10",[\s\S]*?"status":\s*)"planned"'
    replacement = r'\1"published"'
    content = re.sub(pattern, replacement, content)
    
    # 加入 youtube 與 podcastYoutube 等屬性
    props = f'''    "bannerImage": "assets/images/ch10/ch10_hero_banner.jpg",
    "youtube": "{v1_id}",
    "podcastYoutube": "{v2_id}",
    "audioFile": "https://github.com/clive520/taiwan-history/releases/download/v1.0.0/ch10_podcast_deepdive.m4a",
    "notebooklm": "https://notebook.google.com/notebook/2e42523c-3cd8-4b77-9db8-471e84baee53",
    "srtFile": "第10章_唐山過臺灣的黑水溝血淚_說明影片.srt",'''
    
    if '"youtube":' not in content[content.find('"id": "ch10"'):content.find('"id": "ch11"')]:
        ch10_target = r'(\{\s*"id":\s*"ch10",[\s\S]*?"status":\s*"published",)'
        content = re.sub(ch10_target, r'\1\n' + props, content)
        
    data_js.write_text(content, encoding="utf-8")
    print(f"✅ js/data.js 已成功更新第 10 章 YouTube IDs 與音訊串流連結！")

if __name__ == "__main__":
    upload_ch10()
