# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第 02 章 YouTube 雙軌排程自動化發布管線
- 說明短片排程：2026-11-14 17:30
- 播客長片排程：2026-11-14 19:30
- 播放清單：舌尖上的臺灣 (PLAFdajbNY8qg)
- 自動更新 js/data-food.js、舌尖上的臺灣/js/data.js 與專題長文超連結
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
FOOD_DIR = BASE_DIR / "舌尖上的臺灣" / "01_山海風土與島嶼原味"
THUMB_DIR = BASE_DIR / "assets" / "images" / "food_ch02"

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
    audio_release_url = "https://github.com/clive520/taiwan-history/releases/download/v1.0.0/food_ch02_podcast_deepdive.m4a"
    
    # 1. 更新 js/data-food.js
    db_paths = [
        BASE_DIR / "js" / "data-food.js",
        BASE_DIR / "舌尖上的臺灣" / "js" / "data.js"
    ]
    
    for db_path in db_paths:
        if not db_path.exists():
            continue
        c = db_path.read_text(encoding='utf-8')
        c_norm = c.replace("\r\n", "\n")
        
        target_pattern = r'(\{\s*"id":\s*"ch02",[\s\S]*?"status":\s*)"planned"([\s\S]*?"file":\s*"第02章_大航海的蔗香與鹿皮_荷西東印度公司糖業拓墾與熱帶果物登陸\.md",)'
        
        replacement = (
            r'\1"published",\n'
            f'    "bannerImage": "assets/images/food_ch02/food_ch02_hero_banner.jpg",\n'
            f'    "youtube": "{v1_id}",\n'
            f'    "podcastYoutube": "{v2_id}",\n'
            f'    "audioFile": "{audio_release_url}",\n'
            r'\2'
        )
        
        if re.search(target_pattern, c_norm):
            c_new = re.sub(target_pattern, replacement, c_norm)
            db_path.write_text(c_new, encoding='utf-8')
            print(f"✅ 已成功更新 {db_path.relative_to(BASE_DIR)}！")
        else:
            print(f"[WARN] 未能在 {db_path.name} 找到 ch02 預備替換區塊，請手動檢查。")

    # 2. 更新 Markdown 導讀影音超連結
    md_file = FOOD_DIR / "第02章_大航海的蔗香與鹿皮_荷西東印度公司糖業拓墾與熱帶果物登陸.md"
    if md_file.exists():
        md_c = md_file.read_text(encoding='utf-8')
        md_c = md_c.replace("https://youtu.be/pending_food_ch02_video", f"https://youtu.be/{v1_id}")
        md_c = md_c.replace("https://youtu.be/pending_food_ch02_podcast", f"https://youtu.be/{v2_id}")
        md_file.write_text(md_c, encoding='utf-8')
        print(f"✅ 已成功更新專題長文 {md_file.name} 影音超連結！")

def upload_all():
    v1_file = FOOD_DIR / "第02章_大航海的蔗香與鹿皮_說明影片.mp4"
    v1_title = "【舌尖上的臺灣 EP02】大航海的蔗香與鹿皮！荷蘭東印度公司、王田糖廍與熱帶果物登陸傳奇"
    v1_desc = FOOD_DIR / "food_ch02_desc.txt"
    v1_thumb = THUMB_DIR / "food_ch02_youtube_thumbnail.jpg"
    v1_srt = FOOD_DIR / "第02章_大航海的蔗香與鹿皮_說明影片.srt"
    v1_schedule = "2026-11-14 17:30"
    
    print("\n" + "="*70)
    print("🚀 [1/2] 正在上傳第 02 章 說明影片...")
    print("="*70)
    cmd1 = [
        PYTHON_EXE, str(UPLOADER_SCRIPT),
        "--video", str(v1_file),
        "--title", v1_title,
        "--desc-file", str(v1_desc),
        "--thumbnail", str(v1_thumb),
        "--srt", str(v1_srt),
        "--schedule", v1_schedule,
        "--playlist", "舌尖上的臺灣"
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
            
    v2_file = FOOD_DIR / "第02章_大航海的蔗香與鹿皮_播客深度對談.mp4"
    v2_title = "【舌尖上的臺灣 PODCAST EP02】17世紀的甜蜜與殘酷：鹿皮海嘯、糖業拓墾與臺南甜的歷史身世（深度對談）"
    v2_desc = FOOD_DIR / "food_ch02_podcast_desc.txt"
    v2_thumb = THUMB_DIR / "food_ch02_podcast_thumbnail.jpg"
    v2_srt = FOOD_DIR / "第02章_大航海的蔗香與鹿皮_雙人對談.srt"
    v2_schedule = "2026-11-14 19:30"
    
    print("\n" + "="*70)
    print("🚀 [2/2] 正在上傳第 02 章 播客深度對談影片...")
    print("="*70)
    cmd2 = [
        PYTHON_EXE, str(UPLOADER_SCRIPT),
        "--video", str(v2_file),
        "--title", v2_title,
        "--desc-file", str(v2_desc),
        "--thumbnail", str(v2_thumb),
        "--srt", str(v2_srt),
        "--schedule", v2_schedule,
        "--playlist", "舌尖上的臺灣"
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
            
    print("\n" + "="*70)
    print("🎉 上傳作業彙整：")
    print(f"🎬 說明短片 ID: {v1_id} (https://youtu.be/{v1_id})")
    print(f"🎙️ 播客長片 ID: {v2_id} (https://youtu.be/{v2_id})")
    print("="*70)
    
    if v1_id and v2_id:
        update_databases(v1_id, v2_id)
    else:
        print("⚠️ 未能完全獲取兩個 Video ID，請手動確認上傳記錄！")

if __name__ == "__main__":
    upload_all()
