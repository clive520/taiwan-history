# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第 09 章 YouTube 雙軌排程自動上架發布腳本
- 說明短片排程：2026-11-21 17:30
- 播客長片排程：2026-11-21 19:30
- 官方清單：舌尖上的臺灣 (PLAFdajbNY8qg)
- 自動更新 js/data-food.js、舌尖上的臺灣/js/data.js 與專題長文導讀模組
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
FOOD_DIR = BASE_DIR / "舌尖上的臺灣" / "03_帝國之眼與東洋滋味"
THUMB_DIR = BASE_DIR / "assets" / "images" / "food_ch09"

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

def update_databases(v1_id, v2_id):
    audio_release_url = "https://github.com/clive520/taiwan-history/releases/download/v1.0.0/food_ch09_podcast_deepdive.m4a"
    
    # 1. 更新 js/data-food.js 與 舌尖上的臺灣/js/data.js
    db_paths = [
        BASE_DIR / "js" / "data-food.js",
        BASE_DIR / "舌尖上的臺灣" / "js" / "data.js"
    ]
    
    for db_path in db_paths:
        if not db_path.exists():
            continue
        c = db_path.read_text(encoding='utf-8')
        pattern = r'("id":\s*"ch09",[\s\S]*?"status":\s*)"planned"'
        replacement = rf'\1"published",\n      "videoId": "{v1_id}",\n      "podcastId": "{v2_id}"'
        c_new = re.sub(pattern, replacement, c)
        db_path.write_text(c_new, encoding='utf-8')
        print(f"✅ 已更新資料庫: {db_path.name}")

    # 2. 更新專題長文導讀模組
    doc_path = FOOD_DIR / "第09章_汽笛聲中的木片便當_縱貫鐵路通車生啤酒喫茶店與鐵路便當的摩登生活.md"
    if doc_path.exists():
        t = doc_path.read_text(encoding='utf-8')
        t = t.replace("placeholder_food_ch09_video", v1_id)
        t = t.replace("placeholder_food_ch09_podcast", v2_id)
        doc_path.write_text(t, encoding='utf-8')
        print(f"✅ 已更新專題長文導讀模組 Video IDs")

def main():
    # 說明短片設定
    v1_file = FOOD_DIR / "第09章_汽笛聲中的木片便當_說明影片.mp4"
    v1_title = "【舌尖上的臺灣 EP09】汽笛聲中的木片便當！縱貫鐵路全通、經木盒呼吸防餿與月台便當的百年演進"
    v1_desc = FOOD_DIR / "food_ch09_desc.txt"
    v1_thumb = THUMB_DIR / "food_ch09_youtube_thumbnail.jpg"
    v1_srt = FOOD_DIR / "第09章_汽笛聲中的木片便當_說明影片.srt"
    
    # 播客長片設定
    v2_file = FOOD_DIR / "第09章_汽笛聲中的木片便當_播客深度對談.mp4"
    v2_title = "【深度播客】汽笛、黑膠與生啤酒：從臺灣鐵道飯店法式西餐、波麗路喫茶店相親到建國啤酒廠前身的摩登狂潮"
    v2_desc = FOOD_DIR / "food_ch09_podcast_desc.txt"
    v2_thumb = THUMB_DIR / "food_ch09_podcast_thumbnail.jpg"
    v2_srt = FOOD_DIR / "第09章_汽笛聲中的木片便當_雙人對談.srt"
    
    tags = "臺灣歷史,舌尖上的臺灣,鐵路便當,縱貫鐵路,臺鐵排骨便當,經木盒,波麗路,高砂麥酒,建國啤酒廠,大正浪漫,昭和摩登,臺灣鐵道飯店,喫茶店,山水亭,女給,生啤酒"
    playlist_name = "舌尖上的臺灣"

    if not v1_file.exists():
        print(f"❌ 說明短片不存在：{v1_file}")
        sys.exit(1)
    if not v2_file.exists():
        print(f"❌ 播客影片不存在：{v2_file}")
        sys.exit(1)

    print("🚀 開始執行第 09 章 YouTube 雙軌排程上傳...")

    # 1. 上傳說明短片（排程 2026-11-21 17:30）
    cmd_v1 = [
        PYTHON_EXE, str(UPLOADER_SCRIPT),
        "--video", str(v1_file),
        "--title", v1_title,
        "--desc-file", str(v1_desc),
        "--tags", tags,
        "--schedule", "2026-11-21 17:30",
        "--playlist", playlist_name,
        "--thumbnail", str(v1_thumb),
        "--srt", str(v1_srt)
    ]
    ret1, out1 = run_cmd(cmd_v1)
    if ret1 != 0:
        print("❌ 說明短片上傳失敗！")
        sys.exit(ret1)
    
    v1_id = None
    m1 = re.search(r"Video ID:\s*([a-zA-Z0-9_-]+)", out1)
    if not m1:
        m1 = re.search(r"影片 ID:\s*([a-zA-Z0-9_-]+)", out1)
    if m1:
        v1_id = m1.group(1)
    print(f"\n🎉 說明短片上傳成功！Video ID: {v1_id}")

    # 2. 上傳播客長片（排程 2026-11-21 19:30）
    cmd_v2 = [
        PYTHON_EXE, str(UPLOADER_SCRIPT),
        "--video", str(v2_file),
        "--title", v2_title,
        "--desc-file", str(v2_desc),
        "--tags", tags,
        "--schedule", "2026-11-21 19:30",
        "--playlist", playlist_name,
        "--thumbnail", str(v2_thumb),
        "--srt", str(v2_srt)
    ]
    ret2, out2 = run_cmd(cmd_v2)
    if ret2 != 0:
        print("❌ 播客長片上傳失敗！")
        sys.exit(ret2)

    v2_id = None
    m2 = re.search(r"Video ID:\s*([a-zA-Z0-9_-]+)", out2)
    if not m2:
        m2 = re.search(r"影片 ID:\s*([a-zA-Z0-9_-]+)", out2)
    if m2:
        v2_id = m2.group(1)
    print(f"\n🎉 播客長片上傳成功！Video ID: {v2_id}")

    # 3. 更新資料庫與專題長文
    if v1_id and v2_id:
        update_databases(v1_id, v2_id)
        print(f"\n🔥 第 09 章發布流程全部圓滿成功！\n- 說明短片: https://youtu.be/{v1_id}\n- 播客長片: https://youtu.be/{v2_id}")
        
        # 輸出 ID 供 log 更新
        with open(BASE_DIR / "00_專案計畫與規範" / "food_ch09_youtube_ids.txt", "w", encoding="utf-8") as f:
            f.write(f"{v1_id}\n{v2_id}\n")

if __name__ == "__main__":
    main()
