# -*- coding: utf-8 -*-
"""
第02章 YouTube 影音全自動發布管線
調用 youtube_api_uploader.py 發布說明影片與播客影片，
設定排程、高清封面、繁體中文字幕軌與播放清單，並自動更新 js/data.js。
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

def upload_ch02():
    base_dir = Path("d:/Antigravity/科技歷史/臺灣史")
    uploader_script = base_dir / "00_專案計畫與規範" / "youtube_api_uploader.py"
    
    # 1. 說明影片
    v1_file = base_dir / "01_史前文明與南島之源" / "第02章_大海是唯一的路徑_說明影片.mp4"
    v1_title = "【臺灣史 EP02】大海是唯一的路徑：南島語族原鄉假說與跨太平洋的獨木舟"
    v1_desc = base_dir / "01_史前文明與南島之源" / "ch02_desc.txt"
    v1_thumb = base_dir / "assets" / "images" / "ch02" / "ch02_hero_banner.jpg"
    v1_srt = base_dir / "01_史前文明與南島之源" / "第02章_大海是唯一的路徑_說明影片.srt"
    v1_schedule = "2026-10-27 17:30"
    
    print("\n" + "=" * 60)
    print("🚀 [1/2] 正在上傳第 02 章 重點解說影片...")
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
    
    # 提取 Video ID
    v1_id = None
    m1 = re.search(r"https://youtu\.be/([a-zA-Z0-9_-]{11})", out1)
    if m1:
        v1_id = m1.group(1)
        print(f"✅ 解說影片上傳成功！Video ID: {v1_id}")
    else:
        # 檢查 .uploaded 檔
        up_file1 = v1_file.with_suffix(".uploaded")
        if up_file1.exists():
            v1_id = up_file1.read_text(encoding="utf-8").strip()
            print(f"✅ 解說影片已存在或已上傳！Video ID: {v1_id}")
    
    # 2. 播客影片
    v2_file = base_dir / "01_史前文明與南島之源" / "第02章_大海是唯一的路徑_播客深度對談.mp4"
    v2_title = "【臺灣史 PODCAST EP02】大海是唯一的路徑：南島語族原鄉假說（雙人深度對談）"
    v2_desc = base_dir / "01_史前文明與南島之源" / "ch02_podcast_desc.txt"
    v2_thumb = base_dir / "assets" / "images" / "ch02" / "ch02_hero_banner.jpg"
    v2_srt = base_dir / "01_史前文明與南島之源" / "第02章_大海是唯一的路徑_雙人對談.srt"
    v2_schedule = "2026-10-27 19:30"
    
    print("\n" + "=" * 60)
    print("🚀 [2/2] 正在上傳第 02 章 深度雙人對談播客影片...")
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
    if v1_id or v2_id:
        print("\n📝 正在更新 js/data.js 中繼資料...")
        data_js_path = base_dir / "js" / "data.js"
        content = data_js_path.read_text(encoding="utf-8")
        
        if v1_id:
            content = re.sub(
                r'("id":\s*"ch02"[\s\S]*?"youtube":\s*")[^"]*(")',
                rf'\g<1>{v1_id}\g<2>',
                content
            )
        if v2_id:
            content = re.sub(
                r'("id":\s*"ch02"[\s\S]*?"podcastYoutube":\s*")[^"]*(")',
                rf'\g<1>{v2_id}\g<2>',
                content
            )
        data_js_path.write_text(content, encoding="utf-8")
        print("✅ js/data.js 更新完成！")
        
    print("\n🎉 第 02 章 YouTube 影音雙軌上傳發布流程全數完成！")
    print(f"   - 說明影片: https://youtu.be/{v1_id}")
    print(f"   - 播客影片: https://youtu.be/{v2_id}")

if __name__ == "__main__":
    upload_ch02()
