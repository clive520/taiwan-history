# -*- coding: utf-8 -*-
"""
《舌尖上的臺灣》第 06 章 YouTube 雙軌排程自動上架發布腳本
- 說明短片排程：2026-11-18 17:30
- 播客長片排程：2026-11-18 19:30
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
FOOD_DIR = BASE_DIR / "舌尖上的臺灣" / "02_唐山渡海與閩粵交融"
THUMB_DIR = BASE_DIR / "assets" / "images" / "food_ch06"

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
    audio_release_url = "https://github.com/clive520/taiwan-history/releases/download/v1.0.0/food_ch06_podcast_deepdive.m4a"
    
    # 1. 更新 js/data-food.js 與 舌尖上的臺灣/js/data.js
    db_paths = [
        BASE_DIR / "js" / "data-food.js",
        BASE_DIR / "舌尖上的臺灣" / "js" / "data.js"
    ]
    
    for db_path in db_paths:
        if not db_path.exists():
            continue
        c = db_path.read_text(encoding='utf-8')
        c_norm = c.replace("\r\n", "\n")
        
        # 替換 ch06 的 youtube 與 podcastYoutube
        target_pattern = r'(\{\s*"id":\s*"ch06",[\s\S]*?"youtube":\s*")[^"]*("[\s\S]*?"podcastYoutube":\s*")[^"]*(")'
        if re.search(target_pattern, c_norm):
            c_new = re.sub(target_pattern, rf'\g<1>{v1_id}\g<2>{v2_id}\g<3>', c_norm)
            db_path.write_text(c_new, encoding='utf-8')
            print(f"✅ 已成功更新 {db_path.relative_to(BASE_DIR)} 的 Video ID！")
        else:
            # 尚未 published 的情形
            p2 = r'(\{\s*"id":\s*"ch06",[\s\S]*?"status":\s*)"planned"([\s\S]*?"file":\s*"第06章_廟埕香火與米食變奏_炊粿米苔目米粉與紅龜粿的歲時禮俗\.md",)'
            replacement = (
                r'\1"published",\n'
                f'    "bannerImage": "assets/images/food_ch06/food_ch06_hero_banner.jpg",\n'
                f'    "youtube": "{v1_id}",\n'
                f'    "podcastYoutube": "{v2_id}",\n'
                f'    "audioFile": "{audio_release_url}",\n'
                r'\2'
            )
            c_new = re.sub(p2, replacement, c_norm)
            db_path.write_text(c_new, encoding='utf-8')
            print(f"✅ 已成功登錄並發布 {db_path.name}！")

    # 2. 更新 Markdown 導讀影音超連結
    md_file = FOOD_DIR / "第06章_廟埕香火與米食變奏_炊粿米苔目米粉與紅龜粿的歲時禮俗.md"
    if md_file.exists():
        md_c = md_file.read_text(encoding='utf-8')
        md_c = re.sub(r'https://youtu\.be/[a-zA-Z0-9_-]+（98°C在來米', f'https://youtu.be/{v1_id}（98°C在來米', md_c)
        md_c = re.sub(r'https://youtu\.be/(?:pending_food_ch06_video|EjvkHIRrDyM)', f'https://youtu.be/{v1_id}', md_c)
        md_c = re.sub(r'https://youtu\.be/(?:pending_food_ch06_podcast|lqA98KpG-UQ)', f'https://youtu.be/{v2_id}', md_c)
        md_file.write_text(md_c, encoding='utf-8')
        print(f"✅ 已成功更新專題長文導讀模組 Video ID：{md_file.name}！")

def main():
    # 說明短片設定
    v1_file = FOOD_DIR / "第06章_廟埕香火與米食變奏_說明影片.mp4"
    v1_title = "【舌尖上的臺灣 EP06】廟埕香火與米食變奏！新竹米粉九降風天然氣刀、在來米30%直鏈澱粉凝膠與紅龜粿歲時禮俗"
    v1_desc = FOOD_DIR / "food_ch06_desc.txt"
    v1_thumb = THUMB_DIR / "food_ch06_youtube_thumbnail.jpg"
    v1_srt = FOOD_DIR / "第06章_廟埕香火與米食變奏_說明影片.srt"
    
    # 播客長片設定
    v2_file = FOOD_DIR / "第06章_廟埕香火與米食變奏_播客深度對談.mp4"
    v2_title = "【深度播客】廟埕香火與米食變奏：從新竹都城隍廟祈年、九降風米粉到客庄面帕粄與米苔目瞬時凝膠的生命交響"
    v2_desc = FOOD_DIR / "food_ch06_podcast_desc.txt"
    v2_thumb = THUMB_DIR / "food_ch06_podcast_thumbnail.jpg"
    v2_srt = FOOD_DIR / "第06章_廟埕香火與米食變奏_雙人對談.srt"
    
    tags = "臺灣歷史,舌尖上的臺灣,新竹米粉,紅龜粿,客家粄條,面帕粄,米苔目,新竹都城隍廟,九降風,在來米,食品科學,民俗信仰,歲時禮俗,飲食文化"
    playlist_name = "舌尖上的臺灣"
    
    print("\n" + "="*70)
    print("🚀 [軌道一] 開始排程上架說明短片...")
    print("="*70)
    cmd1 = [
        PYTHON_EXE, str(UPLOADER_SCRIPT),
        "--video", str(v1_file),
        "--title", v1_title,
        "--desc-file", str(v1_desc),
        "--tags", tags,
        "--schedule", "2026-11-18 17:30",
        "--thumbnail", str(v1_thumb),
        "--srt", str(v1_srt),
        "--playlist", playlist_name
    ]
    ret1, out1 = run_cmd(cmd1)
    
    v1_id = None
    m1 = re.search(r"Video ID:\s*([a-zA-Z0-9_-]+)", out1)
    if not m1:
        m1 = re.search(r"影片 ID:\s*([a-zA-Z0-9_-]+)", out1)
    if m1:
        v1_id = m1.group(1)
        print(f"🎉 說明短片上架成功！Video ID: {v1_id}")
    else:
        uploaded_marker = FOOD_DIR / (v1_file.name + ".uploaded")
        if uploaded_marker.exists():
            v1_id = uploaded_marker.read_text(encoding="utf-8").strip()
            print(f"🎉 由標記檔讀取 Video ID: {v1_id}")
        else:
            print("❌ 未能識別說明短片 Video ID！")

    print("\n" + "="*70)
    print("🚀 [軌道二] 開始排程上架播客長片...")
    print("="*70)
    cmd2 = [
        PYTHON_EXE, str(UPLOADER_SCRIPT),
        "--video", str(v2_file),
        "--title", v2_title,
        "--desc-file", str(v2_desc),
        "--tags", tags,
        "--schedule", "2026-11-18 19:30",
        "--thumbnail", str(v2_thumb),
        "--srt", str(v2_srt),
        "--playlist", playlist_name
    ]
    ret2, out2 = run_cmd(cmd2)
    
    v2_id = None
    m2 = re.search(r"Video ID:\s*([a-zA-Z0-9_-]+)", out2)
    if not m2:
        m2 = re.search(r"影片 ID:\s*([a-zA-Z0-9_-]+)", out2)
    if m2:
        v2_id = m2.group(1)
        print(f"🎉 播客長片上架成功！Video ID: {v2_id}")
    else:
        uploaded_marker = FOOD_DIR / (v2_file.name + ".uploaded")
        if uploaded_marker.exists():
            v2_id = uploaded_marker.read_text(encoding="utf-8").strip()
            print(f"🎉 由標記檔讀取 Video ID: {v2_id}")
        else:
            print("❌ 未能識別播客長片 Video ID！")

    if v1_id and v2_id:
        print("\n" + "="*70)
        print("💾 正在同步更新全站資料庫與長文導讀模組...")
        print("="*70)
        update_databases(v1_id, v2_id)
        print("\n✨ 第 06 章 YouTube 雙軌排程上架與資料庫同步大功告成！")
    else:
        print("\n⚠️ 因 Video ID 缺失，跳過資料庫自動更新，請手動檢查。")

if __name__ == "__main__":
    main()
